"""Administrative user management endpoints."""
from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import require_admin
from app.db.session import get_session
from app.models import District, School, User
from app.schemas import UserInviteRequest, UserRead, UserUpdateRequest
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


def _ensure_district_scoped(
    db: Session,
    tenant_id: UUID,
    district_id: UUID | None,
) -> District | None:
    if district_id is None:
        return None

    district = db.get(District, district_id)
    if not district or district.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="District not found")
    return district


def _ensure_school_scoped(
    db: Session,
    tenant_id: UUID,
    district: District | None,
    school_id: UUID | None,
) -> School | None:
    if school_id is None:
        return None
    school = db.get(School, school_id)
    if not school:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="School not found")
    if district and school.district_id != district.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="School not found")
    owning_district = db.get(District, school.district_id)
    if not owning_district or owning_district.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="School not found")
    return school


@router.get("/", response_model=List[UserRead])
def list_users(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_session),
) -> List[UserRead]:
    """Return all users within the admin's tenant."""

    results = (
        db.execute(
            select(User)
            .where(User.tenant_id == current_user.tenant_id)
            .order_by(User.full_name.is_(None), User.full_name, User.email)
        )
        .scalars()
        .all()
    )
    return [UserRead.model_validate(user) for user in results]


@router.post("/invite", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def invite_user(
    payload: UserInviteRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_session),
) -> UserRead:
    """Invite a new user (stubbed email) and assign a role."""

    district = _ensure_district_scoped(db, current_user.tenant_id, payload.district_id)
    school = _ensure_school_scoped(db, current_user.tenant_id, district, payload.school_id)

    service = UserService(db)
    user = service.invite_user(
        email=payload.email,
        full_name=payload.full_name,
        role=payload.role,
        district_id=district.id if district else None,
        school_id=school.id if school else None,
    )
    db.commit()
    db.refresh(user)
    return UserRead.model_validate(user)


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: UUID,
    payload: UserUpdateRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_session),
) -> UserRead:
    """Update user profile, activation status, and role."""

    user = db.get(User, user_id)
    if not user or user.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.is_active is not None:
        user.is_active = payload.is_active

    if payload.district_id is not None or payload.school_id is not None:
        district = _ensure_district_scoped(
            db,
            current_user.tenant_id,
            payload.district_id or user.district_id,
        )
        school = _ensure_school_scoped(db, current_user.tenant_id, district, payload.school_id)
        user.district_id = district.id if district else None
        user.school_id = school.id if school else None

    service = UserService(db)
    service.update_user_role(user, payload.role)

    db.commit()
    db.refresh(user)
    return UserRead.model_validate(user)
