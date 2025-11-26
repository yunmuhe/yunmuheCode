"""
验证工具
"""
import re
from typing import List, Dict, Any, Optional
from .logger import get_logger

logger = get_logger(__name__)

class ValidationError(Exception):
    """验证错误异常"""
    pass

class InputValidator:
    """输入验证器"""
    
    @staticmethod
    def validate_description(description: str) -> Dict[str, Any]:
        """验证角色描述"""
        if not description:
            raise ValidationError("角色描述不能为空")
        
        if not isinstance(description, str):
            raise ValidationError("角色描述必须是字符串")
        
        # 去除首尾空格
        description = description.strip()
        
        if len(description) < 5:
            raise ValidationError("角色描述至少需要5个字符")
        
        if len(description) > 1000:
            raise ValidationError("角色描述不能超过1000个字符")
        
        # 检查是否包含敏感词
        sensitive_words = ['政治', '宗教', '暴力', '色情', '违法']
        for word in sensitive_words:
            if word in description:
                raise ValidationError(f"角色描述不能包含敏感词: {word}")
        
        return {
            'valid': True,
            'description': description,
            'length': len(description)
        }
    
    @staticmethod
    def validate_name_count(count: int) -> Dict[str, Any]:
        """验证姓名数量"""
        if not isinstance(count, int):
            raise ValidationError("姓名数量必须是整数")
        
        if count < 1:
            raise ValidationError("姓名数量至少为1")
        
        if count > 20:
            raise ValidationError("姓名数量不能超过20")
        
        return {
            'valid': True,
            'count': count
        }
    
    @staticmethod
    def validate_cultural_style(style: str) -> Dict[str, Any]:
        """验证文化风格"""
        valid_styles = ['chinese_traditional', 'chinese_modern', 'fantasy', 'western', 'japanese']

        if style not in valid_styles:
            raise ValidationError(f"无效的文化风格: {style}")

        return {
            'valid': True,
            'style': style
        }
    
    @staticmethod
    def validate_gender(gender: str) -> Dict[str, Any]:
        """验证性别"""
        valid_genders = ['male', 'female', 'neutral']
        
        if gender not in valid_genders:
            raise ValidationError(f"无效的性别: {gender}")
        
        return {
            'valid': True,
            'gender': gender
        }
    
    @staticmethod
    def validate_age(age: str) -> Dict[str, Any]:
        """验证年龄"""
        valid_ages = ['child', 'teen', 'adult', 'elder']
        
        if age not in valid_ages:
            raise ValidationError(f"无效的年龄: {age}")
        
        return {
            'valid': True,
            'age': age
        }

