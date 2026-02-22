"""
统一API客户端
"""
from typing import Dict, Any, List, Optional
import time
import random
import traceback
from .adapters.base_adapter import BaseAPIAdapter, APIException
from .router_strategy import get_router_strategy

# 延迟导入，避免循环导入问题
def get_api_manager():
    """获取API管理器"""
    try:
        # 尝试多种导入路径
        try:
            from ...config.api_config import api_manager
            return api_manager
        except ImportError:
            try:
                from config.api_config import api_manager
                return api_manager
            except ImportError:
                # 手动创建API管理器
                from config.api_config import PaiouConfig, APIManager
                manager = APIManager()
                return manager
    except ImportError:
        # 返回默认配置
        class DefaultAPIManager:
            def __init__(self):
                self.apis = {}
            
            def get_available_apis(self):
                return []
        
        return DefaultAPIManager()

def get_logger(name):
    """获取日志记录器"""
    try:
        from ...utils.logger import get_logger as _get_logger
        return _get_logger(name)
    except ImportError:
        import logging
        return logging.getLogger(name)

def get_settings():
    try:
        from ...config.settings import Config as _Config
        return _Config
    except ImportError:
        class _Default:
            ROUTER_STRATEGY = 'priority'
            ROUTER_WEIGHTS = ''
        return _Default

def get_cache_manager():
    """获取缓存管理器"""
    try:
        from ...utils.cache_manager import CacheManager
        return CacheManager()
    except ImportError:
        # 返回简单的缓存管理器
        class SimpleCacheManager:
            def __init__(self):
                self.cache = {}
                self.hits = 0
                self.misses = 0
            
            def get(self, key):
                if key in self.cache:
                    self.hits += 1
                    return self.cache[key]
                else:
                    self.misses += 1
                    return None
            
            def set(self, key, value):
                self.cache[key] = value
            
            def get_stats(self):
                """获取缓存统计信息"""
                total_requests = self.hits + self.misses
                hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
                
                return {
                    'cache_size': len(self.cache),
                    'hits': self.hits,
                    'misses': self.misses,
                    'hit_rate': round(hit_rate, 2),
                    'total_requests': total_requests
                }
            
            def clear(self):
                """清空缓存"""
                self.cache.clear()
                self.hits = 0
                self.misses = 0
        
        return SimpleCacheManager()

logger = get_logger(__name__)

