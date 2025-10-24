"""Pydantic schemas for lessons and lesson versions."""
from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


JsonList = List[dict[str, Any]]


class LessonVersionBase(BaseModel):
    objective: Optional[str] = None
    duration_minutes: Optional[int] = None
    teacher_script_md: Optional[str] = None
    materials: JsonList = Field(default_factory=list)
    flow: JsonList = Field(default_factory=list)
    differentiation: JsonList = Field(default_factory=list)
    assessments: JsonList = Field(default_factory=list)
    accommodations: JsonList = Field(default_factory=list)
    source: dict[str, Any] = Field(default_factory=dict)
    blocks: JsonList = Field(default_factory=list)

    @field_validator(
        "materials",
        "flow",
        "differentiation",
        "assessments",
        "accommodations",
        "blocks",
        mode="before",
    )
    @classmethod
    def ensure_list(cls, value: Any) -> JsonList:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return list(value)


class LessonCreate(LessonVersionBase):
    title: str
    subject: str
    grade_level: str
    language: str = "en"
    visibility: str = "private"
    status: str = "draft"
    tags: List[str] = Field(default_factory=list)


class LessonVersionCreate(LessonVersionBase):
    status: Optional[str] = None


class LessonVersionRead(LessonVersionBase):
    id: UUID
    lesson_id: UUID
    version_no: int
    created_at: datetime
    created_by_user_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class LessonSummary(BaseModel):
    id: UUID
    title: str
    subject: str
    grade_level: str
    language: str
    status: str
    tags: List[str] = Field(default_factory=list)
    visibility: str
    current_version_id: Optional[UUID] = None
    updated_at: datetime

    class Config:
        from_attributes = True

    @field_validator("tags", mode="before")
    @classmethod
    def ensure_tags(cls, value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]


class LessonDetail(LessonSummary):
    owner_user_id: UUID
    versions: List[LessonVersionRead] = Field(default_factory=list)

    class Config:
        from_attributes = True

    @field_validator("versions", mode="before")
    @classmethod
    def ensure_versions(cls, value: Any) -> List[LessonVersionRead] | Any:
        if value is None:
            return []
        return value


class LessonRestoreResponse(BaseModel):
    lesson_id: UUID
    current_version_id: UUID
    restored_version: int


class LessonDifferentiateRequest(BaseModel):
    audience: str = Field(pattern="^(ELL|IEP|GIFTED)$", description="Differentiation audience")
    notes: Optional[str] = None
