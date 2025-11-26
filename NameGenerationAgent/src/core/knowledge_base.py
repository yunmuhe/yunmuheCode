"""
知识库管理
"""
import json
import os
from typing import Dict, Any, List, Optional
from ..config.settings import Config
from ..utils.logger import get_logger

logger = get_logger(__name__)

class KnowledgeBase:
    """知识库管理器"""
    
    def __init__(self):
        self.data_dir = Config.DATA_DIR
        self.knowledge_file = os.path.join(self.data_dir, 'knowledge_base.json')
        self.knowledge_data = {}
        self._load_knowledge()
    
    def _load_knowledge(self):
        """加载知识库数据"""
        try:
            if os.path.exists(self.knowledge_file):
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    self.knowledge_data = json.load(f)
                logger.info(f"加载知识库数据，共 {len(self.knowledge_data)} 个条目")
            else:
                self.knowledge_data = self._initialize_default_knowledge()
                self._save_knowledge()
                logger.info("创建默认知识库")
        except Exception as e:
            logger.error(f"加载知识库失败: {str(e)}")
            self.knowledge_data = self._initialize_default_knowledge()
    
    def _initialize_default_knowledge(self) -> Dict[str, Any]:
        """初始化默认知识库"""
        return {
            'chinese_surnames': [
                '王', '李', '张', '刘', '陈', '杨', '赵', '黄', '周', '吴',
                '徐', '孙', '胡', '朱', '高', '林', '何', '郭', '马', '罗',
                '梁', '宋', '郑', '谢', '韩', '唐', '冯', '于', '董', '萧',
                '程', '曹', '袁', '邓', '许', '傅', '沈', '曾', '彭', '吕',
                '苏', '卢', '蒋', '蔡', '贾', '丁', '魏', '薛', '叶', '阎'
            ],
            'chinese_given_names': {
                'male': [
                    '伟', '强', '磊', '军', '勇', '峰', '明', '超', '涛', '亮',
                    '华', '刚', '辉', '鹏', '飞', '龙', '杰', '斌', '浩', '宇',
                    '博', '文', '志', '建', '国', '海', '山', '仁', '波', '宁',
                    '福', '生', '龙', '元', '思', '智', '振', '嘉', '俊', '天'
                ],
                'female': [
                    '丽', '敏', '静', '秀', '英', '华', '慧', '巧', '美', '娜',
                    '欣', '雅', '婷', '雪', '梅', '兰', '竹', '菊', '莲', '荷',
                    '春', '夏', '秋', '冬', '月', '星', '云', '雨', '风', '花',
                    '梦', '诗', '画', '音', '韵', '香', '甜', '美', '好', '佳'
                ],
                'neutral': [
                    '文', '武', '德', '才', '智', '慧', '明', '亮', '清', '雅',
                    '正', '直', '诚', '信', '仁', '义', '礼', '智', '信', '和',
                    '平', '安', '康', '乐', '福', '寿', '喜', '庆', '吉', '祥'
                ]
            },
            'name_meanings': {
                'positive': [
                    '智慧', '勇敢', '善良', '美丽', '聪明', '坚强', '温柔', '优雅',
                    '才华', '品德', '成功', '幸福', '健康', '长寿', '富贵', '吉祥',
                    '和谐', '和平', '光明', '希望', '梦想', '自由', '快乐', '真诚'
                ],
                'nature': [
                    '山', '水', '花', '草', '树', '鸟', '鱼', '云', '风', '雨',
                    '雪', '月', '星', '日', '天', '地', '海', '江', '河', '湖'
                ],
                'virtues': [
                    '仁', '义', '礼', '智', '信', '忠', '孝', '廉', '耻', '勇',
                    '勤', '俭', '诚', '实', '善', '良', '正', '直', '公', '平'
                ]
            },
            'cultural_references': {
                'chinese_traditional': {
                    'poetry': [
                        '李白', '杜甫', '苏轼', '辛弃疾', '李清照', '陆游', '王维', '孟浩然'
                    ],
                    'philosophy': [
                        '孔子', '孟子', '老子', '庄子', '荀子', '墨子', '韩非子', '孙子'
                    ],
                    'history': [
                        '秦始皇', '汉武帝', '唐太宗', '宋太祖', '明太祖', '康熙', '乾隆'
                    ]
                },
                'modern': {
                    'celebrities': [
                        '马云', '马化腾', '李彦宏', '刘强东', '雷军', '任正非', '董明珠'
                    ],
                    'artists': [
                        '成龙', '李连杰', '周杰伦', '王菲', '邓丽君', '张学友', '刘德华'
                    ]
                }
            },
            'name_patterns': {
                'chinese': {
                    'surname_first': True,
                    'common_lengths': [2, 3],
                    'rare_lengths': [1, 4],
                    'avoid_characters': ['死', '病', '穷', '苦', '难', '凶', '恶']
                },
                'english': {
                    'surname_last': True,
                    'common_lengths': [2, 3],
                    'rare_lengths': [1, 4],
                    'avoid_words': ['death', 'sick', 'poor', 'bad', 'evil', 'hate']
                }
            }
        }
    
    def _save_knowledge(self):
        """保存知识库数据"""
        try:
            Config.ensure_directories()
            with open(self.knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_data, f, ensure_ascii=False, indent=2)
            logger.info("知识库数据已保存")
        except Exception as e:
            logger.error(f"保存知识库失败: {str(e)}")
    
    def get_surnames(self, culture: str = 'chinese') -> List[str]:
        """获取姓氏列表"""
        if culture == 'chinese':
            return self.knowledge_data.get('chinese_surnames', [])
        return []
    
    def get_given_names(self, gender: str = 'neutral', culture: str = 'chinese') -> List[str]:
        """获取名字列表"""
        if culture == 'chinese':
            given_names = self.knowledge_data.get('chinese_given_names', {})
            return given_names.get(gender, given_names.get('neutral', []))
        return []
    
    def get_name_meanings(self, category: str = 'positive') -> List[str]:
        """获取姓名寓意列表"""
        meanings = self.knowledge_data.get('name_meanings', {})
        return meanings.get(category, [])
    
    def get_cultural_references(self, style: str = 'chinese_traditional') -> Dict[str, List[str]]:
        """获取文化参考"""
        references = self.knowledge_data.get('cultural_references', {})
        return references.get(style, {})
    
    def get_name_patterns(self, culture: str = 'chinese') -> Dict[str, Any]:
        """获取命名模式"""
        patterns = self.knowledge_data.get('name_patterns', {})
        return patterns.get(culture, {})
    
    def add_surname(self, surname: str, culture: str = 'chinese'):
        """添加姓氏"""
        if culture == 'chinese':
            surnames = self.knowledge_data.get('chinese_surnames', [])
            if surname not in surnames:
                surnames.append(surname)
                self.knowledge_data['chinese_surnames'] = surnames
                self._save_knowledge()
                logger.info(f"添加姓氏: {surname}")
    
    def add_given_name(self, name: str, gender: str = 'neutral', culture: str = 'chinese'):
        """添加名字"""
        if culture == 'chinese':
            given_names = self.knowledge_data.get('chinese_given_names', {})
            if gender not in given_names:
                given_names[gender] = []
            
            if name not in given_names[gender]:
                given_names[gender].append(name)
                self.knowledge_data['chinese_given_names'] = given_names
                self._save_knowledge()
                logger.info(f"添加名字: {name} ({gender})")
    
    def add_name_meaning(self, meaning: str, category: str = 'positive'):
        """添加姓名寓意"""
        meanings = self.knowledge_data.get('name_meanings', {})
        if category not in meanings:
            meanings[category] = []
        
        if meaning not in meanings[category]:
            meanings[category].append(meaning)
            self.knowledge_data['name_meanings'] = meanings
            self._save_knowledge()
            logger.info(f"添加寓意: {meaning} ({category})")
    
    def search_names(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索姓名"""
        results = []
        query = query.lower()
        
        # 搜索姓氏
        surnames = self.get_surnames()
        for surname in surnames:
            if query in surname.lower():
                results.append({
                    'type': 'surname',
                    'name': surname,
                    'culture': 'chinese'
                })
        
        # 搜索名字
        for gender in ['male', 'female', 'neutral']:
            given_names = self.get_given_names(gender)
            for name in given_names:
                if query in name.lower():
                    results.append({
                        'type': 'given_name',
                        'name': name,
                        'gender': gender,
                        'culture': 'chinese'
                    })
        
        return results[:limit]
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        surnames = self.get_surnames()
        given_names = self.knowledge_data.get('chinese_given_names', {})
        
        return {
            'total_surnames': len(surnames),
            'total_given_names': sum(len(names) for names in given_names.values()),
            'male_names': len(given_names.get('male', [])),
            'female_names': len(given_names.get('female', [])),
            'neutral_names': len(given_names.get('neutral', [])),
            'total_meanings': sum(len(meanings) for meanings in self.knowledge_data.get('name_meanings', {}).values()),
            'cultural_references': len(self.knowledge_data.get('cultural_references', {})),
            'knowledge_file': self.knowledge_file
        }

# 全局知识库实例
knowledge_base = KnowledgeBase()
