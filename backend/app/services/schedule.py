from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Appointment, AppointmentStatus, Doctor, DoctorScheduleRule, ScheduleException


def _combine_utc(d: date, t: time) -> datetime:
    return datetime.combine(d, t, tzinfo=timezone.utc)


def _iter_slot_starts(start: time, end: time, slot_minutes: int) -> Iterable[time]:
    cursor = datetime.combine(date.today(), start)
    end_dt = datetime.combine(date.today(), end)
    delta = timedelta(minutes=slot_minutes)
    while cursor + delta <= end_dt:
        yield cursor.time()
        cursor += delta


def get_day_schedule(
    db: Session,
    doctor_id: int,
    day: date,
) -> tuple[bool, time | None, time | None, int]:
    """Return (is_working, start, end, slot_minutes)."""
    exception = db.scalar(
        select(ScheduleException).where(
            ScheduleException.doctor_id == doctor_id,
            ScheduleException.exception_date == day,
        )
    )
    if exception:
        if exception.is_day_off:
            return False, None, None, 30
        return True, exception.start_time, exception.end_time, exception.slot_minutes or 30

    weekday = day.weekday()
    rule = db.scalar(
        select(DoctorScheduleRule).where(
            DoctorScheduleRule.doctor_id == doctor_id,
            DoctorScheduleRule.weekday == weekday,
            DoctorScheduleRule.is_active.is_(True),
        )
    )
    if not rule:
        return False, None, None, 30
    return True, rule.start_time, rule.end_time, rule.slot_minutes


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


def compute_free_slots(
    db: Session,
    doctor: Doctor,
    from_date: date,
    to_date: date,
) -> list[tuple[datetime, datetime]]:
    slots: list[tuple[datetime, datetime]] = []
    day = from_date
    while day <= to_date:
        working, start_t, end_t, slot_minutes = get_day_schedule(db, doctor.id, day)
        if working and start_t and end_t:
            for slot_start in _iter_slot_starts(start_t, end_t, slot_minutes):
                starts_at = _combine_utc(day, slot_start)
                ends_at = starts_at + timedelta(minutes=slot_minutes)
                if starts_at > datetime.now(timezone.utc):
                    slots.append((starts_at, ends_at))
        day += timedelta(days=1)

    if not slots:
        return []

    range_start = slots[0][0]
    range_end = slots[-1][1]
    booked = get_booked_ranges(db, doctor.id, range_start, range_end)

    free: list[tuple[datetime, datetime]] = []
    for starts_at, ends_at in slots:
        overlap = any(not (ends_at <= b_start or starts_at >= b_end) for b_start, b_end in booked)
        if not overlap:
            free.append((starts_at, ends_at))
    return free


def is_slot_available(db: Session, doctor_id: int, starts_at: datetime, ends_at: datetime) -> bool:
    day = starts_at.date()
    working, start_t, end_t, slot_minutes = get_day_schedule(db, doctor_id, day)
    if not working or not start_t or not end_t:
        return False
    if starts_at.time() < start_t or ends_at.time() > end_t:
        return False
    expected_end = starts_at + timedelta(minutes=slot_minutes)
    if ends_at != expected_end:
        return False

    booked = get_booked_ranges(
        db,
        doctor_id,
        starts_at - timedelta(days=1),
        ends_at + timedelta(days=1),
    )
    for b_start, b_end in booked:
        if not (ends_at <= b_start or starts_at >= b_end):
            return False
    return True
