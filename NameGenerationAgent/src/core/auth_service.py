"""
Authentication service backed by SQLite.
"""
from __future__ import annotations

import os
import re
import secrets
import sqlite3
import hashlib
import hmac
import base64
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple


PHONE_PATTERN = re.compile(r"^1\d{10}$")
PBKDF2_ITERATIONS = 150000


def _utc_now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat()


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
    def __init__(self, db_path: Optional[str] = None):
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_dir = os.path.join(root_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        env_db_path = os.getenv("AUTH_DB_PATH")
        self.db_path = db_path or env_db_path or os.path.join(data_dir, "auth.db")
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_login_at TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_tokens (
                    token TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    revoked INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_user_tokens_user_id
                ON user_tokens(user_id)
                """
            )

    def _validate_credentials(self, phone: str, password: str) -> Optional[str]:
        if not PHONE_PATTERN.match(phone or ""):
            return "手机号格式不正确"
        if not password or len(password) < 6:
            return "密码长度至少 6 位"
        return None

    def _row_to_user(self, row: sqlite3.Row) -> Dict:
        return {
            "id": row["id"],
            "phone": row["phone"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "last_login_at": row["last_login_at"],
        }

    def register_user(self, phone: str, password: str) -> Tuple[bool, Dict, int]:
        error = self._validate_credentials(phone, password)
        if error:
            return False, {"success": False, "error": error}, 400

        now = _utc_now_iso()
        password_hash = _hash_password(password)
        try:
            with self._get_conn() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO users (phone, password_hash, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (phone, password_hash, now, now),
                )
                user_id = cursor.lastrowid
                user_row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            return True, {"success": True, "user": self._row_to_user(user_row)}, 201
        except sqlite3.IntegrityError:
            return False, {"success": False, "error": "该手机号已注册"}, 409

    def login_user(self, phone: str, password: str, token_ttl_days: int = 7) -> Tuple[bool, Dict, int]:
        error = self._validate_credentials(phone, password)
        if error:
            return False, {"success": False, "error": error}, 400

        with self._get_conn() as conn:
            user_row = conn.execute("SELECT * FROM users WHERE phone = ?", (phone,)).fetchone()
            if not user_row:
                return False, {"success": False, "error": "账号不存在"}, 404
            if not _verify_password(password, user_row["password_hash"]):
                return False, {"success": False, "error": "密码错误"}, 401

            now = datetime.utcnow().replace(microsecond=0)
            expires = now + timedelta(days=token_ttl_days)
            token = secrets.token_urlsafe(40)
            conn.execute(
                """
                INSERT INTO user_tokens (token, user_id, created_at, expires_at, revoked)
                VALUES (?, ?, ?, ?, 0)
                """,
                (token, user_row["id"], now.isoformat(), expires.isoformat()),
            )
            conn.execute(
                "UPDATE users SET last_login_at = ?, updated_at = ? WHERE id = ?",
                (now.isoformat(), now.isoformat(), user_row["id"]),
            )
            fresh_user = conn.execute("SELECT * FROM users WHERE id = ?", (user_row["id"],)).fetchone()

        return True, {
            "success": True,
            "token": token,
            "expires_at": expires.isoformat(),
            "user": self._row_to_user(fresh_user),
        }, 200

    def get_user_by_token(self, token: str) -> Optional[Dict]:
        if not token:
            return None
        now = _utc_now_iso()
        with self._get_conn() as conn:
            row = conn.execute(
                """
                SELECT u.*
                FROM user_tokens t
                JOIN users u ON t.user_id = u.id
                WHERE t.token = ?
                  AND t.revoked = 0
                  AND t.expires_at > ?
                """,
                (token, now),
            ).fetchone()
            if not row:
                return None
            return self._row_to_user(row)

    def logout_token(self, token: str) -> bool:
        if not token:
            return False
        with self._get_conn() as conn:
            result = conn.execute(
                "UPDATE user_tokens SET revoked = 1 WHERE token = ? AND revoked = 0",
                (token,),
            )
            return result.rowcount > 0


auth_service = AuthService()
