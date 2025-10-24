"""Authentication and authorization helpers."""
from __future__ import annotations

import uuid
from typing import Callable

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_session
from app.models.user import User


def _extract_user_id(request: Request) -> uuid.UUID:
    """Read the authenticated user id from the session cookie."""

    raw_user_id = request.session.get("user_id")
    if not raw_user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        return uuid.UUID(str(raw_user_id))
    except ValueError as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session") from exc


def get_current_user(
    request: Request,
    db: Session = Depends(get_session),
) -> User:
    """Return the currently authenticated user."""

    user_id = _extract_user_id(request)
    stmt = select(User).options(selectinload(User.roles)).where(User.id == user_id)
    user = db.execute(stmt).scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure the current user is active."""

    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is disabled")
    return current_user


def require_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Ensure the current user has administrative rights."""

    if current_user.is_superuser or current_user.has_role("admin"):
        return current_user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
