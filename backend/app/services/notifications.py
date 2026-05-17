from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import Notification, NotificationType, User


def create_notification(
    db: Session,
    *,
    user_id: int,
    ntype: NotificationType,
    title: str,
    message: str,
    appointment_id: int | None = None,
) -> Notification:
    notification = Notification(
        user_id=user_id,
        type=ntype,
        title=title,
        message=message,
        appointment_id=appointment_id,
    )
    db.add(notification)
    return notification


def notify_users(db: Session, users: list[User], **kwargs) -> None:
    for user in users:
        create_notification(db, user_id=user.id, **kwargs)
