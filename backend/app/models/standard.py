"""Standards data models."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from .lesson import LessonVersion


class StandardsFramework(Base):
    """Catalog of academic standards frameworks (e.g., CCSS, NGSS)."""

    __tablename__ = "standards_frameworks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(String(length=50), nullable=False)
    name: Mapped[str] = mapped_column(String(length=255), nullable=False)
    jurisdiction: Mapped[str | None] = mapped_column(String(length=100), nullable=True)
    language: Mapped[str] = mapped_column(String(length=10), nullable=False, default="en")
    metadata_json: Mapped[dict[str, object]] = mapped_column(
        "metadata", JSON, default=dict, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    standards: Mapped[list["Standard"]] = relationship(
        back_populates="framework", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("code", "jurisdiction", name="ux_framework_code_jurisdiction"),
    )


class Standard(Base):
    """Represents a specific academic standard entry."""

    __tablename__ = "standards"
    __table_args__ = (
        UniqueConstraint("framework_id", "code", name="ux_standard_framework_code"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    framework_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("standards_frameworks.id", ondelete="CASCADE"),
        nullable=False,
    )
    code: Mapped[str] = mapped_column(String(length=100), nullable=False)
    grade_band: Mapped[str | None] = mapped_column(String(length=20), nullable=True)
    subject: Mapped[str] = mapped_column(String(length=100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    metadata_json: Mapped[dict[str, object]] = mapped_column(
        "metadata", JSON, default=dict, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    framework: Mapped["StandardsFramework"] = relationship(back_populates="standards")
    lesson_links: Mapped[list["LessonStandard"]] = relationship(
        back_populates="standard", cascade="all, delete-orphan"
    )


class LessonStandard(Base):
    """Association between lesson versions and aligned standards."""

    __tablename__ = "lesson_standards"

    lesson_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("lesson_versions.id", ondelete="CASCADE"),
        primary_key=True,
    )
    standard_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("standards.id", ondelete="CASCADE"),
        primary_key=True,
    )
    aligned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    lesson_version: Mapped["LessonVersion"] = relationship(back_populates="standards_links")
    standard: Mapped["Standard"] = relationship(back_populates="lesson_links")
