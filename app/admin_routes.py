from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from app.admin_auth import require_admin
from app.db import get_db
from app.models import Document, Job, JobArtifact
from app.pinecone_client import PineconeClient, delete_namespace, list_namespaces

logger = logging.getLogger("admin")

admin_router = APIRouter(
    prefix="/api/admin",
    dependencies=[Depends(require_admin)],
)


# ── Documents ──────────────────────────────────────────────


@admin_router.get("/documents")
def list_documents(db: Session = Depends(get_db)):
    docs = db.execute(
        select(Document).order_by(Document.created_at.desc())
    ).scalars().all()
    return {
        "documents": [
            {
                "id": str(d.id),
                "title": d.title,
                "author": d.author,
                "source_ref": d.source_ref,
                "ingest_status": d.ingest_status,
                "has_summary": d.summary is not None,
                "pinecone_namespace": d.pinecone_namespace,
                "created_at": d.created_at.isoformat() if d.created_at else None,
            }
            for d in docs
        ]
    }


@admin_router.delete("/documents/{doc_id}/summary")
def delete_document_summary(doc_id: UUID, db: Session = Depends(get_db)):
    doc = db.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    doc.summary = None
    doc.summary_chunk_count = 0
    db.commit()
    return {"ok": True}


@admin_router.delete("/documents/{doc_id}/vectors")
def delete_document_vectors(doc_id: UUID, db: Session = Depends(get_db)):
    doc = db.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    try:
        pc = PineconeClient()
        delete_namespace(pc, doc.pinecone_namespace)
    except Exception:
        logger.exception("Failed to delete Pinecone namespace %s", doc.pinecone_namespace)
    doc.ingest_status = "pending"
    db.commit()
    return {"ok": True}


@admin_router.delete("/documents/{doc_id}")
def delete_document(doc_id: UUID, db: Session = Depends(get_db)):
    doc = db.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    # Delete Pinecone namespace
    try:
        pc = PineconeClient()
        delete_namespace(pc, doc.pinecone_namespace)
    except Exception:
        logger.exception("Failed to delete Pinecone namespace %s", doc.pinecone_namespace)
    # Delete artifacts for all jobs of this document
    job_ids = [j.id for j in doc.jobs]
    if job_ids:
        db.execute(delete(JobArtifact).where(JobArtifact.job_id.in_(job_ids)))
        db.execute(delete(Job).where(Job.id.in_(job_ids)))
    db.delete(doc)
    db.commit()
    return {"deleted": 1}


# ── Jobs ───────────────────────────────────────────────────


@admin_router.get("/jobs")
def list_jobs(db: Session = Depends(get_db)):
    rows = db.execute(
        select(Job.id, Job.status, Job.created_at, Document.title, Document.author)
        .join(Document, Job.document_id == Document.id)
        .order_by(Job.created_at.desc())
    ).all()
    return {
        "jobs": [
            {
                "id": str(job_id),
                "status": status,
                "title": title,
                "author": author,
                "created_at": created_at.isoformat() if created_at else None,
            }
            for job_id, status, created_at, title, author in rows
        ]
    }


@admin_router.delete("/jobs/{job_id}")
def delete_job(job_id: UUID, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.execute(delete(JobArtifact).where(JobArtifact.job_id == job.id))
    db.delete(job)
    db.commit()
    return {"deleted": 1}


# ── Orphan Pinecone namespaces ─────────────────────────────


@admin_router.get("/orphan-namespaces")
def get_orphan_namespaces(db: Session = Depends(get_db)):
    try:
        pc = PineconeClient()
        all_ns = list_namespaces(pc)
    except Exception:
        logger.exception("Failed to list Pinecone namespaces")
        return {"namespaces": []}
    # Get all namespaces tracked in the database
    db_namespaces = set(
        db.execute(select(Document.pinecone_namespace)).scalars().all()
    )
    orphans = [
        {"namespace": ns, "vector_count": count}
        for ns, count in sorted(all_ns.items())
        if ns and ns not in db_namespaces
    ]
    return {"namespaces": orphans}


@admin_router.delete("/orphan-namespaces/{namespace:path}")
def delete_orphan_namespace(namespace: str):
    try:
        pc = PineconeClient()
        delete_namespace(pc, namespace)
    except Exception:
        logger.exception("Failed to delete orphan namespace %s", namespace)
        raise HTTPException(status_code=500, detail="Failed to delete namespace")
    return {"deleted": 1}


@admin_router.post("/bulk/delete-orphan-namespaces")
def bulk_delete_orphan_namespaces(db: Session = Depends(get_db)):
    try:
        pc = PineconeClient()
        all_ns = list_namespaces(pc)
    except Exception:
        logger.exception("Failed to list Pinecone namespaces")
        return {"deleted": 0}
    db_namespaces = set(
        db.execute(select(Document.pinecone_namespace)).scalars().all()
    )
    count = 0
    for ns in all_ns:
        if ns and ns not in db_namespaces:
            try:
                delete_namespace(pc, ns)
                count += 1
            except Exception:
                logger.exception("Failed to delete orphan namespace %s", ns)
    return {"deleted": count}


# ── Bulk operations ───────────────────────────────────────


class BulkDeleteJobsRequest(BaseModel):
    status: str = "all"


@admin_router.post("/bulk/delete-jobs")
def bulk_delete_jobs(body: BulkDeleteJobsRequest, db: Session = Depends(get_db)):
    query = select(Job.id)
    if body.status != "all":
        query = query.where(Job.status == body.status)
    job_ids = db.execute(query).scalars().all()
    if job_ids:
        db.execute(delete(JobArtifact).where(JobArtifact.job_id.in_(job_ids)))
        db.execute(delete(Job).where(Job.id.in_(job_ids)))
    db.commit()
    return {"deleted": len(job_ids)}


@admin_router.post("/bulk/delete-summaries")
def bulk_delete_summaries(db: Session = Depends(get_db)):
    docs = db.execute(select(Document).where(Document.summary.isnot(None))).scalars().all()
    count = 0
    for doc in docs:
        doc.summary = None
        doc.summary_chunk_count = 0
        count += 1
    db.commit()
    return {"deleted": count}


@admin_router.post("/bulk/delete-vectors")
def bulk_delete_vectors(db: Session = Depends(get_db)):
    docs = db.execute(select(Document)).scalars().all()
    pc = None
    try:
        pc = PineconeClient()
    except Exception:
        logger.exception("Failed to create PineconeClient")
    count = 0
    for doc in docs:
        if pc:
            try:
                delete_namespace(pc, doc.pinecone_namespace)
            except Exception:
                logger.exception("Failed to delete namespace %s", doc.pinecone_namespace)
        doc.ingest_status = "pending"
        count += 1
    db.commit()
    return {"deleted": count}


@admin_router.post("/bulk/nuke")
def bulk_nuke(db: Session = Depends(get_db)):
    # Delete all Pinecone namespaces
    docs = db.execute(select(Document)).scalars().all()
    pc = None
    try:
        pc = PineconeClient()
    except Exception:
        logger.exception("Failed to create PineconeClient")
    for doc in docs:
        if pc:
            try:
                delete_namespace(pc, doc.pinecone_namespace)
            except Exception:
                logger.exception("Failed to delete namespace %s", doc.pinecone_namespace)
        doc.summary = None
        doc.summary_chunk_count = 0
        doc.ingest_status = "pending"
    # Delete all jobs and artifacts
    db.execute(delete(JobArtifact))
    db.execute(delete(Job))
    db.commit()
    return {"ok": True}
