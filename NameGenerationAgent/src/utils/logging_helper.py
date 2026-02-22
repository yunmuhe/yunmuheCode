"""
日志辅助工具
提供统一的日志记录器获取方法
"""

def get_logger(name):
    """
    获取日志记录器

    Args:
        name: 日志记录器名称（通常使用 __name__）

    Returns:
        Logger: 日志记录器实例
    """
    try:
        from .logger import get_logger as _get_logger
        return _get_logger(name)
    except ImportError:
        import logging
        return logging.getLogger(name)
