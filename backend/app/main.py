import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import appointments, auth, doctors, notifications, schedule, users
from app.settings import settings

logging.basicConfig(level=logging.INFO)


def create_app() -> FastAPI:
    app = FastAPI(
        title="SKEMA API",
        version="1.0.0",
        description="REST API для управления онлайн-записями пациентов",
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
    app.include_router(schedule.router, prefix="/api")
    app.include_router(appointments.router, prefix="/api")
    app.include_router(notifications.router, prefix="/api")

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
