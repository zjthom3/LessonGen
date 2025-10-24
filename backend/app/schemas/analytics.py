"""Schemas for analytics endpoints."""
from __future__ import annotations

from pydantic import BaseModel, Field


class AnalyticsSummaryResponse(BaseModel):
    lessons_created: int = Field(ge=0)
    lessons_generated: int = Field(ge=0)
    lessons_differentiated: int = Field(ge=0)
    exports: int = Field(ge=0)
    lms_pushes: int = Field(ge=0)
    total_lessons: int = Field(ge=0)
    estimated_time_saved_minutes: int = Field(ge=0)
