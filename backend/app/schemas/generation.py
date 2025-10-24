"""Schemas for generation job endpoints."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.lesson import LessonDetail
from app.schemas.standard import StandardRead


class GenerationRequest(BaseModel):
    subject: str
    grade_level: str
    topic: str
    duration_minutes: int = Field(ge=5, le=180)
    teaching_style: str
    focus_keywords: List[str] = Field(default_factory=list)
    standard_codes: Optional[List[str]] = None


class GenerationJobRead(BaseModel):
    id: UUID
    status: str
    lesson_id: Optional[UUID]
    lesson_version_id: Optional[UUID]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class GenerationResponse(BaseModel):
    job: GenerationJobRead
    lesson: LessonDetail
    standards: List[StandardRead] = Field(default_factory=list)
