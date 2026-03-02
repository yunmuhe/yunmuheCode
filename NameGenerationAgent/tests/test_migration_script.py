import importlib.util
import sqlite3
from pathlib import Path

from src.core.auth_service import AuthService


def _load_script_module():
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "migrate_auth_sqlite_to_mysql.py"
    spec = importlib.util.spec_from_file_location("migrate_auth_sqlite_to_mysql", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_migrate_auth_data_from_sqlite(tmp_path):
    source = tmp_path / "source_auth.db"
    target = tmp_path / "target_auth.db"

    conn = sqlite3.connect(source)
    conn.execute(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            last_login_at TEXT,
            role TEXT NOT NULL DEFAULT 'user',
            is_enabled INTEGER NOT NULL DEFAULT 1,
            must_change_password INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE user_tokens (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            revoked INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    conn.execute(
        """
        INSERT INTO users (phone, password_hash, created_at, updated_at, role, is_enabled, must_change_password)
        VALUES ('13300133000', 'pbkdf2_sha256$150000$abc$def', '2026-01-01T00:00:00', '2026-01-01T00:00:00', 'admin', 1, 0)
        """
    )
    conn.execute(
        """
        INSERT INTO user_tokens (token, user_id, created_at, expires_at, revoked)
        VALUES ('token_x', 1, '2026-01-01T00:00:00', '2027-01-01T00:00:00', 0)
        """
    )
    conn.commit()
    conn.close()

    target_service = AuthService(db_url=f"sqlite:///{target}")
    module = _load_script_module()
    result = module.migrate_auth_data(
        sqlite_path=str(source),
        target_db_url=f"sqlite:///{target}",
    )

    assert result["users"] == 1
    assert result["tokens"] == 1

    user = target_service.get_user_by_phone("13300133000")
    assert user
    assert user["role"] == "admin"
