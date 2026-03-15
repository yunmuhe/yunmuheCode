import types

import src.web.app as web_app_module
import src.api.model_manager as model_manager_module
import src.api.unified_client as unified_client_module


class DummyAdapter:
    def __init__(self, available=True):
        self._available = available

    def is_available(self):
        return self._available


def test_get_all_models_returns_platform_summary(monkeypatch):
    fake_model_manager = types.SimpleNamespace(
        get_all_models=lambda adapters: {
            "aliyun": [{"id": "qwen-turbo", "name": "qwen-turbo", "is_default": True}],
            "siliconflow": [{"id": "sf-model", "name": "sf-model", "is_default": False}],
        }
    )
    fake_unified_client = types.SimpleNamespace(adapters={"aliyun": DummyAdapter(), "siliconflow": DummyAdapter()})

    monkeypatch.setattr(model_manager_module, "model_manager", fake_model_manager)
    monkeypatch.setattr(unified_client_module, "unified_client", fake_unified_client)

    app = web_app_module.app
    app.config["TESTING"] = True

    with app.test_client() as client:
        response = client.get("/models")

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["platforms"] == ["aliyun", "siliconflow"]
    assert data["total_count"] == 2
    assert data["models"]["aliyun"][0]["id"] == "qwen-turbo"


def test_get_platform_models_refreshes_cache(monkeypatch):
    clear_calls = []
    fake_model_manager = types.SimpleNamespace(
        clear_cache=lambda api_name: clear_calls.append(api_name),
        get_models_for_api=lambda api_name, adapter: [
            {"id": "qwen-turbo", "name": "qwen-turbo", "description": "fallback", "is_default": True}
        ],
    )
    fake_unified_client = types.SimpleNamespace(adapters={"aliyun": DummyAdapter()})

    monkeypatch.setattr(model_manager_module, "model_manager", fake_model_manager)
    monkeypatch.setattr(unified_client_module, "unified_client", fake_unified_client)

    app = web_app_module.app
    app.config["TESTING"] = True

    with app.test_client() as client:
        response = client.get("/models?api=aliyun&refresh=true")

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["api"] == "aliyun"
    assert data["count"] == 1
    assert clear_calls == ["aliyun"]


def test_generate_forwards_requested_model_to_generator(monkeypatch):
    calls = []

    class DummyGenerator:
        def generate_names(self, **kwargs):
            calls.append(kwargs)
            return {
                "success": True,
                "names": [{"name": "林清扬", "meaning": "清朗高远"}],
                "api_name": kwargs.get("preferred_api"),
                "model": kwargs.get("model"),
            }

    monkeypatch.setattr(web_app_module, "get_auth_service", lambda: object())
    monkeypatch.setattr(
        web_app_module,
        "get_current_user_from_token",
        lambda auth_service: {"id": 1, "phone": "13800138000"},
    )
    monkeypatch.setattr(web_app_module, "get_name_generator", lambda: DummyGenerator())
    monkeypatch.setattr(web_app_module, "get_record_service", lambda: None)

    app = web_app_module.app
    app.config["TESTING"] = True

    with app.test_client() as client:
        response = client.post(
            "/generate",
            json={
                "description": "一个清雅的古风男性角色",
                "count": 1,
                "preferred_api": "aliyun",
                "model": "qwen-turbo",
            },
            headers={"Authorization": "Bearer test-token"},
        )

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert calls[0]["preferred_api"] == "aliyun"
    assert calls[0]["model"] == "qwen-turbo"
