"""
关系验证器单元测试
测试关系验证器的各种功能
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os
import pandas as pd

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.business.relation_validator import RelationValidator
from src.core.config import ConfigManager
from src.data.csv_processor import CSVProcessor


class TestRelationValidator(unittest.TestCase):
    """关系验证器测试类"""

    def setUp(self):
        """测试前准备"""
        # 创建模拟对象
        self.mock_config_manager = Mock(spec=ConfigManager)
        self.mock_csv_processor = Mock(spec=CSVProcessor)
        
        # 设置模拟返回值
        self.mock_config_manager.get_value.return_value = "config/csv/relation.csv"
        
        # 模拟关系数据
        self.mock_relation_data = pd.DataFrame({
            'PROGRAM_NO': [1, 1, 2, 2],
            'PARAM1': ['#500', '#501', '#502', '#503'],
            'PARAM2': ['#501', '#502', '#503', '#504'],
            'OPERATOR': ['==', '>', '<', '>='],
            'EXPECTED_VALUE': [None, None, None, None],
            'ERROR_MESSAGE': [
                '参数#500和#501必须相等',
                '参数#501必须大于#502',
                '参数#502必须小于#503',
                '参数#503必须大于等于#504'
            ]
        })
        
        self.mock_csv_processor.load_csv_to_dataframe.return_value = self.mock_relation_data
        
        # 创建关系验证器实例
        self.relation_validator = RelationValidator(
            self.mock_config_manager, 
            self.mock_csv_processor
        )

    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.relation_validator)
        self.assertEqual(self.relation_validator.config_manager, self.mock_config_manager)
        self.assertEqual(self.relation_validator.csv_processor, self.mock_csv_processor)
        self.assertIsNone(self.relation_validator.relation_data)

    def test_load_relation_data_success(self):
        """测试成功加载关系数据"""
        result = self.relation_validator.load_relation_data()
        
        self.assertTrue(result)
        self.assertIsNotNone(self.relation_validator.relation_data)
        self.mock_csv_processor.load_csv_to_dataframe.assert_called_once()

    def test_load_relation_data_failure(self):
        """测试加载关系数据失败"""
        # 模拟加载失败
        self.mock_csv_processor.load_csv_to_dataframe.side_effect = Exception("加载失败")
        
        result = self.relation_validator.load_relation_data()
        
        self.assertFalse(result)
        self.assertIsNone(self.relation_validator.relation_data)

    def test_validate_relations_success(self):
        """测试成功验证关系"""
        # 先加载数据
        self.relation_validator.load_relation_data()
        
        # 测试参数验证
        parameters = {
            '#500': 10,
            '#501': 10,
            '#502': 5,
            '#503': 8,
            '#504': 8
        }
        
        result = self.relation_validator.validate_relations(1, parameters)
        
        self.assertTrue(result["valid"])
        self.assertEqual(len(result["errors"]), 0)
        self.assertEqual(len(result["warnings"]), 0)

    def test_validate_relations_with_errors(self):
        """测试验证关系有错误"""
        # 先加载数据
        self.relation_validator.load_relation_data()
        
        # 测试参数验证失败
        parameters = {
            '#500': 10,
            '#501': 20,  # 不相等
            '#502': 15,  # 不大于
            '#503': 5,   # 不小于
            '#504': 10   # 不大于等于
        }
        
        result = self.relation_validator.validate_relations(1, parameters)
        
        self.assertFalse(result["valid"])
        self.assertGreater(len(result["errors"]), 0)

    def test_validate_relations_missing_parameters(self):
        """测试验证关系参数缺失"""
        # 先加载数据
        self.relation_validator.load_relation_data()
        
        # 测试参数缺失
        parameters = {
            '#500': 10,
            # '#501' 缺失
            '#502': 5
        }
        
        result = self.relation_validator.validate_relations(1, parameters)
        
        # 参数缺失应该产生警告而不是错误
        self.assertTrue(result["valid"])
        self.assertGreater(len(result["warnings"]), 0)

    def test_validate_relations_data_not_loaded(self):
        """测试验证关系数据未加载"""
        # 不加载数据，直接验证
        parameters = {'#500': 10, '#501': 10}
        
        result = self.relation_validator.validate_relations(1, parameters)
        
        self.assertFalse(result["valid"])
        self.assertIn("关系数据加载失败", result["errors"][0])

    def test_validate_single_rule(self):
        """测试验证单个规则"""
        # 先加载数据
        self.relation_validator.load_relation_data()
        
        # 获取第一条规则
        rule = self.mock_relation_data.iloc[0].to_dict()
        
        # 测试相等规则
        parameters = {'#500': 10, '#501': 10}
        result = self.relation_validator._validate_single_rule(rule, parameters)
        
        self.assertTrue(result["valid"])
        self.assertEqual(len(result["errors"]), 0)

    def test_validate_single_rule_failure(self):
        """测试验证单个规则失败"""
        # 先加载数据
        self.relation_validator.load_relation_data()
        
        # 获取第一条规则
        rule = self.mock_relation_data.iloc[0].to_dict()
        
        # 测试不相等
        parameters = {'#500': 10, '#501': 20}
        result = self.relation_validator._validate_single_rule(rule, parameters)
        
        self.assertFalse(result["valid"])
        self.assertGreater(len(result["errors"]), 0)

    def test_validate_single_rule_missing_parameters(self):
        """测试验证单个规则参数缺失"""
        # 先加载数据
        self.relation_validator.load_relation_data()
        
        # 获取第一条规则
        rule = self.mock_relation_data.iloc[0].to_dict()
        
        # 测试参数缺失
        parameters = {'#500': 10}  # '#501' 缺失
        result = self.relation_validator._validate_single_rule(rule, parameters)
        
        self.assertTrue(result["valid"])  # 参数缺失不视为错误
        self.assertGreater(len(result["warnings"]), 0)

    def test_compare_values(self):
        """测试比较值"""
        # 测试相等
        self.assertTrue(self.relation_validator._compare_values(10, 10, '==', None))
        
        # 测试不相等
        self.assertTrue(self.relation_validator._compare_values(10, 20, '!=', None))
        
        # 测试大于
        self.assertTrue(self.relation_validator._compare_values(20, 10, '>', None))
        
        # 测试小于
        self.assertTrue(self.relation_validator._compare_values(10, 20, '<', None))
        
        # 测试大于等于
        self.assertTrue(self.relation_validator._compare_values(10, 10, '>=', None))
        
        # 测试小于等于
        self.assertTrue(self.relation_validator._compare_values(10, 10, '<=', None))

    def test_compare_values_string(self):
        """测试比较字符串值"""
        # 测试字符串相等
        self.assertTrue(self.relation_validator._compare_values("ABC", "ABC", '==', None))
        
        # 测试字符串不相等
        self.assertTrue(self.relation_validator._compare_values("ABC", "XYZ", '!=', None))

    def test_compare_values_unsupported_operator(self):
        """测试不支持的操作符"""
        # 测试不支持的操作符
        result = self.relation_validator._compare_values(10, 10, 'unsupported', None)
        
        # 不支持的操作符应该返回True（不产生错误）
        self.assertTrue(result)

    def test_get_relation_rules(self):
        """测试获取关系规则"""
        # 先加载数据
        self.relation_validator.load_relation_data()
        
        # 获取程序1的规则
        rules = self.relation_validator.get_relation_rules(1)
        
        self.assertIsInstance(rules, list)
        self.assertEqual(len(rules), 2)  # 程序1有2条规则
        
        # 验证规则内容
        for rule in rules:
            self.assertIn('PARAM1', rule)
            self.assertIn('PARAM2', rule)
            self.assertIn('OPERATOR', rule)

    def test_get_relation_rules_data_not_loaded(self):
        """测试获取关系规则数据未加载"""
        # 不加载数据，直接获取规则
        rules = self.relation_validator.get_relation_rules(1)
        
        self.assertEqual(len(rules), 0)

    def test_get_relation_rules_program_not_found(self):
        """测试获取不存在的程序的关系规则"""
        # 先加载数据
        self.relation_validator.load_relation_data()
        
        # 获取不存在的程序的规则
        rules = self.relation_validator.get_relation_rules(999)
        
        self.assertEqual(len(rules), 0)

    def test_clear_cache(self):
        """测试清理缓存"""
        # 先加载数据
        self.relation_validator.load_relation_data()
        self.assertIsNotNone(self.relation_validator.relation_data)
        
        # 清理缓存
        self.relation_validator.clear_cache()
        
        self.assertIsNone(self.relation_validator.relation_data)

    def test_validate_relations_numeric_comparison(self):
        """测试数值比较"""
        # 先加载数据
        self.relation_validator.load_relation_data()
        
        # 测试数值比较
        parameters = {
            '#500': '10',  # 字符串数值
            '#501': 10,    # 整数数值
            '#502': '5.5', # 字符串浮点数
            '#503': 5.5    # 浮点数
        }
        
        result = self.relation_validator.validate_relations(1, parameters)
        
        # 数值比较应该成功
        self.assertTrue(result["valid"])

    def test_validate_relations_string_comparison(self):
        """测试字符串比较"""
        # 先加载数据
        self.relation_validator.load_relation_data()
        
        # 测试字符串比较
        parameters = {
            '#500': 'ABC',
            '#501': 'ABC',
            '#502': 'XYZ',
            '#503': 'XYZ'
        }
        
        result = self.relation_validator.validate_relations(1, parameters)
        
        # 字符串比较应该成功
        self.assertTrue(result["valid"])

    def test_validate_relations_mixed_types(self):
        """测试混合类型比较"""
        # 先加载数据
        self.relation_validator.load_relation_data()
        
        # 测试混合类型比较
        parameters = {
            '#500': '10',  # 字符串
            '#501': 10,    # 整数
            '#502': '5.5', # 字符串
            '#503': 5.5    # 浮点数
        }
        
        result = self.relation_validator.validate_relations(1, parameters)
        
        # 混合类型比较应该成功（系统会尝试转换）
        self.assertTrue(result["valid"])

    def test_validate_relations_exception_handling(self):
        """测试异常处理"""
        # 先加载数据
        self.relation_validator.load_relation_data()
        
        # 测试异常情况（例如无效的比较）
        parameters = {
            '#500': 'invalid',
            '#501': 'values',
            '#502': 'that',
            '#503': 'cannot'
        }
        
        result = self.relation_validator.validate_relations(1, parameters)
        
        # 即使有异常，也应该返回结果而不是崩溃
        self.assertIsNotNone(result)
        self.assertIn("valid", result)


if __name__ == '__main__':
    unittest.main()
