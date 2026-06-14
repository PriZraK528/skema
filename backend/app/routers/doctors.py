from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.constants import DEFAULT_PAGE_LIMIT, MAX_PAGE_LIMIT
from app.db import get_db
from app.deps import get_current_user
from app.models import Doctor
from app.schemas.common import PaginatedResponse
from app.schemas.schedule import DoctorOut

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("", response_model=PaginatedResponse[DoctorOut])
def list_doctors(
    limit: int = Query(default=DEFAULT_PAGE_LIMIT, ge=1, le=MAX_PAGE_LIMIT),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    stmt = select(Doctor).options(joinedload(Doctor.user))
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    doctors = db.scalars(stmt.order_by(Doctor.id).offset(offset).limit(limit)).all()
    items = [
        DoctorOut(
            id=d.id,
            user_id=d.user_id,
            full_name=d.full_name,
            specialization=d.specialization,
            email=d.user.email if d.user else None,
        )
        for d in doctors
    ]
    return PaginatedResponse(items=items, total=total, limit=limit, offset=offset)
