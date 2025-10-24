"""Lesson and version data models."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from .gen_job import GenerationJob
    from .lms import LMSPush
    from .share import Share
    from .standard import LessonStandard, Standard
    from .tenant import Tenant
    from .user import User


class LessonVersion(Base):
    """Immutable snapshot of lesson content."""

    __tablename__ = "lesson_versions"
    __table_args__ = (
        UniqueConstraint("lesson_id", "version_no", name="ux_lesson_versions_version_no"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    lesson_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False,
    )
    version_no: Mapped[int] = mapped_column(Integer, nullable=False)
    objective: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    teacher_script_md: Mapped[str | None] = mapped_column(Text, nullable=True)
    materials: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list, nullable=False)
    flow: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list, nullable=False)
    differentiation: Mapped[list[dict[str, object]]] = mapped_column(
        JSON, default=list, nullable=False
    )
    assessments: Mapped[list[dict[str, object]]] = mapped_column(
        JSON, default=list, nullable=False
    )
    accommodations: Mapped[list[dict[str, object]]] = mapped_column(
        JSON, default=list, nullable=False
    )
    source: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    lesson: Mapped["Lesson"] = relationship(
        "Lesson",
        back_populates="versions",
        foreign_keys="lesson_versions.c.lesson_id",
    )
    created_by: Mapped["User | None"] = relationship(
        "User", foreign_keys=[created_by_user_id]
    )
    blocks: Mapped[list["LessonBlock"]] = relationship(
        back_populates="version",
        cascade="all, delete-orphan",
        order_by="LessonBlock.sequence",
    )
    standards_links: Mapped[list["LessonStandard"]] = relationship(
        "LessonStandard",
        back_populates="lesson_version",
        cascade="all, delete-orphan",
    )
    standards: Mapped[list["Standard"]] = relationship(
        "Standard",
        secondary="lesson_standards",
        viewonly=True,
    )
    generation_jobs: Mapped[list["GenerationJob"]] = relationship(
        "GenerationJob",
        back_populates="lesson_version",
    )
    shares: Mapped[list["Share"]] = relationship(
        "Share",
        back_populates="lesson_version",
        cascade="all, delete-orphan",
    )
    lms_pushes: Mapped[list["LMSPush"]] = relationship(
        "LMSPush",
        back_populates="lesson_version",
    )


class LessonBlock(Base):
    """Fine-grained content block within a lesson version."""

    __tablename__ = "lesson_blocks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    lesson_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("lesson_versions.id", ondelete="CASCADE"),
        nullable=False,
    )
    block_type: Mapped[str] = mapped_column(String(length=50), nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    content_md: Mapped[str] = mapped_column(Text, nullable=False)
    est_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metadata_json: Mapped[dict[str, object]] = mapped_column(
        "metadata", JSON, default=dict, nullable=False
    )

    version: Mapped["LessonVersion"] = relationship(back_populates="blocks")


class Lesson(Base):
    """Represents a lesson owned by a user within a tenant."""

    __tablename__ = "lessons"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    owner_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(length=255), nullable=False)
    subject: Mapped[str] = mapped_column(String(length=100), nullable=False)
    grade_level: Mapped[str] = mapped_column(String(length=20), nullable=False)
    language: Mapped[str] = mapped_column(String(length=10), nullable=False, default="en")
    status: Mapped[str] = mapped_column(String(length=20), nullable=False, default="draft")
    current_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    visibility: Mapped[str] = mapped_column(String(length=20), nullable=False, default="private")
    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    metadata_json: Mapped[dict[str, object]] = mapped_column(
        "metadata", JSON, default=dict, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    owner: Mapped["User"] = relationship(back_populates="lessons")
    tenant: Mapped["Tenant"] = relationship(back_populates="lessons")
    versions: Mapped[list[LessonVersion]] = relationship(
        LessonVersion,
        back_populates="lesson",
        cascade="all, delete-orphan",
        order_by=LessonVersion.version_no,
        foreign_keys=[LessonVersion.lesson_id],
    )
    generation_jobs: Mapped[list["GenerationJob"]] = relationship(
        "GenerationJob",
        back_populates="lesson",
    )
    lms_pushes: Mapped[list["LMSPush"]] = relationship(
        "LMSPush",
        back_populates="lesson",
        foreign_keys="LMSPush.lesson_id",
    )
    shares: Mapped[list["Share"]] = relationship(
        "Share",
        back_populates="lesson",
        cascade="all, delete-orphan",
    )
