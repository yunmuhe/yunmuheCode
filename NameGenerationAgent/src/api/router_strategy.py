from typing import Dict, Any, Optional, List
import threading
from .adapters.base_adapter import BaseAPIAdapter

class RouterStrategy:
    def __init__(self, default_order: Optional[List[str]] = None, weights: Optional[Dict[str, float]] = None):
        self.default_order = default_order or ['aistudio', 'aliyun', 'siliconflow', 'paiou', 'openai', 'gemini']
        self.weights = weights or {}
    def get_priority(self, adapters: Dict[str, BaseAPIAdapter], preferred_api: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> List[str]:
        return list(adapters.keys())

class PriorityRouterStrategy(RouterStrategy):
    def get_priority(self, adapters: Dict[str, BaseAPIAdapter], preferred_api: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> List[str]:
        available = list(adapters.keys())
        if not available:
            return []
        if preferred_api and preferred_api in available:
            result = [preferred_api]
            result.extend([a for a in available if a != preferred_api])
            return result
        result: List[str] = []
        for api in self.default_order:
            if api in available:
                result.append(api)
        for api in available:
            if api not in result:
                result.append(api)
        return result

class WeightedRouterStrategy(RouterStrategy):
    def get_priority(self, adapters: Dict[str, BaseAPIAdapter], preferred_api: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> List[str]:
        available = list(adapters.keys())
        if not available:
            return []
        if preferred_api and preferred_api in available:
            result = [preferred_api]
            result.extend([a for a in available if a != preferred_api])
            return result
        default_index = {api: i for i, api in enumerate(self.default_order)}
        def weight_of(api: str) -> float:
            w = self.weights.get(api)
            try:
                return float(w) if w is not None else 0.0
            except Exception:
                return 0.0
        def tie_break(api: str) -> int:
            return default_index.get(api, len(self.default_order))
        ordered = sorted(available, key=lambda a: (-weight_of(a), tie_break(a), a))
        return ordered

class RoundRobinRouterStrategy(RouterStrategy):
    def __init__(self, default_order: Optional[List[str]] = None, weights: Optional[Dict[str, float]] = None):
        super().__init__(default_order, weights)
        self._order: List[str] = []
        self._idx: int = -1
        self._lock = threading.Lock()
    def _rebuild_order(self, available: List[str]) -> None:
        base: List[str] = []
        for api in self.default_order:
            if api in available:
                base.append(api)
        for api in available:
            if api not in base:
                base.append(api)
        self._order = base
        self._idx = (self._idx + 1) % len(self._order) if self._order else -1
    def get_priority(self, adapters: Dict[str, BaseAPIAdapter], preferred_api: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> List[str]:
        available = list(adapters.keys())
        if not available:
            return []
        if preferred_api and preferred_api in available:
            result = [preferred_api]
            result.extend([a for a in available if a != preferred_api])
            return result
        with self._lock:
            if set(self._order) != set(available):
                self._rebuild_order(available)
            if not self._order:
                return []
            start = self._idx if self._idx >= 0 else 0
            return self._order[start:] + self._order[:start]

class CapabilityRouterStrategy(RouterStrategy):
    def get_priority(self, adapters: Dict[str, BaseAPIAdapter], preferred_api: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> List[str]:
        available = list(adapters.keys())
        if not available:
            return []
        if context is None:
            context = {}
        avoid = set(context.get('avoid_apis', []) or [])
        filtered = [a for a in available if a not in avoid]
        if not filtered:
            filtered = available
        need_stream = bool(context.get('need_stream', False))
        def has_stream(a: str) -> bool:
            adapter = adapters.get(a)
            cfg = getattr(adapter, 'config', None)
            return bool(getattr(cfg, 'stream', False)) if cfg is not None else False
        if need_stream:
            stream_first = [a for a in filtered if has_stream(a)]
            non_stream = [a for a in filtered if a not in stream_first]
            ordered = []
            for api in self.default_order:
                if api in stream_first:
                    ordered.append(api)
            for api in stream_first:
                if api not in ordered:
                    ordered.append(api)
            for api in self.default_order:
                if api in non_stream:
                    ordered.append(api)
            for api in non_stream:
                if api not in ordered:
                    ordered.append(api)
        else:
            ordered = []
            for api in self.default_order:
                if api in filtered:
                    ordered.append(api)
            for api in filtered:
                if api not in ordered:
                    ordered.append(api)
        if preferred_api and preferred_api in ordered:
            return [preferred_api] + [a for a in ordered if a != preferred_api]
        return ordered

def _parse_weights(s: Optional[str]) -> Dict[str, float]:
    if not s:
        return {}
    items = [x for x in str(s).split(',') if x.strip()]
    result: Dict[str, float] = {}
    for item in items:
        if '=' in item:
            k, v = item.split('=', 1)
        elif ':' in item:
            k, v = item.split(':', 1)
        else:
            continue
        k = k.strip()
        try:
            result[k] = float(v.strip())
        except Exception:
            continue
    return result

def get_router_strategy(name: str, default_order: Optional[List[str]] = None, weights_raw: Optional[str] = None) -> RouterStrategy:
    weights = _parse_weights(weights_raw)
    n = (name or 'priority').strip().lower()
    if n == 'weighted':
        return WeightedRouterStrategy(default_order, weights)
    if n == 'roundrobin' or n == 'round_robin':
        return RoundRobinRouterStrategy(default_order, weights)
    if n == 'capability':
        return CapabilityRouterStrategy(default_order, weights)
    return PriorityRouterStrategy(default_order, weights)
