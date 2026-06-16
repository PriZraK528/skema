#!/bin/sh
set -e
cd /app
alembic upgrade head
if [ "$SEED_ON_STARTUP" = "true" ]; then
  python -c "from app.seed import run_seed; run_seed()"
fi
PORT="${PORT:-8000}"
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
