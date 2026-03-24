"""
Authentication service backed by SQLAlchemy with SQLite persistence.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import re
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from zoneinfo import ZoneInfo

from sqlalchemy import and_, select

from src.db.database import get_engine, get_session_factory, init_db
from src.db.models import User, UserToken

PHONE_PATTERN = re.compile(r"^1\d{10}$")
PBKDF2_ITERATIONS = 150000
BEIJING_TZ = ZoneInfo("Asia/Shanghai")


def _utc_now() -> datetime:
    return datetime.now(BEIJING_TZ).replace(microsecond=0, tzinfo=None)


def _utc_now_iso() -> str:
    return _utc_now().isoformat()


def _hash_password(password: str, salt: Optional[bytes] = None) -> str:
    if salt is None:
        salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    salt_text = base64.urlsafe_b64encode(salt).decode("ascii")
    digest_text = base64.urlsafe_b64encode(digest).decode("ascii")
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt_text}${digest_text}"


def _verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations_text, salt_text, digest_text = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        iterations = int(iterations_text)
        salt = base64.urlsafe_b64decode(salt_text.encode("ascii"))
        expected = base64.urlsafe_b64decode(digest_text.encode("ascii"))
    except Exception:
        return False

    current = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations,
    )
    return hmac.compare_digest(current, expected)


class AuthService:
    def __init__(self, db_url: Optional[str] = None):
        self.engine = get_engine(db_url)
        init_db(self.engine)
        self.SessionLocal = get_session_factory(db_url)
        self._ensure_admin_user_from_env()

    def _validate_credentials(self, phone: str, password: str) -> Optional[str]:
        if not PHONE_PATTERN.match(phone or ""):
            return "手机号格式不正确"
        if not password or len(password) < 6:
            return "密码长度至少 6 位"
        return None

    @staticmethod
    def _row_to_user(row: User) -> Dict:
        def to_iso(value):
            return value.isoformat() if value else None

        return {
            "id": row.id,
            "phone": row.phone,
            "role": row.role,
            "is_enabled": bool(row.is_enabled),
            "must_change_password": bool(row.must_change_password),
            "created_at": to_iso(row.created_at),
            "updated_at": to_iso(row.updated_at),
            "last_login_at": to_iso(row.last_login_at),
        }

    def _ensure_admin_user_from_env(self) -> None:
        phone = (os.getenv("ADMIN_PHONE") or "").strip()
        password = (os.getenv("ADMIN_PASSWORD") or "").strip()
        if not phone or not password:
            return
        if not PHONE_PATTERN.match(phone):
            return
        if len(password) < 6:
            return

        with self.SessionLocal() as session:
            row = session.execute(select(User).where(User.phone == phone)).scalar_one_or_none()
            now = _utc_now()
            if row is None:
                row = User(
                    phone=phone,
                    password_hash=_hash_password(password),
                    role="admin",
                    is_enabled=True,
                    must_change_password=False,
                    created_at=now,
                    updated_at=now,
                )
                session.add(row)
            else:
                row.role = "admin"
                row.is_enabled = True
                row.updated_at = now
            session.commit()

    def register_user(self, phone: str, password: str) -> Tuple[bool, Dict, int]:
        error = self._validate_credentials(phone, password)
        if error:
            return False, {"success": False, "error": error}, 400

        now = _utc_now()
        with self.SessionLocal() as session:
            exists = session.execute(select(User).where(User.phone == phone)).scalar_one_or_none()
            if exists:
                return False, {"success": False, "error": "该手机号已注册"}, 409

            row = User(
                phone=phone,
                password_hash=_hash_password(password),
                role="user",
                is_enabled=True,
                must_change_password=False,
                created_at=now,
                updated_at=now,
            )
            session.add(row)
            session.commit()
            session.refresh(row)
            return True, {"success": True, "user": self._row_to_user(row)}, 201

    def login_user(self, phone: str, password: str, token_ttl_days: int = 7) -> Tuple[bool, Dict, int]:
        error = self._validate_credentials(phone, password)
        if error:
            return False, {"success": False, "error": error}, 400

        with self.SessionLocal() as session:
            row = session.execute(select(User).where(User.phone == phone)).scalar_one_or_none()
            if row is None:
                return False, {"success": False, "error": "账号不存在"}, 404
            if not row.is_enabled:
                return False, {"success": False, "error": "账号已被禁用"}, 403
            if not _verify_password(password, row.password_hash):
                return False, {"success": False, "error": "密码错误"}, 401

            now = _utc_now()
            expires = now + timedelta(days=token_ttl_days)
            token = secrets.token_urlsafe(40)
            token_row = UserToken(
                token=token,
                user_id=row.id,
                created_at=now,
                expires_at=expires,
                revoked=False,
            )
            row.last_login_at = now
            row.updated_at = now
            session.add(token_row)
            session.commit()
            session.refresh(row)
            return (
                True,
                {
                    "success": True,
                    "token": token,
                    "expires_at": expires.isoformat(),
                    "user": self._row_to_user(row),
                },
                200,
            )

    def get_user_by_token(self, token: str) -> Optional[Dict]:
        if not token:
            return None
        now = _utc_now()
        with self.SessionLocal() as session:
            stmt = (
                select(User)
                .join(UserToken, UserToken.user_id == User.id)
                .where(
                    and_(
                        UserToken.token == token,
                        UserToken.revoked.is_(False),
                        UserToken.expires_at > now,
                    )
                )
            )
            row = session.execute(stmt).scalar_one_or_none()
            if not row:
                return None
            return self._row_to_user(row)

    def logout_token(self, token: str) -> bool:
        if not token:
            return False
        with self.SessionLocal() as session:
            row = session.execute(select(UserToken).where(UserToken.token == token)).scalar_one_or_none()
            if not row or row.revoked:
                return False
            row.revoked = True
            session.commit()
            return True

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        with self.SessionLocal() as session:
            row = session.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
            return self._row_to_user(row) if row else None

    def get_user_by_phone(self, phone: str) -> Optional[Dict]:
        with self.SessionLocal() as session:
            row = session.execute(select(User).where(User.phone == phone)).scalar_one_or_none()
            return self._row_to_user(row) if row else None

    def set_user_enabled(self, user_id: int, enabled: bool) -> bool:
        with self.SessionLocal() as session:
            row = session.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
            if not row:
                return False
            row.is_enabled = bool(enabled)
            row.updated_at = _utc_now()
            session.commit()
            return True

    def set_user_role(self, user_id: int, role: str) -> bool:
        if role not in {"admin", "user"}:
            return False
        with self.SessionLocal() as session:
            row = session.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
            if not row:
                return False
            row.role = role
            row.updated_at = _utc_now()
            session.commit()
            return True

    def mark_user_must_change_password(self, user_id: int, required: bool) -> bool:
        with self.SessionLocal() as session:
            row = session.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
            if not row:
                return False
            row.must_change_password = bool(required)
            row.updated_at = _utc_now()
            session.commit()
            return True

    def reset_user_password(self, user_id: int, temp_password: str = "123456") -> bool:
        if len(temp_password) < 6:
            return False
        with self.SessionLocal() as session:
            row = session.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
            if not row:
                return False
            row.password_hash = _hash_password(temp_password)
            row.must_change_password = True
            row.updated_at = _utc_now()
            session.commit()
            return True

    def change_password_by_token(
        self, token: str, old_password: str, new_password: str
    ) -> Tuple[bool, Dict, int]:
        if not token:
            return False, {"success": False, "error": "未提供令牌"}, 401
        if not new_password or len(new_password) < 6:
            return False, {"success": False, "error": "新密码长度至少 6 位"}, 400

        now = _utc_now()
        with self.SessionLocal() as session:
            stmt = (
                select(User, UserToken)
                .join(UserToken, UserToken.user_id == User.id)
                .where(
                    and_(
                        UserToken.token == token,
                        UserToken.revoked.is_(False),
                        UserToken.expires_at > now,
                    )
                )
            )
            row = session.execute(stmt).first()
            if not row:
                return False, {"success": False, "error": "令牌无效或已过期"}, 401
            user = row[0]
            if not _verify_password(old_password or "", user.password_hash):
                return False, {"success": False, "error": "原密码错误"}, 401
            user.password_hash = _hash_password(new_password)
            user.must_change_password = False
            user.updated_at = now
            session.commit()
        return True, {"success": True}, 200

    def list_users(
        self,
        phone: str = "",
        role: str = "",
        enabled: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict:
        safe_page = max(1, int(page or 1))
        safe_size = max(1, min(100, int(page_size or 20)))

        with self.SessionLocal() as session:
            stmt = select(User)
            if phone:
                stmt = stmt.where(User.phone.like(f"%{phone}%"))
            if role in {"admin", "user"}:
                stmt = stmt.where(User.role == role)
            if enabled is not None:
                stmt = stmt.where(User.is_enabled.is_(bool(enabled)))

            all_rows = session.execute(stmt.order_by(User.id.desc())).scalars().all()
            total = len(all_rows)
            start = (safe_page - 1) * safe_size
            end = start + safe_size
            items = [self._row_to_user(x) for x in all_rows[start:end]]
            return {
                "items": items,
                "total": total,
                "page": safe_page,
                "page_size": safe_size,
            }


def _build_default_auth_service() -> Optional[AuthService]:
    try:
        return AuthService()
    except Exception:
        return None


auth_service = _build_default_auth_service()
