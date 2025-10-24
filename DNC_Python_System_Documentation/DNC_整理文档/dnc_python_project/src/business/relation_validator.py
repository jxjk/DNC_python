"""
关系验证器模块
负责验证参数之间的逻辑关系
"""

import logging
from typing import Dict, Any, List, Optional
from src.core.config import ConfigManager
from src.data.csv_processor import CSVProcessor


class RelationValidator:
    """关系验证器类"""
    
    def __init__(self, config_manager: ConfigManager, csv_processor: CSVProcessor):
        """
        初始化关系验证器
        
        Args:
            config_manager: 配置管理器实例
            csv_processor: CSV处理器实例
        """
        self.config_manager = config_manager
        self.csv_processor = csv_processor
        self.logger = logging.getLogger(__name__)
        self.relation_data = None
        
    def load_relation_data(self) -> bool:
        """
        加载关系验证数据
        
        Returns:
            bool: 加载是否成功
        """
        try:
            relation_file = self.config_manager.get_value('relation_file', 'config/csv/relation.csv')
            self.relation_data = self.csv_processor.load_csv_to_dataframe(relation_file)
            self.logger.info("关系验证数据加载成功")
            return True
        except Exception as e:
            self.logger.error(f"加载关系验证数据失败: {e}")
            return False
    
    def validate_relations(self, program_no: int, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证参数关系
        
        Args:
            program_no: 程序编号
            parameters: 参数字典
            
        Returns:
            Dict[str, Any]: 验证结果，包含验证状态和错误信息
        """
        if self.relation_data is None:
            if not self.load_relation_data():
                return {"valid": False, "errors": ["关系数据加载失败"]}
        
        try:
            errors = []
            warnings = []
            
            # 获取当前程序的关系规则
            program_rules = self.relation_data[
                self.relation_data['PROGRAM_NO'] == program_no
            ]
            
            for _, rule in program_rules.iterrows():
                validation_result = self._validate_single_rule(rule, parameters)
                if not validation_result["valid"]:
                    errors.extend(validation_result["errors"])
                if validation_result["warnings"]:
                    warnings.extend(validation_result["warnings"])
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings
            }
            
        except Exception as e:
            self.logger.error(f"关系验证失败: {e}")
            return {"valid": False, "errors": [f"关系验证异常: {str(e)}"]}
    
    def _validate_single_rule(self, rule: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证单个关系规则
        
        Args:
            rule: 关系规则
            parameters: 参数字典
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        errors = []
        warnings = []
        
        param1 = rule.get('PARAM1')
        param2 = rule.get('PARAM2')
        operator = rule.get('OPERATOR')
        expected_value = rule.get('EXPECTED_VALUE')
        error_message = rule.get('ERROR_MESSAGE', '参数关系验证失败')
        
        if param1 not in parameters or param2 not in parameters:
            warnings.append(f"关系验证参数缺失: {param1} 或 {param2}")
            return {"valid": True, "errors": [], "warnings": warnings}
        
        value1 = parameters[param1]
        value2 = parameters[param2]
        
        try:
            # 尝试转换为数值进行比较
            try:
                val1 = float(value1)
                val2 = float(value2)
            except (ValueError, TypeError):
                # 如果无法转换为数值，进行字符串比较
                val1 = str(value1)
                val2 = str(value2)
            
            valid = self._compare_values(val1, val2, operator, expected_value)
            
            if not valid:
                errors.append(f"{error_message} ({param1}: {value1}, {param2}: {value2})")
                
        except Exception as e:
            errors.append(f"关系验证执行失败: {str(e)}")
        
        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}
    
    def _compare_values(self, value1: Any, value2: Any, operator: str, expected_value: Any) -> bool:
        """
        比较两个值
        
        Args:
            value1: 第一个值
            value2: 第二个值
            operator: 比较操作符
            expected_value: 期望值
            
        Returns:
            bool: 比较结果
        """
        if operator == '==':
            return value1 == value2
        elif operator == '!=':
            return value1 != value2
        elif operator == '>':
            return value1 > value2
        elif operator == '>=':
            return value1 >= value2
        elif operator == '<':
            return value1 < value2
        elif operator == '<=':
            return value1 <= value2
        elif operator == 'in':
            return value1 in value2
        elif operator == 'not in':
            return value1 not in value2
        else:
            self.logger.warning(f"不支持的关系操作符: {operator}")
            return True
    
    def get_relation_rules(self, program_no: int) -> List[Dict[str, Any]]:
        """
        获取指定程序的关系规则
        
        Args:
            program_no: 程序编号
            
        Returns:
            List[Dict[str, Any]]: 关系规则列表
        """
        if self.relation_data is None:
            if not self.load_relation_data():
                return []
        
        try:
            program_rules = self.relation_data[
                self.relation_data['PROGRAM_NO'] == program_no
            ]
            return program_rules.to_dict('records')
        except Exception as e:
            self.logger.error(f"获取关系规则失败: {e}")
            return []
    
    def clear_cache(self) -> None:
        """清理缓存数据"""
        self.relation_data = None
        self.logger.info("关系验证器缓存已清理")
