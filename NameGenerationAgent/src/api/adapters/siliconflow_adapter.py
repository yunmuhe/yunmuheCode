"""
硅基流动API适配器
"""
from typing import Dict, Any, List
import json
from .base_adapter import BaseAPIAdapter, APIException
from ...utils.logger import get_logger
from . import register_adapter

logger = get_logger(__name__)

class SiliconFlowAdapter(BaseAPIAdapter):
    """硅基流动API适配器"""

    def list_models(self) -> List[Dict[str, Any]]:
        """
        获取硅基流动可用的模型列表

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
                # 过滤出聊天模型
                if 'chat' in model_data.get('object', '').lower() or \
                   any(keyword in model_id.lower() for keyword in ['qwen', 'llama', 'deepseek', 'yi', 'mistral', 'glm']):
                    models.append({
                        'id': model_id,
                        'name': model_id.split('/')[-1] if '/' in model_id else model_id,
                        'description': f'硅基流动 {model_id}',
                        'is_default': model_id == self.config.model,
                        'owned_by': model_data.get('owned_by', 'siliconflow')
                    })

            if not models:
                return []

            return models

        except Exception as e:
            logger.warning(f"获取硅基流动模型列表异常: {str(e)}")
            return []

    def generate_names(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """生成姓名（支持动态指定模型）"""
        if not self.is_available():
            raise APIException("硅基流动API未配置或不可用")

        # 支持动态指定模型
        model = kwargs.get('model', self.config.model)

        # 构建请求数据
        data = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个专业的姓名生成专家，擅长根据角色描述生成具有文化内涵和美感的姓名。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": kwargs.get('max_tokens', self.config.max_tokens),
            "temperature": kwargs.get('temperature', 0.7),
            "top_p": kwargs.get('top_p', 0.9),
            "stream": False
        }

        try:
            response = self._make_request("chat/completions", data)

            # 解析响应
            if 'choices' in response and len(response['choices']) > 0:
                generated_text = response['choices'][0]['message']['content']
                names = self._parse_names(generated_text)

                return {
                    'success': True,
                    'names': names,
                    'raw_response': generated_text,
                    'api_name': self.name,
                    'model': model
                }
            else:
                raise APIException("硅基流动API响应格式错误")

        except Exception as e:
            logger.error(f"硅基流动API调用失败: {str(e)}")
            raise APIException(f"硅基流动API调用失败: {str(e)}")

register_adapter('siliconflow', lambda cfg: SiliconFlowAdapter(cfg))
