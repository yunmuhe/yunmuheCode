from . import register_adapter
from .openai_compatible_adapter import OpenAICompatibleAdapter


class BaishanAdapter(OpenAICompatibleAdapter):
    pass


register_adapter("baishan", lambda cfg: BaishanAdapter(cfg))
