"""Shared helper functions for backend API tests."""
from __future__ import annotations

from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.google_oauth import GoogleOAuthUser
from app.services.user_service import UserService


def login_user(client: TestClient, fake_google_oauth, email: str) -> None:
    """Authenticate the test client as the supplied user."""

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
    session_status = client.get("/auth/session").json()
    assert session_status["authenticated"] is True


def ensure_user(session: Session, email: str) -> UUID:
    """Create the provided user in the database if it does not already exist."""

    service = UserService(session)
    user = service.invite_user(email=email, role="teacher", full_name="Taylor Teacher")
    session.commit()
    session.refresh(user)
    return user.id
