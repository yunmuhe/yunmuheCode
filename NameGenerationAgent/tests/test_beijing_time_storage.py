from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select

from src.core.record_service import RecordService
from src.db.models import FavoriteRecord, GenerationRecord


BEIJING_TZ = ZoneInfo("Asia/Shanghai")


def _beijing_now_naive() -> datetime:
    return datetime.now(BEIJING_TZ).replace(microsecond=0, tzinfo=None)


def test_generation_record_created_at_is_stored_in_beijing_time(tmp_path):
    service = RecordService(db_url=f"sqlite:///{tmp_path / 'beijing_generation.db'}")

    before = _beijing_now_naive()
    item = service.create_generation_record(
        user_id=1,
        description="北京时间生成记录",
        cultural_style="chinese_modern",
        gender="neutral",
        age="adult",
        request_count=2,
        api_name="mock",
        model="mock-model",
        names=[{"name": "明远"}],
    )
    after = _beijing_now_naive()

    with service.SessionLocal() as session:
        row = session.execute(
            select(GenerationRecord).where(GenerationRecord.id == int(item["id"]))
        ).scalar_one()

    assert before <= row.created_at <= after


def test_favorite_record_timestamps_are_stored_in_beijing_time(tmp_path):
    service = RecordService(db_url=f"sqlite:///{tmp_path / 'beijing_favorite.db'}")

    before = _beijing_now_naive()
    item = service.upsert_favorite(
        user_id=1,
        item={
            "id": "fav-1",
            "name": "清和",
            "meaning": "温润平和",
            "style": "modern",
            "gender": "neutral",
            "source": "mock",
        },
    )
    after = _beijing_now_naive()

    with service.SessionLocal() as session:
        row = session.execute(
            select(FavoriteRecord).where(FavoriteRecord.favorite_uid == item["id"])
        ).scalar_one()

    assert before <= row.created_at <= after
    assert before <= row.updated_at <= after