class NameValidator:
    """姓名验证器"""
    
    @staticmethod
    def validate_chinese_name(name: str) -> Dict[str, Any]:
        """验证中文姓名"""
        if not name:
            return {'valid': False, 'error': '姓名不能为空'}
        
        # 去除空格
        name = name.strip()
        
        # 检查长度
        if len(name) < 1:
            return {'valid': False, 'error': '姓名至少需要1个字符'}
        
        if len(name) > 15:
            return {'valid': False, 'error': '姓名不能超过15个字符'}
        
        # 检查是否包含中文字符
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
        if not chinese_pattern.search(name):
            return {'valid': False, 'error': '姓名必须包含中文字符'}
        
        # 检查是否包含过多非中文字符
        non_chinese_pattern = re.compile(r'[^\u4e00-\u9fff]')
        non_chinese_chars = non_chinese_pattern.findall(name)
        if len(non_chinese_chars) > len(name) * 2 // 3:  # 允许1/3的非中文字符
            return {'valid': False, 'error': '姓名包含过多非中文字符'}
        
        # 检查是否包含生僻字（简单检查）
        rare_chars = ['龖', '龘', '䨻', '䲜', '䴎', '䴏', '䴐', '䴑', '䴒', '䴓']
        for char in rare_chars:
            if char in name:
                return {'valid': False, 'error': '姓名包含生僻字，建议使用常用字'}
        
        return {
            'valid': True,
            'name': name,
            'length': len(name),
            'type': 'chinese'
        }
    
    @staticmethod
    def validate_english_name(name: str) -> Dict[str, Any]:
        """验证英文姓名"""
        if not name:
            return {'valid': False, 'error': '姓名不能为空'}
        
        # 去除空格
        name = name.strip()
        
        # 检查长度
        if len(name) < 2:
            return {'valid': False, 'error': '姓名至少需要2个字符'}
        
        if len(name) > 50:
            return {'valid': False, 'error': '姓名不能超过50个字符'}
        
        # 检查是否包含英文字符
        english_pattern = re.compile(r'^[a-zA-Z\s]+$')
        if not english_pattern.match(name):
            return {'valid': False, 'error': '英文姓名只能包含英文字母和空格'}
        
        return {
            'valid': True,
            'name': name,
            'length': len(name),
            'type': 'english'
        }
    
    @staticmethod
    def validate_name(name: str) -> Dict[str, Any]:
        """通用姓名验证"""
        if not name:
            return {'valid': False, 'error': '姓名不能为空'}
        
        # 去除空格
        name = name.strip()
        
        # 检查长度
        if len(name) < 1:
            return {'valid': False, 'error': '姓名不能为空'}
        
        if len(name) > 50:
            return {'valid': False, 'error': '姓名不能超过50个字符'}
        
        # 首先尝试清理姓名
        cleaned_name = name
        
        # 清理序号和标签
        cleaned_name = re.sub(r'^\d+\.?\s*', '', cleaned_name)  # 去掉序号
        cleaned_name = re.sub(r'^姓名[：:]\s*', '', cleaned_name)  # 去掉"姓名："
        cleaned_name = re.sub(r'[：:]\s*$', '', cleaned_name)  # 去掉结尾的冒号
        cleaned_name = cleaned_name.strip()
        
        # 如果清理后为空，使用原始姓名
        if not cleaned_name:
            cleaned_name = name
        
        # 检查是否包含中文字符
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
        if chinese_pattern.search(cleaned_name):
            # 中文姓名验证
            chinese_result = NameValidator.validate_chinese_name(cleaned_name)
            if chinese_result['valid']:
                return chinese_result
        
        # 检查是否包含英文字符
        english_pattern = re.compile(r'[a-zA-Z]+')
        if english_pattern.search(cleaned_name):
            # 英文姓名验证
            english_result = NameValidator.validate_english_name(cleaned_name)
            if english_result['valid']:
                return english_result
        
        # 如果包含中文字符但验证失败，尝试更宽松的验证
        if chinese_pattern.search(cleaned_name):
            # 检查是否主要是中文字符
            chinese_chars = chinese_pattern.findall(cleaned_name)
            chinese_text = ''.join(chinese_chars)
            if len(chinese_text) >= len(cleaned_name) // 2:
                return {
                    'valid': True,
                    'name': cleaned_name,
                    'length': len(cleaned_name),
                    'type': 'chinese'
                }
        
        # 如果包含英文字符但验证失败，尝试更宽松的验证
        if english_pattern.search(cleaned_name):
            # 检查是否主要是英文字符
            english_chars = english_pattern.findall(cleaned_name)
            english_text = ''.join(english_chars)
            if len(english_text) >= len(cleaned_name) // 2:
                return {
                    'valid': True,
                    'name': cleaned_name,
                    'length': len(cleaned_name),
                    'type': 'english'
                }
        
        # 最后的宽松验证：如果姓名长度合理且不全是特殊字符
        special_chars = re.findall(r'[^\u4e00-\u9fff\w\s]', cleaned_name)
        if len(special_chars) < len(cleaned_name) // 2 and len(cleaned_name) >= 1:
            return {
                'valid': True,
                'name': cleaned_name,
                'length': len(cleaned_name),
                'type': 'mixed'
            }
        
        # 都不符合，返回错误
        return {
            'valid': False,
            'error': '姓名格式不正确，请使用中文或英文姓名'
        }

class ResponseValidator:
    """响应验证器"""
    
    @staticmethod
    def validate_api_response(response: Dict[str, Any]) -> Dict[str, Any]:
        """验证API响应"""
        if not isinstance(response, dict):
            return {'valid': False, 'error': '响应必须是字典格式'}
        
        # 检查必要字段
        required_fields = ['success', 'names']
        for field in required_fields:
            if field not in response:
                return {'valid': False, 'error': f'响应缺少必要字段: {field}'}
        
        # 检查success字段
        if not isinstance(response['success'], bool):
            return {'valid': False, 'error': 'success字段必须是布尔值'}
        
        # 检查names字段
        if not isinstance(response['names'], list):
            return {'valid': False, 'error': 'names字段必须是列表'}
        
        # 验证每个姓名
        for i, name_data in enumerate(response['names']):
            if not isinstance(name_data, dict):
                return {'valid': False, 'error': f'第{i+1}个姓名数据格式错误'}
            
            if 'name' not in name_data:
                return {'valid': False, 'error': f'第{i+1}个姓名缺少name字段'}
            
            # 验证姓名
            name_validation = NameValidator.validate_name(name_data['name'])
            if not name_validation['valid']:
                return {'valid': False, 'error': f'第{i+1}个姓名无效: {name_validation["error"]}'}
        
        return {
            'valid': True,
            'names_count': len(response['names'])
        }
