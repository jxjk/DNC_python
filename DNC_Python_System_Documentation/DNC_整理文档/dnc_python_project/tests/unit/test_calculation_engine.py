"""
计算引擎单元测试
测试计算引擎的各种功能
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.business.calculation_engine import CalculationEngine
from src.core.config import ConfigManager
from src.data.csv_processor import CSVProcessor


class TestCalculationEngine(unittest.TestCase):
    """计算引擎测试类"""

    def setUp(self):
        """测试前准备"""
        # 创建模拟对象
        self.mock_config_manager = Mock(spec=ConfigManager)
        self.mock_csv_processor = Mock(spec=CSVProcessor)
        
        # 设置模拟返回值
        self.mock_config_manager.get_csv_config_path.return_value = "test_path.csv"
        
        # 模拟计算数据
        self.mock_calc_data = [
            ["DEFINE", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
            ["calc1", "=", "calc1", "+", "1", "", "", "", "", "", ""],
            ["calc2", "=", "#500", "*", "2", "", "", "", "", "", ""],
            ["calc3", "=", "#501", "/", "2", "", "", "", "", "", ""],
            ["calc4", "=", "#502", "-", "1", "", "", "", "", "", ""],
            ["calc5", "=", "#503", "+", "#504", "", "", "", "", "", ""]
        ]
        
        self.mock_csv_processor.read_csv.return_value = self.mock_calc_data
        
        # 创建计算引擎实例
        self.calculation_engine = CalculationEngine(
            self.mock_config_manager, 
            self.mock_csv_processor
        )

    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.calculation_engine)
        self.assertEqual(self.calculation_engine.config_manager, self.mock_config_manager)
        self.assertEqual(self.calculation_engine.csv_processor, self.mock_csv_processor)
        self.assertIsNone(self.calculation_engine.calc_data)

    def test_load_calc_data_success(self):
        """测试成功加载计算数据"""
        result = self.calculation_engine.load_calc_data()
        
        self.assertTrue(result)
        self.assertIsNotNone(self.calculation_engine.calc_data)
        self.mock_csv_processor.read_csv.assert_called_once()

    def test_load_calc_data_failure(self):
        """测试加载计算数据失败"""
        # 模拟加载失败
        self.mock_csv_processor.read_csv.side_effect = Exception("加载失败")
        
        result = self.calculation_engine.load_calc_data()
        
        self.assertFalse(result)
        self.assertIsNone(self.calculation_engine.calc_data)

    def test_calculate_simple_expression(self):
        """测试计算简单表达式"""
        # 先加载数据
        self.calculation_engine.load_calc_data()
        
        # 测试简单加法
        parameters = {'#500': 10}
        result = self.calculation_engine.calculate("calc2", parameters)
        
        self.assertEqual(result, 20)  # 10 * 2 = 20

    def test_calculate_complex_expression(self):
        """测试计算复杂表达式"""
        # 先加载数据
        self.calculation_engine.load_calc_data()
        
        # 测试复杂表达式
        parameters = {'#503': 10, '#504': 5}
        result = self.calculation_engine.calculate("calc5", parameters)
        
        self.assertEqual(result, 15)  # 10 + 5 = 15

    def test_calculate_division(self):
        """测试除法计算"""
        # 先加载数据
        self.calculation_engine.load_calc_data()
        
        # 测试除法
        parameters = {'#501': 10}
        result = self.calculation_engine.calculate("calc3", parameters)
        
        self.assertEqual(result, 5)  # 10 / 2 = 5

    def test_calculate_subtraction(self):
        """测试减法计算"""
        # 先加载数据
        self.calculation_engine.load_calc_data()
        
        # 测试减法
        parameters = {'#502': 10}
        result = self.calculation_engine.calculate("calc4", parameters)
        
        self.assertEqual(result, 9)  # 10 - 1 = 9

    def test_calculate_self_reference(self):
        """测试自引用计算"""
        # 先加载数据
        self.calculation_engine.load_calc_data()
        
        # 测试自引用（递归计算）
        result = self.calculation_engine.calculate("calc1", {})
        
        # 自引用应该返回0（基础值）
        self.assertEqual(result, 0)

    def test_calculate_missing_parameters(self):
        """测试计算参数缺失"""
        # 先加载数据
        self.calculation_engine.load_calc_data()
        
        # 测试参数缺失
        result = self.calculation_engine.calculate("calc2", {})
        
        # 参数缺失应该返回0
        self.assertEqual(result, 0)

    def test_calculate_data_not_loaded(self):
        """测试计算数据未加载"""
        # 不加载数据，直接计算
        result = self.calculation_engine.calculate("calc2", {'#500': 10})
        
        # 数据未加载应该返回0
        self.assertEqual(result, 0)

    def test_calculate_unknown_define(self):
        """测试计算未知定义"""
        # 先加载数据
        self.calculation_engine.load_calc_data()
        
        # 测试未知定义
        result = self.calculation_engine.calculate("unknown", {'#500': 10})
        
        # 未知定义应该返回0
        self.assertEqual(result, 0)

    def test_calculate_with_zero_division(self):
        """测试除零计算"""
        # 先加载数据
        self.calculation_engine.load_calc_data()
        
        # 测试除零
        parameters = {'#501': 10}
        # 修改calc3为除零
        self.calculation_engine.calc_data["calc3"] = ["=", "#501", "/", "0"]
        
        result = self.calculation_engine.calculate("calc3", parameters)
        
        # 除零应该返回0
        self.assertEqual(result, 0)

    def test_calculate_with_invalid_expression(self):
        """测试无效表达式计算"""
        # 先加载数据
        self.calculation_engine.load_calc_data()
        
        # 测试无效表达式
        self.calculation_engine.calc_data["invalid"] = ["=", "invalid", "+", "expression"]
        
        result = self.calculation_engine.calculate("invalid", {})
        
        # 无效表达式应该返回0
        self.assertEqual(result, 0)

    def test_evaluate_expression_simple(self):
        """测试评估简单表达式"""
        # 先加载数据
        self.calculation_engine.load_calc_data()
        
        # 测试简单表达式
        result = self.calculation_engine._evaluate_expression(["10", "+", "5"], {})
        
        self.assertEqual(result, 15)

    def test_evaluate_expression_complex(self):
        """测试评估复杂表达式"""
        # 先加载数据
        self.calculation_engine.load_calc_data()
        
        # 测试复杂表达式
        parameters = {'#500': 10, '#501': 5}
        result = self.calculation_engine._evaluate_expression(
            ["#500", "*", "2", "+", "#501"], parameters
        )
        
        self.assertEqual(result, 25)  # 10 * 2 + 5 = 25

    def test_evaluate_expression_with_parentheses(self):
        """测试带括号的表达式"""
        # 先加载数据
        self.calculation_engine.load_calc_data()
        
        # 测试带括号的表达式
        result = self.calculation_engine._evaluate_expression(
            ["(", "10", "+", "5", ")", "*", "2"], {}
        )
        
        self.assertEqual(result, 30)  # (10 + 5) * 2 = 30

    def test_evaluate_expression_operator_precedence(self):
        """测试操作符优先级"""
        # 先加载数据
        self.calculation_engine.load_calc_data()
        
        # 测试操作符优先级
        result = self.calculation_engine._evaluate_expression(
            ["10", "+", "5", "*", "2"], {}
        )
        
        self.assertEqual(result, 20)  # 10 + (5 * 2) = 20

    def test_evaluate_expression_invalid_operator(self):
        """测试无效操作符"""
        # 先加载数据
        self.calculation_engine.load_calc_data()
        
        # 测试无效操作符
        result = self.calculation_engine._evaluate_expression(
            ["10", "invalid", "5"], {}
        )
        
        # 无效操作符应该返回0
        self.assertEqual(result, 0)

    def test_evaluate_expression_missing_operand(self):
        """测试缺失操作数"""
        # 先加载数据
        self.calculation_engine.load_calc_data()
        
        # 测试缺失操作数
        result = self.calculation_engine._evaluate_expression(
            ["10", "+"], {}
        )
        
        # 缺失操作数应该返回0
        self.assertEqual(result, 0)

    def test_parse_expression_tokens(self):
        """测试解析表达式标记"""
        # 先加载数据
        self.calculation_engine.load_calc_data()
        
        # 测试解析简单表达式
        tokens = self.calculation_engine._parse_expression_tokens("10 + 5 * 2")
        
        self.assertEqual(tokens, ["10", "+", "5", "*", "2"])

    def test_parse_expression_tokens_with_parentheses(self):
        """测试解析带括号的表达式标记"""
        # 先加载数据
        self.calculation_engine.load_calc_data()
        
        # 测试解析带括号的表达式
        tokens = self.calculation_engine._parse_expression_tokens("(10 + 5) * 2")
        
        self.assertEqual(tokens, ["(", "10", "+", "5", ")", "*", "2"])

    def test_parse_expression_tokens_with_parameters(self):
        """测试解析带参数的表达式标记"""
        # 先加载数据
        self.calculation_engine.load_calc_data()
        
        # 测试解析带参数的表达式
        tokens = self.calculation_engine._parse_expression_tokens("#500 + #501 * 2")
        
        self.assertEqual(tokens, ["#500", "+", "#501", "*", "2"])

    def test_get_parameter_value(self):
        """测试获取参数值"""
        # 先加载数据
        self.calculation_engine.load_calc_data()
        
        # 测试获取存在的参数值
        parameters = {'#500': 10, '#501': 5}
        value = self.calculation_engine._get_parameter_value("#500", parameters)
        
        self.assertEqual(value, 10)

    def test_get_parameter_value_missing(self):
        """测试获取缺失的参数值"""
        # 先加载数据
        self.calculation_engine.load_calc_data()
        
        # 测试获取不存在的参数值
        parameters = {'#500': 10}
        value = self.calculation_engine._get_parameter_value("#501", parameters)
        
        # 不存在的参数应该返回0
        self.assertEqual(value, 0)

    def test_get_parameter_value_numeric(self):
        """测试获取数值参数值"""
        # 先加载数据
        self.calculation_engine.load_calc_data()
        
        # 测试获取数值
        value = self.calculation_engine._get_parameter_value("10", {})
        
        self.assertEqual(value, 10)

    def test_get_parameter_value_float(self):
        """测试获取浮点数参数值"""
        # 先加载数据
        self.calculation_engine.load_calc_data()
        
        # 测试获取浮点数
        value = self.calculation_engine._get_parameter_value("10.5", {})
        
        self.assertEqual(value, 10.5)

    def test_get_parameter_value_invalid(self):
        """测试获取无效参数值"""
        # 先加载数据
        self.calculation_engine.load_calc_data()
        
        # 测试获取无效值
        value = self.calculation_engine._get_parameter_value("invalid", {})
        
        # 无效值应该返回0
        self.assertEqual(value, 0)

    def test_apply_operator(self):
        """测试应用操作符"""
        # 先加载数据
        self.calculation_engine.load_calc_data()
        
        # 测试加法
        result = self.calculation_engine._apply_operator(10, 5, "+")
        self.assertEqual(result, 15)
        
        # 测试减法
        result = self.calculation_engine._apply_operator(10, 5, "-")
        self.assertEqual(result, 5)
        
        # 测试乘法
        result = self.calculation_engine._apply_operator(10, 5, "*")
        self.assertEqual(result, 50)
        
        # 测试除法
        result = self.calculation_engine._apply_operator(10, 5, "/")
        self.assertEqual(result, 2)
        
        # 测试无效操作符
        result = self.calculation_engine._apply_operator(10, 5, "invalid")
        self.assertEqual(result, 0)

    def test_apply_operator_division_by_zero(self):
        """测试除零操作符"""
        # 先加载数据
        self.calculation_engine.load_calc_data()
        
        # 测试除零
        result = self.calculation_engine._apply_operator(10, 0, "/")
        
        # 除零应该返回0
        self.assertEqual(result, 0)

    def test_batch_calculate(self):
        """测试批量计算"""
        # 先加载数据
        self.calculation_engine.load_calc_data()
        
        # 测试批量计算
        defines = ["calc2", "calc3", "calc4"]
        parameters = {'#500': 10, '#501': 10, '#502': 10}
        
        results = self.calculation_engine.batch_calculate(defines, parameters)
        
        self.assertEqual(len(results), 3)
        self.assertEqual(results["calc2"], 20)  # 10 * 2
        self.assertEqual(results["calc3"], 5)   # 10 / 2
        self.assertEqual(results["calc4"], 9)   # 10 - 1

    def test_batch_calculate_data_not_loaded(self):
        """测试批量计算数据未加载"""
        # 不加载数据，直接批量计算
        defines = ["calc2", "calc3"]
        parameters = {'#500': 10}
        
        results = self.calculation_engine.batch_calculate(defines, parameters)
        
        # 数据未加载应该返回空字典
        self.assertEqual(len(results), 0)

    def test_clear_cache(self):
        """测试清理缓存"""
        # 先加载数据
        self.calculation_engine.load_calc_data()
        self.assertIsNotNone(self.calculation_engine.calc_data)
        
        # 清理缓存
        self.calculation_engine.clear_cache()
        
        self.assertIsNone(self.calculation_engine.calc_data)

    def test_get_calculation_defines(self):
        """测试获取计算定义"""
        # 先加载数据
        self.calculation_engine.load_calc_data()
        
        defines = self.calculation_engine.get_calculation_defines()
        
        self.assertIsInstance(defines, list)
        self.assertGreater(len(defines), 0)
        self.assertIn("calc1", defines)
        self.assertIn("calc2", defines)

    def test_get_calculation_defines_data_not_loaded(self):
        """测试获取计算定义数据未加载"""
        # 不加载数据，直接获取定义
        defines = self.calculation_engine.get_calculation_defines()
        
        self.assertEqual(len(defines), 0)

    def test_validate_calculation_data(self):
        """测试验证计算数据"""
        # 先加载数据
        self.calculation_engine.load_calc_data()
        
        result = self.calculation_engine.validate_calculation_data()
        
        self.assertTrue(result["valid"])
        self.assertEqual(len(result["errors"]), 0)

    def test_validate_calculation_data_invalid(self):
        """测试验证无效计算数据"""
        # 先加载数据
        self.calculation_engine.load_calc_data()
        
        # 添加无效数据
        self.calculation_engine.calc_data["invalid"] = ["="]
        
        result = self.calculation_engine.validate_calculation_data()
        
        self.assertFalse(result["valid"])
        self.assertGreater(len(result["errors"]), 0)


if __name__ == '__main__':
    unittest.main()
