import type { User } from "../../api";
import { NAV_BADGE_MAX } from "../../constants";
import { canManageSchedule, isAdmin } from "../../utils/roles";

export type Tab = "appointments" | "schedule" | "notifications" | "profile" | "users";

interface SidebarProps {
  tab: Tab;
  user: User;
  unreadCount: number;
  onTabChange: (tab: Tab) => void;
}

export function Sidebar({ tab, user, unreadCount, onTabChange }: SidebarProps) {
  const canSchedule = canManageSchedule(user);
  const canUsers = isAdmin(user);
  const showNotifications = !isAdmin(user);

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
        {showNotifications && (
          <button
            type="button"
            className={`nav-btn ${tab === "notifications" ? "active" : ""}`}
            onClick={() => onTabChange("notifications")}
          >
            <span className="nav-btn-label">
              Уведомления
              {unreadCount > 0 && (
                <span className="nav-badge">
                  {unreadCount > NAV_BADGE_MAX ? `${NAV_BADGE_MAX}+` : unreadCount}
                </span>
              )}
            </span>
          </button>
        )}
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
    </aside>
  );
}
