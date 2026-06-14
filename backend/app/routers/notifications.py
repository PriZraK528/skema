from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.constants import DEFAULT_NOTIFICATIONS_LIMIT, ErrorDetail, MAX_PAGE_LIMIT
from app.db import get_db
from app.deps import get_current_user
from app.models import Notification, User
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.notification import NotificationMarkRead, NotificationOut

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
    limit: int = Query(default=DEFAULT_NOTIFICATIONS_LIMIT, ge=1, le=MAX_PAGE_LIMIT),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    stmt = select(Notification).where(Notification.user_id == user.id)
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
