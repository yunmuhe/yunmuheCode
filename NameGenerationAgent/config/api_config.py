"""
多平台API配置
"""

import os
from typing import Any, Dict, Optional

from src.utils.env_loader import get_env_source, set_env_source


def load_env_file():
    """加载.env文件"""
    env_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")

    if os.path.exists(env_file_path):
        try:
            with open(env_file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()

                        # 移除引号
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]

                        if key not in os.environ:
                            os.environ[key] = value
                            set_env_source(key, ".env")
                        else:
                            if get_env_source(key) == "missing":
                                set_env_source(key, "process_env")
        except Exception as e:
            print(f"加载.env文件失败: {str(e)}")


# 自动加载.env文件
load_env_file()


def _mask_secret(value: Optional[str]) -> str:
    if not value:
        return ""
    if len(value) <= 6:
        return "***"
    return f"{value[:3]}***{value[-3:]}"


def summarize_api_configurations(configs: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    summary: Dict[str, Dict[str, Any]] = {}
    for api_name, config in configs.items():
        env_key = f"{api_name.upper()}_API_KEY"
        api_key = getattr(config, "api_key", None)
        summary[api_name] = {
            "enabled": bool(getattr(config, "enabled", api_key)),
            "api_key_source": get_env_source(env_key),
            "api_key_masked": _mask_secret(api_key),
            "model": getattr(config, "model", None),
            "base_url": getattr(config, "base_url", None),
        }
    return summary


class APIConfig:
    """API平台配置基类"""

    def __init__(self, name: str, base_url: str, api_key: str = None):
        self.name = name
        self.base_url = base_url
        self.api_key = api_key or os.environ.get(f"{name.upper()}_API_KEY")
        self.enabled = bool(self.api_key)

    def get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }


class AliyunConfig(APIConfig):
    """阿里云百炼配置"""

    def __init__(self):
        super().__init__(
            name="aliyun",
            base_url="https://dashscope.aliyuncs.com/api/v1",
            api_key=os.environ.get("ALIYUN_API_KEY"),
        )
        # 支持通过环境变量覆盖模型
        self.model = os.environ.get("ALIYUN_MODEL", "qwen3-235b-a22b-thinking-2507")
        self.max_tokens = 2000
        # 降级候选模型列表
        self.fallback_models = [os.environ.get("ALIYUN_FALLBACK_MODEL", "qwen-turbo")]

    def get_headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }


class SiliconFlowConfig(APIConfig):
    """硅基流动配置"""

    def __init__(self):
        super().__init__(
            name="siliconflow",
            base_url="https://api.siliconflow.cn/v1",
            api_key=os.environ.get("SILICONFLOW_API_KEY"),
        )
        self.model = os.environ.get("SILICONFLOW_MODEL", "Pro/zai-org/GLM-4.7")
        self.max_tokens = 2000


class BaishanConfig(APIConfig):
    """白山智算配置"""

    def __init__(self):
        super().__init__(
            name="baishan",
            base_url=os.environ.get("BAISHAN_BASE_URL", "https://api.edgefn.net/v1"),
            api_key=os.environ.get("BAISHAN_API_KEY"),
        )
        self.model = os.environ.get("BAISHAN_MODEL", "MiniMax-M2.5")
        self.max_tokens = int(os.environ.get("BAISHAN_MAX_TOKENS", 2000))


class OpenAIConfig(APIConfig):
    """OpenAI配置"""

    def __init__(self):
        super().__init__(
            name="openai",
            base_url="https://api.openai.com/v1",
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
        self.model = "gpt-4o"
        self.max_tokens = 2000
        self.temperature = 0.7


class GeminiConfig(APIConfig):
    """Google Gemini配置"""

    def __init__(self):
        super().__init__(
            name="gemini",
            base_url="https://generativelanguage.googleapis.com",
            api_key=os.environ.get("GEMINI_API_KEY"),
        )
        self.model = "gemini-2.0-flash-exp"
        self.max_tokens = 2000
        self.temperature = 0.7


class PaiouConfig(APIConfig):
    """派欧云配置"""

    def __init__(self):
        super().__init__(
            name="paiou",
            base_url="https://api.ppinfra.com/openai",
            api_key=os.environ.get("PAIOU_API_KEY"),
        )
        self.model = "deepseek/deepseek-v3-0324"
        self.max_tokens = 1000
        self.stream = True  # 默认启用流式响应
        self.response_format = {"type": "text"}

    def get_headers(self) -> Dict[str, str]:
        """获取派欧云请求头"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def get_client_config(self) -> Dict[str, Any]:
        """获取OpenAI客户端配置"""
        return {"base_url": self.base_url, "api_key": self.api_key}

    def get_completion_params(self) -> Dict[str, Any]:
        """获取聊天完成参数"""
        return {
            "model": self.model,
            "stream": self.stream,
            "max_tokens": self.max_tokens,
            "response_format": self.response_format,
            "extra_body": {},
        }


class AistudioConfig:
    def __init__(self):
        self.name = "aistudio"
        self.base_url = os.environ.get(
            "AISTUDIO_API_URL", "https://api-n0gca1bcpar672zf.aistudio-app.com/v1"
        )
        self.model = os.environ.get("AISTUDIO_MODEL", "Qwen3-30B-A3B-Q4_K_M")
        self.api_key = os.environ.get("AISTUDIO_API_KEY")
        self.max_tokens = int(os.environ.get("AISTUDIO_MAX_TOKENS", 2000))
        self.enabled = bool(self.api_key)
        self.stream = True
        self.response_format = None
        self.fallback_models = ["Qwen3-30B-A3B-Q4_K_M"]

    def get_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def get_client_config(self):
        return {"base_url": self.base_url, "api_key": self.api_key}

    def get_completion_params(self):
        return {
            "model": self.model,
            "stream": self.stream,
            "max_tokens": self.max_tokens,
            "response_format": self.response_format,
        }


class APIManager:
    """API管理器"""

    def __init__(self):
        self.apis = {
            "aliyun": AliyunConfig(),
            "siliconflow": SiliconFlowConfig(),
            "baishan": BaishanConfig(),
            "openai": OpenAIConfig(),
            "gemini": GeminiConfig(),
            "paiou": PaiouConfig(),
            "aistudio": AistudioConfig(),
        }
        # 在所有配置都添加完成后再计算active_apis
        self.active_apis = [
            name for name, config in self.apis.items() if config.enabled
        ]

    def get_available_apis(self) -> list:
        """获取可用的API列表"""
        return self.active_apis

    def get_api_config(self, api_name: str) -> Optional[APIConfig]:
        """获取指定API的配置"""
        return self.apis.get(api_name)

    def get_api_diagnostics(self) -> Dict[str, Dict[str, Any]]:
        return summarize_api_configurations(self.apis)

    def get_primary_api(self) -> Optional[str]:
        """获取主要API（优先级顺序）"""
        priority_order = [
            "aliyun",
            "siliconflow",
            "baishan",
            "openai",
            "gemini",
            "paiou",
            "aistudio",
        ]
        for api_name in priority_order:
            if api_name in self.active_apis:
                return api_name
        return None

    def get_fallback_apis(self, primary_api: str) -> list:
        """获取备用API列表"""
        return [name for name in self.active_apis if name != primary_api]


# 全局API管理器实例
api_manager = APIManager()
