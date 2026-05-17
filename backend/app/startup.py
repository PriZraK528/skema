import logging

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from app.db import engine
from app.seed import run_seed
from app.settings import settings

logger = logging.getLogger(__name__)


def run_migrations() -> None:
    cfg = Config("alembic.ini")
    command.upgrade(cfg, "head")
    logger.info("Database migrations applied")


def init_db() -> None:
    if settings.database_url.startswith("sqlite"):
        return
    run_migrations()
    if settings.seed_on_startup:
        run_seed()
        logger.info("Seed data loaded")
