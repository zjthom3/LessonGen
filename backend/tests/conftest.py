"""Shared pytest fixtures for backend tests."""
from __future__ import annotations

from collections.abc import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.main import app
from app.services.google_oauth import (
    GoogleAuthorizationRequest,
    GoogleOAuthClient,
    GoogleOAuthUser,
)
from app.services.google_oauth import get_google_oauth_client


class FakeGoogleOAuthClient(GoogleOAuthClient):
    """Test double that skips external Google calls."""

    def __init__(self) -> None:
        # Intentionally bypass parent init to avoid network metadata request
        self._authorization_url = "https://accounts.google.com/o/oauth2/auth?client_id=test"
        self._state = "test-state"

    async def create_authorization_url(self, request, redirect_uri: str) -> GoogleAuthorizationRequest:  # type: ignore[override]
        return GoogleAuthorizationRequest(
            authorization_url=self._authorization_url,
            state=self._state,
            code_verifier=None,
        )

    async def exchange_code(self, request) -> GoogleOAuthUser:  # type: ignore[override]
        return GoogleOAuthUser(
            email="teacher@example.edu",
            full_name="Taylor Teacher",
            subject="fake-subject",
            picture="https://example.edu/avatar.png",
        )


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session(engine) -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    TestingSessionLocal = sessionmaker(bind=connection, expire_on_commit=False, class_=Session)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def fake_google_oauth() -> FakeGoogleOAuthClient:
    return FakeGoogleOAuthClient()


@pytest.fixture()
def client(db_session: Session, fake_google_oauth: FakeGoogleOAuthClient) -> Generator[TestClient, None, None]:
    def override_get_session() -> Generator[Session, None, None]:
        yield db_session

    def override_google_oauth() -> FakeGoogleOAuthClient:
        return fake_google_oauth

    app.dependency_overrides[get_google_oauth_client] = override_google_oauth
    from app.db.session import get_session  # local import to avoid circular

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
