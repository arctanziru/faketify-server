from pydantic import BaseModel

from app.schemas.common import PaginatedResponse


class UserResponse(BaseModel):
    id: str
    full_name: str
    email: str
    is_admin: bool
    created_at: str
    updated_at: str


class UserRequest(BaseModel):
    full_name: str
    email: str
    password: str


PaginatedUserResponse = PaginatedResponse[UserResponse]
