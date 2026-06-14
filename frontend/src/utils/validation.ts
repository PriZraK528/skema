import {
  MAX_FULL_NAME_LENGTH,
  MAX_NOTE_LENGTH,
  MAX_PASSWORD_LENGTH,
  MAX_SLOT_DURATION_MINUTES,
  MIN_FULL_NAME_LENGTH,
  MIN_PASSWORD_LENGTH,
  MIN_SLOT_DURATION_MINUTES,
  OTHER_SPECIALIZATION,
  PHONE_ERROR_RU,
} from "../constants";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function normalizePhone(phone: string): string | null {
  const digits = phone.replace(/\D/g, "");

  let normalized = digits;
  if (digits.length === 11 && digits.startsWith("8")) {
    normalized = `7${digits.slice(1)}`;
  } else if (digits.length === 10) {
    normalized = `7${digits}`;
  } else if (digits.length === 11 && digits.startsWith("7")) {
    normalized = digits;
  } else {
    return null;
  }

  if (normalized.length !== 11 || !normalized.startsWith("7")) {
    return null;
  }

  return `+${normalized}`;
}

export function firstError(...checks: Array<string | null | undefined>): string | null {
  for (const check of checks) {
    if (check) return check;
  }
  return null;
}

function normalizeText(value: string): string {
  return value.trim().replace(/\s+/g, " ");
}

export function validateEmail(email: string): string | null {
  const value = email.trim();
  if (!value) return "Email: обязательное поле";
  if (!EMAIL_RE.test(value)) return "Некорректный email";
  return null;
}

export function validatePassword(password: string): string | null {
  if (!password) return "Пароль: обязательное поле";
  if (password.length < MIN_PASSWORD_LENGTH) {
    return `Пароль: минимум ${MIN_PASSWORD_LENGTH} символов`;
  }
  if (password.length > MAX_PASSWORD_LENGTH) {
    return `Пароль: максимум ${MAX_PASSWORD_LENGTH} символов`;
  }
  return null;
}

export function validateFullName(name: string): string | null {
  const value = normalizeText(name);
  if (value.length < MIN_FULL_NAME_LENGTH) {
    return `ФИО: минимум ${MIN_FULL_NAME_LENGTH} символа`;
  }
  if (value.length > MAX_FULL_NAME_LENGTH) {
    return `ФИО: максимум ${MAX_FULL_NAME_LENGTH} символов`;
  }
  return null;
}

export function validatePatientName(name: string): string | null {
  const value = normalizeText(name);
  if (value.length < MIN_FULL_NAME_LENGTH) {
    return `ФИО пациента: минимум ${MIN_FULL_NAME_LENGTH} символа`;
  }
  if (value.length > MAX_FULL_NAME_LENGTH) {
    return `ФИО пациента: максимум ${MAX_FULL_NAME_LENGTH} символов`;
  }
  return null;
}

export function validatePhone(phone: string): string | null {
  if (!phone.trim()) return "Телефон: обязательное поле";
  if (!normalizePhone(phone)) return PHONE_ERROR_RU;
  return null;
}

export function validateSpecialization(
  specialization: string,
  customSpecialization: string,
): string | null {
  if (!specialization) return "Укажите специальность";
  if (specialization === OTHER_SPECIALIZATION) {
    const value = normalizeText(customSpecialization);
    if (value.length < 2) return "Специальность: минимум 2 символа";
    if (value.length > 200) return "Специальность: максимум 200 символов";
  }
  return null;
}

export function validateClinicKey(clinicKey: string): string | null {
  if (!clinicKey.trim()) return "Укажите ключ клиники";
  return null;
}

export function validateNote(note: string): string | null {
  const value = note.trim();
  if (value.length > MAX_NOTE_LENGTH) {
    return `Комментарий: максимум ${MAX_NOTE_LENGTH} символов`;
  }
  return null;
}

export function validateSlotDuration(duration: number): string | null {
  if (!Number.isFinite(duration)) return "Длительность: укажите целое число";
  if (duration < MIN_SLOT_DURATION_MINUTES || duration > MAX_SLOT_DURATION_MINUTES) {
    return `Длительность: от ${MIN_SLOT_DURATION_MINUTES} до ${MAX_SLOT_DURATION_MINUTES} минут`;
  }
  return null;
}

export function validateSlotStart(startsAt: string): string | null {
  if (!startsAt) return "Начало приёма: обязательное поле";
  const start = new Date(startsAt);
  if (Number.isNaN(start.getTime())) return "Начало приёма: некорректная дата и время";
  if (start.getTime() <= Date.now()) return "Нельзя создать окно в прошлом";
  return null;
}

export function validateAppointmentSlot(slot: string): string | null {
  if (!slot) return "Выберите время приёма";
  return null;
}

export function validateRegisterForm(form: {
  email: string;
  password: string;
  fullName: string;
  phone: string;
  role: string;
  specialization: string;
  customSpecialization: string;
  clinicKey: string;
}): string | null {
  return firstError(
    validateEmail(form.email),
    validatePassword(form.password),
    validateFullName(form.fullName),
    validatePhone(form.phone),
    form.role === "doctor"
      ? validateSpecialization(form.specialization, form.customSpecialization)
      : null,
    form.role === "doctor" ? validateClinicKey(form.clinicKey) : null,
  );
}

export function validateProfileForm(form: {
  fullName: string;
  phone: string;
  password?: string;
  isDoctor: boolean;
  specialization: string;
  customSpecialization: string;
}): string | null {
  return firstError(
    validateFullName(form.fullName),
    validatePhone(form.phone),
    form.password ? validatePassword(form.password) : null,
    form.isDoctor
      ? validateSpecialization(form.specialization, form.customSpecialization)
      : null,
  );
}

export function validateBookForm(form: {
  slot: string;
  note: string;
  patientName?: string;
  staffView: boolean;
}): string | null {
  return firstError(
    validateAppointmentSlot(form.slot),
    validateNote(form.note),
    form.staffView ? validatePatientName(form.patientName ?? "") : null,
  );
}
