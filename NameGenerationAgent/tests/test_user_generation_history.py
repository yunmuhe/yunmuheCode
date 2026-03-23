import src.core.auth_service as auth_module
import src.core.record_service as record_module
import src.web.app as web_app_module
from src.core.auth_service import AuthService
from src.core.record_service import RecordService


class DummyNameGenerator:
    def generate_names(self, **kwargs):
        count = kwargs.get("count", 2)
        names = []
        for idx in range(count):
            names.append(
                {
                    "id": f"name_{idx}",
                    "name": f"测试名{idx}",
                    "meaning": f"寓意{idx}",
                    "source": "mock",
                }
            )
        return {"success": True, "names": names, "api_name": "mock", "model": "mock-model"}

    def get_generation_stats(self):
        return {
            "available_apis": 1,
            "api_status": {"mock": {"enabled": True}},
            "cache_stats": {"active_entries": 0},
        }


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _register_and_login(client, phone):
    client.post("/auth/register", json={"phone": phone, "password": "123456"})
    login = client.post("/auth/login", json={"phone": phone, "password": "123456"})
    return login.get_json()["token"]


def test_generate_and_history_are_user_scoped(tmp_path, monkeypatch):
    test_db = tmp_path / "history_test.db"
    db_url = f"sqlite:///{test_db}"
    monkeypatch.setattr(auth_module, "auth_service", AuthService(db_url=db_url))
    monkeypatch.setattr(record_module, "record_service", RecordService(db_url=db_url))
    monkeypatch.setattr(web_app_module, "get_name_generator", lambda: DummyNameGenerator())

    app = web_app_module.app
    app.config["TESTING"] = True

    with app.test_client() as client:
        anonymous = client.post(
            "/generate",
            json={"description": "一个勇敢的角色", "count": 2, "cultural_style": "chinese_modern", "gender": "neutral", "age": "adult"},
        )
        assert anonymous.status_code == 401

        token_a = _register_and_login(client, "13700137000")
        token_b = _register_and_login(client, "13600136000")

        gen_a = client.post(
            "/generate",
            headers=_auth_header(token_a),
            json={"description": "用户A角色", "count": 2, "cultural_style": "chinese_modern", "gender": "neutral", "age": "adult"},
        )
        assert gen_a.status_code == 200

        gen_b = client.post(
            "/generate",
            headers=_auth_header(token_b),
            json={"description": "用户B角色", "count": 1, "cultural_style": "chinese_modern", "gender": "neutral", "age": "adult"},
        )
        assert gen_b.status_code == 200

        hist_a = client.get("/history/list?page=1&page_size=20", headers=_auth_header(token_a))
        hist_b = client.get("/history/list?page=1&page_size=20", headers=_auth_header(token_b))

        assert hist_a.status_code == 200
        assert hist_b.status_code == 200
        items_a = hist_a.get_json()["items"]
        items_b = hist_b.get_json()["items"]
        assert len(items_a) == 1
        assert len(items_b) == 1
        assert "用户A角色" in items_a[0]["description"]
        assert "用户B角色" in items_b[0]["description"]


def test_stats_returns_today_generated_for_current_user(tmp_path, monkeypatch):
    test_db = tmp_path / "stats_history_test.db"
    db_url = f"sqlite:///{test_db}"
    monkeypatch.setattr(auth_module, "auth_service", AuthService(db_url=db_url))
    monkeypatch.setattr(record_module, "record_service", RecordService(db_url=db_url))
    monkeypatch.setattr(web_app_module, "get_name_generator", lambda: DummyNameGenerator())

    app = web_app_module.app
    app.config["TESTING"] = True

    with app.test_client() as client:
        token_a = _register_and_login(client, "13500135000")
        token_b = _register_and_login(client, "13400134000")

        client.post(
            "/generate",
            headers=_auth_header(token_a),
            json={"description": "用户A今日记录", "count": 2, "cultural_style": "chinese_modern", "gender": "neutral", "age": "adult"},
        )
        client.post(
            "/generate",
            headers=_auth_header(token_b),
            json={"description": "用户B今日记录", "count": 1, "cultural_style": "chinese_modern", "gender": "neutral", "age": "adult"},
        )

        stats_response = client.get("/stats", headers=_auth_header(token_a))

        assert stats_response.status_code == 200
        payload = stats_response.get_json()
        assert payload["success"] is True
        assert payload["stats"]["today_generated"] == 1
