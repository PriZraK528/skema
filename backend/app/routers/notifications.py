from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.constants import (
    DEFAULT_NOTIFICATIONS_LIMIT,
    ErrorDetail,
    MAX_PAGE_LIMIT,
    NOTIFICATION_TITLE_REMINDER,
    REMINDER_WINDOW_HOURS,
)
from app.db import get_db
from app.deps import get_current_user, require_roles
from app.models import Appointment, AppointmentStatus, Notification, NotificationType, User, UserRole
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.notification import NotificationMarkRead, NotificationOut
from app.services.notifications import create_notification
from app.utils.formatting import format_dt_ru

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/unread-count")
def unread_count(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict[str, int]:
    count = db.scalar(
        select(func.count())
        .select_from(Notification)
        .where(Notification.user_id == user.id, Notification.is_read.is_(False))
    )
    return {"count": count or 0}


@router.get("", response_model=PaginatedResponse[NotificationOut])
def list_notifications(
    unread_only: bool = False,
    ntype: NotificationType | None = Query(default=None, alias="type"),
    limit: int = Query(default=DEFAULT_NOTIFICATIONS_LIMIT, ge=1, le=MAX_PAGE_LIMIT),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    stmt = select(Notification).where(Notification.user_id == user.id)
    if unread_only:
        stmt = stmt.where(Notification.is_read.is_(False))
    if ntype:
        stmt = stmt.where(Notification.type == ntype)
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.scalars(
        stmt.order_by(Notification.created_at.desc()).offset(offset).limit(limit)
    ).all()
    return PaginatedResponse(
        items=[NotificationOut.model_validate(n) for n in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.patch("/{notification_id}", response_model=NotificationOut)
def mark_read(
    notification_id: int,
    payload: NotificationMarkRead,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    notification = db.get(Notification, notification_id)
    if not notification or notification.user_id != user.id:
        raise HTTPException(status_code=404, detail=ErrorDetail.NOTIFICATION_NOT_FOUND)
    notification.is_read = payload.is_read
    db.commit()
    db.refresh(notification)
    return NotificationOut.model_validate(notification)


@router.post("/read-all", response_model=MessageResponse)
def mark_all_read(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    db.execute(
        update(Notification)
        .where(Notification.user_id == user.id, Notification.is_read.is_(False))
        .values(is_read=True)
    )
    db.commit()
    return MessageResponse(message="All notifications marked as read")


@router.post("/reminders/run", response_model=MessageResponse)
def run_reminders(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
):
    """Send reminders for appointments in the next N hours (cron-friendly endpoint)."""
    now = datetime.now(timezone.utc)
    window_end = now + timedelta(hours=REMINDER_WINDOW_HOURS)
    from sqlalchemy.orm import joinedload

    appointments = db.scalars(
        select(Appointment)
        .options(joinedload(Appointment.patient), joinedload(Appointment.doctor))
        .where(
            Appointment.status == AppointmentStatus.booked,
            Appointment.starts_at >= now,
            Appointment.starts_at <= window_end,
        )
    ).all()
    count = 0
    for appt in appointments:
        create_notification(
            db,
            user_id=appt.patient.user_id,
            ntype=NotificationType.appointment_reminder,
            title=NOTIFICATION_TITLE_REMINDER,
            message=f"Приём {format_dt_ru(appt.starts_at)} у врача {appt.doctor.full_name}",
            appointment_id=appt.id,
        )
        count += 1
    db.commit()
    return MessageResponse(message=f"Reminders sent: {count}")
