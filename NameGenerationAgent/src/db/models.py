"""
SQLAlchemy models for authentication and generation records.
"""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


BEIJING_TZ = ZoneInfo("Asia/Shanghai")


def utc_now() -> datetime:
    return datetime.now(BEIJING_TZ).replace(microsecond=0, tzinfo=None)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    phone: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user")
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    must_change_password: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utc_now
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    tokens: Mapped[list["UserToken"]] = relationship(
        "UserToken", back_populates="user", cascade="all, delete-orphan"
    )
    generation_records: Mapped[list["GenerationRecord"]] = relationship(
        "GenerationRecord", back_populates="user", cascade="all, delete-orphan"
    )
    favorites: Mapped[list["FavoriteRecord"]] = relationship(
        "FavoriteRecord", back_populates="user", cascade="all, delete-orphan"
    )


class UserToken(Base):
    __tablename__ = "user_tokens"

    token: Mapped[str] = mapped_column(String(200), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utc_now
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    user: Mapped["User"] = relationship("User", back_populates="tokens")


class GenerationRecord(Base):
    __tablename__ = "generation_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    cultural_style: Mapped[str] = mapped_column(String(64), nullable=False)
    gender: Mapped[str] = mapped_column(String(32), nullable=False)
    age: Mapped[str] = mapped_column(String(32), nullable=False)
    request_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    api_name: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    model: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    names_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utc_now, index=True
    )

    user: Mapped["User"] = relationship("User", back_populates="generation_records")


class FavoriteRecord(Base):
    __tablename__ = "favorite_records"
    __table_args__ = (UniqueConstraint("user_id", "favorite_uid", name="uq_user_favorite_uid"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    favorite_uid: Mapped[str] = mapped_column(String(120), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    meaning: Mapped[str] = mapped_column(Text, nullable=False, default="")
    style: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    gender: Mapped[str] = mapped_column(String(60), nullable=False, default="")
    source: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utc_now, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utc_now
    )

    user: Mapped["User"] = relationship("User", back_populates="favorites")
