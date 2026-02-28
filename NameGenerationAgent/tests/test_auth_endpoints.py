import src.core.auth_service as auth_module
import src.web.app as web_app_module
from src.core.auth_service import AuthService


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_auth_register_login_me_logout_flow(tmp_path, monkeypatch):
    test_db = tmp_path / "auth_test.db"
    monkeypatch.setattr(auth_module, "auth_service", AuthService(db_path=str(test_db)))

    app = web_app_module.app
    app.config["TESTING"] = True

    with app.test_client() as client:
        register_resp = client.post(
            "/auth/register",
            json={"phone": "13800138000", "password": "123456"},
        )
        assert register_resp.status_code == 201
        register_data = register_resp.get_json()
        assert register_data["success"] is True
        assert register_data["user"]["phone"] == "13800138000"

        duplicate_resp = client.post(
            "/auth/register",
            json={"phone": "13800138000", "password": "123456"},
        )
        assert duplicate_resp.status_code == 409

        login_resp = client.post(
            "/auth/login",
            json={"phone": "13800138000", "password": "123456"},
        )
        assert login_resp.status_code == 200
        login_data = login_resp.get_json()
        assert login_data["success"] is True
        token = login_data["token"]
        assert token

        me_resp = client.get("/auth/me", headers=_auth_header(token))
        assert me_resp.status_code == 200
        me_data = me_resp.get_json()
        assert me_data["success"] is True
        assert me_data["user"]["phone"] == "13800138000"

        logout_resp = client.post("/auth/logout", headers=_auth_header(token))
        assert logout_resp.status_code == 200
        assert logout_resp.get_json()["success"] is True

        expired_resp = client.get("/auth/me", headers=_auth_header(token))
        assert expired_resp.status_code == 401
