"""Tests for profile endpoints."""
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.google_oauth import GoogleOAuthUser
from app.services.user_service import UserService


def login_user(client: TestClient, fake_google_oauth, email: str) -> None:
    async def exchange(_request) -> GoogleOAuthUser:
        return GoogleOAuthUser(
            email=email,
            full_name="Taylor Teacher",
            subject="fake-subject",
            picture=None,
        )

    fake_google_oauth.exchange_code = exchange  # type: ignore[assignment]
    state = client.get("/auth/login").json()["state"]
    client.get("/auth/callback", params={"state": state}, allow_redirects=False)


def test_me_endpoint_returns_current_user(
    client: TestClient, db_session: Session, fake_google_oauth
) -> None:
    service = UserService(db_session)
    user = service.invite_user("teacher@example.edu", full_name="Taylor Teacher", role="teacher")
    db_session.commit()

    login_user(client, fake_google_oauth, email=user.email)

    response = client.get("/me")
    assert response.status_code == 200
    payload = response.json()
    assert payload["email"] == "teacher@example.edu"
    assert isinstance(payload["roles"], list)


def test_update_profile_persists_preferences(
    client: TestClient, db_session: Session, fake_google_oauth
) -> None:
    service = UserService(db_session)
    user = service.invite_user("teacher@example.edu", full_name="Taylor Teacher", role="teacher")
    db_session.commit()

    login_user(client, fake_google_oauth, email=user.email)

    response = client.put(
        "/me",
        json={
            "full_name": "Taylor T.",
            "preferred_subjects": ["Science", "Math"],
            "preferred_grade_levels": ["5", "6"],
            "locale": "en-US",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["full_name"] == "Taylor T."
    assert payload["preferred_subjects"] == ["Science", "Math"]
    assert payload["preferred_grade_levels"] == ["5", "6"]
