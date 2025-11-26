"""
缓存管理工具
"""
import json
import os
import time
from typing import Any, Optional, Dict
from ..config.settings import Config
from .logger import get_logger

logger = get_logger(__name__)

class CacheManager:
    """缓存管理器"""
    
    def __init__(self, cache_file: str = None):
        self.cache_file = cache_file or os.path.join(Config.CACHE_DIR, 'cache.json')
        self.cache_data = {}
        self.max_size = Config.MAX_CACHE_SIZE
        self.ttl = Config.CACHE_TTL
        
        # 确保缓存目录存在
        Config.ensure_directories()
        
        # 加载现有缓存
        self._load_cache()
    
    def _load_cache(self):
        """加载缓存数据"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache_data = json.load(f)
                logger.info(f"加载缓存数据，共 {len(self.cache_data)} 条记录")
            else:
                self.cache_data = {}
                logger.info("缓存文件不存在，创建新缓存")
        except Exception as e:
            logger.error(f"加载缓存失败: {str(e)}")
            self.cache_data = {}
    
    def _save_cache(self):
        """保存缓存数据"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_data, f, ensure_ascii=False, indent=2)
            logger.debug("缓存数据已保存")
        except Exception as e:
            logger.error(f"保存缓存失败: {str(e)}")
    
    def _is_expired(self, timestamp: float) -> bool:
        """检查缓存是否过期"""
        return time.time() - timestamp > self.ttl
    
    def _cleanup_expired(self):
        """清理过期的缓存条目"""
        current_time = time.time()
        expired_keys = []
        
        for key, data in self.cache_data.items():
            if isinstance(data, dict) and 'timestamp' in data:
                if current_time - data['timestamp'] > self.ttl:
                    expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache_data[key]
        
        if expired_keys:
            logger.info(f"清理了 {len(expired_keys)} 个过期缓存条目")
    
    def _evict_oldest(self):
        """淘汰最旧的缓存条目"""
        if not self.cache_data:
            return
        
        # 找到最旧的条目
        oldest_key = min(
            self.cache_data.keys(),
            key=lambda k: self.cache_data[k].get('timestamp', 0)
        )
        
        del self.cache_data[oldest_key]
        logger.debug(f"淘汰最旧的缓存条目: {oldest_key}")
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        if key not in self.cache_data:
            return None
        
        data = self.cache_data[key]
        
        # 检查是否过期
        if isinstance(data, dict) and 'timestamp' in data:
            if self._is_expired(data['timestamp']):
                del self.cache_data[key]
                logger.debug(f"缓存条目 {key} 已过期，已删除")
                return None
        
        logger.debug(f"从缓存获取数据: {key}")
        return data.get('value') if isinstance(data, dict) else data
    
    def set(self, key: str, value: Any):
        """设置缓存数据"""
        # 清理过期条目
        self._cleanup_expired()
        
        # 如果缓存已满，淘汰最旧的条目
        if len(self.cache_data) >= self.max_size:
            self._evict_oldest()
        
        # 存储数据
        self.cache_data[key] = {
            'value': value,
            'timestamp': time.time()
        }
        
        logger.debug(f"缓存数据: {key}")
        
        # 定期保存缓存
        if len(self.cache_data) % 10 == 0:
            self._save_cache()
    
    def delete(self, key: str) -> bool:
        """删除缓存数据"""
        if key in self.cache_data:
            del self.cache_data[key]
            logger.debug(f"删除缓存条目: {key}")
            return True
        return False
    
    def clear(self):
        """清空所有缓存"""
        self.cache_data.clear()
        self._save_cache()
        logger.info("已清空所有缓存")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        current_time = time.time()
        total_entries = len(self.cache_data)
        expired_entries = 0
        
        for data in self.cache_data.values():
            if isinstance(data, dict) and 'timestamp' in data:
                if current_time - data['timestamp'] > self.ttl:
                    expired_entries += 1
        
        return {
            'total_entries': total_entries,
            'expired_entries': expired_entries,
            'active_entries': total_entries - expired_entries,
            'max_size': self.max_size,
            'ttl': self.ttl,
            'cache_file': self.cache_file
        }
    
    def __del__(self):
        """析构函数，保存缓存"""
        try:
            self._save_cache()
        except:
            pass
