import importlib


def test_build_database_url_defaults_to_project_sqlite(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DB_DIALECT", raising=False)
    monkeypatch.delenv("SQLITE_DATABASE_PATH", raising=False)

    database = importlib.import_module("src.db.database")

    url = database.build_database_url()

    assert url.startswith("sqlite:///")
    assert "data" in url
    assert url.endswith("name_generation_agent.db")


def test_build_database_url_ignores_non_sqlite_database_url(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", "mysql+pymysql://demo:demo@127.0.0.1:3306/demo")
    monkeypatch.setenv("DB_DIALECT", "mysql+pymysql")
    monkeypatch.setenv("SQLITE_DATABASE_PATH", str(tmp_path / "forced.sqlite"))

    database = importlib.import_module("src.db.database")

    url = database.build_database_url()

    assert url == f"sqlite:///{tmp_path / 'forced.sqlite'}"
