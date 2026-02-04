from __future__ import annotations

import json
import hashlib
import time
from typing import Any

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from sqlalchemy import select

from app.config import get_settings
from app.db import SessionLocal
from app.gutenberg import fetch_gutenberg_text, normalize_gutenberg_text
from app.graph.prompts import (
    ESSAY_DRAFT_SYSTEM,
    ESSAY_DRAFT_USER,
    REVIEW_SYSTEM,
    REVIEW_USER,
    REVISE_SYSTEM,
    REVISE_USER,
    SUMMARIZE_CHUNK_SYSTEM,
    SUMMARIZE_CHUNK_USER,
    THEME_DISCOVERY_SYSTEM,
    THEME_DISCOVERY_USER,
    THEME_INTRO_SYSTEM,
    THEME_INTRO_USER,
)
from app.graph.state import EssayGraphState
from app.logging_config import configure_logging
from app.models import Document, Job, JobArtifact
from app.pinecone_client import PineconeClient, query_similar, upsert_embeddings
from app.queue import update_job_progress
from app.segment import segment_text

logger = configure_logging("graph", "worker.log")


def _get_settings():
    return get_settings()


def _build_evidence_block(themes: list[str], evidence: dict[str, list[dict]]) -> str:
    lines = []
    for theme in themes:
        lines.append(f"Theme: {theme}")
        for item in evidence.get(theme, []):
            lines.append(f"- [{item['segment_id']}] {item['text']}")
    return "\n".join(lines)


def _build_expanded_evidence_block(
    themes: list[str], expanded_evidence: dict[str, list[dict]]
) -> str:
    lines = []
    for theme in themes:
        lines.append(f"Theme: {theme}")
        for item in expanded_evidence.get(theme, []):
            if item.get("context_before"):
                lines.append(f"  [context] {item['context_before']}")
            lines.append(f"  [{item['segment_id']}] {item['text']}")
            if item.get("context_after"):
                lines.append(f"  [context] {item['context_after']}")
            lines.append("")
    return "\n".join(lines)


def _build_theme_intros_block(themes: list[str], theme_intros: dict[str, str]) -> str:
    lines = []
    for theme in themes:
        intro = theme_intros.get(theme, "")
        if intro:
            lines.append(f"## Theme: {theme}")
            lines.append(f"Introduction:\n{intro}")
            lines.append("")
    return "\n".join(lines)


