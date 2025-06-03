from pydantic import BaseModel
from typing import Generic, List, TypeVar, Optional

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    page: int
    page_size: int
    items: List[T]


class PaginationRequest(BaseModel):
    page: Optional[int] = 1
    page_size: Optional[int] = 10
