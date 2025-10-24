"""Authentication endpoints."""
from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_current_user
from app.db.session import get_session
from app.models import User, UserRole
from app.schemas import AuthSessionResponse, UserRead, UserRoleRead
from app.services.google_oauth import GoogleOAuthClient, GoogleOAuthException, get_google_oauth_client
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


def _clear_auth_state(request: Request) -> None:
    request.session.pop("oauth_state", None)
    request.session.pop("post_login_redirect", None)


def _build_redirect_url(target_path: str) -> str:
    if target_path.startswith(("http://", "https://")):
        return target_path
    if not target_path.startswith("/"):
        target_path = f"/{target_path}"
    return f"{settings.frontend_app_url.rstrip('/')}{target_path}"


@router.get("/login", response_model=dict[str, Any])
async def login(
    request: Request,
    oauth_client: GoogleOAuthClient = Depends(get_google_oauth_client),
) -> dict[str, Any]:
    """Initiate Google OAuth login by returning an authorization URL."""

    redirect_uri = settings.google_redirect_uri
    auth_request = await oauth_client.create_authorization_url(
        request=request,
        redirect_uri=redirect_uri,
    )

    if "next" in request.query_params:
        request.session["post_login_redirect"] = request.query_params["next"]

    return {"authorization_url": auth_request.authorization_url, "state": auth_request.state}


def _validate_allowed_domain(email: str) -> None:
    if not settings.google_allowed_domains:
        return
    domain = email.split("@")[-1].lower()
    allowed = {entry.lower() for entry in settings.google_allowed_domains}
    if domain not in allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Domain not permitted")


@router.get("/callback")
async def callback(
    request: Request,
    db: Session = Depends(get_session),
    oauth_client: GoogleOAuthClient = Depends(get_google_oauth_client),
) -> Response:
    """Handle the OAuth callback after Google authentication."""

    try:
        google_user = await oauth_client.exchange_code(request)
    except GoogleOAuthException as exc:
        _clear_auth_state(request)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if not google_user.email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not provided")

    _validate_allowed_domain(google_user.email)

    service = UserService(db)
    user = service.upsert_google_user(google_user)
    db.commit()

    redirect_target = request.query_params.get("next") or request.session.get("post_login_redirect")

    request.session["user_id"] = str(user.id)
    request.session["tenant_id"] = str(user.tenant_id)
    _clear_auth_state(request)

    if not redirect_target:
        redirect_target = "/dashboard"

    redirect_url = _build_redirect_url(redirect_target)
    return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)


@router.get("/session", response_model=AuthSessionResponse)
def session_status(
    request: Request,
    db: Session = Depends(get_session),
) -> AuthSessionResponse:
    """Return whether the user is authenticated and include profile details."""

    raw_user_id = request.session.get("user_id")
    if not raw_user_id:
        return AuthSessionResponse(authenticated=False, user=None)

    try:
        user_id = uuid.UUID(str(raw_user_id))
    except ValueError:
        request.session.clear()
        return AuthSessionResponse(authenticated=False, user=None)

    user = db.get(User, user_id)
    if not user or not user.is_active:
        request.session.clear()
        return AuthSessionResponse(authenticated=False, user=None)

    role_rows = db.execute(
        select(UserRole).where(UserRole.user_id == user.id)
    ).scalars().all()
    roles = [UserRoleRead.model_validate(role).model_dump() for role in role_rows]
    user_payload = {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "avatar_url": user.avatar_url,
        "locale": user.locale,
        "preferred_subjects": user.preferred_subjects,
        "preferred_grade_levels": user.preferred_grade_levels,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "roles": roles,
    }
    return AuthSessionResponse(
        authenticated=True,
        user=UserRead.model_validate(user_payload),
    )


@router.post("/logout")
def logout(request: Request) -> JSONResponse:
    """Clear the user's session."""

    request.session.clear()
    return JSONResponse(status_code=status.HTTP_200_OK, content={"success": True})
