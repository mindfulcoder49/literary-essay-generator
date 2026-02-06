from __future__ import annotations

import logging
import threading
from datetime import datetime, timedelta

import httpx
from sqlalchemy import select, update, or_
from sqlalchemy.orm import Session

from app.models import Job

logger = logging.getLogger("queue")


def claim_next_job(db: Session) -> Job | None:
    job = (
        db.execute(
            select(Job)
            .where(Job.status == "queued")
            .where(
                or_(
                    Job.next_attempt_at.is_(None),
                    Job.next_attempt_at <= datetime.utcnow(),
                )
            )
            .order_by(Job.created_at.asc())
            .with_for_update(skip_locked=True)
            .limit(1)
        )
        .scalars()
        .first()
    )
    if not job:
        return None

    job.status = "running"
    job.started_at = datetime.utcnow()
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def mark_job_succeeded(db: Session, job: Job):
    job.status = "succeeded"
    job.finished_at = datetime.utcnow()
    db.add(job)
    db.commit()


def mark_job_failed(db: Session, job: Job, message: str):
    job.status = "failed"
    job.finished_at = datetime.utcnow()
    job.progress = {"error": message}
    db.add(job)
    db.commit()


def mark_job_requeued(db: Session, job: Job, reason: str, delay_seconds: int = 10):
    job.status = "queued"
    job.next_attempt_at = datetime.utcnow() + timedelta(seconds=delay_seconds)
    job.progress = {"requeued": reason, "at": datetime.utcnow().isoformat()}
    db.add(job)
    db.commit()


def _send_keepalive():
    """Send a request to the local web server to keep Fly.io machine alive."""
    try:
        httpx.get("http://127.0.0.1:8080/api/health", timeout=5)
    except Exception as e:
        logger.debug("keepalive ping failed: %s", e)


def update_job_progress(db: Session, job: Job, step: str, detail: str):
    job.progress = {"current_step": step, "detail": detail}
    db.add(job)
    db.commit()
    # Send keepalive in background thread to avoid blocking
    threading.Thread(target=_send_keepalive, daemon=True).start()
