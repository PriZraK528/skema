from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

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
from app.services.schedule import get_day_schedule, is_slot_available


def _appointment_duration_minutes(db: Session, doctor_id: int, starts_at: datetime) -> int:
    working, _, _, slot_minutes = get_day_schedule(db, doctor_id, starts_at.date())
    return slot_minutes if working else 30


def enrich_appointment(appointment: Appointment) -> AppointmentOut:
    return AppointmentOut(
        id=appointment.id,
        patient_id=appointment.patient_id,
        doctor_id=appointment.doctor_id,
        starts_at=appointment.starts_at,
        ends_at=appointment.ends_at,
        status=appointment.status,
        note=appointment.note,
        rescheduled_from_id=appointment.rescheduled_from_id,
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    return appointment


def resolve_patient_id(db: Session, user: User, patient_id: int | None) -> int:
    if user.role == UserRole.patient:
        if not user.patient:
            raise HTTPException(status_code=400, detail="Patient profile missing")
        if patient_id and patient_id != user.patient.id:
            raise HTTPException(status_code=403, detail="Cannot book for another patient")
        return user.patient.id
    if patient_id is None:
        raise HTTPException(status_code=400, detail="patient_id is required")
    patient = db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient_id


def create_appointment(
    db: Session,
    *,
    user: User,
    doctor_id: int,
    starts_at: datetime,
    note: str | None,
    patient_id: int | None,
) -> Appointment:
    if starts_at.tzinfo is None:
        starts_at = starts_at.replace(tzinfo=timezone.utc)

    doctor = db.get(Doctor, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    if user.role == UserRole.doctor and user.doctor and user.doctor.id != doctor_id:
        if patient_id is None:
            raise HTTPException(status_code=403, detail="Doctor can only use own schedule when assigning")

    pid = resolve_patient_id(db, user, patient_id)
    duration = _appointment_duration_minutes(db, doctor_id, starts_at)
    ends_at = starts_at + timedelta(minutes=duration)

    if not is_slot_available(db, doctor_id, starts_at, ends_at):
        raise HTTPException(status_code=409, detail="Selected time slot is not available")

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
        raise HTTPException(status_code=404, detail="Patient not found")
    msg = f"Запись на приём {starts_at.isoformat()} к врачу {doctor.full_name}"
    create_notification(
        db,
        user_id=patient.user_id,
        ntype=NotificationType.appointment_booked,
        title="Запись подтверждена",
        message=msg,
        appointment_id=appointment.id,
    )
    create_notification(
        db,
        user_id=doctor.user_id,
        ntype=NotificationType.appointment_booked,
        title="Новая запись",
        message=msg,
        appointment_id=appointment.id,
    )
    db.commit()
    db.refresh(appointment)
    return load_appointment(db, appointment.id)


def cancel_appointment(db: Session, appointment: Appointment, user: User) -> Appointment:
    if appointment.status != AppointmentStatus.booked:
        raise HTTPException(status_code=400, detail="Only booked appointments can be cancelled")
    _check_access(appointment, user, write=True)
    appointment.status = AppointmentStatus.cancelled
    appointment.updated_at = datetime.now(timezone.utc)
    msg = f"Запись {appointment.starts_at.isoformat()} отменена"
    for uid in {appointment.patient.user_id, appointment.doctor.user_id}:
        create_notification(
            db,
            user_id=uid,
            ntype=NotificationType.appointment_cancelled,
            title="Запись отменена",
            message=msg,
            appointment_id=appointment.id,
        )
    db.commit()
    return load_appointment(db, appointment.id)


def reschedule_appointment(
    db: Session,
    appointment: Appointment,
    user: User,
    new_starts_at: datetime,
    note: str | None,
) -> Appointment:
    if appointment.status != AppointmentStatus.booked:
        raise HTTPException(status_code=400, detail="Only booked appointments can be rescheduled")
    _check_access(appointment, user, write=True)

    if new_starts_at.tzinfo is None:
        new_starts_at = new_starts_at.replace(tzinfo=timezone.utc)

    duration = _appointment_duration_minutes(db, appointment.doctor_id, new_starts_at)
    new_ends_at = new_starts_at + timedelta(minutes=duration)

    if not is_slot_available(db, appointment.doctor_id, new_starts_at, new_ends_at):
        raise HTTPException(status_code=409, detail="Selected time slot is not available")

    old_start = appointment.starts_at
    appointment.status = AppointmentStatus.cancelled
    appointment.updated_at = datetime.now(timezone.utc)

    new_appt = Appointment(
        patient_id=appointment.patient_id,
        doctor_id=appointment.doctor_id,
        starts_at=new_starts_at,
        ends_at=new_ends_at,
        status=AppointmentStatus.booked,
        note=note or appointment.note,
        rescheduled_from_id=appointment.id,
    )
    db.add(new_appt)
    db.flush()

    msg = f"Запись перенесена с {old_start.isoformat()} на {new_starts_at.isoformat()}"
    for uid in {appointment.patient.user_id, appointment.doctor.user_id}:
        create_notification(
            db,
            user_id=uid,
            ntype=NotificationType.appointment_rescheduled,
            title="Запись перенесена",
            message=msg,
            appointment_id=new_appt.id,
        )
    db.commit()
    return load_appointment(db, new_appt.id)


def _check_access(appointment: Appointment, user: User, write: bool = False) -> None:
    if user.role == UserRole.admin or user.role == UserRole.registrar:
        return
    if user.role == UserRole.patient and user.patient and appointment.patient_id == user.patient.id:
        return
    if user.role == UserRole.doctor and user.doctor and appointment.doctor_id == user.doctor.id:
        return
    raise HTTPException(status_code=403, detail="Access denied")


def list_appointments_query(db: Session, user: User):  # noqa: ANN201
    q = select(Appointment).options(
        joinedload(Appointment.patient).joinedload(Patient.user),
        joinedload(Appointment.doctor).joinedload(Doctor.user),
    )
    if user.role == UserRole.patient and user.patient:
        q = q.where(Appointment.patient_id == user.patient.id)
    elif user.role == UserRole.doctor and user.doctor:
        q = q.where(Appointment.doctor_id == user.doctor.id)
    return q
