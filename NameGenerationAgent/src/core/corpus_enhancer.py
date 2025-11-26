"""
基于语料库的姓名生成增强器
结合大语言模型和人名语料库，提供更智能的姓名推荐
"""
import random
from typing import List, Dict, Optional
from ..data.corpus_loader import get_corpus_loader

class CorpusEnhancer:
    """语料库增强器"""
    
    def __init__(self):
        self.corpus_loader = get_corpus_loader()
    
    def enhance_prompt(self, description: str, options: Dict = None) -> str:
        """
        使用语料库数据增强提示词
        
        Args:
            description: 原始角色描述
            options: 生成选项（性别、风格等）
            
        Returns:
            增强后的提示词
        """
        options = options or {}
        
        # 获取性别
        gender = options.get('gender')
        gender_map = {'male': '男', 'female': '女'}
        gender_zh = gender_map.get(gender) if gender else None
        
        # 获取文化风格
        cultural_style = options.get('cultural_style', 'chinese_modern')
        
        # 根据风格获取示例
        examples = self._get_style_examples(cultural_style, gender_zh)
        
        # 构建增强提示词
        enhanced = f"{description}\n\n"
        
        if examples:
            enhanced += f"参考示例姓名：{', '.join(examples[:5])}\n"
        
        return enhanced
    
    def get_name_suggestions(self, keywords: List[str], gender: str = None, count: int = 10) -> List[Dict[str, str]]:
        """
        基于关键词从语料库中获取姓名建议
        
        Args:
            keywords: 关键词列表
            gender: 性别过滤
            count: 返回数量
            
        Returns:
            姓名建议列表
        """
        gender_map = {'male': '男', 'female': '女'}
        gender_zh = gender_map.get(gender) if gender else None
        
        suggestions = []
        
        # 对每个关键词搜索
        for keyword in keywords:
            if len(keyword) > 0:
                # 取第一个字进行搜索
                char = keyword[0]
                matched = self.corpus_loader.search_names_by_char(char, gender_zh, limit=5)
                suggestions.extend(matched)
        
        # 去重
        seen = set()
        unique_suggestions = []
        for item in suggestions:
            if item['name'] not in seen:
                seen.add(item['name'])
                unique_suggestions.append(item)
        
        # 如果数量不足，随机补充
        if len(unique_suggestions) < count:
            random_names = self.corpus_loader.get_random_names(
                count=count - len(unique_suggestions),
                gender=gender_zh
            )
            unique_suggestions.extend(random_names)
        
        return unique_suggestions[:count]
    
    def get_chengyu_names(self, count: int = 5) -> List[Dict[str, str]]:
        """
        基于成语生成姓名建议
        
        Args:
            count: 返回数量
            
        Returns:
            成语姓名建议列表
        """
        chengyus = self.corpus_loader.get_chengyu_for_naming(count=count * 2)
        
        suggestions = []
        for item in chengyus[:count]:
            suggestions.append({
                'name': item['suggested_chars'],
                'meaning': f"取自成语「{item['chengyu']}」",
                'source': 'chengyu',
                'chengyu': item['chengyu']
            })
        
        return suggestions
    
    def filter_and_rank_names(self, generated_names: List[Dict], description: str) -> List[Dict]:
        """
        过滤和排序生成的姓名
        
        Args:
            generated_names: 大模型生成的姓名列表
            description: 原始描述
            
        Returns:
            过滤和排序后的姓名列表
        """
        # TODO: 实现基于语料库的姓名质量评估
        # 1. 检查姓名是否在语料库中（说明是常见/合理的姓名）
        # 2. 检查字的组合是否常见
        # 3. 根据描述关键词相关性排序
        
        return generated_names
    
    def _get_style_examples(self, style: str, gender: str = None) -> List[str]:
        """
        根据风格获取示例姓名
        
        Args:
            style: 文化风格
            gender: 性别
            
        Returns:
            示例姓名列表
        """
        if style in ['chinese_traditional', 'fantasy_chinese']:
            # 使用古代人名
            names = self.corpus_loader.load_ancient_names(limit=1000)
            return random.sample(names, min(10, len(names)))
        else:
            # 使用现代人名
            names_data = self.corpus_loader.get_random_names(count=20, gender=gender)
            return [n['name'] for n in names_data]
    
    def get_corpus_stats(self) -> Dict:
        """获取语料库统计信息"""
        return self.corpus_loader.get_stats()

# 全局单例
_corpus_enhancer = None

def get_corpus_enhancer() -> CorpusEnhancer:
    """获取全局语料库增强器实例"""
    global _corpus_enhancer
    if _corpus_enhancer is None:
        _corpus_enhancer = CorpusEnhancer()
    return _corpus_enhancer