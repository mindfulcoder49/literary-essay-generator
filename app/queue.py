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
    """Send a request through the external domain to keep Fly.io machine alive.

    We must go through the external URL so Fly.io's proxy sees the traffic.
    Internal localhost requests don't prevent auto-stop.
    """
    try:
        httpx.get("https://literary-essays.fly.dev/api/health", timeout=10)
    except Exception as e:
        logger.debug("keepalive ping failed: %s", e)


def send_keepalive():
    """Public function to send a keepalive ping in a background thread."""
    threading.Thread(target=_send_keepalive, daemon=True).start()


class KeepaliveThread:
    """
    Background thread that sends periodic keepalive pings.
    Use as a context manager for long-running operations.

    Example:
        with KeepaliveThread(interval=30):
            # long running LLM call
            result = llm.invoke(...)
    """
    def __init__(self, interval: float = 30.0):
        self.interval = interval
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def _run(self):
        while not self._stop_event.wait(self.interval):
            _send_keepalive()

    def __enter__(self):
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1)
        return False


def update_job_progress(db: Session, job: Job, step: str, detail: str):
    job.progress = {"current_step": step, "detail": detail}
    db.add(job)
    db.commit()
    # Send keepalive in background thread to avoid blocking
    send_keepalive()
