"""
Database configuration and session management.
"""

from __future__ import annotations

import os
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

_ENGINE_CACHE = {}


def get_default_sqlite_path() -> str:
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)

    configured_path = (os.getenv("SQLITE_DATABASE_PATH") or "").strip()
    if configured_path:
        return (
            configured_path
            if os.path.isabs(configured_path)
            else os.path.join(project_root, configured_path)
        )

    return os.path.join(data_dir, "name_generation_agent.db")


def build_database_url() -> str:
    explicit = (os.getenv("DATABASE_URL") or "").strip()
    if explicit.lower().startswith("sqlite:"):
        return explicit

    sqlite_path = get_default_sqlite_path()
    return f"sqlite:///{sqlite_path}"


def get_engine(db_url: Optional[str] = None):
    url = db_url or build_database_url()
    cached = _ENGINE_CACHE.get(url)
    if cached is not None:
        return cached

    kwargs = {"future": True}
    if not url.startswith("sqlite"):
        kwargs["pool_pre_ping"] = True

    engine = create_engine(url, **kwargs)
    _ENGINE_CACHE[url] = engine
    return engine


def get_session_factory(db_url: Optional[str] = None):
    engine = get_engine(db_url)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db(engine=None) -> None:
    from . import models  # noqa: F401

    active_engine = engine or get_engine()
    Base.metadata.create_all(bind=active_engine)
