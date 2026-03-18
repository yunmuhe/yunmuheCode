import json
from typing import Any, Dict, List

from . import register_adapter
from .openai_compatible_adapter import OpenAICompatibleAdapter


class AistudioAdapter(OpenAICompatibleAdapter):
    def list_models(self) -> List[Dict[str, Any]]:
        if not self.is_available():
            return []

        current_model = getattr(self.config, "model", "Qwen3-30B-A3B-Q4_K_M")
        return [
            {
                "id": current_model,
                "name": current_model,
                "description": f"AI Studio {current_model}",
                "is_default": True,
            }
        ]

    def _resolve_stream(self, kwargs: Dict[str, Any]) -> bool:
        return bool(kwargs.get("stream", getattr(self.config, "stream", True)))

    def _provider_completion_params(self, **kwargs) -> Dict[str, Any]:
        params = super()._provider_completion_params(**kwargs)
        response_format = kwargs.get(
            "response_format", getattr(self.config, "response_format", None)
        )
        if response_format:
            params["response_format"] = response_format
        return params

    def _should_fallback(self, error_message: str) -> bool:
        return ("暂不支持该模型" in error_message) or ("40405" in error_message)

    def _extract_stream_chunk_text(self, chunk: Any) -> str:
        choices = getattr(chunk, "choices", None) or []
        if not choices:
            return ""
        delta = getattr(choices[0], "delta", None)
        return (
            getattr(delta, "reasoning_content", None)
            or getattr(delta, "content", None)
            or ""
        )

    def _parse_generated_text(self, text: str):
        return self._parse_structured_or_text(text)

    def _parse_structured_or_text(self, text: str):
        try:
            obj = json.loads(text)
        except Exception:
            return self._parse_names(text)

        items = obj.get("items") or obj.get("names") or obj.get("data") or []
        result = []
        for item in items:
            name = (item.get("name") or "").strip()
            meaning = (item.get("meaning") or "").strip()
            if name and meaning and self._is_valid_name(name) and self._is_valid_meaning(meaning):
                result.append({"name": name, "meaning": meaning, "source": "aistudio"})
        return result or self._parse_names(text)

    def _parse_names(self, text: str):
        names = []
        import re

        for line in text.strip().split("\n"):
            line = line.strip()
            if not self._is_candidate_line(line):
                continue
            patterns = [
                r"\d+\.?\s*姓名[：:]?\s*([\u4e00-\u9fa5a-zA-Z]+)[\s\-—–]+(.+)",
                r"\d+\.?\s*([\u4e00-\u9fa5a-zA-Z]+)[\s\-—–]+(.+)",
            ]
            for pattern in patterns:
                match = re.search(pattern, line)
                if not match:
                    continue
                name, meaning = match.group(1).strip(), match.group(2).strip()
                if self._is_valid_name(name) and self._is_valid_meaning(meaning):
                    names.append({"name": name, "meaning": meaning, "source": "aistudio"})
                break
        return names

    def _is_candidate_line(self, line: str) -> bool:
        if not line:
            return False
        bad_tokens = ["例如", "示例", "参考", "格式", "输出", "要求", "System", "system", "提示", "说明"]
        return not any(token in line for token in bad_tokens)

    def _is_valid_name(self, name: str) -> bool:
        import re

        if not name or name in ["例如", "示例", "参考"]:
            return False
        if len(name) < 2 or len(name) > 10:
            return False
        return bool(re.search(r"[\u4e00-\u9fa5]", name))

    def _is_valid_meaning(self, meaning: str) -> bool:
        if not meaning:
            return False
        bad_tokens = ["根据角色描述生成", "示例", "例如", "参考", "格式"]
        if any(token in meaning for token in bad_tokens):
            return False
        return len(meaning) >= 2


register_adapter("aistudio", lambda cfg: AistudioAdapter(cfg))
