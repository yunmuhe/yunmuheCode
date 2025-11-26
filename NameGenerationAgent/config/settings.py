"""
应用配置设置
"""
import os
from typing import Dict, Any

class Config:
    """应用基础配置"""
    
    # 应用基础设置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    # 应用信息
    APP_NAME = "智能姓名生成系统"
    APP_VERSION = "1.0.0"
    
    # 数据存储路径
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    CACHE_DIR = os.path.join(DATA_DIR, 'cache')
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.path.join(DATA_DIR, 'app.log')
    
    # 缓存配置
    CACHE_TTL = 3600  # 缓存过期时间（秒）
    MAX_CACHE_SIZE = 1000  # 最大缓存条目数
    
    # API请求配置
    REQUEST_TIMEOUT = 30  # 请求超时时间（秒）
    MAX_RETRIES = 3  # 最大重试次数
    RETRY_DELAY = 1  # 重试延迟（秒）
    
    # 姓名生成配置
    DEFAULT_NAME_COUNT = 5  # 默认生成姓名数量
    MAX_NAME_COUNT = 20  # 最大生成姓名数量
    MIN_DESCRIPTION_LENGTH = 5  # 最小描述长度
    
    @staticmethod
    def ensure_directories():
        """确保必要的目录存在"""
        directories = [Config.DATA_DIR, Config.CACHE_DIR]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
