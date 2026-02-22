"""
API适配器基类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import re
import requests
import json
import time
from ...utils.logging_helper import get_logger

logger = get_logger(__name__)

class BaseAPIAdapter(ABC):
    """API适配器基类"""

    def __init__(self, config):
        self.config = config
        self.name = config.name
        self.base_url = config.base_url
        self.api_key = config.api_key
        self.enabled = config.enabled

    @abstractmethod
    def generate_names(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """生成姓名"""
        pass

    def list_models(self) -> List[Dict[str, Any]]:
        """
        获取平台可用的模型列表

        Returns:
            List[Dict]: 模型列表，每个模型包含:
                - id: 模型ID
                - name: 模型显示名称
                - description: 模型描述（可选）
                - capabilities: 模型能力标签（可选）
        """
        # 默认实现：返回配置中的默认模型
        default_model = getattr(self.config, 'model', None)
        if default_model:
            return [{
                'id': default_model,
                'name': default_model,
                'description': f'{self.name}默认模型',
                'is_default': True
            }]
        return []

    def _make_request(self, endpoint: str, data: Dict[str, Any],
                     timeout: int = 30, method: str = 'POST') -> Dict[str, Any]:
        """发送HTTP请求"""
        url = f"{self.base_url}/{endpoint}"
        headers = self.config.get_headers()

        try:
            logger.info(f"发送请求到 {self.name}: {url}")
            if method.upper() == 'GET':
                response = requests.get(
                    url,
                    headers=headers,
                    timeout=timeout
                )
            else:
                response = requests.post(
                    url,
                    headers=headers,
                    json=data,
                    timeout=timeout
                )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"{self.name} API请求失败: {str(e)}")
            raise APIException(f"{self.name} API请求失败: {str(e)}")

    def is_available(self) -> bool:
        """检查API是否可用"""
        return self.enabled and bool(self.api_key)

    def _parse_names(self, text: str) -> List[Dict[str, str]]:
        """
        通用姓名解析方法

        支持以下格式：
        - 数字. 姓名：xxx - 含义
        - 数字. xxx：含义
        - 数字. xxx - 含义（dash 分隔）
        - 姓名：xxx - 含义
        - xxx：含义

        子类可重写此方法以实现自定义解析逻辑。

        Returns:
            解析出的姓名列表
        """
        names = []
        lines = text.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 策略1：冒号分隔
            if '：' in line or ':' in line:
                try:
                    separator = '：' if '：' in line else ':'
                    parts = line.split(separator, 1)

                    if len(parts) < 2:
                        continue

                    name_part = parts[0].strip()
                    meaning_part = parts[1].strip()

                    name = self._clean_name_prefix(name_part)

                    if name and meaning_part and 2 <= len(name) <= 10:
                        names.append({
                            'name': name,
                            'meaning': meaning_part,
                            'source': self.name,
                        })
                        continue
                except Exception:
                    pass

            # 策略2：dash 分隔（如 "1. 苏映雪 - 寓意如映雪般纯净"）
            dash_match = re.search(r'^(.+?)\s*[-–—]\s*(.+)$', line)
            if dash_match:
                try:
                    name_part = dash_match.group(1).strip()
                    meaning_part = dash_match.group(2).strip()

                    name = self._clean_name_prefix(name_part)

                    if name and meaning_part and 2 <= len(name) <= 10:
                        names.append({
                            'name': name,
                            'meaning': meaning_part,
                            'source': self.name,
                        })
                except Exception:
                    pass

        return names

    @staticmethod
    def _clean_name_prefix(raw: str) -> str:
        """清理姓名前缀（序号、'姓名'标签、冒号等）"""
        name = raw.strip()
        # 先剥离序号（如 "1." "2、" "3)" "4）"）
        name = re.sub(r'^\d+[.、)）]\s*', '', name).strip()
        # 再剥离"姓名"前缀
        if name.startswith('姓名'):
            name = name[2:].strip()
        # 清理残余冒号
        name = name.replace('：', '').replace(':', '').strip()
        return name

class APIException(Exception):
    """API异常"""
    pass
