"""
数据验证器模块
负责数据格式和内容的验证
"""

import re
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime


class DataValidator:
    """数据验证器类"""
    
    def __init__(self):
        """初始化数据验证器"""
        self.logger = logging.getLogger(__name__)
        
        # 预定义验证规则
        self.validation_rules = {
            'integer': r'^-?\d+$',
            'float': r'^-?\d+(\.\d+)?$',
            'positive_integer': r'^\d+$',
            'positive_float': r'^\d+(\.\d+)?$',
            'alphanumeric': r'^[a-zA-Z0-9]+$',
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'date_yyyy_mm_dd': r'^\d{4}-\d{2}-\d{2}$',
            'time_hh_mm_ss': r'^\d{2}:\d{2}:\d{2}$',
            'mac_address': r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$',
            'ip_address': r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        }
    
    def validate_value(self, value: Any, rule_type: str, **kwargs) -> Dict[str, Any]:
        """
        验证单个值
        
        Args:
            value: 要验证的值
            rule_type: 验证规则类型
            **kwargs: 额外参数
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        try:
            # 如果值为None，根据配置决定是否允许
            if value is None:
                allow_none = kwargs.get('allow_none', False)
                return {
                    'valid': allow_none,
                    'errors': [] if allow_none else ['值不能为空'],
                    'warnings': []
                }
            
            # 转换为字符串进行验证
            str_value = str(value).strip()
            
            if rule_type in self.validation_rules:
                # 使用预定义规则
                pattern = self.validation_rules[rule_type]
                if re.match(pattern, str_value):
                    return {'valid': True, 'errors': [], 'warnings': []}
                else:
                    return {
                        'valid': False, 
                        'errors': [f'值 "{str_value}" 不符合 {rule_type} 格式'],
                        'warnings': []
                    }
            
            elif rule_type == 'custom':
                # 自定义正则表达式
                pattern = kwargs.get('pattern')
                if pattern and re.match(pattern, str_value):
                    return {'valid': True, 'errors': [], 'warnings': []}
                else:
                    return {
                        'valid': False,
                        'errors': [f'值 "{str_value}" 不符合自定义格式'],
                        'warnings': []
                    }
            
            elif rule_type == 'range':
                # 数值范围验证
                try:
                    num_value = float(str_value)
                    min_val = kwargs.get('min')
                    max_val = kwargs.get('max')
                    
                    errors = []
                    if min_val is not None and num_value < min_val:
                        errors.append(f'值不能小于 {min_val}')
                    if max_val is not None and num_value > max_val:
                        errors.append(f'值不能大于 {max_val}')
                    
                    return {
                        'valid': len(errors) == 0,
                        'errors': errors,
                        'warnings': []
                    }
                except ValueError:
                    return {
                        'valid': False,
                        'errors': ['值不是有效的数字'],
                        'warnings': []
                    }
            
            elif rule_type == 'length':
                # 长度验证
                min_len = kwargs.get('min_length')
                max_len = kwargs.get('max_length')
                
                errors = []
                if min_len is not None and len(str_value) < min_len:
                    errors.append(f'长度不能小于 {min_len}')
                if max_len is not None and len(str_value) > max_len:
                    errors.append(f'长度不能大于 {max_len}')
                
                return {
                    'valid': len(errors) == 0,
                    'errors': errors,
                    'warnings': []
                }
            
            elif rule_type == 'enum':
                # 枚举值验证
                allowed_values = kwargs.get('allowed_values', [])
                if str_value in allowed_values:
                    return {'valid': True, 'errors': [], 'warnings': []}
                else:
                    return {
                        'valid': False,
                        'errors': [f'值 "{str_value}" 不在允许的范围内: {allowed_values}'],
                        'warnings': []
                    }
            
            else:
                return {
                    'valid': False,
                    'errors': [f'不支持的验证规则类型: {rule_type}'],
                    'warnings': []
                }
                
        except Exception as e:
            self.logger.error(f"验证值失败: {value}, 规则: {rule_type}, 错误: {e}")
            return {
                'valid': False,
                'errors': [f'验证过程异常: {str(e)}'],
                'warnings': []
            }
    
    def validate_data_structure(self, data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证数据结构
        
        Args:
            data: 要验证的数据
            schema: 数据模式定义
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        errors = []
        warnings = []
        validated_data = {}
        
        for field, field_schema in schema.items():
            field_value = data.get(field)
            required = field_schema.get('required', True)
            
            # 检查必填字段
            if required and field_value is None:
                errors.append(f'必填字段 "{field}" 为空')
                continue
            
            # 如果字段为空且非必填，跳过验证
            if field_value is None and not required:
                validated_data[field] = None
                continue
            
            # 验证字段值
            rule_type = field_schema.get('type', 'string')
            validation_result = self.validate_value(
                field_value, 
                rule_type, 
                **field_schema.get('constraints', {})
            )
            
            if not validation_result['valid']:
                for error in validation_result['errors']:
                    errors.append(f'字段 "{field}": {error}')
            else:
                validated_data[field] = field_value
            
            if validation_result['warnings']:
                for warning in validation_result['warnings']:
                    warnings.append(f'字段 "{field}": {warning}')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'validated_data': validated_data
        }
    
    def validate_csv_data(self, csv_data: List[Dict[str, Any]], schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证CSV数据
        
        Args:
            csv_data: CSV数据列表
            schema: 数据模式定义
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        all_errors = []
        all_warnings = []
        valid_rows = []
        invalid_rows = []
        
        for row_num, row_data in enumerate(csv_data, 1):
            validation_result = self.validate_data_structure(row_data, schema)
            
            if validation_result['valid']:
                valid_rows.append(validation_result['validated_data'])
            else:
                invalid_rows.append({
                    'row_number': row_num,
                    'data': row_data,
                    'errors': validation_result['errors']
                })
            
            all_errors.extend([f"第{row_num}行: {error}" for error in validation_result['errors']])
            all_warnings.extend([f"第{row_num}行: {warning}" for warning in validation_result['warnings']])
        
        return {
            'valid': len(invalid_rows) == 0,
            'total_rows': len(csv_data),
            'valid_rows': len(valid_rows),
            'invalid_rows': len(invalid_rows),
            'errors': all_errors,
            'warnings': all_warnings,
            'valid_rows_data': valid_rows,
            'invalid_rows_details': invalid_rows
        }
    
    def validate_numeric_range(self, value: Any, min_value: Optional[float] = None, 
                              max_value: Optional[float] = None) -> Dict[str, Any]:
        """
        验证数值范围
        
        Args:
            value: 要验证的值
            min_value: 最小值
            max_value: 最大值
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        return self.validate_value(value, 'range', min=min_value, max=max_value)
    
    def validate_string_length(self, value: Any, min_length: Optional[int] = None,
                              max_length: Optional[int] = None) -> Dict[str, Any]:
        """
        验证字符串长度
        
        Args:
            value: 要验证的值
            min_length: 最小长度
            max_length: 最大长度
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        return self.validate_value(value, 'length', min_length=min_length, max_length=max_length)
    
    def validate_enum(self, value: Any, allowed_values: List[Any]) -> Dict[str, Any]:
        """
        验证枚举值
        
        Args:
            value: 要验证的值
            allowed_values: 允许的值列表
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        return self.validate_value(value, 'enum', allowed_values=allowed_values)
    
    def add_custom_rule(self, rule_name: str, pattern: str) -> bool:
        """
        添加自定义验证规则
        
        Args:
            rule_name: 规则名称
            pattern: 正则表达式模式
            
        Returns:
            bool: 添加是否成功
        """
        try:
            # 验证正则表达式是否有效
            re.compile(pattern)
            self.validation_rules[rule_name] = pattern
            self.logger.info(f"自定义验证规则添加成功: {rule_name}")
            return True
        except re.error as e:
            self.logger.error(f"添加自定义验证规则失败: {rule_name}, 错误: {e}")
            return False
    
    def get_available_rules(self) -> List[str]:
        """
        获取可用的验证规则
        
        Returns:
            List[str]: 规则名称列表
        """
        return list(self.validation_rules.keys())
    
    def validate_date_format(self, value: Any, date_format: str = '%Y-%m-%d') -> Dict[str, Any]:
        """
        验证日期格式
        
        Args:
            value: 要验证的值
            date_format: 日期格式
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        try:
            if value is None:
                return {'valid': False, 'errors': ['日期不能为空'], 'warnings': []}
            
            str_value = str(value).strip()
            datetime.strptime(str_value, date_format)
            return {'valid': True, 'errors': [], 'warnings': []}
        except ValueError:
            return {
                'valid': False,
                'errors': [f'日期 "{str_value}" 不符合格式 {date_format}'],
                'warnings': []
            }
        except Exception as e:
            self.logger.error(f"验证日期格式失败: {value}, 错误: {e}")
            return {
                'valid': False,
                'errors': [f'日期验证异常: {str(e)}'],
                'warnings': []
            }
