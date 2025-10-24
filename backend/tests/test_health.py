"""Tests for health endpoints."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healthcheck() -> None:
    """Health endpoint returns expected payload."""

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version() -> None:
    """Version endpoint returns an application version string."""

    response = client.get("/version")
    assert response.status_code == 200
    assert "version" in response.json()
    assert isinstance(response.json()["version"], str)
