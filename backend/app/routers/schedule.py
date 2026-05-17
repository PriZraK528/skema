from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user, require_roles
from app.models import Doctor, DoctorScheduleRule, NotificationType, ScheduleException, User, UserRole
from app.schemas.common import MessageResponse
from app.schemas.schedule import (
    FreeSlotOut,
    ScheduleExceptionCreate,
    ScheduleExceptionOut,
    ScheduleRuleCreate,
    ScheduleRuleOut,
    ScheduleRuleUpdate,
)
from app.services.notifications import create_notification, notify_users
from app.services.schedule import compute_free_slots

router = APIRouter(tags=["schedule"])


def _get_doctor_or_404(db: Session, doctor_id: int) -> Doctor:
    doctor = db.get(Doctor, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


def _ensure_schedule_access(doctor: Doctor, user: User, write: bool = False) -> None:
    if user.role in (UserRole.admin, UserRole.registrar):
        return
    if user.role == UserRole.doctor and user.doctor and user.doctor.id == doctor.id:
        return
    if not write:
        return
    raise HTTPException(status_code=403, detail="Cannot modify this schedule")


@router.get("/doctors/{doctor_id}/schedule/rules", response_model=list[ScheduleRuleOut])
def list_schedule_rules(
    doctor_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _get_doctor_or_404(db, doctor_id)
    rules = db.scalars(
        select(DoctorScheduleRule).where(DoctorScheduleRule.doctor_id == doctor_id)
    ).all()
    return rules


@router.post(
    "/doctors/{doctor_id}/schedule/rules",
    response_model=ScheduleRuleOut,
    status_code=status.HTTP_201_CREATED,
)
def create_schedule_rule(
    doctor_id: int,
    payload: ScheduleRuleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.doctor, UserRole.registrar)),
):
    doctor = _get_doctor_or_404(db, doctor_id)
    _ensure_schedule_access(doctor, user, write=True)
    existing = db.scalar(
        select(DoctorScheduleRule).where(
            DoctorScheduleRule.doctor_id == doctor_id,
            DoctorScheduleRule.weekday == payload.weekday,
        )
    )
    if existing:
        raise HTTPException(status_code=409, detail="Rule for this weekday already exists")
    rule = DoctorScheduleRule(doctor_id=doctor_id, **payload.model_dump())
    db.add(rule)
    _notify_schedule_change(db, doctor, "Добавлено правило расписания")
    db.commit()
    db.refresh(rule)
    return rule


@router.patch("/schedule/rules/{rule_id}", response_model=ScheduleRuleOut)
def update_schedule_rule(
    rule_id: int,
    payload: ScheduleRuleUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.doctor, UserRole.registrar)),
):
    rule = db.get(DoctorScheduleRule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    doctor = _get_doctor_or_404(db, rule.doctor_id)
    _ensure_schedule_access(doctor, user, write=True)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(rule, key, value)
    _notify_schedule_change(db, doctor, "Изменено правило расписания")
    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/schedule/rules/{rule_id}", response_model=MessageResponse)
def delete_schedule_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.doctor, UserRole.registrar)),
):
    rule = db.get(DoctorScheduleRule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    doctor = _get_doctor_or_404(db, rule.doctor_id)
    _ensure_schedule_access(doctor, user, write=True)
    db.delete(rule)
    _notify_schedule_change(db, doctor, "Удалено правило расписания")
    db.commit()
    return MessageResponse(message="Rule deleted")


@router.get("/doctors/{doctor_id}/schedule/exceptions", response_model=list[ScheduleExceptionOut])
def list_exceptions(
    doctor_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _get_doctor_or_404(db, doctor_id)
    return db.scalars(
        select(ScheduleException).where(ScheduleException.doctor_id == doctor_id)
    ).all()


@router.post(
    "/doctors/{doctor_id}/schedule/exceptions",
    response_model=ScheduleExceptionOut,
    status_code=status.HTTP_201_CREATED,
)
def create_exception(
    doctor_id: int,
    payload: ScheduleExceptionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.doctor, UserRole.registrar)),
):
    doctor = _get_doctor_or_404(db, doctor_id)
    _ensure_schedule_access(doctor, user, write=True)
    exc = ScheduleException(doctor_id=doctor_id, **payload.model_dump())
    db.add(exc)
    _notify_schedule_change(db, doctor, f"Исключение в расписании на {payload.exception_date}")
    db.commit()
    db.refresh(exc)
    return exc


@router.get("/doctors/{doctor_id}/slots/free", response_model=list[FreeSlotOut])
def free_slots(
    doctor_id: int,
    from_date: date = Query(..., alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    doctor = _get_doctor_or_404(db, doctor_id)
    if to_date is None:
        to_date = from_date + timedelta(days=13)
    if to_date < from_date:
        raise HTTPException(status_code=400, detail="'to' must be >= 'from'")
    slots = compute_free_slots(db, doctor, from_date, to_date)
    return [
        FreeSlotOut(doctor_id=doctor_id, starts_at=s, ends_at=e) for s, e in slots
    ]


@router.post("/doctors/{doctor_id}/schedule/refresh", response_model=MessageResponse)
def refresh_schedule(
    doctor_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.doctor, UserRole.registrar)),
):
    """Recompute availability cache and notify patients with upcoming bookings if slots changed."""
    doctor = _get_doctor_or_404(db, doctor_id)
    _ensure_schedule_access(doctor, user, write=True)
    today = datetime.now(timezone.utc).date()
    compute_free_slots(db, doctor, today, today + timedelta(days=30))
    _notify_schedule_change(db, doctor, "Расписание автоматически обновлено")
    db.commit()
    return MessageResponse(message="Schedule refreshed")


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
