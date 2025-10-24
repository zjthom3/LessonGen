"""District data model."""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from .school import School
    from .tenant import Tenant
    from .user import User


class District(Base):
    """Represents a school district under a tenant."""

    __tablename__ = "districts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(length=255), nullable=False)

    tenant: Mapped["Tenant"] = relationship(back_populates="districts")
    schools: Mapped[list["School"]] = relationship(
        back_populates="district", cascade="all, delete-orphan"
    )
    users: Mapped[list["User"]] = relationship(
        back_populates="district", cascade="all, delete-orphan"
    )
