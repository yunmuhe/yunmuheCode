import importlib
import os
import sys
import types


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from config.prompts import PromptTemplates


class DummyUnifiedClient:
    def __init__(self):
        self.calls = []

    def generate_names(self, **kwargs):
        self.calls.append(kwargs)
        return {
            "success": True,
            "names": [
                {"name": "林清扬", "meaning": "清朗高远", "source": "mock"},
                {"name": "苏知远", "meaning": "学识深远", "source": "mock"},
                {"name": "顾明澈", "meaning": "聪慧澄明", "source": "mock"},
            ],
            "api_name": "mock",
            "model": "mock-model",
        }

    def get_available_apis(self):
        return ["mock"]

    def get_api_status(self):
        return {"mock": {"enabled": True}}


class DummyPromptTemplates:
    def build_prompt(self, **kwargs):
        return f"base:{kwargs['description']}|count:{kwargs['count']}"

    def get_available_styles(self):
        return ["chinese_modern"]

    def get_available_genders(self):
        return ["neutral"]

    def get_available_ages(self):
        return ["adult"]

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


class DummyCorpusEnhancer:
    def __init__(self):
        self.enhanced_prompts = []
        self.filter_calls = []

    def get_corpus_stats(self):
        return {
            "现代人名总数": 100,
            "古代人名总数": 80,
            "成语总数": 60,
        }

    def get_name_suggestions(self, keywords, gender=None, count=10):
        return [
            {"name": "清扬", "meaning": "清朗飞扬"},
            {"name": "知远", "meaning": "见识高远"},
        ][:count]

    def enhance_prompt(self, base_prompt, description, options=None):
        prompt = f"{base_prompt}|enhanced:{description}"
        self.enhanced_prompts.append(
            {
                "base_prompt": base_prompt,
                "description": description,
                "options": options or {},
                "prompt": prompt,
            }
        )
        return prompt

    def get_chengyu_names(self, count=5):
        return [
            {
                "name": "清扬",
                "meaning": "取自神采飞扬",
                "source": "chengyu",
            }
        ][:count]

    def filter_and_rank_names(self, generated_names, description, options=None):
        self.filter_calls.append(
            {
                "generated_names": generated_names,
                "description": description,
                "options": options or {},
            }
        )
        return [
            {
                "name": item["name"],
                "meaning": item["meaning"],
                "source": "corpus_rank",
            }
            for item in generated_names
        ]


def import_name_generator_module(monkeypatch):
    dummy_client = DummyUnifiedClient()
    dummy_enhancer = DummyCorpusEnhancer()

    unified_client_module = types.ModuleType("src.api.unified_client")
    unified_client_module.unified_client = dummy_client

    corpus_enhancer_module = types.ModuleType("src.core.corpus_enhancer")
    corpus_enhancer_module.get_corpus_enhancer = lambda: dummy_enhancer

    monkeypatch.setitem(sys.modules, "src.api.unified_client", unified_client_module)
    monkeypatch.setitem(sys.modules, "src.core.corpus_enhancer", corpus_enhancer_module)
    sys.modules.pop("src.core.name_generator", None)

    module = importlib.import_module("src.core.name_generator")
    return module, dummy_client, dummy_enhancer


def build_generator(monkeypatch):
    module, dummy_client, dummy_enhancer = import_name_generator_module(monkeypatch)

    monkeypatch.setattr(module, "get_unified_client", lambda: dummy_client)
    monkeypatch.setattr(module, "get_prompt_templates", lambda: DummyPromptTemplates())
    monkeypatch.setattr(module, "get_input_validator", lambda: DummyValidator())
    monkeypatch.setattr(module, "get_response_validator", lambda: DummyValidator())
    monkeypatch.setattr(module, "get_corpus_enhancer", lambda: dummy_enhancer)

    return module.NameGenerator(), dummy_client, dummy_enhancer


def test_corpus_enhancer_initialization(monkeypatch):
    generator, _, _ = build_generator(monkeypatch)

    stats = generator.corpus_enhancer.get_corpus_stats()

    assert generator.corpus_enhancer is not None
    assert stats["现代人名总数"] == 100
    assert stats["古代人名总数"] == 80
    assert stats["成语总数"] == 60


def test_corpus_helper_methods(monkeypatch):
    generator, _, _ = build_generator(monkeypatch)

    suggestions = generator.corpus_enhancer.get_name_suggestions(["智", "学"], gender="neutral", count=2)
    chengyu_names = generator.corpus_enhancer.get_chengyu_names()

    assert len(suggestions) == 2
    assert suggestions[0]["name"] == "清扬"
    assert chengyu_names[0]["source"] == "chengyu"


def test_full_generation_with_corpus_uses_local_stubs(monkeypatch):
    generator, dummy_client, dummy_enhancer = build_generator(monkeypatch)

    result = generator.generate_names(
        description="一个聪明好学的孩子",
        count=3,
        cultural_style="chinese_modern",
        gender="neutral",
        use_mock_on_failure=False,
    )

    assert result["success"] is True
    assert result["api_name"] == "mock"
    assert result["model"] == "mock-model"
    assert len(result["names"]) == 3
    assert len(dummy_client.calls) == 1
    assert "enhanced:一个聪明好学的孩子" in dummy_client.calls[0]["prompt"]
    assert dummy_enhancer.enhanced_prompts[0]["options"]["cultural_style"] == "chinese_modern"
    assert dummy_enhancer.filter_calls[0]["options"]["cultural_style"] == "chinese_modern"

    for name_obj in result["names"]:
        assert name_obj["source"] == "corpus_rank"
        assert "features" in name_obj
        assert "length" in name_obj["features"]


def test_prompt_templates_with_corpus_examples():
    prompt = PromptTemplates.build_prompt(
        description="一个智慧的学者",
        count=5,
        cultural_style="chinese_traditional",
        gender="male",
        corpus_examples=["清扬", "知远"],
        enhancement_type="realistic",
    )

    assert isinstance(prompt, str)
    assert "一个智慧的学者" in prompt
    assert "清扬" in prompt
    assert "知远" in prompt
    assert "chinese_traditional" not in prompt


def test_prompt_templates_expose_enhancement_types():
    enhancement_types = PromptTemplates.get_available_enhancement_types()

    assert isinstance(enhancement_types, list)
    assert "realistic" in enhancement_types
