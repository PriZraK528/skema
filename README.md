# Сервис управления онлайн-записями пациентов

Fullstack CRUD-приложение (Python backend + Web frontend) для управления пациентами, врачами и онлайн-записями (appointments).

## Технологии

- Backend: **Python 3.11**, **FastAPI**, SQLAlchemy, Alembic, JWT (auth), pytest, schemathesis/hypothesis (фаззинг)
- DB: **PostgreSQL 16**
- Frontend: **React + Vite + TypeScript**
- Infra: **Docker**, **docker-compose**, Git

## Структура проекта

```
skema/
  backend/                 # FastAPI-приложение, миграции, сиды, тесты
    app/
      main.py
      settings.py
    Dockerfile
    pyproject.toml
  frontend/                # Vite/React приложение
    src/
      main.tsx
    Dockerfile
    package.json
  docker-compose.yml       # запуск всего стека
  .gitignore
  README.md
```

## Запуск (Docker)

```bash
docker compose up --build
```

- Backend: `http://localhost:8000` (health: `/health`, swagger: `/docs`)
- Frontend: `http://localhost:5173`

## Примечания по 12-factor

- Конфигурация через переменные окружения (см. `docker-compose.yml`)
- Логи пишутся в stdout/stderr контейнеров
- Stateless backend (состояние в БД)

