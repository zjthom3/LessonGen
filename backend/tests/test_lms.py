"""Tests for LMS endpoint stubs."""
from __future__ import annotations

from datetime import datetime, timedelta
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.user_service import UserService

from .test_lessons import login_user


def ensure_user(session: Session, email: str) -> UUID:
    service = UserService(session)
    user = service.invite_user(email=email, full_name="Taylor Teacher", role="teacher")
    session.commit()
    return user.id


def create_lesson(client: TestClient) -> str:
    payload = {
        "title": "Gravity Lab",
        "subject": "Science",
        "grade_level": "5",
        "objective": "Students will observe gravitational effects.",
    }
    response = client.post("/lessons", json=payload)
    assert response.status_code == 201
    return response.json()["id"]


def connect_classroom(client: TestClient) -> str:
    response = client.post(
        "/lms/google-classroom/connect",
        json={
            "access_token": "mock-access",
            "refresh_token": "mock-refresh",
            "expires_in": 3600,
            "profile": {"teacher": "Taylor"},
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_lms_connect_and_push(client: TestClient, db_session: Session, fake_google_oauth) -> None:
    ensure_user(db_session, "lms@example.edu")
    login_user(client, fake_google_oauth, "lms@example.edu")

    connection_id = connect_classroom(client)
    assert connection_id

    lesson_id = create_lesson(client)
    due_date = (datetime.utcnow() + timedelta(days=3)).isoformat() + "Z"

    response = client.post(
        "/lms/google-classroom/push",
        json={
            "lesson_id": lesson_id,
            "course_id": "course-123",
            "topic_id": "topic-456",
            "due_date": due_date,
        },
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] == "posted"
    assert payload["external_assignment_id"].startswith("mock-assignment-")
