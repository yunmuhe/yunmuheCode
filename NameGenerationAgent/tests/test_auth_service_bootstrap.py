import importlib
import sys


def test_build_default_auth_service_returns_none_when_default_database_is_unavailable(
    monkeypatch, tmp_path
):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'bootstrap.db'}")
    monkeypatch.setenv("DB_DIALECT", "sqlite")
    sys.modules.pop("src.core.auth_service", None)

    auth_module = importlib.import_module("src.core.auth_service")

    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DB_DIALECT", raising=False)

    class BrokenAuthService:
        def __init__(self, db_url=None):
            raise RuntimeError("db unavailable")

    monkeypatch.setattr(auth_module, "AuthService", BrokenAuthService)

    assert auth_module._build_default_auth_service() is None
