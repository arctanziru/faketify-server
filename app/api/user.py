from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from app.db.database import get_db
from app.db.models import UserModel

from app.schemas.common import PaginationRequest
from app.schemas.user import (
    PaginatedUserResponse,
    UserResponse,
    UserRequest,
)

from app.services.auth import get_password_hash, get_current_user
from app.utils.auth import role_required

router = APIRouter(tags=["User"])


@router.get(
    "/admin/user",
    summary="List paginated users",
)
@role_required("admin")
def get_paginated_users(
    request: PaginationRequest = Depends(),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    page = request.page
    page_size = request.page_size

    query = db.query(UserModel)
    total = query.count()
    results = query.offset((page - 1) * page_size).limit(page_size).all()

    items = [UserResponse(**r.to_dict()) for r in results]

    return PaginatedUserResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items,
    )


@router.get(
    "/admin/user/{id}",
    summary="Get a specific user",
)
@role_required("admin")
def get_user(
    id: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    entry = db.query(UserModel).filter_by(id=id).first()
    if entry:
        return UserResponse(**entry.to_dict())
    raise HTTPException(status_code=404, detail="User not found")


@router.post(
    "/admin/user",
    summary="Create a new user",
)
@role_required("admin")
def create_user(
    request: UserRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    new_user = UserModel(
        id=str(uuid.uuid4()),
        full_name=request.full_name,
        email=request.email,
        created_by=current_user.id,
        hashed_password=get_password_hash(request.password),
    )
    db.add(new_user)
    db.commit()
    return UserResponse(**new_user.to_dict())


@router.patch(
    "/admin/user/{id}",
    summary="Update a user",
)
@role_required("admin")
def update_user(
    id: str,
    request: UserRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    entry = db.query(UserModel).filter_by(id=id).first()
    if entry:
        entry.full_name = request.full_name
        entry.email = request.email
        entry.age = request.age
        db.commit()
        return UserResponse(**entry.to_dict())
    raise HTTPException(status_code=404, detail="User not found")


@router.delete("/admin/user/{id}", summary="Delete a user", response_model=dict)
@role_required("admin")
def delete_user(
    id: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    entry = db.query(UserModel).filter_by(id=id).first()
    if entry:
        db.delete(entry)
        db.commit()
        return {"detail": "User deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")
