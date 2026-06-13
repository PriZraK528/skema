from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.constants import MIN_PASSWORD_LENGTH
from app.models import UserRole
from app.schemas.common import TokenPair, UserPublic


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=MIN_PASSWORD_LENGTH, max_length=128)
    role: UserRole = UserRole.patient
    full_name: str = Field(min_length=2, max_length=200)
    phone: str = Field(min_length=5, max_length=32)
    specialization: str | None = Field(default=None, min_length=2, max_length=200)
    clinic_key: str | None = Field(default=None, min_length=1, max_length=128)

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: UserRole) -> UserRole:
        if value == UserRole.admin:
            raise ValueError("Cannot self-register as admin")
        return value

    @model_validator(mode="after")
    def validate_doctor_fields(self) -> "RegisterRequest":
        if self.role == UserRole.doctor:
            if not self.specialization or not self.specialization.strip():
                raise ValueError("specialization is required for doctors")
            if not self.clinic_key or not self.clinic_key.strip():
                raise ValueError("clinic_key is required for doctors")
        return self


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class AuthResponse(TokenPair):
    user: UserPublic


class ProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=200)
    phone: str | None = Field(default=None, min_length=5, max_length=32)
    password: str | None = Field(default=None, min_length=MIN_PASSWORD_LENGTH, max_length=128)
    specialization: str | None = Field(default=None, min_length=2, max_length=200)
