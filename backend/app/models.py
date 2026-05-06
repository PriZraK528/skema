import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint
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
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    patient: Mapped["Patient | None"] = relationship(back_populates="user", uselist=False)
    doctor: Mapped["Doctor | None"] = relationship(back_populates="user", uselist=False)


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
    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus, name="appointment_status"),
        default=AppointmentStatus.booked,
        nullable=False,
    )
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    patient: Mapped[Patient] = relationship(back_populates="appointments")
    doctor: Mapped[Doctor] = relationship(back_populates="appointments")

