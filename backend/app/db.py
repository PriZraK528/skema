import enum

from sqlalchemy import Enum, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.settings import settings


class Base(DeclarativeBase):
    pass


def db_enum(enum_cls: type[enum.Enum], name: str) -> Enum:
    native = settings.database_url.startswith("postgresql")
    return Enum(enum_cls, name=name, native_enum=native)


engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

