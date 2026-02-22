"""
阿里云百炼API适配器
"""
from typing import Dict, Any, List
import re
import json
from .base_adapter import BaseAPIAdapter, APIException
from ...utils.logger import get_logger
from . import register_adapter

logger = get_logger(__name__)

class AliyunAdapter(BaseAPIAdapter):
    """阿里云百炼API适配器"""

    def list_models(self) -> List[Dict[str, Any]]:
        """
        获取阿里云百炼可用的模型列表

        Returns:
            List[Dict]: 模型列表
        """
        if not self.is_available():
            return []

        # 阿里云暂不提供公开的模型列表API，返回预定义的常用模型
        return self._get_default_models()

    def _get_default_models(self) -> List[Dict[str, Any]]:
        """返回默认的阿里云模型列表"""
        default_models = [
            {'id': 'qwen-max', 'name': 'Qwen Max', 'description': '通义千问超大规模语言模型，适用于复杂任务', 'is_default': False},
            {'id': 'qwen-plus', 'name': 'Qwen Plus', 'description': '通义千问增强版，性能与成本平衡', 'is_default': False},
            {'id': 'qwen-turbo', 'name': 'Qwen Turbo', 'description': '通义千问高性能版，响应速度快', 'is_default': False},
            {'id': 'qwen3-235b-a22b-thinking-2507', 'name': 'Qwen3 235B Thinking', 'description': '通义千问3代思考模型', 'is_default': True},
            {'id': 'qwen2.5-72b-instruct', 'name': 'Qwen2.5 72B', 'description': '通义千问2.5 72B指令模型', 'is_default': False},
            {'id': 'qwen2.5-32b-instruct', 'name': 'Qwen2.5 32B', 'description': '通义千问2.5 32B指令模型', 'is_default': False},
            {'id': 'qwen2.5-14b-instruct', 'name': 'Qwen2.5 14B', 'description': '通义千问2.5 14B指令模型', 'is_default': False},
            {'id': 'qwen2.5-7b-instruct', 'name': 'Qwen2.5 7B', 'description': '通义千问2.5 7B指令模型', 'is_default': False},
        ]
        # 标记当前配置的模型为默认
        for model in default_models:
            if model['id'] == self.config.model:
                model['is_default'] = True
            else:
                model['is_default'] = False
        return default_models

    def generate_names(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """生成姓名（支持动态指定模型）"""
        if not self.is_available():
            raise APIException("阿里云API未配置或不可用")

        # 支持动态指定模型
        model = kwargs.get('model', self.config.model)

        # 构建请求数据
        data = {
            "model": model,
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

        def _call_with_model(model_name: str) -> Dict[str, Any]:
            payload = dict(data)
            payload["model"] = model_name
            resp = self._make_request("services/aigc/text-generation/generation", payload)
            if 'output' in resp and 'text' in resp['output']:
                return resp
            raise APIException("阿里云API响应格式错误")

        try:
            response = _call_with_model(model)
        except Exception as e:
            msg = str(e)
            unsupported_patterns = [
                r'不支持', r'unsupported', r'not\s+support', r'404', r'Model\s+not\s+found', r'Invalid\s+model'
            ]
            need_fallback = any(re.search(pat, msg, flags=re.IGNORECASE) for pat in unsupported_patterns)
            if need_fallback and getattr(self.config, "fallback_models", []):
                for fb in self.config.fallback_models:
                    try:
                        response = _call_with_model(fb)
                        model = fb  # 更新使用的模型
                        break
                    except Exception:
                        continue
                else:
                    logger.error(f"阿里云API降级失败: {msg}")
                    raise APIException(f"阿里云API调用失败: {msg}")
            else:
                logger.error(f"阿里云API调用失败: {msg}")
                raise APIException(f"阿里云API调用失败: {msg}")

        generated_text = response['output']['text']
        names = self._parse_names(generated_text)

        return {
            'success': True,
            'names': names,
            'raw_response': generated_text,
            'api_name': self.name,
            'model': model
        }

register_adapter('aliyun', lambda cfg: AliyunAdapter(cfg))
