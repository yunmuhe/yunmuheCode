import importlib
import sys


def test_build_default_record_service_returns_none_when_default_database_is_unavailable(
    monkeypatch, tmp_path
):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'records.db'}")
    monkeypatch.setenv("DB_DIALECT", "sqlite")
    sys.modules.pop("src.core.record_service", None)

    record_module = importlib.import_module("src.core.record_service")

    class BrokenRecordService:
        def __init__(self, db_url=None):
            raise RuntimeError("db unavailable")

    monkeypatch.setattr(record_module, "RecordService", BrokenRecordService)

    assert record_module._build_default_record_service() is None


def test_build_default_record_service_uses_sqlite_default(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DB_DIALECT", raising=False)
    sys.modules.pop("src.core.record_service", None)

    record_module = importlib.import_module("src.core.record_service")

    calls = []

    class FakeRecordService:
        def __init__(self, db_url=None):
            calls.append(db_url)

    monkeypatch.setattr(record_module, "RecordService", FakeRecordService)

    service = record_module._build_default_record_service()

    assert service is not None
    assert calls == [None]
