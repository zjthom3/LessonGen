"""API endpoints for lesson management."""
from __future__ import annotations

import io
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.db.session import get_session
from app.models.user import User
from app.schemas import (
    LessonCreate,
    LessonDetail,
    LessonDifferentiateRequest,
    LessonRestoreResponse,
    LessonSummary,
    LessonVersionCreate,
    LessonVersionRead,
)
from app.services import EventService, ExportService, LessonFilters, LessonService

router = APIRouter(prefix="/lessons", tags=["lessons"])


def _build_service(db: Session) -> LessonService:
    return LessonService(session=db)


@router.get("/", response_model=List[LessonSummary])
def list_lessons(
    subject: str | None = Query(default=None),
    grade_level: str | None = Query(default=None),
    tags: List[str] | None = Query(default=None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session),
) -> List[LessonSummary]:
    """Return a filtered list of lessons for the current tenant."""

    service = _build_service(db)
    lessons = service.list_lessons(
        tenant_id=current_user.tenant_id,
        filters=LessonFilters(subject=subject, grade_level=grade_level, tags=tags),
    )
    return [LessonSummary.model_validate(lesson) for lesson in lessons]


@router.post("/", response_model=LessonDetail, status_code=status.HTTP_201_CREATED)
def create_lesson(
    payload: LessonCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session),
) -> LessonDetail:
    """Create a new lesson and initial version."""

    service = _build_service(db)
    lesson = service.create_lesson(
        owner=current_user,
        title=payload.title,
        subject=payload.subject,
        grade_level=payload.grade_level,
        language=payload.language,
        tags=payload.tags,
        visibility=payload.visibility,
        status=payload.status,
        version_payload=payload.model_dump(),
    )
    EventService(db).log_event(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="lesson_created",
        metadata={"lesson_id": str(lesson.id)},
    )
    db.commit()
    db.refresh(lesson)
    return LessonDetail.model_validate(lesson)


@router.get("/{lesson_id}", response_model=LessonDetail)
def read_lesson(
    lesson_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session),
) -> LessonDetail:
    """Fetch a single lesson with its versions."""

    service = _build_service(db)
    try:
        lesson = service.get_lesson(lesson_id=lesson_id, tenant_id=current_user.tenant_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found") from exc
    return LessonDetail.model_validate(lesson)


@router.post("/{lesson_id}/versions", response_model=LessonVersionRead, status_code=status.HTTP_201_CREATED)
def create_lesson_version(
    lesson_id: UUID,
    payload: LessonVersionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session),
) -> LessonVersionRead:
    """Create a new version of a lesson and mark it current."""

    service = _build_service(db)
    try:
        lesson = service.get_lesson(lesson_id=lesson_id, tenant_id=current_user.tenant_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found") from exc

    version = service.create_new_version(lesson=lesson, creator=current_user, payload=payload.model_dump())
    db.commit()
    db.refresh(version)
    return LessonVersionRead.model_validate(version)


@router.post("/{lesson_id}/restore/{version_no}", response_model=LessonRestoreResponse)
def restore_version(
    lesson_id: UUID,
    version_no: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session),
) -> LessonRestoreResponse:
    """Restore a lesson to a specified version."""

    service = _build_service(db)
    try:
        lesson = service.get_lesson(lesson_id=lesson_id, tenant_id=current_user.tenant_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found") from exc

    try:
        version = service.restore_version(lesson=lesson, target_version_no=version_no)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found") from exc

    db.commit()
    return LessonRestoreResponse(
        lesson_id=lesson.id,
        current_version_id=version.id,
        restored_version=version.version_no,
    )


@router.get("/{lesson_id}/export")
def export_lesson(
    lesson_id: UUID,
    format: str = Query(..., description="Export format: pdf, docx, gdoc"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session),
):
    """Export the specified lesson version in the requested format."""

    service = _build_service(db)
    try:
        lesson = service.get_lesson(lesson_id=lesson_id, tenant_id=current_user.tenant_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found") from exc

    version = lesson.versions[-1] if lesson.versions else None
    if not version:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Lesson has no versions")

    export_service = ExportService(db)
    try:
        export_payload = export_service.export(lesson, version, format)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    filename_base = lesson.title.lower().replace(" ", "-") or "lesson"
    EventService(db).log_event(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="lesson_exported",
        metadata={"lesson_id": str(lesson.id), "format": format.lower()},
    )
    db.commit()
    if format.lower() == "pdf":
        return StreamingResponse(
            io.BytesIO(export_payload),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=\"{filename_base}.pdf\""
            },
        )
    if format.lower() == "docx":
        return StreamingResponse(
            io.BytesIO(export_payload),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename=\"{filename_base}.docx\""
            },
        )

    return JSONResponse(status_code=status.HTTP_200_OK, content=export_payload)


@router.post(
    "/{lesson_id}/differentiate",
    response_model=LessonVersionRead,
    status_code=status.HTTP_201_CREATED,
)
def differentiate_lesson(
    lesson_id: UUID,
    payload: LessonDifferentiateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session),
) -> LessonVersionRead:
    """Create a differentiated version of a lesson for a target audience."""

    service = _build_service(db)
    try:
        lesson = service.get_lesson(lesson_id=lesson_id, tenant_id=current_user.tenant_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found") from exc

    base_version = lesson.versions[-1] if lesson.versions else None
    if base_version is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Lesson has no versions")

    new_payload = {
        "objective": base_version.objective,
        "duration_minutes": base_version.duration_minutes,
        "teacher_script_md": base_version.teacher_script_md,
        "materials": list(base_version.materials or []),
        "flow": list(base_version.flow or []),
        "differentiation": list(base_version.differentiation or []),
        "assessments": list(base_version.assessments or []),
        "accommodations": list(base_version.accommodations or []),
        "source": dict(base_version.source or {}),
    }

    audience = payload.audience.upper()
    differentiation_notes = {
        "ELL": {
            "strategy": "ELL",
            "description": "Provide visuals, vocabulary scaffolds, and sentence frames.",
        },
        "IEP": {
            "strategy": "IEP",
            "description": "Chunk tasks, provide guided notes, and allow extra processing time.",
        },
        "GIFTED": {
            "strategy": "Gifted",
            "description": "Offer extension projects and inquiry-based challenges.",
        },
    }

    differentiation_entry = differentiation_notes.get(audience)
    if differentiation_entry is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported audience")

    accommodation_notes = {
        "ELL": {"type": "Supports", "description": "Glossary with visuals and translated summaries."},
        "IEP": {"type": "Supports", "description": "Flexible grouping and assistive technology options."},
        "GIFTED": {"type": "Extension", "description": "Opportunities for independent research."},
    }
    accommodation_entry = accommodation_notes.get(audience)
    if accommodation_entry is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported audience")

    new_payload["differentiation"].append(differentiation_entry)
    new_payload["accommodations"].append(accommodation_entry)

    if payload.notes:
        new_payload["differentiation"].append({"strategy": "Notes", "description": payload.notes})

    version = service.create_new_version(lesson=lesson, creator=current_user, payload=new_payload)
    EventService(db).log_event(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="lesson_differentiated",
        metadata={"lesson_id": str(lesson.id), "audience": audience},
    )
    db.commit()
    db.refresh(version)
    return LessonVersionRead.model_validate(version)
