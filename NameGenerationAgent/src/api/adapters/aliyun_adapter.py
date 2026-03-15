"""
阿里云 DashScope 适配器。
"""

from typing import Any, Dict, List
import re

import requests

from . import register_adapter
from .base_adapter import APIException, BaseAPIAdapter
from ...utils.logger import get_logger

logger = get_logger(__name__)


class AliyunAdapter(BaseAPIAdapter):
    """阿里云 DashScope API 适配器。"""

    MODEL_LIST_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/models"
    CHAT_COMPLETIONS_URL = (
        "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    )
    FALLBACK_PATTERNS = [
        r"不支持",
        r"unsupported",
        r"not\s+support",
        r"404",
        r"Model\s+not\s+found",
        r"Invalid\s+model",
        r"AllocationQuota\.FreeTierOnly",
        r"free tier .* exhausted",
    ]

    def list_models(self) -> List[Dict[str, Any]]:
        """获取阿里云兼容模式下可用的模型列表。"""
        if not self.is_available():
            return []

        try:
            resp = requests.get(
                self.MODEL_LIST_URL,
                headers=self.config.get_headers(),
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            logger.warning(f"获取阿里云模型列表异常: {exc}")
            return []

        models = []
        for model_data in data.get("data", []):
            model_id = model_data.get("id", "")
            models.append(
                {
                    "id": model_id,
                    "name": model_id,
                    "description": f"阿里云 {model_id}",
                    "is_default": model_id == self.config.model,
                    "owned_by": model_data.get("owned_by", ""),
                }
            )
        return models

    def generate_names(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """生成姓名，支持动态指定模型和免费额度耗尽时降级。"""
        if not self.is_available():
            raise APIException("阿里云API未配置或不可用")

        model = kwargs.get("model", self.config.model)
        request_data = self._build_request_payload(prompt, **kwargs)

        try:
            response = self._call_with_model(model, request_data)
        except Exception as exc:
            msg = str(exc)
            if self._should_fallback(msg) and getattr(self.config, "fallback_models", []):
                for fallback_model in self.config.fallback_models:
                    try:
                        response = self._call_with_model(fallback_model, request_data)
                        model = fallback_model
                        break
                    except Exception:
                        continue
                else:
                    logger.error(f"阿里云API降级失败: {msg}")
                    raise APIException(f"阿里云API调用失败: {msg}") from exc
            else:
                logger.error(f"阿里云API调用失败: {msg}")
                raise APIException(f"阿里云API调用失败: {msg}") from exc

        generated_text = response["output"]["text"]
        names = self._parse_names(generated_text)

        return {
            "success": True,
            "names": names,
            "raw_response": generated_text,
            "api_name": self.name,
            "model": model,
        }

    def _build_request_payload(self, prompt: str, **kwargs) -> Dict[str, Any]:
        return {
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个专业的姓名生成专家，擅长根据角色描述生成具有文化内涵和美感的姓名。",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 0.9),
        }

    def _call_with_model(
        self, model_name: str, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        payload = dict(request_data)
        payload["model"] = model_name

        try:
            resp = requests.post(
                self.CHAT_COMPLETIONS_URL,
                headers=self.config.get_headers(),
                json=payload,
                timeout=(10, 90),
            )
            resp.raise_for_status()
        except requests.exceptions.RequestException as exc:
            detail = ""
            response = getattr(exc, "response", None)
            if response is not None:
                try:
                    error_payload = response.json()
                    detail = error_payload.get("code") or error_payload.get("message") or ""
                except Exception:
                    detail = response.text
            msg = str(exc)
            if detail:
                msg = f"{msg} - {detail}"
            raise APIException(f"{self.name} API请求失败: {msg}") from exc

        body = resp.json()
        choices = body.get("choices") or []
        if not choices:
            raise APIException("阿里云API响应格式错误")

        message = choices[0].get("message") or {}
        content = message.get("content")
        if not content:
            raise APIException("阿里云API响应格式错误")

        return {
            "choices": choices,
            "output": {"text": content},
        }

    def _should_fallback(self, error_message: str) -> bool:
        return any(
            re.search(pattern, error_message, flags=re.IGNORECASE)
            for pattern in self.FALLBACK_PATTERNS
        )


register_adapter("aliyun", lambda cfg: AliyunAdapter(cfg))
