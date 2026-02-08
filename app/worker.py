from __future__ import annotations

import asyncio
import traceback

from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import SessionLocal
from app.graph.builder import build_essay_graph
from app.logging_config import configure_logging, log_startup_config
from app.models import Document, Job
from app.queue import claim_next_job, mark_job_failed, KeepaliveThread

logger = configure_logging("worker", "worker.log")


def build_initial_state(db: Session, job: Job) -> dict:
    document = db.get(Document, job.document_id)
    if not document:
        raise RuntimeError(f"Document {job.document_id} not found")

    return {
        "job_id": job.id,
        "document_id": document.id,
        "gutenberg_id": int(document.source_ref),
        "title": document.title,
        "author": document.author,
        "pinecone_namespace": document.pinecone_namespace,
        "revision_count": 0,
    }


async def process_job(db: Session, job: Job):
    initial_state = build_initial_state(db, job)
    graph = build_essay_graph()
    await asyncio.to_thread(graph.invoke, initial_state)


async def run_worker():
    settings = get_settings()
    log_startup_config(logger, settings)

    while True:
        job = None
        try:
            with SessionLocal() as db:
                job = claim_next_job(db)

            if not job:
                logger.info("no jobs, sleeping")
                await asyncio.sleep(settings.worker_poll_seconds)
                continue

            logger.info("claimed job %s (%s)", job.id, job.job_type)
            with KeepaliveThread(interval=30):
                with SessionLocal() as db:
                    await process_job(db, job)
            logger.info("completed job %s", job.id)
        except Exception as exc:
            logger.error("worker error: %s", exc)
            logger.error(traceback.format_exc())
            if job:
                with SessionLocal() as db:
                    mark_job_failed(db, job, str(exc))
            await asyncio.sleep(settings.worker_poll_seconds)


if __name__ == "__main__":
    asyncio.run(run_worker())
