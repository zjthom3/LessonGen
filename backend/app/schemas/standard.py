"""Schemas for standards responses."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class StandardsFrameworkRead(BaseModel):
    id: UUID
    code: str
    name: str
    jurisdiction: str | None
    language: str

    class Config:
        from_attributes = True


class StandardRead(BaseModel):
    id: UUID
    framework_id: UUID
    code: str
    grade_band: str | None
    subject: str
    description: str
    tags: list[str] = Field(default_factory=list)
    framework: StandardsFrameworkRead | None = None

    class Config:
        from_attributes = True
