"""Services for producing analytics summaries."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Dict
import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Lesson, MetricsDaily


@dataclass(slots=True)
class AnalyticsSummary:
    lessons_created: int
    lessons_generated: int
    lessons_differentiated: int
    exports: int
    lms_pushes: int
    total_lessons: int
    estimated_time_saved_minutes: int


class AnalyticsService:
    """Aggregates metrics for dashboards."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_summary(self, tenant_id: uuid.UUID, days: int = 30) -> AnalyticsSummary:
        start_date = dt.date.today() - dt.timedelta(days=days - 1)
        metrics_stmt = (
            select(
                MetricsDaily.metric_name,
                func.coalesce(func.sum(MetricsDaily.value), 0),
            )
            .where(
                MetricsDaily.tenant_id == tenant_id,
                MetricsDaily.metric_date >= start_date,
            )
            .group_by(MetricsDaily.metric_name)
        )
        aggregated: Dict[str, int] = {row[0]: int(row[1]) for row in self.session.execute(metrics_stmt)}

        total_lessons = self.session.execute(
            select(func.count(Lesson.id)).where(Lesson.tenant_id == tenant_id)
        ).scalar_one()

        time_saved_minutes = aggregated.get("lessons_generated", 0) * 30

        return AnalyticsSummary(
            lessons_created=aggregated.get("lessons_created", 0),
            lessons_generated=aggregated.get("lessons_generated", 0),
            lessons_differentiated=aggregated.get("lessons_differentiated", 0),
            exports=aggregated.get("exports", 0),
            lms_pushes=aggregated.get("lms_pushes", 0),
            total_lessons=total_lessons,
            estimated_time_saved_minutes=time_saved_minutes,
        )
