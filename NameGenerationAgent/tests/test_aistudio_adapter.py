from src.api.adapters.aistudio_adapter import AistudioAdapter


class DummyAistudioConfig:
    def __init__(self):
        self.name = "aistudio"
        self.base_url = "https://example.aistudio/v1"
        self.api_key = "test-key"
        self.enabled = True
        self.model = "bad-model"
        self.max_tokens = 2000
        self.stream = True
        self.response_format = None
        self.fallback_models = ["fallback-model"]

    def get_completion_params(self):
        return {
            "model": self.model,
            "stream": self.stream,
            "max_tokens": self.max_tokens,
            "response_format": self.response_format,
        }


def test_aistudio_adapter_falls_back_and_reads_reasoning_content(monkeypatch):
    calls = {"models": []}

    class FakeChunk:
        def __init__(self, reasoning_content=None, content=None):
            delta = type(
                "Delta",
                (),
                {"reasoning_content": reasoning_content, "content": content},
            )()
            self.choices = [type("Choice", (), {"delta": delta})()]

    class FakeCompletions:
        def create(self, **kwargs):
            calls["models"].append(kwargs["model"])
            if kwargs["model"] == "bad-model":
                raise Exception("40405 unsupported model")
            return iter([FakeChunk(reasoning_content="1. 林听风 - 如风般清朗")])

    class FakeOpenAI:
        def __init__(self, api_key=None, base_url=None):
            self.chat = type("Chat", (), {"completions": FakeCompletions()})()

    monkeypatch.setattr("openai.OpenAI", FakeOpenAI)

    adapter = AistudioAdapter(DummyAistudioConfig())
    result = adapter.generate_names("测试提示词")

    assert result["success"] is True
    assert result["model"] == "fallback-model"
    assert calls["models"] == ["bad-model", "fallback-model"]
