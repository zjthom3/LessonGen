"""API router configuration."""
from __future__ import annotations

from fastapi import APIRouter

from . import analytics, auth, gen_jobs, health, lessons, lms, profile, shares, users

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router)
api_router.include_router(profile.router)
api_router.include_router(users.router)
api_router.include_router(lessons.router)
api_router.include_router(gen_jobs.router)
api_router.include_router(lms.router)
api_router.include_router(analytics.router)
api_router.include_router(shares.router)
