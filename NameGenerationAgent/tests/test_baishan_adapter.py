import importlib
import os
import sys


class DummyBaishanConfig:
    def __init__(self):
        self.name = "baishan"
        self.base_url = "https://api.edgefn.net/v1"
        self.api_key = "test-key"
        self.enabled = True
        self.model = "MiniMax-M2.5"
        self.max_tokens = 2000


def test_baishan_generate_names_uses_openai_compatible_chat_completions(monkeypatch):
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
                                    "Msg", (), {"content": "1. 白澈 - 清明通透"}
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

    from src.api.adapters.baishan_adapter import BaishanAdapter

    adapter = BaishanAdapter(DummyBaishanConfig())
    result = adapter.generate_names("请生成一个测试姓名")

    assert result["success"] is True
    assert calls["client"]["base_url"] == "https://api.edgefn.net/v1"
    assert calls["create"]["model"] == "MiniMax-M2.5"
    assert calls["create"]["messages"][1]["content"] == "请生成一个测试姓名"


def test_baishan_generate_names_allows_runtime_model_override(monkeypatch):
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
                                    "Msg", (), {"content": "1. 白衡 - 稳重平衡"}
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

    from src.api.adapters.baishan_adapter import BaishanAdapter

    adapter = BaishanAdapter(DummyBaishanConfig())
    result = adapter.generate_names("prompt", model="MiniMax-Text-01")

    assert result["success"] is True
    assert result["model"] == "MiniMax-Text-01"
    assert calls["create"]["model"] == "MiniMax-Text-01"


def test_api_manager_includes_baishan_when_api_key_present(monkeypatch):
    monkeypatch.setenv("BAISHAN_API_KEY", "baishan-test-key")
    monkeypatch.setenv("BAISHAN_MODEL", "MiniMax-M2.5")

    sys.modules.pop("config.api_config", None)
    module = importlib.import_module("config.api_config")
    module = importlib.reload(module)

    manager = module.APIManager()

    assert "baishan" in manager.apis
    assert "baishan" in manager.active_apis
    assert manager.apis["baishan"].base_url == "https://api.edgefn.net/v1"
    assert manager.apis["baishan"].model == "MiniMax-M2.5"
