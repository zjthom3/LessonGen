"""Google OAuth client wrapper."""
from __future__ import annotations

import secrets
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Tuple

from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import Request

from app.core.config import settings

GOOGLE_SERVER_METADATA_URL = "https://accounts.google.com/.well-known/openid-configuration"
GOOGLE_DEFAULT_SCOPE = "openid email profile"


class GoogleOAuthException(RuntimeError):
    """Raised when Google OAuth flow fails."""


@dataclass(slots=True)
class GoogleOAuthUser:
    """Simple DTO representing Google authenticated user info."""

    email: str
    full_name: str | None
    subject: str | None
    picture: str | None


@dataclass(slots=True)
class GoogleAuthorizationRequest:
    """Represents data needed to initiate Google's authorization redirect."""

    authorization_url: str
    state: str
    code_verifier: str | None = None


class GoogleOAuthClient:
    """Thin wrapper around Authlib OAuth client for Google."""

    def __init__(self) -> None:
        self._oauth = OAuth()
        self._register_client()

    def _register_client(self) -> None:
        """Register the Google OAuth client with Authlib."""

        self._oauth.register(
            name="google",
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret,
            server_metadata_url=GOOGLE_SERVER_METADATA_URL,
            client_kwargs={
                "scope": GOOGLE_DEFAULT_SCOPE,
                "prompt": "select_account",
                "access_type": "offline",
            },
        )

    async def create_authorization_url(
        self, request: Request, redirect_uri: str
    ) -> GoogleAuthorizationRequest:
        """Create an authorization URL and associated state nonce."""

        generated_state = secrets.token_urlsafe()
        result = await self._oauth.google.create_authorization_url(
            redirect_uri=redirect_uri,
            state=generated_state,
            prompt="select_account",
        )
        await self._oauth.google.save_authorize_data(
            request,
            redirect_uri=redirect_uri,
            **result,
        )
        authorization_url = result.get("url")
        state = result.get("state")
        if not authorization_url or not state:
            raise GoogleOAuthException("Google did not return authorization URL/state")
        return GoogleAuthorizationRequest(
            authorization_url=authorization_url,
            state=state,
            code_verifier=result.get("code_verifier"),
        )

    async def exchange_code(self, request: Request) -> GoogleOAuthUser:
        """Exchange authorization code for tokens and extract user info."""

        try:
            token = await self._oauth.google.authorize_access_token(request)
        except OAuthError as exc:  # pragma: no cover - network failures
            import logging

            logging.getLogger(__name__).warning(
                "Google OAuth authorize_access_token failed: %s", exc
            )
            raise GoogleOAuthException("Failed to authorize with Google") from exc

        user_info: dict[str, Any] | None = token.get("userinfo")
        if not user_info:
            try:
                user_info = await self._oauth.google.userinfo(token=token)
            except OAuthError as exc:  # pragma: no cover - network failures
                import logging

                logging.getLogger(__name__).warning(
                    "Google OAuth userinfo failed: %s", exc
                )
                raise GoogleOAuthException("Failed to fetch Google user info") from exc

        if not user_info:
            raise GoogleOAuthException("Google user info payload missing")

        return GoogleOAuthUser(
            email=user_info.get("email", ""),
            full_name=user_info.get("name"),
            subject=user_info.get("sub"),
            picture=user_info.get("picture"),
        )


@lru_cache(maxsize=1)
def get_google_oauth_client() -> GoogleOAuthClient:
    """Return a cached Google OAuth client instance."""

    return GoogleOAuthClient()
