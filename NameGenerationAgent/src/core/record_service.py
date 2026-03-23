"""
Generation record persistence service.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Dict, List, Optional
from zoneinfo import ZoneInfo

from sqlalchemy import and_, delete, func, select

from src.db.database import get_engine, get_session_factory, init_db
from src.db.models import FavoriteRecord, GenerationRecord

BEIJING_TZ = ZoneInfo("Asia/Shanghai")


def _to_iso(dt: Optional[datetime]) -> Optional[str]:
    return dt.isoformat() if dt else None


def _utc_now() -> datetime:
    return datetime.now(BEIJING_TZ).replace(microsecond=0, tzinfo=None)


def _generate_favorite_uid(item: Dict) -> str:
    return str(item.get("id") or f"f_{int(datetime.now(UTC).timestamp() * 1000)}")


class RecordService:
    def __init__(self, db_url: Optional[str] = None):
        self.engine = get_engine(db_url)
        init_db(self.engine)
        self.SessionLocal = get_session_factory(db_url)

    def create_generation_record(
        self,
        user_id: int,
        description: str,
        cultural_style: str,
        gender: str,
        age: str,
        request_count: int,
        api_name: str,
        model: str,
        names: List[Dict],
    ) -> Dict:
        names_json = json.dumps(names or [], ensure_ascii=False)
        row = GenerationRecord(
            user_id=user_id,
            description=description,
            cultural_style=cultural_style,
            gender=gender,
            age=age,
            request_count=max(1, int(request_count or 1)),
            api_name=api_name or "",
            model=model or "",
            names_json=names_json,
        )
        with self.SessionLocal() as session:
            session.add(row)
            session.commit()
            session.refresh(row)
            return self._row_to_history_item(row)

    def _row_to_history_item(self, row: GenerationRecord) -> Dict:
        try:
            names = json.loads(row.names_json or "[]")
        except Exception:
            names = []
        return {
            "id": str(row.id),
            "description": row.description,
            "count": int(row.request_count),
            "time": _to_iso(row.created_at),
            "names": [item.get("name", "") for item in names if isinstance(item, dict)],
            "api_name": row.api_name,
            "model": row.model,
            "user_id": row.user_id,
            "names_detail": names,
        }

    def list_user_records(
        self, user_id: int, page: int = 1, page_size: int = 10, q: str = ""
    ) -> Dict:
        safe_page = max(1, int(page or 1))
        safe_size = max(1, min(100, int(page_size or 10)))
        keyword = (q or "").strip()

        with self.SessionLocal() as session:
            stmt = select(GenerationRecord).where(GenerationRecord.user_id == user_id)
            if keyword:
                stmt = stmt.where(GenerationRecord.description.like(f"%{keyword}%"))
            rows = session.execute(
                stmt.order_by(GenerationRecord.created_at.desc(), GenerationRecord.id.desc())
            ).scalars().all()

            total = len(rows)
            start = (safe_page - 1) * safe_size
            end = start + safe_size
            items = [self._row_to_history_item(item) for item in rows[start:end]]
            return {
                "items": items,
                "total": total,
                "page": safe_page,
                "page_size": safe_size,
            }

    def list_records_for_admin(
        self,
        user_id: int,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict:
        safe_page = max(1, int(page or 1))
        safe_size = max(1, min(100, int(page_size or 20)))

        with self.SessionLocal() as session:
            stmt = select(GenerationRecord).where(GenerationRecord.user_id == user_id)
            conditions = []
            if start is not None:
                conditions.append(GenerationRecord.created_at >= start)
            if end is not None:
                conditions.append(GenerationRecord.created_at <= end)
            if conditions:
                stmt = stmt.where(and_(*conditions))

            rows = session.execute(
                stmt.order_by(GenerationRecord.created_at.desc(), GenerationRecord.id.desc())
            ).scalars().all()
            total = len(rows)
            start_idx = (safe_page - 1) * safe_size
            end_idx = start_idx + safe_size
            items = [self._row_to_history_item(item) for item in rows[start_idx:end_idx]]
            return {
                "items": items,
                "total": total,
                "page": safe_page,
                "page_size": safe_size,
            }

    def count_user_records_today(self, user_id: int) -> int:
        start_of_today = datetime.now(BEIJING_TZ).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        )
        with self.SessionLocal() as session:
            stmt = select(func.count(GenerationRecord.id)).where(
                and_(
                    GenerationRecord.user_id == int(user_id),
                    GenerationRecord.created_at >= start_of_today,
                )
            )
            return int(session.execute(stmt).scalar_one() or 0)

    def delete_record(self, record_id: int) -> bool:
        with self.SessionLocal() as session:
            result = session.execute(
                delete(GenerationRecord).where(GenerationRecord.id == int(record_id))
            )
            session.commit()
            return result.rowcount > 0

    @staticmethod
    def _favorite_to_item(row: FavoriteRecord) -> Dict:
        return {
            "id": row.favorite_uid,
            "name": row.name,
            "meaning": row.meaning,
            "style": row.style,
            "gender": row.gender,
            "source": row.source,
            "time": _to_iso(row.created_at),
        }

    def list_favorites(self, user_id: int) -> List[Dict]:
        with self.SessionLocal() as session:
            rows = session.execute(
                select(FavoriteRecord)
                .where(FavoriteRecord.user_id == int(user_id))
                .order_by(FavoriteRecord.updated_at.desc(), FavoriteRecord.id.desc())
            ).scalars().all()
            return [self._favorite_to_item(row) for row in rows]

    def upsert_favorite(self, user_id: int, item: Dict) -> Dict:
        favorite_uid = _generate_favorite_uid(item)
        now = _utc_now()
        with self.SessionLocal() as session:
            row = session.execute(
                select(FavoriteRecord).where(
                    and_(
                        FavoriteRecord.user_id == int(user_id),
                        FavoriteRecord.favorite_uid == favorite_uid,
                    )
                )
            ).scalar_one_or_none()
            if row is None:
                row = FavoriteRecord(
                    user_id=int(user_id),
                    favorite_uid=favorite_uid,
                    created_at=now,
                    updated_at=now,
                )
                session.add(row)

            row.name = str(item.get("name") or "")
            row.meaning = str(item.get("meaning") or "")
            row.style = str(item.get("style") or "")
            row.gender = str(item.get("gender") or "")
            row.source = str(item.get("source") or "")
            row.updated_at = now

            session.commit()
            session.refresh(row)
            return self._favorite_to_item(row)

    def delete_favorites(self, user_id: int, ids: List[str]) -> List[str]:
        if not ids:
            return []
        normalized_ids = [str(i) for i in ids if str(i).strip()]
        if not normalized_ids:
            return []

        with self.SessionLocal() as session:
            rows = session.execute(
                select(FavoriteRecord).where(
                    and_(
                        FavoriteRecord.user_id == int(user_id),
                        FavoriteRecord.favorite_uid.in_(normalized_ids),
                    )
                )
            ).scalars().all()
            deleted_ids = [row.favorite_uid for row in rows]
            if rows:
                row_ids = [row.id for row in rows]
                session.execute(delete(FavoriteRecord).where(FavoriteRecord.id.in_(row_ids)))
                session.commit()
            return deleted_ids


def _build_default_record_service() -> Optional[RecordService]:
    try:
        return RecordService()
    except Exception:
        import os

        url = (os.getenv("DATABASE_URL") or "").strip().lower()
        dialect = (os.getenv("DB_DIALECT") or "").strip().lower()
        if url.startswith("sqlite:") or dialect.startswith("sqlite"):
            try:
                root_dir = os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                )
                data_dir = os.path.join(root_dir, "data")
                os.makedirs(data_dir, exist_ok=True)
                fallback_db = os.path.join(data_dir, "auth_fallback.db")
                return RecordService(db_url=f"sqlite:///{fallback_db}")
            except Exception:
                return None
        raise


record_service = _build_default_record_service()
