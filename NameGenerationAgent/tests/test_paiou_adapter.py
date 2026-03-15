from src.api.adapters.paiou_adapter import PaiouAdapter


class DummyPaiouConfig:
    def __init__(self):
        self.name = "paiou"
        self.base_url = "https://api.ppinfra.com/openai"
        self.api_key = "test-key"
        self.enabled = True
        self.model = "deepseek/deepseek-v3-0324"
        self.max_tokens = 1000
        self.stream = True
        self.response_format = {"type": "text"}


def test_paiou_adapter_passes_provider_specific_completion_params(monkeypatch):
    calls = {}

    class FakeChunk:
        def __init__(self, content):
            self.choices = [type("Choice", (), {"delta": type("Delta", (), {"content": content})()})()]

    class FakeCompletions:
        def create(self, **kwargs):
            calls["create"] = kwargs
            return iter([FakeChunk("1. 林见川 - 如山川般沉静")])

    class FakeOpenAI:
        def __init__(self, api_key=None, base_url=None):
            self.chat = type("Chat", (), {"completions": FakeCompletions()})()

    monkeypatch.setattr("openai.OpenAI", FakeOpenAI)

    adapter = PaiouAdapter(DummyPaiouConfig())
    result = adapter.generate_names("测试提示词")

    assert result["success"] is True
    assert calls["create"]["response_format"] == {"type": "text"}
    assert calls["create"]["stream"] is True