def ingest_node(state: EssayGraphState) -> dict[str, Any]:
    settings = _get_settings()
    job_id = state["job_id"]
    document_id = state["document_id"]
    gutenberg_id = state["gutenberg_id"]
    namespace = state["pinecone_namespace"]

    with SessionLocal() as db:
        doc = db.get(Document, document_id)
        if not doc:
            raise RuntimeError(f"Document {document_id} not found")

        job = db.get(Job, job_id)
        update_job_progress(db, job, "ingest", "starting ingestion")

        if doc.ingest_status == "ready":
            logger.info("ingest_node: already ready document_id=%s", document_id)
            update_job_progress(db, job, "ingest", "already ingested")
            # Re-fetch and segment text so downstream nodes have segments
            raw = fetch_gutenberg_text(gutenberg_id)
            normalized = normalize_gutenberg_text(raw)
            segments = segment_text(normalized, settings.max_segment_chars)
            seg_dicts = [
                {
                    "segment_id": seg.segment_id,
                    "text": seg.text,
                    "chapter": seg.chapter,
                    "paragraph_index": seg.paragraph_index,
                }
                for seg in segments
            ]
            return {
                "segments": seg_dicts,
                "segment_count": len(seg_dicts),
                "ingest_complete": True,
                "current_step": "ingest_complete",
            }

        doc.ingest_status = "running"
        db.add(doc)
        db.commit()

        logger.info("ingest_node: fetching text gutenberg_id=%s", gutenberg_id)
        update_job_progress(db, job, "ingest", "fetching text from Gutenberg")
        raw = fetch_gutenberg_text(gutenberg_id)
        normalized = normalize_gutenberg_text(raw)
        segments = segment_text(normalized, settings.max_segment_chars)
        logger.info("ingest_node: segmented count=%s", len(segments))

        update_job_progress(db, job, "ingest", f"embedding {len(segments)} segments")

        if segments:
            embeddings_model = OpenAIEmbeddings(
                model=settings.openai_embedding_model,
                api_key=settings.openai_api_key,
            )
            texts = [seg.text for seg in segments]
            embeddings = embeddings_model.embed_documents(texts)
            logger.info("ingest_node: embedded %s segments", len(embeddings))

            pc = PineconeClient()
            pc.ensure_index(dimension=len(embeddings[0]))

            batch = []
            for seg, embedding in zip(segments, embeddings):
                metadata = {
                    "document_id": str(doc.id),
                    "paragraph_index": seg.paragraph_index,
                    "text": seg.text,
                }
                if seg.chapter is not None:
                    metadata["chapter"] = seg.chapter
                batch.append((seg.segment_id, embedding, metadata))

            update_job_progress(db, job, "ingest", f"upserting {len(batch)} vectors to Pinecone")
            upsert_embeddings(pc, namespace, batch)
            logger.info("ingest_node: upserted namespace=%s count=%s", namespace, len(batch))

        doc.ingest_status = "ready"
        db.add(doc)
        db.commit()

        update_job_progress(db, job, "ingest", "ingestion complete")
        logger.info("ingest_node: complete document_id=%s", document_id)

    seg_dicts = [
        {
            "segment_id": seg.segment_id,
            "text": seg.text,
            "chapter": seg.chapter,
            "paragraph_index": seg.paragraph_index,
        }
        for seg in segments
    ] if segments else []

    return {
        "segments": seg_dicts,
        "segment_count": len(seg_dicts),
        "ingest_complete": True,
        "current_step": "ingest_complete",
    }


def summarize_book_node(state: EssayGraphState) -> dict[str, Any]:
    settings = _get_settings()
    job_id = state["job_id"]
    document_id = state["document_id"]
    segments = state["segments"]

    with SessionLocal() as db:
        job = db.get(Job, job_id)
        doc = db.get(Document, document_id)

        # Check for cached summary
        if doc and doc.summary:
            logger.info("summarize_book_node: using cached summary document_id=%s", document_id)
            update_job_progress(db, job, "summarize_book", "using cached summary")
            return {"book_summary": doc.summary, "current_step": "book_summarized"}

        update_job_progress(db, job, "summarize_book", "starting summarization")

    chunk_size = settings.summary_chunk_size
    texts = [seg["text"] for seg in segments]
    chunks = [texts[i : i + chunk_size] for i in range(0, len(texts), chunk_size)]
    total_chunks = len(chunks)

    llm = ChatOpenAI(
        model=settings.openai_chat_model,
        api_key=settings.openai_api_key,
        temperature=0.2,
    )

    running_summary = ""
    for i, chunk in enumerate(chunks):
        chunk_text = "\n\n".join(chunk)
        with SessionLocal() as db:
            job = db.get(Job, job_id)
            update_job_progress(
                db, job, "summarize_book", f"Summarizing chunk {i + 1}/{total_chunks}..."
            )

        prompt = SUMMARIZE_CHUNK_USER.format(
            running_summary=running_summary or "(none — this is the first chunk)",
            chunk_text=chunk_text,
        )
        response = llm.invoke([
            {"role": "system", "content": SUMMARIZE_CHUNK_SYSTEM},
            {"role": "user", "content": prompt},
        ])
        running_summary = response.content
        logger.info("summarize_book_node: chunk %s/%s done", i + 1, total_chunks)

    # Cache the summary on the document
    with SessionLocal() as db:
        doc = db.get(Document, document_id)
        if doc:
            doc.summary = running_summary
            db.add(doc)
            db.commit()
        job = db.get(Job, job_id)
        update_job_progress(db, job, "summarize_book", "summarization complete")

    return {
        "book_summary": running_summary,
        "chunks_summarized": total_chunks,
        "current_step": "book_summarized",
    }


