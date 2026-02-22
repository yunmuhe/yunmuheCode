"""
Google Gemini API适配器
支持Gemini 2.0 Flash等模型
"""
from typing import Dict, Any, List
import requests
from .base_adapter import BaseAPIAdapter, APIException
from . import register_adapter
from ...utils.logging_helper import get_logger

logger = get_logger(__name__)

class GeminiAdapter(BaseAPIAdapter):
    """Google Gemini API适配器"""

    def __init__(self, config):
        super().__init__(config)
        self.api_key = config.api_key
        self.base_url = config.base_url
        self.model = config.model
        self.max_tokens = getattr(config, 'max_tokens', 2000)
        self.temperature = getattr(config, 'temperature', 0.7)

        if not self.api_key:
            logger.warning("Gemini API密钥未配置")
            self.enabled = False

    def list_models(self) -> List[Dict[str, Any]]:
        """
        获取Gemini可用的模型列表

        Returns:
            List[Dict]: 模型列表
        """
        if not self.enabled:
            return []

        # Gemini提供模型列表API
        try:
            url = f"{self.base_url}/v1beta/models?key={self.api_key}"
            response = requests.get(url, timeout=10)

            if response.status_code != 200:
                logger.warning(f"获取Gemini模型列表失败: {response.status_code}")
                return self._get_default_models()

            result = response.json()
            models = []

            for model_data in result.get('models', []):
                model_name = model_data.get('name', '').replace('models/', '')
                # 过滤出生成模型
                if 'generateContent' in model_data.get('supportedGenerationMethods', []):
                    models.append({
                        'id': model_name,
                        'name': model_name,
                        'description': model_data.get('description', f'Google {model_name}'),
                        'is_default': model_name == self.model,
                        'display_name': model_data.get('displayName', model_name)
                    })

            if not models:
                return self._get_default_models()

            return models

        except Exception as e:
            logger.warning(f"获取Gemini模型列表异常: {str(e)}")
            return self._get_default_models()

    def _get_default_models(self) -> List[Dict[str, Any]]:
        """返回默认的Gemini模型列表"""
        default_models = [
            {'id': 'gemini-2.0-flash-exp', 'name': 'Gemini 2.0 Flash', 'description': 'Google最新实验性快速模型', 'is_default': True},
            {'id': 'gemini-1.5-pro', 'name': 'Gemini 1.5 Pro', 'description': 'Google高性能模型', 'is_default': False},
            {'id': 'gemini-1.5-flash', 'name': 'Gemini 1.5 Flash', 'description': 'Google快速响应模型', 'is_default': False},
            {'id': 'gemini-pro', 'name': 'Gemini Pro', 'description': 'Google标准模型', 'is_default': False},
        ]
        return default_models

    def generate_names(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        调用Gemini API生成姓名（支持动态指定模型）

        Args:
            prompt: 提示词
            **kwargs: 其他参数（支持 model 参数）

        Returns:
            Dict包含生成的姓名列表
        """
        if not self.enabled:
            return {
                'success': False,
                'error': 'Gemini API未启用',
                'names': [],
                'api_name': self.name
            }

        try:
            # 支持动态指定模型
            model = kwargs.get('model', self.model)

            # 构建请求URL（Gemini API使用URL参数传递API密钥）
            url = f"{self.base_url}/v1beta/models/{model}:generateContent?key={self.api_key}"

            headers = {
                'Content-Type': 'application/json'
            }

            # Gemini API请求格式
            data = {
                'contents': [
                    {
                        'parts': [
                            {
                                'text': f"你是一个专业的姓名生成专家，擅长根据角色描述生成具有文化内涵和美感的姓名。\n\n{prompt}"
                            }
                        ]
                    }
                ],
                'generationConfig': {
                    'temperature': self.temperature,
                    'maxOutputTokens': self.max_tokens,
                    'topP': 0.8,
                    'topK': 10
                }
            }

            # 发送请求
            logger.info(f"正在调用Gemini API (model={model})...")
            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=30
            )

            # 检查响应
            if response.status_code != 200:
                error_msg = f"Gemini API请求失败: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail.get('error', {}).get('message', '')}"
                except Exception:
                    error_msg += f" - {response.text}"
                logger.error(error_msg)
                raise APIException(error_msg)

            # 解析响应
            result = response.json()

            # Gemini API响应格式
            if 'candidates' not in result or not result['candidates']:
                error_msg = "Gemini API返回格式错误或无内容"
                logger.error(error_msg)
                raise APIException(error_msg)

            try:
                content = result['candidates'][0]['content']['parts'][0]['text']
            except (KeyError, IndexError) as e:
                error_msg = f"Gemini API响应格式异常: {str(e)}"
                logger.error(error_msg)
                raise APIException(error_msg)

            logger.info(f"Gemini API返回内容长度: {len(content)}")
            logger.debug(f"Gemini API返回内容:\n{content}")

            # 解析姓名列表
            names = self._parse_names(content)

            if not names:
                logger.warning("Gemini返回内容无法解析出姓名")
                return {
                    'success': False,
                    'error': '无法解析Gemini返回的姓名',
                    'names': [],
                    'api_name': self.name,
                    'model': model
                }

            logger.info(f"Gemini API成功生成 {len(names)} 个姓名")
            return {
                'success': True,
                'names': names,
                'api_name': self.name,
                'model': model
            }

        except requests.exceptions.Timeout:
            error_msg = "Gemini API请求超时"
            logger.error(error_msg)
            raise APIException(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"Gemini API请求失败: {str(e)}"
            logger.error(error_msg)
            raise APIException(error_msg)
        except Exception as e:
            error_msg = f"Gemini API调用异常: {str(e)}"
            logger.error(error_msg)
            logger.exception("详细错误信息:")
            raise APIException(error_msg)

    def _parse_names(self, text: str) -> List[Dict[str, str]]:
        """解析生成的姓名"""
        names = []
        lines = text.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if '：' in line or ':' in line:
                try:
                    separator = '：' if '：' in line else ':'
                    parts = line.split(separator, 1)

                    if len(parts) >= 2:
                        name_part = parts[0].strip()
                        meaning_part = parts[1].strip()

                        name = name_part
                        if name.startswith('姓名'):
                            name = name[2:].strip()

                        name = name.replace('：', '').replace(':', '').strip()

                        for i in range(10):
                            if name.startswith(f'{i}.') or name.startswith(f'{i}、'):
                                name = name[2:].strip()
                                break

                        if name and len(name) >= 2 and len(name) <= 4:
                            names.append({
                                'name': name,
                                'meaning': meaning_part
                            })
                except Exception:
                    continue

        return names

register_adapter('gemini', lambda cfg: GeminiAdapter(cfg))
