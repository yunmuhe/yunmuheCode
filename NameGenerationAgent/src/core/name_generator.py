"""
姓名生成核心逻辑
"""
from typing import Dict, Any, List, Optional
import random
import time

# 语料库增强器（可选）
def get_corpus_enhancer():
    """获取语料库增强器"""
    try:
        from .corpus_enhancer import get_corpus_enhancer as _get_enhancer
        return _get_enhancer()
    except Exception as e:
        print(f"语料库增强器加载失败: {e}")
        return None

# 延迟导入，避免循环导入问题
def get_unified_client():
    """获取统一客户端"""
    try:
        from ..api.unified_client import unified_client
        return unified_client
    except ImportError:
        # 返回模拟客户端
        class MockUnifiedClient:
            def generate_names(self, **kwargs):
                return {
                    'success': True,
                    'names': [
                        {'name': '测试姓名1', 'meaning': '测试含义1'},
                        {'name': '测试姓名2', 'meaning': '测试含义2'}
                    ],
                    'api_name': 'mock'
                }
            
            def get_available_apis(self):
                return ['mock']
            
            def get_api_status(self):
                return {'mock': {'enabled': True}}
            
            def cache_manager(self):
                class MockCache:
                    def get_stats(self):
                        return {
                            'cache_size': 0,
                            'hits': 0,
                            'misses': 0,
                            'hit_rate': 0.0,
                            'total_requests': 0
                        }
                
                return MockCache()
        
        return MockUnifiedClient()

def get_prompt_templates():
    """获取提示词模板"""
    try:
        from config.prompts import PromptTemplates
        return PromptTemplates()
    except ImportError as e:
        print(f"Warning: Failed to import PromptTemplates: {e}")
        # 返回默认模板
        class DefaultPromptTemplates:
            def build_prompt(self, **kwargs):
                return f"请根据描述生成姓名: {kwargs.get('description', '')}"

            def get_available_styles(self):
                return ['chinese_modern', 'chinese_traditional', 'fantasy', 'western', 'japanese']

            def get_available_genders(self):
                return ['male', 'female', 'neutral']

            def get_available_ages(self):
                return ['child', 'adult', 'elder']

        return DefaultPromptTemplates()

def get_input_validator():
    """获取输入验证器"""
    try:
        from ..utils.validation import InputValidator
        return InputValidator()
    except ImportError:
        # 返回默认验证器
        class DefaultInputValidator:
            def validate_description(self, desc):
                return {'valid': True}
            
            def validate_name_count(self, count):
                return {'valid': True}
            
            def validate_cultural_style(self, style):
                return {'valid': True}
            
            def validate_gender(self, gender):
                return {'valid': True}
            
            def validate_age(self, age):
                return {'valid': True}
        
        return DefaultInputValidator()

def get_response_validator():
    """获取响应验证器"""
    try:
        from ..utils.validation import ResponseValidator
        return ResponseValidator()
    except ImportError:
        # 返回默认验证器
        class DefaultResponseValidator:
            def validate_api_response(self, response):
                return {'valid': True}
        
        return DefaultResponseValidator()

def get_logger(name):
    """获取日志记录器"""
    try:
        from ..utils.logger import get_logger as _get_logger
        return _get_logger(name)
    except ImportError:
        import logging
        return logging.getLogger(name)

logger = get_logger(__name__)

