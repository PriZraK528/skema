import { LOCALE_RU, MS_PER_DAY } from "../constants";

export function toDatetimeLocal(d: Date): string {
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

export function formatDateTime(value: Date | string): string {
  return new Date(value).toLocaleString(LOCALE_RU);
}

export function todayIsoDate(): string {
  return new Date().toISOString().slice(0, 10);
}

export function addDaysIso(from: Date, days: number): string {
  return new Date(from.getTime() + days * MS_PER_DAY).toISOString().slice(0, 10);
}
