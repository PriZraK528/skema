import { useCallback, useEffect, useState } from "react";
import { api, User } from "./api";
import { AuthScreen } from "./components/auth/AuthScreen";
import { AppointmentsPanel } from "./components/appointments/AppointmentsPanel";
import { SchedulePanel } from "./components/schedule/SchedulePanel";
import { NotificationsPanel } from "./components/notifications/NotificationsPanel";
import { ProfilePanel } from "./components/profile/ProfilePanel";
import { UsersPanel } from "./components/users/UsersPanel";
import { AppLayout } from "./components/layout/AppLayout";
import { UNREAD_POLL_INTERVAL_MS } from "./constants";
import { canManageSchedule, isAdmin } from "./utils/roles";
import type { Tab } from "./components/layout/Sidebar";

export default function App() {
  const [user, setUser] = useState<User | null>(() => {
    const raw = localStorage.getItem("user");
    return raw ? (JSON.parse(raw) as User) : null;
  });
  const [tab, setTab] = useState<Tab>("appointments");
  const [unreadCount, setUnreadCount] = useState(0);

  const refreshUnreadCount = useCallback(() => {
    api
      .unreadNotificationsCount()
      .then((r) => setUnreadCount(r.count))
      .catch(() => setUnreadCount(0));
  }, []);

  useEffect(() => {
    if (!user || isAdmin(user)) return;
    refreshUnreadCount();
    const intervalId = window.setInterval(refreshUnreadCount, UNREAD_POLL_INTERVAL_MS);
    const onFocus = () => refreshUnreadCount();
    window.addEventListener("focus", onFocus);
    document.addEventListener("visibilitychange", onFocus);
    return () => {
      window.clearInterval(intervalId);
      window.removeEventListener("focus", onFocus);
      document.removeEventListener("visibilitychange", onFocus);
    };
  }, [user, refreshUnreadCount]);

  useEffect(() => {
    if (user && isAdmin(user) && tab === "notifications") {
      setTab("appointments");
    }
  }, [user, tab]);

  const onAuth = (u: User, access: string) => {
    localStorage.setItem("user", JSON.stringify(u));
    localStorage.setItem("access_token", access);
    setUser(u);
  };

  const logout = () => {
    localStorage.clear();
    setUser(null);
    setUnreadCount(0);
  };

  if (!user) return <AuthScreen onAuth={onAuth} />;

  const canSchedule = canManageSchedule(user);
  const canUsers = isAdmin(user);
  const showNotifications = !isAdmin(user);

  return (
    <AppLayout user={user} tab={tab} unreadCount={unreadCount} onTabChange={setTab}>
      {tab === "appointments" && (
        <AppointmentsPanel user={user} onActivity={refreshUnreadCount} />
      )}
      {tab === "schedule" && canSchedule && (
        <SchedulePanel user={user} onActivity={refreshUnreadCount} />
      )}
      {tab === "notifications" && showNotifications && (
        <NotificationsPanel onUnreadChange={refreshUnreadCount} />
      )}
      {tab === "profile" && (
        <ProfilePanel
          user={user}
          onUpdate={(u) => {
            setUser(u);
            localStorage.setItem("user", JSON.stringify(u));
          }}
          onLogout={logout}
        />
      )}
      {tab === "users" && canUsers && <UsersPanel />}
    </AppLayout>
  );
}
