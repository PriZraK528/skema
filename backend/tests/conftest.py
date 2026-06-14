import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "test-secret"
os.environ["SEED_ON_STARTUP"] = "false"
os.environ["CLINIC_REGISTRATION_KEY"] = "test-clinic-key"
os.environ["ENABLE_APPOINTMENT_COMPLETER"] = "false"


@pytest.fixture(scope="session")
def db_engine():
    import app.db as db_module
    from app.db import Base
    from app import models
    from app.seed import run_seed

    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    db_module.engine = engine
    db_module.SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    run_seed()
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session", autouse=True)
def _init_db(db_engine):
    yield


@pytest.fixture()
def client(db_engine):
    from app.db import get_db
    from app.main import create_app

    TestingSession = sessionmaker(bind=db_engine, autoflush=False, autocommit=False)

    app = create_app()

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
