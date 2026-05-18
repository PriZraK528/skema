from __future__ import annotations

from app.models import User
from app.schemas.common import UserPublic


def user_to_public(user: User) -> UserPublic:
    full_name = user.full_name
    phone = user.phone
    if user.patient:
        full_name = full_name or user.patient.full_name
        phone = phone or user.patient.phone
    elif user.doctor:
        full_name = full_name or user.doctor.full_name
    return UserPublic(
        id=user.id,
        email=user.email,
        role=user.role.value,
        full_name=full_name,
        phone=phone,
        created_at=user.created_at,
    )
