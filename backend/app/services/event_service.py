"""Service helpers for logging analytics events."""
from __future__ import annotations

import datetime as dt
import uuid
from collections import defaultdict
from typing import Mapping

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Event, MetricsDaily


METRIC_ACTION_MAP: Mapping[str, str] = {
    "lesson_created": "lessons_created",
    "lesson_generated": "lessons_generated",
    "lesson_differentiated": "lessons_differentiated",
    "lesson_exported": "exports",
    "lms_push": "lms_pushes",
    "lesson_shared": "shares_created",
}


class EventService:
    """Persists events and updates daily metrics."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def log_event(
        self,
        *,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID | None,
        action: str,
        metadata: dict[str, object] | None = None,
    ) -> Event:
        event = Event(
            tenant_id=tenant_id,
            user_id=user_id,
            action=action,
            metadata_json=metadata or {},
        )
        self.session.add(event)
        self._increment_metric(tenant_id, action)
        return event

    def _increment_metric(self, tenant_id: uuid.UUID, action: str) -> None:
        metric_name = METRIC_ACTION_MAP.get(action)
        if not metric_name:
            return

        today = dt.date.today()
        stmt = select(MetricsDaily).where(
            MetricsDaily.tenant_id == tenant_id,
            MetricsDaily.metric_date == today,
            MetricsDaily.metric_name == metric_name,
        )
        metrics_row = self.session.execute(stmt).scalar_one_or_none()
        if metrics_row is None:
            metrics_row = MetricsDaily(
                tenant_id=tenant_id,
                metric_date=today,
                metric_name=metric_name,
                value=1,
            )
            self.session.add(metrics_row)
            return

        metrics_row.value += 1
