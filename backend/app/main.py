import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers import appointments, auth, doctors, notifications, patients, schedule, users
from app.settings import settings
from app.validation_errors import translate_validation_error

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

    return app


app = create_app()
