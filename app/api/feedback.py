from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from app.db.database import get_db
from app.db.models import FeedbackModel

from app.schemas.common import PaginationRequest
from app.schemas.feedback import (
    PaginatedFeedbackResponse,
    FeedbackRequest,
    FeedbackResponse,
)

from app.services.auth import get_current_user

from app.utils.auth import role_required

router = APIRouter(tags=["Feedback"])


@router.post(
    "/feedback",
    response_model=FeedbackResponse,
    summary="Submit feedback after getting detection",
)
def submit_feedback(request: FeedbackRequest, db: Session = Depends(get_db)):
    # Log to DB
    log = FeedbackModel(
        id=str(uuid.uuid4()),
        full_name=request.full_name,
        email=request.email,
        feedback=request.feedback,
        detection_id=request.detection_id,
    )
    db.add(log)
    db.commit()

    return FeedbackResponse(**log.to_dict())


@router.get(
    "/admin/feedback",
    summary="List paginated feedback",
    response_model=PaginatedFeedbackResponse,
)
@role_required("admin")
def get_paginated_feedback(
    request: PaginationRequest = Depends(),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    page = request.page
    page_size = request.page_size

    query = db.query(FeedbackModel)
    total = query.count()
    results = query.offset((page - 1) * page_size).limit(page_size).all()

    items = [FeedbackResponse(**r.to_dict()) for r in results]

    return PaginatedFeedbackResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items,
    )


@router.get(
    "/admin/feedback/{id}",
    summary="Get a specific feedback",
    response_model=FeedbackResponse,
)
@role_required("admin")
def get_feedback(
    id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    entry = db.query(FeedbackModel).filter_by(id=id).first()
    if entry:
        return FeedbackResponse(**entry.to_dict())
    raise HTTPException(status_code=404, detail="Feedback not found")


@router.delete("/admin/feedback/{id}", summary="Delete a feedback", response_model=dict)
@role_required("admin")
def delete_feedback(
    id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    entry = db.query(FeedbackModel).filter_by(id=id).first()
    if entry:
        db.delete(entry)
        db.commit()
        return {"detail": "Feedback deleted successfully"}
    raise HTTPException(status_code=404, detail="Feedback not found")
