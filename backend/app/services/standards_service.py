"""Services for working with academic standards."""
from __future__ import annotations

import logging
from typing import Iterable, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.standard import LessonStandard, Standard, StandardsFramework

logger = logging.getLogger(__name__)


class StandardsService:
    """Provides lookup and alignment helpers for standards."""

    def __init__(self, session: Session) -> None:
        self.session = session

    # ------------------------------------------------------------------
    # Suggestion + lookup helpers
    # ------------------------------------------------------------------

    def suggest_standards(
        self,
        subject: str,
        grade_level: str,
        keywords: Sequence[str] | None = None,
        limit: int = 5,
    ) -> list[Standard]:
        """Return standards matching the provided filters."""

        stmt = select(Standard).join(Standard.framework).where(Standard.subject.ilike(subject))

        if grade_level:
            stmt = stmt.where(
                (Standard.grade_band == grade_level)
                | (Standard.grade_band.is_(None))
            )

        standards = list(self.session.execute(stmt).scalars())

        if keywords:
            lowered = {kw.lower() for kw in keywords if kw}
            if lowered:
                standards.sort(
                    key=lambda std: -self._keyword_score(std, lowered)
                )

        return standards[:limit]

    def _keyword_score(self, standard: Standard, keywords: set[str]) -> int:
        score = 0
        search_text = f"{standard.code} {standard.description} {' '.join(standard.tags)}".lower()
        for keyword in keywords:
            if keyword in search_text:
                score += 2
            elif any(keyword in tag.lower() for tag in standard.tags):
                score += 1
        return score

    def attach_standards(self, lesson_version_id: str, standards: Iterable[Standard]) -> None:
        """Associate the provided standards with a lesson version."""

        existing = {
            link.standard_id
            for link in self.session.execute(
                select(LessonStandard).where(LessonStandard.lesson_version_id == lesson_version_id)
            ).scalars()
        }

        for standard in standards:
            if standard.id in existing:
                continue
            self.session.add(
                LessonStandard(
                    lesson_version_id=lesson_version_id,
                    standard_id=standard.id,
                )
            )

    # ------------------------------------------------------------------
    # Utility helpers for seeding/tests
    # ------------------------------------------------------------------

    def ensure_framework(
        self,
        code: str,
        name: str,
        jurisdiction: str | None = None,
    ) -> StandardsFramework:
        """Return or create a standards framework entry."""

        framework = self.session.execute(
            select(StandardsFramework).where(
                StandardsFramework.code == code,
                StandardsFramework.jurisdiction.is_(jurisdiction),
            )
        ).scalar_one_or_none()

        if framework:
            return framework

        framework = StandardsFramework(code=code, name=name, jurisdiction=jurisdiction)
        self.session.add(framework)
        self.session.flush()
        logger.info("Created standards framework %s", code)
        return framework
