"""
派欧云API适配器
"""
from typing import Dict, Any, List
import json
from .base_adapter import BaseAPIAdapter, APIException
from . import register_adapter

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

class PaiouAdapter(BaseAPIAdapter):
    """派欧云API适配器"""

    def list_models(self) -> List[Dict[str, Any]]:
        """
        获取派欧云可用的模型列表（动态获取）

        Returns:
            List[Dict]: 模型列表
        """
        if not self.is_available():
            return []

        try:
            response = self._make_request("models", {}, method='GET', timeout=10)

            models = []
            for model_data in response.get('data', []):
                model_id = model_data.get('id', '')
                models.append({
                    'id': model_id,
                    'name': model_id.split('/')[-1] if '/' in model_id else model_id,
                    'description': f'派欧云 {model_id}',
                    'is_default': model_id == getattr(self.config, 'model', ''),
                    'owned_by': model_data.get('owned_by', '')
                })

            if not models:
                return []

            return models

        except Exception as e:
            logger.warning(f"获取派欧云模型列表异常: {str(e)}")
            return []

    def generate_names(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """生成姓名"""
        if not self.is_available():
            raise APIException("派欧云API未配置或不可用")
        
        try:
            # 使用OpenAI客户端
            from openai import OpenAI
            
            client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
            )
            
            # 构建消息
            messages = [
                {
                    "role": "system",
                    "content": """你是一个专业的姓名生成专家，擅长根据角色描述生成具有文化内涵和美感的姓名。

你的任务是：
1. 根据用户提供的角色描述生成指定数量的姓名
2. 严格按照指定的格式输出结果
3. 确保每个姓名都有明确的寓意解释
4. 不添加任何额外的解释或说明文字

输出格式要求：
- 每行格式：数字. 姓名：{姓名} - {寓意}
- 严格按照要求的数量生成
- 不要添加任何前缀或后缀文字"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            # 获取配置参数
            completion_params = self.config.get_completion_params()
            
            # 调用API
            response = client.chat.completions.create(
                model=completion_params['model'],
                messages=messages,
                stream=kwargs.get('stream', completion_params['stream']),
                max_tokens=kwargs.get('max_tokens', completion_params['max_tokens']),
                temperature=kwargs.get('temperature', 0.3),  # 降低温度以提高格式一致性
                top_p=kwargs.get('top_p', 0.8),  # 降低top_p以提高格式一致性
                response_format=completion_params['response_format'],
                extra_body=completion_params['extra_body']
            )
            
            # 处理流式和非流式响应
            if kwargs.get('stream', completion_params['stream']):
                # 流式响应处理
                generated_text = ""
                for chunk in response:
                    if chunk.choices and len(chunk.choices) > 0:
                        content = chunk.choices[0].delta.content
                        if content:
                            generated_text += content
                
                if not generated_text:
                    raise APIException("派欧云API流式响应返回空内容")
                    
                names = self._parse_names(generated_text)
                
                return {
                    'success': True,
                    'names': names,
                    'raw_response': generated_text,
                    'api_name': self.name,
                    'model': completion_params['model'],
                    'stream': True
                }
            else:
                # 非流式响应处理
                if not response.choices or len(response.choices) == 0:
                    raise APIException("派欧云API响应中没有choices数据")
                    
                generated_text = response.choices[0].message.content
                if not generated_text:
                    raise APIException("派欧云API返回空内容")
                    
                names = self._parse_names(generated_text)
                
                return {
                    'success': True,
                    'names': names,
                    'raw_response': generated_text,
                    'api_name': self.name,
                    'model': completion_params['model'],
                    'stream': False
                }
                
        except Exception as e:
            logger.error(f"派欧云API调用失败: {str(e)}")
            raise APIException(f"派欧云API调用失败: {str(e)}")
    
    def _parse_names(self, text: str) -> List[Dict[str, str]]:
        """解析生成的姓名"""
        names = []
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 多种解析模式
            import re
            
            # 模式1: 1. 姓名：xxx - xxx
            pattern1 = r'(\d+)\.?\s*姓名[：:]\s*(.+?)\s*[-–—]\s*(.+)'
            match1 = re.search(pattern1, line)
            if match1:
                name = match1.group(2).strip()
                meaning = match1.group(3).strip()
                if name and meaning:
                    names.append({
                        'name': name,
                        'meaning': meaning,
                        'source': 'paiou'
                    })
                continue
            
            # 模式2: 1. xxx - xxx
            pattern2 = r'(\d+)\.?\s*(.+?)\s*[-–—]\s*(.+)'
            match2 = re.search(pattern2, line)
            if match2:
                name = match2.group(2).strip()
                meaning = match2.group(3).strip()
                if name and meaning:
                    names.append({
                        'name': name,
                        'meaning': meaning,
                        'source': 'paiou'
                    })
                continue
            
            # 模式3: 姓名：xxx - xxx
            pattern3 = r'姓名[：:]\s*(.+?)\s*[-–—]\s*(.+)'
            match3 = re.search(pattern3, line)
            if match3:
                name = match3.group(1).strip()
                meaning = match3.group(2).strip()
                if name and meaning:
                    names.append({
                        'name': name,
                        'meaning': meaning,
                        'source': 'paiou'
                    })
                continue
            
            # 模式4: xxx - xxx
            pattern4 = r'(.+?)\s*[-–—]\s*(.+)'
            match4 = re.search(pattern4, line)
            if match4:
                name = match4.group(1).strip()
                meaning = match4.group(2).strip()
                # 清理姓名中的序号和标签
                name = re.sub(r'^\d+\.?\s*', '', name)  # 去掉序号
                name = re.sub(r'^姓名[：:]\s*', '', name)  # 去掉"姓名："
                name = name.strip()
                
                if name and meaning and len(name) >= 2:
                    names.append({
                        'name': name,
                        'meaning': meaning,
                        'source': 'paiou'
                    })
                continue
            
            # 模式5: 简单的姓名列表（没有含义）
            if len(line) >= 2 and len(line) <= 6:
                # 检查是否包含中文字符
                chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
                if chinese_pattern.search(line):
                    names.append({
                        'name': line,
                        'meaning': '根据角色特点生成的姓名',
                        'source': 'paiou'
                    })
        
        return names

register_adapter('paiou', lambda cfg: PaiouAdapter(cfg))
