from . import register_adapter
from .openai_compatible_adapter import OpenAICompatibleAdapter


class BaishanAdapter(OpenAICompatibleAdapter):
    system_prompt = "你是一个有用的助手"


register_adapter("baishan", lambda cfg: BaishanAdapter(cfg))
