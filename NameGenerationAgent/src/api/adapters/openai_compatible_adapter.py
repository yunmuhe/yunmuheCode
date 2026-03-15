from typing import Any, Dict, Iterable, List, Optional

from .base_adapter import APIException, BaseAPIAdapter
from ...utils.logging_helper import get_logger

logger = get_logger(__name__)


class OpenAICompatibleAdapter(BaseAPIAdapter):
    system_prompt = "你是一个专业的姓名生成专家。"
    default_temperature = 0.7

    def __init__(self, config):
        super().__init__(config)
        self.client = self._create_client()

    def _create_client(self):
        try:
            from openai import OpenAI
        except Exception as exc:
            raise APIException(f"{self.name} OpenAI客户端导入失败: {exc}") from exc

        try:
            return OpenAI(api_key=self.api_key, base_url=self.base_url)
        except Exception as exc:
            raise APIException(f"{self.name} OpenAI客户端初始化失败: {exc}") from exc

    def generate_names(self, prompt: str, **kwargs) -> Dict[str, Any]:
        if not self.is_available():
            raise APIException(f"{self.name} API未配置或不可用")

        request_kwargs = dict(kwargs)
        model = request_kwargs.pop("model", None) or getattr(self.config, "model", "")

        try:
            final_model, response = self._request_with_fallback(prompt, model, **request_kwargs)
            stream = self._resolve_stream(request_kwargs)
            generated_text = self._collect_response_text(response, stream=stream)
            names = self._parse_generated_text(generated_text)
            return {
                "success": True,
                "names": names,
                "raw_response": generated_text,
                "api_name": self.name,
                "model": final_model,
                "stream": stream,
            }
        except APIException:
            raise
        except Exception as exc:
            logger.error(f"{self.name} API调用失败: {exc}")
            raise APIException(f"{self.name} API调用失败: {exc}") from exc

    def _request_with_fallback(self, prompt: str, model: str, **kwargs):
        try:
            return model, self._request_completion(prompt, model, **kwargs)
        except Exception as exc:
            if not self._should_fallback(str(exc)):
                raise APIException(f"{self.name} API调用失败: {exc}") from exc

            for fallback_model in self._fallback_models():
                try:
                    return fallback_model, self._request_completion(
                        prompt, fallback_model, **kwargs
                    )
                except Exception:
                    continue
            raise APIException(f"{self.name} API调用失败: {exc}") from exc

    def _request_completion(self, prompt: str, model: str, **kwargs):
        params = self._build_completion_params(prompt, model, **kwargs)
        return self.client.chat.completions.create(**params)

    def _build_completion_params(
        self, prompt: str, model: str, **kwargs
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "model": model,
            "messages": self._build_messages(prompt),
            "stream": self._resolve_stream(kwargs),
            "max_tokens": kwargs.get(
                "max_tokens", getattr(self.config, "max_tokens", 2000)
            ),
            "temperature": kwargs.get("temperature", self.default_temperature),
        }
        top_p = kwargs.get("top_p")
        if top_p is not None:
            params["top_p"] = top_p
        params.update(self._provider_completion_params(**kwargs))
        return params

    def _build_messages(self, prompt: str) -> List[Dict[str, str]]:
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt},
        ]

    def _resolve_stream(self, kwargs: Dict[str, Any]) -> bool:
        return bool(kwargs.get("stream", getattr(self.config, "stream", False)))

    def _provider_completion_params(self, **kwargs) -> Dict[str, Any]:
        return {}

    def _should_fallback(self, error_message: str) -> bool:
        return False

    def _fallback_models(self) -> List[str]:
        return list(getattr(self.config, "fallback_models", []) or [])

    def _collect_response_text(self, response: Any, stream: bool) -> str:
        if stream:
            chunks = []
            for chunk in response:
                text = self._extract_stream_chunk_text(chunk)
                if text:
                    chunks.append(text)
            result = "".join(chunks)
        else:
            choices = getattr(response, "choices", None) or []
            if not choices:
                raise APIException(f"{self.name} API响应中没有choices数据")
            message = getattr(choices[0], "message", None)
            result = getattr(message, "content", None) if message else None

        if not result:
            raise APIException(f"{self.name} API返回空内容")
        return result

    def _extract_stream_chunk_text(self, chunk: Any) -> str:
        choices = getattr(chunk, "choices", None) or []
        if not choices:
            return ""
        delta = getattr(choices[0], "delta", None)
        return getattr(delta, "content", None) or ""

    def _parse_generated_text(self, text: str):
        return self._parse_names(text)
