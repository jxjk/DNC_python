"""
配置验证器
提供配置数据的完整性和一致性验证
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
import re

from src.utils.logger import get_logger


class ValidationLevel(Enum):
    """验证级别枚举"""
    CRITICAL = "critical"  # 关键错误，必须修复
    ERROR = "error"        # 错误，建议修复
    WARNING = "warning"    # 警告，可能影响功能
    INFO = "info"          # 信息，不影响功能


@dataclass
class ValidationIssue:
    """验证问题"""
    level: ValidationLevel
    message: str
    file: Optional[str] = None
    field: Optional[str] = None
    value: Optional[Any] = None
    suggestion: Optional[str] = None
    
    def __str__(self) -> str:
        base_msg = f"[{self.level.value.upper()}] {self.message}"
        if self.file:
            base_msg += f" (文件: {self.file})"
        if self.field:
            base_msg += f" (字段: {self.field})"
        if self.value is not None:
            base_msg += f" (值: {self.value})"
        if self.suggestion:
            base_msg += f" | 建议: {self.suggestion}"
        return base_msg


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    issues: List[ValidationIssue]
    summary: Dict[str, int]
    
    def __init__(self, is_valid: bool, issues: List[ValidationIssue]):
        self.is_valid = is_valid
        self.issues = issues
        self.summary = self._generate_summary()
    
    def _generate_summary(self) -> Dict[str, int]:
        """生成验证摘要"""
        summary = {
            'critical': 0,
            'error': 0,
            'warning': 0,
            'info': 0,
            'total': len(self.issues)
        }
        
        for issue in self.issues:
            summary[issue.level.value] += 1
        
        return summary
    
    def has_critical_issues(self) -> bool:
        """检查是否存在关键问题"""
        return self.summary['critical'] > 0
    
    def has_errors(self) -> bool:
        """检查是否存在错误"""
        return self.summary['critical'] > 0 or self.summary['error'] > 0
    
    def get_issues_by_level(self, level: ValidationLevel) -> List[ValidationIssue]:
        """按级别获取问题"""
        return [issue for issue in self.issues if issue.level == level]
    
    def get_issues_by_file(self, file: str) -> List[ValidationIssue]:
        """按文件获取问题"""
        return [issue for issue in self.issues if issue.file == file]


class ConfigValidator:
    """
    配置验证器
    提供配置数据的完整性和一致性验证
    """
    
    def __init__(self):
        """初始化配置验证器"""
        self.logger = get_logger("ConfigValidator")
        
        # 必需配置文件列表
        self.required_files = {
            'ini.csv': ['QRmode', 'QRspltStr', 'MODELplc', 'POplc', 'QTYplc'],
            'header.csv': ['C', 'X'],
            'type_define.csv': ['NO', 'TYPE'],
            'type_prg.csv': ['NO', 'prg1', 'prg2', 'prg3'],
            'load.csv': ['NO', 'MACRO', 'VALUE'],
            'define.csv': ['DEFINE', 'STR', 'BEFORE', 'AFTER', 'CHNGVL', 'CALC'],
            'chngValue.csv': ['DEFINE', 'BEFORE', 'AFTER'],
            'calc.csv': ['DEFINE', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
            'relation.csv': ['DEFINE', 'VALUE', '1', '2', '3', '4', '5', '6', '7', '8'],
            'cntrl.csv': ['NO', 'KIND', 'MACRO', 'DISPFLG', 'ROW', 'COLUMN']
        }
        
        # 字段验证规则
        self.field_rules = {
            'QRmode': {
                'type': int,
                'valid_values': [0, 1],
                'required': True
            },
            'QRspltStr': {
                'type': str,
                'max_length': 10,
                'required': True
            },
            'MODELplc': {
                'type': int,
                'min_value': 0,
                'required': True
            },
            'POplc': {
                'type': int,
                'min_value': 0,
                'required': True
            },
            'QTYplc': {
                'type': int,
                'min_value': 0,
                'required': True
            },
            'BarCodeHeaderStrNum': {
                'type': int,
                'min_value': 0,
                'required': True
            },
            'DecimalPlace': {
                'type': int,
                'min_value': 0,
                'max_value': 6,
                'required': True
            }
        }
    
    def validate_config_structure(self, config_data: Dict[str, Any]) -> ValidationResult:
        """
        验证配置结构完整性
        
        Args:
            config_data: 配置数据字典
            
        Returns:
            ValidationResult: 验证结果
        """
        issues = []
        
        # 1. 验证必需配置文件
        issues.extend(self._validate_required_files(config_data))
        
        # 2. 验证字段完整性
        for file_name, required_fields in self.required_files.items():
            if file_name in config_data and config_data[file_name]:
                issues.extend(self._validate_file_fields(file_name, config_data[file_name], required_fields))
        
        # 3. 验证字段值
        issues.extend(self._validate_field_values(config_data))
        
        # 4. 验证配置一致性
        issues.extend(self._validate_config_consistency(config_data))
        
        # 5. 验证数据关系
        issues.extend(self._validate_data_relationships(config_data))
        
        is_valid = not any(issue.level in [ValidationLevel.CRITICAL, ValidationLevel.ERROR] for issue in issues)
        return ValidationResult(is_valid, issues)
    
    def _validate_required_files(self, config_data: Dict[str, Any]) -> List[ValidationIssue]:
        """验证必需配置文件"""
        issues = []
        
        for file_name in self.required_files.keys():
            if file_name not in config_data or not config_data[file_name]:
                issues.append(ValidationIssue(
                    level=ValidationLevel.CRITICAL,
                    message=f"必需配置文件缺失: {file_name}",
                    file=file_name,
                    suggestion=f"请确保 {file_name} 文件存在且包含有效数据"
                ))
        
        return issues
    
    def _validate_file_fields(self, file_name: str, file_data: List[Dict[str, str]], required_fields: List[str]) -> List[ValidationIssue]:
        """验证文件字段完整性"""
        issues = []
        
        if not file_data:
            issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message=f"配置文件为空: {file_name}",
                file=file_name,
                suggestion="请检查文件内容或重新生成配置文件"
            ))
            return issues
        
        # 检查字段是否存在
        first_row = file_data[0]
        missing_fields = [field for field in required_fields if field not in first_row]
        
        for missing_field in missing_fields:
            issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message=f"必需字段缺失: {missing_field}",
                file=file_name,
                field=missing_field,
                suggestion=f"请在 {file_name} 中添加 {missing_field} 字段"
            ))
        
        # 检查数据行完整性
        for i, row in enumerate(file_data, 1):
            for field in required_fields:
                if field in row and not row[field]:
                    issues.append(ValidationIssue(
                        level=ValidationLevel.WARNING,
                        message=f"字段值为空",
                        file=file_name,
                        field=field,
                        value=f"第{i}行",
                        suggestion=f"请检查 {file_name} 第{i}行的 {field} 字段值"
                    ))
        
        return issues
    
    def _validate_field_values(self, config_data: Dict[str, Any]) -> List[ValidationIssue]:
        """验证字段值"""
        issues = []
        
        # 验证ini.csv中的配置值
        if 'ini.csv' in config_data and config_data['ini.csv']:
            ini_config = config_data['ini.csv']
            
            for row in ini_config:
                define = row.get('DEFINE')
                value = row.get('VALUE')
                
                if define in self.field_rules:
                    rule = self.field_rules[define]
                    issues.extend(self._validate_single_field(define, value, rule, 'ini.csv'))
        
        # 验证其他文件的数值字段
        numeric_files = {
            'type_define.csv': ['NO'],
            'type_prg.csv': ['NO', 'prg1', 'prg2', 'prg3'],
            'load.csv': ['NO'],
            'cntrl.csv': ['NO', 'ROW', 'COLUMN']
        }
        
        for file_name, numeric_fields in numeric_files.items():
            if file_name in config_data and config_data[file_name]:
                for row in config_data[file_name]:
                    for field in numeric_fields:
                        if field in row and row[field]:
                            try:
                                int(row[field])
                            except ValueError:
                                issues.append(ValidationIssue(
                                    level=ValidationLevel.ERROR,
                                    message=f"数值字段包含非数字值",
                                    file=file_name,
                                    field=field,
                                    value=row[field],
                                    suggestion=f"请确保 {file_name} 的 {field} 字段只包含数字"
                                ))
        
        return issues
    
    def _validate_single_field(self, field_name: str, value: str, rule: Dict[str, Any], file_name: str) -> List[ValidationIssue]:
        """验证单个字段"""
        issues = []
        
        # 检查必需性
        if rule.get('required', False) and (value is None or value == ''):
            issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message=f"必需字段为空",
                file=file_name,
                field=field_name,
                suggestion=f"请为 {field_name} 字段提供值"
            ))
            return issues
        
        if value is None or value == '':
            return issues  # 非必需字段为空是允许的
        
        # 类型验证
        expected_type = rule.get('type')
        if expected_type:
            try:
                if expected_type == int:
                    converted_value = int(value)
                elif expected_type == float:
                    converted_value = float(value)
                elif expected_type == str:
                    converted_value = str(value)
                else:
                    converted_value = value
            except (ValueError, TypeError):
                issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    message=f"字段类型不匹配",
                    file=file_name,
                    field=field_name,
                    value=value,
                    suggestion=f"请确保 {field_name} 字段的值是 {expected_type.__name__} 类型"
                ))
                return issues
        
        # 有效值验证
        valid_values = rule.get('valid_values')
        if valid_values is not None and value not in [str(v) for v in valid_values]:
            issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message=f"字段值不在有效范围内",
                file=file_name,
                field=field_name,
                value=value,
                suggestion=f"请确保 {field_name} 字段的值在 {valid_values} 范围内"
            ))
        
        # 数值范围验证
        if 'min_value' in rule and converted_value < rule['min_value']:
            issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message=f"字段值小于最小值",
                file=file_name,
                field=field_name,
                value=value,
                suggestion=f"请确保 {field_name} 字段的值不小于 {rule['min_value']}"
            ))
        
        if 'max_value' in rule and converted_value > rule['max_value']:
            issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message=f"字段值大于最大值",
                file=file_name,
                field=field_name,
                value=value,
                suggestion=f"请确保 {field_name} 字段的值不大于 {rule['max_value']}"
            ))
        
        # 字符串长度验证
        if 'max_length' in rule and len(value) > rule['max_length']:
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                message=f"字段值长度超过限制",
                file=file_name,
                field=field_name,
                value=value,
                suggestion=f"请确保 {field_name} 字段的值长度不超过 {rule['max_length']} 个字符"
            ))
        
        return issues
    
    def _validate_config_consistency(self, config_data: Dict[str, Any]) -> List[ValidationIssue]:
        """验证配置一致性"""
        issues = []
        
        # 验证type_define.csv和type_prg.csv的一致性
        if 'type_define.csv' in config_data and 'type_prg.csv' in config_data:
            type_define_nos = set(row['NO'] for row in config_data['type_define.csv'] if 'NO' in row)
            type_prg_nos = set(row['NO'] for row in config_data['type_prg.csv'] if 'NO' in row)
            
            missing_in_prg = type_define_nos - type_prg_nos
            missing_in_define = type_prg_nos - type_define_nos
            
            for no in missing_in_prg:
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    message=f"类型定义在type_prg.csv中缺失",
                    file='type_prg.csv',
                    field='NO',
                    value=no,
                    suggestion=f"请在type_prg.csv中添加编号为 {no} 的记录"
                ))
            
            for no in missing_in_define:
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    message=f"类型程序在type_define.csv中缺失",
                    file='type_define.csv',
                    field='NO',
                    value=no,
                    suggestion=f"请在type_define.csv中添加编号为 {no} 的记录"
                ))
        
        return issues
    
    def _validate_data_relationships(self, config_data: Dict[str, Any]) -> List[ValidationIssue]:
        """验证数据关系"""
        issues = []
        
        # 验证define.csv中的引用关系
        if 'define.csv' in config_data and config_data['define.csv']:
            define_data = config_data['define.csv']
            
            # 收集所有DEFINE字段值
            define_names = set(row.get('DEFINE') for row in define_data if row.get('DEFINE'))
            
            # 验证CHNGVL字段引用
            for row in define_data:
                chngvl = row.get('CHNGVL')
                if chngvl and chngvl not in define_names:
                    issues.append(ValidationIssue(
                        level=ValidationLevel.WARNING,
                        message=f"CHNGVL字段引用未定义的DEFINE",
                        file='define.csv',
                        field='CHNGVL',
                        value=chngvl,
                        suggestion=f"请确保 {chngvl} 在define.csv的DEFINE字段中定义"
                    ))
        
        return issues
    
    def validate_qr_config_consistency(self, qr_config: Dict[str, Any], ini_config: List[Dict[str, str]]) -> ValidationResult:
        """
        验证QR配置一致性
        
        Args:
            qr_config: QR配置字典
            ini_config: ini.csv配置数据
            
        Returns:
            ValidationResult: 验证结果
        """
        issues = []
        
        if not ini_config:
            issues.append(ValidationIssue(
                level=ValidationLevel.CRITICAL,
                message="ini.csv配置为空",
                file='ini.csv',
                suggestion="请检查ini.csv文件内容"
            ))
            return ValidationResult(False, issues)
        
        # 从ini.csv中提取配置值
        ini_values = {}
        for row in ini_config:
            define = row.get('DEFINE')
            value = row.get('VALUE')
            if define and value is not None:
                ini_values[define] = value
        
        # 验证配置一致性
        consistency_checks = [
            ('QRmode', 'qr_mode', int),
            ('MODELplc', 'model_place', int),
            ('POplc', 'po_place', int),
            ('QTYplc', 'qty_place', int),
            ('BarCodeHeaderStrNum', 'barcode_header_str_num', int),
            ('DecimalPlace', 'decimal_place', int)
        ]
        
        for ini_field, qr_field, converter in consistency_checks:
            if ini_field in ini_values and qr_field in qr_config:
                try:
                    ini_value = converter(ini_values[ini_field])
                    qr_value = converter(qr_config[qr_field])
                    
                    if ini_value != qr_value:
                        issues.append(ValidationIssue(
                            level=ValidationLevel.WARNING,
                            message=f"QR配置与ini.csv不一致",
                            field=qr_field,
                            value=f"ini.csv: {ini_value}, QR配置: {qr_value}",
                            suggestion=f"请确保 {ini_field} 在ini.csv和QR配置中的值一致"
                        ))
                except (ValueError, TypeError):
                    issues.append(ValidationIssue(
                        level=ValidationLevel.ERROR,
                        message=f"配置值转换失败",
                        field=ini_field,
                        value=f"ini.csv: {ini_values[ini_field]}, QR配置: {qr_config[qr_field]}",
                        suggestion=f"请检查 {ini_field} 字段的值类型"
                    ))
        
        is_valid = len(issues) == 0
        return ValidationResult(is_valid, issues)
    
    def generate_validation_report(self, result: ValidationResult) -> str:
        """
        生成验证报告
        
        Args:
            result: 验证结果
            
        Returns:
            str: 验证报告
        """
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("配置验证报告")
        report_lines.append("=" * 60)
        
        # 摘要信息
        summary = result.summary
        report_lines.append(f"验证摘要:")
        report_lines.append(f"  关键问题: {summary['critical']}")
        report_lines.append(f"  错误: {summary['error']}")
        report_lines.append(f"  警告: {summary['warning']}")
        report_lines.append(f"  信息: {summary['info']}")
        report_lines.append(f"  总计: {summary['total']}")
        report_lines.append(f"验证结果: {'通过' if result.is_valid else '失败'}")
        report_lines.append("")
        
        # 按级别显示问题
        for level in [ValidationLevel.CRITICAL, ValidationLevel.ERROR, ValidationLevel.WARNING, ValidationLevel.INFO]:
            issues = result.get_issues_by_level(level)
            if issues:
                report_lines.append(f"{level.value.upper()} 级别问题 ({len(issues)}):")
                report_lines.append("-" * 40)
                for issue in issues:
                    report_lines.append(f"  {issue}")
                report_lines.append("")
        
        # 按文件显示问题
        files = set(issue.file for issue in result.issues if issue.file)
        if files:
            report_lines.append("按文件分类:")
            for file in sorted(files):
                file_issues = result.get_issues_by_file(file)
                if file_issues:
                    report_lines.append(f"  {file} ({len(file_issues)}):")
                    for issue in file_issues:
                        report_lines.append(f"    {issue}")
            report_lines.append("")
        
        report_lines.append("=" * 60)
        return "\n".join(report_lines)
    
    def quick_validate(self, config_data: Dict[str, Any]) -> bool:
        """
        快速验证配置
        
        Args:
            config_data: 配置数据字典
            
        Returns:
            bool: 是否通过验证
        """
        result = self.validate_config_structure(config_data)
        return result.is_valid and not result.has_critical_issues()


# 全局配置验证器实例
_global_config_validator: Optional[ConfigValidator] = None


def get_global_config_validator() -> ConfigValidator:
    """
    获取全局配置验证器实例
    
    Returns:
        ConfigValidator: 全局配置验证器实例
    """
    global _global_config_validator
    if _global_config_validator is None:
        _global_config_validator = ConfigValidator()
    return _global_config_validator


def validate_config_structure(config_data: Dict[str, Any]) -> ValidationResult:
    """
    验证配置结构（便捷函数）
    
    Args:
        config_data: 配置数据字典
        
    Returns:
        ValidationResult: 验证结果
    """
    validator = get_global_config_validator()
    return validator.validate_config_structure(config_data)


def quick_validate_config(config_data: Dict[str, Any]) -> bool:
    """
    快速验证配置（便捷函数）
    
    Args:
        config_data: 配置数据字典
        
    Returns:
        bool: 是否通过验证
    """
    validator = get_global_config_validator()
    return validator.quick_validate(config_data)
