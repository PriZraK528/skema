import type { UserRole } from "../../api";

interface RoleBadgeProps {
  role: UserRole | string;
}

const LABELS: Record<UserRole, string> = {
  admin: "Администратор",
  doctor: "Врач",
  patient: "Пациент",
  registrar: "Регистратор",
};

export function RoleBadge({ role }: RoleBadgeProps) {
  return <span className="badge">{LABELS[role as UserRole] ?? role}</span>;
}
