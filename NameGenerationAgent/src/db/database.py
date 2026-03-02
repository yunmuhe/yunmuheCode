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


def build_database_url() -> str:
    explicit = (os.getenv("DATABASE_URL") or "").strip()
    if explicit:
        return explicit

    dialect = os.getenv("DB_DIALECT", "mysql+pymysql")
    # For ops/debugging only; SQLAlchemy URL does not require this label.
    _connection_name = os.getenv("MYSQL_CONNECTION_NAME", "name_agent_mysql")
    host = os.getenv("MYSQL_HOST", "127.0.0.1")
    port = os.getenv("MYSQL_PORT", "3306")
    user = os.getenv("MYSQL_USER", "name_agent_app")
    password = os.getenv("MYSQL_PASSWORD", "")
    database = os.getenv("MYSQL_DATABASE", "name_generation_agent")

    if dialect.startswith("sqlite"):
        return f"sqlite:///{database}"

    return f"{dialect}://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"


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
