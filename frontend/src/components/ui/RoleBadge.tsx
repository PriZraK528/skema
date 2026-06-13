import { ROLE_LABELS } from "../../constants";
import type { UserRole } from "../../api";

interface RoleBadgeProps {
  role: UserRole | string;
}

export function RoleBadge({ role }: RoleBadgeProps) {
  return <span className="badge">{ROLE_LABELS[role as UserRole] ?? role}</span>;
}
