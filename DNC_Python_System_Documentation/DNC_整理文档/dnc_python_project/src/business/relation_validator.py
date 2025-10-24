"""
关系验证器
负责验证参数之间的逻辑关系
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

from ..core.config import ConfigManager
from ..data.csv_processor import CSVProcessor


@dataclass
class ValidationResult:
    """验证结果"""
    valid: bool
    errors: List[str]
    warnings: List[str]
    program_no: int


class RelationValidator:
    """关系验证器"""
    
    def __init__(self, config_manager: ConfigManager, csv_processor: CSVProcessor):
        """
        初始化关系验证器
        
        Args:
            config_manager: 配置管理器
            csv_processor: CSV处理器
        """
        self.config_manager = config_manager
        self.csv_processor = csv_processor
        self.logger = logging.getLogger(__name__)
        
        # 加载关系数据
        self.relation_data = None
        self._load_relation_data()
    
    def _load_relation_data(self) -> None:
        """加载关系数据"""
        try:
            # 加载关系数据
            relation_path = self.config_manager.get_csv_config_path("relation.csv")
            self.relation_data = self.csv_processor.read_csv(relation_path)
            
            self.logger.info("关系数据加载成功")
            
        except Exception as e:
            self.logger.error(f"关系数据加载失败: {e}")
    
    def validate_relations(self, program_no: int, parameters: Dict[str, Any]) -> ValidationResult:
        """
        验证参数关系
        
        Args:
            program_no: 程序编号
            parameters: 参数字典
            
        Returns:
            ValidationResult: 验证结果
        """
        try:
            self.logger.info(f"开始验证参数关系，程序: {program_no}")
            
            if not self.relation_data:
                return ValidationResult(
                    valid=False,
                    errors=["关系数据未加载"],
                    warnings=[],
                    program_no=program_no
                )
            
            errors = []
            warnings = []
            
            # 查找当前程序的关系规则
            for row in self.relation_data:
                if len(row) >= 6:
                    try:
                        rule_program_no = int(row[0])
                        if rule_program_no == program_no:
                            # 验证单个关系规则
                            rule_result = self._validate_single_rule(row, parameters)
                            if not rule_result["valid"]:
                                errors.extend(rule_result["errors"])
                            if rule_result["warnings"]:
                                warnings.extend(rule_result["warnings"])
                    except (ValueError, IndexError):
                        continue
            
            valid = len(errors) == 0
            
            result = ValidationResult(
                valid=valid,
                errors=errors,
                warnings=warnings,
                program_no=program_no
            )
            
            if valid:
                self.logger.info(f"参数关系验证通过，程序: {program_no}")
            else:
                self.logger.warning(f"参数关系验证失败，程序: {program_no}, 错误数: {len(errors)}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"参数关系验证异常: {e}")
            return ValidationResult(
                valid=False,
                errors=[f"验证异常: {str(e)}"],
                warnings=[],
                program_no=program_no
            )
    
    def _validate_single_rule(self, rule_row: List[str], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证单个关系规则
        
        Args:
            rule_row: 关系规则行数据
            parameters: 参数字典
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        errors = []
        warnings = []
        
        try:
            # 解析规则行数据
            # 格式: [程序编号, 参数1, 参数2, 操作符, 期望值, 错误消息]
            param1 = rule_row[1] if len(rule_row) > 1 else ""
            param2 = rule_row[2] if len(rule_row) > 2 else ""
            operator = rule_row[3] if len(rule_row) > 3 else ""
            expected_value = rule_row[4] if len(rule_row) > 4 else ""
            error_message = rule_row[5] if len(rule_row) > 5 else "参数关系验证失败"
            
            if not param1 or not param2:
                warnings.append("关系规则参数不完整")
                return {"valid": True, "errors": [], "warnings": warnings}
            
            if param1 not in parameters or param2 not in parameters:
                warnings.append(f"关系验证参数缺失: {param1} 或 {param2}")
                return {"valid": True, "errors": [], "warnings": warnings}
            
            value1 = parameters[param1]
            value2 = parameters[param2]
            
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
        if not self.relation_data:
            self._load_relation_data()
            if not self.relation_data:
                return []
        
        rules = []
        for row in self.relation_data:
            if len(row) >= 6:
                try:
                    rule_program_no = int(row[0])
                    if rule_program_no == program_no:
                        rule = {
                            "program_no": rule_program_no,
                            "param1": row[1] if len(row) > 1 else "",
                            "param2": row[2] if len(row) > 2 else "",
                            "operator": row[3] if len(row) > 3 else "",
                            "expected_value": row[4] if len(row) > 4 else "",
                            "error_message": row[5] if len(row) > 5 else ""
                        }
                        rules.append(rule)
                except (ValueError, IndexError):
                    continue
        
        return rules
    
    def reload_relation_data(self) -> bool:
        """
        重新加载关系数据
        
        Returns:
            bool: 重新加载是否成功
        """
        try:
            self._load_relation_data()
            self.logger.info("关系数据重新加载成功")
            return True
        except Exception as e:
            self.logger.error(f"关系数据重新加载失败: {e}")
            return False
    
    def clear_cache(self) -> None:
        """清理缓存数据"""
        self.relation_data = None
        self.logger.info("关系验证器缓存已清理")
