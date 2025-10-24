"""Seed script to create demo tenant, district, school, and admin user."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.models import (
    District,
    School,
    StandardsFramework,
    Standard,
    Tenant,
    User,
    UserRole,
)

DEFAULT_DISTRICT_NAME = "Aurora Public Schools"
DEFAULT_SCHOOL_NAME = "Aurora STEM Academy"
ADMIN_EMAIL = "admin@example.edu"
TEACHER_EMAIL = "teacher@example.edu"


def seed() -> None:
    """Insert baseline records if they do not already exist."""

    session = SessionLocal()
    try:
        tenant = (
            session.execute(
                select(Tenant).where(Tenant.name == settings.default_tenant_name)
            ).scalar_one_or_none()
            or Tenant(name=settings.default_tenant_name)
        )
        session.add(tenant)
        session.flush()

        district = (
            session.execute(
                select(District)
                .where(District.tenant_id == tenant.id)
                .where(District.name == DEFAULT_DISTRICT_NAME)
            ).scalar_one_or_none()
            or District(tenant_id=tenant.id, name=DEFAULT_DISTRICT_NAME)
        )
        session.add(district)
        session.flush()

        school = (
            session.execute(
                select(School)
                .where(School.district_id == district.id)
                .where(School.name == DEFAULT_SCHOOL_NAME)
            ).scalar_one_or_none()
            or School(district_id=district.id, name=DEFAULT_SCHOOL_NAME, grade_levels="6-8")
        )
        session.add(school)
        session.flush()

        if not session.execute(select(User).where(User.email == ADMIN_EMAIL)).scalar_one_or_none():
            admin = User(
                tenant_id=tenant.id,
                district_id=district.id,
                school_id=school.id,
                email=ADMIN_EMAIL,
                full_name="Alex Admin",
                auth_provider="google",
                is_active=True,
                is_superuser=True,
                preferred_subjects=["Science"],
                preferred_grade_levels=["6"],
            )
            session.add(admin)
            session.flush()
            session.add(UserRole(user_id=admin.id, role="admin"))

        if not session.execute(select(User).where(User.email == TEACHER_EMAIL)).scalar_one_or_none():
            teacher = User(
                tenant_id=tenant.id,
                district_id=district.id,
                school_id=school.id,
                email=TEACHER_EMAIL,
                full_name="Taylor Teacher",
                auth_provider="google",
                is_active=True,
                preferred_subjects=["Science"],
                preferred_grade_levels=["5"],
            )
            session.add(teacher)
            session.flush()
            session.add(UserRole(user_id=teacher.id, role="teacher"))

        _ensure_sample_standards(session)
        session.commit()
        print("Demo data seeded successfully.")
    finally:
        session.close()


def _ensure_sample_standards(session: Session) -> None:
    framework = (
        session.execute(
            select(StandardsFramework).where(StandardsFramework.code == "NGSS")
        ).scalar_one_or_none()
    )
    if framework is None:
        framework = StandardsFramework(code="NGSS", name="Next Generation Science Standards")
        session.add(framework)
        session.flush()

    existing_codes = {
        std.code
        for std in session.execute(
            select(Standard.code).where(Standard.framework_id == framework.id)
        ).scalars()
    }

    samples = [
        (
            "NGSS 5-ESS1-1",
            "Support an argument that differences in the apparent brightness of the sun compared to other stars is due to their relative distances from Earth.",
            "Science",
            "5",
            ["astronomy", "earth science", "brightness"],
        ),
        (
            "NGSS 4-PS3-2",
            "Make observations to provide evidence that energy can be transferred from place to place by sound, light, heat, and electric currents.",
            "Science",
            "4",
            ["energy", "transfer"],
        ),
    ]

    for code, description, subject, grade_band, tags in samples:
        if code in existing_codes:
            continue
        session.add(
            Standard(
                framework_id=framework.id,
                code=code,
                description=description,
                subject=subject,
                grade_band=grade_band,
                tags=tags,
            )
        )


def main() -> None:  # pragma: no cover - script entry point
    seed()


if __name__ == "__main__":  # pragma: no cover
    main()
