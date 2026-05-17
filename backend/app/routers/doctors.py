from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.db import get_db
from app.deps import get_current_user
from app.models import Doctor, User
from app.schemas.common import PaginatedResponse
from app.schemas.schedule import DoctorOut

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("", response_model=PaginatedResponse[DoctorOut])
def list_doctors(
    q: str | None = Query(default=None, description="Search by name or specialization"),
    specialization: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    stmt = select(Doctor).options(joinedload(Doctor.user))
    if specialization:
        stmt = stmt.where(Doctor.specialization.ilike(f"%{specialization}%"))
    if q:
        pattern = f"%{q}%"
        stmt = stmt.where(
            (Doctor.full_name.ilike(pattern)) | (Doctor.specialization.ilike(pattern))
        )
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


@router.get("/{doctor_id}", response_model=DoctorOut)
def get_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    doctor = db.scalar(
        select(Doctor).options(joinedload(Doctor.user)).where(Doctor.id == doctor_id)
    )
    if not doctor:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Doctor not found")
    return DoctorOut(
        id=doctor.id,
        user_id=doctor.user_id,
        full_name=doctor.full_name,
        specialization=doctor.specialization,
        email=doctor.user.email if doctor.user else None,
    )
