from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator

from app.constants import MAX_FULL_NAME_LENGTH, MAX_NOTE_LENGTH, MIN_FULL_NAME_LENGTH
from app.models import AppointmentStatus
from app.schemas.common import ORMModel
from app.validators import normalize_note, normalize_patient_name


class AppointmentCreate(BaseModel):
    doctor_id: int = Field(ge=1)
    starts_at: datetime
    note: str | None = Field(default=None, max_length=MAX_NOTE_LENGTH)
    patient_id: int | None = Field(default=None, ge=1)

    @field_validator("note")
    @classmethod
    def validate_note(cls, value: str | None) -> str | None:
        return normalize_note(value)


class AppointmentAssign(BaseModel):
    patient_id: int | None = Field(default=None, ge=1)
    patient_name: str | None = Field(default=None, min_length=MIN_FULL_NAME_LENGTH, max_length=MAX_FULL_NAME_LENGTH)
    doctor_id: int | None = Field(default=None, ge=1)
    starts_at: datetime
    note: str | None = Field(default=None, max_length=MAX_NOTE_LENGTH)

    @field_validator("patient_name")
    @classmethod
    def validate_patient_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return normalize_patient_name(value)

    @field_validator("note")
    @classmethod
    def validate_note(cls, value: str | None) -> str | None:
        return normalize_note(value)

    @model_validator(mode="after")
    def require_patient_ref(self) -> "AppointmentAssign":
        if self.patient_id is None and not (self.patient_name and self.patient_name.strip()):
            raise ValueError("Укажите ФИО пациента")
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
