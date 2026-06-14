from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.constants import DOCTOR_SPECIALIZATIONS, ErrorDetail, TOKEN_TYPE_REFRESH
from app.db import get_db
from app.deps import get_current_user
from app.models import Doctor, Patient, User, UserRole
from app.schemas.auth import AuthResponse, LoginRequest, ProfileUpdate, RefreshRequest, RegisterRequest
from app.schemas.common import TokenPair, UserPublic
from app.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.services.user_utils import user_to_public
from app.settings import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/specializations", response_model=list[str])
def list_specializations() -> list[str]:
    return list(DOCTOR_SPECIALIZATIONS)


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    exists = db.scalar(select(User).where(User.email == payload.email))
    if exists:
        raise HTTPException(status_code=409, detail=ErrorDetail.EMAIL_ALREADY_REGISTERED)

    if payload.role == UserRole.doctor:
        if payload.clinic_key != settings.clinic_registration_key:
            raise HTTPException(status_code=403, detail=ErrorDetail.INVALID_CLINIC_KEY)

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role,
        full_name=payload.full_name,
        phone=payload.phone,
    )
    db.add(user)
    db.flush()

    if payload.role == UserRole.patient:
        db.add(
            Patient(user_id=user.id, full_name=payload.full_name, phone=payload.phone)
        )
    elif payload.role == UserRole.doctor:
        db.add(
            Doctor(
                user_id=user.id,
                full_name=payload.full_name,
                specialization=payload.specialization.strip(),
            )
        )

    db.commit()
    db.refresh(user)
    return AuthResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user=user_to_public(user),
    )


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail=ErrorDetail.INVALID_CREDENTIALS)
    return AuthResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user=user_to_public(user),
    )


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    try:
        data = decode_token(payload.refresh_token)
    except JWTError:
        raise HTTPException(status_code=401, detail=ErrorDetail.INVALID_REFRESH_TOKEN)
    if data.get("type") != TOKEN_TYPE_REFRESH:
        raise HTTPException(status_code=401, detail=ErrorDetail.INVALID_TOKEN_TYPE)
    try:
        user_id = int(data["sub"])
    except (KeyError, TypeError, ValueError):
        raise HTTPException(status_code=401, detail=ErrorDetail.INVALID_REFRESH_TOKEN)
    if not db.get(User, user_id):
        raise HTTPException(status_code=401, detail=ErrorDetail.INVALID_REFRESH_TOKEN)
    return TokenPair(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )


@router.patch("/me", response_model=UserPublic)
def update_profile(
    payload: ProfileUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.full_name is not None:
        user.full_name = payload.full_name
        if user.patient:
            user.patient.full_name = payload.full_name
        if user.doctor:
            user.doctor.full_name = payload.full_name
    if payload.phone is not None:
        user.phone = payload.phone
        if user.patient:
            user.patient.phone = payload.phone
    if payload.specialization is not None and user.doctor:
        user.doctor.specialization = payload.specialization.strip()
    if payload.password:
        user.password_hash = hash_password(payload.password)
    db.commit()
    db.refresh(user)
    return user_to_public(user)
