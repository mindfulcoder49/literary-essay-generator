from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import select, update, or_
from sqlalchemy.orm import Session

from app.models import Job


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


def update_job_progress(db: Session, job: Job, step: str, detail: str):
    job.progress = {"current_step": step, "detail": detail}
    db.add(job)
    db.commit()
