import src.core.auth_service as auth_module
import src.web.app as web_app_module
from src.core.auth_service import AuthService


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_disabled_user_cannot_login_and_role_fields_visible(tmp_path, monkeypatch):
    test_db = tmp_path / "auth_roles_test.db"
    service = AuthService(db_url=f"sqlite:///{test_db}")
    monkeypatch.setattr(auth_module, "auth_service", service)

    app = web_app_module.app
    app.config["TESTING"] = True

    with app.test_client() as client:
        register_resp = client.post(
            "/auth/register",
            json={"phone": "13900139000", "password": "123456"},
        )
        assert register_resp.status_code == 201
        user_id = register_resp.get_json()["user"]["id"]

        service.set_user_enabled(user_id, False)
        login_resp = client.post(
            "/auth/login",
            json={"phone": "13900139000", "password": "123456"},
        )
        assert login_resp.status_code == 403

        service.set_user_enabled(user_id, True)
        service.mark_user_must_change_password(user_id, True)
        login_resp2 = client.post(
            "/auth/login",
            json={"phone": "13900139000", "password": "123456"},
        )
        assert login_resp2.status_code == 200
        payload = login_resp2.get_json()
        assert payload["user"]["role"] == "user"
        assert payload["user"]["must_change_password"] is True
        token = payload["token"]

        me_resp = client.get("/auth/me", headers=_auth_header(token))
        assert me_resp.status_code == 200
        me_data = me_resp.get_json()
        assert me_data["user"]["role"] == "user"
        assert me_data["user"]["must_change_password"] is True