def discover_themes_node(state: EssayGraphState) -> dict[str, Any]:
    settings = _get_settings()
    title = state.get("title") or "Unknown Title"
    author = state.get("author") or "Unknown Author"
    book_summary = state.get("book_summary", "")
    job_id = state["job_id"]

    with SessionLocal() as db:
        job = db.get(Job, job_id)
        update_job_progress(db, job, "discover_themes", "identifying literary themes")

    llm = ChatOpenAI(
        model=settings.openai_chat_model,
        api_key=settings.openai_api_key,
        temperature=0.2,
    )
    prompt = THEME_DISCOVERY_USER.format(
        title=title, author=author, book_summary=book_summary
    )
    response = llm.invoke([
        {"role": "system", "content": THEME_DISCOVERY_SYSTEM},
        {"role": "user", "content": prompt},
    ])

    raw = response.content
    try:
        data = json.loads(raw)
        themes = [str(item) for item in data][:6]
    except json.JSONDecodeError:
        themes = [line.strip("- ") for line in raw.splitlines() if line.strip()][:6]

    logger.info("discover_themes_node: found %s themes", len(themes))

    with SessionLocal() as db:
        job = db.get(Job, job_id)
        update_job_progress(db, job, "discover_themes", f"found {len(themes)} themes")

    return {"themes": themes, "current_step": "themes_discovered"}


def retrieve_evidence_node(state: EssayGraphState) -> dict[str, Any]:
    settings = _get_settings()
    themes = state["themes"]
    namespace = state["pinecone_namespace"]
    job_id = state["job_id"]

    with SessionLocal() as db:
        job = db.get(Job, job_id)
        update_job_progress(db, job, "retrieve_evidence", "embedding theme queries")

    embeddings_model = OpenAIEmbeddings(
        model=settings.openai_embedding_model,
        api_key=settings.openai_api_key,
    )
    query_embeddings = embeddings_model.embed_documents(themes)

    pc = PineconeClient()
    evidence: dict[str, list[dict]] = {}

    for theme, embedding in zip(themes, query_embeddings):
        result = query_similar(pc, namespace, embedding, top_k=settings.top_k_evidence)
        matches = []
        for match in result.get("matches", []):
            md = match.get("metadata") or {}
            matches.append({
                "segment_id": match.get("id"),
                "score": match.get("score"),
                "text": md.get("text"),
                "chapter": md.get("chapter"),
                "paragraph_index": md.get("paragraph_index"),
            })
        evidence[theme] = matches

    total = sum(len(v) for v in evidence.values())
    logger.info("retrieve_evidence_node: %s themes, %s total matches", len(themes), total)

    with SessionLocal() as db:
        job = db.get(Job, job_id)
        update_job_progress(db, job, "retrieve_evidence", f"retrieved {total} evidence passages")

    return {"evidence": evidence, "current_step": "evidence_retrieved"}


def expand_context_node(state: EssayGraphState) -> dict[str, Any]:
    settings = _get_settings()
    evidence = state["evidence"]
    segments = state["segments"]
    job_id = state["job_id"]
    window = settings.expand_context_window

    with SessionLocal() as db:
        job = db.get(Job, job_id)
        update_job_progress(db, job, "expand_context", "expanding evidence context")

    # Build index lookup: segment_id -> index in segments list
    seg_index = {seg["segment_id"]: i for i, seg in enumerate(segments)}

    expanded_evidence: dict[str, list[dict]] = {}
    for theme, matches in evidence.items():
        expanded = []
        for match in matches:
            sid = match["segment_id"]
            idx = seg_index.get(sid)
            context_before = ""
            context_after = ""
            if idx is not None:
                before_segs = segments[max(0, idx - window) : idx]
                after_segs = segments[idx + 1 : idx + 1 + window]
                context_before = " ".join(s["text"] for s in before_segs)
                context_after = " ".join(s["text"] for s in after_segs)
            expanded.append({
                **match,
                "context_before": context_before,
                "context_after": context_after,
            })
        expanded_evidence[theme] = expanded

    logger.info("expand_context_node: expanded context for %s themes", len(expanded_evidence))

    with SessionLocal() as db:
        job = db.get(Job, job_id)
        update_job_progress(db, job, "expand_context", "context expansion complete")

    return {"expanded_evidence": expanded_evidence, "current_step": "context_expanded"}


