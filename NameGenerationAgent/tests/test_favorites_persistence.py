import src.core.auth_service as auth_module
import src.core.record_service as record_module
import src.web.app as web_app_module
from src.core.auth_service import AuthService
from src.core.record_service import RecordService


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _register_and_login(client, phone: str) -> str:
    client.post("/auth/register", json={"phone": phone, "password": "123456"})
    resp = client.post("/auth/login", json={"phone": phone, "password": "123456"})
    return resp.get_json()["token"]


def test_favorites_are_persistent_and_user_scoped(tmp_path, monkeypatch):
    test_db = tmp_path / "favorites_test.db"
    db_url = f"sqlite:///{test_db}"

    monkeypatch.setattr(auth_module, "auth_service", AuthService(db_url=db_url))
    monkeypatch.setattr(record_module, "record_service", RecordService(db_url=db_url))

    app = web_app_module.app
    app.config["TESTING"] = True

    with app.test_client() as client:
        no_auth = client.get("/favorites")
        assert no_auth.status_code == 401

        token_a = _register_and_login(client, "13100131000")
        token_b = _register_and_login(client, "13200132000")

        add_a = client.post(
            "/favorites",
            headers=_auth_header(token_a),
            json={
                "id": "fav-1",
                "name": "张三",
                "meaning": "寓意测试",
                "style": "现代中文",
                "gender": "中性",
                "source": "mock",
            },
        )
        assert add_a.status_code == 200
        assert add_a.get_json()["item"]["id"] == "fav-1"

        add_b = client.post(
            "/favorites",
            headers=_auth_header(token_b),
            json={
                "id": "fav-1",
                "name": "李四",
                "meaning": "另一个用户",
                "style": "现代中文",
                "gender": "中性",
                "source": "mock",
            },
        )
        assert add_b.status_code == 200

        list_a = client.get("/favorites", headers=_auth_header(token_a)).get_json()
        list_b = client.get("/favorites", headers=_auth_header(token_b)).get_json()
        assert len(list_a["items"]) == 1
        assert len(list_b["items"]) == 1
        assert list_a["items"][0]["name"] == "张三"
        assert list_b["items"][0]["name"] == "李四"

        # update same favorite id for user A should overwrite
        client.post(
            "/favorites",
            headers=_auth_header(token_a),
            json={
                "id": "fav-1",
                "name": "张三新",
                "meaning": "更新含义",
                "style": "古风",
                "gender": "中性",
                "source": "mock",
            },
        )
        list_a2 = client.get("/favorites", headers=_auth_header(token_a)).get_json()
        assert len(list_a2["items"]) == 1
        assert list_a2["items"][0]["name"] == "张三新"

        delete_resp = client.delete(
            "/favorites",
            headers=_auth_header(token_a),
            json={"ids": ["fav-1"]},
        )
        assert delete_resp.status_code == 200
        assert delete_resp.get_json()["deleted"] == ["fav-1"]
        list_a3 = client.get("/favorites", headers=_auth_header(token_a)).get_json()
        assert list_a3["items"] == []
