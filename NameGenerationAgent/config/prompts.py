"""
提示词模板配置
"""
from typing import Dict, List

class PromptTemplates:
    """提示词模板管理"""
    
    # 基础姓名生成提示词
    BASE_NAME_GENERATION_PROMPT = """你是一个专业的姓名生成专家，擅长根据角色描述生成具有文化内涵和美感的姓名。

请根据以下角色描述，生成{count}个符合要求的姓名：

角色描述：{description}

要求：
1. 姓名要符合角色的性格特点和背景设定
2. 具有文化内涵和美感
3. 朗朗上口，易于记忆
4. 避免过于生僻或难读的字
5. 考虑姓名的寓意和象征意义

**重要：请严格按照以下格式输出，不要添加任何其他内容：**

格式要求：
- 每行必须以数字开头，格式为"数字. 姓名："
- 姓名和含义之间用" - "分隔
- 不要添加序号以外的任何前缀
- 不要添加解释性文字
- 严格按照要求的数量生成

示例格式：
1. 姓名：张三 - 勇敢的战士
2. 姓名：李四 - 智慧的法师
3. 姓名：王五 - 正直的骑士"""

    # 文化风格提示词
    CULTURAL_STYLE_PROMPTS = {
        'chinese_traditional': """
请生成具有中国传统文化特色的姓名，考虑：
- 古典诗词的意境
- 传统美德和价值观
- 五行相生相克的理念
- 古代文人雅士的命名风格
""",
        'chinese_modern': """
请生成具有现代感的中国姓名，考虑：
- 现代审美和流行趋势
- 简洁大方的风格
- 积极向上的寓意
- 易于书写和记忆
""",
        'fantasy': """
请生成具有奇幻色彩的姓名，考虑：
- 神秘感和想象力
- 独特的音韵美感
- 符合奇幻世界的设定
- 具有魔幻色彩的字词
""",
        'western': """
请生成具有西方文化特色的姓名，考虑：
- 西方命名传统（名字 + 姓氏）
- 音韵的和谐美感
- 现代国际化的风格
- 易于国际交流

**重要格式要求：**
- 必须同时提供英文名和中文译名
- 格式：英文名（中文译名）
- 示例：John Smith（约翰·史密斯）、Emma Watson（艾玛·沃森）
- 每行格式：数字. 姓名：英文名（中文译名） - 含义说明
""",
        'japanese': """
请生成具有日本文化特色的姓名，考虑：
- 日本传统命名习惯（姓氏 + 名字）
- 常见的日本姓氏（如：佐藤、铃木、田中、山本等）
- 优美的日文汉字组合
- 符合日本文化的寓意
- 音韵和谐，易于发音

**格式要求：**
- 使用日文汉字
- 姓氏在前，名字在后
- 示例：佐藤美咲、山田太郎、铃木花子
- 每行格式：数字. 姓名：日文姓名 - 含义说明
"""
    }
    
    # 性别特定提示词
    GENDER_PROMPTS = {
        'male': "请生成适合男性的姓名，体现阳刚、坚强、智慧等特质。",
        'female': "请生成适合女性的姓名，体现温柔、美丽、聪慧等特质。",
        'neutral': "请生成中性化的姓名，适合任何性别。"
    }
    
    # 年龄特定提示词
    AGE_PROMPTS = {
        'child': "请生成适合儿童的姓名，体现活泼、可爱、纯真等特质。",
        'teen': "请生成适合青少年的姓名，体现青春、活力、梦想等特质。",
        'adult': "请生成适合成年人的姓名，体现成熟、稳重、专业等特质。",
        'elder': "请生成适合长者的姓名，体现智慧、慈祥、德高望重等特质。"
    }
    
    # 语料库增强提示词
    CORPUS_ENHANCEMENT_PROMPTS = {
        'realistic': """
参考以下真实姓名示例：
{examples}

请确保生成的姓名符合中文姓名的常见结构和习惯，避免生僻字组合。
""",
        'chengyu': """
参考以下成语取名示例：
{examples}

请生成具有成语意境的姓名，体现深厚的文化内涵。
""",
        'thematic': """
参考以下主题姓名示例：
{examples}

请生成符合主题风格的姓名，体现特定的文化特色。
"""
    }
    
    @classmethod
    def build_prompt(cls, description: str, count: int = 5, 
                    cultural_style: str = 'chinese_modern',
                    gender: str = 'neutral', age: str = 'adult',
                    corpus_examples: List[str] = None, 
                    enhancement_type: str = 'realistic') -> str:
        """构建完整的提示词"""
        
        # 基础提示词
        prompt = cls.BASE_NAME_GENERATION_PROMPT.format(
            count=count,
            description=description
        )
        
        # 添加文化风格
        if cultural_style in cls.CULTURAL_STYLE_PROMPTS:
            prompt += cls.CULTURAL_STYLE_PROMPTS[cultural_style]
        
        # 添加性别要求
        if gender in cls.GENDER_PROMPTS:
            prompt += cls.GENDER_PROMPTS[gender]
        
        # 添加年龄要求
        if age in cls.AGE_PROMPTS:
            prompt += cls.AGE_PROMPTS[age]
        
        # 添加语料库增强示例
        if corpus_examples and enhancement_type in cls.CORPUS_ENHANCEMENT_PROMPTS:
            examples_str = ", ".join(corpus_examples[:5])  # 只取前5个示例
            prompt += cls.CORPUS_ENHANCEMENT_PROMPTS[enhancement_type].format(
                examples=examples_str
            )
        
        return prompt.strip()
    
    @classmethod
    def get_available_styles(cls) -> List[str]:
        """获取可用的文化风格"""
        return list(cls.CULTURAL_STYLE_PROMPTS.keys())
    
    @classmethod
    def get_available_genders(cls) -> List[str]:
        """获取可用的性别选项"""
        return list(cls.GENDER_PROMPTS.keys())
    
    @classmethod
    def get_available_ages(cls) -> List[str]:
        """获取可用的年龄选项"""
        return list(cls.AGE_PROMPTS.keys())
    
    @classmethod
    def get_available_enhancement_types(cls) -> List[str]:
        """获取可用的语料库增强类型"""
        return list(cls.CORPUS_ENHANCEMENT_PROMPTS.keys())

# 系统提示词
SYSTEM_PROMPTS = {
    'name_generator': """你是一个专业的姓名生成专家，擅长根据角色描述生成具有文化内涵和美感的姓名。

你的任务是：
1. 根据用户提供的角色描述生成指定数量的姓名
2. 严格按照指定的格式输出结果
3. 确保每个姓名都有明确的寓意解释
4. 不添加任何额外的解释或说明文字

输出格式要求：
- 每行格式：数字. 姓名：{姓名} - {寓意}
- 严格按照要求的数量生成
- 不要添加任何前缀或后缀文字""",
    'name_analyzer': "你是一个姓名分析专家，能够分析姓名的寓意、音韵和文化内涵。",
    'name_validator': "你是一个姓名验证专家，能够检查姓名的合理性和文化适宜性。"
}
