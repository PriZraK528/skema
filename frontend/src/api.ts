import {
  API_BASE_DEFAULT,
  API_ERRORS,
  DEFAULT_LIST_LIMIT,
  GENERIC_ERROR_RU,
  type UserRole,
} from "./constants";

export type { UserRole };

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? API_BASE_DEFAULT;

function errorMessage(detail: unknown): string {
  if (detail == null) return GENERIC_ERROR_RU;
  if (typeof detail === "string") return API_ERRORS[detail] ?? detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) =>
        typeof item === "object" && item !== null && "msg" in item
          ? API_ERRORS[(item as { msg: string }).msg] ?? (item as { msg: string }).msg
          : errorMessage(item),
      )
      .join("; ");
  }
  return String(detail);
}

export interface User {
  id: number;
  email: string;
  role: UserRole;
  full_name?: string;
  phone?: string;
  specialization?: string;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
}

export interface AuthResponse extends TokenPair {
  user: User;
}

export interface Paginated<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

export interface Doctor {
  id: number;
  user_id: number;
  full_name: string;
  specialization: string;
  email?: string;
}

export interface FreeSlot {
  doctor_id: number;
  starts_at: string;
  ends_at: string;
}

export interface Appointment {
  id: number;
  patient_id: number;
  doctor_id: number;
  starts_at: string;
  ends_at: string;
  status: string;
  note?: string;
  patient_name?: string;
  doctor_name?: string;
  specialization?: string;
}

export interface Notification {
  id: number;
  type: string;
  title: string;
  message: string;
  is_read: boolean;
  appointment_id?: number;
  created_at: string;
}

export interface PatientBrief {
  id: number;
  full_name: string;
  phone: string;
}

export interface AvailabilitySlot {
  id: number;
  doctor_id: number;
  starts_at: string;
  ends_at: string;
  is_active: boolean;
  is_booked: boolean;
}

function authHeaders(): HeadersInit {
  const token = localStorage.getItem("access_token");
  return token
    ? { Authorization: `Bearer ${token}`, "Content-Type": "application/json" }
    : { "Content-Type": "application/json" };
}

function clearSession() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("user");
}

let refreshPromise: Promise<boolean> | null = null;

async function tryRefreshSession(): Promise<boolean> {
  const refreshToken = localStorage.getItem("refresh_token");
  if (!refreshToken) return false;
  if (!refreshPromise) {
    refreshPromise = (async () => {
      try {
        const res = await fetch(`${API_BASE}/api/auth/refresh`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });
        if (!res.ok) return false;
        const data = (await res.json()) as TokenPair;
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("refresh_token", data.refresh_token);
        return true;
      } catch {
        return false;
      } finally {
        refreshPromise = null;
      }
    })();
  }
  return refreshPromise;
}

function isAuthPath(path: string): boolean {
  return (
    path === "/api/auth/login" ||
    path === "/api/auth/register" ||
    path === "/api/auth/refresh"
  );
}

async function request<T>(path: string, init?: RequestInit, retried = false): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { ...authHeaders(), ...init?.headers },
  });
  if (res.status === 401 && !retried && !isAuthPath(path)) {
    const refreshed = await tryRefreshSession();
    if (refreshed) return request<T>(path, init, true);
    clearSession();
    window.location.reload();
  }
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(errorMessage(body.detail) || res.statusText);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export function saveSession(user: User, access: string, refresh: string) {
  localStorage.setItem("user", JSON.stringify(user));
  localStorage.setItem("access_token", access);
  localStorage.setItem("refresh_token", refresh);
}

const listLimit = `limit=${DEFAULT_LIST_LIMIT}`;

export const api = {
  login: (email: string, password: string) =>
    request<AuthResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  register: (data: Record<string, unknown>) =>
    request<AuthResponse>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  specializations: () => request<string[]>("/api/auth/specializations"),
  updateProfile: (data: Record<string, unknown>) =>
    request<User>("/api/auth/me", { method: "PATCH", body: JSON.stringify(data) }),
  doctors: () => request<Paginated<Doctor>>(`/api/doctors?${listLimit}`),
  freeSlots: (doctorId: number, from: string, to?: string) =>
    request<FreeSlot[]>(
      `/api/doctors/${doctorId}/slots/free?from=${from}${to ? `&to=${to}` : ""}`,
    ),
  availabilitySlots: (doctorId: number) =>
    request<AvailabilitySlot[]>(`/api/doctors/${doctorId}/schedule/slots`),
  createAvailabilitySlot: (doctorId: number, data: Record<string, unknown>) =>
    request<AvailabilitySlot>(`/api/doctors/${doctorId}/schedule/slots`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  deleteAvailabilitySlot: (slotId: number) =>
    request<{ message: string }>(`/api/schedule/slots/${slotId}`, { method: "DELETE" }),
  appointments: (params?: string) =>
    request<Paginated<Appointment>>(`/api/appointments?${listLimit}${params ?? ""}`),
  book: (data: Record<string, unknown>) =>
    request<Appointment>("/api/appointments", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  assign: (data: Record<string, unknown>) =>
    request<Appointment>("/api/appointments/assign", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  cancel: (id: number) =>
    request<Appointment>(`/api/appointments/${id}/cancel`, { method: "POST" }),
  unreadNotificationsCount: () =>
    request<{ count: number }>("/api/notifications/unread-count"),
  patients: () => request<PatientBrief[]>(`/api/patients?${listLimit}`),
  notifications: () => request<Paginated<Notification>>(`/api/notifications?${listLimit}`),
  markNotification: (id: number) =>
    request<Notification>(`/api/notifications/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ is_read: true }),
    }),
  markAllNotificationsRead: () =>
    request<{ message: string }>("/api/notifications/read-all", { method: "POST" }),
  users: (q?: string) =>
    request<Paginated<User>>(`/api/users?${listLimit}${q ? `&q=${encodeURIComponent(q)}` : ""}`),
};
