from typing import Dict, Callable
from ...utils.logging_helper import get_logger

ADAPTER_BUILDERS: Dict[str, Callable] = {}
logger = get_logger(__name__)

def register_adapter(name: str, builder: Callable) -> None:
    ADAPTER_BUILDERS[name] = builder

def ensure_adapters_imported() -> None:
    try:
        from . import aliyun_adapter  # noqa: F401
    except Exception as e:
        logger.warning(f"导入 aliyun_adapter 失败: {e}")
    try:
        from . import siliconflow_adapter  # noqa: F401
    except Exception as e:
        logger.warning(f"导入 siliconflow_adapter 失败: {e}")
    try:
        from . import openai_adapter  # noqa: F401
    except Exception as e:
        logger.warning(f"导入 openai_adapter 失败: {e}")
    try:
        from . import gemini_adapter  # noqa: F401
    except Exception as e:
        logger.warning(f"导入 gemini_adapter 失败: {e}")
    try:
        from . import paiou_adapter  # noqa: F401
    except Exception as e:
        logger.warning(f"导入 paiou_adapter 失败: {e}")
    try:
        from . import aistudio_adapter  # noqa: F401
    except Exception as e:
        logger.warning(f"导入 aistudio_adapter 失败: {e}")

def build_adapters(api_configs: Dict[str, object]) -> Dict[str, object]:
    ensure_adapters_imported()
    result: Dict[str, object] = {}
    for name, config in (api_configs or {}).items():
        if name in ADAPTER_BUILDERS and getattr(config, 'enabled', False):
            try:
                adapter = ADAPTER_BUILDERS[name](config)
                if adapter:
                    result[name] = adapter
            except Exception as e:
                logger.warning(f"构建适配器 {name} 失败: {e}")
                continue
    return result
