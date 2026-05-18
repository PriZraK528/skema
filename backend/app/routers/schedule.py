from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user, require_roles
from app.models import Doctor, DoctorAvailabilitySlot, NotificationType, User, UserRole
from app.schemas.common import MessageResponse
from app.schemas.schedule import AvailabilitySlotCreate, AvailabilitySlotOut, FreeSlotOut
from app.services.notifications import notify_users
from app.services.schedule import (
    compute_free_slots,
    create_availability_slot,
    delete_availability_slot,
    get_booked_ranges,
    list_availability_slots,
)

router = APIRouter(tags=["schedule"])


def _get_doctor_or_404(db: Session, doctor_id: int) -> Doctor:
    doctor = db.get(Doctor, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


def _resolve_doctor_id(db: Session, user: User, doctor_id: int | None) -> int:
    if user.role == UserRole.doctor and user.doctor:
        return user.doctor.id
    if doctor_id is None:
        raise HTTPException(status_code=400, detail="doctor_id required")
    return doctor_id


def _ensure_schedule_access(doctor: Doctor, user: User, write: bool = False) -> None:
    if user.role in (UserRole.admin, UserRole.registrar):
        return
    if user.role == UserRole.doctor and user.doctor and user.doctor.id == doctor.id:
        return
    if not write:
        return
    raise HTTPException(status_code=403, detail="Cannot modify this schedule")


def _slot_to_out(slot: DoctorAvailabilitySlot, booked: list[tuple[datetime, datetime]]) -> AvailabilitySlotOut:
    from app.services.schedule import _overlaps_booked

    is_booked = _overlaps_booked(slot.starts_at, slot.ends_at, booked)
    return AvailabilitySlotOut(
        id=slot.id,
        doctor_id=slot.doctor_id,
        starts_at=slot.starts_at,
        ends_at=slot.ends_at,
        is_active=slot.is_active,
        is_booked=is_booked,
    )


@router.get("/doctors/{doctor_id}/schedule/slots", response_model=list[AvailabilitySlotOut])
def list_doctor_slots(
    doctor_id: int,
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Все окна врача (включая занятые записью)."""
    _get_doctor_or_404(db, doctor_id)
    slots = list_availability_slots(db, doctor_id, from_date=from_date, to_date=to_date)
    if not slots:
        return []
    booked = get_booked_ranges(db, doctor_id, slots[0].starts_at, slots[-1].ends_at)
    return [_slot_to_out(s, booked) for s in slots]


@router.post(
    "/doctors/{doctor_id}/schedule/slots",
    response_model=AvailabilitySlotOut,
    status_code=status.HTTP_201_CREATED,
)
def add_availability_slot(
    doctor_id: int,
    payload: AvailabilitySlotCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.doctor, UserRole.registrar)),
):
    """Врач вручную открывает окно для записи."""
    doctor = _get_doctor_or_404(db, doctor_id)
    _ensure_schedule_access(doctor, user, write=True)

    ends_at = payload.ends_at
    if ends_at is None and payload.duration_minutes:
        ends_at = payload.starts_at + timedelta(minutes=payload.duration_minutes)

    slot = create_availability_slot(db, doctor, payload.starts_at, ends_at)
    _notify_schedule_change(db, doctor, f"Добавлено окно приёма {slot.starts_at.isoformat()}")
    db.commit()
    db.refresh(slot)
    return _slot_to_out(slot, [])


@router.delete("/schedule/slots/{slot_id}", response_model=MessageResponse)
def remove_availability_slot(
    slot_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.doctor, UserRole.registrar)),
):
    slot = db.get(DoctorAvailabilitySlot, slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    doctor = _get_doctor_or_404(db, slot.doctor_id)
    _ensure_schedule_access(doctor, user, write=True)
    delete_availability_slot(db, slot)
    _notify_schedule_change(db, doctor, f"Удалено окно приёма {slot.starts_at.isoformat()}")
    db.commit()
    return MessageResponse(message="Slot deleted")


@router.get("/doctors/{doctor_id}/slots/free", response_model=list[FreeSlotOut])
def free_slots(
    doctor_id: int,
    from_date: date = Query(..., alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Свободные окна — только те, что врач создал и которые ещё не заняты."""
    doctor = _get_doctor_or_404(db, doctor_id)
    if to_date is None:
        to_date = from_date + timedelta(days=60)
    if to_date < from_date:
        raise HTTPException(status_code=400, detail="'to' must be >= 'from'")

    slots = list_availability_slots(
        db, doctor.id, from_date=from_date, to_date=to_date, only_free=True
    )
    return [
        FreeSlotOut(
            doctor_id=doctor_id,
            starts_at=s.starts_at,
            ends_at=s.ends_at,
            slot_id=s.id,
        )
        for s in slots
    ]


def _notify_schedule_change(db: Session, doctor: Doctor, message: str) -> None:
    from sqlalchemy.orm import joinedload

    from app.models import Appointment, AppointmentStatus

    upcoming = db.scalars(
        select(Appointment)
        .options(joinedload(Appointment.patient))
        .where(
            Appointment.doctor_id == doctor.id,
            Appointment.status == AppointmentStatus.booked,
            Appointment.starts_at >= datetime.now(timezone.utc),
        )
    ).all()
    user_ids = {doctor.user_id}
    for appt in upcoming:
        user_ids.add(appt.patient.user_id)
    users = [db.get(User, uid) for uid in user_ids if uid]
    notify_users(
        db,
        [u for u in users if u],
        ntype=NotificationType.schedule_changed,
        title="Изменение расписания",
        message=message,
    )
