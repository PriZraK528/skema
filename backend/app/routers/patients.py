from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.constants import DEFAULT_PAGE_LIMIT, MAX_PAGE_LIMIT
from app.db import get_db
from app.deps import require_roles
from app.models import Patient, User, UserRole
from app.schemas.patient import PatientBrief

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("", response_model=list[PatientBrief])
def list_patients(
    q: str | None = Query(default=None, description="Search by patient name"),
    limit: int = Query(default=DEFAULT_PAGE_LIMIT, ge=1, le=MAX_PAGE_LIMIT),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.doctor)),
):
    stmt = select(Patient).order_by(Patient.full_name).limit(limit)
    if q:
        stmt = stmt.where(Patient.full_name.ilike(f"%{q.strip()}%"))
    return list(db.scalars(stmt).all())
