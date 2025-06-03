from fastapi import APIRouter
from . import detection, feedback, user, meta, auth

router = APIRouter(prefix="/api/v1")

router.include_router(meta.router)
router.include_router(
    auth.router,
)
router.include_router(
    detection.router,
)
router.include_router(
    feedback.router,
)
router.include_router(
    user.router,
)
