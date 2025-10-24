"""Endpoints for lesson generation jobs."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.db.session import get_session
from app.models import GenerationJob, Lesson
from app.schemas import (
    GenerationJobRead,
    GenerationRequest,
    GenerationResponse,
    LessonDetail,
    StandardRead,
)
from app.services import (
    EventService,
    GenerationInput,
    GenerationService,
    LessonService,
    StandardsService,
)

router = APIRouter(prefix="/gen-jobs", tags=["generation"])


def get_generation_service(db: Session = Depends(get_session)) -> GenerationService:
    lesson_service = LessonService(db)
    standards_service = StandardsService(db)
    return GenerationService(db, lesson_service, standards_service)


@router.post("/", response_model=GenerationResponse, status_code=status.HTTP_201_CREATED)
def create_generation_job(
    payload: GenerationRequest,
    generation_service: GenerationService = Depends(get_generation_service),
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_session),
) -> GenerationResponse:
    generation_input = GenerationInput(
        subject=payload.subject,
        grade_level=payload.grade_level,
        topic=payload.topic,
        duration_minutes=payload.duration_minutes,
        teaching_style=payload.teaching_style,
        focus_keywords=payload.focus_keywords,
        standard_codes=payload.standard_codes,
    )

    job, lesson, version, standards = generation_service.generate_lesson(current_user, generation_input)
    EventService(db).log_event(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="lesson_generated",
        metadata={"lesson_id": str(lesson.id), "job_id": str(job.id)},
    )
    db.commit()
    db.refresh(job)
    db.refresh(lesson)

    return GenerationResponse(
        job=GenerationJobRead.model_validate(job),
        lesson=LessonDetail.model_validate(lesson),
        standards=[StandardRead.model_validate(std) for std in standards],
    )
