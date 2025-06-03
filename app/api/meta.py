from fastapi import APIRouter, Depends

from app.services.auth import get_password_hash, get_current_user
from app.utils.auth import role_required


router = APIRouter(tags=["Meta"])


@router.get("/health", summary="Health check")
def health():
    return {"status": "ok"}


@router.get("/version", summary="Model version")
def version():
    return {"model_version": "1.0.0"}
