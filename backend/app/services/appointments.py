from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session, joinedload

from app.constants import (
    ErrorDetail,
    NOTIFICATION_TITLE_BOOKED,
    NOTIFICATION_TITLE_CANCELLED,
    NOTIFICATION_TITLE_NEW_APPOINTMENT,
)
from app.models import (
    Appointment,
    AppointmentStatus,
    Doctor,
    NotificationType,
    Patient,
    User,
    UserRole,
)
from app.schemas.appointment import AppointmentOut
from app.services.notifications import create_notification
from app.services.schedule import get_availability_slot, is_slot_available
from app.utils.formatting import format_dt_ru


def _ends_at_from_availability(db: Session, doctor_id: int, starts_at: datetime) -> datetime:
    from app.services.schedule import _normalize_dt

    slot = get_availability_slot(db, doctor_id, starts_at)
    if not slot:
        raise HTTPException(status_code=409, detail=ErrorDetail.SLOT_NOT_AVAILABLE)
    return _normalize_dt(slot.ends_at)


def enrich_appointment(appointment: Appointment) -> AppointmentOut:
    return AppointmentOut(
        id=appointment.id,
        patient_id=appointment.patient_id,
        doctor_id=appointment.doctor_id,
        starts_at=appointment.starts_at,
        ends_at=appointment.ends_at,
        status=appointment.status,
        note=appointment.note,
        created_at=appointment.created_at,
        updated_at=appointment.updated_at,
        patient_name=appointment.patient.full_name if appointment.patient else None,
        doctor_name=appointment.doctor.full_name if appointment.doctor else None,
        specialization=appointment.doctor.specialization if appointment.doctor else None,
    )


def load_appointment(db: Session, appointment_id: int) -> Appointment:
    appointment = db.scalar(
        select(Appointment)
        .options(joinedload(Appointment.patient), joinedload(Appointment.doctor))
        .where(Appointment.id == appointment_id)
    )
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorDetail.APPOINTMENT_NOT_FOUND,
        )
    return appointment


def resolve_patient_id(
    db: Session,
    user: User,
    patient_id: int | None,
    patient_name: str | None = None,
) -> int:
    if user.role == UserRole.patient:
        if not user.patient:
            raise HTTPException(status_code=400, detail=ErrorDetail.PATIENT_PROFILE_MISSING)
        if patient_id and patient_id != user.patient.id:
            raise HTTPException(status_code=403, detail=ErrorDetail.CANNOT_BOOK_FOR_OTHER)
        return user.patient.id
    if patient_id is not None:
        patient = db.get(Patient, patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail=ErrorDetail.PATIENT_NOT_FOUND)
        return patient_id
    if not patient_name or not patient_name.strip():
        raise HTTPException(status_code=400, detail=ErrorDetail.PATIENT_NAME_REQUIRED)
    name = patient_name.strip()
    exact = db.scalars(select(Patient).where(Patient.full_name.ilike(name))).all()
    exact_matches = [p for p in exact if p.full_name.lower() == name.lower()]
    if len(exact_matches) == 1:
        return exact_matches[0].id
    matches = db.scalars(select(Patient).where(Patient.full_name.ilike(f"%{name}%"))).all()
    if not matches:
        raise HTTPException(status_code=404, detail=ErrorDetail.PATIENT_NOT_FOUND)
    if len(matches) > 1:
        raise HTTPException(status_code=400, detail=ErrorDetail.MULTIPLE_PATIENTS_MATCH)
    return matches[0].id


def create_appointment(
    db: Session,
    *,
    user: User,
    doctor_id: int,
    starts_at: datetime,
    note: str | None,
    patient_id: int | None,
    patient_name: str | None = None,
) -> Appointment:
    from app.services.schedule import _normalize_dt

    starts_at = _normalize_dt(starts_at)

    doctor = db.get(Doctor, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail=ErrorDetail.DOCTOR_NOT_FOUND)

    if user.role == UserRole.doctor and user.doctor and user.doctor.id != doctor_id:
        if patient_id is None:
            raise HTTPException(status_code=403, detail=ErrorDetail.DOCTOR_OWN_SCHEDULE_ONLY)

    pid = resolve_patient_id(db, user, patient_id, patient_name)
    ends_at = _ends_at_from_availability(db, doctor_id, starts_at)

    if not is_slot_available(db, doctor_id, starts_at, ends_at):
        raise HTTPException(status_code=409, detail=ErrorDetail.SLOT_NOT_AVAILABLE)

    appointment = Appointment(
        patient_id=pid,
        doctor_id=doctor_id,
        starts_at=starts_at,
        ends_at=ends_at,
        status=AppointmentStatus.booked,
        note=note,
    )
    db.add(appointment)
    db.flush()

    patient = db.get(Patient, pid)
    if not patient:
        raise HTTPException(status_code=404, detail=ErrorDetail.PATIENT_NOT_FOUND)
    msg = f"Запись на приём {format_dt_ru(starts_at)} к врачу {doctor.full_name}"
    create_notification(
        db,
        user_id=patient.user_id,
        ntype=NotificationType.appointment_booked,
        title=NOTIFICATION_TITLE_BOOKED,
        message=msg,
        appointment_id=appointment.id,
    )
    create_notification(
        db,
        user_id=doctor.user_id,
        ntype=NotificationType.appointment_booked,
        title=NOTIFICATION_TITLE_NEW_APPOINTMENT,
        message=msg,
        appointment_id=appointment.id,
    )
    db.commit()
    db.refresh(appointment)
    return load_appointment(db, appointment.id)


def complete_past_appointments(db: Session) -> int:
    now = datetime.now(timezone.utc)
    result = db.execute(
        update(Appointment)
        .where(
            Appointment.status == AppointmentStatus.booked,
            Appointment.ends_at <= now,
        )
        .values(status=AppointmentStatus.completed, updated_at=now)
    )
    if result.rowcount:
        db.commit()
    return result.rowcount or 0


def cancel_appointment(db: Session, appointment: Appointment, user: User) -> Appointment:
    if appointment.status != AppointmentStatus.booked:
        raise HTTPException(status_code=400, detail=ErrorDetail.ONLY_BOOKED_CAN_CANCEL)
    _check_access(appointment, user, write=True)
    appointment.status = AppointmentStatus.cancelled
    appointment.updated_at = datetime.now(timezone.utc)
    msg = f"Запись {format_dt_ru(appointment.starts_at)} отменена"
    for uid in {appointment.patient.user_id, appointment.doctor.user_id}:
        create_notification(
            db,
            user_id=uid,
            ntype=NotificationType.appointment_cancelled,
            title=NOTIFICATION_TITLE_CANCELLED,
            message=msg,
            appointment_id=appointment.id,
        )
    db.commit()
    return load_appointment(db, appointment.id)


def _check_access(appointment: Appointment, user: User, write: bool = False) -> None:
    if user.role == UserRole.admin:
        return
    if user.role == UserRole.patient and user.patient and appointment.patient_id == user.patient.id:
        return
    if user.role == UserRole.doctor and user.doctor and appointment.doctor_id == user.doctor.id:
        return
    raise HTTPException(status_code=403, detail=ErrorDetail.ACCESS_DENIED)


def list_appointments_query(db: Session, user: User):
    q = select(Appointment).options(
        joinedload(Appointment.patient).joinedload(Patient.user),
        joinedload(Appointment.doctor).joinedload(Doctor.user),
    )
    if user.role == UserRole.patient and user.patient:
        q = q.where(Appointment.patient_id == user.patient.id)
    elif user.role == UserRole.doctor and user.doctor:
        q = q.where(Appointment.doctor_id == user.doctor.id)
    return q
