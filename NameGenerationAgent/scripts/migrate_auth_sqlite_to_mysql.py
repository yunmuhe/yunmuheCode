"""
Migrate auth users/tokens data from SQLite to target SQLAlchemy DB URL.
"""

from __future__ import annotations

import argparse
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable

from sqlalchemy import select

from src.db.database import get_engine, get_session_factory, init_db
from src.db.models import User, UserToken


def _parse_dt(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    text = str(value).strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text)
    except Exception:
        return None


def _sqlite_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {row[1] for row in rows}


def _rows(conn: sqlite3.Connection, sql: str) -> Iterable[sqlite3.Row]:
    conn.row_factory = sqlite3.Row
    return conn.execute(sql).fetchall()


def migrate_auth_data(sqlite_path: str, target_db_url: str) -> Dict[str, int]:
    source = Path(sqlite_path)
    if not source.exists():
        raise FileNotFoundError(f"SQLite file not found: {sqlite_path}")

    source_conn = sqlite3.connect(str(source))
    source_conn.row_factory = sqlite3.Row

    engine = get_engine(target_db_url)
    init_db(engine)
    SessionLocal = get_session_factory(target_db_url)

    user_columns = _sqlite_columns(source_conn, "users")
    token_columns = _sqlite_columns(source_conn, "user_tokens")

    users = _rows(source_conn, "SELECT * FROM users")
    tokens = _rows(source_conn, "SELECT * FROM user_tokens")

    migrated_users = 0
    migrated_tokens = 0

    with SessionLocal() as session:
        for row in users:
            row_id = int(row["id"]) if "id" in row.keys() and row["id"] is not None else None
            phone = str(row["phone"]).strip()
            password_hash = str(row["password_hash"])
            role = str(row["role"]) if "role" in user_columns and row["role"] else "user"
            is_enabled = bool(int(row["is_enabled"])) if "is_enabled" in user_columns else True
            must_change_password = (
                bool(int(row["must_change_password"]))
                if "must_change_password" in user_columns
                else False
            )

            created_at = _parse_dt(row["created_at"]) or datetime.utcnow()
            updated_at = _parse_dt(row["updated_at"]) or created_at
            last_login_at = _parse_dt(row["last_login_at"]) if "last_login_at" in user_columns else None

            target_user = session.execute(select(User).where(User.phone == phone)).scalar_one_or_none()
            if target_user is None:
                target_user = User(
                    id=row_id,
                    phone=phone,
                    password_hash=password_hash,
                    role=role,
                    is_enabled=is_enabled,
                    must_change_password=must_change_password,
                    created_at=created_at,
                    updated_at=updated_at,
                    last_login_at=last_login_at,
                )
                session.add(target_user)
            else:
                target_user.password_hash = password_hash
                target_user.role = role
                target_user.is_enabled = is_enabled
                target_user.must_change_password = must_change_password
                target_user.created_at = created_at
                target_user.updated_at = updated_at
                target_user.last_login_at = last_login_at
            migrated_users += 1

        session.commit()

        for row in tokens:
            token = str(row["token"])
            user_id = int(row["user_id"])
            created_at = _parse_dt(row["created_at"]) or datetime.utcnow()
            expires_at = _parse_dt(row["expires_at"]) or datetime.utcnow()
            revoked = bool(int(row["revoked"])) if "revoked" in token_columns else False

            user_exists = session.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
            if not user_exists:
                continue

            target_token = session.execute(
                select(UserToken).where(UserToken.token == token)
            ).scalar_one_or_none()
            if target_token is None:
                target_token = UserToken(
                    token=token,
                    user_id=user_id,
                    created_at=created_at,
                    expires_at=expires_at,
                    revoked=revoked,
                )
                session.add(target_token)
            else:
                target_token.user_id = user_id
                target_token.created_at = created_at
                target_token.expires_at = expires_at
                target_token.revoked = revoked
            migrated_tokens += 1

        session.commit()

    source_conn.close()
    return {"users": migrated_users, "tokens": migrated_tokens}


def main():
    parser = argparse.ArgumentParser(description="Migrate auth data from SQLite to target DB")
    parser.add_argument("--sqlite-path", required=True, help="Source sqlite auth.db path")
    parser.add_argument("--target-db-url", required=True, help="Target SQLAlchemy database URL")
    args = parser.parse_args()

    result = migrate_auth_data(args.sqlite_path, args.target_db_url)
    print(f"migrated users={result['users']} tokens={result['tokens']}")


if __name__ == "__main__":
    main()
