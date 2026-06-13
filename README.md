# SKEMA — сервис управления онлайн-записями пациентов

Fullstack CRUD: **FastAPI** + **PostgreSQL** + **React (Vite/TypeScript)**.  
JWT, роли, ручное расписание врача, онлайн-запись, уведомления, REST API с фильтрацией и поиском.

## Функциональность

| Модуль | Возможности |
|--------|-------------|
| **Пользователи** | Регистрация, вход, refresh-токен, профиль; роли: `admin`, `doctor`, `patient` |
| **Расписание** | Врач создаёт окна приёма вручную; админ выбирает врача (ФИО + специальность) и управляет его окнами |
| **Записи** | Запись пациентом, отмена, назначение врачом/админом по ФИО пациента (`POST /api/appointments/assign`) |
| **Уведомления** | О записи, отмене, изменении расписания; счётчик непрочитанных в меню; cron-напоминания (`POST /api/notifications/reminders/run`) |
| **API** | OpenAPI `/docs`, JSON, пагинация, фильтры (`q`, `status`, `from`, `to`) |

### Роли

| Роль | Доступ |
|------|--------|
| `patient` | Запись к врачу, свои записи, профиль, уведомления |
| `doctor` | Своё расписание, назначение записей по ФИО пациента, просмотр своих приёмов |
| `admin` | Расписание любого врача, назначение записей, список пользователей |

## Структура проекта

```
skema/
├── docker-compose.yml          # db + backend + frontend
├── backend/
│   ├── entrypoint.sh           # миграции, seed, запуск API (Docker)
│   ├── app/
│   │   ├── constants.py        # специальности, seed, ошибки, лимиты
│   │   ├── main.py
│   │   ├── models.py           # ORM-модели (users, doctors, patients, appointments…)
│   │   ├── db.py               # подключение к PostgreSQL
│   │   ├── security.py, deps.py, seed.py
│   │   ├── routers/            # auth, users, doctors, patients, schedule, appointments, notifications
│   │   ├── schemas/
│   │   └── services/
│   ├── alembic/                # миграции БД
│   ├── tests/
│   ├── Dockerfile
│   └── pyproject.toml
└── frontend/
    ├── src/
    │   ├── App.tsx             # маршрутизация вкладок и auth
    │   ├── api.ts
    │   ├── constants.ts        # лимиты, подписи ролей, перевод ошибок
    │   ├── utils/              # roles.ts, datetime.ts
    │   ├── styles.css
    │   └── components/
    │       ├── auth/AuthScreen.tsx
    │       ├── appointments/AppointmentsPanel.tsx
    │       ├── schedule/SchedulePanel.tsx
    │       ├── notifications/NotificationsPanel.tsx
    │       ├── profile/ProfilePanel.tsx
    │       ├── users/UsersPanel.tsx
    │       ├── layout/AppLayout.tsx, Sidebar.tsx
    │       └── ui/StatusBadge.tsx, RoleBadge.tsx
    ├── Dockerfile
    └── package.json
```

## Запуск (Docker)

1. Запустите **Docker Desktop**.
2. В корне проекта:

```bash
docker compose up --build
```

### Демо-аккаунты (пароль: `Password123!`)

| Email | Роль |
|-------|------|
| admin@clinic.example | admin |
| doctor@clinic.example | doctor |
| patient@clinic.example | patient |

## Тестирование

```bash
cd backend
pip install -e ".[dev]"
pytest -q
pytest tests/test_schemathesis.py -q   # OpenAPI fuzzing, дольше
```

## Основные API (префикс `/api`)

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/auth/register`, `/auth/login` | Регистрация / вход |
| GET | `/auth/specializations` | Список специальностей для регистрации врача |
| GET/PATCH | `/auth/me` | Профиль |
| GET | `/users` | Список пользователей (admin) |
| GET | `/doctors` | Список врачей (`q`) |
| GET | `/patients` | Список пациентов для назначения |
| GET/POST | `/doctors/{id}/schedule/slots` | Окна приёма |
| DELETE | `/schedule/slots/{id}` | Удалить свободное окно |
| GET | `/doctors/{id}/slots/free?from=&to=` | Свободные слоты |
| GET/POST | `/appointments` | Записи |
| POST | `/appointments/assign` | Назначение по `patient_name` |
| POST | `/appointments/{id}/cancel` | Отмена |
| GET | `/notifications` | Уведомления |
| GET | `/notifications/unread-count` | Число непрочитанных |
