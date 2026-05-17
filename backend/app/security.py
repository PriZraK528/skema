from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _create_token(subject: str, expires_delta: timedelta, token_type: str) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=ALGORITHM)


def create_access_token(user_id: int) -> str:
    return _create_token(
        str(user_id),
        timedelta(minutes=settings.jwt_access_token_expires_minutes),
        "access",
    )


def create_refresh_token(user_id: int) -> str:
    return _create_token(
        str(user_id),
        timedelta(days=settings.jwt_refresh_token_expires_days),
        "refresh",
    )


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[ALGORITHM])
