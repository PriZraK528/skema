"""Shared application constants."""

from enum import Enum

# --- Domain lists ---

DOCTOR_SPECIALIZATIONS: tuple[str, ...] = (
    "Терапевт",
    "Кардиолог",
    "Невролог",
    "Хирург",
    "Педиатр",
    "Стоматолог",
    "Офтальмолог",
    "ЛОР",
    "Гинеколог",
    "Уролог",
    "Дерматолог",
    "Психиатр",
    "Эндокринолог",
)

# --- Seed / demo ---

SEED_PASSWORD = "Password123!"
SEED_ADMIN_EMAIL = "admin@clinic.example"
SEED_DOCTOR_EMAIL = "doctor@clinic.example"
SEED_PATIENT_EMAIL = "patient@clinic.example"
SEED_DOCTOR_SPECIALIZATION = DOCTOR_SPECIALIZATIONS[0]

# --- Pagination ---

DEFAULT_PAGE_LIMIT = 50
MAX_PAGE_LIMIT = 100
DEFAULT_NOTIFICATIONS_LIMIT = 50

# --- Auth / JWT ---

JWT_ALGORITHM = "HS256"
TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"
MIN_PASSWORD_LENGTH = 8
MIN_FULL_NAME_LENGTH = 2
MAX_FULL_NAME_LENGTH = 200
PHONE_INPUT_MIN_LENGTH = 10
PHONE_INPUT_MAX_LENGTH = 18
PHONE_ERROR = "Телефон: укажите номер в формате +7XXXXXXXXXX"
MAX_PASSWORD_LENGTH = 128
MIN_SPECIALIZATION_LENGTH = 2
MAX_SPECIALIZATION_LENGTH = 200
MAX_NOTE_LENGTH = 500

# --- Schedule / slots ---

DEFAULT_SLOT_DURATION_MINUTES = 30
MIN_SLOT_DURATION_MINUTES = 5
MAX_SLOT_DURATION_MINUTES = 480
FREE_SLOTS_DEFAULT_RANGE_DAYS = 60
REMINDER_WINDOW_HOURS = 24
APPOINTMENT_COMPLETE_INTERVAL_SECONDS = 60

# --- Notification titles (Russian) ---

NOTIFICATION_TITLE_BOOKED = "Запись подтверждена"
NOTIFICATION_TITLE_NEW_APPOINTMENT = "Новая запись"
NOTIFICATION_TITLE_CANCELLED = "Запись отменена"
NOTIFICATION_TITLE_REMINDER = "Напоминание о приёме"
NOTIFICATION_TITLE_SCHEDULE_CHANGED = "Изменение расписания"


class ErrorDetail(str, Enum):
    """API error detail strings (keys for frontend API_ERRORS)."""

    NOT_AUTHENTICATED = "Not authenticated"
    INVALID_TOKEN = "Invalid token"
    INVALID_TOKEN_TYPE = "Invalid token type"
    USER_NOT_FOUND = "User not found"
    INSUFFICIENT_PERMISSIONS = "Insufficient permissions"
    EMAIL_ALREADY_REGISTERED = "Email already registered"
    INVALID_CLINIC_KEY = "Invalid clinic registration key"
    INVALID_CREDENTIALS = "Invalid credentials"
    INVALID_REFRESH_TOKEN = "Invalid refresh token"
    DOCTOR_NOT_FOUND = "Doctor not found"
    PATIENT_NOT_FOUND = "Patient not found"
    APPOINTMENT_NOT_FOUND = "Appointment not found"
    SLOT_NOT_AVAILABLE = "Selected time slot is not available"
    PATIENT_PROFILE_MISSING = "Patient profile missing"
    CANNOT_BOOK_FOR_OTHER = "Cannot book for another patient"
    PATIENT_NAME_REQUIRED = "patient_name is required"
    MULTIPLE_PATIENTS_MATCH = "Multiple patients match this name"
    DOCTOR_OWN_SCHEDULE_ONLY = "Doctor can only use own schedule when assigning"
    ONLY_BOOKED_CAN_CANCEL = "Only booked appointments can be cancelled"
    ACCESS_DENIED = "Access denied"
    DOCTOR_ID_REQUIRED = "doctor_id required"
    CANNOT_MODIFY_SCHEDULE = "Cannot modify this schedule"
    SLOT_NOT_FOUND = "Slot not found"
    ENDS_BEFORE_STARTS = "ends_at must be after starts_at"
    SLOT_IN_PAST = "Cannot create slots in the past"
    SLOT_ALREADY_EXISTS = "Slot at this time already exists"
    SLOT_OVERLAPS = "Overlaps with another availability slot"
    SLOT_HAS_APPOINTMENT = "Cannot delete slot with an active appointment"
    DATE_RANGE_INVALID = "'to' must be >= 'from'"
    NOTIFICATION_NOT_FOUND = "Notification not found"
