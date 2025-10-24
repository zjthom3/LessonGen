"""Domain services for user management."""
from __future__ import annotations

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import District, School, Tenant, User, UserRole
from app.services.google_oauth import GoogleOAuthUser

logger = logging.getLogger(__name__)


class UserService:
    """Service layer responsible for user lifecycle operations."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def _ensure_default_tenant(self) -> Tenant:
        tenant = self.session.execute(
            select(Tenant).where(Tenant.name == settings.default_tenant_name)
        ).scalar_one_or_none()

        if tenant:
            return tenant

        tenant = Tenant(name=settings.default_tenant_name)
        self.session.add(tenant)
        self.session.flush()
        logger.info("Created default tenant '%s'", settings.default_tenant_name)
        return tenant

    def _get_default_district(self, tenant: Tenant) -> Optional[District]:
        district = self.session.execute(
            select(District).where(District.tenant_id == tenant.id).order_by(District.created_at)
        ).scalars().first()
        return district

    def _get_default_school(self, district: Optional[District]) -> Optional[School]:
        if district is None:
            return None
        school = self.session.execute(
            select(School).where(School.district_id == district.id).order_by(School.created_at)
        ).scalars().first()
        return school

    def upsert_google_user(self, google_user: GoogleOAuthUser) -> User:
        """Find or create a user record from Google profile information."""

        user = self.session.execute(
            select(User).where(User.email == google_user.email)
        ).scalar_one_or_none()

        if user:
            user.full_name = google_user.full_name or user.full_name
            user.avatar_url = google_user.picture or user.avatar_url
            user.auth_provider = "google"
            user.is_active = True
            self.session.flush()
            return user

        tenant = self._ensure_default_tenant()
        district = self._get_default_district(tenant)
        school = self._get_default_school(district)

        user = User(
            tenant_id=tenant.id,
            district_id=district.id if district else None,
            school_id=school.id if school else None,
            email=google_user.email,
            full_name=google_user.full_name,
            avatar_url=google_user.picture,
            auth_provider="google",
            is_active=True,
        )
        self.session.add(user)
        self.session.flush()

        self._ensure_role(user, "teacher")
        return user

    def invite_user(
        self,
        email: str,
        role: str,
        full_name: Optional[str] = None,
        district_id: Optional[UUID] = None,
        school_id: Optional[UUID] = None,
    ) -> User:
        """Create or update a user invitation (stubbed email)."""

        user = self.session.execute(select(User).where(User.email == email)).scalar_one_or_none()
        if user:
            logger.info("User %s already exists, updating role to %s", email, role)
        else:
            tenant = self._ensure_default_tenant()
            user = User(
                tenant_id=tenant.id,
                district_id=district_id,
                school_id=school_id,
                email=email,
                full_name=full_name,
                auth_provider="google",
                is_active=True,
            )
            self.session.add(user)
            self.session.flush()

        if full_name:
            user.full_name = full_name
        if district_id:
            user.district_id = district_id
        if school_id:
            user.school_id = school_id

        self._ensure_role(user, role)
        return user

    def update_user_role(self, user: User, role: str | None) -> None:
        """Sync the user's primary role assignment."""

        if role is None:
            return

        normalized_role = role.lower()
        for existing in list(user.roles):
            if existing.role.lower() != normalized_role:
                self.session.delete(existing)
        if any(item.role.lower() == normalized_role for item in user.roles):
            return

        self._ensure_role(user, normalized_role)

    def _ensure_role(self, user: User, role: str) -> UserRole:
        normalized_role = role.lower()
        existing_role = next((item for item in user.roles if item.role.lower() == normalized_role), None)
        if existing_role:
            return existing_role

        new_role = UserRole(user_id=user.id, role=normalized_role)
        self.session.add(new_role)
        self.session.flush()
        return new_role