class UnifiedAPIClient:
    """统一API客户端"""
    
    def __init__(self):
        self.adapters = {}
        self.cache_manager = get_cache_manager()
        self._initialize_adapters()
        self._initialize_router()
    
    def _initialize_adapters(self):
        """初始化API适配器"""
        try:
            api_manager = get_api_manager()
            from .adapters import build_adapters
            self.adapters = build_adapters(api_manager.apis)
            logger.info(f"已初始化 {len(self.adapters)} 个API适配器: {list(self.adapters.keys())}")
        except Exception as e:
            logger.error(f"初始化适配器失败: {str(e)}")
            logger.error("详细错误堆栈:")
            traceback.print_exc()
    
    def _initialize_router(self):
        settings = get_settings()
        strategy_name = getattr(settings, 'ROUTER_STRATEGY', 'priority')
        weights_raw = getattr(settings, 'ROUTER_WEIGHTS', '')
        default_order = ['aistudio', 'aliyun', 'siliconflow', 'paiou', 'openai', 'gemini']
        try:
            self.router_strategy = get_router_strategy(strategy_name, default_order, weights_raw)
            logger.info(f"路由策略已启用: {strategy_name}")
        except Exception as e:
            self.router_strategy = get_router_strategy('priority', default_order, '')
            logger.warning(f"路由策略初始化失败，使用默认策略: {str(e)}")
    
    def generate_names(self, prompt: str, count: int = 5, 
                      preferred_api: Optional[str] = None,
                      use_cache: bool = True,
                      use_mock_on_failure: bool = True,
                      **kwargs) -> Dict[str, Any]:
        """生成姓名"""
        
        # 检查缓存
        if use_cache:
            cache_key = self._generate_cache_key(prompt, count, kwargs)
            cached_result = self.cache_manager.get(cache_key)
            if cached_result:
                logger.info("从缓存中获取结果")
                return cached_result
        
        # 获取API优先级列表
        api_priority = self._get_api_priority(preferred_api, kwargs)
        
        # 尝试调用API
        last_error = None
        for api_name in api_priority:
            if api_name not in self.adapters:
                continue
            
            try:
                logger.info(f"尝试使用 {api_name} API生成姓名")
                result = self.adapters[api_name].generate_names(prompt, **kwargs)
                
                # 限制返回的姓名数量
                if 'names' in result and len(result['names']) > count:
                    result['names'] = result['names'][:count]
                
                # 缓存结果
                if use_cache:
                    self.cache_manager.set(cache_key, result)
                
                logger.info(f"成功使用 {api_name} API生成 {len(result.get('names', []))} 个姓名")
                return result
                
            except APIException as e:
                logger.warning(f"{api_name} API调用失败: {str(e)}")
                last_error = e
                continue
            except Exception as e:
                logger.error(f"{api_name} API调用出现未知错误: {str(e)}")
                last_error = e
                continue
        
        # 所有API都失败
        if use_mock_on_failure:
            logger.info("所有API调用失败，使用模拟数据")
            mock_result = self._generate_mock_names(prompt, count)
            
            # 缓存模拟结果
            if use_cache:
                self.cache_manager.set(cache_key, mock_result)
            
            return mock_result
        else:
            # 不使用模拟数据，返回错误
            error_msg = f"所有API调用失败，最后错误: {str(last_error)}" if last_error else "所有API调用失败"
            logger.error(error_msg)
            
            return {
                'success': False,
                'error': error_msg,
                'names': [],
                'api_name': 'none'
            }
    
    def _get_api_priority(self, preferred_api: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> List[str]:
        try:
            return self.router_strategy.get_priority(self.adapters, preferred_api, context)
        except Exception:
            available_apis = list(self.adapters.keys())
            if not available_apis:
                return []
            if preferred_api and preferred_api in available_apis:
                priority = [preferred_api]
                priority.extend([api for api in available_apis if api != preferred_api])
                return priority
            default_priority = ['aistudio', 'aliyun', 'siliconflow', 'paiou', 'openai', 'gemini']
            result: List[str] = []
            for api in default_priority:
                if api in available_apis:
                    result.append(api)
            for api in available_apis:
                if api not in result:
                    result.append(api)
            return result
    
    def _generate_mock_names(self, prompt: str, count: int) -> Dict[str, Any]:
        """生成模拟姓名数据"""
        import random
        import time
        
        # 根据提示词生成相关的模拟姓名
        mock_names_db = {
            '战士': [
                {'name': '张勇', 'meaning': '勇敢坚强，意志坚定'},
                {'name': '李刚', 'meaning': '刚毅不屈，勇往直前'},
                {'name': '王强', 'meaning': '力量强大，无所畏惧'},
                {'name': '赵武', 'meaning': '武艺高强，战无不胜'},
                {'name': '陈军', 'meaning': '军人之风，纪律严明'}
            ],
            '学者': [
                {'name': '李智', 'meaning': '智慧超群，学识渊博'},
                {'name': '王博', 'meaning': '博学多才，见多识广'},
                {'name': '张文', 'meaning': '文采斐然，才华横溢'},
                {'name': '陈学', 'meaning': '学富五车，知识渊博'},
                {'name': '刘思', 'meaning': '思维敏捷，逻辑清晰'}
            ],
            '公主': [
                {'name': '李美', 'meaning': '美丽动人，气质优雅'},
                {'name': '王雅', 'meaning': '雅致高贵，风度翩翩'},
                {'name': '张柔', 'meaning': '温柔如水，心地善良'},
                {'name': '陈雪', 'meaning': '冰雪聪明，纯洁无瑕'},
                {'name': '刘梦', 'meaning': '梦幻般美丽，如诗如画'}
            ],
            'default': [
                {'name': '张三', 'meaning': '寓意勇敢坚强'},
                {'name': '李四', 'meaning': '寓意智慧聪慧'},
                {'name': '王五', 'meaning': '寓意正直善良'},
                {'name': '赵六', 'meaning': '寓意温和友善'},
                {'name': '钱七', 'meaning': '寓意聪明机智'},
                {'name': '孙八', 'meaning': '寓意勤奋努力'},
                {'name': '周九', 'meaning': '寓意诚实可靠'},
                {'name': '吴十', 'meaning': '寓意乐观开朗'}
            ]
        }
        
        # 根据提示词选择相应的姓名库
        selected_names = mock_names_db['default']
        for keyword, names in mock_names_db.items():
            if keyword in prompt:
                selected_names = names
                break
        
        # 随机选择指定数量的姓名
        selected_count = min(count, len(selected_names))
        chosen_names = random.sample(selected_names, selected_count)
        
        return {
            'success': True,
            'names': chosen_names,
            'total_generated': len(chosen_names),
            'api_name': 'mock',
            'model': 'mock_model',
            'raw_response': f"模拟生成 {len(chosen_names)} 个姓名",
            'generated_at': time.time()
        }
    
    def _generate_cache_key(self, prompt: str, count: int, kwargs: Dict[str, Any]) -> str:
        """生成缓存键"""
        import hashlib
        
        # 构建缓存键的组成部分
        key_parts = [
            prompt,
            str(count),
            str(sorted(kwargs.items()))
        ]
        
        key_string = '|'.join(key_parts)
        return hashlib.md5(key_string.encode('utf-8')).hexdigest()
    
    def get_available_apis(self) -> List[str]:
        """获取可用的API列表"""
        return list(self.adapters.keys())
    
    def get_api_status(self) -> Dict[str, Dict[str, Any]]:
        """获取API状态信息"""
        status = {}
        
        for name, adapter in self.adapters.items():
            status[name] = {
                'enabled': adapter.is_available(),
                'name': adapter.name,
                'base_url': adapter.base_url
            }
        
        return status
    
    def test_api_connection(self, api_name: str) -> Dict[str, Any]:
        """测试API连接"""
        if api_name not in self.adapters:
            return {
                'success': False,
                'error': f'API {api_name} 不存在'
            }
        
        try:
            # 使用简单的测试提示词
            test_prompt = "请生成1个测试姓名"
            result = self.adapters[api_name].generate_names(test_prompt, max_tokens=100)
            
            return {
                'success': True,
                'message': f'{api_name} API连接正常',
                'test_result': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'{api_name} API连接失败: {str(e)}'
            }

# 全局统一API客户端实例
unified_client = UnifiedAPIClient()
