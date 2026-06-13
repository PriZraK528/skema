from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_roles
from app.models import User, UserRole
from app.schemas.common import PaginatedResponse, UserPublic
from app.services.user_utils import user_to_public

router = APIRouter(prefix="/users", tags=["users"])


class AdminUserCreate(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=128)
    role: UserRole
    full_name: str = Field(min_length=2, max_length=200)
    phone: str | None = None

    @field_validator("role")
    @classmethod
    def reject_invalid_role(cls, value: str) -> UserRole:
        try:
            role = value if isinstance(value, UserRole) else UserRole(value)
        except ValueError as exc:
            raise ValueError(
                f"Invalid role '{value}'. Allowed: {[r.value for r in UserRole]}"
            ) from exc
        return role


class AdminUserRoleUpdate(BaseModel):
    role: UserRole

    @field_validator("role")
    @classmethod
    def reject_invalid_role(cls, value: UserRole) -> UserRole:
        return value


@router.get("", response_model=PaginatedResponse[UserPublic])
def list_users(
    q: str | None = Query(default=None, description="Search by email or name"),
    role: UserRole | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
):
    stmt = select(User)
    if role:
        stmt = stmt.where(User.role == role)
    if q:
        pattern = f"%{q}%"
        stmt = stmt.where(
            (User.email.ilike(pattern))
            | (User.full_name.ilike(pattern))
        )
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    users = db.scalars(stmt.order_by(User.id).offset(offset).limit(limit)).all()
    return PaginatedResponse(
        items=[user_to_public(u) for u in users],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.patch("/{user_id}/role", response_model=UserPublic)
def update_user_role(
    user_id: int,
    payload: AdminUserRoleUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = payload.role
    db.commit()
    db.refresh(user)
    return user_to_public(user)
