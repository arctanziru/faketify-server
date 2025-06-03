from pydantic import BaseModel
from typing import Optional

from app.schemas.common import PaginatedResponse


class FeedbackRequest(BaseModel):
    full_name: Optional[str]
    email: Optional[str]
    feedback: str
    detection_id: str


class FeedbackResponse(BaseModel):
    id: str
    full_name: Optional[str]
    email: Optional[str]
    feedback: str
    detection_id: str
    created_at: str


PaginatedFeedbackResponse = PaginatedResponse[FeedbackResponse]
