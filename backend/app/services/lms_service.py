"""Stub services for LMS integrations such as Google Classroom."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.models import LMSConnection, LMSPush, Lesson, LessonVersion


class LMSService:
    """Creates and manages LMS connections and push records."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def connect_google_classroom(
        self,
        *,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        access_token: str,
        refresh_token: str | None = None,
        expires_in: int | None = None,
        profile: dict[str, Any] | None = None,
    ) -> LMSConnection:
        """Persist a Google Classroom connection (synchronous stub)."""

        expires_at = None
        if expires_in:
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        connection = LMSConnection(
            tenant_id=tenant_id,
            user_id=user_id,
            provider="google_classroom",
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            metadata_json={"profile": profile or {}},
        )
        self.session.add(connection)
        self.session.flush()
        return connection

    def push_google_classroom_assignment(
        self,
        connection: LMSConnection,
        lesson: Lesson,
        version: LessonVersion | None,
        course_id: str,
        topic_id: str | None,
        due_date: datetime | None,
    ) -> LMSPush:
        """Log a Google Classroom push (stubbed synchronous behavior)."""

        assignment_id = f"mock-assignment-{uuid.uuid4().hex[:8]}"
        push = LMSPush(
            connection_id=connection.id,
            lesson_id=lesson.id,
            lesson_version_id=version.id if version else None,
            provider="google_classroom",
            status="posted",
            course_id=course_id,
            topic_id=topic_id,
            external_assignment_id=assignment_id,
            due_date=due_date,
            metadata_json={
                "title": lesson.title,
                "posted_at": datetime.utcnow().isoformat() + "Z",
            },
        )
        self.session.add(push)
        self.session.flush()
        return push
