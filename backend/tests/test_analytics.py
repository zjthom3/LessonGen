"""Tests for analytics summary endpoint."""
from __future__ import annotations

import datetime as dt

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.lesson import Lesson
from app.models.metrics import MetricsDaily
from app.models.user import User

from .helpers import ensure_user, login_user


def test_analytics_summary_aggregates_recent_metrics(
    client: TestClient, db_session: Session, fake_google_oauth
) -> None:
    user_id = ensure_user(db_session, "analytics.teacher@example.edu")
    login_user(client, fake_google_oauth, "analytics.teacher@example.edu")

    user = db_session.get(User, user_id)
    assert user is not None

    # Seed lessons for total count.
    for idx in range(2):
        lesson = Lesson(
            tenant_id=user.tenant_id,
            owner_user_id=user.id,
            title=f"Lesson {idx}",
            subject="Science",
            grade_level="5",
            language="en",
            status="draft",
            visibility="private",
            tags=[],
        )
        db_session.add(lesson)

    today = dt.date.today()
    recent_metrics = [
        MetricsDaily(
            tenant_id=user.tenant_id,
            metric_date=today,
            metric_name="lessons_created",
            value=3,
        ),
        MetricsDaily(
            tenant_id=user.tenant_id,
            metric_date=today - dt.timedelta(days=1),
            metric_name="lessons_created",
            value=2,
        ),
        MetricsDaily(
            tenant_id=user.tenant_id,
            metric_date=today,
            metric_name="lessons_generated",
            value=4,
        ),
        MetricsDaily(
            tenant_id=user.tenant_id,
            metric_date=today,
            metric_name="lessons_differentiated",
            value=1,
        ),
        MetricsDaily(
            tenant_id=user.tenant_id,
            metric_date=today,
            metric_name="exports",
            value=5,
        ),
        MetricsDaily(
            tenant_id=user.tenant_id,
            metric_date=today,
            metric_name="lms_pushes",
            value=2,
        ),
    ]
    db_session.add_all(recent_metrics)

    # Metric outside of the requested window should be ignored.
    db_session.add(
        MetricsDaily(
            tenant_id=user.tenant_id,
            metric_date=today - dt.timedelta(days=40),
            metric_name="lessons_generated",
            value=10,
        )
    )

    db_session.commit()

    response = client.get("/analytics/summary", params={"days": 30})
    assert response.status_code == 200
    payload = response.json()

    assert payload["lessons_created"] == 5
    assert payload["lessons_generated"] == 4
    assert payload["lessons_differentiated"] == 1
    assert payload["exports"] == 5
    assert payload["lms_pushes"] == 2
    assert payload["total_lessons"] == 2
    assert payload["estimated_time_saved_minutes"] == 120

