from src.api.adapters.siliconflow_adapter import SiliconFlowAdapter


class DummySiliconFlowConfig:
    def __init__(self):
        self.name = "siliconflow"
        self.base_url = "https://api.siliconflow.cn/v1"
        self.api_key = "test-key"
        self.enabled = True
        self.model = "Pro/zai-org/GLM-4.7"
        self.max_tokens = 2000

    def get_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }


def test_siliconflow_generate_names_uses_openai_compatible_chat_completions(monkeypatch):
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
                                    "Msg", (), {"content": "1. 林星野 - 如星野般辽阔"}
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

    adapter = SiliconFlowAdapter(DummySiliconFlowConfig())
    result = adapter.generate_names("请生成一个测试姓名")

    assert result["success"] is True
    assert calls["client"]["base_url"] == "https://api.siliconflow.cn/v1"
    assert calls["create"]["model"] == "Pro/zai-org/GLM-4.7"
    assert calls["create"]["messages"][1]["content"] == "请生成一个测试姓名"

