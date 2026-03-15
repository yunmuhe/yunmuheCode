import importlib
import sys
import warnings


def _import_with_sqlite(monkeypatch, module_name: str, tmp_path):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'warnings.db'}")
    monkeypatch.setenv("DB_DIALECT", "sqlite")
    sys.modules.pop(module_name, None)
    return importlib.import_module(module_name)


def test_auth_service_utc_now_does_not_emit_deprecation_warning(monkeypatch, tmp_path):
    auth_service_module = _import_with_sqlite(monkeypatch, "src.core.auth_service", tmp_path)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        value = auth_service_module._utc_now()

    assert value.microsecond == 0


def test_models_utc_now_does_not_emit_deprecation_warning(monkeypatch, tmp_path):
    _import_with_sqlite(monkeypatch, "src.core.auth_service", tmp_path)
    models_module = importlib.import_module("src.db.models")
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        value = models_module.utc_now()

    assert value.microsecond == 0


def test_record_service_utc_helpers_do_not_emit_deprecation_warning(monkeypatch, tmp_path):
    record_service_module = _import_with_sqlite(monkeypatch, "src.core.record_service", tmp_path)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        now = record_service_module._utc_now()
        favorite_uid = record_service_module._generate_favorite_uid({})

    assert now.microsecond == 0
    assert favorite_uid.startswith("f_")
