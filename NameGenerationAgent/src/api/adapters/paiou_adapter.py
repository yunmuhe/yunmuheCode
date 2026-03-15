from typing import Any, Dict, List

from . import register_adapter
from .openai_compatible_adapter import OpenAICompatibleAdapter
from ...utils.logging_helper import get_logger

logger = get_logger(__name__)


class PaiouAdapter(OpenAICompatibleAdapter):
    system_prompt = """你是一个专业的姓名生成专家，擅长根据角色描述生成具有文化内涵和美感的姓名。

你的任务是：
1. 根据用户提供的角色描述生成指定数量的姓名
2. 严格按照指定的格式输出结果
3. 确保每个姓名都有明确的寓意解释
4. 不添加任何额外的解释或说明文字

输出格式要求：
- 每行格式：数字. 姓名：{姓名} - {寓意}
- 严格按照要求的数量生成
- 不要添加任何前缀或后缀文字"""
    default_temperature = 0.3

    def list_models(self) -> List[Dict[str, Any]]:
        if not self.is_available():
            return []

        try:
            response = self._make_request("models", {}, method="GET", timeout=10)
        except Exception as exc:
            logger.warning(f"获取派欧云模型列表异常: {exc}")
            return []

        models = []
        for model_data in response.get("data", []):
            model_id = model_data.get("id", "")
            models.append(
                {
                    "id": model_id,
                    "name": model_id.split("/")[-1] if "/" in model_id else model_id,
                    "description": f"派欧云 {model_id}",
                    "is_default": model_id == getattr(self.config, "model", ""),
                    "owned_by": model_data.get("owned_by", ""),
                }
            )
        return models

    def _provider_completion_params(self, **kwargs) -> Dict[str, Any]:
        return {
            "top_p": kwargs.get("top_p", 0.8),
            "response_format": getattr(self.config, "response_format", None),
            "extra_body": {"source": "paiou"},
        }

    def _resolve_stream(self, kwargs: Dict[str, Any]) -> bool:
        return bool(kwargs.get("stream", getattr(self.config, "stream", True)))

    def _parse_generated_text(self, text: str):
        return self._parse_names(text)

    def _parse_names(self, text: str) -> List[Dict[str, str]]:
        names = []
        lines = text.strip().split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            import re

            patterns = [
                r"(\d+)\.?\s*姓名[：:]\s*(.+?)\s*[-—–]\s*(.+)",
                r"(\d+)\.?\s*(.+?)\s*[-—–]\s*(.+)",
                r"姓名[：:]\s*(.+?)\s*[-—–]\s*(.+)",
                r"(.+?)\s*[-—–]\s*(.+)",
            ]

            for pattern in patterns:
                match = re.search(pattern, line)
                if not match:
                    continue
                if len(match.groups()) == 3:
                    name = match.group(2).strip()
                    meaning = match.group(3).strip()
                else:
                    name = match.group(1).strip()
                    meaning = match.group(2).strip()
                name = re.sub(r"^\d+\.?\s*", "", name)
                name = re.sub(r"^姓名[：:]\s*", "", name).strip()
                if name and meaning and len(name) >= 2:
                    names.append({"name": name, "meaning": meaning, "source": "paiou"})
                break
        return names


register_adapter("paiou", lambda cfg: PaiouAdapter(cfg))
