import asyncio
import os
from collections.abc import Generator
from pathlib import Path
import sys

import httpx
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

TEST_DB_PATH = Path("/tmp/forgemath-test.sqlite3")
SQLALCHEMY_TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"
os.environ.setdefault("FORGEMATH_DATABASE_URL", SQLALCHEMY_TEST_DATABASE_URL)
os.environ.setdefault("FORGEMATH_HOST", "127.0.0.1")
os.environ.setdefault("FORGEMATH_PORT", "8011")

from app.config import validate_config
from app.database import Base, get_db, get_session_factory
from app.main import app
from app.models import governance  # noqa: F401
from app.models import evaluation  # noqa: F401
import app.services.immutability as _immutability  # noqa: F401


engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


class SyncASGIClient:
    def __init__(self) -> None:
        self._transport = httpx.ASGITransport(app=app)
        self._base_url = "http://testserver"

    async def _request_async(self, method: str, url: str, **kwargs):
        async with httpx.AsyncClient(
            transport=self._transport,
            base_url=self._base_url,
        ) as client:
            return await client.request(method, url, **kwargs)

    def request(self, method: str, url: str, **kwargs):
        return asyncio.run(self._request_async(method, url, **kwargs))

    def get(self, url: str, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs):
        return self.request("POST", url, **kwargs)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[SyncASGIClient, None, None]:
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
    validate_config()
    yield SyncASGIClient()

    app.dependency_overrides.clear()
