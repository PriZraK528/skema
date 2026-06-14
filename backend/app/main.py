from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.db import SessionLocal
from app.openapi import build_openapi
from app.routers import appointments, auth, doctors, notifications, patients, schedule, users
from app.services.appointments import complete_past_appointments
from app.settings import settings
from app.validation_errors import translate_validation_error

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def _appointment_completer_loop() -> None:
    interval = settings.appointment_complete_interval_seconds
    while True:
        try:
            db = SessionLocal()
            try:
                count = complete_past_appointments(db)
                if count:
                    logger.info("Auto-completed %s past appointment(s)", count)
            finally:
                db.close()
        except Exception:
            logger.exception("Appointment auto-complete task failed")
        await asyncio.sleep(interval)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task: asyncio.Task | None = None
    if settings.enable_appointment_completer:
        task = asyncio.create_task(_appointment_completer_loop())
    yield
    if task is not None:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


def create_app() -> FastAPI:
    app = FastAPI(
        title="SKEMA API",
        version="1.0.0",
        description="REST API для управления онлайн-записями пациентов",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router, prefix="/api")
    app.include_router(users.router, prefix="/api")
    app.include_router(doctors.router, prefix="/api")
    app.include_router(patients.router, prefix="/api")
    app.include_router(schedule.router, prefix="/api")
    app.include_router(appointments.router, prefix="/api")
    app.include_router(notifications.router, prefix="/api")

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_request, exc: RequestValidationError):
        messages = [translate_validation_error(err) for err in exc.errors()]
        return JSONResponse(status_code=422, content={"detail": "; ".join(messages)})

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    app.openapi = lambda: build_openapi(app)

    return app


app = create_app()
