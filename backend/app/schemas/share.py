"""Schemas for share endpoints."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.lesson import LessonVersionRead


class ShareCreateRequest(BaseModel):
    expires_in_hours: int | None = Field(default=72, ge=1)


class ShareCreateResponse(BaseModel):
    token: str
    url: str
    expires_at: datetime | None = None


class SharedLessonResponse(BaseModel):
    lesson_id: UUID
    lesson_version: LessonVersionRead
    expires_at: datetime | None = None
