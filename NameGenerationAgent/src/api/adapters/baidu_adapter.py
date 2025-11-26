"""
百度千帆API适配器
"""
from typing import Dict, Any, List
import json
import time
import hashlib
import hmac
from urllib.parse import urlencode
from .base_adapter import BaseAPIAdapter, APIException
from ...utils.logger import get_logger

logger = get_logger(__name__)

class BaiduAdapter(BaseAPIAdapter):
    """百度千帆API适配器"""
    
    def __init__(self, config):
        super().__init__(config)
        self.secret_key = config.secret_key or ""
    
    def generate_names(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """生成姓名"""
        if not self.is_available():
            raise APIException("百度千帆API未配置或不可用")
        
        # 构建请求数据
        data = {
            "messages": [
                {
                    "role": "user",
                    "content": f"你是一个专业的姓名生成专家，擅长根据角色描述生成具有文化内涵和美感的姓名。\n\n{prompt}"
                }
            ],
            "temperature": kwargs.get('temperature', 0.7),
            "top_p": kwargs.get('top_p', 0.9),
            "penalty_score": kwargs.get('penalty_score', 1.0),
            "max_output_tokens": kwargs.get('max_tokens', self.config.max_tokens)
        }
        
        try:
            # 百度千帆需要特殊的认证方式
            headers = self._get_auth_headers()
            url = f"{self.base_url}/chat/completions"
            
            logger.info(f"发送请求到 {self.name}: {url}")
            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            # 解析响应
            if 'result' in result:
                generated_text = result['result']
                names = self._parse_names(generated_text)
                
                return {
                    'success': True,
                    'names': names,
                    'raw_response': generated_text,
                    'api_name': self.name,
                    'model': self.config.model
                }
            else:
                raise APIException("百度千帆API响应格式错误")
                
        except Exception as e:
            logger.error(f"百度千帆API调用失败: {str(e)}")
            raise APIException(f"百度千帆API调用失败: {str(e)}")
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """获取百度千帆认证头"""
        # 百度千帆的认证方式
        timestamp = str(int(time.time()))
        nonce = str(int(time.time() * 1000))
        
        # 构建签名字符串
        sign_string = f"{self.api_key}{timestamp}{nonce}"
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            sign_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return {
            'Content-Type': 'application/json',
            'X-Bce-Access-Key': self.api_key,
            'X-Bce-Timestamp': timestamp,
            'X-Bce-Nonce': nonce,
            'X-Bce-Signature': signature
        }
    
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
                                'source': 'baidu'
                            })
                
                except Exception as e:
                    logger.warning(f"解析姓名行失败: {line}, 错误: {str(e)}")
                    continue
        
        return names
