"""
OpenAI API适配器
支持GPT-4o等模型
"""
from typing import Dict, Any, List
import requests
from .base_adapter import BaseAPIAdapter, APIException
from . import register_adapter
from ...utils.logging_helper import get_logger

logger = get_logger(__name__)

class OpenAIAdapter(BaseAPIAdapter):
    """OpenAI API适配器"""

    def __init__(self, config):
        super().__init__(config)
        self.api_key = config.api_key
        self.base_url = config.base_url
        self.model = config.model
        self.max_tokens = getattr(config, 'max_tokens', 2000)
        self.temperature = getattr(config, 'temperature', 0.7)

        if not self.api_key:
            logger.warning("OpenAI API密钥未配置")
            self.enabled = False

    def list_models(self) -> List[Dict[str, Any]]:
        """
        获取OpenAI可用的模型列表

        Returns:
            List[Dict]: 模型列表
        """
        if not self.enabled:
            return []

        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }

            response = requests.get(
                f"{self.base_url}/models",
                headers=headers,
                timeout=10
            )

            if response.status_code != 200:
                logger.warning(f"获取OpenAI模型列表失败: {response.status_code}")
                return self._get_default_models()

            result = response.json()
            models = []

            # 过滤出聊天模型
            chat_model_prefixes = ['gpt-4', 'gpt-3.5', 'o1', 'o3']
            for model_data in result.get('data', []):
                model_id = model_data.get('id', '')
                if any(model_id.startswith(prefix) for prefix in chat_model_prefixes):
                    models.append({
                        'id': model_id,
                        'name': model_id,
                        'description': f'OpenAI {model_id}',
                        'is_default': model_id == self.model,
                        'created': model_data.get('created'),
                        'owned_by': model_data.get('owned_by', 'openai')
                    })

            # 按创建时间倒序排序
            models.sort(key=lambda x: x.get('created', 0), reverse=True)

            if not models:
                return self._get_default_models()

            return models

        except Exception as e:
            logger.warning(f"获取OpenAI模型列表异常: {str(e)}")
            return self._get_default_models()

    def _get_default_models(self) -> List[Dict[str, Any]]:
        """返回默认的OpenAI模型列表"""
        default_models = [
            {'id': 'gpt-4o', 'name': 'GPT-4o', 'description': 'OpenAI最新多模态模型', 'is_default': True},
            {'id': 'gpt-4o-mini', 'name': 'GPT-4o Mini', 'description': '轻量级GPT-4o模型'},
            {'id': 'gpt-4-turbo', 'name': 'GPT-4 Turbo', 'description': 'GPT-4 Turbo模型'},
            {'id': 'gpt-4', 'name': 'GPT-4', 'description': 'GPT-4标准模型'},
            {'id': 'gpt-3.5-turbo', 'name': 'GPT-3.5 Turbo', 'description': 'GPT-3.5 Turbo模型'},
        ]
        return default_models

    def generate_names(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        调用OpenAI API生成姓名

        Args:
            prompt: 提示词
            **kwargs: 其他参数（支持 model 参数动态指定模型）

        Returns:
            Dict包含生成的姓名列表
        """
        if not self.enabled:
            return {
                'success': False,
                'error': 'OpenAI API未启用',
                'names': [],
                'api_name': self.name
            }

        try:
            # 支持动态指定模型
            model = kwargs.get('model', self.model)

            # 构建请求
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }

            data = {
                'model': model,
                'messages': [
                    {
                        'role': 'system',
                        'content': '你是一个专业的姓名生成专家，擅长根据角色描述生成具有文化内涵和美感的姓名。'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': self.max_tokens,
                'temperature': self.temperature
            }

            # 发送请求
            logger.info(f"正在调用OpenAI API (model={model})...")
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )

            # 检查响应
            if response.status_code != 200:
                error_msg = f"OpenAI API请求失败: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail.get('error', {}).get('message', '')}"
                except Exception:
                    error_msg += f" - {response.text}"
                logger.error(error_msg)
                raise APIException(error_msg)

            # 解析响应
            result = response.json()
            try:
                content = result['choices'][0]['message']['content']
            except (KeyError, IndexError) as e:
                error_msg = f"OpenAI API响应格式异常: {str(e)}"
                logger.error(error_msg)
                raise APIException(error_msg)

            logger.info(f"OpenAI API返回内容长度: {len(content)}")
            logger.debug(f"OpenAI API返回内容:\n{content}")

            # 解析姓名列表
            names = self._parse_names(content)

            if not names:
                logger.warning("OpenAI返回内容无法解析出姓名")
                return {
                    'success': False,
                    'error': '无法解析OpenAI返回的姓名',
                    'names': [],
                    'api_name': self.name,
                    'model': model
                }

            logger.info(f"OpenAI API成功生成 {len(names)} 个姓名")
            return {
                'success': True,
                'names': names,
                'api_name': self.name,
                'model': model
            }

        except requests.exceptions.Timeout:
            error_msg = "OpenAI API请求超时"
            logger.error(error_msg)
            raise APIException(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"OpenAI API请求失败: {str(e)}"
            logger.error(error_msg)
            raise APIException(error_msg)
        except Exception as e:
            error_msg = f"OpenAI API调用异常: {str(e)}"
            logger.error(error_msg)
            logger.exception("详细错误信息:")
            raise APIException(error_msg)

register_adapter('openai', lambda cfg: OpenAIAdapter(cfg))
