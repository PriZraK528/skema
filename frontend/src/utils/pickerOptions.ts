import type { Doctor, FreeSlot } from "../api";
import { OTHER_SPECIALIZATION, ROLE_LABELS, type UserRole } from "../constants";
import { formatDateTime } from "./datetime";

export function roleOptions(): { value: string; label: string }[] {
  return (["patient", "doctor"] as UserRole[]).map((role) => ({
    value: role,
    label: ROLE_LABELS[role],
  }));
}

export function specializationOptions(items: string[]): { value: string; label: string }[] {
  return [
    ...items.map((item) => ({ value: item, label: item })),
    { value: OTHER_SPECIALIZATION, label: "Другое" },
  ];
}

export function doctorOptions(doctors: Doctor[]): { value: string; label: string }[] {
  return doctors.map((doctor) => ({
    value: String(doctor.id),
    label: `${doctor.full_name} — ${doctor.specialization}`,
  }));
}

export function slotOptions(slots: FreeSlot[]): { value: string; label: string }[] {
  return slots.map((slot) => ({
    value: slot.starts_at,
    label: formatDateTime(slot.starts_at),
  }));
}

export function patientOptions(names: string[]): { value: string; label: string }[] {
  return names.map((name) => ({ value: name, label: name }));
}
