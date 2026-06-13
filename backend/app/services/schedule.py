from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.constants import ErrorDetail
from app.models import Appointment, AppointmentStatus, Doctor, DoctorAvailabilitySlot


def _ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _normalize_dt(dt: datetime) -> datetime:
    """Drop microseconds so API round-trips match DB values."""
    return _ensure_utc(dt).replace(microsecond=0)


def get_booked_ranges(
    db: Session,
    doctor_id: int,
    from_dt: datetime,
    to_dt: datetime,
) -> list[tuple[datetime, datetime]]:
    rows = db.scalars(
        select(Appointment).where(
            Appointment.doctor_id == doctor_id,
            Appointment.status == AppointmentStatus.booked,
            Appointment.starts_at >= from_dt,
            Appointment.starts_at < to_dt,
        )
    ).all()
    return [(a.starts_at, a.ends_at) for a in rows]


def _overlaps_booked(
    starts_at: datetime,
    ends_at: datetime,
    booked: list[tuple[datetime, datetime]],
) -> bool:
    return any(not (ends_at <= b_start or starts_at >= b_end) for b_start, b_end in booked)


def list_availability_slots(
    db: Session,
    doctor_id: int,
    *,
    from_date: date | None = None,
    to_date: date | None = None,
    only_free: bool = False,
) -> list[DoctorAvailabilitySlot]:
    now = datetime.now(timezone.utc)
    stmt = select(DoctorAvailabilitySlot).where(
        DoctorAvailabilitySlot.doctor_id == doctor_id,
        DoctorAvailabilitySlot.is_active.is_(True),
    )
    if from_date:
        stmt = stmt.where(
            DoctorAvailabilitySlot.starts_at
            >= datetime.combine(from_date, datetime.min.time(), tzinfo=timezone.utc)
        )
    if to_date:
        end = datetime.combine(to_date, datetime.max.time(), tzinfo=timezone.utc)
        stmt = stmt.where(DoctorAvailabilitySlot.starts_at <= end)
    stmt = stmt.where(DoctorAvailabilitySlot.starts_at > now).order_by(
        DoctorAvailabilitySlot.starts_at
    )
    slots = list(db.scalars(stmt).all())
    if not slots:
        return []

    range_start = slots[0].starts_at
    range_end = slots[-1].ends_at
    booked = get_booked_ranges(db, doctor_id, range_start, range_end)

    if only_free:
        return [s for s in slots if not _overlaps_booked(s.starts_at, s.ends_at, booked)]
    return slots


def get_availability_slot(
    db: Session,
    doctor_id: int,
    starts_at: datetime,
) -> DoctorAvailabilitySlot | None:
    starts_at = _normalize_dt(starts_at)
    slots = db.scalars(
        select(DoctorAvailabilitySlot).where(
            DoctorAvailabilitySlot.doctor_id == doctor_id,
            DoctorAvailabilitySlot.is_active.is_(True),
        )
    ).all()
    for slot in slots:
        if _normalize_dt(slot.starts_at) == starts_at:
            return slot
    return None


def is_slot_available(db: Session, doctor_id: int, starts_at: datetime, ends_at: datetime) -> bool:
    starts_at = _normalize_dt(starts_at)
    ends_at = _normalize_dt(ends_at)
    slot = get_availability_slot(db, doctor_id, starts_at)
    if not slot or _normalize_dt(slot.ends_at) != ends_at:
        return False
    if starts_at <= datetime.now(timezone.utc):
        return False
    booked = get_booked_ranges(
        db,
        doctor_id,
        starts_at - timedelta(seconds=1),
        ends_at + timedelta(seconds=1),
    )
    return not _overlaps_booked(starts_at, ends_at, booked)


def create_availability_slot(
    db: Session,
    doctor: Doctor,
    starts_at: datetime,
    ends_at: datetime,
) -> DoctorAvailabilitySlot:
    starts_at = _normalize_dt(starts_at)
    ends_at = _normalize_dt(ends_at)
    if ends_at <= starts_at:
        raise HTTPException(status_code=400, detail=ErrorDetail.ENDS_BEFORE_STARTS)
    if starts_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail=ErrorDetail.SLOT_IN_PAST)

    existing = get_availability_slot(db, doctor.id, starts_at)
    if existing:
        raise HTTPException(status_code=409, detail=ErrorDetail.SLOT_ALREADY_EXISTS)

    overlap = db.scalar(
        select(DoctorAvailabilitySlot).where(
            DoctorAvailabilitySlot.doctor_id == doctor.id,
            DoctorAvailabilitySlot.is_active.is_(True),
            DoctorAvailabilitySlot.starts_at < ends_at,
            DoctorAvailabilitySlot.ends_at > starts_at,
        )
    )
    if overlap:
        raise HTTPException(status_code=409, detail=ErrorDetail.SLOT_OVERLAPS)

    slot = DoctorAvailabilitySlot(
        doctor_id=doctor.id,
        starts_at=starts_at,
        ends_at=ends_at,
    )
    db.add(slot)
    db.flush()
    return slot


def delete_availability_slot(db: Session, slot: DoctorAvailabilitySlot) -> None:
    booked = get_booked_ranges(
        db,
        slot.doctor_id,
        slot.starts_at,
        slot.ends_at + timedelta(seconds=1),
    )
    if _overlaps_booked(slot.starts_at, slot.ends_at, booked):
        raise HTTPException(status_code=409, detail=ErrorDetail.SLOT_HAS_APPOINTMENT)
    db.delete(slot)
