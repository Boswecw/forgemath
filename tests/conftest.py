import os
from collections.abc import Generator
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

SQLALCHEMY_TEST_DATABASE_URL = "sqlite://"
os.environ.setdefault("FORGEMATH_DATABASE_URL", SQLALCHEMY_TEST_DATABASE_URL)
os.environ.setdefault("FORGEMATH_HOST", "127.0.0.1")
os.environ.setdefault("FORGEMATH_PORT", "8011")

from app.database import Base, get_db, get_session_factory
from app.main import app
from app.models import governance  # noqa: F401
from app.models import evaluation  # noqa: F401
import app.services.immutability as _immutability  # noqa: F401


engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    def override_get_session_factory():
        return TestingSessionLocal

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_session_factory] = override_get_session_factory

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
