"""
统一API客户端
"""
from typing import Dict, Any, List, Optional
import time
import random
import traceback
from .adapters.base_adapter import BaseAPIAdapter, APIException

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
    
    def _initialize_adapters(self):
        """初始化API适配器"""
        try:
            # 获取API配置
            api_manager = get_api_manager()
            api_configs = api_manager.apis
            
            # 延迟导入适配器
            adapters_to_init = []
            
            # 强制初始化派欧云适配器
            try:
                from .adapters.paiou_adapter import PaiouAdapter
                
                # 检查是否有派欧云配置
                if 'paiou' in api_configs and api_configs['paiou'].enabled:
                    config = api_configs['paiou']
                    adapters_to_init.append(('paiou', PaiouAdapter, config))
                    logger.info("找到派欧云配置，准备初始化")
                else:
                    # 创建默认派欧云配置
                    import os
                    class DefaultPaiouConfig:
                        def __init__(self):
                            self.name = 'paiou'
                            self.base_url = 'https://api.ppinfra.com/openai'
                            self.model = 'deepseek/deepseek-v3-0324'
                            self.max_tokens = 1000
                            self.stream = True
                            self.response_format = {"type": "text"}
                            self.api_key = os.environ.get('PAIOU_API_KEY', 'sk_w4VWR2BAZTrwkilopHVMC65rhkmE0D7gayGEQKzjCi8')
                            self.enabled = bool(self.api_key)
                        
                        def get_headers(self):
                            return {
                                'Content-Type': 'application/json',
                                'Authorization': f'Bearer {self.api_key}'
                            }
                        
                        def get_client_config(self):
                            return {
                                'base_url': self.base_url,
                                'api_key': self.api_key
                            }
                        
                        def get_completion_params(self):
                            return {
                                'model': self.model,
                                'stream': self.stream,
                                'max_tokens': self.max_tokens,
                                'response_format': self.response_format,
                                'extra_body': {}
                            }
                    
                    config = DefaultPaiouConfig()
                    if config.enabled:
                        adapters_to_init.append(('paiou', PaiouAdapter, config))
                        logger.info("使用默认派欧云配置")
                    else:
                        logger.warning("派欧云API密钥未设置")
                        
            except ImportError as e:
                logger.error(f"派欧云适配器导入失败: {str(e)}")
            
            # 在初始化位置导入aistudio适配器
            try:
                logger.info("开始导入Aistudio适配器...")
                from .adapters.aistudio_adapter import AistudioAdapter
                logger.info("Aistudio适配器导入成功")
                
                if 'aistudio' in api_configs and api_configs['aistudio'].enabled:
                    config = api_configs['aistudio']
                    adapters_to_init.append(('aistudio', AistudioAdapter, config))
                    logger.info(f"找到Aistudio配置，准备初始化 (api_key={config.api_key[:20]}...)")
                else:
                    logger.warning(f"Aistudio配置未找到或未启用: api_configs.keys={list(api_configs.keys())}")
            except ImportError as e:
                logger.error(f"Aistudio适配器导入失败: {str(e)}")
                traceback.print_exc()
            except Exception as e:
                logger.error(f"Aistudio适配器检查失败: {str(e)}")
                traceback.print_exc()
            
            # 检查其他适配器
            for api_name in ['aliyun', 'siliconflow', 'baishan', 'baidu']:
                if api_name in api_configs and api_configs[api_name].enabled:
                    try:
                        # 使用绝对导入而不是相对导入
                        module_name = f'src.api.adapters.{api_name}_adapter'
                        adapter_class_name = f'{api_name.title()}Adapter'
                        logger.info(f"尝试导入 {module_name}.{adapter_class_name}...")
                        
                        adapter_module = __import__(module_name, fromlist=[adapter_class_name])
                        adapter_class = getattr(adapter_module, adapter_class_name)
                        adapters_to_init.append((api_name, adapter_class, api_configs[api_name]))
                        logger.info(f"✅ {api_name} 适配器导入成功")
                    except ImportError as e:
                        logger.warning(f"{api_name}适配器导入失败: {str(e)}")
                    except Exception as e:
                        logger.error(f"{api_name}适配器导入异常: {str(e)}")
                        traceback.print_exc()
            
            # 初始化适配器
            for api_name, adapter_class, config in adapters_to_init:
                try:
                    logger.info(f"正在初始化 {api_name} 适配器 (class={adapter_class.__name__})...")
                    self.adapters[api_name] = adapter_class(config)
                    logger.info(f"✅ 成功初始化 {api_name} 适配器")
                except Exception as e:
                    logger.error(f"❌ 初始化 {api_name} 适配器失败: {str(e)}")
                    logger.error(f"详细错误信息:")
                    traceback.print_exc()
            
            logger.info(f"已初始化 {len(self.adapters)} 个API适配器: {list(self.adapters.keys())}")
            
        except Exception as e:
            logger.error(f"初始化适配器失败: {str(e)}")
            logger.error("详细错误堆栈:")
            traceback.print_exc()
            # 至少初始化派欧云适配器
            try:
                from .adapters.paiou_adapter import PaiouAdapter
                import os
                
                class FallbackConfig:
                    def __init__(self):
                        self.name = 'paiou'
                        self.base_url = 'https://api.ppinfra.com/openai'
                        self.model = 'deepseek/deepseek-v3-0324'
                        self.max_tokens = 1000
                        self.stream = True
                        self.response_format = {"type": "text"}
                        self.api_key = os.environ.get('PAIOU_API_KEY', 'sk_w4VWR2BAZTrwkilopHVMC65rhkmE0D7gayGEQKzjCi8')
                        self.enabled = bool(self.api_key)
                    
                    def get_headers(self):
                        return {
                            'Content-Type': 'application/json',
                            'Authorization': f'Bearer {self.api_key}'
                        }
                    
                    def get_client_config(self):
                        return {
                            'base_url': self.base_url,
                            'api_key': self.api_key
                        }
                    
                    def get_completion_params(self):
                        return {
                            'model': self.model,
                            'stream': self.stream,
                            'max_tokens': self.max_tokens,
                            'response_format': self.response_format,
                            'extra_body': {}
                        }
                
                fallback_config = FallbackConfig()
                if fallback_config.enabled:
                    self.adapters['paiou'] = PaiouAdapter(fallback_config)
                    logger.info("已初始化派欧云适配器（备用配置）")
                else:
                    logger.warning("派欧云API密钥未设置，无法初始化适配器")
            except Exception as mock_e:
                logger.error(f"初始化派欧云适配器失败: {str(mock_e)}")
    
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
        api_priority = self._get_api_priority(preferred_api)
        
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
    
    def _get_api_priority(self, preferred_api: Optional[str] = None) -> List[str]:
        """获取API优先级列表"""
        available_apis = list(self.adapters.keys())
        
        if not available_apis:
            return []
        
        if preferred_api and preferred_api in available_apis:
            # 将首选API放在第一位
            priority = [preferred_api]
            priority.extend([api for api in available_apis if api != preferred_api])
            return priority
        
        # 默认优先级顺序
        default_priority = ['aliyun', 'siliconflow', 'baishan', 'baidu', 'paiou']
        priority = []
        
        # 按默认优先级排序
        for api in default_priority:
            if api in available_apis:
                priority.append(api)
        
        # 添加其他API
        for api in available_apis:
            if api not in priority:
                priority.append(api)
        
        return priority
    
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
