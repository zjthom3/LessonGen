"""Endpoints for the authenticated user's profile."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.db.session import get_session
from app.models import User
from app.schemas import UserProfileUpdate, UserRead

router = APIRouter(tags=["profile"])


@router.get("/me", response_model=UserRead)
def read_current_user(
    current_user: User = Depends(get_current_active_user),
) -> UserRead:
    """Return the currently authenticated user."""

    return UserRead.model_validate(current_user)


@router.put("/me", response_model=UserRead)
def update_profile(
    payload: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session),
) -> UserRead:
    """Update the authenticated user's profile and preferences."""

    user = db.get(User, current_user.id)
    if not user:
        # Safety guard: if the user was deleted mid-session, treat as unauthenticated.
        raise RuntimeError("Authenticated user record missing")

    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.locale is not None:
        user.locale = payload.locale
    if payload.preferred_subjects is not None:
        user.preferred_subjects = payload.preferred_subjects
    if payload.preferred_grade_levels is not None:
        user.preferred_grade_levels = payload.preferred_grade_levels

    db.commit()
    db.refresh(user)
    return UserRead.model_validate(user)
