from __future__ import annotations

import re

from app.constants import (
    MAX_SLOT_DURATION_MINUTES,
    MIN_SLOT_DURATION_MINUTES,
)

FIELD_LABELS: dict[str, str] = {
    "email": "Email",
    "password": "Пароль",
    "full_name": "ФИО",
    "phone": "Телефон",
    "specialization": "Специальность",
    "clinic_key": "Ключ клиники",
    "patient_name": "ФИО пациента",
    "note": "Комментарий",
    "starts_at": "Начало приёма",
    "ends_at": "Конец приёма",
    "duration_minutes": "Длительность",
    "doctor_id": "Врач",
    "role": "Роль",
}


def translate_validation_error(error: dict) -> str:
    msg = str(error.get("msg", ""))
    loc = error.get("loc", ())
    field = str(loc[-1]) if loc else ""
    label = FIELD_LABELS.get(field, field)

    if msg.startswith("Value error, "):
        return msg.removeprefix("Value error, ")

    if msg == "Field required":
        return f"{label}: обязательное поле" if label else "Обязательное поле"

    if "valid email" in msg or "value is not a valid email" in msg:
        return "Некорректный email"

    min_match = re.match(r"^String should have at least (\d+) characters?$", msg)
    if min_match:
        n = min_match.group(1)
        return f"{label}: минимум {n} символов" if label else f"Минимум {n} символов"

    max_match = re.match(r"^String should have at most (\d+) characters?$", msg)
    if max_match:
        n = max_match.group(1)
        return f"{label}: максимум {n} символов" if label else f"Максимум {n} символов"

    ge_match = re.match(r"^Input should be greater than or equal to (\d+)$", msg)
    if ge_match:
        n = ge_match.group(1)
        return f"{label}: не меньше {n}" if label else f"Значение не меньше {n}"

    le_match = re.match(r"^Input should be less than or equal to (\d+)$", msg)
    if le_match:
        n = le_match.group(1)
        return f"{label}: не больше {n}" if label else f"Значение не больше {n}"

    if msg == "Input should be a valid datetime":
        return f"{label}: некорректная дата и время" if label else "Некорректная дата и время"

    if msg == "Input should be a valid integer":
        return f"{label}: укажите целое число" if label else "Укажите целое число"

    if field == "duration_minutes" and "greater than or equal" in msg:
        return f"Длительность: от {MIN_SLOT_DURATION_MINUTES} до {MAX_SLOT_DURATION_MINUTES} минут"

    return msg
