import importlib


def test_db_models_have_required_fields(tmp_path):
    db_path = tmp_path / "db_models_test.sqlite"
    db_url = f"sqlite:///{db_path}"

    database = importlib.import_module("src.db.database")
    models = importlib.import_module("src.db.models")

    engine = database.get_engine(db_url)
    database.init_db(engine)

    inspector = importlib.import_module("sqlalchemy").inspect(engine)
    tables = set(inspector.get_table_names())
    assert "users" in tables
    assert "user_tokens" in tables
    assert "generation_records" in tables
    assert "favorite_records" in tables

    users_columns = {item["name"] for item in inspector.get_columns("users")}
    assert "role" in users_columns
    assert "is_enabled" in users_columns
    assert "must_change_password" in users_columns

    record_columns = {item["name"] for item in inspector.get_columns("generation_records")}
    assert "user_id" in record_columns
    assert "names_json" in record_columns

    fav_columns = {item["name"] for item in inspector.get_columns("favorite_records")}
    assert "user_id" in fav_columns
    assert "favorite_uid" in fav_columns

    assert hasattr(models.User, "generation_records")
    assert hasattr(models.User, "favorites")
