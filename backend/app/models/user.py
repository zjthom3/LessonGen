"""User data model."""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from .district import District
    from .event import Event
    from .gen_job import GenerationJob
    from .lesson import Lesson
    from .lms import LMSConnection
    from .share import Share
    from .school import School
    from .tenant import Tenant
    from .user_role import UserRole


class User(Base):
    """Represents a user in LessonGen."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    district_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("districts.id", ondelete="SET NULL"), nullable=True
    )
    school_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("schools.id", ondelete="SET NULL"), nullable=True
    )
    email: Mapped[str] = mapped_column(String(length=255), unique=True, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(length=255), nullable=True)
    auth_provider: Mapped[str] = mapped_column(String(length=50), default="google", nullable=False)
    locale: Mapped[str] = mapped_column(String(length=20), default="en-US", nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(length=500), nullable=True)
    metadata_json: Mapped[dict[str, object]] = mapped_column(
        "metadata", JSON, default=dict, nullable=False
    )
    preferred_subjects: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    preferred_grade_levels: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    tenant: Mapped["Tenant"] = relationship(back_populates="users")
    district: Mapped["District | None"] = relationship(back_populates="users")
    school: Mapped["School | None"] = relationship(back_populates="users")
    roles: Mapped[list["UserRole"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )
    lessons: Mapped[list["Lesson"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )
    generation_jobs: Mapped[list["GenerationJob"]] = relationship(
        "GenerationJob",
        back_populates="user",
    )
    lms_connections: Mapped[list["LMSConnection"]] = relationship(
        "LMSConnection",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    events: Mapped[list["Event"]] = relationship(
        "Event",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    shares: Mapped[list["Share"]] = relationship(
        "Share",
        back_populates="created_by",
        cascade="all, delete-orphan",
    )

    def has_role(self, role: str) -> bool:
        """Check if the user has a given role."""

        normalized = role.lower()
        if self.is_superuser:
            return True
        return any(r.role.lower() == normalized for r in self.roles)
