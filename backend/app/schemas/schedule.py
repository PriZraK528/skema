from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.schemas.common import ORMModel


class AvailabilitySlotCreate(BaseModel):
    starts_at: datetime
    ends_at: datetime | None = None
    duration_minutes: int | None = Field(default=None, ge=5, le=480)

    @model_validator(mode="after")
    def validate_interval(self):
        if self.ends_at is None and self.duration_minutes is None:
            raise ValueError("Provide ends_at or duration_minutes")
        if self.ends_at and self.duration_minutes:
            raise ValueError("Provide only ends_at or duration_minutes, not both")
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
