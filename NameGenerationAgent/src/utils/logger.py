"""
日志管理工具
"""
import logging
import os
from datetime import datetime

# 延迟导入Config，避免循环导入
def get_config():
    """获取配置"""
    try:
        from ...config.settings import Config
        return Config
    except ImportError:
        # 返回默认配置
        class DefaultConfig:
            LOG_LEVEL = 'INFO'
            LOG_FILE = 'app.log'
            
            @staticmethod
            def ensure_directories():
                os.makedirs('logs', exist_ok=True)
        
        return DefaultConfig

def setup_logger(name: str, level: str = None) -> logging.Logger:
    """设置日志记录器"""
    
    Config = get_config()
    
    # 确保日志目录存在
    Config.ensure_directories()
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level or Config.LOG_LEVEL))
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 文件处理器
    try:
        file_handler = logging.FileHandler(Config.LOG_FILE, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception:
        # 如果文件处理器失败，只使用控制台处理器
        pass
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """获取日志记录器"""
    return logging.getLogger(name)

# 初始化根日志记录器
root_logger = setup_logger('NameGenerationAgent')
