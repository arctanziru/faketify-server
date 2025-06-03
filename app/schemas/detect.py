from typing import Optional
from pydantic import BaseModel

from app.schemas.common import PaginatedResponse
from app.schemas.feedback import FeedbackResponse


class DetectionRequest(BaseModel):
    headline: str
    headline_date: Optional[str] = None


class DetectionResponse(BaseModel):
    id: str
    headline: str
    headline_date: Optional[str] = None
    detection: bool
    probability: float
    detection_duration: Optional[float] = None
    created_at: str
    # review
    reviewer_verdict: Optional[bool] = None
    reviewer_id: Optional[str] = None
    reviewer_note: Optional[str] = None
    reviewed_at: Optional[str] = None
    feedbacks: Optional[list[FeedbackResponse]] = None


class DetectionReviewRequest(BaseModel):
    detection_id: str
    verdict: Optional[bool] = None
    note: str


PaginatedDetectionResponse = PaginatedResponse[DetectionResponse]
