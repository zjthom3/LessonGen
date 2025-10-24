"""Domain services for managing lessons and versions."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Sequence
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models.lesson import Lesson, LessonBlock, LessonVersion
from app.models.user import User

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class LessonFilters:
    """Filtering options when listing lessons."""

    subject: str | None = None
    grade_level: str | None = None
    tags: Sequence[str] | None = None


class LessonService:
    """Encapsulates lesson business logic.

    This keeps the FastAPI endpoints thin and testable.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    # ------------------------------------------------------------------
    # Lesson retrieval helpers
    # ------------------------------------------------------------------

    def _lesson_select(self) -> Select[tuple[Lesson]]:
        return select(Lesson).order_by(Lesson.updated_at.desc(), Lesson.created_at.desc())

    def list_lessons(self, tenant_id: UUID, filters: LessonFilters | None = None) -> list[Lesson]:
        """Return lessons for a tenant applying optional filters."""

        stmt = self._lesson_select().where(Lesson.tenant_id == tenant_id)

        if filters:
            if filters.subject:
                stmt = stmt.where(Lesson.subject == filters.subject)
            if filters.grade_level:
                stmt = stmt.where(Lesson.grade_level == filters.grade_level)

        results = list(self.session.execute(stmt).scalars())

        if filters and filters.tags:
            tag_set = {tag.lower() for tag in filters.tags}
            results = [
                lesson
                for lesson in results
                if tag_set.issubset({tag.lower() for tag in lesson.tags})
            ]

        return results

    def get_lesson(self, lesson_id: UUID, tenant_id: UUID) -> Lesson:
        """Fetch a lesson ensuring tenant scope."""

        lesson = self.session.get(Lesson, lesson_id)
        if lesson is None or lesson.tenant_id != tenant_id:
            raise LookupError("Lesson not found")
        return lesson

    # ------------------------------------------------------------------
    # Lesson creation & versions
    # ------------------------------------------------------------------

    def create_lesson(
        self,
        owner: User,
        title: str,
        subject: str,
        grade_level: str,
        language: str,
        tags: Sequence[str],
        visibility: str,
        status: str,
        version_payload: dict[str, object],
    ) -> Lesson:
        """Create a new lesson with an initial version."""

        lesson = Lesson(
            tenant_id=owner.tenant_id,
            owner_user_id=owner.id,
            title=title,
            subject=subject,
            grade_level=grade_level,
            language=language,
            tags=list(tags),
            visibility=visibility,
            status=status,
        )
        self.session.add(lesson)
        self.session.flush()

        version = self._build_version(
            lesson=lesson,
            creator=owner,
            version_no=1,
            payload=version_payload,
        )
        lesson.current_version_id = version.id
        self.session.flush()

        logger.info("Created lesson %s with initial version", lesson.id)
        return lesson

    def create_new_version(
        self,
        lesson: Lesson,
        creator: User,
        payload: dict[str, object],
    ) -> LessonVersion:
        """Create a new immutable version for a lesson."""

        next_version = self._next_version_number(lesson.id)
        version = self._build_version(
            lesson=lesson,
            creator=creator,
            version_no=next_version,
            payload=payload,
        )
        lesson.current_version_id = version.id
        status_override = payload.get("status")
        if isinstance(status_override, str) and status_override:
            lesson.status = status_override
        self.session.flush()

        logger.info(
            "Created lesson version %s for lesson %s", version.version_no, lesson.id
        )
        return version

    def restore_version(self, lesson: Lesson, target_version_no: int) -> LessonVersion:
        """Mark an existing version as the lesson's current version."""

        version = next(
            (v for v in lesson.versions if v.version_no == target_version_no),
            None,
        )
        if version is None:
            raise LookupError("Version not found")

        lesson.current_version_id = version.id
        self.session.flush()
        return version

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _next_version_number(self, lesson_id: UUID) -> int:
        current_max = self.session.execute(
            select(func.max(LessonVersion.version_no)).where(LessonVersion.lesson_id == lesson_id)
        ).scalar_one()
        if current_max is None:
            return 1
        return current_max + 1

    @staticmethod
    def _ensure_list_of_dicts(value: object) -> list[dict[str, object]]:
        if value is None:
            return []
        result: list[dict[str, object]] = []
        if isinstance(value, (list, tuple)):
            iterable = value
        else:
            iterable = [value]

        for item in iterable:
            if isinstance(item, dict):
                result.append(dict(item))
            else:
                result.append({"value": item})

        return result

    def _build_version(
        self,
        lesson: Lesson,
        creator: User | None,
        version_no: int,
        payload: dict[str, object],
    ) -> LessonVersion:
        """Create and persist a LessonVersion entity from payload values."""

        version = LessonVersion(
            lesson_id=lesson.id,
            version_no=version_no,
            objective=payload.get("objective"),
            duration_minutes=payload.get("duration_minutes"),
            teacher_script_md=payload.get("teacher_script_md"),
            materials=self._ensure_list_of_dicts(payload.get("materials")),
            flow=self._ensure_list_of_dicts(payload.get("flow")),
            differentiation=self._ensure_list_of_dicts(payload.get("differentiation")),
            assessments=self._ensure_list_of_dicts(payload.get("assessments")),
            accommodations=self._ensure_list_of_dicts(payload.get("accommodations")),
            source=dict(payload.get("source", {})),
            created_by_user_id=creator.id if creator else None,
        )
        version.lesson = lesson
        self.session.add(version)
        self.session.flush()

        blocks_payload = self._ensure_list_of_dicts(payload.get("blocks"))
        for index, block in enumerate(blocks_payload, start=1):
            lesson_block = LessonBlock(
                lesson_version_id=version.id,
                block_type=str(block.get("block_type", "content")),
                sequence=block.get("sequence", index),
                content_md=str(block.get("content_md", "")),
                est_minutes=block.get("est_minutes"),
                metadata_json=dict(block.get("metadata", {})),
            )
            self.session.add(lesson_block)

        return version
