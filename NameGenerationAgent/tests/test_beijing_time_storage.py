import importlib
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select

from src.core.auth_service import AuthService
from src.db.models import FavoriteRecord, GenerationRecord, User, UserToken


BEIJING_TZ = ZoneInfo("Asia/Shanghai")


def _beijing_now_naive() -> datetime:
    return datetime.now(BEIJING_TZ).replace(microsecond=0, tzinfo=None)


def _import_record_service(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'bootstrap.db'}")
    monkeypatch.setenv("DB_DIALECT", "sqlite")
    sys.modules.pop("src.core.record_service", None)
    return importlib.import_module("src.core.record_service")


def test_generation_record_created_at_is_stored_in_beijing_time(tmp_path, monkeypatch):
    record_module = _import_record_service(monkeypatch, tmp_path)
    service = record_module.RecordService(
        db_url=f"sqlite:///{tmp_path / 'beijing_generation.db'}"
    )

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


def test_favorite_record_timestamps_are_stored_in_beijing_time(tmp_path, monkeypatch):
    record_module = _import_record_service(monkeypatch, tmp_path)
    service = record_module.RecordService(
        db_url=f"sqlite:///{tmp_path / 'beijing_favorite.db'}"
    )

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


def test_auth_service_user_and_token_timestamps_are_stored_in_beijing_time(tmp_path):
    service = AuthService(db_url=f"sqlite:///{tmp_path / 'beijing_auth.db'}")

    before_register = _beijing_now_naive()
    ok, payload, status = service.register_user("13900139000", "123456")
    after_register = _beijing_now_naive()

    assert ok is True
    assert status == 201

    before_login = _beijing_now_naive()
    ok, payload, status = service.login_user("13900139000", "123456")
    after_login = _beijing_now_naive()

    assert ok is True
    assert status == 200

    with service.SessionLocal() as session:
        user = session.execute(select(User).where(User.phone == "13900139000")).scalar_one()
        token = session.execute(
            select(UserToken).where(UserToken.user_id == user.id)
        ).scalar_one()

    assert before_register <= user.created_at <= after_register
    assert before_login <= user.updated_at <= after_login
    assert before_login <= user.last_login_at <= after_login
    assert before_login <= token.created_at <= after_login
