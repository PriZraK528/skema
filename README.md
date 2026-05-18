# SKEMA — сервис управления онлайн-записями пациентов

Fullstack CRUD-приложение: **Python (FastAPI)** + **PostgreSQL** + **React (Vite/TypeScript)**.  
Реализованы регистрация/авторизация (JWT), ролевая модель, расписание врачей, онлайн-запись, уведомления, REST API с JSON, фильтрация и поиск.

## Функциональность

| Модуль | Возможности |
|--------|-------------|
| **Пользователи** | Регистрация, вход, refresh-токен, профиль, роли: `admin`, `doctor`, `patient`, `registrar` |
| **Расписание** | Врач вручную создаёт окна приёма; без этого записаться нельзя (`POST /api/doctors/{id}/schedule/slots`) |
| **Записи** | Запись, отмена, перенос, история, назначение врачом (`POST /api/appointments/assign`) |
| **Уведомления** | О записи, переносе, отмене, изменении расписания; напоминания (`POST /api/notifications/reminders/run`) |
| **API** | OpenAPI `/docs`, JSON, пагинация, query-фильтры (`q`, `status`, `from`, `to`) |

## Структура проекта

```
skema/
├── backend/                    # FastAPI
│   ├── app/
│   │   ├── main.py             # точка входа, роутеры
│   │   ├── models.py           # SQLAlchemy-модели
│   │   ├── security.py         # JWT, bcrypt
│   │   ├── deps.py             # авторизация, RBAC
│   │   ├── seed.py             # тестовые данные
│   │   ├── routers/            # REST endpoints
│   │   ├── schemas/            # Pydantic DTO
│   │   └── services/           # бизнес-логика
│   ├── alembic/                # миграции БД
│   ├── tests/                  # pytest, hypothesis, schemathesis
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/                   # React SPA
│   ├── src/App.tsx
│   ├── src/api.ts
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Запуск (Docker)

1. Запустите **Docker Desktop**.
2. В корне проекта:

```bash
docker compose up --build
```

- API: http://localhost:8000 (Swagger: http://localhost:8000/docs)
- UI: http://localhost:5173

### Тестовые учётные записи (пароль для всех: `Password123!`)

| Email | Роль |
|-------|------|
| admin@clinic.example | admin |
| doctor@clinic.example | doctor |
| registrar@clinic.example | registrar |
| patient@clinic.example | patient |

## Локальная разработка

**Backend:**

```bash
cd backend
pip install -e ".[dev]"
# PostgreSQL на localhost:5432 (см. docker-compose)
alembic upgrade head
python -c "from app.seed import run_seed; run_seed()"
uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

Переменные окружения (12-factor): `DATABASE_URL`, `JWT_SECRET_KEY`, `CORS_ORIGINS`, `SEED_ON_STARTUP`.

## Тестирование

```bash
cd backend
pytest -q                          # unit + роли + hypothesis
pytest tests/test_schemathesis.py  # OpenAPI fuzzing (медленнее)
```

- Валидация ролей: отклонение `admin` при саморегистрации, неверных строк роли.
- Фаззинг: Hypothesis (схемы) + Schemathesis (HTTP по OpenAPI).

## Основные API (префикс `/api`)

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/auth/register`, `/auth/login` | Регистрация / вход |
| GET/PATCH | `/auth/me` | Профиль |
| GET | `/doctors` | Список врачей (поиск `q`) |
| GET/POST | `/doctors/{id}/schedule/slots` | Окна приёма (создаёт врач) |
| DELETE | `/schedule/slots/{id}` | Удалить свободное окно |
| GET | `/doctors/{id}/slots/free?from=&to=` | Свободные (созданные и не занятые) |
| GET/POST | `/appointments` | Записи, фильтры |
| POST | `/appointments/assign` | Назначение врачом |
| POST | `/appointments/{id}/cancel`, `.../reschedule` | Отмена / перенос |
| GET | `/notifications` | Уведомления |
