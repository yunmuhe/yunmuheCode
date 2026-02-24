from typing import Dict, Any, List
from .base_adapter import BaseAPIAdapter
from . import register_adapter

class AistudioAdapter(BaseAPIAdapter):
    def __init__(self, config):
        super().__init__(config)
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=config.api_key, base_url=config.base_url)
        except Exception as e:
            print("[AistudioAdapter] OpenAI客户端初始化失败:", e)
        # 不使用__name__，不存储日志器，初始化只使用print提示

    def list_models(self) -> List[Dict[str, Any]]:
        """获取AI Studio可用的模型列表"""
        if not self.is_available():
            return []

        current_model = getattr(self.config, 'model', 'Qwen3-30B-A3B-Q4_K_M')
        return [
            {
                'id': current_model,
                'name': current_model,
                'description': f'AI Studio {current_model}',
                'is_default': True,
            },
        ]

    def generate_names(self, prompt, count=5, **kwargs):
        completion_params = self.config.get_completion_params()
        model = kwargs.get("model", completion_params["model"])
        messages = [
            {"role": "system", "content": "你是一个专业的姓名生成专家。"},
            {"role": "user", "content": prompt}
        ]
        stream = kwargs.get("stream", completion_params["stream"])
        temperature = kwargs.get("temperature", 0.7)
        response_format = kwargs.get("response_format", completion_params.get("response_format"))

        def _do_request(curr_model):
            params = dict(
                model=curr_model,
                messages=messages,
                stream=stream,
                max_tokens=completion_params["max_tokens"],
                temperature=temperature
            )
            if response_format:
                params["response_format"] = response_format
            return self.client.chat.completions.create(**params)

        try:
            response = _do_request(model)
        except Exception as e:
            msg = str(e)
            if ("暂不支持该模型" in msg) or ("40405" in msg):
                fallback_model = getattr(self.config, "fallback_models", ["Qwen3-30B-A3B-Q4_K_M"])[0]
                try:
                    response = _do_request(fallback_model)
                    model = fallback_model
                except Exception as e2:
                    raise e2
            else:
                raise

        if stream:
            generated_text = ""
            for chunk in response:
                content = ""
                if hasattr(chunk.choices[0].delta, "reasoning_content") and chunk.choices[0].delta.reasoning_content:
                    content = chunk.choices[0].delta.reasoning_content
                else:
                    content = chunk.choices[0].delta.content
                if content:
                    generated_text += content
            names = self._parse_structured_or_text(generated_text)
            return {
                "success": True,
                "names": names,
                "raw_response": generated_text,
                "api_name": self.name,
                "model": model,
                "stream": True
            }
        else:
            content = response.choices[0].message.content
            names = self._parse_structured_or_text(content)
            return {
                "success": True,
                "names": names,
                "raw_response": content,
                "api_name": self.name,
                "model": model,
                "stream": False
            }

    def _parse_structured_or_text(self, text):
        try:
            import json
            obj = json.loads(text)
            items = obj.get("items") or obj.get("names") or obj.get("data") or []
            result = []
            for it in items:
                n = (it.get("name") or "").strip()
                m = (it.get("meaning") or "").strip()
                if n and m and self._is_valid_name(n) and self._is_valid_meaning(m):
                    result.append({"name": n, "meaning": m, "source": "aistudio"})
            if result:
                return result
        except Exception:
            pass
        return self._parse_names(text)

    def _parse_names(self, text):
        names = []
        import re
        lines = text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not self._is_candidate_line(line):
                continue
            m = re.search(r'\d+\.?\s*姓名[：:]{0,1}\s*([\u4e00-\u9fa5a-zA-Z]+)[\s\-–—]+(.+)', line)
            if m:
                name, meaning = m.group(1).strip(), m.group(2).strip()
                if self._is_valid_name(name) and self._is_valid_meaning(meaning):
                    names.append({"name": name, "meaning": meaning, "source": "aistudio"})
                continue
            m2 = re.search(r'\d+\.?\s*([\u4e00-\u9fa5a-zA-Z]+)[\s\-–—]+(.+)', line)
            if m2:
                name, meaning = m2.group(1).strip(), m2.group(2).strip()
                if self._is_valid_name(name) and self._is_valid_meaning(meaning):
                    names.append({"name": name, "meaning": meaning, "source": "aistudio"})
                continue
        return names

    def _is_candidate_line(self, line: str) -> bool:
        if not line:
            return False
        bad = ["例如", "示例", "参考", "格式", "输出", "要求", "System", "system", "提示", "说明"]
        for b in bad:
            if b in line:
                return False
        return True

    def _is_valid_name(self, name: str) -> bool:
        import re
        if not name:
            return False
        if name in ["例如", "示例", "参考"]:
            return False
        if len(name) < 2 or len(name) > 10:
            return False
        return bool(re.search(r'[\u4e00-\u9fa5]', name))

    def _is_valid_meaning(self, meaning: str) -> bool:
        if not meaning:
            return False
        bad = ["根据角色描述生成", "示例", "例如", "参考", "格式"]
        for b in bad:
            if b in meaning:
                return False
        return len(meaning) >= 2

register_adapter("aistudio", lambda cfg: AistudioAdapter(cfg))
