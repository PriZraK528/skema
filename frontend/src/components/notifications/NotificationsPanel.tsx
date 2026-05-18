import { useEffect, useState } from "react";
import { api, Notification } from "../../api";

export function NotificationsPanel() {
  const [items, setItems] = useState<Notification[]>([]);

  const load = () => api.notifications().then((r) => setItems(r.items));

  useEffect(() => {
    load().catch(console.error);
  }, []);

  return (
    <div className="card">
      <h2>Уведомления</h2>
      <p className="muted">Записи, напоминания, изменения расписания</p>
      <ul className="notification-list">
        {items.map((n) => (
          <li key={n.id} className={n.is_read ? "notification-read" : ""}>
            <strong>{n.title}</strong>
            <br />
            <span className="muted">{n.message}</span>
            <br />
            <span className="muted notification-time">
              {new Date(n.created_at).toLocaleString("ru-RU")}
            </span>
            <br />
            {!n.is_read && (
              <button type="button" className="ghost" onClick={() => api.markNotification(n.id).then(load)}>
                Прочитано
              </button>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
