"""Pydantic schemas for user and auth payloads."""
from __future__ import annotations

from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class UserRoleRead(BaseModel):
    """Represents a role attached to a user."""

    role: str
    scope: dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class UserRead(BaseModel):
    """Serialized user record for API responses."""

    id: UUID
    email: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    locale: str
    preferred_subjects: List[str] = Field(default_factory=list)
    preferred_grade_levels: List[str] = Field(default_factory=list)
    is_active: bool
    is_superuser: bool
    roles: List[UserRoleRead] = Field(default_factory=list)

    class Config:
        from_attributes = True

    @field_validator("preferred_subjects", "preferred_grade_levels", mode="before")
    @classmethod
    def ensure_list(cls, value: object) -> list[str]:
        """Ensure JSON arrays come back as Python lists."""

        if value is None:
            return []
        if isinstance(value, list):
            return value
        return list(value)

    @field_validator("roles", mode="before")
    @classmethod
    def ensure_roles(cls, value: object) -> object:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return list(value)


class UserProfileUpdate(BaseModel):
    """Payload for updating the current user's profile."""

    full_name: Optional[str] = None
    preferred_subjects: List[str] = Field(default_factory=list)
    preferred_grade_levels: List[str] = Field(default_factory=list)
    locale: Optional[str] = None


class UserInviteRequest(BaseModel):
    """Request payload for inviting/creating a user."""

    email: str
    full_name: Optional[str] = None
    role: str = Field(default="teacher")
    district_id: Optional[UUID] = None
    school_id: Optional[UUID] = None


class UserUpdateRequest(BaseModel):
    """Payload for updating an existing user."""

    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None
    district_id: Optional[UUID] = None
    school_id: Optional[UUID] = None


class AuthSessionResponse(BaseModel):
    """Represents the current authentication session status."""

    authenticated: bool
    user: Optional[UserRead] = None
