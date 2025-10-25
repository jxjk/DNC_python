"""
数据验证器模块
提供数据验证功能
"""

import re
from typing import Dict, Any, List, Optional, Union


class DataValidator:
    """数据验证器类"""
    
    def __init__(self):
        """初始化验证器"""
        self._rules = {
            'integer': r'^-?\d+$',
            'float': r'^-?\d+(\.\d+)?$',
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'ip_address': r'^(\d{1,3}\.){3}\d{1,3}$',
            'date': r'^\d{4}-\d{2}-\d{2}$',
            'time': r'^\d{2}:\d{2}(:\d{2})?$',
            'phone': r'^1[3-9]\d{9}$',
            'url': r'^https?://[^\s/$.?#].[^\s]*$'
        }
        self._custom_rules = {}
    
    def validate_value(self, value: str, rule_type: str, **kwargs) -> Dict[str, Any]:
        """
        验证单个值
        
        Args:
            value: 要验证的值
            rule_type: 验证规则类型
            **kwargs: 额外参数
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        errors = []
        warnings = []
        
        if value is None:
            return {
                'valid': False,
                'errors': ['值不能为空'],
                'warnings': warnings
            }
        
        # 检查自定义规则
        if rule_type in self._custom_rules:
            pattern = self._custom_rules[rule_type]
            if not re.match(pattern, str(value)):
                errors.append(f'值 "{value}" 不符合自定义规则 "{rule_type}"')
        
        # 检查内置规则
        elif rule_type in self._rules:
            pattern = self._rules[rule_type]
            if not re.match(pattern, str(value)):
                errors.append(f'值 "{value}" 不符合规则 "{rule_type}"')
        
        # 特殊规则处理
        elif rule_type == 'range':
            try:
                num = float(value)
                min_val = kwargs.get('min', float('-inf'))
                max_val = kwargs.get('max', float('inf'))
                if num < min_val or num > max_val:
                    errors.append(f'值 "{value}" 不在范围 [{min_val}, {max_val}] 内')
            except ValueError:
                errors.append(f'值 "{value}" 不是有效的数字')
        
        elif rule_type == 'length':
            str_value = str(value)
            min_len = kwargs.get('min_length', 0)
            max_len = kwargs.get('max_length', float('inf'))
            if len(str_value) < min_len or len(str_value) > max_len:
                errors.append(f'长度 {len(str_value)} 不在范围 [{min_len}, {max_len}] 内')
        
        elif rule_type == 'enum':
            allowed_values = kwargs.get('allowed_values', [])
            if value not in allowed_values:
                errors.append(f'值 "{value}" 不在允许的值列表中: {allowed_values}')
        
        else:
            warnings.append(f'未知的验证规则类型: {rule_type}')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
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
            
            # 检查必填字段 - 包括空字符串的情况
            if required and (field_value is None or field_value == ""):
                errors.append(f'必填字段 "{field}" 为空')
                continue
            
            # 如果字段为空且非必填，跳过验证
            if (field_value is None or field_value == "") and not required:
                validated_data[field] = None
                continue
            
            # 验证字段值
            rule_type = field_schema.get('type', 'string')
            
            # 对于string类型，默认总是有效
            if rule_type == 'string':
                validated_data[field] = field_value
                continue
                
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
        valid_rows = []
        invalid_rows = []
        total_errors = []
        
        for i, row in enumerate(csv_data, 1):
            result = self.validate_data_structure(row, schema)
            if result['valid']:
                valid_rows.append(row)
            else:
                invalid_rows.append({
                    'row_number': i,
                    'row_data': row,
                    'errors': result['errors']
                })
                total_errors.extend(result['errors'])
        
        return {
            'valid': len(invalid_rows) == 0,
            'total_rows': len(csv_data),
            'valid_rows': len(valid_rows),
            'invalid_rows': len(invalid_rows),
            'valid_data': valid_rows,
            'invalid_data': invalid_rows,
            'errors': total_errors
        }
    
    def validate_numeric_range(self, value: Union[int, float], min_value: float = None, max_value: float = None) -> Dict[str, Any]:
        """
        验证数值范围
        
        Args:
            value: 要验证的数值
            min_value: 最小值
            max_value: 最大值
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        errors = []
        
        if min_value is not None and value < min_value:
            errors.append(f'值 {value} 小于最小值 {min_value}')
        
        if max_value is not None and value > max_value:
            errors.append(f'值 {value} 大于最大值 {max_value}')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': []
        }
    
    def validate_string_length(self, value: str, min_length: int = None, max_length: int = None) -> Dict[str, Any]:
        """
        验证字符串长度
        
        Args:
            value: 要验证的字符串
            min_length: 最小长度
            max_length: 最大长度
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        errors = []
        length = len(value)
        
        if min_length is not None and length < min_length:
            errors.append(f'长度 {length} 小于最小长度 {min_length}')
        
        if max_length is not None and length > max_length:
            errors.append(f'长度 {length} 大于最大长度 {max_length}')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': []
        }
    
    def validate_enum(self, value: Any, allowed_values: List[Any]) -> Dict[str, Any]:
        """
        验证枚举值
        
        Args:
            value: 要验证的值
            allowed_values: 允许的值列表
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        errors = []
        
        if value not in allowed_values:
            errors.append(f'值 "{value}" 不在允许的值列表中: {allowed_values}')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': []
        }
    
    def add_custom_rule(self, rule_name: str, pattern: str) -> bool:
        """
        添加自定义验证规则
        
        Args:
            rule_name: 规则名称
            pattern: 正则表达式模式
            
        Returns:
            bool: 是否添加成功
        """
        if rule_name in self._rules or rule_name in self._custom_rules:
            return False
        
        self._custom_rules[rule_name] = pattern
        return True
    
    def get_available_rules(self) -> List[str]:
        """
        获取可用规则列表
        
        Returns:
            List[str]: 规则名称列表
        """
        return list(self._rules.keys()) + list(self._custom_rules.keys())
    
    def validate_date_format(self, value: str) -> Dict[str, Any]:
        """
        验证日期格式 (YYYY-MM-DD)
        
        Args:
            value: 日期字符串
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        return self.validate_value(value, 'date')
