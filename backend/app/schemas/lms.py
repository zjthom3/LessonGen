"""Schemas for LMS integration endpoints."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ClassroomConnectRequest(BaseModel):
    access_token: str
    refresh_token: str | None = None
    expires_in: int | None = Field(default=3600, ge=0)
    profile: dict[str, str] | None = None


class ClassroomConnectResponse(BaseModel):
    id: UUID
    provider: str
    created_at: datetime
    expires_at: datetime | None
    profile: dict[str, str] | None = None

    class Config:
        from_attributes = True


class ClassroomPushRequest(BaseModel):
    lesson_id: UUID
    course_id: str
    topic_id: str | None = None
    due_date: datetime | None = None


class ClassroomPushResponse(BaseModel):
    id: UUID
    status: str
    external_assignment_id: str | None
    created_at: datetime

    class Config:
        from_attributes = True
