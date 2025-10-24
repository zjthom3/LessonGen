"""Endpoints for LMS integrations such as Google Classroom."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.db.session import get_session
from app.models import LMSConnection, Lesson
from app.schemas import (
    ClassroomConnectRequest,
    ClassroomConnectResponse,
    ClassroomPushRequest,
    ClassroomPushResponse,
)
from app.services import EventService, LMSService, LessonService

router = APIRouter(prefix="/lms", tags=["lms"])


def _get_lms_service(db: Session = Depends(get_session)) -> LMSService:
    return LMSService(db)


def _lesson_service(db: Session = Depends(get_session)) -> LessonService:
    return LessonService(db)


@router.post(
    "/google-classroom/connect",
    response_model=ClassroomConnectResponse,
    status_code=status.HTTP_201_CREATED,
)
def connect_google_classroom(
    payload: ClassroomConnectRequest,
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_session),
    lms_service: LMSService = Depends(_get_lms_service),
) -> ClassroomConnectResponse:
    connection = lms_service.connect_google_classroom(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        access_token=payload.access_token,
        refresh_token=payload.refresh_token,
        expires_in=payload.expires_in,
        profile=payload.profile,
    )
    db.commit()
    db.refresh(connection)
    return ClassroomConnectResponse(
        id=connection.id,
        provider=connection.provider,
        created_at=connection.created_at,
        expires_at=connection.expires_at,
        profile=(payload.profile or {}),
    )


def _get_connection(
    db: Session,
    user_id: UUID,
    provider: str,
) -> LMSConnection:
    stmt = select(LMSConnection).where(
        LMSConnection.user_id == user_id,
        LMSConnection.provider == provider,
    ).order_by(LMSConnection.created_at.desc())
    connection = db.execute(stmt).scalars().first()
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Google Classroom connection found for user",
        )
    return connection


@router.post(
    "/google-classroom/push",
    response_model=ClassroomPushResponse,
    status_code=status.HTTP_201_CREATED,
)
def push_google_classroom(
    payload: ClassroomPushRequest,
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_session),
    lms_service: LMSService = Depends(_get_lms_service),
    lesson_service: LessonService = Depends(_lesson_service),
) -> ClassroomPushResponse:
    connection = _get_connection(db, current_user.id, provider="google_classroom")

    try:
        lesson = lesson_service.get_lesson(payload.lesson_id, current_user.tenant_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found") from exc

    version = lesson.versions[-1] if lesson.versions else None
    push = lms_service.push_google_classroom_assignment(
        connection=connection,
        lesson=lesson,
        version=version,
        course_id=payload.course_id,
        topic_id=payload.topic_id,
        due_date=payload.due_date,
    )
    EventService(db).log_event(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="lms_push",
        metadata={"lesson_id": str(lesson.id), "course_id": payload.course_id},
    )
    db.commit()
    db.refresh(push)
    return ClassroomPushResponse(
        id=push.id,
        status=push.status,
        external_assignment_id=push.external_assignment_id,
        created_at=push.created_at,
    )
