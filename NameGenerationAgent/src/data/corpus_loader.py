"""
中文人名语料库加载器
加载Chinese-Names-Corpus数据集
"""
import os
import random
from typing import List, Dict, Optional, Tuple

class CorpusLoader:
    """语料库加载器"""
    
    def __init__(self, corpus_path: str = None):
        """
        初始化语料库加载器
        
        Args:
            corpus_path: 语料库根目录路径
        """
        if corpus_path is None:
            # 默认路径：项目根目录的上级目录
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            corpus_path = os.path.join(os.path.dirname(project_root), 'Chinese-Names-Corpus-master')
        
        self.corpus_path = corpus_path
        self.chinese_names_path = os.path.join(corpus_path, 'Chinese_Names_Corpus')
        self.dict_path = os.path.join(corpus_path, 'Chinese_Dict_Corpus')
        
        # 缓存数据
        self._names_cache = None
        self._names_gender_cache = None
        self._family_names_cache = None
        self._ancient_names_cache = None
        self._chengyu_cache = None
    
    def load_names(self, with_gender: bool = False, limit: int = None) -> List[str] | List[Dict[str, str]]:
        """
        加载中文人名语料库
        
        Args:
            with_gender: 是否包含性别信息
            limit: 限制加载数量，None表示全部加载
            
        Returns:
            人名列表，如果with_gender=True则返回字典列表
        """
        if with_gender:
            if self._names_gender_cache is None:
                file_path = os.path.join(self.chinese_names_path, 'Chinese_Names_Corpus_Gender（120W）.txt')
                self._names_gender_cache = self._load_gender_names(file_path)
            
            data = self._names_gender_cache
        else:
            if self._names_cache is None:
                file_path = os.path.join(self.chinese_names_path, 'Chinese_Names_Corpus（120W）.txt')
                self._names_cache = self._load_simple_names(file_path)
            
            data = self._names_cache
        
        if limit:
            return data[:limit]
        return data
    
    def load_ancient_names(self, limit: int = None) -> List[str]:
        """
        加载古代人名语料库
        
        Args:
            limit: 限制加载数量
            
        Returns:
            古代人名列表
        """
        if self._ancient_names_cache is None:
            file_path = os.path.join(self.chinese_names_path, 'Ancient_Names_Corpus（25W）.txt')
            self._ancient_names_cache = self._load_simple_names(file_path)
        
        data = self._ancient_names_cache
        if limit:
            return data[:limit]
        return data
    
    def load_chengyu(self, limit: int = None) -> List[str]:
        """
        加载成语词典
        
        Args:
            limit: 限制加载数量
            
        Returns:
            成语列表
        """
        if self._chengyu_cache is None:
            file_path = os.path.join(self.dict_path, 'ChengYu_Corpus（5W）.txt')
            self._chengyu_cache = self._load_simple_names(file_path)
        
        data = self._chengyu_cache
        if limit:
            return data[:limit]
        return data
    
    def get_random_names(self, count: int = 10, gender: str = None, style: str = 'modern') -> List[Dict[str, str]]:
        """
        随机获取人名
        
        Args:
            count: 数量
            gender: 性别过滤 ('男', '女', None表示不过滤)
            style: 风格 ('modern'现代, 'ancient'古代)
            
        Returns:
            人名字典列表
        """
        if style == 'ancient':
            names = self.load_ancient_names()
            # 古代人名没有性别标注，返回随机选择
            selected = random.sample(names, min(count, len(names)))
            return [{'name': name, 'gender': '未知', 'style': 'ancient'} for name in selected]
        else:
            names = self.load_names(with_gender=True)
            
            # 性别过滤
            if gender:
                names = [n for n in names if n['gender'] == gender]
            
            # 随机选择
            if len(names) > count:
                selected = random.sample(names, count)
            else:
                selected = names
            
            # 添加风格标记
            for name in selected:
                name['style'] = 'modern'
            
            return selected
    
    def search_names_by_char(self, char: str, gender: str = None, limit: int = 20) -> List[Dict[str, str]]:
        """
        根据字符搜索人名
        
        Args:
            char: 搜索的字符
            gender: 性别过滤
            limit: 返回数量限制
            
        Returns:
            匹配的人名列表
        """
        names = self.load_names(with_gender=True)
        
        # 筛选包含指定字符的人名
        matched = [n for n in names if char in n['name']]
        
        # 性别过滤
        if gender:
            matched = [n for n in matched if n['gender'] == gender]
        
        return matched[:limit]
    
    def get_chengyu_for_naming(self, count: int = 10) -> List[Dict[str, str]]:
        """
        获取适合取名的成语
        
        Args:
            count: 数量
            
        Returns:
            成语列表，包含成语和可提取的字
        """
        chengyus = self.load_chengyu()
        selected = random.sample(chengyus, min(count, len(chengyus)))
        
        result = []
        for chengyu in selected:
            if len(chengyu) == 4:  # 标准四字成语
                # 提取可用于取名的字（通常是后两个字）
                name_chars = chengyu[2:4]
                result.append({
                    'chengyu': chengyu,
                    'suggested_chars': name_chars,
                    'full_chars': list(chengyu)
                })
        
        return result
    
    def _load_simple_names(self, file_path: str) -> List[str]:
        """
        加载简单人名文件（每行一个人名）
        
        Args:
            file_path: 文件路径
            
        Returns:
            人名列表
        """
        if not os.path.exists(file_path):
            print(f"警告: 文件不存在 {file_path}")
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                names = [line.strip() for line in f if line.strip()]
            return names
        except Exception as e:
            print(f"加载文件失败 {file_path}: {e}")
            return []
    
    def _load_gender_names(self, file_path: str) -> List[Dict[str, str]]:
        """
        加载带性别的人名文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            人名字典列表 [{'name': '张三', 'gender': '男'}, ...]
        """
        if not os.path.exists(file_path):
            print(f"警告: 文件不存在 {file_path}")
            return []
        
        try:
            names = []
            with open(file_path, 'r', encoding='utf-8') as f:
                # 跳过标题行
                next(f, None)
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    parts = line.split(',')
                    if len(parts) == 2:
                        names.append({
                            'name': parts[0].strip(),
                            'gender': parts[1].strip()
                        })
            
            return names
        except Exception as e:
            print(f"加载文件失败 {file_path}: {e}")
            return []
    
    def get_stats(self) -> Dict[str, int]:
        """
        获取语料库统计信息
        
        Returns:
            统计字典
        """
        stats = {
            '现代人名总数': len(self.load_names()),
            '古代人名总数': len(self.load_ancient_names()),
            '成语总数': len(self.load_chengyu())
        }
        
        # 统计性别分布
        names_with_gender = self.load_names(with_gender=True)
        male_count = sum(1 for n in names_with_gender if n['gender'] == '男')
        female_count = sum(1 for n in names_with_gender if n['gender'] == '女')
        unknown_count = sum(1 for n in names_with_gender if n['gender'] == '未知')
        
        stats.update({
            '男性人名': male_count,
            '女性人名': female_count,
            '性别未知': unknown_count
        })
        
        return stats

# 全局单例
_corpus_loader = None

def get_corpus_loader() -> CorpusLoader:
    """获取全局语料库加载器实例"""
    global _corpus_loader
    if _corpus_loader is None:
        _corpus_loader = CorpusLoader()
    return _corpus_loader

