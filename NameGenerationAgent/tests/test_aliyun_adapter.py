from src.api.adapters.aliyun_adapter import AliyunAdapter


class DummyAliyunConfig:
    def __init__(self):
        self.name = "aliyun"
        self.base_url = "https://dashscope.aliyuncs.com/api/v1"
        self.api_key = "test-key"
        self.enabled = True
        self.model = "qwen3-235b-a22b"
        self.max_tokens = 2000
        self.fallback_models = ["qwen-turbo"]

    def get_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }


class MockResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload
        self.text = str(payload)

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests

            raise requests.exceptions.HTTPError(
                f"{self.status_code} Client Error", response=self
            )


def test_generate_names_uses_dashscope_compatible_chat_completions(monkeypatch):
    calls = []

    def fake_post(url, headers=None, json=None, timeout=None):
        calls.append({"url": url, "headers": headers, "json": json, "timeout": timeout})
        return MockResponse(
            200,
            {
                "choices": [
                    {
                        "message": {
                            "content": "1. 林子轩: 寓意聪慧俊朗",
                        }
                    }
                ]
            },
        )

    monkeypatch.setattr("requests.post", fake_post)

    adapter = AliyunAdapter(DummyAliyunConfig())
    result = adapter.generate_names("请生成一个测试姓名")

    assert result["success"] is True
    assert result["model"] == "qwen3-235b-a22b"
    assert result["names"][0]["name"] == "林子轩"
    assert calls[0]["url"] == "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    assert calls[0]["json"]["model"] == "qwen3-235b-a22b"
    assert "messages" in calls[0]["json"]


def test_generate_names_falls_back_when_free_tier_quota_is_exhausted(monkeypatch):
    calls = []

    def fake_post(url, headers=None, json=None, timeout=None):
        calls.append({"url": url, "headers": headers, "json": json, "timeout": timeout})
        if len(calls) == 1:
            return MockResponse(
                403,
                {
                    "code": "AllocationQuota.FreeTierOnly",
                    "message": "The free tier of the model has been exhausted.",
                },
            )
        return MockResponse(
            200,
            {
                "choices": [
                    {
                        "message": {
                            "content": "1. 赵清岚: 寓意清雅坚定",
                        }
                    }
                ]
            },
        )

    monkeypatch.setattr("requests.post", fake_post)

    adapter = AliyunAdapter(DummyAliyunConfig())
    result = adapter.generate_names("请生成一个测试姓名")

    assert result["success"] is True
    assert result["model"] == "qwen-turbo"
    assert len(calls) == 2
    assert calls[0]["json"]["model"] == "qwen3-235b-a22b"
    assert calls[1]["json"]["model"] == "qwen-turbo"


def test_parse_names_cleans_markdown_labels():
    adapter = AliyunAdapter(DummyAliyunConfig())

    names = adapter._parse_names(
        "**姓名**：林清扬\n**寓意**：取自清风朗月，象征清雅坚定"
    )

    assert names == [
        {
            "name": "林清扬",
            "meaning": "取自清风朗月，象征清雅坚定",
            "source": "aliyun",
        }
    ]
