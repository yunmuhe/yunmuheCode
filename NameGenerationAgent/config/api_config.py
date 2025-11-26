"""
多平台API配置
"""
import os
from typing import Dict, Any, Optional

def load_env_file():
    """加载.env文件"""
    env_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    
    if os.path.exists(env_file_path):
        try:
            with open(env_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # 移除引号
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        os.environ[key] = value
        except Exception as e:
            print(f"加载.env文件失败: {str(e)}")

# 自动加载.env文件
load_env_file()

class APIConfig:
    """API平台配置基类"""
    
    def __init__(self, name: str, base_url: str, api_key: str = None):
        self.name = name
        self.base_url = base_url
        self.api_key = api_key or os.environ.get(f'{name.upper()}_API_KEY')
        self.enabled = bool(self.api_key)
    
    def get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

class AliyunConfig(APIConfig):
    """阿里云百炼配置"""
    
    def __init__(self):
        super().__init__(
            name='aliyun',
            base_url='https://dashscope.aliyuncs.com/api/v1',
            api_key=os.environ.get('ALIYUN_API_KEY')
        )
        self.model = 'qwen-turbo'
        self.max_tokens = 2000
    
    def get_headers(self) -> Dict[str, str]:
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

class SiliconFlowConfig(APIConfig):
    """硅基流动配置"""
    
    def __init__(self):
        super().__init__(
            name='siliconflow',
            base_url='https://api.siliconflow.cn/v1',
            api_key=os.environ.get('SILICONFLOW_API_KEY')
        )
        self.model = 'Qwen/Qwen2.5-7B-Instruct'
        self.max_tokens = 2000

class BaishanConfig(APIConfig):
    """白山云配置"""
    
    def __init__(self):
        super().__init__(
            name='baishan',
            base_url='https://api.baishancloud.com/v1',
            api_key=os.environ.get('BAISHAN_API_KEY')
        )
        self.model = 'gpt-3.5-turbo'
        self.max_tokens = 2000

class BaiduConfig(APIConfig):
    """百度千帆配置"""
    
    def __init__(self):
        super().__init__(
            name='baidu',
            base_url='https://qianfan.baidubce.com/rest/2.0/ai_custom/v1',
            api_key=os.environ.get('BAIDU_API_KEY')
        )
        self.model = 'ernie-bot-turbo'
        self.max_tokens = 2000

class PaiouConfig(APIConfig):
    """派欧云配置"""
    
    def __init__(self):
        super().__init__(
            name='paiou',
            base_url='https://api.ppinfra.com/openai',
            api_key=os.environ.get('PAIOU_API_KEY')
        )
        self.model = 'deepseek/deepseek-v3-0324'
        self.max_tokens = 1000
        self.stream = True  # 默认启用流式响应
        self.response_format = {"type": "text"}
    
    def get_headers(self) -> Dict[str, str]:
        """获取派欧云请求头"""
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
    
    def get_client_config(self) -> Dict[str, Any]:
        """获取OpenAI客户端配置"""
        return {
            'base_url': self.base_url,
            'api_key': self.api_key
        }
    
    def get_completion_params(self) -> Dict[str, Any]:
        """获取聊天完成参数"""
        return {
            'model': self.model,
            'stream': self.stream,
            'max_tokens': self.max_tokens,
            'response_format': self.response_format,
            'extra_body': {}
        }

class AistudioConfig:
    def __init__(self):
        self.name = "aistudio"
        self.base_url = os.environ.get("AISTUDIO_API_URL", "https://api-n0gca1bcpar672zf.aistudio-app.com/v1")
        self.model = os.environ.get("AISTUDIO_MODEL", "qwen3:235b")
        self.api_key = os.environ.get("AISTUDIO_API_KEY")
        self.max_tokens = int(os.environ.get("AISTUDIO_MAX_TOKENS", 2000))
        self.enabled = bool(self.api_key)
        self.stream = True

    def get_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    def get_client_config(self):
        return {
            "base_url": self.base_url,
            "api_key": self.api_key
        }
    def get_completion_params(self):
        return {
            "model": self.model,
            "stream": self.stream,
            "max_tokens": self.max_tokens,
        }

class APIManager:
    """API管理器"""
    
    def __init__(self):
        self.apis = {
            'aliyun': AliyunConfig(),
            'siliconflow': SiliconFlowConfig(),
            'baishan': BaishanConfig(),
            'baidu': BaiduConfig(),
            'paiou': PaiouConfig(),
            'aistudio': AistudioConfig()  # 将aistudio添加到初始字典中
        }
        # 在所有配置都添加完成后再计算active_apis
        self.active_apis = [name for name, config in self.apis.items() if config.enabled]
    
    def get_available_apis(self) -> list:
        """获取可用的API列表"""
        return self.active_apis
    
    def get_api_config(self, api_name: str) -> Optional[APIConfig]:
        """获取指定API的配置"""
        return self.apis.get(api_name)
    
    def get_primary_api(self) -> Optional[str]:
        """获取主要API（优先级顺序）"""
        priority_order = ['aliyun', 'siliconflow', 'baishan', 'baidu', 'paiou', 'aistudio']
        for api_name in priority_order:
            if api_name in self.active_apis:
                return api_name
        return None
    
    def get_fallback_apis(self, primary_api: str) -> list:
        """获取备用API列表"""
        return [name for name in self.active_apis if name != primary_api]

# 全局API管理器实例
api_manager = APIManager()
