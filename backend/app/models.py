from __future__ import annotations

import enum
from datetime import date, datetime, time
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, String, Text, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


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
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", native_enum=False), nullable=False
    )
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
    schedule_rules: Mapped[list["DoctorScheduleRule"]] = relationship(back_populates="doctor")
    schedule_exceptions: Mapped[list["ScheduleException"]] = relationship(back_populates="doctor")


class DoctorScheduleRule(Base):
    """Weekly recurring working hours for a doctor."""

    __tablename__ = "doctor_schedule_rules"
    __table_args__ = (UniqueConstraint("doctor_id", "weekday", name="uq_doctor_weekday"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id", ondelete="CASCADE"), index=True)
    weekday: Mapped[int] = mapped_column(Integer, nullable=False)  # 0=Monday .. 6=Sunday
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    slot_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    doctor: Mapped[Doctor] = relationship(back_populates="schedule_rules")


class ScheduleException(Base):
    """Day-off or special hours overriding the weekly rule."""

    __tablename__ = "schedule_exceptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id", ondelete="CASCADE"), index=True)
    exception_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    is_day_off: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    start_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    end_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    slot_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)

    doctor: Mapped[Doctor] = relationship(back_populates="schedule_exceptions")


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
        Enum(AppointmentStatus, name="appointment_status", native_enum=False),
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
        Enum(NotificationType, name="notification_type", native_enum=False), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    appointment_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    user: Mapped[User] = relationship(back_populates="notifications")
