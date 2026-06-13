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
    if (!user) return;
    refreshUnreadCount();
    const id = window.setInterval(refreshUnreadCount, UNREAD_POLL_INTERVAL_MS);
    return () => window.clearInterval(id);
  }, [user, refreshUnreadCount]);

  const onAuth = (u: User, access: string, refresh: string) => {
    localStorage.setItem("user", JSON.stringify(u));
    localStorage.setItem("access_token", access);
    localStorage.setItem("refresh_token", refresh);
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

  return (
    <AppLayout
      user={user}
      tab={tab}
      unreadCount={unreadCount}
      onTabChange={setTab}
      onLogout={logout}
    >
      {tab === "appointments" && <AppointmentsPanel user={user} />}
      {tab === "schedule" && canSchedule && <SchedulePanel user={user} />}
      {tab === "notifications" && (
        <NotificationsPanel onUnreadChange={refreshUnreadCount} />
      )}
      {tab === "profile" && (
        <ProfilePanel
          user={user}
          onUpdate={(u) => {
            setUser(u);
            localStorage.setItem("user", JSON.stringify(u));
          }}
        />
      )}
      {tab === "users" && canUsers && <UsersPanel />}
    </AppLayout>
  );
}
