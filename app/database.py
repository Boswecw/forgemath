from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import DATABASE_URL


def _build_engine_kwargs(database_url: str) -> dict[str, object]:
    url = make_url(database_url)
    kwargs: dict[str, object] = {"pool_pre_ping": True}
    if url.get_backend_name().startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    return kwargs


class Base(DeclarativeBase):
    pass


engine = create_engine(DATABASE_URL, **_build_engine_kwargs(DATABASE_URL))
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


def get_session_factory():
    return SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

