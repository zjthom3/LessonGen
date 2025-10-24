"""Tests covering the authentication flow."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.services.google_oauth import GoogleOAuthUser


def test_login_returns_authorization_url(client: TestClient) -> None:
    response = client.get("/auth/login")
    assert response.status_code == 200
    payload = response.json()
    assert "authorization_url" in payload
    assert payload["state"] == "test-state"
    assert payload["authorization_url"].startswith("https://accounts.google.com/")


def test_callback_creates_user_and_sets_session(client: TestClient) -> None:
    state = client.get("/auth/login").json()["state"]

    response = client.get("/auth/callback", params={"state": state}, allow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "http://localhost:5173/dashboard"

    session_response = client.get("/auth/session")
    assert session_response.status_code == 200
    data = session_response.json()
    assert data["authenticated"] is True
    assert data["user"]["email"] == "teacher@example.edu"
    assert data["user"]["roles"] == [{"role": "teacher", "scope": {}}]


def test_session_endpoint_when_logged_out(client: TestClient) -> None:
    response = client.get("/auth/session")
    assert response.status_code == 200
    assert response.json() == {"authenticated": False, "user": None}


def test_callback_blocks_disallowed_domains(
    client: TestClient, fake_google_oauth, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "google_allowed_domains", ["district.edu"], raising=False)

    async def disallowed_user(_request) -> GoogleOAuthUser:
        return GoogleOAuthUser(
            email="intruder@other.edu",
            full_name="Imposter",
            subject="fake-subject",
            picture=None,
        )

    fake_google_oauth.exchange_code = disallowed_user  # type: ignore[assignment]

    state = client.get("/auth/login").json()["state"]
    response = client.get("/auth/callback", params={"state": state}, allow_redirects=False)
    assert response.status_code == 403
    assert response.json()["detail"] == "Domain not permitted"
