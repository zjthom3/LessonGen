"""Tests for lesson export endpoints."""
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.user_service import UserService

from .test_lessons import login_user


def ensure_user(session: Session, email: str) -> None:
    service = UserService(session)
    service.invite_user(email=email, full_name="Taylor Teacher", role="teacher")
    session.commit()


def _create_lesson(client: TestClient) -> str:
    payload = {
        "title": "Water Cycle Exploration",
        "subject": "Science",
        "grade_level": "5",
        "language": "en",
        "objective": "Students will describe the stages of the water cycle.",
        "materials": [
            {"type": "text", "label": "Slides", "value": "Water cycle slides"}
        ],
        "flow": [
            {"phase": "Engage", "minutes": 10, "content_md": "Discuss evaporation."},
            {"phase": "Explore", "minutes": 25, "content_md": "Group experiment."},
        ],
    }
    response = client.post("/lessons", json=payload)
    assert response.status_code == 201
    return response.json()["id"]


def test_export_pdf(client: TestClient, db_session: Session, fake_google_oauth) -> None:
    ensure_user(db_session, "exporter@example.edu")
    login_user(client, fake_google_oauth, "exporter@example.edu")

    lesson_id = _create_lesson(client)

    response = client.get(f"/lessons/{lesson_id}/export", params={"format": "pdf"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.headers["content-disposition"].endswith(".pdf\"")
    assert len(response.content) > 100


def test_export_docx(client: TestClient, db_session: Session, fake_google_oauth) -> None:
    ensure_user(db_session, "docx@example.edu")
    login_user(client, fake_google_oauth, "docx@example.edu")

    lesson_id = _create_lesson(client)

    response = client.get(f"/lessons/{lesson_id}/export", params={"format": "docx"})
    assert response.status_code == 200
    content_type = response.headers["content-type"]
    assert "wordprocessingml" in content_type
    assert response.headers["content-disposition"].endswith(".docx\"")
    assert len(response.content) > 200


def test_export_gdoc(client: TestClient, db_session: Session, fake_google_oauth) -> None:
    ensure_user(db_session, "gdoc@example.edu")
    login_user(client, fake_google_oauth, "gdoc@example.edu")

    lesson_id = _create_lesson(client)

    response = client.get(f"/lessons/{lesson_id}/export", params={"format": "gdoc"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["title"]
