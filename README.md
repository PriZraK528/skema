# SKEMA — сервис управления онлайн-записями пациентов

Fullstack CRUD: **FastAPI** + **PostgreSQL** + **React (Vite/TypeScript)**.  
JWT, роли, ручное расписание врача, онлайн-запись, уведомления, REST API с фильтрацией и поиском.

## Функциональность

| Модуль | Возможности |
|--------|-------------|
| **Пользователи** | Регистрация, вход, refresh-токен, профиль; роли: `admin`, `doctor`, `patient`, `registrar` |
| **Расписание** | Врач создаёт окна приёма вручную (`POST /api/doctors/{id}/schedule/slots`); без окон запись недоступна |
| **Записи** | Запись, отмена, перенос, назначение врачом (`POST /api/appointments/assign`) |
| **Уведомления** | О записи, переносе, отмене; cron-напоминания (`POST /api/notifications/reminders/run`) |
| **API** | OpenAPI `/docs`, JSON, пагинация, фильтры (`q`, `status`, `from`, `to`) |

## Структура проекта

```
skema/
├── docker-compose.yml          # db + backend + frontend
├── backend/
│   ├── entrypoint.sh           # миграции, seed, запуск API (Docker)
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── security.py, deps.py, seed.py
│   │   ├── routers/
│   │   ├── schemas/
│   │   └── services/
│   ├── alembic/
│   ├── tests/
│   ├── Dockerfile
│   └── pyproject.toml
└── frontend/
    ├── src/
    │   ├── App.tsx             # маршрутизация вкладок и auth
    │   ├── api.ts
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
| registrar@clinic.example | registrar |
| patient@clinic.example | patient |

## Тестирование

В контейнере backend или локально с установленными зависимостями:

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
| GET/PATCH | `/auth/me` | Профиль |
| GET | `/doctors` | Список врачей (`q`) |
| GET/POST | `/doctors/{id}/schedule/slots` | Окна приёма |
| DELETE | `/schedule/slots/{id}` | Удалить свободное окно |
| GET | `/doctors/{id}/slots/free?from=&to=` | Свободные слоты |
| GET/POST | `/appointments` | Записи |
| POST | `/appointments/assign` | Назначение врачом |
| POST | `/appointments/{id}/cancel`, `.../reschedule` | Отмена / перенос |
| GET | `/notifications` | Уведомления |
