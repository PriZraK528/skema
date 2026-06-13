from __future__ import annotations

import re

from app.constants import (
    MAX_FULL_NAME_LENGTH,
    MAX_NOTE_LENGTH,
    MAX_PASSWORD_LENGTH,
    MAX_SPECIALIZATION_LENGTH,
    MIN_FULL_NAME_LENGTH,
    MIN_PASSWORD_LENGTH,
    MIN_SPECIALIZATION_LENGTH,
    PHONE_ERROR,
)

_DIGITS_RE = re.compile(r"\D")


def normalize_text(value: str, *, field: str, min_len: int, max_len: int) -> str:
    text = " ".join(value.strip().split())
    if len(text) < min_len:
        raise ValueError(f"{field}: минимум {min_len} символа")
    if len(text) > max_len:
        raise ValueError(f"{field}: максимум {max_len} символов")
    return text


def normalize_full_name(value: str) -> str:
    return normalize_text(
        value,
        field="ФИО",
        min_len=MIN_FULL_NAME_LENGTH,
        max_len=MAX_FULL_NAME_LENGTH,
    )


def normalize_patient_name(value: str) -> str:
    return normalize_text(
        value,
        field="ФИО пациента",
        min_len=MIN_FULL_NAME_LENGTH,
        max_len=MAX_FULL_NAME_LENGTH,
    )


def normalize_specialization(value: str) -> str:
    return normalize_text(
        value,
        field="Специальность",
        min_len=MIN_SPECIALIZATION_LENGTH,
        max_len=MAX_SPECIALIZATION_LENGTH,
    )


def normalize_password(value: str) -> str:
    if len(value) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Пароль: минимум {MIN_PASSWORD_LENGTH} символов")
    if len(value) > MAX_PASSWORD_LENGTH:
        raise ValueError(f"Пароль: максимум {MAX_PASSWORD_LENGTH} символов")
    return value


def normalize_phone(value: str) -> str:
    digits = _DIGITS_RE.sub("", value.strip())

    if len(digits) == 11 and digits.startswith("8"):
        digits = "7" + digits[1:]
    elif len(digits) == 10:
        digits = "7" + digits
    elif len(digits) == 11 and digits.startswith("7"):
        pass
    else:
        raise ValueError(PHONE_ERROR)

    if len(digits) != 11 or not digits.startswith("7"):
        raise ValueError(PHONE_ERROR)

    return f"+{digits}"


def normalize_note(value: str | None) -> str | None:
    if value is None:
        return None
    note = value.strip()
    if not note:
        return None
    if len(note) > MAX_NOTE_LENGTH:
        raise ValueError(f"Комментарий: максимум {MAX_NOTE_LENGTH} символов")
    return note
