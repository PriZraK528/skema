from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.models import NotificationType
from app.schemas.common import ORMModel


class NotificationOut(ORMModel):
    id: int
    type: NotificationType
    title: str
    message: str
    is_read: bool
    appointment_id: int | None
    created_at: datetime


class NotificationMarkRead(BaseModel):
    is_read: bool = True
