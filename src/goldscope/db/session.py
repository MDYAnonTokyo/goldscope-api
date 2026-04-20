from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from goldscope.core.config import get_settings


def _engine_kwargs(database_url: str) -> dict:
    if database_url.startswith("sqlite"):
        return {
            "connect_args": {"check_same_thread": False},
            "future": True,
        }
    return {"future": True}


@lru_cache
def create_engine_for_url(database_url: str):
    return create_engine(database_url, **_engine_kwargs(database_url))


def get_engine():
    settings = get_settings()
    return create_engine_for_url(settings.database_url)


def get_session_factory():
    return sessionmaker(bind=get_engine(), autoflush=False, autocommit=False, class_=Session)


def get_db():
    session_factory = get_session_factory()
    db = session_factory()
    try:
        yield db
    finally:
        db.close()