def write_theme_intros_node(state: EssayGraphState) -> dict[str, Any]:
    settings = _get_settings()
    themes = state["themes"]
    evidence = state["evidence"]
    book_summary = state.get("book_summary", "")
    job_id = state["job_id"]

    with SessionLocal() as db:
        job = db.get(Job, job_id)
        update_job_progress(db, job, "write_theme_intros", "writing theme introductions")

    llm = ChatOpenAI(
        model=settings.openai_chat_model,
        api_key=settings.openai_api_key,
        temperature=0.3,
    )

    theme_intros: dict[str, str] = {}
    for i, theme in enumerate(themes):
        with SessionLocal() as db:
            job = db.get(Job, job_id)
            update_job_progress(
                db, job, "write_theme_intros",
                f"writing introduction {i + 1}/{len(themes)}: {theme}"
            )

        snippets = evidence.get(theme, [])
        evidence_text = "\n".join(
            f"- [{s['segment_id']}] {s['text']}" for s in snippets[:5]
        )

        prompt = THEME_INTRO_USER.format(
            book_summary=book_summary,
            theme=theme,
            evidence_snippets=evidence_text,
        )
        response = llm.invoke([
            {"role": "system", "content": THEME_INTRO_SYSTEM},
            {"role": "user", "content": prompt},
        ])
        theme_intros[theme] = response.content
        logger.info("write_theme_intros_node: wrote intro for theme '%s'", theme)

    with SessionLocal() as db:
        job = db.get(Job, job_id)
        update_job_progress(
            db, job, "write_theme_intros",
            f"wrote {len(theme_intros)} theme introductions"
        )

    return {"theme_intros": theme_intros, "current_step": "theme_intros_written"}


def draft_essay_node(state: EssayGraphState) -> dict[str, Any]:
    settings = _get_settings()
    themes = state["themes"]
    expanded_evidence = state.get("expanded_evidence", {})
    evidence = state["evidence"]
    book_summary = state.get("book_summary", "")
    theme_intros = state.get("theme_intros", {})
    job_id = state["job_id"]

    with SessionLocal() as db:
        job = db.get(Job, job_id)
        doc = db.get(Document, state["document_id"])
        title = state.get("title") or (doc.title if doc else "Unknown Title")
        author = state.get("author") or (doc.author if doc else "Unknown Author")
        update_job_progress(db, job, "draft_essay", "generating essay draft")

    # Use expanded evidence if available, fall back to basic evidence
    if expanded_evidence:
        evidence_block = _build_expanded_evidence_block(themes, expanded_evidence)
    else:
        evidence_block = _build_evidence_block(themes, evidence)

    theme_intros_block = _build_theme_intros_block(themes, theme_intros)

    llm = ChatOpenAI(
        model=settings.openai_chat_model,
        api_key=settings.openai_api_key,
        temperature=0.3,
    )
    prompt = ESSAY_DRAFT_USER.format(
        title=title,
        author=author,
        book_summary=book_summary,
        theme_intros_block=theme_intros_block,
        evidence_block=evidence_block,
    )
    response = llm.invoke([
        {"role": "system", "content": ESSAY_DRAFT_SYSTEM},
        {"role": "user", "content": prompt},
    ])

    essay = response.content
    logger.info("draft_essay_node: drafted essay for %s themes", len(themes))

    with SessionLocal() as db:
        job = db.get(Job, job_id)
        update_job_progress(db, job, "draft_essay", "essay draft complete")

    return {
        "essay_markdown": essay,
        "revision_count": state.get("revision_count", 0),
        "current_step": "essay_drafted",
    }


