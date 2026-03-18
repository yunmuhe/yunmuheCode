"""
API 适配器基类。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
import re

import requests

from ...utils.logging_helper import get_logger

logger = get_logger(__name__)


class BaseAPIAdapter(ABC):
    """API 适配器基类。"""

    def __init__(self, config):
        self.config = config
        self.name = config.name
        self.base_url = config.base_url
        self.api_key = config.api_key
        self.enabled = config.enabled

    @abstractmethod
    def generate_names(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """生成姓名。"""

    def list_models(self) -> List[Dict[str, Any]]:
        """返回默认模型列表。"""
        default_model = getattr(self.config, "model", None)
        if not default_model:
            return []
        return [
            {
                "id": default_model,
                "name": default_model,
                "description": f"{self.name}默认模型",
                "is_default": True,
            }
        ]

    def _make_request(
        self, endpoint: str, data: Dict[str, Any], timeout: int = 30, method: str = "POST"
    ) -> Dict[str, Any]:
        """发送 HTTP 请求。timeout 为读取超时，连接超时固定 10 秒。"""
        url = f"{self.base_url}/{endpoint}"
        headers = self.config.get_headers()
        # (连接超时, 读取超时) 分开设置
        req_timeout = (10, timeout)

        try:
            logger.info(f"发送请求到 {self.name}: {url}")
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=req_timeout)
            else:
                response = requests.post(url, headers=headers, json=data, timeout=req_timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as exc:
            logger.error(f"{self.name} API请求失败: {exc}")
            raise APIException(f"{self.name} API请求失败: {exc}") from exc

    def is_available(self) -> bool:
        """检查 API 是否可用。"""
        return self.enabled and bool(self.api_key)

    def _parse_names(self, text: str) -> List[Dict[str, str]]:
        """
        通用姓名解析方法。

        支持：
        - `1. 姓名：寓意`
        - `姓名：...` + `寓意：...`
        - `1. 姓名 - 寓意`
        """
        names: List[Dict[str, str]] = []
        pending_name = ""

        for raw_line in text.strip().split("\n"):
            line = raw_line.strip()
            if not line:
                continue

            labeled = self._parse_labeled_line(line)
            if labeled:
                label, value = labeled
                if label == "name":
                    # 处理 "姓名：xxx - 寓意：yyy" 同行格式
                    dash_match = re.search(r"^(.+?)\s*[-—–]\s*(?:寓意[：:])?(.+)$", value)
                    if dash_match:
                        name = self._clean_name_prefix(dash_match.group(1).strip())
                        meaning = self._clean_text(dash_match.group(2).strip())
                        if name and meaning and 2 <= len(name) <= 10:
                            names.append({"name": name, "meaning": meaning, "source": self.name})
                            continue
                    pending_name = value
                    continue
                if label == "meaning" and pending_name:
                    names.append(
                        {
                            "name": pending_name,
                            "meaning": value,
                            "source": self.name,
                        }
                    )
                    pending_name = ""
                    continue

            colon_match = self._split_line(line)
            if colon_match:
                name_part, meaning_part = colon_match
                name = self._clean_name_prefix(name_part)
                if name and meaning_part and 2 <= len(name) <= 10:
                    names.append(
                        {
                            "name": name,
                            "meaning": meaning_part,
                            "source": self.name,
                        }
                    )
                    continue

            dash_match = re.search(r"^(.+?)\s*[-—–]\s*(.+)$", line)
            if dash_match:
                name = self._clean_name_prefix(dash_match.group(1).strip())
                meaning = self._clean_text(dash_match.group(2))
                if name and meaning and 2 <= len(name) <= 10:
                    names.append(
                        {
                            "name": name,
                            "meaning": meaning,
                            "source": self.name,
                        }
                    )

        return names

    @classmethod
    def _split_line(cls, line: str):
        cleaned = cls._clean_text(line)
        if "：" in cleaned:
            parts = cleaned.split("：", 1)
        elif ":" in cleaned:
            parts = cleaned.split(":", 1)
        else:
            return None
        if len(parts) < 2:
            return None
        return parts[0].strip(), parts[1].strip()

    @classmethod
    def _clean_name_prefix(cls, raw: str) -> str:
        """清理姓名前缀、编号、标签和 Markdown 标记。"""
        name = cls._clean_text(raw)
        name = re.sub(r"^\d+[.\u3001\)\s]*", "", name).strip()
        lowered = name.lower()

        for prefix in ("姓名", "名字"):
            if name.startswith(prefix):
                name = name[len(prefix) :].strip()
        if lowered.startswith("name"):
            name = name[4:].strip()

        return name.replace("：", "").replace(":", "").strip()

    @staticmethod
    def _clean_text(value: str) -> str:
        return value.replace("**", "").replace("*", "").strip()

    @classmethod
    def _parse_labeled_line(cls, line: str):
        parts = cls._split_line(line)
        if not parts:
            return None

        label, value = parts
        normalized = re.sub(r"^\d+[.\u3001\)\s]*", "", label).strip().lower()

        if normalized in {"姓名", "名字", "name"}:
            return "name", value
        if normalized in {"寓意", "含义", "解释", "meaning"}:
            return "meaning", value
        return None


class APIException(Exception):
    """API 异常。"""

