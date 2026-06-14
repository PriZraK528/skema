from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.constants import DEFAULT_PAGE_LIMIT, ErrorDetail, MAX_PAGE_LIMIT
from app.db import get_db
from app.deps import get_current_user, require_roles
from app.models import Appointment, Doctor, Patient, User, UserRole
from app.schemas.appointment import AppointmentAssign, AppointmentCreate, AppointmentOut
from app.schemas.common import PaginatedResponse
from app.services.appointments import (
    cancel_appointment,
    complete_past_appointments,
    create_appointment,
    enrich_appointment,
    list_appointments_query,
    load_appointment,
)

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.get("", response_model=PaginatedResponse[AppointmentOut])
def list_appointments(
    q: str | None = Query(default=None, description="Search in note, patient or doctor name"),
    limit: int = Query(default=DEFAULT_PAGE_LIMIT, ge=1, le=MAX_PAGE_LIMIT),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    complete_past_appointments(db)
    stmt = list_appointments_query(db, user)
    if q:
        pattern = f"%{q.strip()}%"
        stmt = (
            stmt.join(Appointment.patient)
            .join(Appointment.doctor)
            .where(
                or_(
                    Appointment.note.ilike(pattern),
                    Patient.full_name.ilike(pattern),
                    Doctor.full_name.ilike(pattern),
                )
            )
        )
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.scalars(stmt.order_by(Appointment.starts_at.desc()).offset(offset).limit(limit)).all()
    return PaginatedResponse(
        items=[enrich_appointment(a) for a in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=AppointmentOut, status_code=201)
def book_appointment(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    doctor_id = payload.doctor_id
    if user.role == UserRole.doctor and user.doctor:
        doctor_id = user.doctor.id
    appointment = create_appointment(
        db,
        user=user,
        doctor_id=doctor_id,
        starts_at=payload.starts_at,
        note=payload.note,
        patient_id=payload.patient_id,
    )
    return enrich_appointment(appointment)


@router.post("/assign", response_model=AppointmentOut, status_code=201)
def assign_appointment(
    payload: AppointmentAssign,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.doctor, UserRole.admin)),
):
    doctor_id = payload.doctor_id
    if user.role == UserRole.doctor and user.doctor:
        doctor_id = user.doctor.id
    if doctor_id is None:
        raise HTTPException(status_code=400, detail=ErrorDetail.DOCTOR_ID_REQUIRED)
    appointment = create_appointment(
        db,
        user=user,
        doctor_id=doctor_id,
        starts_at=payload.starts_at,
        note=payload.note,
        patient_id=payload.patient_id,
        patient_name=payload.patient_name,
    )
    return enrich_appointment(appointment)


@router.post("/{appointment_id}/cancel", response_model=AppointmentOut)
def cancel(
    appointment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    appointment = load_appointment(db, appointment_id)
    appointment = cancel_appointment(db, appointment, user)
    return enrich_appointment(appointment)
