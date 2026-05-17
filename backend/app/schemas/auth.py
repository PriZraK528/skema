from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models import UserRole
from app.schemas.common import ORMModel, TokenPair, UserPublic


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: UserRole = UserRole.patient
    full_name: str = Field(min_length=2, max_length=200)
    phone: str = Field(min_length=5, max_length=32)

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: UserRole) -> UserRole:
        if value == UserRole.admin:
            raise ValueError("Cannot self-register as admin")
        return value


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
    password: str | None = Field(default=None, min_length=8, max_length=128)
