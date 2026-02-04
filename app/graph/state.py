from __future__ import annotations

from typing import TypedDict


class EssayGraphState(TypedDict, total=False):
    # Inputs
    job_id: str
    document_id: str
    gutenberg_id: int
    title: str | None
    author: str | None
    pinecone_namespace: str

    # Ingest outputs
    segments: list[dict]
    segment_count: int
    ingest_complete: bool

    # Theme outputs
    themes: list[str]

    # Evidence outputs
    evidence: dict[str, list[dict]]

    # Essay outputs
    essay_markdown: str
    essay_approved: bool
    revision_count: int
    review_feedback: str

    # Book summary
    book_summary: str

    # Expanded evidence with surrounding context
    expanded_evidence: dict[str, list[dict]]

    # Per-theme introductions
    theme_intros: dict[str, str]

    # Summarization progress
    chunks_summarized: int

    # Progress
    current_step: str
    error: str | None
