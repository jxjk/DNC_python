"""
DNC参数计算系统 - 计算引擎单元测试
"""

import pytest
import math
from src.utils.calculation import CalculationEngine


class TestCalculationEngine:
    """计算引擎测试"""
    
    def test_calculation_engine_creation(self):
        """测试计算引擎创建"""
        engine = CalculationEngine()
        assert engine is not None
        assert hasattr(engine, 'formulas')
    
    def test_evaluate_formula_simple(self):
        """测试简单公式计算"""
        engine = CalculationEngine()
        
        # 测试基本算术运算
        result = engine.evaluate_formula("2 + 3", {})
        assert result == 5.0
        
        result = engine.evaluate_formula("10 - 4", {})
        assert result == 6.0
        
        result = engine.evaluate_formula("3 * 4", {})
        assert result == 12.0
        
        result = engine.evaluate_formula("15 / 3", {})
        assert result == 5.0
    
    def test_evaluate_formula_with_variables(self):
        """测试带变量的公式计算"""
        engine = CalculationEngine()
        
        variables = {
            "length": 100.0,
            "width": 50.0,
            "height": 25.0
        }
        
        result = engine.evaluate_formula("length * width", variables)
        assert result == 5000.0
        
        result = engine.evaluate_formula("length * width * height", variables)
        assert result == 125000.0
        
        result = engine.evaluate_formula("(length + width) * 2", variables)
        assert result == 300.0
    
    def test_evaluate_formula_complex(self):
        """测试复杂公式计算"""
        engine = CalculationEngine()
        
        variables = {
            "radius": 10.0,
            "pi": math.pi
        }
        
        # 圆面积计算
        result = engine.evaluate_formula("pi * radius * radius", variables)
        expected = math.pi * 10.0 * 10.0
        assert abs(result - expected) < 0.001
        
        # 带括号的复杂表达式
        result = engine.evaluate_formula("(radius * 2) + (radius / 2)", variables)
        assert result == 25.0
    
    def test_evaluate_formula_invalid_expression(self):
        """测试无效表达式"""
        engine = CalculationEngine()
        
        # 测试语法错误
        result = engine.evaluate_formula("length * ", {"length": 10.0})
        assert result is None
        
        # 测试未定义变量
        result = engine.evaluate_formula("undefined_var * 2", {})
        assert result is None
        
        # 测试除零错误
        result = engine.evaluate_formula("10 / 0", {})
        assert result is None
    
    def test_calculate_geometry_volume(self):
        """测试几何体积计算"""
        engine = CalculationEngine()
        
        # 长方体体积计算
        parameters = {
            "length": 100.0,
            "width": 50.0,
            "height": 25.0
        }
        
        result = engine.calculate_geometry("volume", parameters)
        assert result is not None
        assert result == 125000.0
        
        # 圆柱体体积计算
        parameters = {
            "radius": 10.0,
            "height": 20.0
        }
        
        result = engine.calculate_geometry("volume", parameters)
        assert result is not None
        expected = math.pi * 10.0 * 10.0 * 20.0
        assert abs(result - expected) < 0.001
    
    def test_calculate_geometry_surface_area(self):
        """测试几何表面积计算"""
        engine = CalculationEngine()
        
        # 长方体表面积计算
        parameters = {
            "length": 100.0,
            "width": 50.0,
            "height": 25.0
        }
        
        result = engine.calculate_geometry("surface_area", parameters)
        assert result is not None
        expected = 2 * (100*50 + 100*25 + 50*25)
        assert result == expected
        
        # 球体表面积计算
        parameters = {
            "radius": 10.0
        }
        
        result = engine.calculate_geometry("surface_area", parameters)
        assert result is not None
        expected = 4 * math.pi * 10.0 * 10.0
        assert abs(result - expected) < 0.001
    
    def test_calculate_geometry_weight(self):
        """测试重量计算"""
        engine = CalculationEngine()
        
        parameters = {
            "volume": 1000.0,
            "density": 2.5
        }
        
        result = engine.calculate_geometry("weight", parameters)
        assert result is not None
        assert result == 2500.0
        
        # 测试默认密度
        parameters = {
            "volume": 1000.0
        }
        
        result = engine.calculate_geometry("weight", parameters)
        assert result is not None
        assert result == 1000.0  # 默认密度为1.0
    
    def test_calculate_geometry_unknown_type(self):
        """测试未知几何类型计算"""
        engine = CalculationEngine()
        
        parameters = {
            "length": 100.0,
            "width": 50.0
        }
        
        result = engine.calculate_geometry("unknown_type", parameters)
        assert result is None
    
    def test_calculate_geometry_missing_parameters(self):
        """测试缺少参数的计算"""
        engine = CalculationEngine()
        
        # 缺少必需参数
        parameters = {
            "length": 100.0
            # 缺少width和height
        }
        
        result = engine.calculate_geometry("volume", parameters)
        assert result is None
    
    def test_validate_calculation_success(self):
        """测试成功验证计算"""
        engine = CalculationEngine()
        
        input_params = {
            "length": 100.0,
            "width": 50.0,
            "height": 25.0
        }
        
        calculated_params = {
            "volume": 125000.0,
            "surface_area": 17500.0
        }
        
        is_valid = engine.validate_calculation(input_params, calculated_params)
        assert is_valid is True
    
    def test_validate_calculation_invalid_volume(self):
        """测试验证无效体积计算"""
        engine = CalculationEngine()
        
        input_params = {
            "length": 100.0,
            "width": 50.0,
            "height": 25.0
        }
        
        # 错误的体积值
        calculated_params = {
            "volume": 100000.0,  # 应该是125000.0
            "surface_area": 17500.0
        }
        
        is_valid = engine.validate_calculation(input_params, calculated_params)
        assert is_valid is False
    
    def test_validate_calculation_missing_calculated_params(self):
        """测试验证缺少计算参数"""
        engine = CalculationEngine()
        
        input_params = {
            "length": 100.0,
            "width": 50.0,
            "height": 25.0
        }
        
        # 缺少必要的计算参数
        calculated_params = {
            "volume": 125000.0
            # 缺少surface_area
        }
        
        is_valid = engine.validate_calculation(input_params, calculated_params)
        assert is_valid is False
    
    def test_validate_calculation_negative_values(self):
        """测试验证负值计算"""
        engine = CalculationEngine()
        
        input_params = {
            "length": 100.0,
            "width": 50.0,
            "height": 25.0
        }
        
        # 负的计算值
        calculated_params = {
            "volume": -125000.0,  # 负体积
            "surface_area": 17500.0
        }
        
        is_valid = engine.validate_calculation(input_params, calculated_params)
        assert is_valid is False
    
    def test_calculate_geometry_with_precision(self):
        """测试带精度的几何计算"""
        engine = CalculationEngine()
        
        parameters = {
            "length": 100.123,
            "width": 50.456,
            "height": 25.789
        }
        
        # 测试默认精度
        result = engine.calculate_geometry("volume", parameters)
        assert result is not None
        
        # 验证结果精度
        expected = 100.123 * 50.456 * 25.789
        assert abs(result - expected) < 0.001
    
    def test_calculate_geometry_edge_cases(self):
        """测试边界情况计算"""
        engine = CalculationEngine()
        
        # 测试零值
        parameters = {
            "length": 0.0,
            "width": 50.0,
            "height": 25.0
        }
        
        result = engine.calculate_geometry("volume", parameters)
        assert result == 0.0
        
        # 测试极小值
        parameters = {
            "length": 0.001,
            "width": 0.001,
            "height": 0.001
        }
        
        result = engine.calculate_geometry("volume", parameters)
        assert result is not None
        assert result > 0.0
    
    def test_calculate_geometry_complex_shapes(self):
        """测试复杂几何形状计算"""
        engine = CalculationEngine()
        
        # 测试圆锥体积
        parameters = {
            "radius": 10.0,
            "height": 30.0
        }
        
        result = engine.calculate_geometry("volume", parameters)
        assert result is not None
        expected = (1/3) * math.pi * 10.0 * 10.0 * 30.0
        assert abs(result - expected) < 0.001
        
        # 测试圆环体积
        parameters = {
            "outer_radius": 15.0,
            "inner_radius": 10.0,
            "height": 5.0
        }
        
        result = engine.calculate_geometry("volume", parameters)
        assert result is not None
        expected = math.pi * (15.0*15.0 - 10.0*10.0) * 5.0
        assert abs(result - expected) < 0.001


if __name__ == "__main__":
    pytest.main([__file__])
