interface StatusBadgeProps {
  status: string;
  className?: string;
}

const LABELS: Record<string, string> = {
  booked: "Записан",
  cancelled: "Отменён",
  completed: "Завершён",
};

export function StatusBadge({ status, className = "" }: StatusBadgeProps) {
  return (
    <span className={`badge ${status} ${className}`.trim()}>
      {LABELS[status] ?? status}
    </span>
  );
}
