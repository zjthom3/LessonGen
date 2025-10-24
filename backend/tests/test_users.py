"""Tests for admin user management endpoints."""
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User
from app.services.google_oauth import GoogleOAuthUser
from app.services.user_service import UserService


def create_user(session: Session, email: str, role: str, *, full_name: str, is_superuser: bool = False) -> User:
    service = UserService(session)
    user = service.invite_user(email=email, full_name=full_name, role=role)
    user.is_superuser = is_superuser
    session.commit()
    session.refresh(user)
    return user


def login_via_oauth(
    client: TestClient,
    fake_google_oauth,
    email: str,
    full_name: str = "Taylor Teacher",
) -> None:
    async def exchange(_request) -> GoogleOAuthUser:
        return GoogleOAuthUser(
            email=email,
            full_name=full_name,
            subject="fake-subject",
            picture=None,
        )

    fake_google_oauth.exchange_code = exchange  # type: ignore[assignment]
    state = client.get("/auth/login").json()["state"]
    client.get("/auth/callback", params={"state": state}, allow_redirects=False)


def test_list_users_requires_admin(
    client: TestClient, db_session: Session, fake_google_oauth
) -> None:
    create_user(db_session, "teacher@example.edu", role="teacher", full_name="Taylor Teacher")
    login_via_oauth(client, fake_google_oauth, email="teacher@example.edu")

    response = client.get("/users/")
    assert response.status_code == 403


def test_admin_can_list_users(
    client: TestClient, db_session: Session, fake_google_oauth
) -> None:
    admin = create_user(
        db_session,
        "admin@example.edu",
        role="admin",
        full_name="Alex Admin",
        is_superuser=True,
    )
    teacher = create_user(
        db_session,
        "teacher@example.edu",
        role="teacher",
        full_name="Taylor Teacher",
    )

    login_via_oauth(client, fake_google_oauth, email=admin.email, full_name=admin.full_name or "")

    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    emails = [item["email"] for item in data]
    assert admin.email in emails
    assert teacher.email in emails


def test_admin_can_invite_user(
    client: TestClient, db_session: Session, fake_google_oauth
) -> None:
    admin = create_user(
        db_session,
        "admin@example.edu",
        role="admin",
        full_name="Alex Admin",
        is_superuser=True,
    )
    login_via_oauth(client, fake_google_oauth, email=admin.email)

    response = client.post(
        "/users/invite",
        json={"email": "new.teacher@example.edu", "full_name": "New Teacher", "role": "teacher"},
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["email"] == "new.teacher@example.edu"
    assert payload["roles"] == [{"role": "teacher", "scope": {}}]


def test_admin_can_update_user_role_and_status(
    client: TestClient, db_session: Session, fake_google_oauth
) -> None:
    admin = create_user(
        db_session,
        "admin@example.edu",
        role="admin",
        full_name="Alex Admin",
        is_superuser=True,
    )
    user = create_user(
        db_session,
        "teacher@example.edu",
        role="teacher",
        full_name="Taylor Teacher",
    )
    login_via_oauth(client, fake_google_oauth, email=admin.email)

    response = client.patch(
        f"/users/{user.id}",
        json={"role": "coach", "is_active": False},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["is_active"] is False
    assert payload["roles"] == [{"role": "coach", "scope": {}}]
