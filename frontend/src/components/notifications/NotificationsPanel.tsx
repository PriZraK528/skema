import { useEffect, useState } from "react";
import { api, Notification } from "../../api";
import { formatDateTime, formatNotificationMessage } from "../../utils/datetime";

interface NotificationsPanelProps {
  onUnreadChange?: () => void;
}

export function NotificationsPanel({ onUnreadChange }: NotificationsPanelProps) {
  const [items, setItems] = useState<Notification[]>([]);

  const load = () =>
    api.notifications().then((r) => {
      setItems(r.items);
      onUnreadChange?.();
    });

  useEffect(() => {
    load().catch(console.error);
  }, []);

  const markRead = (id: number) => {
    api.markNotification(id).then(load).catch(console.error);
  };

  const markAllRead = () => {
    api.markAllNotificationsRead().then(load).catch(console.error);
  };

  const hasUnread = items.some((item) => !item.is_read);

  return (
    <div className="card">
      <div className="panel-header">
        <div>
          <h2>Уведомления</h2>
          <p className="muted">Записи, напоминания, изменения расписания</p>
        </div>
        {hasUnread && (
          <button type="button" className="ghost" onClick={markAllRead}>
            Прочитать все
          </button>
        )}
      </div>
      <div className="notification-list">
        {items.length === 0 && <p className="muted">Нет уведомлений</p>}
        {items.map((n) => (
          <article
            key={n.id}
            className={`notification-card ${n.is_read ? "notification-read" : "notification-unread"}`}
          >
            <div className="notification-card-header">
              <strong>{n.title}</strong>
              <time className="notification-time">{formatDateTime(n.created_at)}</time>
            </div>
            <p className="notification-message">
              {formatNotificationMessage(n.message)}
            </p>
            {!n.is_read && (
              <button type="button" className="ghost" onClick={() => markRead(n.id)}>
                Прочитано
              </button>
            )}
          </article>
        ))}
      </div>
    </div>
  );
}
