# SKEMA

Клиент–серверное приложение для онлайн-записи пациентов в клинику.

- **Развёрнутый проект:** https://skema-frontend.onrender.com
- **Серверная часть:** FastAPI + SQLAlchemy + Alembic (JWT access/refresh)
- **Клиентская часть:** React (Vite, TypeScript)
- **База данных:** PostgreSQL

Архитектура: трёхуровневая client–server, монолитный backend (routers → services → ORM).

## Структура

| Путь | Содержимое |
|------|------------|
| `backend/` | REST API, миграции Alembic, тесты, `Dockerfile` |
| `backend/app/routers/` | HTTP-эндпоинты |
| `backend/app/services/` | Бизнес-логика |
| `backend/alembic/versions/` | Миграции БД |
| `frontend/` | SPA (Vite), `Dockerfile` (production), `Dockerfile.dev` (локальный Docker) |
| `docker-compose.yml` | Postgres + backend + frontend (режим разработки) |

## Требования

- **Docker:** Docker Desktop + Compose (рекомендуемый способ запуска)
- **Без Docker:** Python 3.9+, Node 18+, PostgreSQL 14+

## Запуск в Docker

Рабочая директория — **корень репозитория**.

### Первый запуск (или после изменений в коде / Dockerfile)

```bash
docker compose up --build
```

При старте backend:

1. `alembic upgrade head` — миграции
2. при `SEED_ON_STARTUP=true` — демо-пользователи (идемпотентно: если в БД уже есть пользователи, сид пропускается)

| Сервис | Адрес |
|--------|--------|
| Frontend | http://localhost:5173 |
| Backend | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |
| Health | http://localhost:8000/health |

### Последующие запуски

```bash
docker compose up
```

Флаг `--build` нужен снова после изменений в коде, зависимостях или Dockerfile.

### Данные между запусками

Том `db_data` **сохраняется**: после `docker compose down` пользователи и записи остаются. Миграции уже применённые повторно не накатываются.

**Сбросить БД «как в первый раз»:**

```bash
docker compose down -v
docker compose up --build
```

## Демо-учётные записи

Создаются при `SEED_ON_STARTUP=true` на **пустой** БД. Пароль для всех: `Password123!`

| Email | Роль | Примечание |
|-------|------|------------|
| `patient@clinic.example` | Пациент | Запись к врачу, свои приёмы |
| `doctor@clinic.example` | Врач | Расписание, назначение записей |
| `admin@clinic.example` | Администратор | Все записи, расписание любого врача, список пользователей |

Ключ регистрации врача (Docker): `clinic-demo-key` — см. `docker-compose.yml`.

## Роли и возможности

**Пациент** — запись на свободное окно, просмотр и отмена своих записей, профиль, уведомления.

**Врач** — создание и удаление своих окон приёма, назначение записей **существующим** пациентам, просмотр своих приёмов.

**Администратор** — расписание любого врача, назначение записей, все записи, список пользователей (без раздела уведомлений).

Записаться можно только на окно из раздела «Расписание». Записи со статусом «Записан» после `ends_at` автоматически переводятся в «Завершён».

## Локальная разработка без Docker

1. Поднять PostgreSQL с БД `clinic` (учётные данные как в `docker-compose.yml` или свои).
2. **Backend:**

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/macOS
pip install -e ".[dev]"
set DATABASE_URL=postgresql+psycopg://clinic:clinic@localhost:5432/clinic   # Windows cmd
# export DATABASE_URL=postgresql+psycopg://clinic:clinic@localhost:5432/clinic
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. **Frontend:**

```bash
cd frontend
npm install
npm run dev
```

UI: http://localhost:5173 — по умолчанию API: `http://localhost:8000` (см. `frontend/src/constants.ts`, `API_BASE_DEFAULT`).

## Команды

| Где | Команда |
|-----|---------|
| корень | `docker compose up --build`, `docker compose down`, `docker compose down -v` |
| `backend/` | `uvicorn app.main:app --reload`, `alembic upgrade head` |
| `frontend/` | `npm run dev`, `npm run build` |
| `backend/` | `pytest -q`, `pytest tests/test_schemathesis.py -q` |

## Документация API (OpenAPI / Swagger)

- Swagger UI: `/docs`
- OpenAPI JSON: `/openapi.json`
- Префикс REST: `/api`

Заголовок для защищённых маршрутов: `Authorization: Bearer <access_token>`.

| Метод | Путь | Назначение |
|-------|------|------------|
| POST | `/api/auth/register`, `/api/auth/login` | Регистрация и вход |
| POST | `/api/auth/refresh` | Обновление пары токенов |
| GET | `/api/auth/specializations` | Специальности для регистрации врача |
| PATCH | `/api/auth/me` | Профиль |
| GET | `/api/users` | Список пользователей (**admin**) |
| GET | `/api/doctors` | Список врачей |
| GET | `/api/patients` | Список пациентов (**admin**, **doctor**) |
| GET/POST | `/api/doctors/{id}/schedule/slots` | Окна приёма |
| DELETE | `/api/schedule/slots/{id}` | Удалить свободное окно |
| GET | `/api/doctors/{id}/slots/free` | Свободные слоты |
| GET/POST | `/api/appointments` | Список и запись |
| POST | `/api/appointments/assign` | Назначение по ФИО пациента (**doctor**, **admin**) |
| POST | `/api/appointments/{id}/cancel` | Отмена |
| GET | `/api/notifications/unread-count` | Счётчик непрочитанных |
| GET | `/api/notifications` | Уведомления |
| PATCH | `/api/notifications/{id}` | Прочитать одно |
| POST | `/api/notifications/read-all` | Прочитать все |

Списки отдают не более 50 элементов за запрос (`limit=50`).

## Тестирование

Зависимости для разработки:

```bash
cd backend
pip install -e ".[dev]"
```

### Модульные и интеграционные тесты (pytest)

```bash
cd backend
pytest -q
```

### Fuzz-тестирование API (Schemathesis)

Проверка соответствия ответов OpenAPI-схеме:

```bash
cd backend
pytest tests/test_schemathesis.py -q
```
