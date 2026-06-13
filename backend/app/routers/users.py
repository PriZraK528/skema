from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.constants import DEFAULT_PAGE_LIMIT, ErrorDetail, MAX_PAGE_LIMIT
from app.db import get_db
from app.deps import require_roles
from app.models import User, UserRole
from app.schemas.common import PaginatedResponse, UserPublic
from app.services.user_utils import user_to_public

router = APIRouter(prefix="/users", tags=["users"])


class AdminUserRoleUpdate(BaseModel):
    role: UserRole


@router.get("", response_model=PaginatedResponse[UserPublic])
def list_users(
    q: str | None = Query(default=None, description="Search by email or name"),
    role: UserRole | None = None,
    limit: int = Query(default=DEFAULT_PAGE_LIMIT, ge=1, le=MAX_PAGE_LIMIT),
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
        raise HTTPException(status_code=404, detail=ErrorDetail.USER_NOT_FOUND)
    user.role = payload.role
    db.commit()
    db.refresh(user)
    return user_to_public(user)
