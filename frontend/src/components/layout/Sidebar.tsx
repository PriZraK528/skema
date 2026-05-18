import type { User } from "../../api";

export type Tab = "appointments" | "schedule" | "notifications" | "profile" | "users";

interface SidebarProps {
  tab: Tab;
  user: User;
  onTabChange: (tab: Tab) => void;
  onLogout: () => void;
}

export function Sidebar({ tab, user, onTabChange, onLogout }: SidebarProps) {
  const canSchedule =
    user.role === "doctor" || user.role === "admin" || user.role === "registrar";
  const canUsers = user.role === "admin" || user.role === "registrar";

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h1 className="brand">SKEMA</h1>
        <p className="brand-sub">Онлайн-запись</p>
      </div>
      <nav className="sidebar-nav">
        <button
          type="button"
          className={`nav-btn ${tab === "appointments" ? "active" : ""}`}
          onClick={() => onTabChange("appointments")}
        >
          Записи
        </button>
        {canSchedule && (
          <button
            type="button"
            className={`nav-btn ${tab === "schedule" ? "active" : ""}`}
            onClick={() => onTabChange("schedule")}
          >
            Расписание
          </button>
        )}
        <button
          type="button"
          className={`nav-btn ${tab === "notifications" ? "active" : ""}`}
          onClick={() => onTabChange("notifications")}
        >
          Уведомления
        </button>
        <button
          type="button"
          className={`nav-btn ${tab === "profile" ? "active" : ""}`}
          onClick={() => onTabChange("profile")}
        >
          Профиль
        </button>
        {canUsers && (
          <button
            type="button"
            className={`nav-btn ${tab === "users" ? "active" : ""}`}
            onClick={() => onTabChange("users")}
          >
            Пользователи
          </button>
        )}
      </nav>
      <div className="sidebar-footer">
        <button type="button" className="nav-btn nav-btn-logout" onClick={onLogout}>
          Выход
        </button>
      </div>
    </aside>
  );
}

