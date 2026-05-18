import type { ReactNode } from "react";
import type { User } from "../../api";
import { Sidebar, type Tab } from "./Sidebar";

interface AppLayoutProps {
  user: User;
  tab: Tab;
  onTabChange: (tab: Tab) => void;
  onLogout: () => void;
  children: ReactNode;
}

export function AppLayout({ user, tab, onTabChange, onLogout, children }: AppLayoutProps) {
  return (
    <div className="layout">
      <Sidebar tab={tab} user={user} onTabChange={onTabChange} onLogout={onLogout} />
      <main className="main">{children}</main>
    </div>
  );
}
