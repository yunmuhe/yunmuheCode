"""
API适配器基类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import requests
import json
import time

# 延迟导入logger，避免循环导入
def get_logger(name):
    """获取日志记录器"""
    try:
        from ...utils.logger import get_logger as _get_logger
        return _get_logger(name)
    except ImportError:
        import logging
        return logging.getLogger(name)

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

class APIException(Exception):
    """API异常"""
    pass