class NameGenerator:
    """姓名生成器"""
    
    def __init__(self):
        self.unified_client = get_unified_client()
        self.prompt_templates = get_prompt_templates()
        self.input_validator = get_input_validator()
        self.response_validator = get_response_validator()
        self.corpus_enhancer = get_corpus_enhancer()
    
    def generate_names(self, description: str, count: int = 5,
                      cultural_style: str = 'chinese_modern',
                      gender: str = 'neutral', age: str = 'adult',
                      preferred_api: Optional[str] = None,
                      use_cache: bool = True,
                      use_mock_on_failure: bool = True) -> Dict[str, Any]:
        """生成姓名"""
        
        try:
            # 验证输入参数
            self._validate_inputs(description, count, cultural_style, gender, age)
            
            # 构建提示词
            prompt = self.prompt_templates.build_prompt(
                description=description,
                count=count,
                cultural_style=cultural_style,
                gender=gender,
                age=age
            )
            
            # 使用语料库增强器增强提示词
            if self.corpus_enhancer:
                options = {
                    'gender': gender,
                    'cultural_style': cultural_style
                }
                prompt = self.corpus_enhancer.enhance_prompt(description, options)
            
            logger.info(f"开始生成姓名，描述: {description[:50]}...")
            
            # 调用API生成姓名
            api_result = self.unified_client.generate_names(
                prompt=prompt,
                count=count,
                preferred_api=preferred_api,
                use_cache=use_cache,
                use_mock_on_failure=use_mock_on_failure,
                temperature=0.7,
                max_tokens=2000
            )
            
            # 验证API响应
            validation_result = self.response_validator.validate_api_response(api_result)
            if not validation_result['valid']:
                logger.error(f"API响应验证失败: {validation_result['error']}")
                return {
                    'success': False,
                    'error': f"API响应验证失败: {validation_result['error']}",
                    'names': []
                }
            
            # 处理生成结果
            result = self._process_generated_names(api_result, description)
            
            logger.info(f"成功生成 {len(result['names'])} 个姓名")
            return result
            
        except Exception as e:
            logger.error(f"生成姓名失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'names': []
            }
    
    def _validate_inputs(self, description: str, count: int,
                        cultural_style: str, gender: str, age: str):
        """验证输入参数"""
        
        # 验证描述
        desc_result = self.input_validator.validate_description(description)
        if not desc_result['valid']:
            raise ValueError(f"描述验证失败: {desc_result.get('error', '未知错误')}")
        
        # 验证数量
        count_result = self.input_validator.validate_name_count(count)
        if not count_result['valid']:
            raise ValueError(f"数量验证失败: {count_result.get('error', '未知错误')}")
        
        # 验证文化风格
        style_result = self.input_validator.validate_cultural_style(cultural_style)
        if not style_result['valid']:
            raise ValueError(f"文化风格验证失败: {style_result.get('error', '未知错误')}")
        
        # 验证性别
        gender_result = self.input_validator.validate_gender(gender)
        if not gender_result['valid']:
            raise ValueError(f"性别验证失败: {gender_result.get('error', '未知错误')}")
        
        # 验证年龄
        age_result = self.input_validator.validate_age(age)
        if not age_result['valid']:
            raise ValueError(f"年龄验证失败: {age_result.get('error', '未知错误')}")
    
    def _process_generated_names(self, api_result: Dict[str, Any], 
                                description: str) -> Dict[str, Any]:
        """处理生成的姓名"""
        
        if not api_result.get('success', False):
            return {
                'success': False,
                'error': api_result.get('error', 'API调用失败'),
                'names': []
            }
        
        names = api_result.get('names', [])
        processed_names = []
        
        for i, name_data in enumerate(names):
            try:
                processed_name = self._process_single_name(name_data, i + 1)
                processed_names.append(processed_name)
            except Exception as e:
                logger.warning(f"处理第{i+1}个姓名失败: {str(e)}")
                continue
        
        return {
            'success': True,
            'names': processed_names,
            'total_generated': len(names),
            'successfully_processed': len(processed_names),
            'api_name': api_result.get('api_name', 'unknown'),
            'model': api_result.get('model', 'unknown'),
            'description': description,
            'generated_at': time.time()
        }
    
    def _process_single_name(self, name_data: Dict[str, str], index: int) -> Dict[str, Any]:
        """处理单个姓名"""
        
        name = name_data.get('name', '').strip()
        meaning = name_data.get('meaning', '').strip()
        source = name_data.get('source', 'unknown')
        
        # 清理姓名
        name = self._clean_name(name)
        
        # 生成姓名ID
        name_id = f"name_{int(time.time())}_{index}"
        
        # 分析姓名特征
        features = self._analyze_name_features(name)
        
        return {
            'id': name_id,
            'name': name,
            'meaning': meaning,
            'source': source,
            'features': features,
            'created_at': time.time()
        }
    
    def _clean_name(self, name: str) -> str:
        """清理姓名"""
        # 去除序号
        import re
        
        # 去除开头的数字和点
        name = re.sub(r'^\d+\.?\s*', '', name)
        
        # 去除特殊字符
        name = re.sub(r'[^\u4e00-\u9fff\w\s]', '', name)
        
        # 去除多余空格
        name = ' '.join(name.split())
        
        return name.strip()
    
    def _analyze_name_features(self, name: str) -> Dict[str, Any]:
        """分析姓名特征"""
        features = {
            'length': len(name),
            'character_count': len(name.replace(' ', '')),
            'word_count': len(name.split()),
            'has_space': ' ' in name,
            'is_chinese': self._is_chinese_name(name),
            'is_english': self._is_english_name(name)
        }
        
        # 分析音韵特征（简单分析）
        if features['is_chinese']:
            features['tone_pattern'] = self._analyze_chinese_tone(name)
            features['stroke_count'] = self._estimate_stroke_count(name)
        
        return features
    
    def _is_chinese_name(self, name: str) -> bool:
        """判断是否为中文姓名"""
        import re
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
        return bool(chinese_pattern.search(name))
    
    def _is_english_name(self, name: str) -> bool:
        """判断是否为英文姓名"""
        import re
        english_pattern = re.compile(r'^[a-zA-Z\s]+$')
        return bool(english_pattern.match(name))
    
    def _analyze_chinese_tone(self, name: str) -> str:
        """分析中文姓名的音韵特征（简化版）"""
        # 这里可以实现更复杂的音韵分析
        # 目前返回简单的特征描述
        if len(name) == 2:
            return "双字名"
        elif len(name) == 3:
            return "三字名"
        else:
            return "多字名"
    
    def _estimate_stroke_count(self, name: str) -> int:
        """估算中文字符的笔画数（简化版）"""
        # 这里可以实现更精确的笔画数计算
        # 目前返回估算值
        stroke_map = {
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10
        }
        
        total_strokes = 0
        for char in name:
            if char in stroke_map:
                total_strokes += stroke_map[char]
            else:
                # 默认估算笔画数
                total_strokes += 8
        
        return total_strokes
    
    def get_available_options(self) -> Dict[str, List[str]]:
        """获取可用的选项"""
        return {
            'cultural_styles': self.prompt_templates.get_available_styles(),
            'genders': self.prompt_templates.get_available_genders(),
            'ages': self.prompt_templates.get_available_ages(),
            'apis': self.unified_client.get_available_apis()
        }
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """获取生成统计信息"""
        return {
            'available_apis': len(self.unified_client.get_available_apis()),
            'api_status': self.unified_client.get_api_status(),
            'cache_stats': self.unified_client.cache_manager.get_stats()
        }

# 全局姓名生成器实例
name_generator = NameGenerator()
