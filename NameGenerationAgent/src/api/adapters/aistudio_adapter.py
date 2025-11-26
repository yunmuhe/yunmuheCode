from .base_adapter import BaseAPIAdapter

class AistudioAdapter(BaseAPIAdapter):
    def __init__(self, config):
        super().__init__(config)
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=config.api_key, base_url=config.base_url)
        except Exception as e:
            print("[AistudioAdapter] OpenAI客户端初始化失败:", e)
        # 不使用__name__，不存储日志器，初始化只使用print提示

    def generate_names(self, prompt, count=5, **kwargs):
        completion_params = self.config.get_completion_params()
        messages = [
            {"role": "system", "content": "你是一个专业的姓名生成专家。"},
            {"role": "user", "content": prompt}
        ]
        stream = kwargs.get("stream", completion_params["stream"])
        response = self.client.chat.completions.create(
            model=completion_params["model"],
            messages=messages,
            stream=stream,
            max_tokens=completion_params["max_tokens"],
            temperature=kwargs.get("temperature", 0.7)
        )
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
            names = self._parse_names(generated_text)
            return {
                "success": True,
                "names": names,
                "raw_response": generated_text,
                "api_name": self.name,
                "model": completion_params["model"],
                "stream": True
            }
        else:
            content = response.choices[0].message.content
            names = self._parse_names(content)
            return {
                "success": True,
                "names": names,
                "raw_response": content,
                "api_name": self.name,
                "model": completion_params["model"],
                "stream": False
            }

    def _parse_names(self, text):
        names = []
        import re
        lines = text.strip().split('\n')
        for line in lines:
            line = line.strip()
            # 修复正则表达式：将 [\s-–—] 改为 [\s\-–—]，转义减号
            m = re.search(r'\d+\.?\s*姓名[：:]{0,1}\s*([\u4e00-\u9fa5a-zA-Z]+)[\s\-–—]+(.+)', line)
            if m:
                name, meaning = m.group(1).strip(), m.group(2).strip()
                names.append({"name": name, "meaning": meaning, "source": "aistudio"})
                continue
            m2 = re.search(r'\d+\.?\s*([\u4e00-\u9fa5a-zA-Z]+)[\s\-–—]+(.+)', line)
            if m2:
                name, meaning = m2.group(1).strip(), m2.group(2).strip()
                names.append({"name": name, "meaning": meaning, "source": "aistudio"})
                continue
            if 2 <= len(line) <= 10 and re.search(r'[\u4e00-\u9fa5a-zA-Z]', line):
                names.append({"name": line, "meaning": "根据角色描述生成", "source": "aistudio"})
        return names
