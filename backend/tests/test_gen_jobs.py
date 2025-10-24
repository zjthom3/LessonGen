"""Tests for generation job endpoint."""
from __future__ import annotations

from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import GenerationJob, Lesson, StandardsFramework, Standard
from app.services.google_oauth import GoogleOAuthUser
from app.services.user_service import UserService


def ensure_user(session: Session, email: str) -> UUID:
    service = UserService(session)
    user = service.invite_user(email=email, role="teacher", full_name="Taylor Teacher")
    session.commit()
    session.refresh(user)
    return user.id


def ensure_standard(session: Session) -> Standard:
    framework = session.query(StandardsFramework).filter_by(code="NGSS").first()
    if not framework:
        framework = StandardsFramework(code="NGSS", name="Next Generation Science Standards")
        session.add(framework)
        session.flush()

    standard = session.query(Standard).filter_by(code="NGSS 5-ESS1-1").first()
    if not standard:
        standard = Standard(
            framework_id=framework.id,
            code="NGSS 5-ESS1-1",
            description="Support an argument that differences in the apparent brightness of the sun compared to other stars is due to their relative distances from Earth.",
            subject="Science",
            grade_band="5",
            tags=["astronomy", "brightness"],
        )
        session.add(standard)
        session.flush()

    return standard


def test_gen_job_creates_lesson(client: TestClient, db_session: Session, fake_google_oauth) -> None:
    ensure_user(db_session, "generator@example.edu")
    ensure_standard(db_session)

    async def exchange(_request) -> GoogleOAuthUser:
        return GoogleOAuthUser(
            email="generator@example.edu",
            full_name="Taylor Teacher",
            subject="fake-subject",
            picture=None,
        )

    fake_google_oauth.exchange_code = exchange  # type: ignore[assignment]
    state = client.get("/auth/login").json()["state"]
    client.get("/auth/callback", params={"state": state}, allow_redirects=False)

    payload = {
        "subject": "Science",
        "grade_level": "5",
        "topic": "Phases of the Moon",
        "duration_minutes": 45,
        "teaching_style": "inquiry",
        "focus_keywords": ["moon", "orbit"],
        "standard_codes": ["NGSS 5-ESS1-1"],
    }

    response = client.post("/gen-jobs/", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert "job" in data
    assert data["job"]["status"] == "completed"
    assert data["lesson"]["title"]
    assert data["lesson"]["subject"] == "Science"
    assert data["lesson"]["grade_level"] == "5"
    assert data["standards"]
    assert data["standards"][0]["code"] == "NGSS 5-ESS1-1"

    job = db_session.get(GenerationJob, UUID(data["job"]["id"]))
    assert job is not None
    assert job.lesson_id is not None
    assert job.lesson_version_id is not None

    lesson = db_session.get(Lesson, job.lesson_id)
    assert lesson is not None
    assert lesson.versions