def review_essay_node(state: EssayGraphState) -> dict[str, Any]:
    settings = _get_settings()
    themes = state["themes"]
    essay = state["essay_markdown"]
    job_id = state["job_id"]
    revision_count = state.get("revision_count", 0)

    with SessionLocal() as db:
        job = db.get(Job, job_id)
        update_job_progress(db, job, "review_essay", f"reviewing essay (revision {revision_count})")

    llm = ChatOpenAI(
        model=settings.openai_chat_model,
        api_key=settings.openai_api_key,
        temperature=0.1,
    )
    prompt = REVIEW_USER.format(themes=", ".join(themes), essay=essay)
    response = llm.invoke([
        {"role": "system", "content": REVIEW_SYSTEM},
        {"role": "user", "content": prompt},
    ])

    raw = response.content
    try:
        review = json.loads(raw)
        approved = bool(review.get("approved", False))
        feedback = review.get("feedback", "")
    except json.JSONDecodeError:
        approved = "approved" in raw.lower() and "true" in raw.lower()
        feedback = raw

    logger.info("review_essay_node: approved=%s revision_count=%s", approved, revision_count)

    with SessionLocal() as db:
        job = db.get(Job, job_id)
        status = "approved" if approved else f"needs revision ({feedback[:80]}...)"
        update_job_progress(db, job, "review_essay", status)

    return {
        "essay_approved": approved,
        "review_feedback": feedback,
        "current_step": "essay_reviewed",
    }


def revise_essay_node(state: EssayGraphState) -> dict[str, Any]:
    settings = _get_settings()
    themes = state["themes"]
    evidence = state["evidence"]
    essay = state["essay_markdown"]
    feedback = state["review_feedback"]
    revision_count = state.get("revision_count", 0)
    job_id = state["job_id"]

    with SessionLocal() as db:
        job = db.get(Job, job_id)
        update_job_progress(db, job, "revise_essay", f"revising essay (attempt {revision_count + 1})")

    evidence_block = _build_evidence_block(themes, evidence)

    llm = ChatOpenAI(
        model=settings.openai_chat_model,
        api_key=settings.openai_api_key,
        temperature=0.3,
    )
    prompt = REVISE_USER.format(feedback=feedback, essay=essay, evidence_block=evidence_block)
    response = llm.invoke([
        {"role": "system", "content": REVISE_SYSTEM},
        {"role": "user", "content": prompt},
    ])

    revised = response.content
    logger.info("revise_essay_node: revised essay revision_count=%s", revision_count + 1)

    with SessionLocal() as db:
        job = db.get(Job, job_id)
        update_job_progress(db, job, "revise_essay", "revision complete")

    return {
        "essay_markdown": revised,
        "revision_count": revision_count + 1,
        "current_step": "essay_revised",
    }


def persist_results_node(state: EssayGraphState) -> dict[str, Any]:
    job_id = state["job_id"]
    themes = state["themes"]
    evidence = state["evidence"]
    essay = state["essay_markdown"]
    book_summary = state.get("book_summary", "")

    with SessionLocal() as db:
        job = db.get(Job, job_id)
        update_job_progress(db, job, "persist_results", "saving results")

        db.add(JobArtifact(job_id=job_id, artifact_type="themes_json", blob_json={"themes": themes}))
        db.add(JobArtifact(job_id=job_id, artifact_type="evidence_json", blob_json=evidence))
        db.add(JobArtifact(job_id=job_id, artifact_type="essay_md", blob_text=essay))
        if book_summary:
            db.add(JobArtifact(job_id=job_id, artifact_type="summary_md", blob_text=book_summary))
        db.commit()

        from app.queue import mark_job_succeeded
        mark_job_succeeded(db, job)
        logger.info("persist_results_node: saved artifacts job_id=%s", job_id)

    return {"current_step": "completed"}
