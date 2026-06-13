import { APPOINTMENT_STATUS_LABELS } from "../../constants";

interface StatusBadgeProps {
  status: string;
  className?: string;
}

export function StatusBadge({ status, className = "" }: StatusBadgeProps) {
  return (
    <span className={`badge ${status} ${className}`.trim()}>
      {APPOINTMENT_STATUS_LABELS[status] ?? status}
    </span>
  );
}
