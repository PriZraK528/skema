import type { User } from "../api";

export function isStaff(user: User): boolean {
  return user.role === "doctor" || user.role === "admin";
}

export function isAdmin(user: User): boolean {
  return user.role === "admin";
}

export function canManageSchedule(user: User): boolean {
  return isStaff(user);
}
