from __future__ import annotations

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class JobCreateRequest(BaseModel):
    gutenberg_id: int = Field(..., ge=1)


class JobStatusResponse(BaseModel):
    id: UUID
    status: str
    job_type: str
    progress: dict | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    book_summary: str | None = None


class JobResultResponse(BaseModel):
    job_id: UUID
    themes: list[str]
    evidence: dict
    essay_markdown: str
    book_summary: str = ""


class GutenbergSearchResponse(BaseModel):
    count: int
    results: list[dict]
