from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models import AppointmentStatus
from app.schemas.common import ORMModel


class AppointmentCreate(BaseModel):
    doctor_id: int
    starts_at: datetime
    note: str | None = Field(default=None, max_length=500)
    patient_id: int | None = None  # for doctor/registrar assignment


class AppointmentAssign(BaseModel):
    patient_id: int
    doctor_id: int | None = None
    starts_at: datetime
    note: str | None = Field(default=None, max_length=500)


class AppointmentReschedule(BaseModel):
    starts_at: datetime
    note: str | None = Field(default=None, max_length=500)


class AppointmentUpdate(BaseModel):
    status: AppointmentStatus | None = None
    note: str | None = Field(default=None, max_length=500)


class AppointmentOut(ORMModel):
    id: int
    patient_id: int
    doctor_id: int
    starts_at: datetime
    ends_at: datetime
    status: AppointmentStatus
    note: str | None
    rescheduled_from_id: int | None
    created_at: datetime
    updated_at: datetime
    patient_name: str | None = None
    doctor_name: str | None = None
    specialization: str | None = None
