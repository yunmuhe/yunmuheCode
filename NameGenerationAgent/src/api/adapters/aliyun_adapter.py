"""
阿里云百炼API适配器
"""
from typing import Dict, Any, List
import json
from .base_adapter import BaseAPIAdapter, APIException
from ...utils.logger import get_logger

logger = get_logger(__name__)

class AliyunAdapter(BaseAPIAdapter):
    """阿里云百炼API适配器"""
    
    def generate_names(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """生成姓名"""
        if not self.is_available():
            raise APIException("阿里云API未配置或不可用")
        
        # 构建请求数据
        data = {
            "model": self.config.model,
            "input": {
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的姓名生成专家，擅长根据角色描述生成具有文化内涵和美感的姓名。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            },
            "parameters": {
                "max_tokens": kwargs.get('max_tokens', self.config.max_tokens),
                "temperature": kwargs.get('temperature', 0.7),
                "top_p": kwargs.get('top_p', 0.9)
            }
        }
        
        try:
            response = self._make_request("services/aigc/text-generation/generation", data)
            
            # 解析响应
            if 'output' in response and 'text' in response['output']:
                generated_text = response['output']['text']
                names = self._parse_names(generated_text)
                
                return {
                    'success': True,
                    'names': names,
                    'raw_response': generated_text,
                    'api_name': self.name,
                    'model': self.config.model
                }
            else:
                raise APIException("阿里云API响应格式错误")
                
        except Exception as e:
            logger.error(f"阿里云API调用失败: {str(e)}")
            raise APIException(f"阿里云API调用失败: {str(e)}")
    
    def _parse_names(self, text: str) -> List[Dict[str, str]]:
        """解析生成的姓名"""
        names = []
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 解析格式：姓名：{name} - {meaning}
            if '：' in line or ':' in line:
                try:
                    # 处理中文冒号和英文冒号
                    separator = '：' if '：' in line else ':'
                    parts = line.split(separator, 1)
                    
                    if len(parts) >= 2:
                        name_part = parts[0].strip()
                        meaning_part = parts[1].strip()
                        
                        # 提取姓名（去掉序号）
                        name = name_part
                        if name.startswith('姓名'):
                            name = name[2:].strip()
                        
                        # 清理姓名
                        name = name.replace('：', '').replace(':', '').strip()
                        
                        if name and meaning_part:
                            names.append({
                                'name': name,
                                'meaning': meaning_part,
                                'source': 'aliyun'
                            })
                
                except Exception as e:
                    logger.warning(f"解析姓名行失败: {line}, 错误: {str(e)}")
                    continue
        
        return names
