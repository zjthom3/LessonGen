"""Service helpers for share tokens."""
from __future__ import annotations

import secrets
import string
import uuid
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Share


class ShareService:
    """Creates and resolves share tokens for lessons."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create_share(
        self,
        *,
        tenant_id: uuid.UUID,
        lesson_id: uuid.UUID,
        lesson_version_id: uuid.UUID,
        created_by_user_id: uuid.UUID,
        expires_in_hours: int | None = 72,
    ) -> Share:
        token = self._generate_token()
        expires_at = None
        if expires_in_hours:
            expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)

        share = Share(
            token=token,
            tenant_id=tenant_id,
            lesson_id=lesson_id,
            lesson_version_id=lesson_version_id,
            created_by_user_id=created_by_user_id,
            expires_at=expires_at,
        )
        self.session.add(share)
        return share

    def get_share(self, token: str) -> Share:
        stmt = select(Share).where(Share.token == token)
        share = self.session.execute(stmt).scalar_one_or_none()
        if share is None:
            raise ValueError("Share not found")
        if share.expires_at and share.expires_at < datetime.utcnow():
            raise ValueError("Share expired")
        return share

    def _generate_token(self, length: int = 32) -> str:
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))
