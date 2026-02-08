from __future__ import annotations

import asyncio
import hashlib
import json
from uuid import UUID
from pathlib import Path
from time import perf_counter

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.routing import APIRouter
from fastapi.staticfiles import StaticFiles
import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from sse_starlette.sse import EventSourceResponse

from app.config import get_settings
from app.db import get_db, SessionLocal
from app.gutenberg import fetch_gutenberg_metadata, fetch_gutenberg_text, normalize_gutenberg_text, search_gutenberg
from app.logging_config import configure_logging, log_startup_config
from app.models import Document, Job, JobArtifact
from app.schemas import JobCreateRequest, JobResultResponse, JobStatusResponse, GutenbergSearchResponse

app = FastAPI(title=get_settings().app_name)
logger = configure_logging("api", "api.log")

api = APIRouter(prefix="/api")


@app.on_event("startup")
def on_startup():
    settings = get_settings()
    log_startup_config(logger, settings)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = perf_counter()
    response = await call_next(request)
    duration_ms = int((perf_counter() - start) * 1000)
    logger.info(
        "request %s %s -> %s (%sms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


def _ensure_document(db: Session, gutenberg_id: int) -> Document:
    logger.info("ensure_document: gutenberg_id=%s", gutenberg_id)
    raw = fetch_gutenberg_text(gutenberg_id)
    normalized = normalize_gutenberg_text(raw)
    content_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    existing = db.execute(
        select(Document).where(Document.canonical_hash == content_hash)
    ).scalars().first()
    if existing:
        if existing.title is None or existing.author is None:
            meta = fetch_gutenberg_metadata(gutenberg_id)
            if existing.title is None:
                existing.title = meta.get("title")
            if existing.author is None:
                existing.author = meta.get("author")
            db.add(existing)
            db.commit()
            db.refresh(existing)
        return existing

    meta = fetch_gutenberg_metadata(gutenberg_id)
    namespace = f"gb:{gutenberg_id}:{content_hash[:8]}"
    doc = Document(
        source_type="gutenberg",
        source_ref=str(gutenberg_id),
        canonical_hash=content_hash,
        title=meta.get("title"),
        author=meta.get("author"),
        ingest_status="pending",
        pinecone_namespace=namespace,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


# --- API routes ---


@api.get("/health")
def health():
    return {"status": "ok"}


@api.get("/gutenberg/search", response_model=GutenbergSearchResponse)
def gutenberg_search(q: str):
    logger.info("gutenberg search: %s", q)
    data = search_gutenberg(q)
    return {"count": data.get("count", 0), "results": data.get("results", [])}


@api.get("/jobs")
def list_jobs(db: Session = Depends(get_db)):
    logger.info("list jobs")
    jobs = db.execute(
        select(Job.id, Job.status, Job.created_at, Document.title, Document.author)
        .join(Document, Job.document_id == Document.id)
        .where(Job.status.in_(["succeeded", "running", "queued"]))
        .order_by(
            # Running/queued first, then succeeded
            sa.case(
                (Job.status == "running", 0),
                (Job.status == "queued", 1),
                else_=2,
            ),
            Job.created_at.desc(),
        )
        .limit(20)
    ).all()
    return {
        "jobs": [
            {
                "id": str(job_id),
                "status": status,
                "title": title,
                "author": author,
            }
            for job_id, status, created_at, title, author in jobs
        ]
    }


@api.post("/jobs", response_model=JobStatusResponse)
def create_job(payload: JobCreateRequest, db: Session = Depends(get_db)):
    logger.info("create job: gutenberg_id=%s", payload.gutenberg_id)
    document = _ensure_document(db, payload.gutenberg_id)

    job = Job(
        document_id=document.id,
        job_type="essay_pipeline",
        status="queued",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    return JobStatusResponse(
        id=job.id,
        status=job.status,
        job_type=job.job_type,
        progress=job.progress,
        created_at=job.created_at,
        started_at=job.started_at,
        finished_at=job.finished_at,
    )


@api.post("/jobs/{job_id}/resume")
def resume_job(job_id: UUID, db: Session = Depends(get_db)):
    """Requeue a running job that was interrupted (e.g., by Fly.io auto-stop).

    Only affects jobs with status 'running'. Returns the updated job status.
    If the job is already queued or completed, this is a no-op.
    """
    logger.info("resume job: %s", job_id)
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status == "running":
        job.status = "queued"
        job.started_at = None
        db.commit()
        db.refresh(job)
        logger.info("requeued stalled job %s", job_id)

    return {"status": job.status, "requeued": job.status == "queued"}


@api.get("/jobs/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: UUID, db: Session = Depends(get_db)):
    logger.info("job status: %s", job_id)
    stmt = select(Job).options(joinedload(Job.document)).where(Job.id == job_id)
    job = db.execute(stmt).scalars().first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    book_summary = None
    if job.document:
        book_summary = job.document.summary

    return JobStatusResponse(
        id=job.id,
        status=job.status,
        job_type=job.job_type,
        progress=job.progress,
        created_at=job.created_at,
        started_at=job.started_at,
        finished_at=job.finished_at,
        book_summary=book_summary,
    )


@api.get("/jobs/{job_id}/result", response_model=JobResultResponse)
def get_job_result(job_id: UUID, db: Session = Depends(get_db)):
    logger.info("job result: %s", job_id)
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "succeeded":
        raise HTTPException(status_code=400, detail="Job not completed")

    artifacts = db.execute(
        select(JobArtifact).where(JobArtifact.job_id == job.id)
    ).scalars().all()

    themes = []
    evidence = {}
    essay = ""
    book_summary = ""
    for artifact in artifacts:
        if artifact.artifact_type == "themes_json" and artifact.blob_json:
            themes = artifact.blob_json.get("themes", [])
        if artifact.artifact_type == "evidence_json" and artifact.blob_json:
            evidence = artifact.blob_json
        if artifact.artifact_type == "essay_md" and artifact.blob_text:
            essay = artifact.blob_text
        if artifact.artifact_type == "summary_md" and artifact.blob_text:
            book_summary = artifact.blob_text

    return JobResultResponse(
        job_id=job.id, themes=themes, evidence=evidence,
        essay_markdown=essay, book_summary=book_summary,
    )


def _get_job_progress(job_id: UUID) -> dict | None:
    with SessionLocal() as db:
        job = db.get(Job, job_id)
        if not job:
            return None
        return {
            "status": job.status,
            "progress": job.progress or {},
        }


@api.get("/jobs/{job_id}/stream")
async def job_stream(job_id: UUID):
    async def event_generator():
        last_step = None
        last_detail = None
        last_summary = None
        heartbeat_counter = 0
        while True:
            job_info = await asyncio.to_thread(_get_job_progress, job_id)
            if not job_info:
                yield {"event": "error", "data": "Job not found"}
                return

            progress = job_info.get("progress", {})
            current_step = progress.get("current_step")
            detail = progress.get("detail", "")
            running_summary = progress.get("running_summary", "")

            changed = (
                current_step
                and (
                    current_step != last_step
                    or detail != last_detail
                    or running_summary != last_summary
                )
            )

            if changed:
                event_data: dict[str, str] = {"step": current_step, "detail": detail}
                if running_summary:
                    event_data["running_summary"] = running_summary
                yield {
                    "event": "progress",
                    "data": json.dumps(event_data),
                }
                last_step = current_step
                last_detail = detail
                last_summary = running_summary
                heartbeat_counter = 0
            else:
                # Send a heartbeat comment every ~30s (15 cycles * 2s)
                # to keep the connection alive through proxies
                heartbeat_counter += 1
                if heartbeat_counter >= 15:
                    yield {"comment": "heartbeat"}
                    heartbeat_counter = 0

            job_status = job_info.get("status")
            if job_status in ("succeeded", "failed"):
                yield {
                    "event": "done",
                    "data": json.dumps({"status": job_status}),
                }
                return

            await asyncio.sleep(2)

    return EventSourceResponse(event_generator())


# Mount API router
app.include_router(api)

# Mount admin router (before SPA catch-all)
from app.admin_routes import admin_router
app.include_router(admin_router)

# Serve Vue SPA with catch-all fallback to index.html for client-side routing.
# StaticFiles(html=True) does NOT handle SPA fallback — it only serves
# index.html for the root path, so /jobs/:id would 404 on page refresh.
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    # Mount static assets (JS, CSS, images, etc.) so they're served directly
    assets_dir = static_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve static files if they exist, otherwise serve index.html for SPA routing."""
        file_path = static_dir / full_path
        if full_path and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(static_dir / "index.html")
