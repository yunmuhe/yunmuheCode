"""
测试语料库集成功能
"""
import unittest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestCorpusIntegration(unittest.TestCase):
    """测试语料库集成功能"""
    
    def setUp(self):
        """测试前准备"""
        from src.core.name_generator import NameGenerator
        self.generator = NameGenerator()
    
    def test_corpus_enhancer_initialization(self):
        """测试语料库增强器初始化"""
        # 检查语料库增强器是否正确加载
        self.assertIsNotNone(self.generator.corpus_enhancer)
        
        # 如果语料库增强器存在，检查其基本功能
        if self.generator.corpus_enhancer:
            # 测试获取语料库统计信息
            stats = self.generator.corpus_enhancer.get_corpus_stats()
            self.assertIsInstance(stats, dict)
            self.assertIn('现代人名总数', stats)
            self.assertIn('古代人名总数', stats)
            self.assertIn('成语总数', stats)
    
    def test_prompt_enhancement(self):
        """测试提示词增强功能"""
        description = "一个勇敢的战士"
        options = {
            'gender': 'male',
            'cultural_style': 'chinese_traditional'
        }
        
        # 如果语料库增强器存在，测试提示词增强
        if self.generator.corpus_enhancer:
            enhanced_prompt = self.generator.corpus_enhancer.enhance_prompt(
                description, options
            )
            self.assertIsInstance(enhanced_prompt, str)
            self.assertGreater(len(enhanced_prompt), 0)
    
    def test_name_suggestions(self):
        """测试姓名建议功能"""
        keyword = "勇"
        
        # 如果语料库增强器存在，测试姓名建议功能
        if self.generator.corpus_enhancer:
            suggestions = self.generator.corpus_enhancer.get_name_suggestions(keyword)
            self.assertIsInstance(suggestions, list)
    
    def test_chengyu_names(self):
        """测试成语姓名生成功能"""
        # 如果语料库增强器存在，测试成语姓名生成功能
        if self.generator.corpus_enhancer:
            chengyu_names = self.generator.corpus_enhancer.get_chengyu_names()
            self.assertIsInstance(chengyu_names, list)
    
    def test_full_generation_with_corpus(self):
        """测试完整的姓名生成功能（结合语料库）"""
        result = self.generator.generate_names(
            description="一个聪明好学的孩子",
            count=3,
            cultural_style='chinese_modern',
            gender='neutral'
        )
        
        # 检查生成结果的基本结构
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
        self.assertIn('names', result)
        
        # 如果生成成功，检查生成的姓名
        if result['success']:
            self.assertGreater(len(result['names']), 0)
            for name_obj in result['names']:
                self.assertIn('name', name_obj)
                self.assertIn('meaning', name_obj)
                self.assertIn('features', name_obj)

class TestPromptTemplatesWithCorpus(unittest.TestCase):
    """测试结合语料库的提示词模板"""
    
    def setUp(self):
        """测试前准备"""
        from config.prompts import PromptTemplates
        self.templates = PromptTemplates()
    
    def test_build_prompt_with_corpus_examples(self):
        """测试构建带语料库示例的提示词"""
        # 构建基础提示词
        prompt = self.templates.build_prompt(
            description="一个智慧的学者",
            count=5,
            cultural_style='chinese_traditional',
            gender='male'
        )
        
        self.assertIsInstance(prompt, str)
        self.assertIn("智慧", prompt)
        self.assertIn("学者", prompt)
    
    def test_get_available_enhancement_types(self):
        """测试获取可用的增强类型"""
        if hasattr(self.templates, 'get_available_enhancement_types'):
            enhancement_types = self.templates.get_available_enhancement_types()
            self.assertIsInstance(enhancement_types, list)

if __name__ == '__main__':
    unittest.main()