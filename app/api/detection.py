from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from app.db.database import get_db
from app.db.models import DetectionModel, UserModel

from app.schemas.common import PaginationRequest
from app.schemas.detect import (
    DetectionRequest,
    DetectionResponse,
    DetectionReviewRequest,
    PaginatedDetectionResponse,
)

from app.services.detector import detect_text
from app.services.auth import get_current_user

from app.utils.auth import role_required


router = APIRouter(tags=["Detection"])


@router.post(
    "/detect",
    response_model=DetectionResponse,
    summary="Detect hoax in a news from it's headline",
)
def detect(request: DetectionRequest, db: Session = Depends(get_db)):
    result = detect_text(request.headline, request.headline_date)

    log = DetectionModel(
        id=str(uuid.uuid4()),
        headline=request.headline,
        headline_date=request.headline_date,
        detection=result["detection"],
        probability=result["probability"],
        detection_duration=result.get("detection_duration", None),
    )
    db.add(log)
    db.commit()

    return log.to_dict()


@router.get(
    "/detection",
    summary="List paginated detections",
    response_model=PaginatedDetectionResponse,
)
def get_paginated_detections(
    request: PaginationRequest = Depends(),
    db: Session = Depends(get_db),
):
    page = request.page
    page_size = request.page_size

    query = db.query(DetectionModel).order_by(DetectionModel.created_at.desc())
    total = query.count()
    results = query.offset((page - 1) * page_size).limit(page_size).all()

    items = [DetectionResponse(**r.to_dict()) for r in results]

    return PaginatedDetectionResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items,
    )


@router.get(
    "/detection/{id}",
    summary="Get details of detection and the feedbacks of corresponding detection",
    response_model=DetectionResponse,
)
def get_detection(
    id: str,
    db: Session = Depends(get_db),
):
    entry = db.query(DetectionModel).filter_by(id=id).first()
    if entry:
        return entry.to_dict()
    raise HTTPException(status_code=404, detail="Detection not found")


@router.patch(
    "/admin/detection/{id}",
    summary="Update a detection",
    response_model=DetectionResponse,
)
@role_required("admin")
def update_detection(
    id: str,
    request: DetectionRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    entry = db.query(DetectionModel).filter_by(id=id).first()
    if entry:
        entry.headline = request.headline
        entry.headline_date = request.headline_date
        db.commit()
        return DetectionResponse(**entry.to_dict())
    raise HTTPException(status_code=404, detail="Detection not found")


@router.delete(
    "/admin/detection/{id}", summary="Delete a detection", response_model=dict
)
@role_required("admin")
def delete_detection(
    id: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    entry = db.query(DetectionModel).filter_by(id=id).first()
    if entry:
        db.delete(entry)
        db.commit()
        return {"detail": "Detection deleted successfully"}
    raise HTTPException(status_code=404, detail="Detection not found")


@router.delete(
    "/admin/detection/clear",
    summary="Delete all detections",
    response_model=dict,
)
@role_required("admin")
def clear_detections(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    db.query(DetectionModel).delete()
    db.commit()
    return {"detail": "All detections deleted successfully"}


@router.post(
    "/admin/detection/review",
    summary="Submit a reviewed detection",
    response_model=DetectionResponse,
)
@role_required("admin")
def review_detection(
    request: DetectionReviewRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    entry = db.query(DetectionModel).filter_by(id=request.id).first()
    if entry:
        entry.reviewer_verdict = request.verdict
        entry.reviewer_note = request.note
        entry.reviewer_id = current_user.id
        entry.reviewed_at = datetime.utcnow()
        db.commit()
        return DetectionResponse(**entry.to_dict())
    raise HTTPException(status_code=404, detail="Detection not found")


@router.get(
    "/admin/detection/download",
    summary="Download detections as CSV",
)
@role_required("admin")
def download_detections(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    import pandas as pd
    from fastapi.responses import StreamingResponse
    from io import StringIO

    entries = db.query(DetectionModel).all()
    df = pd.DataFrame([entry.to_dict() for entry in entries])
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    return StreamingResponse(
        iter([csv_buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=detections.csv"},
    )
