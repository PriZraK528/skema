from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.models import AppointmentStatus
from app.schemas.common import ORMModel


class AppointmentCreate(BaseModel):
    doctor_id: int
    starts_at: datetime
    note: str | None = Field(default=None, max_length=500)
    patient_id: int | None = None


class AppointmentAssign(BaseModel):
    patient_id: int | None = None
    patient_name: str | None = Field(default=None, min_length=2, max_length=200)
    doctor_id: int | None = None
    starts_at: datetime
    note: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def require_patient_ref(self) -> "AppointmentAssign":
        if self.patient_id is None and not (self.patient_name and self.patient_name.strip()):
            raise ValueError("patient_name is required")
        return self


class AppointmentOut(ORMModel):
    id: int
    patient_id: int
    doctor_id: int
    starts_at: datetime
    ends_at: datetime
    status: AppointmentStatus
    note: str | None
    created_at: datetime
    updated_at: datetime
    patient_name: str | None = None
    doctor_name: str | None = None
    specialization: str | None = None
