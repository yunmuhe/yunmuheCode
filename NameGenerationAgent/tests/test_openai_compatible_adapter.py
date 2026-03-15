class DummyConfig:
    def __init__(self):
        self.name = "dummy"
        self.base_url = "https://example.com/v1"
        self.api_key = "test-key"
        self.enabled = True
        self.model = "test-model"
        self.max_tokens = 256


def test_openai_compatible_adapter_uses_openai_client_and_returns_standard_result(monkeypatch):
    calls = {}

    class FakeCompletions:
        def create(self, **kwargs):
            calls["create"] = kwargs
            return type(
                "Resp",
                (),
                {
                    "choices": [
                        type(
                            "Choice",
                            (),
                            {
                                "message": type(
                                    "Msg", (), {"content": "1. test - standard"}
                                )()
                            },
                        )()
                    ]
                },
            )()

    class FakeOpenAI:
        def __init__(self, api_key=None, base_url=None):
            calls["client"] = {"api_key": api_key, "base_url": base_url}
            self.chat = type("Chat", (), {"completions": FakeCompletions()})()

    monkeypatch.setattr("openai.OpenAI", FakeOpenAI)

    from src.api.adapters.openai_compatible_adapter import OpenAICompatibleAdapter

    class DummyAdapter(OpenAICompatibleAdapter):
        system_prompt = "test system"

        def _parse_generated_text(self, text):
            return [{"name": "test", "meaning": text, "source": self.name}]

    adapter = DummyAdapter(DummyConfig())
    result = adapter.generate_names("prompt", temperature=0.2)

    assert calls["client"]["base_url"] == "https://example.com/v1"
    assert calls["create"]["model"] == "test-model"
    assert calls["create"]["messages"][0]["content"] == "test system"
    assert result["success"] is True
    assert result["model"] == "test-model"
    assert result["names"][0]["name"] == "test"


def test_openai_compatible_adapter_allows_runtime_model_override(monkeypatch):
    calls = {}

    class FakeCompletions:
        def create(self, **kwargs):
            calls["create"] = kwargs
            return type(
                "Resp",
                (),
                {
                    "choices": [
                        type(
                            "Choice",
                            (),
                            {
                                "message": type(
                                    "Msg", (), {"content": "1. test - override"}
                                )()
                            },
                        )()
                    ]
                },
            )()

    class FakeOpenAI:
        def __init__(self, api_key=None, base_url=None):
            self.chat = type("Chat", (), {"completions": FakeCompletions()})()

    monkeypatch.setattr("openai.OpenAI", FakeOpenAI)

    from src.api.adapters.openai_compatible_adapter import OpenAICompatibleAdapter

    class DummyAdapter(OpenAICompatibleAdapter):
        def _parse_generated_text(self, text):
            return [{"name": "test", "meaning": text, "source": self.name}]

    adapter = DummyAdapter(DummyConfig())
    result = adapter.generate_names("prompt", model="runtime-model")

    assert result["success"] is True
    assert result["model"] == "runtime-model"
    assert calls["create"]["model"] == "runtime-model"
