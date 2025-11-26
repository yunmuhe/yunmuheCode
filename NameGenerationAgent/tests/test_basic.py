"""
测试文件
"""
import unittest
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.core.name_generator import NameGenerator
from src.utils.validation import InputValidator, NameValidator
from src.utils.cache_manager import CacheManager

class TestNameGenerator(unittest.TestCase):
    """姓名生成器测试"""
    
    def setUp(self):
        self.generator = NameGenerator()
    
    def test_get_available_options(self):
        """测试获取可用选项"""
        options = self.generator.get_available_options()
        self.assertIsInstance(options, dict)
        self.assertIn('cultural_styles', options)
        self.assertIn('genders', options)
        self.assertIn('ages', options)
        self.assertIn('apis', options)

class TestInputValidator(unittest.TestCase):
    """输入验证器测试"""
    
    def setUp(self):
        self.validator = InputValidator()
    
    def test_validate_description(self):
        """测试描述验证"""
        # 有效描述
        result = self.validator.validate_description("一个勇敢的骑士")
        self.assertTrue(result['valid'])
        
        # 空描述
        with self.assertRaises(Exception):
            self.validator.validate_description("")
        
        # 过短描述
        with self.assertRaises(Exception):
            self.validator.validate_description("骑士")
    
    def test_validate_name_count(self):
        """测试姓名数量验证"""
        # 有效数量
        result = self.validator.validate_name_count(5)
        self.assertTrue(result['valid'])
        
        # 无效数量
        with self.assertRaises(Exception):
            self.validator.validate_name_count(0)
        
        with self.assertRaises(Exception):
            self.validator.validate_name_count(25)

class TestNameValidator(unittest.TestCase):
    """姓名验证器测试"""
    
    def setUp(self):
        self.validator = NameValidator()
    
    def test_validate_chinese_name(self):
        """测试中文姓名验证"""
        # 有效中文姓名
        result = self.validator.validate_chinese_name("张三")
        self.assertTrue(result['valid'])
        
        # 无效姓名
        result = self.validator.validate_chinese_name("")
        self.assertFalse(result['valid'])
        
        result = self.validator.validate_chinese_name("a")
        self.assertFalse(result['valid'])

class TestCacheManager(unittest.TestCase):
    """缓存管理器测试"""
    
    def setUp(self):
        self.cache = CacheManager()
    
    def test_cache_operations(self):
        """测试缓存操作"""
        # 设置缓存
        self.cache.set("test_key", "test_value")
        
        # 获取缓存
        value = self.cache.get("test_key")
        self.assertEqual(value, "test_value")
        
        # 删除缓存
        result = self.cache.delete("test_key")
        self.assertTrue(result)
        
        # 获取不存在的缓存
        value = self.cache.get("test_key")
        self.assertIsNone(value)

if __name__ == '__main__':
    unittest.main()
