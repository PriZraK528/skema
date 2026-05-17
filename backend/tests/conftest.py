import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "test-secret"
os.environ["SEED_ON_STARTUP"] = "false"


@pytest.fixture()
def client():
    import app.db as db_module
    from app.db import Base, get_db
    from app import models  # noqa: F401
    from app.seed import run_seed

    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db_module.engine = engine
    db_module.SessionLocal = TestingSession
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    run_seed()

    from app.main import create_app

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

    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()
