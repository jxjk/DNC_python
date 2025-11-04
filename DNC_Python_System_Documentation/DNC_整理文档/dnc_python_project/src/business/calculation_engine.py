# src/business/calculation_engine.py
"""
计算引擎
负责参数计算和公式处理
"""

import logging
import re
import math
import os
import time
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass

from src.core.config import ConfigManager
from src.data.csv_processor import CSVProcessor
from src.utils.logger import get_logger
from src.utils.error_handler import handle_errors
from src.core.cache_manager import get_global_cache_manager
from src.core.performance_monitor import get_global_performance_monitor


@dataclass
class CalculationStep:
    """计算步骤"""
    step_no: int
    operation: str
    operands: List[str]
    result: Any
    description: str
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'step_no': self.step_no,
            'operation': self.operation,
            'operands': self.operands,
            'result': self.result,
            'description': self.description
        }


@dataclass
class CalculationResult:
    """计算结果"""
    program_no: int
    parameters: Dict[str, Any]
    calculation_steps: List[CalculationStep]
    success: bool
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'program_no': self.program_no,
            'parameters': self.parameters,
            'calculation_steps': [step.to_dict() for step in self.calculation_steps] if self.calculation_steps else [],
            'success': self.success,
            'error_message': self.error_message
        }


@dataclass
class FormBuildingResult:
    """表单构建结果"""
    forms: Dict[str, Any]
    variables: Dict[str, 'Variable']
    active_program: str = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'forms': self.forms,
            'variables': {name: var.to_dict() for name, var in self.variables.items()} if self.variables else {},
            'active_program': self.active_program
        }


@dataclass
class Variable:
    """变量定义"""
    name: str
    kind: str
    value: Any = None
    definition: str = None
    display_flag: bool = True
    send_flag: bool = True
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    label_text: str = ""
    error_message: str = None
    
    @property
    def is_valid(self) -> bool:
        """检查变量值是否有效"""
        if self.value is None:
            return False
        
        # 检查数值范围
        if self.min_value is not None and self.value < self.min_value:
            return False
        if self.max_value is not None and self.value > self.max_value:
            return False
            
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'name': self.name,
            'kind': self.kind,
            'value': self.value,
            'definition': self.definition,
            'display_flag': self.display_flag,
            'send_flag': self.send_flag,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'label_text': self.label_text,
            'error_message': self.error_message,
            'is_valid': self.is_valid
        }


@dataclass
class ProgramConfig:
    """程序配置"""
    name: str
    ctrl_config: List[Dict[str, Any]]
    load_config: List[Dict[str, Any]]
    form_config: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'name': self.name,
            'ctrl_config': self.ctrl_config,
            'load_config': self.load_config,
            'form_config': self.form_config
        }


@dataclass
class CalculationResult:
    """计算结果"""
    success: bool
    value: Any = None
    error_message: str = None
    
    @classmethod
    def success(cls, value: Any) -> 'CalculationResult':
        """创建成功结果"""
        return cls(success=True, value=value)
    
    @classmethod
    def error(cls, error_message: str) -> 'CalculationResult':
        """创建错误结果"""
        return cls(success=False, error_message=error_message)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'success': self.success,
            'value': self.value,
            'error_message': self.error_message
        }


@dataclass
class DefineConfig:
    """define配置"""
    name: str
    before: str = ""
    after: str = ""
    chngvl: str = ""
    calc: str = ""
    target: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'name': self.name,
            'before': self.before,
            'after': self.after,
            'chngvl': self.chngvl,
            'calc': self.calc,
            'target': self.target
        }


@dataclass
class RelationConfig:
    """relation配置"""
    name: str
    conditions: List['Condition'] = None
    default_value: Any = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'name': self.name,
            'conditions': [cond.to_dict() for cond in self.conditions] if self.conditions else [],
            'default_value': self.default_value
        }


@dataclass
class Condition:
    """条件定义"""
    left_operand: str
    operator: str
    right_operand: str
    value: Any
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'left_operand': self.left_operand,
            'operator': self.operator,
            'right_operand': self.right_operand,
            'value': self.value
        }


class CalculationEngineError(Exception):
    """计算引擎错误异常"""
    pass


class DefinitionParseError(Exception):
    """定义解析错误异常"""
    pass


class ConditionEvaluationError(Exception):
    """条件评估错误异常"""
    pass


class FormBuildingError(Exception):
    """表单构建错误异常"""
    pass


class VariableValidationError(Exception):
    """变量验证错误异常"""
    pass


