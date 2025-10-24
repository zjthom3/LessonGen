"""School data model."""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from .district import District
    from .user import User


class School(Base):
    """Represents a school within a district."""

    __tablename__ = "schools"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    district_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("districts.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(length=255), nullable=False)
    grade_levels: Mapped[str | None] = mapped_column(String(length=50), nullable=True)

    district: Mapped["District"] = relationship(back_populates="schools")
    users: Mapped[list["User"]] = relationship(
        back_populates="school", cascade="all, delete-orphan"
    )
