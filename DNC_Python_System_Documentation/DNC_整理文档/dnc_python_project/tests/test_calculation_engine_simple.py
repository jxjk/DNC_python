"""
计算引擎简化测试
只测试核心功能，避免复杂依赖
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

from src.business.calculation_engine import (
    CalculationEngine, 
    CalculationResult
)


class TestCalculationEngineSimple:
    """计算引擎简化测试类"""
    
    def test_calculate_parameters_success(self, calculation_engine):
        """测试成功计算参数"""
        calculation_engine.calc_data = [
            ["1", "10", "20", "30"]
        ]
        
        parameters = {"param1": 5, "param2": 10}
        result = calculation_engine.calculate_parameters(1, parameters)
        
        assert result.program_no == 1
        assert result.success is True
        assert result.parameters is not None
        assert result.error_message is None
    
    def test_calculate_parameters_no_match(self, calculation_engine):
        """测试无程序匹配计算"""
        calculation_engine.calc_data = [
            ["1", "10", "20", "30"]
        ]
        
        parameters = {"param1": 5, "param2": 10}
        result = calculation_engine.calculate_parameters(999, parameters)
        
        assert result.program_no == 999
        assert result.success is True  # 根据实际代码，无匹配程序不会导致计算失败
        assert result.parameters is not None  # 会有一些默认参数
    
    def test_calculate_parameters_no_data(self, calculation_engine):
        """测试无数据计算"""
        calculation_engine.calc_data = None
        
        parameters = {"param1": 5, "param2": 10}
        result = calculation_engine.calculate_parameters(1, parameters)
        
        assert result.program_no == 1
        assert result.success is True  # 根据实际代码，无数据不会导致计算失败
    
    def test_batch_calculate_simple(self, calculation_engine):
        """测试简单批量计算"""
        calculation_engine.calc_data = [
            ["1", "10", "20", "30"],
            ["2", "15", "25", "35"]
        ]
        
        calculations = [
            (1, {"param1": 5, "param2": 10}),
            (2, {"param1": 8, "param2": 12})
        ]
        
        results = calculation_engine.batch_calculate(calculations)
        
        assert len(results) == 2
        assert results[0].success is True
        assert results[1].success is True
    
    def test_get_calculation_statistics_simple(self, calculation_engine):
        """测试简单统计信息"""
        results = [
            CalculationResult(1, {"param1": 10}, [], True),
            CalculationResult(2, {"param2": 20}, [], True),
            CalculationResult(3, {}, [], False, "错误")
        ]
        
        stats = calculation_engine.get_calculation_statistics(results)
        
        assert stats["total"] == 3
        assert stats["successful"] == 2
        assert stats["failed"] == 1
        assert stats["success_rate"] == pytest.approx(66.67, 0.01)
    
    def test_reload_calculation_data_success(self, calculation_engine):
        """测试重新加载数据成功"""
        with patch.object(calculation_engine, '_load_calculation_data') as mock_load:
            result = calculation_engine.reload_calculation_data()
            
            assert result is True
            mock_load.assert_called_once()
    
    def test_reload_calculation_data_failure(self, calculation_engine):
        """测试重新加载数据失败"""
        with patch.object(calculation_engine, '_load_calculation_data') as mock_load:
            mock_load.side_effect = Exception("加载失败")
            
            result = calculation_engine.reload_calculation_data()
            
            assert result is False
            mock_load.assert_called_once()


@pytest.mark.parametrize("program_no,expected_success", [
    (1, True),
    (2, True),
    (999, True),  # 根据实际代码，无匹配程序不会导致计算失败
])
def test_calculate_parameters_parametrized(program_no, expected_success, calculation_engine):
    """参数化测试计算参数"""
    calculation_engine.calc_data = [
        ["1", "10", "20", "30"],
        ["2", "15", "25", "35"]
    ]
    
    parameters = {"param1": 5, "param2": 10}
    result = calculation_engine.calculate_parameters(program_no, parameters)
    
    if expected_success:
        assert result.success is True
        assert result.parameters is not None
        assert result.error_message is None
