# SKEMA — онлайн-запись в клинику

Веб-приложение для записи пациентов на приём: врач открывает окна в расписании, пациент выбирает свободный слот, администратор и врач могут назначать записи пациентам.

Стек: **FastAPI**, **PostgreSQL**, **React** (Vite, TypeScript). JWT: access-токен (30 мин) и refresh-токен (14 дней); фронт обновляет сессию автоматически.

## Быстрый старт

Нужен [Docker Desktop](https://www.docker.com/products/docker-desktop/). В корне проекта:

```bash
docker compose up --build
```

| Сервис   | Адрес |
|----------|--------|
| Frontend | http://localhost:5173 |
| Backend  | http://localhost:8000 |
| Swagger  | http://localhost:8000/docs |

При первом запуске выполняются миграции БД и создаются демо-пользователи.

## Демо-аккаунты

Пароль для всех: `Password123!`

| Email | Роль |
|-------|------|
| patient@clinic.example | Пациент |
| doctor@clinic.example | Врач |
| admin@clinic.example | Администратор |

Ключ регистрации врача (Docker): `clinic-demo-key`

## Роли и возможности

**Пациент** — запись к врачу на свободное окно, просмотр и отмена своих записей, профиль, уведомления.

**Врач** — создание и удаление своих окон приёма, назначение записей пациентам из списка зарегистрированных, просмотр своих приёмов.

**Администратор** — управление расписанием любого врача, назначение записей, просмотр всех записей, список пользователей.

Записаться можно только на окно, которое врач заранее создал в разделе «Расписание». Прошедшие записи со статусом «Записан» автоматически переводятся в «Завершён».

## Структура проекта

```
skema/
├── docker-compose.yml
├── backend/          # FastAPI, Alembic, тесты
│   ├── app/
│   │   ├── routers/  # auth, users, doctors, patients, schedule, appointments, notifications
│   │   ├── services/
│   │   └── models.py
│   └── tests/
└── frontend/         # React SPA
    └── src/
        └── components/
```

## API

Префикс: `/api`. Документация: `/docs`.

| Метод | Путь | Назначение |
|-------|------|------------|
| POST | `/auth/register`, `/auth/login` | Регистрация и вход |
| POST | `/auth/refresh` | Обновление access-токена |
| GET | `/auth/specializations` | Специальности для регистрации врача |
| PATCH | `/auth/me` | Редактирование профиля |
| GET | `/users` | Список пользователей (admin) |
| GET | `/doctors` | Список врачей |
| GET | `/patients` | Список пациентов (admin, doctor) |
| GET/POST | `/doctors/{id}/schedule/slots` | Окна приёма |
| DELETE | `/schedule/slots/{id}` | Удалить свободное окно |
| GET | `/doctors/{id}/slots/free` | Свободные слоты для записи |
| GET/POST | `/appointments` | Список и создание записи |
| POST | `/appointments/assign` | Назначение записи по ФИО пациента |
| POST | `/appointments/{id}/cancel` | Отмена |
| GET | `/notifications` | Уведомления |
| GET | `/notifications/unread-count` | Счётчик непрочитанных |
| PATCH | `/notifications/{id}` | Отметить прочитанным |
| POST | `/notifications/read-all` | Прочитать все |

## Локальная разработка без Docker

**Backend:**

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

## Тесты

```bash
cd backend
pip install -e ".[dev]"
pytest -q
pytest tests/test_schemathesis.py -q
```