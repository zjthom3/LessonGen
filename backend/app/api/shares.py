"""Endpoints for shared lesson links."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_current_active_user
from app.db.session import get_session
from app.schemas import LessonVersionRead, ShareCreateRequest, ShareCreateResponse, SharedLessonResponse
from app.services import EventService, LessonService, ShareService

router = APIRouter(tags=["shares"])


@router.post("/lessons/{lesson_id}/share", response_model=ShareCreateResponse, status_code=status.HTTP_201_CREATED)
def create_share(
    lesson_id: UUID,
    payload: ShareCreateRequest,
    request: Request,
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_session),
) -> ShareCreateResponse:
    lesson_service = LessonService(db)
    try:
        lesson = lesson_service.get_lesson(lesson_id=lesson_id, tenant_id=current_user.tenant_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found") from exc

    version = lesson.versions[-1] if lesson.versions else None
    if version is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Lesson has no versions")

    share_service = ShareService(db)
    share = share_service.create_share(
        tenant_id=current_user.tenant_id,
        lesson_id=lesson.id,
        lesson_version_id=version.id,
        created_by_user_id=current_user.id,
        expires_in_hours=payload.expires_in_hours,
    )
    EventService(db).log_event(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="lesson_shared",
        metadata={"lesson_id": str(lesson.id), "token": share.token},
    )
    db.commit()

    base_url = settings.frontend_app_url.rstrip("/")
    share_url = f"{base_url}/share/{share.token}"
    return ShareCreateResponse(token=share.token, url=share_url, expires_at=share.expires_at)


@router.get("/shares/{token}", response_model=SharedLessonResponse)
def resolve_share(token: str, db: Session = Depends(get_session)) -> SharedLessonResponse:
    share_service = ShareService(db)
    try:
        share = share_service.get_share(token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    lesson_version = LessonVersionRead.model_validate(share.lesson_version)
    return SharedLessonResponse(
        lesson_id=share.lesson_id,
        lesson_version=lesson_version,
        expires_at=share.expires_at,
    )
