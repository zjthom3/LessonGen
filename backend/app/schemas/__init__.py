"""Pydantic schemas for LessonGen."""

from .user import (
    AuthSessionResponse,
    UserInviteRequest,
    UserProfileUpdate,
    UserRead,
    UserRoleRead,
    UserUpdateRequest,
)
from .lesson import (
    LessonCreate,
    LessonDetail,
    LessonRestoreResponse,
    LessonSummary,
    LessonVersionCreate,
    LessonVersionRead,
)
from .generation import GenerationJobRead, GenerationRequest, GenerationResponse
from .standard import StandardRead, StandardsFrameworkRead
from .lms import (
    ClassroomConnectRequest,
    ClassroomConnectResponse,
    ClassroomPushRequest,
    ClassroomPushResponse,
)
from .analytics import AnalyticsSummaryResponse
from .share import ShareCreateRequest, ShareCreateResponse, SharedLessonResponse
from .lesson import LessonDifferentiateRequest

__all__ = [
    "AuthSessionResponse",
    "UserInviteRequest",
    "UserProfileUpdate",
    "UserRead",
    "UserRoleRead",
    "UserUpdateRequest",
    "LessonCreate",
    "LessonDetail",
    "LessonRestoreResponse",
    "LessonSummary",
    "LessonVersionCreate",
    "LessonVersionRead",
    "GenerationRequest",
    "GenerationResponse",
    "GenerationJobRead",
    "StandardRead",
    "StandardsFrameworkRead",
    "ClassroomConnectRequest",
    "ClassroomConnectResponse",
    "ClassroomPushRequest",
    "ClassroomPushResponse",
    "AnalyticsSummaryResponse",
    "ShareCreateRequest",
    "ShareCreateResponse",
    "SharedLessonResponse",
    "LessonDifferentiateRequest",
]
