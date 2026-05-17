from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session

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

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    exists = db.scalar(select(User).where(User.email == payload.email))
    if exists:
        raise HTTPException(status_code=409, detail="Email already registered")

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
                specialization="General",
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
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return AuthResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user=user_to_public(user),
    )


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest):
    try:
        data = decode_token(payload.refresh_token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    if data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
    user_id = int(data["sub"])
    return TokenPair(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )


@router.get("/me", response_model=UserPublic)
def me(user: User = Depends(get_current_user)):
    return user_to_public(user)


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
    if payload.password:
        user.password_hash = hash_password(payload.password)
    db.commit()
    db.refresh(user)
    return user_to_public(user)
