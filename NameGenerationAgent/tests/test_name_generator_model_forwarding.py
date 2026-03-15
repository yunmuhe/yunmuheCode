import importlib
import os
import sys
import types


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


class DummyUnifiedClient:
    def __init__(self):
        self.calls = []

    def generate_names(self, **kwargs):
        self.calls.append(kwargs)
        return {
            "success": True,
            "names": [{"name": "林清扬", "meaning": "清朗高远"}],
            "api_name": "aliyun",
            "model": kwargs.get("model"),
        }


class DummyPromptTemplates:
    def build_prompt(self, **kwargs):
        return "测试提示词"

    def get_available_styles(self):
        return []

    def get_available_genders(self):
        return []

    def get_available_ages(self):
        return []

    def get_available_scenarios(self):
        return []


class DummyValidator:
    def validate_description(self, value):
        return {"valid": True}

    def validate_name_count(self, value):
        return {"valid": True}

    def validate_cultural_style(self, value):
        return {"valid": True}

    def validate_gender(self, value):
        return {"valid": True}

    def validate_age(self, value):
        return {"valid": True}

    def validate_api_response(self, value):
        return {"valid": True}


def import_name_generator_module(monkeypatch):
    dummy_client = DummyUnifiedClient()

    unified_client_module = types.ModuleType("src.api.unified_client")
    unified_client_module.unified_client = dummy_client

    monkeypatch.setitem(sys.modules, "src.api.unified_client", unified_client_module)
    sys.modules.pop("src.core.name_generator", None)

    module = importlib.import_module("src.core.name_generator")
    return module, dummy_client


def test_name_generator_forwards_model_to_unified_client(monkeypatch):
    module, dummy_client = import_name_generator_module(monkeypatch)

    monkeypatch.setattr(module, "get_unified_client", lambda: dummy_client)
    monkeypatch.setattr(module, "get_prompt_templates", lambda: DummyPromptTemplates())
    monkeypatch.setattr(module, "get_input_validator", lambda: DummyValidator())
    monkeypatch.setattr(module, "get_response_validator", lambda: DummyValidator())
    monkeypatch.setattr(module, "get_corpus_enhancer", lambda: None)

    generator = module.NameGenerator()
    result = generator.generate_names(
        description="一个清雅的古风男性角色",
        preferred_api="aliyun",
        model="qwen-turbo",
        count=1,
        use_mock_on_failure=False,
    )

    assert result["success"] is True
    assert dummy_client.calls[0]["preferred_api"] == "aliyun"
    assert dummy_client.calls[0]["model"] == "qwen-turbo"
