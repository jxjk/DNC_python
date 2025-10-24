"""
计算引擎
负责参数计算和公式处理
"""

import logging
import re
import math
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

from ..core.config import ConfigManager
from ..data.csv_processor import CSVProcessor


@dataclass
class CalculationStep:
    """计算步骤"""
    step_no: int
    operation: str
    operands: List[str]
    result: Any
    description: str


@dataclass
class CalculationResult:
    """计算结果"""
    program_no: int
    parameters: Dict[str, Any]
    calculation_steps: List[CalculationStep]
    success: bool
    error_message: Optional[str] = None


class CalculationEngine:
    """计算引擎"""
    
    def __init__(self, config_manager: ConfigManager, csv_processor: CSVProcessor):
        """
        初始化计算引擎
        
        Args:
            config_manager: 配置管理器
            csv_processor: CSV处理器
        """
        self.config_manager = config_manager
        self.csv_processor = csv_processor
        self.logger = logging.getLogger(__name__)
        
        # 加载计算数据
        self.load_data = None
        self.define_data = None
        self.chng_value_data = None
        self.calc_data = None
        self._load_calculation_data()
        
        # 变量存储
        self.variables: Dict[str, Any] = {}
        
    def _load_calculation_data(self) -> None:
        """加载计算数据"""
        try:
            # 加载加载数据
            load_path = self.config_manager.get_csv_config_path("load.csv")
            self.load_data = self.csv_processor.read_csv(load_path)
            
            # 加载定义数据
            define_path = self.config_manager.get_csv_config_path("define.csv")
            self.define_data = self.csv_processor.read_csv(define_path)
            
            # 加载值变更数据
            chng_value_path = self.config_manager.get_csv_config_path("chngValue.csv")
            self.chng_value_data = self.csv_processor.read_csv(chng_value_path)
            
            # 加载计算数据
            calc_path = self.config_manager.get_csv_config_path("calc.csv")
            self.calc_data = self.csv_processor.read_csv(calc_path)
            
            self.logger.info("计算数据加载成功")
            
        except Exception as e:
            self.logger.error(f"计算数据加载失败: {e}")
    
    def calculate_parameters(self, program_no: int, input_data: Dict[str, Any] = None) -> CalculationResult:
        """
        计算参数
        
        Args:
            program_no: 程序编号
            input_data: 输入数据
            
        Returns:
            CalculationResult: 计算结果
        """
        try:
            self.logger.info(f"开始计算参数，程序: {program_no}")
            
            # 重置变量
            self.variables.clear()
            
            # 设置输入数据
            if input_data:
                self.variables.update(input_data)
            
            calculation_steps = []
            
            # 执行加载操作
            load_steps = self._execute_load_operations(program_no)
            calculation_steps.extend(load_steps)
            
            # 执行定义操作
            define_steps = self._execute_define_operations(program_no)
            calculation_steps.extend(define_steps)
            
            # 执行计算操作
            calc_steps = self._execute_calc_operations(program_no)
            calculation_steps.extend(calc_steps)
            
            # 构建结果
            result = CalculationResult(
                program_no=program_no,
                parameters=self.variables.copy(),
                calculation_steps=calculation_steps,
                success=True
            )
            
            self.logger.info(f"参数计算完成，程序: {program_no}, 参数数量: {len(self.variables)}")
            return result
            
        except Exception as e:
            self.logger.error(f"参数计算失败: {e}")
            return CalculationResult(
                program_no=program_no,
                parameters={},
                calculation_steps=[],
                success=False,
                error_message=str(e)
            )
    
    def _execute_load_operations(self, program_no: int) -> List[CalculationStep]:
        """
        执行加载操作
        
        Args:
            program_no: 程序编号
            
        Returns:
            List[CalculationStep]: 计算步骤列表
        """
        steps = []
        
        if not self.load_data:
            return steps
        
        for row in self.load_data:
            if len(row) >= 3:
                try:
                    load_no = int(row[0])
                    macro = row[1]
                    value = row[2]
                    
                    # 只处理当前程序相关的加载操作
                    if load_no == program_no:
                        # 解析值
                        parsed_value = self._parse_value(value)
                        
                        # 设置变量
                        self.variables[macro] = parsed_value
                        
                        step = CalculationStep(
                            step_no=len(steps) + 1,
                            operation="LOAD",
                            operands=[macro, value],
                            result=parsed_value,
                            description=f"加载变量 {macro} = {value}"
                        )
                        steps.append(step)
                        
                except (ValueError, IndexError) as e:
                    self.logger.warning(f"加载操作解析失败: {row}, 错误: {e}")
        
        return steps
    
    def _execute_define_operations(self, program_no: int) -> List[CalculationStep]:
        """
        执行定义操作
        
        Args:
            program_no: 程序编号
            
        Returns:
            List[CalculationStep]: 计算步骤列表
        """
        steps = []
        
        if not self.define_data:
            return steps
        
        for row in self.define_data:
            if len(row) >= 6:
                try:
                    define_name = row[0]
                    search_str = row[1]
                    before_str = row[2]
                    after_str = row[3]
                    chng_value = row[4]
                    calc_name = row[5]
                    
                    # 查找匹配的字符串
                    matched_value = self._find_matching_value(search_str)
                    if matched_value is not None:
                        # 执行字符串替换
                        processed_value = self._process_string_replacement(
                            matched_value, before_str, after_str
                        )
                        
                        # 执行值变更
                        if chng_value:
                            processed_value = self._apply_value_change(processed_value, chng_value)
                        
                        # 执行计算
                        if calc_name:
                            processed_value = self._execute_calculation(processed_value, calc_name)
                        
                        # 设置定义变量
                        self.variables[define_name] = processed_value
                        
                        step = CalculationStep(
                            step_no=len(steps) + 1,
                            operation="DEFINE",
                            operands=[define_name, search_str, before_str, after_str],
                            result=processed_value,
                            description=f"定义变量 {define_name} = {processed_value}"
                        )
                        steps.append(step)
                        
                except (ValueError, IndexError) as e:
                    self.logger.warning(f"定义操作解析失败: {row}, 错误: {e}")
        
        return steps
    
    def _execute_calc_operations(self, program_no: int) -> List[CalculationStep]:
        """
        执行计算操作
        
        Args:
            program_no: 程序编号
            
        Returns:
            List[CalculationStep]: 计算步骤列表
        """
        steps = []
        
        if not self.calc_data:
            return steps
        
        for row in self.calc_data:
            if len(row) >= 2:
                try:
                    calc_name = row[0]
                    expression_parts = row[1:]
                    
                    # 构建表达式
                    expression = self._build_expression(expression_parts)
                    if expression:
                        # 计算表达式
                        result = self._evaluate_expression(expression)
                        
                        # 设置计算变量
                        self.variables[calc_name] = result
                        
                        step = CalculationStep(
                            step_no=len(steps) + 1,
                            operation="CALC",
                            operands=[calc_name] + expression_parts,
                            result=result,
                            description=f"计算 {calc_name} = {expression} = {result}"
                        )
                        steps.append(step)
                        
                except (ValueError, IndexError) as e:
                    self.logger.warning(f"计算操作解析失败: {row}, 错误: {e}")
        
        return steps
    
    def _parse_value(self, value: str) -> Any:
        """
        解析值
        
        Args:
            value: 原始值字符串
            
        Returns:
            Any: 解析后的值
        """
        # 尝试解析为数字
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            # 如果是字符串，直接返回
            return value
    
    def _find_matching_value(self, search_str: str) -> Optional[str]:
        """
        查找匹配的值
        
        Args:
            search_str: 搜索字符串
            
        Returns:
            Optional[str]: 匹配的值
        """
        # 在变量中查找
        for var_name, var_value in self.variables.items():
            if search_str in var_name or search_str == str(var_value):
                return str(var_value)
        
        return None
    
    def _process_string_replacement(self, value: str, before_str: str, after_str: str) -> str:
        """
        处理字符串替换
        
        Args:
            value: 原始值
            before_str: 替换前字符串
            after_str: 替换后字符串
            
        Returns:
            str: 处理后的字符串
        """
        if before_str and after_str:
            return value.replace(before_str, after_str)
        return value
    
    def _apply_value_change(self, value: str, chng_value: str) -> Any:
        """
        应用值变更
        
        Args:
            value: 原始值
            chng_value: 变更值名称
            
        Returns:
            Any: 变更后的值
        """
        if not self.chng_value_data:
            return value
        
        # 查找变更规则
        for row in self.chng_value_data:
            if len(row) >= 3 and row[0] == chng_value:
                before_str = row[1]
                after_str = row[2]
                
                # 执行替换
                if before_str and after_str:
                    try:
                        # 尝试数值转换
                        if value.isdigit():
                            return int(after_str)
                        elif self._is_float(value):
                            return float(after_str)
                        else:
                            return value.replace(before_str, after_str)
                    except (ValueError, TypeError):
                        return value.replace(before_str, after_str)
        
        return value
    
    def _execute_calculation(self, value: Any, calc_name: str) -> Any:
        """
        执行计算
        
        Args:
            value: 输入值
            calc_name: 计算名称
            
        Returns:
            Any: 计算结果
        """
        # 这里可以添加特定的计算逻辑
        # 例如：单位转换、公式计算等
        return value
    
    def _build_expression(self, parts: List[str]) -> Optional[str]:
        """
        构建表达式
        
        Args:
            parts: 表达式部分列表
            
        Returns:
            Optional[str]: 构建的表达式
        """
        expression = ""
        for part in parts:
            if part in ['+', '-', '*', '/', '=', '(', ')']:
                expression += f" {part} "
            else:
                # 检查是否是变量
                if part in self.variables:
                    expression += str(self.variables[part])
                else:
                    # 尝试解析为数值
                    try:
                        float(part)
                        expression += part
                    except ValueError:
                        # 保持原样
                        expression += part
        
        return expression.strip() if expression else None
    
    def _evaluate_expression(self, expression: str) -> Any:
        """
        计算表达式
        
        Args:
            expression: 表达式字符串
            
        Returns:
            Any: 计算结果
        """
        try:
            # 使用安全的eval
            result = eval(expression, {"__builtins__": {}}, self.variables.copy())
            return result
        except Exception as e:
            self.logger.error(f"表达式计算失败: {expression}, 错误: {e}")
            return 0
    
    def _is_float(self, value: str) -> bool:
        """
        检查字符串是否可以转换为浮点数
        
        Args:
            value: 字符串值
            
        Returns:
            bool: 是否可以转换为浮点数
        """
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def batch_calculate(self, program_data: List[Tuple[int, Dict[str, Any]]]) -> List[CalculationResult]:
        """
        批量计算参数
        
        Args:
            program_data: 程序数据列表，每个元素为(程序编号, 输入数据)
            
        Returns:
            List[CalculationResult]: 计算结果列表
        """
        results = []
        for program_no, input_data in program_data:
            result = self.calculate_parameters(program_no, input_data)
            results.append(result)
        
        self.logger.info(f"批量计算完成，共处理{len(program_data)}个程序")
        return results
    
    def get_calculation_statistics(self, results: List[CalculationResult]) -> Dict[str, Any]:
        """
        获取计算统计信息
        
        Args:
            results: 计算结果列表
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        total = len(results)
        successful = sum(1 for r in results if r.success)
        failed = total - successful
        
        total_steps = sum(len(r.calculation_steps) for r in results if r.success)
        avg_steps = total_steps / successful if successful > 0 else 0
        
        total_parameters = sum(len(r.parameters) for r in results if r.success)
        avg_parameters = total_parameters / successful if successful > 0 else 0
        
        return {
            "total": total,
            "successful": successful,
            "failed": failed,
            "success_rate": round(successful / total * 100, 2) if total > 0 else 0.0,
            "total_steps": total_steps,
            "average_steps": round(avg_steps, 2),
            "total_parameters": total_parameters,
            "average_parameters": round(avg_parameters, 2)
        }
    
    def reload_calculation_data(self) -> bool:
        """
        重新加载计算数据
        
        Returns:
            bool: 重新加载是否成功
        """
        try:
            self._load_calculation_data()
            self.logger.info("计算数据重新加载成功")
            return True
        except Exception as e:
            self.logger.error(f"计算数据重新加载失败: {e}")
            return False


class AdvancedCalculationEngine(CalculationEngine):
    """高级计算引擎"""
    
    def __init__(self, config_manager: ConfigManager, csv_processor: CSVProcessor):
        """
        初始化高级计算引擎
        
        Args:
            config_manager: 配置管理器
            csv_processor: CSV处理器
        """
        super().__init__(config_manager, csv_processor)
        self.math_functions = {
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'sqrt': math.sqrt,
            'log': math.log,
            'exp': math.exp,
            'abs': abs,
            'round': round
        }
    
    def _evaluate_expression(self, expression: str) -> Any:
        """
        高级表达式计算（支持数学函数）
        
        Args:
            expression: 表达式字符串
            
        Returns:
            Any: 计算结果
        """
        try:
            # 创建安全的计算环境
            safe_dict = self.variables.copy()
            safe_dict.update(self.math_functions)
            safe_dict['math'] = math
            
            # 使用安全的eval
            result = eval(expression, {"__builtins__": {}}, safe_dict)
            return result
        except Exception as e:
            self.logger.error(f"高级表达式计算失败: {expression}, 错误: {e}")
            return 0
    
    def validate_expression(self, expression: str) -> Dict[str, Any]:
        """
        验证表达式
        
        Args:
            expression: 表达式字符串
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        try:
            # 尝试计算表达式
            result = self._evaluate_expression(expression)
            
            return {
                "valid": True,
                "result": result,
                "error_message": None
            }
        except Exception as e:
            return {
                "valid": False,
                "result": None,
                "error_message": str(e)
            }
    
    def optimize_calculation(self, program_no: int) -> CalculationResult:
        """
        优化计算过程
        
        Args:
            program_no: 程序编号
            
        Returns:
            CalculationResult: 优化后的计算结果
        """
        # 这里可以实现计算优化逻辑
        # 例如：缓存中间结果、并行计算等
        return self.calculate_parameters(program_no)
