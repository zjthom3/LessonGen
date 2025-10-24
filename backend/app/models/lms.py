"""Models for LMS connections and pushes."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from .gen_job import GenerationJob
    from .lesson import Lesson, LessonVersion
    from .tenant import Tenant
    from .user import User


class LMSConnection(Base):
    """Stores OAuth connection metadata for an LMS provider."""

    __tablename__ = "lms_connections"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    provider: Mapped[str] = mapped_column(String(length=50), nullable=False)
    access_token: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_json: Mapped[dict[str, object]] = mapped_column(
        "metadata", JSON, default=dict, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    tenant: Mapped["Tenant"] = relationship(back_populates="lms_connections")
    user: Mapped["User"] = relationship(back_populates="lms_connections")
    pushes: Mapped[list["LMSPush"]] = relationship(
        back_populates="connection", cascade="all, delete-orphan"
    )


class LMSPush(Base):
    """Tracks assignments or pushes made to an LMS provider."""

    __tablename__ = "lms_pushes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    connection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lms_connections.id", ondelete="CASCADE"), nullable=False
    )
    lesson_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="SET NULL"), nullable=True
    )
    lesson_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lesson_versions.id", ondelete="SET NULL"), nullable=True
    )
    provider: Mapped[str] = mapped_column(String(length=50), nullable=False)
    status: Mapped[str] = mapped_column(String(length=20), nullable=False, default="pending")
    course_id: Mapped[str] = mapped_column(String(length=100), nullable=False)
    topic_id: Mapped[str | None] = mapped_column(String(length=100), nullable=True)
    external_assignment_id: Mapped[str | None] = mapped_column(String(length=255), nullable=True)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict[str, object]] = mapped_column(
        "metadata", JSON, default=dict, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    connection: Mapped["LMSConnection"] = relationship(back_populates="pushes")
    lesson: Mapped["Lesson | None"] = relationship(
        "Lesson",
        back_populates="lms_pushes",
        foreign_keys=[lesson_id],
    )
    lesson_version: Mapped["LessonVersion | None"] = relationship(
        back_populates="lms_pushes", foreign_keys=[lesson_version_id]
    )
