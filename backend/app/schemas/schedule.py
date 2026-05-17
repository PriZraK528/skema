from __future__ import annotations

from datetime import date, datetime, time

from pydantic import BaseModel, Field, field_validator, model_validator

from app.schemas.common import ORMModel


class ScheduleRuleCreate(BaseModel):
    weekday: int = Field(ge=0, le=6, description="0=Monday, 6=Sunday")
    start_time: time
    end_time: time
    slot_minutes: int = Field(default=30, ge=5, le=240)

    @model_validator(mode="after")
    def end_after_start(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class ScheduleRuleUpdate(BaseModel):
    start_time: time | None = None
    end_time: time | None = None
    slot_minutes: int | None = Field(default=None, ge=5, le=240)
    is_active: bool | None = None


class ScheduleRuleOut(ORMModel):
    id: int
    doctor_id: int
    weekday: int
    start_time: time
    end_time: time
    slot_minutes: int
    is_active: bool


class ScheduleExceptionCreate(BaseModel):
    exception_date: date
    is_day_off: bool = False
    start_time: time | None = None
    end_time: time | None = None
    slot_minutes: int | None = Field(default=None, ge=5, le=240)
    reason: str | None = Field(default=None, max_length=300)

    @model_validator(mode="after")
    def validate_hours(self):
        if self.is_day_off:
            return self
        if not self.start_time or not self.end_time:
            raise ValueError("start_time and end_time required when not a day off")
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class ScheduleExceptionOut(ORMModel):
    id: int
    doctor_id: int
    exception_date: date
    is_day_off: bool
    start_time: time | None
    end_time: time | None
    slot_minutes: int | None
    reason: str | None


class FreeSlotOut(BaseModel):
    doctor_id: int
    starts_at: datetime
    ends_at: datetime


class DoctorOut(ORMModel):
    id: int
    user_id: int
    full_name: str
    specialization: str
    email: str | None = None
