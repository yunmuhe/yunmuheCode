from typing import Any, Dict, List

from . import register_adapter
from .openai_compatible_adapter import OpenAICompatibleAdapter
from ...utils.logger import get_logger

logger = get_logger(__name__)


class SiliconFlowAdapter(OpenAICompatibleAdapter):
    system_prompt = "你是一个有用的助手"

    def list_models(self) -> List[Dict[str, Any]]:
        if not self.is_available():
            return []

        try:
            response = self._make_request("models", {}, method="GET", timeout=10)
        except Exception as exc:
            logger.warning(f"获取硅基流动模型列表异常: {exc}")
            return []

        models = []
        for model_data in response.get("data", []):
            model_id = model_data.get("id", "")
            if "chat" in model_data.get("object", "").lower() or any(
                keyword in model_id.lower()
                for keyword in ["qwen", "llama", "deepseek", "yi", "mistral", "glm"]
            ):
                models.append(
                    {
                        "id": model_id,
                        "name": model_id.split("/")[-1] if "/" in model_id else model_id,
                        "description": f"硅基流动 {model_id}",
                        "is_default": model_id == self.config.model,
                        "owned_by": model_data.get("owned_by", "siliconflow"),
                    }
                )
        return models

    def _provider_completion_params(self, **kwargs) -> Dict[str, Any]:
        params = super()._provider_completion_params(**kwargs)
        params["top_p"] = kwargs.get("top_p", 0.9)
        return params


register_adapter("siliconflow", lambda cfg: SiliconFlowAdapter(cfg))
