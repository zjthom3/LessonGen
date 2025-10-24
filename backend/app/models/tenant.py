"""Tenant data model."""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from datetime import datetime

from sqlalchemy import DateTime, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from .district import District
    from .gen_job import GenerationJob
    from .lms import LMSConnection
    from .lesson import Lesson
    from .event import Event
    from .metrics import MetricsDaily
    from .share import Share
    from .user import User


class Tenant(Base):
    """Represents an organizational tenant within LessonGen."""

    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(length=255), nullable=False, unique=True)
    plan: Mapped[str] = mapped_column(String(length=50), default="district", nullable=False)
    metadata_json: Mapped[dict[str, object]] = mapped_column(
        "metadata", JSON, default=dict, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    districts: Mapped[list["District"]] = relationship(
        back_populates="tenant", cascade="all, delete-orphan"
    )
    users: Mapped[list["User"]] = relationship(
        back_populates="tenant", cascade="all, delete-orphan"
    )
    lessons: Mapped[list["Lesson"]] = relationship(
        back_populates="tenant", cascade="all, delete-orphan"
    )
    generation_jobs: Mapped[list["GenerationJob"]] = relationship(
        "GenerationJob",
        back_populates="tenant",
    )
    lms_connections: Mapped[list["LMSConnection"]] = relationship(
        "LMSConnection",
        back_populates="tenant",
        cascade="all, delete-orphan",
    )
    events: Mapped[list["Event"]] = relationship(
        "Event",
        back_populates="tenant",
        cascade="all, delete-orphan",
    )
    metrics_daily: Mapped[list["MetricsDaily"]] = relationship(
        "MetricsDaily",
        back_populates="tenant",
        cascade="all, delete-orphan",
    )
    shares: Mapped[list["Share"]] = relationship(
        "Share",
        back_populates="tenant",
        cascade="all, delete-orphan",
    )
