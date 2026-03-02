import src.core.auth_service as auth_module
import src.core.record_service as record_module
import src.web.app as web_app_module
from src.core.auth_service import AuthService
from src.core.record_service import RecordService


def _register_and_login(client, phone, password="123456"):
    client.post("/auth/register", json={"phone": phone, "password": password})
    return client.post("/auth/login", json={"phone": phone, "password": password})


def test_admin_pages_and_actions(tmp_path, monkeypatch):
    test_db = tmp_path / "admin_test.db"
    db_url = f"sqlite:///{test_db}"

    auth = AuthService(db_url=db_url)
    records = RecordService(db_url=db_url)

    monkeypatch.setattr(auth_module, "auth_service", auth)
    monkeypatch.setattr(record_module, "record_service", records)

    app = web_app_module.app
    app.config["TESTING"] = True

    with app.test_client() as client:
        client.get("/admin")
        assert client.get("/admin").status_code in (301, 302)

        # create admin
        admin_login = _register_and_login(client, "13500135000")
        admin_token = admin_login.get_json()["token"]
        admin_user = auth.get_user_by_token(admin_token)
        auth.set_user_role(admin_user["id"], "admin")

        # create normal user and record
        user_login = _register_and_login(client, "13400134000")
        user_token = user_login.get_json()["token"]
        normal_user = auth.get_user_by_token(user_token)
        records.create_generation_record(
            user_id=normal_user["id"],
            description="后台测试记录",
            cultural_style="chinese_modern",
            gender="neutral",
            age="adult",
            request_count=1,
            api_name="mock",
            model="mock-model",
            names=[{"name": "测试名", "meaning": "测试"}],
        )

        # login admin web
        login_page = client.post(
            "/admin/login",
            data={"phone": "13500135000", "password": "123456"},
            follow_redirects=True,
        )
        assert login_page.status_code == 200

        users_page = client.get("/admin")
        assert users_page.status_code == 200

        detail = client.get(f"/admin/users/{normal_user['id']}?start=2000-01-01&end=2100-01-01")
        assert detail.status_code == 200

        disable = client.post(f"/admin/users/{normal_user['id']}/disable", follow_redirects=True)
        assert disable.status_code == 200

        enable = client.post(f"/admin/users/{normal_user['id']}/enable", follow_redirects=True)
        assert enable.status_code == 200

        reset = client.post(f"/admin/users/{normal_user['id']}/reset-password", follow_redirects=True)
        assert reset.status_code == 200

        # after reset, new password should be 123456 and must_change_password should be true
        login_after_reset = client.post("/auth/login", json={"phone": "13400134000", "password": "123456"})
        assert login_after_reset.status_code == 200
        assert login_after_reset.get_json()["user"]["must_change_password"] is True

        user_records = records.list_user_records(normal_user["id"], page=1, page_size=20)
        assert user_records["items"]
        rid = user_records["items"][0]["id"]
        delete_record = client.post(f"/admin/records/{rid}/delete", follow_redirects=True)
        assert delete_record.status_code == 200
