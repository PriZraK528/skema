from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.constants import (
    MAX_SLOT_DURATION_MINUTES,
    MIN_SLOT_DURATION_MINUTES,
)
from app.schemas.common import ORMModel


class AvailabilitySlotCreate(BaseModel):
    starts_at: datetime
    ends_at: datetime | None = None
    duration_minutes: int | None = Field(
        default=None, ge=MIN_SLOT_DURATION_MINUTES, le=MAX_SLOT_DURATION_MINUTES
    )

    @model_validator(mode="after")
    def validate_interval(self):
        if self.ends_at is None and self.duration_minutes is None:
            raise ValueError("Укажите конец приёма или длительность")
        if self.ends_at and self.duration_minutes:
            raise ValueError("Укажите только конец приёма или длительность, не оба поля")
        return self


class AvailabilitySlotOut(ORMModel):
    id: int
    doctor_id: int
    starts_at: datetime
    ends_at: datetime
    is_active: bool
    is_booked: bool = False


class FreeSlotOut(BaseModel):
    doctor_id: int
    starts_at: datetime
    ends_at: datetime
    slot_id: int | None = None


class DoctorOut(ORMModel):
    id: int
    user_id: int
    full_name: str
    specialization: str
    email: str | None = None
