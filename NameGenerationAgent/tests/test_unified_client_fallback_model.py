from src.api.adapters.base_adapter import APIException
import src.api.unified_client as unified_client_module


class DummyRouter:
    def get_priority(self, adapters, preferred_api=None, context=None):
        return ["aliyun", "paiou"]


class FailingAdapter:
    def __init__(self):
        self.calls = []

    def generate_names(self, prompt, **kwargs):
        self.calls.append(kwargs)
        raise APIException("primary failed")


class SuccessAdapter:
    def __init__(self):
        self.calls = []
        self.name = "paiou"
        self.base_url = "https://example.com"

    def generate_names(self, prompt, **kwargs):
        self.calls.append(kwargs)
        return {
            "success": True,
            "names": [{"name": "林清和", "meaning": "清朗平和", "source": "paiou"}],
            "api_name": "paiou",
            "model": kwargs.get("model", "default-model"),
        }


def test_fallback_adapter_does_not_reuse_preferred_model(monkeypatch):
    primary = FailingAdapter()
    fallback = SuccessAdapter()

    monkeypatch.setattr(
        unified_client_module.UnifiedAPIClient,
        "_initialize_adapters",
        lambda self: setattr(self, "adapters", {"aliyun": primary, "paiou": fallback}),
    )
    monkeypatch.setattr(
        unified_client_module.UnifiedAPIClient,
        "_initialize_router",
        lambda self: setattr(self, "router_strategy", DummyRouter()),
    )

    client = unified_client_module.UnifiedAPIClient()

    result = client.generate_names(
        prompt="测试提示词",
        count=1,
        preferred_api="aliyun",
        model="glm-5",
        use_cache=False,
        use_mock_on_failure=False,
    )

    assert result["success"] is True
    assert primary.calls[0]["model"] == "glm-5"
    assert "model" not in fallback.calls[0]
