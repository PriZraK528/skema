from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.constants import (
    MAX_FULL_NAME_LENGTH,
    MAX_PASSWORD_LENGTH,
    MAX_SPECIALIZATION_LENGTH,
    MIN_FULL_NAME_LENGTH,
    MIN_PASSWORD_LENGTH,
    MIN_SPECIALIZATION_LENGTH,
    PHONE_INPUT_MAX_LENGTH,
    PHONE_INPUT_MIN_LENGTH,
)
from app.models import UserRole
from app.schemas.common import TokenPair, UserPublic
from app.validators import (
    normalize_full_name,
    normalize_password,
    normalize_phone,
    normalize_specialization,
)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH)
    role: UserRole = UserRole.patient
    full_name: str = Field(min_length=MIN_FULL_NAME_LENGTH, max_length=MAX_FULL_NAME_LENGTH)
    phone: str = Field(min_length=PHONE_INPUT_MIN_LENGTH, max_length=PHONE_INPUT_MAX_LENGTH)
    specialization: str | None = Field(
        default=None, min_length=MIN_SPECIALIZATION_LENGTH, max_length=MAX_SPECIALIZATION_LENGTH
    )
    clinic_key: str | None = Field(default=None, min_length=1, max_length=128)

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        return normalize_full_name(value)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return normalize_password(value)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        return normalize_phone(value)

    @field_validator("specialization")
    @classmethod
    def validate_specialization(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return normalize_specialization(value)

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: UserRole) -> UserRole:
        if value == UserRole.admin:
            raise ValueError("Нельзя зарегистрироваться как администратор")
        return value

    @model_validator(mode="after")
    def validate_doctor_fields(self) -> "RegisterRequest":
        if self.role == UserRole.doctor:
            if not self.specialization or not self.specialization.strip():
                raise ValueError("Укажите специальность")
            if not self.clinic_key or not self.clinic_key.strip():
                raise ValueError("Укажите ключ клиники")
        return self


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=MAX_PASSWORD_LENGTH)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class AuthResponse(TokenPair):
    user: UserPublic


class ProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=MIN_FULL_NAME_LENGTH, max_length=MAX_FULL_NAME_LENGTH)
    phone: str | None = Field(default=None, min_length=PHONE_INPUT_MIN_LENGTH, max_length=PHONE_INPUT_MAX_LENGTH)
    password: str | None = Field(default=None, min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH)
    specialization: str | None = Field(
        default=None, min_length=MIN_SPECIALIZATION_LENGTH, max_length=MAX_SPECIALIZATION_LENGTH
    )

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return normalize_full_name(value)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return normalize_password(value)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return normalize_phone(value)

    @field_validator("specialization")
    @classmethod
    def validate_specialization(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return normalize_specialization(value)
