"""Lesson generation orchestration service."""
from __future__ import annotations

import json
import logging
import pathlib
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Iterable, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.gen_job import GenerationJob
from app.models.lesson import Lesson, LessonVersion
from app.models.standard import Standard
from app.models.user import User
from app.services.lesson_service import LessonService
from app.services.standards_service import StandardsService

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class GenerationInput:
    subject: str
    grade_level: str
    topic: str
    duration_minutes: int
    teaching_style: str
    focus_keywords: list[str]
    standard_codes: list[str] | None = None


class GenerationService:
    """Coordinates AI generation with lesson persistence."""

    def __init__(
        self,
        session: Session,
        lesson_service: LessonService,
        standards_service: StandardsService,
    ) -> None:
        self.session = session
        self.lesson_service = lesson_service
        self.standards_service = standards_service
        self._prompt_cache: str | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_lesson(
        self,
        user: User,
        generation_input: GenerationInput,
    ) -> tuple[GenerationJob, Lesson, LessonVersion, list[Any]]:
        """Generate a lesson, persist it, and log the job."""

        job = GenerationJob(
            tenant_id=user.tenant_id,
            user_id=user.id,
            status="processing",
            prompt_payload=asdict(generation_input),
        )
        self.session.add(job)
        self.session.flush()

        try:
            content = self._generate_content(generation_input)

            lesson = self.lesson_service.create_lesson(
                owner=user,
                title=content["title"],
                subject=generation_input.subject,
                grade_level=generation_input.grade_level,
                language=content.get("language", "en"),
                tags=generation_input.focus_keywords,
                visibility="private",
                status="draft",
                version_payload={
                    "objective": content.get("objective"),
                    "duration_minutes": generation_input.duration_minutes,
                    "teacher_script_md": content.get("teacher_script_md"),
                    "materials": content.get("materials", []),
                    "flow": content.get("flow", []),
                    "differentiation": content.get("differentiation", []),
                    "assessments": content.get("assessments", []),
                    "accommodations": content.get("accommodations", []),
                    "source": content.get("source", {}),
                },
            )
            self.session.refresh(lesson)
            version = lesson.versions[-1]

            standards = self._resolve_standards(
                generation_input, version, content.get("suggested_standards", [])
            )
            if standards:
                self.standards_service.attach_standards(version.id, standards)

            job.lesson_id = lesson.id
            job.lesson_version_id = version.id
            job.status = "completed"
            job.result_payload = {
                "lesson_id": str(lesson.id),
                "lesson_version_id": str(version.id),
                "title": lesson.title,
            }
            job.completed_at = datetime.utcnow()
            self.session.flush()

            logger.info("Generation job %s completed", job.id)
            return job, lesson, version, standards
        except Exception as exc:  # pragma: no cover - defensive path
            logger.exception("Generation job %s failed", job.id)
            job.status = "failed"
            job.error_message = str(exc)
            job.completed_at = datetime.utcnow()
            self.session.flush()
            raise

    # ------------------------------------------------------------------
    # Content generation helpers
    # ------------------------------------------------------------------

    def _generate_content(self, generation_input: GenerationInput) -> dict[str, Any]:
        if not settings.openai_api_key:
            return self._fallback_content(generation_input)

        try:
            from openai import OpenAI  # type: ignore

            client = OpenAI(api_key=settings.openai_api_key)
            prompt = self._render_prompt(generation_input)
            response = client.responses.create(
                model=settings.openai_model,
                input=prompt,
            )
            raw = response.output[0].content[0].text  # type: ignore[attr-defined]
            return self._parse_model_output(raw, generation_input)
        except Exception as exc:  # pragma: no cover - network path
            logger.warning("OpenAI call failed, using fallback content: %s", exc)
            return self._fallback_content(generation_input)

    def _render_prompt(self, generation_input: GenerationInput) -> str:
        template = self._load_prompt_template()
        data = {
            "subject": generation_input.subject,
            "grade_level": generation_input.grade_level,
            "topic": generation_input.topic,
            "duration_minutes": generation_input.duration_minutes,
            "teaching_style": generation_input.teaching_style,
            "focus_keywords": ", ".join(generation_input.focus_keywords),
        }
        return template.format(**data)

    def _load_prompt_template(self) -> str:
        if self._prompt_cache is not None:
            return self._prompt_cache

        template_path = pathlib.Path(settings.generation_prompt_template)
        if not template_path.is_absolute():
            template_path = pathlib.Path(__file__).resolve().parent.parent / template_path
        if not template_path.exists():
            logger.warning("Prompt template %s missing; using default.", template_path)
            self._prompt_cache = self._default_prompt()
            return self._prompt_cache

        self._prompt_cache = template_path.read_text(encoding="utf-8")
        return self._prompt_cache

    def _default_prompt(self) -> str:
        return (
            "You are an instructional coach generating a lesson. Subject: {subject}. "
            "Grade level: {grade_level}. Topic: {topic}. Duration: {duration_minutes} minutes. "
            "Teaching style: {teaching_style}. Focus keywords: {focus_keywords}."
        )

    def _parse_model_output(
        self, raw: str, generation_input: GenerationInput
    ) -> dict[str, Any]:
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            logger.debug("Model output not JSON; falling back to template parsing")
        return self._fallback_content(generation_input)

    def _fallback_content(self, generation_input: GenerationInput) -> dict[str, Any]:
        lesson_title = f"{generation_input.topic} ({generation_input.subject})"
        return {
            "title": lesson_title,
            "objective": (
                f"Students will explore {generation_input.topic} through {generation_input.teaching_style.lower()} learning."
            ),
            "teacher_script_md": (
                f"### Engage\nIntroduce the topic of {generation_input.topic}.\n\n"
                f"### Explore\nGuide learners through an activity centered on {', '.join(generation_input.focus_keywords) or generation_input.topic}."
            ),
            "materials": [
                {"type": "text", "label": "Materials", "value": "Projector, slide deck, exit ticket"}
            ],
            "flow": [
                {
                    "phase": "Engage",
                    "minutes": 10,
                    "content_md": f"Warm-up discussion about {generation_input.topic}.",
                },
                {
                    "phase": "Explore",
                    "minutes": generation_input.duration_minutes - 20,
                    "content_md": "Facilitated group activity with scaffolded prompts.",
                },
                {
                    "phase": "Reflect",
                    "minutes": 10,
                    "content_md": "Students share takeaways and complete exit ticket.",
                },
            ],
            "differentiation": [
                {"strategy": "ELL", "description": "Provide sentence starters and visuals."},
                {"strategy": "Extension", "description": "Offer challenge problems for early finishers."},
            ],
            "assessments": [
                {"type": "exit_ticket", "description": "Collect quick reflection on learning."}
            ],
            "accommodations": [
                {"type": "iep", "description": "Allow additional think time during discussion."}
            ],
            "language": "en",
        }

    # ------------------------------------------------------------------
    # Standards helpers
    # ------------------------------------------------------------------

    def _resolve_standards(
        self,
        generation_input: GenerationInput,
        version: LessonVersion,
        generated_codes: Sequence[str],
    ) -> list[Any]:
        standards: list[Any] = []
        keywords = generation_input.focus_keywords + [generation_input.topic]

        if generation_input.standard_codes:
            standards.extend(self._fetch_standards_by_codes(generation_input.standard_codes))

        if not standards:
            standards = self.standards_service.suggest_standards(
                subject=generation_input.subject,
                grade_level=generation_input.grade_level,
                keywords=keywords,
            )
        return standards

    def _fetch_standards_by_codes(self, codes: Iterable[str]) -> list[Any]:
        stmt = select(Standard).where(Standard.code.in_(list(codes)))  # type: ignore[name-defined]
        return list(self.session.execute(stmt).scalars())
