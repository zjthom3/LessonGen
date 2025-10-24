"""Tests for lesson management APIs."""
from __future__ import annotations

from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.lesson import Lesson, LessonVersion
from app.models.metrics import MetricsDaily

from .helpers import ensure_user, login_user


def test_create_lesson_with_initial_version(
    client: TestClient, db_session: Session, fake_google_oauth
) -> None:
    ensure_user(db_session, "teacher@example.edu")
    login_user(client, fake_google_oauth, "teacher@example.edu")

    payload = {
        "title": "Explore the Solar System",
        "subject": "Science",
        "grade_level": "5",
        "language": "en",
        "tags": ["space", "astronomy"],
        "objective": "Students will identify the planets in our solar system.",
        "materials": [{"type": "url", "label": "NASA", "value": "https://nasa.gov"}],
        "flow": [
            {"phase": "Engage", "minutes": 5, "content_md": "Show planet imagery."}
        ],
    }

    response = client.post("/lessons", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["title"] == payload["title"]
    assert data["subject"] == payload["subject"]
    assert data["versions"]
    assert data["versions"][0]["version_no"] == 1

    lesson_id = UUID(data["id"])
    version_id = UUID(data["versions"][0]["id"])

    lesson = db_session.get(Lesson, lesson_id)
    assert lesson is not None
    assert lesson.current_version_id == version_id


def test_list_lessons_supports_filters(
    client: TestClient, db_session: Session, fake_google_oauth
) -> None:
    ensure_user(db_session, "filter.teacher@example.edu")
    login_user(client, fake_google_oauth, "filter.teacher@example.edu")

    for subject in ("Science", "Math"):
        payload = {
            "title": f"Lesson {subject}",
            "subject": subject,
            "grade_level": "5",
            "tags": [subject.lower()],
        }
        client.post("/lessons", json=payload)

    response = client.get("/lessons", params={"subject": "Science"})
    assert response.status_code == 200
    lessons = response.json()
    assert len(lessons) == 1
    assert lessons[0]["subject"] == "Science"

    response = client.get("/lessons", params={"tags": "math"})
    assert response.status_code == 200
    lessons = response.json()
    assert len(lessons) == 1
    assert lessons[0]["subject"] == "Math"


def test_create_version_and_restore(
    client: TestClient, db_session: Session, fake_google_oauth
) -> None:
    ensure_user(db_session, "versions.teacher@example.edu")
    login_user(client, fake_google_oauth, "versions.teacher@example.edu")

    create_response = client.post(
        "/lessons",
        json={
            "title": "Narrative Writing",
            "subject": "ELA",
            "grade_level": "4",
            "objective": "Draft a narrative paragraph.",
        },
    )
    lesson_data = create_response.json()
    lesson_id = lesson_data["id"]
    current_version = lesson_data["current_version_id"]

    version_response = client.post(
        f"/lessons/{lesson_id}/versions",
        json={
            "objective": "Revise narrative paragraph with peer feedback.",
            "assessments": [{"type": "exit_ticket", "description": "Peer review notes"}],
        },
    )
    assert version_response.status_code == 201
    new_version = version_response.json()
    assert new_version["version_no"] == 2

    lesson = db_session.get(Lesson, UUID(lesson_id))
    assert lesson is not None
    assert lesson.current_version_id == UUID(new_version["id"])

    restore_response = client.post(f"/lessons/{lesson_id}/restore/1")
    assert restore_response.status_code == 200
    restore_payload = restore_response.json()
    assert restore_payload["restored_version"] == 1
    assert restore_payload["current_version_id"] == current_version

    updated_lesson = db_session.get(Lesson, UUID(lesson_id))
    assert updated_lesson is not None
    assert updated_lesson.current_version_id == UUID(current_version)
    versions = db_session.query(LessonVersion).filter_by(lesson_id=updated_lesson.id).all()
    assert len(versions) == 2


def test_differentiate_lesson_adds_supports_and_logs_metric(
    client: TestClient, db_session: Session, fake_google_oauth
) -> None:
    ensure_user(db_session, "differentiate.teacher@example.edu")
    login_user(client, fake_google_oauth, "differentiate.teacher@example.edu")

    lesson_payload = {
        "title": "Fractions Review",
        "subject": "Math",
        "grade_level": "4",
        "objective": "Compare fractions with unlike denominators.",
    }
    create_response = client.post("/lessons", json=lesson_payload)
    assert create_response.status_code == 201
    lesson_id = create_response.json()["id"]

    diff_response = client.post(
        f"/lessons/{lesson_id}/differentiate",
        json={"audience": "ELL", "notes": "Preview vocabulary before whole-group instruction."},
    )
    assert diff_response.status_code == 201
    version_payload = diff_response.json()

    ell_entries = [entry for entry in version_payload["differentiation"] if entry["strategy"] == "ELL"]
    assert ell_entries, "Expected ELL differentiation strategy to be appended."
    accommodations = [entry for entry in version_payload["accommodations"] if entry["type"] == "Supports"]
    assert accommodations, "Expected accommodations entry to be appended."

    lesson = db_session.get(Lesson, UUID(lesson_id))
    assert lesson is not None
    assert lesson.current_version_id == UUID(version_payload["id"])

    metric = db_session.execute(
        select(MetricsDaily).where(
            MetricsDaily.tenant_id == lesson.tenant_id,
            MetricsDaily.metric_name == "lessons_differentiated",
        )
    ).scalar_one()
    assert metric.value == 1
