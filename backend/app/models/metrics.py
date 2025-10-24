"""Daily metrics aggregates."""
from __future__ import annotations

import uuid
from datetime import datetime, date
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from .tenant import Tenant


class MetricsDaily(Base):
    """Stores per-day metric aggregates for a tenant."""

    __tablename__ = "metrics_daily"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), primary_key=True
    )
    metric_date: Mapped[date] = mapped_column(Date, primary_key=True)
    metric_name: Mapped[str] = mapped_column(String(length=50), primary_key=True)
    value: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    tenant: Mapped["Tenant"] = relationship(back_populates="metrics_daily")
