from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, db_enum


class UserRole(str, enum.Enum):
    admin = "admin"
    doctor = "doctor"
    patient = "patient"
    registrar = "registrar"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(db_enum(UserRole, "user_role"), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    patient: Mapped["Patient | None"] = relationship(back_populates="user", uselist=False)
    doctor: Mapped["Doctor | None"] = relationship(back_populates="user", uselist=False)
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user")


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), nullable=False)

    user: Mapped[User] = relationship(back_populates="patient")
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="patient")


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    specialization: Mapped[str] = mapped_column(String(200), nullable=False)

    user: Mapped[User] = relationship(back_populates="doctor")
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="doctor")
    availability_slots: Mapped[list["DoctorAvailabilitySlot"]] = relationship(
        back_populates="doctor"
    )


class DoctorAvailabilitySlot(Base):
    """Окно приёма, которое врач создаёт вручную. Без записи в этой таблице записаться нельзя."""

    __tablename__ = "doctor_availability_slots"
    __table_args__ = (
        UniqueConstraint("doctor_id", "starts_at", name="uq_doctor_availability_starts_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id", ondelete="CASCADE"), index=True)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    doctor: Mapped[Doctor] = relationship(back_populates="availability_slots")


class AppointmentStatus(str, enum.Enum):
    booked = "booked"
    cancelled = "cancelled"
    completed = "completed"


class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = (
        UniqueConstraint("doctor_id", "starts_at", name="uq_appointment_doctor_starts_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id", ondelete="CASCADE"), index=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id", ondelete="CASCADE"), index=True)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[AppointmentStatus] = mapped_column(
        db_enum(AppointmentStatus, "appointment_status"),
        default=AppointmentStatus.booked,
        nullable=False,
    )
    note: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    rescheduled_from_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    patient: Mapped[Patient] = relationship(back_populates="appointments")
    doctor: Mapped[Doctor] = relationship(back_populates="appointments")


class NotificationType(str, enum.Enum):
    appointment_booked = "appointment_booked"
    appointment_reminder = "appointment_reminder"
    appointment_cancelled = "appointment_cancelled"
    appointment_rescheduled = "appointment_rescheduled"
    schedule_changed = "schedule_changed"


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    type: Mapped[NotificationType] = mapped_column(
        db_enum(NotificationType, "notification_type"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    appointment_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    user: Mapped[User] = relationship(back_populates="notifications")
