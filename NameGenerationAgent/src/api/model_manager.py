"""
模型管理器 - 负责获取和缓存各平台的可用模型列表
"""
from typing import Dict, List, Any, Optional
import time
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ModelManager:
    """模型管理器 - 管理所有平台的模型列表"""

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = 3600  # 缓存1小时
        self._last_update: Dict[str, float] = {}

    def get_models_for_api(self, api_name: str, adapter) -> List[Dict[str, Any]]:
        """
        获取指定API平台的模型列表（带缓存）

        Args:
            api_name: API平台名称
            adapter: API适配器实例

        Returns:
            List[Dict]: 模型列表
        """
        # 检查缓存是否有效
        if self._is_cache_valid(api_name):
            logger.debug(f"从缓存返回 {api_name} 的模型列表")
            return self._cache[api_name]['models']

        # 缓存失效或不存在，重新获取
        try:
            logger.info(f"正在获取 {api_name} 的模型列表...")
            models = adapter.list_models()

            # 更新缓存
            self._cache[api_name] = {
                'models': models,
                'timestamp': time.time()
            }
            self._last_update[api_name] = time.time()

            logger.info(f"成功获取 {api_name} 的 {len(models)} 个模型")
            return models

        except Exception as e:
            logger.error(f"获取 {api_name} 模型列表失败: {str(e)}")
            # 如果有旧缓存，返回旧缓存
            if api_name in self._cache:
                logger.warning(f"返回 {api_name} 的过期缓存")
                return self._cache[api_name]['models']
            return []

    def get_all_models(self, adapters: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取所有可用API平台的模型列表

        Args:
            adapters: 所有API适配器的字典

        Returns:
            Dict: 每个平台的模型列表
        """
        all_models = {}

        for api_name, adapter in adapters.items():
            if not adapter.is_available():
                logger.debug(f"跳过未启用的API: {api_name}")
                continue

            models = self.get_models_for_api(api_name, adapter)
            if models:
                all_models[api_name] = models

        return all_models

    def clear_cache(self, api_name: Optional[str] = None):
        """
        清除模型缓存

        Args:
            api_name: 指定API名称，如果为None则清除所有缓存
        """
        if api_name:
            if api_name in self._cache:
                del self._cache[api_name]
                del self._last_update[api_name]
                logger.info(f"已清除 {api_name} 的模型缓存")
        else:
            self._cache.clear()
            self._last_update.clear()
            logger.info("已清除所有模型缓存")

    def _is_cache_valid(self, api_name: str) -> bool:
        """
        检查缓存是否有效

        Args:
            api_name: API平台名称

        Returns:
            bool: 缓存是否有效
        """
        if api_name not in self._cache:
            return False

        last_update = self._last_update.get(api_name, 0)
        return (time.time() - last_update) < self._cache_ttl

    def set_cache_ttl(self, ttl: int):
        """
        设置缓存过期时间

        Args:
            ttl: 缓存时间（秒）
        """
        self._cache_ttl = ttl
        logger.info(f"模型缓存TTL已设置为 {ttl} 秒")


# 全局模型管理器实例
model_manager = ModelManager()
