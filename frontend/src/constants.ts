export const API_BASE_DEFAULT = "http://localhost:8000";

export const DEFAULT_LIST_LIMIT = 50;
export const UNREAD_POLL_INTERVAL_MS = 10_000;
export const SLOT_LOOKAHEAD_DAYS = 14;
export const MS_PER_DAY = 86_400_000;
export const DEFAULT_SLOT_DURATION_MINUTES = 30;
export const MIN_SLOT_DURATION_MINUTES = 5;
export const MAX_SLOT_DURATION_MINUTES = 480;
export const LOCALE_RU = "ru-RU";
export const OTHER_SPECIALIZATION = "__other__";
export const NAV_BADGE_MAX = 99;
export const GENERIC_ERROR_RU = "Произошла ошибка";

export const MIN_PASSWORD_LENGTH = 8;
export const MAX_PASSWORD_LENGTH = 128;
export const MIN_FULL_NAME_LENGTH = 2;
export const MAX_FULL_NAME_LENGTH = 200;
export const MAX_NOTE_LENGTH = 500;
export const PHONE_ERROR_RU = "Телефон: укажите номер в формате +7XXXXXXXXXX";

export const SEED_ADMIN_EMAIL = "admin@clinic.example";
export const SEED_DOCTOR_EMAIL = "doctor@clinic.example";
export const SEED_PATIENT_EMAIL = "patient@clinic.example";
export const SEED_PASSWORD = "Password123!";

export type UserRole = "admin" | "doctor" | "patient";

export const ROLE_LABELS: Record<UserRole, string> = {
  admin: "Администратор",
  doctor: "Врач",
  patient: "Пациент",
};

export const APPOINTMENT_STATUS_LABELS: Record<string, string> = {
  booked: "Записан",
  cancelled: "Отменён",
  completed: "Завершён",
};

export const API_ERRORS: Record<string, string> = {
  "Not authenticated": "Требуется авторизация",
  "Invalid token": "Недействительный токен",
  "Invalid token type": "Недействительный тип токена",
  "User not found": "Пользователь не найден",
  "Insufficient permissions": "Недостаточно прав",
  "Doctor not found": "Врач не найден",
  "Patient not found": "Пациент не найден",
  "Appointment not found": "Запись не найдена",
  "Selected time slot is not available": "Выбранное время недоступно для записи",
  "Cannot create slots in the past": "Нельзя создать окно в прошлом",
  "Slot at this time already exists": "Окно на это время уже существует",
  "Overlaps with another availability slot": "Пересечение с другим окном",
  "Cannot delete slot with an active appointment": "Нельзя удалить окно с активной записью",
  "Email already registered": "Email уже зарегистрирован",
  "Invalid credentials": "Неверный email или пароль",
  "Invalid refresh token": "Недействительный refresh-токен",
  "Invalid clinic registration key": "Неверный ключ регистрации клиники",
  "Access denied": "Доступ запрещён",
  "Multiple patients match this name": "Найдено несколько пациентов с таким именем",
  "patient_name is required": "Укажите ФИО пациента",
  "Patient profile missing": "Профиль пациента не найден",
  "Cannot book for another patient": "Нельзя записать другого пациента",
  "Doctor can only use own schedule when assigning": "Врач может назначать только в своём расписании",
  "Only booked appointments can be cancelled": "Отменить можно только активную запись",
  "doctor_id required": "Укажите врача",
  "Cannot modify this schedule": "Нет прав на изменение расписания",
  "Slot not found": "Окно не найдено",
  "Notification not found": "Уведомление не найдено",
  "ends_at must be after starts_at": "Конец приёма должен быть позже начала",
  "'to' must be >= 'from'": "Дата «до» должна быть не раньше «от»",
};
