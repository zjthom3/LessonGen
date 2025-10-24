"""Tests for lesson sharing endpoints."""
from __future__ import annotations

from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.lesson import Lesson
from app.models.metrics import MetricsDaily
from app.models.share import Share

from .helpers import ensure_user, login_user


def test_share_create_and_resolve_flow(
    client: TestClient, db_session: Session, fake_google_oauth
) -> None:
    ensure_user(db_session, "share.teacher@example.edu")
    login_user(client, fake_google_oauth, "share.teacher@example.edu")

    lesson_response = client.post(
        "/lessons",
        json={
            "title": "Civics Debate",
            "subject": "Social Studies",
            "grade_level": "8",
            "objective": "Students will analyze viewpoints and defend an argument.",
        },
    )
    assert lesson_response.status_code == 201
    lesson_payload = lesson_response.json()

    share_response = client.post(
        f"/lessons/{lesson_payload['id']}/share",
        json={"expires_in_hours": 48},
    )
    assert share_response.status_code == 201
    share_payload = share_response.json()
    assert share_payload["token"]
    assert share_payload["url"].endswith(share_payload["token"])

    share = db_session.execute(
        select(Share).where(Share.token == share_payload["token"])
    ).scalar_one()
    assert share.lesson_id == UUID(lesson_payload["id"])

    lesson = db_session.get(Lesson, share.lesson_id)
    assert lesson is not None

    metric = db_session.execute(
        select(MetricsDaily).where(
            MetricsDaily.tenant_id == lesson.tenant_id,
            MetricsDaily.metric_name == "shares_created",
        )
    ).scalar_one()
    assert metric.value == 1

    resolve_response = client.get(f"/shares/{share_payload['token']}")
    assert resolve_response.status_code == 200
    resolve_payload = resolve_response.json()
    assert resolve_payload["lesson_id"] == lesson_payload["id"]
    assert resolve_payload["lesson_version"]["id"] == lesson_payload["current_version_id"]

