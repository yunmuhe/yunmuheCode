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
    
    def enhance_prompt(self, base_prompt: str, description: str, options: Dict = None) -> str:
        """
        使用语料库数据增强提示词

        Args:
            base_prompt: 已包含文化风格、性别、年龄等信息的基础提示词
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

        # 根据风格获取示例（仅对中文风格添加示例）
        examples = []
        if cultural_style in ['chinese_traditional', 'chinese_modern', 'chinese_classic']:
            examples = self._get_style_examples(cultural_style, gender_zh)

        # 在基础提示词后面添加语料库示例
        enhanced = base_prompt

        if examples:
            enhanced += f"\n\n参考以下真实姓名示例：{', '.join(examples[:5])}"
            enhanced += "\n请确保生成的姓名符合中文姓名的常见结构和习惯，避免生僻字组合。"

        preferred_surname = (options.get('preferred_surname') or '').strip() if isinstance(options, dict) else ''
        preferred_era = (options.get('preferred_era') or '').strip() if isinstance(options, dict) else ''
        era_map = {
            'pre_qin': '先秦', 'prehistoric': '先秦', 'xianqin': '先秦', '先秦': '先秦', '春秋': '先秦', '战国': '先秦',
            'qin': '秦', '秦': '秦', '秦代': '秦',
            'han': '汉', '汉': '汉', '汉代': '汉',
            'jin': '晋', '晋': '晋', '魏晋': '晋', '魏晋南北朝': '南北朝',
            'southern_and_northern_dynasties': '南北朝', 'nanbeichao': '南北朝', '南北朝': '南北朝',
            'sui': '隋', '隋': '隋', '隋代': '隋',
            'tang': '唐', '唐': '唐', '唐代': '唐',
            'five_dynasties': '五代十国', 'five_dynasties_and_ten_kingdoms': '五代十国', '五代十国': '五代十国', '五代': '五代十国',
            'song': '宋', '宋': '宋', '宋代': '宋',
            'liao': '辽', '辽': '辽', '辽代': '辽',
            'jin_dynasty_later': '金', 'jurchen_jin': '金', 'jin_later': '金', '金': '金',
            'yuan': '元', '元': '元', '元代': '元',
            'ming': '明', '明': '明', '明代': '明',
            'qing': '清', '清': '清', '清代': '清',
            'modern': '近现代', 'contemporary': '近现代', 'republic': '近现代', '民国': '近现代',
            '近现代': '近现代', '近代': '近现代', '现代': '近现代'
        }
        era_zh = era_map.get(preferred_era, '')
        if preferred_surname:
            enhanced += f"\n若可能，请优先使用姓氏：{preferred_surname}。"
        if era_zh:
            if era_zh == '近现代':
                enhanced += "\n若可能，请优先采用近现代风格的用字与审美。"
            else:
                enhanced += f"\n若可能，请参考{era_zh}代的命名风格与审美。"

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
    
    def filter_and_rank_names(self, generated_names: List[Dict], description: str, options: Dict = None) -> List[Dict]:
        """
        过滤和排序生成的姓名
        
        Args:
            generated_names: 大模型生成的姓名列表
            description: 原始描述
            
        Returns:
            过滤和排序后的姓名列表
        """
        options = options or {}
        preferred_surname = (options.get('preferred_surname') or '').strip()
        cultural_style = options.get('cultural_style', 'chinese_modern')
        surname_weight = float(options.get('surname_weight', 1.0) or 1.0)
        era_weight = float(options.get('era_weight', 1.0) or 1.0)
        preferred_era = (options.get('preferred_era') or '').strip()
        era_map = {
            'tang': '唐',
            'song': '宋',
            'yuan': '元',
            'ming': '明',
            'qing': '清',
            'modern': '近现代',
            'contemporary': '近现代',
            '近现代': '近现代',
            '近代': '近现代',
            '现代': '近现代',
            '唐': '唐',
            '宋': '宋',
            '元': '元',
            '明': '明',
            '清': '清'
        }
        era_zh = era_map.get(preferred_era, '')

        cleaned = []
        for item in generated_names:
            n = (item.get('name') or '').strip()
            m = (item.get('meaning') or '').strip()
            if not n or not m:
                continue
            if n in ['例如', '示例', '参考']:
                continue
            if m in ['例如', '示例', '参考', '根据角色描述生成']:
                continue
            exists = self.corpus_loader.name_exists(n)
            base_score = self.corpus_loader.char_presence_score(n)

            era_bonus = 0
            ancient_pref = cultural_style in ['chinese_traditional', 'chinese_classic']
            if era_zh and era_zh != '近现代':
                if self.corpus_loader.exists_in_dynasty(n, era_zh):
                    era_bonus = int(2500 * era_weight)
                elif self.corpus_loader.exists_ancient(n):
                    era_bonus = int(1000 * era_weight)
            else:
                if ancient_pref and self.corpus_loader.exists_ancient(n):
                    era_bonus = int(2000 * era_weight)
                elif (not ancient_pref) and self.corpus_loader.exists_modern(n):
                    era_bonus = int(2000 * era_weight)
                elif self.corpus_loader.exists_ancient(n) or self.corpus_loader.exists_modern(n):
                    era_bonus = int(500 * era_weight)

            surname_bonus = 0
            if preferred_surname and n.startswith(preferred_surname):
                surname_bonus = int(3000 * surname_weight)

            total_score = base_score + era_bonus + surname_bonus
            cleaned.append({
                'name': n,
                'meaning': m,
                'source': item.get('source', ''),
                'exists': exists,
                'score': total_score
            })

        cleaned.sort(key=lambda x: (not x['exists'], -x['score'], x['name']))
        return [{'name': c['name'], 'meaning': c['meaning'], 'source': 'corpus_rank'} for c in cleaned]
    
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
