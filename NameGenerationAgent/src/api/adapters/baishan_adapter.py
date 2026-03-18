from typing import Any, Dict, List

from . import register_adapter
from .openai_compatible_adapter import OpenAICompatibleAdapter
from ...utils.logger import get_logger

logger = get_logger(__name__)


class BaishanAdapter(OpenAICompatibleAdapter):
    def list_models(self) -> List[Dict[str, Any]]:
        if not self.is_available():
            return []

        try:
            response = self._make_request("models", {}, method="GET", timeout=10)
        except Exception as exc:
            logger.warning(f"获取白山智算模型列表异常: {exc}")
            return []

        models = []
        for model_data in response.get("data", []):
            model_id = model_data.get("id", "")
            if not model_id:
                continue
            models.append(
                {
                    "id": model_id,
                    "name": model_id.split("/")[-1] if "/" in model_id else model_id,
                    "description": f"白山智算 {model_id}",
                    "is_default": model_id == self.config.model,
                    "owned_by": model_data.get("owned_by", "baishan"),
                }
            )
        return models


register_adapter("baishan", lambda cfg: BaishanAdapter(cfg))
