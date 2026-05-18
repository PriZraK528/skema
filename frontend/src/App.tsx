import { useState } from "react";
import { User } from "./api";
import { AuthScreen } from "./components/auth/AuthScreen";
import { AppointmentsPanel } from "./components/appointments/AppointmentsPanel";
import { SchedulePanel } from "./components/schedule/SchedulePanel";
import { NotificationsPanel } from "./components/notifications/NotificationsPanel";
import { ProfilePanel } from "./components/profile/ProfilePanel";
import { UsersPanel } from "./components/users/UsersPanel";
import { AppLayout } from "./components/layout/AppLayout";
import type { Tab } from "./components/layout/Sidebar";

export default function App() {
  const [user, setUser] = useState<User | null>(() => {
    const raw = localStorage.getItem("user");
    return raw ? (JSON.parse(raw) as User) : null;
  });
  const [tab, setTab] = useState<Tab>("appointments");

  const onAuth = (u: User, access: string, refresh: string) => {
    localStorage.setItem("user", JSON.stringify(u));
    localStorage.setItem("access_token", access);
    localStorage.setItem("refresh_token", refresh);
    setUser(u);
  };

  const logout = () => {
    localStorage.clear();
    setUser(null);
  };

  if (!user) return <AuthScreen onAuth={onAuth} />;

  const canSchedule =
    user.role === "doctor" || user.role === "admin" || user.role === "registrar";
  const canUsers = user.role === "admin" || user.role === "registrar";

  return (
    <AppLayout user={user} tab={tab} onTabChange={setTab} onLogout={logout}>
      {tab === "appointments" && <AppointmentsPanel user={user} />}
      {tab === "schedule" && canSchedule && <SchedulePanel user={user} />}
      {tab === "notifications" && <NotificationsPanel />}
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
