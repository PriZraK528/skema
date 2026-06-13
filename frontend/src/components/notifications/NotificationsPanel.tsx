import { useEffect, useState } from "react";
import { api, Notification } from "../../api";
import { formatDateTime } from "../../utils/datetime";

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

  return (
    <div className="card">
      <h2>Уведомления</h2>
      <p className="muted">Записи, напоминания, изменения расписания</p>
      <ul className="notification-list">
        {items.length === 0 && <li className="muted">Нет уведомлений</li>}
        {items.map((n) => (
          <li key={n.id} className={n.is_read ? "notification-read" : ""}>
            <strong>{n.title}</strong>
            <br />
            <span className="muted">{n.message}</span>
            <br />
            <span className="muted notification-time">
              {formatDateTime(n.created_at)}
            </span>
            <br />
            {!n.is_read && (
              <button type="button" className="ghost" onClick={() => markRead(n.id)}>
                Прочитано
              </button>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
