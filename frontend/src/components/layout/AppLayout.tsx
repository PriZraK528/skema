import type { ReactNode } from "react";
import type { User } from "../../api";
import { Sidebar, type Tab } from "./Sidebar";

interface AppLayoutProps {
  user: User;
  tab: Tab;
  unreadCount: number;
  onTabChange: (tab: Tab) => void;
  children: ReactNode;
}

export function AppLayout({
  user,
  tab,
  unreadCount,
  onTabChange,
  children,
}: AppLayoutProps) {
  return (
    <div className="layout">
      <Sidebar
        tab={tab}
        user={user}
        unreadCount={unreadCount}
        onTabChange={onTabChange}
      />
      <main className="main">{children}</main>
    </div>
  );
}
