import { LOCALE_RU, MS_PER_DAY } from "../constants";

export function toDatetimeLocal(d: Date): string {
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

export function formatDateTime(value: Date | string): string {
  return new Date(value).toLocaleString(LOCALE_RU);
}

const ISO_DATETIME_RE =
  /\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?/g;

/** Подставляет читаемые даты в текст уведомлений (старые записи с ISO). */
export function formatNotificationMessage(text: string): string {
  return text.replace(ISO_DATETIME_RE, (iso) => formatDateTime(iso));
}

export function todayIsoDate(): string {
  return new Date().toISOString().slice(0, 10);
}

export function addDaysIso(from: Date, days: number): string {
  return new Date(from.getTime() + days * MS_PER_DAY).toISOString().slice(0, 10);
}