class FormulaParser:
    """公式解析器"""
    
    @staticmethod
    def parse_calc_csv(calc_data: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        解析calc.csv数据
        
        Args:
            calc_data: calc.csv的数据
            
        Returns:
            Dict[str, str]: 公式字典 {公式名: 公式表达式}
        """
        formulas = {}
        for row in calc_data:
            if 'NAME' in row and 'FORMULA' in row:
                formulas[row['NAME']] = row['FORMULA']
        return formulas
    
    @staticmethod
    def extract_parameters_from_formula(formula: str) -> List[str]:
        """
        从公式中提取参数
        
        Args:
            formula: 公式字符串
            
        Returns:
            List[str]: 参数列表
        """
        # 匹配 #数字 格式的变量引用
        pattern = r'#(\d+)'
        matches = re.findall(pattern, formula)
        return [f"#{match}" for match in matches]
    
    @staticmethod
    def simplify_formula(formula: str) -> str:
        """
        简化公式格式
        
        Args:
            formula: 原始公式
            
        Returns:
            str: 简化后的公式
        """
        # 移除多余空格
        return re.sub(r'\s+', ' ', formula.strip())
    
    @staticmethod
    def validate_formula_structure(formula: str) -> bool:
        """
        验证公式结构
        
        Args:
            formula: 公式字符串
            
        Returns:
            bool: 是否有效
        """
        # 简单验证公式结构
        if not formula:
            return False
        # 可以添加更复杂的验证逻辑
        return True


class CalculationEngine:
    """计算引擎"""
    
    # 安全计算允许的操作符
    allowed_operators = {
        'abs': abs, 'round': round, 'int': int, 'float': float,
        'min': min, 'max': max, 'sum': sum,
        'math.sqrt': math.sqrt, 'math.pow': math.pow,
        'math.sin': math.sin, 'math.cos': math.cos, 'math.tan': math.tan,
        'math.log': math.log, 'math.log10': math.log10,
        'math.exp': math.exp, 'math.floor': math.floor, 'math.ceil': math.ceil
    }
    
    # 变量替换模式
    variable_pattern = r'#(\d+)'
    
    def __init__(self, config_manager, csv_processor):
        """
        初始化计算引擎
        
        Args:
            config_manager: 配置管理器实例
            csv_processor: CSV处理器实例
        """
        self.config_manager = config_manager
        self.csv_processor = csv_processor
        self.logger = get_logger("CalculationEngine")
        self.cache = get_global_cache_manager()  # 添加缓存管理器
        self.performance_monitor = get_global_performance_monitor()  # 添加性能监控器
        self.form_builder = FormBuildingFlow(config_manager, csv_processor)
        self.calculation_flow = CalculationEngineFlow(config_manager, csv_processor)
        
        # 新增属性
        self.calculation_formulas = {}  # 计算公式字典
        self.variables = {}  # 变量字典
        self.formula_cache = {}  # 公式缓存
    
    def load_calculation_formulas(self, calc_data: List[Dict[str, Any]]) -> None:
        """
        从calc.csv加载计算公式
        
        Args:
            calc_data: calc.csv的数据
        """
        self.calculation_formulas = FormulaParser.parse_calc_csv(calc_data)
        self.logger.debug(f"加载了 {len(self.calculation_formulas)} 个计算公式")
    
    def set_variables(self, variables: Dict[str, Any]) -> None:
        """
        设置计算所需的变量值
        
        Args:
            variables: 变量字典
        """
        self.variables.update(variables)
        self.logger.debug(f"设置了 {len(variables)} 个变量")
    
    def clear_variables(self) -> None:
        """清除所有变量"""
        self.variables.clear()
        self.logger.debug("清除了所有变量")
    
    def calculate_relation(self, macro_no: str, formula_name: str, context: Dict = None) -> Any:
        """
        计算关系类型参数的值
        
        Args:
            macro_no: 宏编号
            formula_name: 公式名称
            context: 上下文字典
            
        Returns:
            Any: 计算结果
        """
        try:
            # 获取公式
            formula = self.calculation_formulas.get(formula_name)
            if not formula:
                self.logger.warning(f"未找到计算公式: {formula_name}")
                return None
            
            # 合并变量和上下文
            all_variables = {**self.variables}
            if context:
                all_variables.update(context)
            
            # 计算表达式
            result = self.calculate_formula(formula, all_variables)
            
            self.logger.debug(f"关系计算完成: {macro_no} -> {formula_name} = {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"计算关系失败: macro_no={macro_no}, formula={formula_name}, error={e}")
            return None
    
    def calculate_formula(self, formula: str, variables: Dict[str, Any]) -> Union[int, float]:
        """
        执行具体的计算公式
        
        Args:
            formula: 公式字符串
            variables: 变量字典
            
        Returns:
            Union[int, float]: 计算结果
        """
        try:
            # 检查缓存
            cache_key = f"{formula}_{str(sorted(variables.items()))}"
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 替换变量引用
            processed_formula = self._replace_variables(formula, variables)
            
            # 验证公式
            self.validate_formula(processed_formula)
            
            # 安全执行计算
            result = self._safe_eval(processed_formula)
            
            # 缓存结果
            self.cache.set(cache_key, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"公式计算失败: formula={formula}, error={e}")
            raise CalculationEngineError(f"公式计算失败: {str(e)}")
    
    def calculate_batch_relations(self, relations: List[Dict[str, str]], context: Dict = None) -> Dict[str, Any]:
        """
        批量计算多个关系参数
        
        Args:
            relations: 关系参数列表 [{macro_no: formula_name}, ...]
            context: 上下文字典
            
        Returns:
            Dict[str, Any]: 计算结果字典
        """
        results = {}
        for relation in relations:
            for macro_no, formula_name in relation.items():
                result = self.calculate_relation(macro_no, formula_name, context)
                results[macro_no] = result
        return results
    
    def validate_formula(self, formula: str) -> bool:
        """
        验证公式语法
        
        Args:
            formula: 公式字符串
            
        Returns:
            bool: 是否有效
        """
        # 检查公式是否包含不允许的字符
        allowed_chars = set("0123456789+-*/().[]{} \t\n\r")
        for char in formula:
            if char.isalpha() and char not in ['e']:  # 允许科学计数法中的'e'
                # 检查是否是允许的操作符
                if not any(op.startswith(char) for op in self.allowed_operators.keys()):
                    raise CalculationEngineError(f"公式包含不允许的字符: {char}")
        
        return True
    
    def get_formula_variables(self, formula: str) -> List[str]:
        """
        获取公式引用的变量
        
        Args:
            formula: 公式字符串
            
        Returns:
            List[str]: 变量列表
        """
        return FormulaParser.extract_parameters_from_formula(formula)
    
    def _replace_variables(self, formula: str, variables: Dict[str, Any]) -> str:
        """
        替换公式中的变量引用
        
        Args:
            formula: 公式字符串
            variables: 变量字典
            
        Returns:
            str: 替换后的公式
        """
        def replace_var(match):
            var_id = match.group(1)
            var_key = f"#{var_id}"
            if var_key in variables and variables[var_key] is not None:
                return str(variables[var_key])
            else:
                raise CalculationEngineError(f"未找到变量: {var_key}")
        
        return re.sub(self.variable_pattern, replace_var, formula)
    
    @handle_errors
    def _safe_eval(self, expression: str) -> Union[int, float]:
        """
        安全执行表达式计算
        
        Args:
            expression: 表达式字符串
            
        Returns:
            Union[int, float]: 计算结果
        """
        start_time = time.time()
        
        try:
            # 创建安全的环境
            safe_env = {
                '__builtins__': {},
            }
            
            # 添加允许的操作符
            safe_env.update(self.allowed_operators)
            
            # 执行计算
            result = eval(expression, safe_env)
            
            # 确保返回数值类型
            if isinstance(result, (int, float)):
                # 记录性能指标
                execution_time = time.time() - start_time
                self.performance_monitor.record_metric(
                    "safe_eval_execution_time",
                    execution_time,
                    tags={"expression_length": len(expression), "success": True}
                )
                return result
            else:
                raise ValueError(f"计算结果不是数值类型: {type(result)}")
                
        except ZeroDivisionError:
            raise CalculationEngineError("除零错误")
        except Exception as e:
            self.logger.error(f"安全计算失败: expression={expression}, error={e}")
            raise
    
    def build_forms_for_programs(self, program_sequence: List[str], 
                                model_segments: List[str]) -> FormBuildingResult:
        """
        为程序序列构建表单
        
        Args:
            program_sequence: 程序序列
            model_segments: 型号片段
            
        Returns:
            FormBuildingResult: 表单构建结果
        """
        try:
            self.logger.info(f"为程序序列构建表单: {program_sequence}")
            
            # 使用FormBuildingFlow构建表单
            form_result = self.form_builder.build_forms(program_sequence, model_segments)
            
            self.logger.info(f"表单构建完成: {len(form_result.forms)} 个表单")
            return form_result
            
        except Exception as e:
            error_msg = f"表单构建失败: {str(e)}"
            self.logger.error(error_msg)
            raise FormBuildingError(error_msg)
    
    @handle_errors
    def calculate(self, definition: str, context_variables: Dict[str, Variable]) -> Any:
        """
        计算变量值
        
        Args:
            definition: 变量定义
            context_variables: 上下文变量
            
        Returns:
            Any: 计算结果
        """
        start_time = time.time()
        
        self.logger.debug(f"计算变量定义: {definition}")
        
        # 使用CalculationEngineFlow进行计算
        result = self.calculation_flow.calculate(definition, context_variables)
        
        if not result.success:
            raise CalculationEngineError(result.error_message)
        
        # 记录性能指标
        execution_time = time.time() - start_time
        self.performance_monitor.record_metric(
            "calculate_execution_time",
            execution_time,
            tags={"definition_length": len(definition), "success": True}
        )
        
        return result.value


class CalculationEngineFlow:
    """计算引擎流程 - 按照标准流程实现变量计算"""
    
    def __init__(self, config_manager, csv_processor):
        """
        初始化计算引擎流程
        
        Args:
            config_manager: 配置管理器实例
            csv_processor: CSV处理器实例
        """
        self.config_manager = config_manager
        self.csv_processor = csv_processor
        self.logger = get_logger("CalculationEngineFlow")
        self.cache = get_global_cache_manager()  # 添加缓存管理器
        self.performance_monitor = get_global_performance_monitor()  # 添加性能监控器
        self.define_registry = None
        self.relation_registry = None
    
    @handle_errors
    def calculate(self, definition: str, context_variables: Dict[str, Variable]) -> CalculationResult:
        """
        计算变量值的完整流程
        
        Args:
            definition: 变量定义
            context_variables: 上下文变量
            
        Returns:
            CalculationResult: 计算结果
        """
        start_time = time.time()
        
        self.logger.debug(f"开始计算: {definition}")
        
        # 1. 加载配置注册表
        self._load_registries()
        
        # 2. 解析定义类型
        definition_type = self._parse_definition_type(definition)
        
        # 3. 根据类型分派计算
        if definition_type == 'size':
            result = self._calculate_size(definition, context_variables)
        elif definition_type == 'define':
            result = self._calculate_define(definition, context_variables)
        elif definition_type == 'relation':
            result = self._calculate_relation(definition, context_variables)
        elif definition_type == 'fixed':
            result = self._parse_fixed_value(definition)
        elif definition_type == 'expression':
            result = self._calculate_expression(definition, context_variables)
        else:
            raise CalculationEngineError(f"未知的定义类型: {definition}")
        
        self.logger.debug(f"计算完成: {definition} = {result}")
        
        # 记录性能指标
        execution_time = time.time() - start_time
        self.performance_monitor.record_metric(
            "flow_calculate_execution_time",
            execution_time,
            tags={"definition_type": definition_type, "success": True}
        )
        
        return CalculationResult.success(result)
    
    def _load_registries(self) -> None:
        """加载配置注册表"""
        try:
            # 检查缓存
            define_cache_key = "define_registry_cache"
            relation_cache_key = "relation_registry_cache"
            
            cached_define = self.cache.get(define_cache_key)
            cached_relation = self.cache.get(relation_cache_key)
            
            if cached_define is not None and cached_relation is not None:
                self.define_registry = cached_define
                self.relation_registry = cached_relation
                self.logger.debug("从缓存加载注册表")
                return
            
            # 加载type_define.csv
            type_define_data = self.config_manager.get_config('type_define.csv')
            if type_define_data:
                self.define_registry = {}
                for row in type_define_data:
                    if 'DEFINE' in row:
                        define_config = DefineConfig(
                            name=row['DEFINE'],
                            before=row.get('BEFORE', ''),
                            after=row.get('AFTER', ''),
                            chngvl=row.get('CHNGVL', ''),
                            calc=row.get('CALC', ''),
                            target=row.get('TARGET', '')
                        )
                        self.define_registry[row['DEFINE']] = define_config
            
            # 加载type_relation.csv
            type_relation_data = self.config_manager.get_config('type_relation.csv')
            if type_relation_data:
                self.relation_registry = {}
                for row in type_relation_data:
                    if 'DEFINE' in row:
                        relation_config = self._parse_relation_config(row)
                        self.relation_registry[row['DEFINE']] = relation_config
            
            # 缓存注册表
            self.cache.set(define_cache_key, self.define_registry)
            self.cache.set(relation_cache_key, self.relation_registry)
            
            self.logger.debug(f"注册表加载完成: {len(self.define_registry or {})} 个define, {len(self.relation_registry or {})} 个relation")
            
        except Exception as e:
            raise CalculationEngineError(f"注册表加载失败: {str(e)}")
    
    def _parse_relation_config(self, row: Dict[str, Any]) -> RelationConfig:
        """解析relation配置"""
        relation_config = RelationConfig(name=row['DEFINE'])
        conditions = []
        
        # 解析条件（假设条件格式为: 条件1=值1,条件2=值2,...）
        condition_str = row.get('CONDITION', '')
        value_str = row.get('VALUE', '')
        
        if condition_str and value_str:
            # 分割条件和值
            condition_parts = condition_str.split(',')
            value_parts = value_str.split(',')
            
            for i, condition_part in enumerate(condition_parts):
                if i < len(value_parts):
                    condition = self._parse_condition(condition_part, value_parts[i])
                    if condition:
                        conditions.append(condition)
        
        relation_config.conditions = conditions
        relation_config.default_value = row.get('DEFAULT', None)
        
        return relation_config
    
    def _parse_condition(self, condition_str: str, value_str: str) -> Optional[Condition]:
        """解析条件字符串"""
        try:
            # 支持的操作符
            operators = ['=', '>', '<', '>=', '<=', '!=', 'and', 'or']
            
            for operator in operators:
                if operator in condition_str:
                    parts = condition_str.split(operator)
                    if len(parts) == 2:
                        return Condition(
                            left_operand=parts[0].strip(),
                            operator=operator,
                            right_operand=parts[1].strip(),
                            value=value_str.strip()
                        )
            
            return None
            
        except Exception as e:
            self.logger.warning(f"条件解析失败 {condition_str}: {str(e)}")
            return None
    
    def _parse_definition_type(self, definition: str) -> str:
        """解析定义类型"""
        if not definition:
            return 'fixed'
        
        definition = definition.strip()
        
        # 检查是否为size类型 (size*)
        if definition.startswith('size*'):
            return 'size'
        
        # 检查是否为define类型 (define*)
        if definition.startswith('define*'):
            return 'define'
        
        # 检查是否为relation类型 (relation*)
        if definition.startswith('relation*'):
            return 'relation'
        
        # 检查是否为表达式 (包含运算符)
        if any(op in definition for op in ['+', '-', '*', '/', '(', ')']):
            return 'expression'
        
        # 默认为固定值
        return 'fixed'
    
    @handle_errors
    def _calculate_size(self, definition: str, context_variables: Dict[str, Variable]) -> Any:
        """计算size类型的值"""
        start_time = time.time()
        
        try:
            # 解析size定义格式: size*目标字符串
            target_str = definition[5:]  # 去掉'size*'
            
            # 获取目标字符串的值
            target_value = self._get_target_string_value(target_str, context_variables)
            
            result = len(str(target_value))
            
            # 记录性能指标
            execution_time = time.time() - start_time
            self.performance_monitor.record_metric(
                "calculate_size_execution_time",
                execution_time,
                tags={"definition_length": len(definition), "success": True}
            )
            
            return result
            
        except Exception as e:
            raise CalculationEngineError(f"size计算失败 {definition}: {str(e)}")
    
    @handle_errors
    def _calculate_define(self, define_name: str, context_variables: Dict[str, Variable]) -> Any:
        """计算define类型的值"""
        start_time = time.time()
        
        try:
            # 解析define名称
            actual_define_name = define_name[7:]  # 去掉'define*'
            
            # 1. 查找define定义
            define_config = self.define_registry.get(actual_define_name)
            if not define_config:
                raise CalculationEngineError(f"未找到define定义: {actual_define_name}")
            
            # 2. 获取目标字符串
            target_string = self._get_target_string(define_config, context_variables)
            
            # 3. 应用BEFORE->AFTER转换
            transformed_value = self._apply_string_transformation(target_string, define_config)
            
            # 4. 应用chngValue转换（如果配置了）
            if define_config.chngvl:
                chnged_value = self._apply_chngvalue_transformation(transformed_value, define_config.chngvl)
                transformed_value = chnged_value
            
            # 5. 应用计算（如果配置了）
            if define_config.calc:
                calculated_value = self._apply_calculation(transformed_value, define_config.calc)
                transformed_value = calculated_value
            
            # 记录性能指标
            execution_time = time.time() - start_time
            self.performance_monitor.record_metric(
                "calculate_define_execution_time",
                execution_time,
                tags={"define_name": actual_define_name, "success": True}
            )
            
            return transformed_value
            
        except Exception as e:
            raise CalculationEngineError(f"define计算失败 {define_name}: {str(e)}")
    
    def _get_target_string(self, define_config: DefineConfig, context_variables: Dict[str, Variable]) -> str:
        """获取目标字符串"""
        target = define_config.target
        
        if not target:
            return ""
        
        # 如果target是变量名，获取变量值
        if target in context_variables:
            variable = context_variables[target]
            return str(variable.value) if variable.value is not None else ""
        
        # 否则直接返回target
        return target
    
    def _apply_string_transformation(self, target_string: str, define_config: DefineConfig) -> str:
        """应用字符串转换 (BEFORE -> AFTER)"""
        result = target_string
        
        if define_config.before and define_config.after:
            result = result.replace(define_config.before, define_config.after)
        
        return result
    
    def _apply_chngvalue_transformation(self, value: str, chngvl_config: str) -> Any:
        """应用chngValue转换"""
        try:
            # 解析chngvl配置格式: 原值1=新值1,原值2=新值2,...
            transformations = {}
            for transformation in chngvl_config.split(','):
                if '=' in transformation:
                    old_val, new_val = transformation.split('=', 1)
                    transformations[old_val.strip()] = new_val.strip()
            
            # 应用转换
            return transformations.get(value, value)
            
        except Exception as e:
            self.logger.warning(f"chngValue转换失败 {chngvl_config}: {str(e)}")
            return value
    
    def _apply_calculation(self, value: str, calc_config: str) -> Any:
        """应用计算"""
        try:
            # 简单的计算支持: +, -, *, /
            if '+' in calc_config:
                parts = calc_config.split('+')
                return float(value) + sum(float(p.strip()) for p in parts[1:])
            elif '-' in calc_config:
                parts = calc_config.split('-')
                result = float(value)
                for p in parts[1:]:
                    result -= float(p.strip())
                return result
            elif '*' in calc_config:
                parts = calc_config.split('*')
                result = float(value)
                for p in parts[1:]:
                    result *= float(p.strip())
                return result
            elif '/' in calc_config:
                parts = calc_config.split('/')
                result = float(value)
                for p in parts[1:]:
                    divisor = float(p.strip())
                    if divisor == 0:
                        raise CalculationEngineError("除数不能为零")
                    result /= divisor
                return result
            else:
                # 直接数值计算
                return eval(f"{value} {calc_config}")
                
        except Exception as e:
            raise CalculationEngineError(f"计算失败 {calc_config}: {str(e)}")
    
    @handle_errors
    def _calculate_relation(self, relation_name: str, context_variables: Dict[str, Variable]) -> Any:
        """计算relation类型的值"""
        start_time = time.time()
        
        try:
            # 解析relation名称
            actual_relation_name = relation_name[9:]  # 去掉'relation*'
            
            relation_config = self.relation_registry.get(actual_relation_name)
            if not relation_config:
                raise CalculationEngineError(f"未找到relation定义: {actual_relation_name}")
            
            for condition in relation_config.conditions:
                if self._evaluate_condition(condition, context_variables):
                    result = self._get_condition_value(condition.value, context_variables)
                    
                    # 记录性能指标
                    execution_time = time.time() - start_time
                    self.performance_monitor.record_metric(
                        "calculate_relation_execution_time",
                        execution_time,
                        tags={"relation_name": actual_relation_name, "success": True}
                    )
                    
                    return result
            
            # 如果没有条件匹配，返回默认值或抛出错误
            if relation_config.default_value is not None:
                result = relation_config.default_value
                
                # 记录性能指标
                execution_time = time.time() - start_time
                self.performance_monitor.record_metric(
                    "calculate_relation_execution_time",
                    execution_time,
                    tags={"relation_name": actual_relation_name, "success": True}
                )
                
                return result
            else:
                raise CalculationEngineError(f"relation条件都不满足: {actual_relation_name}")
                
        except Exception as e:
            raise CalculationEngineError(f"relation计算失败 {relation_name}: {str(e)}")
    
    def _evaluate_condition(self, condition: Condition, context_variables: Dict[str, Variable]) -> bool:
        """评估条件表达式"""
        try:
            left_value = self._get_variable_value(condition.left_operand, context_variables)
            right_value = self._get_variable_value(condition.right_operand, context_variables)
            
            # 转换为数值进行比较（如果可能）
            try:
                left_num = float(left_value)
                right_num = float(right_value)
                left_value, right_value = left_num, right_num
            except (ValueError, TypeError):
                pass  # 保持为字符串比较
            
            if condition.operator == '=':
                return left_value == right_value
            elif condition.operator == '>':
                return left_value > right_value
            elif condition.operator == '<':
                return left_value < right_value
            elif condition.operator == '>=':
                return left_value >= right_value
            elif condition.operator == '<=':
                return left_value <= right_value
            elif condition.operator == '!=':
                return left_value != right_value
            elif condition.operator == 'and':
                return bool(left_value) and bool(right_value)
            elif condition.operator == 'or':
                return bool(left_value) or bool(right_value)
            else:
                raise ConditionEvaluationError(f"不支持的操作符: {condition.operator}")
                
        except Exception as e:
            raise ConditionEvaluationError(f"条件评估失败: {str(e)}")
    
    def _get_variable_value(self, operand: str, context_variables: Dict[str, Variable]) -> Any:
        """获取变量值"""
        # 如果是变量名，获取变量值
        if operand in context_variables:
            variable = context_variables[operand]
            return variable.value if variable.value is not None else 0
        
        # 否则尝试解析为数值或字符串
        try:
            return float(operand)
        except ValueError:
            return operand.strip('"\'')  # 去掉引号
    
    def _get_condition_value(self, value_str: str, context_variables: Dict[str, Variable]) -> Any:
        """获取条件值"""
        # 如果是变量名，获取变量值
        if value_str in context_variables:
            variable = context_variables[value_str]
            return variable.value
        
        # 否则尝试解析为数值或字符串
        try:
            return float(value_str)
        except ValueError:
            return value_str.strip('"\'')  # 去掉引号
    
    def _parse_fixed_value(self, definition: str) -> Any:
        """解析固定值"""
        try:
            # 尝试解析为数值
            return float(definition)
        except ValueError:
            # 返回字符串（去掉可能的引号）
            return definition.strip('"\'')
    
    @handle_errors
    def _calculate_expression(self, expression: str, context_variables: Dict[str, Variable]) -> Any:
        """计算表达式"""
        start_time = time.time()
        
        try:
            # 替换变量引用
            evaluated_expression = expression
            for var_name, variable in context_variables.items():
                if var_name in evaluated_expression and variable.value is not None:
                    evaluated_expression = evaluated_expression.replace(var_name, str(variable.value))
            
            # 安全地计算表达式
            result = eval(evaluated_expression)
            
            # 记录性能指标
            execution_time = time.time() - start_time
            self.performance_monitor.record_metric(
                "calculate_expression_execution_time",
                execution_time,
                tags={"expression_length": len(expression), "success": True}
            )
            
            return result
            
        except Exception as e:
            raise CalculationEngineError(f"表达式计算失败 {expression}: {str(e)}")
    
    def _get_target_string_value(self, target_str: str, context_variables: Dict[str, Variable]) -> str:
        """获取目标字符串的值"""
        # 如果是变量名，获取变量值
        if target_str in context_variables:
            variable = context_variables[target_str]
            return str(variable.value) if variable.value is not None else ""
        
        # 否则直接返回字符串
        return target_str


class FormBuildingFlow:
    """表单构建流程 - 按照标准流程实现表单构建与变量计算"""
    
    def __init__(self, config_manager, csv_processor):
        """
        初始化表单构建流程
        
        Args:
            config_manager: 配置管理器实例
            csv_processor: CSV处理器实例
        """
        self.config_manager = config_manager
        self.csv_processor = csv_processor
        self.logger = get_logger("FormBuildingFlow")
        self.cache = get_global_cache_manager()  # 添加缓存管理器
        self.performance_monitor = get_global_performance_monitor()  # 添加性能监控器
        self.calculation_engine = None
    
    @handle_errors
    def build_forms(self, program_sequence: List[str], 
                   model_segments: List[str]) -> FormBuildingResult:
        """
        构建表单的完整流程
        
        Args:
            program_sequence: 程序序列
            model_segments: 型号片段
            
        Returns:
            FormBuildingResult: 构建结果
        """
        start_time = time.time()
        
        self.logger.info(f"开始构建表单: 程序序列={program_sequence}, 型号片段={model_segments}")
        
        # 1. 初始化计算引擎
        self.calculation_engine = CalculationEngine(self.config_manager, self.csv_processor)
        
        forms = {}
        all_variables = {}
        
        for program_name in program_sequence:
            # 2. 加载程序配置
            program_config = self._load_program_config(program_name)
            
            # 3. 创建变量集合
            program_variables = self._create_variables(
                program_config, 
                model_segments,
                program_name
            )
            
            # 4. 计算变量初始值
            calculated_variables = self._calculate_initial_values(program_variables)
            
            # 5. 构建表单配置
            form_config = self._build_form_config(program_config, calculated_variables)
            
            forms[program_name] = form_config
            all_variables.update(calculated_variables)
        
        self.logger.info(f"表单构建完成: {len(forms)} 个表单, {len(all_variables)} 个变量")
        
        # 记录性能指标
        execution_time = time.time() - start_time
        self.performance_monitor.record_metric(
            "build_forms_execution_time",
            execution_time,
            tags={"program_count": len(program_sequence), "success": True}
        )
        
        return FormBuildingResult(
            forms=forms,
            variables=all_variables,
            active_program=program_sequence[0] if program_sequence else None
        )
    
    def _load_program_config(self, program_name: str) -> ProgramConfig:
        """加载程序配置"""
        try:
            self.logger.debug(f"加载程序配置: {program_name}")
            
            # 加载cntrl.csv配置
            ctrl_config = self._load_ctrl_config(program_name)
            
            # 加载load.csv配置
            load_config = self._load_load_config(program_name)
            
            return ProgramConfig(
                name=program_name,
                ctrl_config=ctrl_config,
                load_config=load_config
            )
            
        except Exception as e:
            raise FormBuildingError(f"程序配置加载失败 {program_name}: {str(e)}")
    
    def _load_ctrl_config(self, program_name: str) -> List[Dict[str, Any]]:
        """加载cntrl.csv配置"""
        try:
            # 检查缓存
            cache_key = f"ctrl_config_{program_name}"
            cached_config = self.cache.get(cache_key)
            if cached_config is not None:
                self.logger.debug(f"从缓存加载cntrl配置: {program_name}")
                return cached_config
            
            cntrl_config = self.config_manager.get_config('cntrl.csv')
            if not cntrl_config:
                return []
            
            # 过滤出当前程序的配置
            program_ctrl = [
                row for row in cntrl_config 
                if row.get('PRG') == program_name
            ]
            
            # 缓存配置
            self.cache.set(cache_key, program_ctrl)
            
            self.logger.debug(f"加载cntrl配置: {program_name} -> {len(program_ctrl)} 个变量")
            return program_ctrl
            
        except Exception as e:
            self.logger.warning(f"cntrl配置加载失败 {program_name}: {str(e)}")
            return []
    
    def _load_load_config(self, program_name: str) -> List[Dict[str, Any]]:
        """加载load.csv配置"""
        try:
            # 检查缓存
            cache_key = f"load_config_{program_name}"
            cached_config = self.cache.get(cache_key)
            if cached_config is not None:
                self.logger.debug(f"从缓存加载load配置: {program_name}")
                return cached_config
            
            load_config = self.config_manager.get_config('load.csv')
            if not load_config:
                return []
            
            # 过滤出当前程序的配置
            program_load = [
                row for row in load_config 
                if row.get('PRG') == program_name
            ]
            
            # 缓存配置
            self.cache.set(cache_key, program_load)
            
            self.logger.debug(f"加载load配置: {program_name} -> {len(program_load)} 个定义")
            return program_load
            
        except Exception as e:
            self.logger.warning(f"load配置加载失败 {program_name}: {str(e)}")
            return []
    
    def _create_variables(self, program_config: ProgramConfig, 
                         model_segments: List[str], 
                         program_name: str) -> Dict[str, Variable]:
        """创建变量对象"""
        variables = {}
        
        # 从cntrl.csv创建变量定义
        for ctrl_row in program_config.ctrl_config:
            var_name = ctrl_row.get('MACRO', '')
            if not var_name:
                continue
                
            variable = Variable(
                name=var_name,
                kind=ctrl_row.get('KIND', ''),
                display_flag=ctrl_row.get('DISPFLG', 1) == 1,
                send_flag=ctrl_row.get('SENDFLG', 1) == 1,
                min_value=self._parse_numeric_value(ctrl_row.get('MIN')),
                max_value=self._parse_numeric_value(ctrl_row.get('MAX')),
                label_text=ctrl_row.get('LABELTXT', '')
            )
            variables[var_name] = variable
        
        # 从load.csv设置变量定义
        matching_load_config = self._find_matching_load_config(program_config.load_config, model_segments)
        if matching_load_config:
            for load_row in matching_load_config:
                var_name = load_row.get('MACRO', '')
                definition = load_row.get('DEFINE', '')
                
                if var_name in variables and definition:
                    variables[var_name].definition = definition
        
        self.logger.debug(f"创建变量: {program_name} -> {len(variables)} 个变量")
        return variables
    
    def _find_matching_load_config(self, load_config: List[Dict[str, Any]], 
                                  model_segments: List[str]) -> List[Dict[str, Any]]:
        """查找匹配的load配置"""
        if not load_config or not model_segments:
            return []
        
        # 构建型号字符串用于匹配
        model_string = '-'.join(model_segments)
        
        matching_configs = []
        for load_row in load_config:
            condition = load_row.get('CONDITION', '')
            
            # 如果没有条件，直接匹配
            if not condition:
                matching_configs.append(load_row)
                continue
            
            # 检查条件是否匹配
            if self._evaluate_load_condition(condition, model_string, model_segments):
                matching_configs.append(load_row)
        
        return matching_configs
    
    def _evaluate_load_condition(self, condition: str, model_string: str, 
                                model_segments: List[str]) -> bool:
        """评估load条件"""
        try:
            # 简单的条件评估逻辑
            # 支持包含、等于等简单条件
            if '=' in condition:
                key, value = condition.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                if key == 'MODEL':
                    return model_string == value
                elif key == 'SEGMENT':
                    return value in model_segments
            elif condition in model_string:
                return True
                
            return False
            
        except Exception as e:
            self.logger.warning(f"条件评估失败 {condition}: {str(e)}")
            return False
    
    @handle_errors
    def _calculate_initial_values(self, variables: Dict[str, Variable]) -> Dict[str, Variable]:
        """计算变量初始值"""
        start_time = time.time()
        
        self.logger.debug("开始计算变量初始值")
        
        # 获取计算顺序（依赖关系分析）
        calculation_order = self._get_calculation_order(variables)
        
        for var_name in calculation_order:
            variable = variables[var_name]
            if variable.definition:
                try:
                    value = self.calculation_engine.calculate(
                        variable.definition, 
                        variables
                    )
                    variable.value = value
                    self.logger.debug(f"计算变量 {var_name} = {value}")
                except CalculationEngineError as e:
                    variable.error_message = str(e)
                    self.logger.warning(f"计算变量 {var_name} 失败: {e}")
                    variable.value = None
        
        self.logger.debug("变量初始值计算完成")
        
        # 记录性能指标
        execution_time = time.time() - start_time
        self.performance_monitor.record_metric(
            "calculate_initial_values_execution_time",
            execution_time,
            tags={"variable_count": len(variables), "success": True}
        )
        
        return variables
    
    def _get_calculation_order(self, variables: Dict[str, Variable]) -> List[str]:
        """获取计算顺序（依赖关系分析）"""
        # 简单的依赖分析：先计算没有依赖的变量，再计算有依赖的变量
        independent_vars = []
        dependent_vars = []
        
        for var_name, variable in variables.items():
            if not variable.definition:
                independent_vars.append(var_name)
            else:
                # 检查定义中是否引用了其他变量
                has_dependency = any(
                    ref_var in variable.definition for ref_var in variables.keys()
                    if ref_var != var_name
                )
                if has_dependency:
                    dependent_vars.append(var_name)
                else:
                    independent_vars.append(var_name)
        
        return independent_vars + dependent_vars
    
    def _build_form_config(self, program_config: ProgramConfig, 
                          variables: Dict[str, Variable]) -> Dict[str, Any]:
        """构建表单配置"""
        form_config = {
            'program_name': program_config.name,
            'variables': {},
            'layout': {}
        }
        
        # 构建变量配置
        for var_name, variable in variables.items():
            if variable.display_flag:
                form_config['variables'][var_name] = {
                    'name': variable.name,
                    'kind': variable.kind,
                    'value': variable.value,
                    'min_value': variable.min_value,
                    'max_value': variable.max_value,
                    'label_text': variable.label_text,
                    'error_message': variable.error_message
                }
        
        # 构建布局配置（可以根据需要扩展）
        form_config['layout'] = self._build_layout_config(variables)
        
        self.logger.debug(f"构建表单配置: {program_config.name} -> {len(form_config['variables'])} 个显示变量")
        return form_config
    
    def _build_layout_config(self, variables: Dict[str, Variable]) -> Dict[str, Any]:
        """构建布局配置"""
        # 简单的布局配置，可以根据变量类型分组
        layout = {
            'groups': [],
            'controls': []
        }
        
        # 按变量类型分组
        groups = {}
        for var_name, variable in variables.items():
            if variable.display_flag:
                group_name = variable.kind or 'default'
                if group_name not in groups:
                    groups[group_name] = []
                groups[group_name].append(var_name)
        
        # 构建分组配置
        for group_name, var_names in groups.items():
            layout['groups'].append({
                'name': group_name,
                'variables': var_names
            })
        
        return layout
    
    def _parse_numeric_value(self, value_str: str) -> Optional[float]:
        """解析数值"""
        if not value_str:
            return None
        
        try:
            return float(value_str)
        except (ValueError, TypeError):
            return None