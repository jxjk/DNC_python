"""
程序匹配器单元测试
测试程序匹配器的各种功能
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.business.program_matcher import ProgramMatcher
from src.core.config import ConfigManager
from src.data.csv_processor import CSVProcessor


class TestProgramMatcher(unittest.TestCase):
    """程序匹配器测试类"""

    def setUp(self):
        """测试前准备"""
        # 创建模拟对象
        self.mock_config_manager = Mock(spec=ConfigManager)
        self.mock_csv_processor = Mock(spec=CSVProcessor)
        
        # 设置模拟返回值
        self.mock_config_manager.get_csv_config_path.return_value = "test_path.csv"
        
        # 模拟程序数据
        self.mock_program_data = [
            ["MODEL", "PROGRAM", "PARAMETERS"],
            ["MODEL001", "O0001", "P1=10,P2=20"],
            ["MODEL002", "O0002", "P1=15,P2=25"],
            ["MODEL003", "O0003", "P1=20,P2=30"],
            ["MODEL004", "O0004", "P1=25,P2=35"]
        ]
        
        self.mock_csv_processor.read_csv.return_value = self.mock_program_data
        
        # 创建程序匹配器实例
        self.program_matcher = ProgramMatcher(
            self.mock_config_manager, 
            self.mock_csv_processor
        )

    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.program_matcher)
        self.assertEqual(self.program_matcher.config_manager, self.mock_config_manager)
        self.assertEqual(self.program_matcher.csv_processor, self.mock_csv_processor)
        self.assertIsNone(self.program_matcher.program_data)

    def test_load_program_data_success(self):
        """测试成功加载程序数据"""
        result = self.program_matcher.load_program_data()
        
        self.assertTrue(result)
        self.assertIsNotNone(self.program_matcher.program_data)
        self.mock_csv_processor.read_csv.assert_called_once()

    def test_load_program_data_failure(self):
        """测试加载程序数据失败"""
        # 模拟加载失败
        self.mock_csv_processor.read_csv.side_effect = Exception("加载失败")
        
        result = self.program_matcher.load_program_data()
        
        self.assertFalse(result)
        self.assertIsNone(self.program_matcher.program_data)

    def test_match_program_exact_match(self):
        """测试精确匹配程序"""
        # 先加载数据
        self.program_matcher.load_program_data()
        
        # 测试精确匹配
        model = "MODEL001"
        result = self.program_matcher.match_program(model)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["program"], "O0001")
        self.assertEqual(result["parameters"], "P1=10,P2=20")

    def test_match_program_case_insensitive(self):
        """测试不区分大小写匹配"""
        # 先加载数据
        self.program_matcher.load_program_data()
        
        # 测试不区分大小写匹配
        model = "model001"  # 小写
        result = self.program_matcher.match_program(model)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["program"], "O0001")

    def test_match_program_partial_match(self):
        """测试部分匹配"""
        # 先加载数据
        self.program_matcher.load_program_data()
        
        # 测试部分匹配
        model = "MODEL00"  # 部分匹配
        result = self.program_matcher.match_program(model)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["program"], "O0001")

    def test_match_program_no_match(self):
        """测试无匹配"""
        # 先加载数据
        self.program_matcher.load_program_data()
        
        # 测试无匹配
        model = "UNKNOWN_MODEL"
        result = self.program_matcher.match_program(model)
        
        self.assertFalse(result["success"])
        self.assertIn("未找到匹配的程序", result["error_message"])

    def test_match_program_data_not_loaded(self):
        """测试匹配程序数据未加载"""
        # 不加载数据，直接匹配
        model = "MODEL001"
        result = self.program_matcher.match_program(model)
        
        self.assertFalse(result["success"])
        self.assertIn("程序数据未加载", result["error_message"])

    def test_match_program_empty_model(self):
        """测试匹配空模型"""
        # 先加载数据
        self.program_matcher.load_program_data()
        
        # 测试空模型
        model = ""
        result = self.program_matcher.match_program(model)
        
        self.assertFalse(result["success"])
        self.assertIn("模型名为空", result["error_message"])

    def test_match_program_none_model(self):
        """测试匹配None模型"""
        # 先加载数据
        self.program_matcher.load_program_data()
        
        # 测试None模型
        model = None
        result = self.program_matcher.match_program(model)
        
        self.assertFalse(result["success"])
        self.assertIn("模型名为空", result["error_message"])

    def test_match_program_with_whitespace(self):
        """测试匹配带空格的模型"""
        # 先加载数据
        self.program_matcher.load_program_data()
        
        # 测试带空格的模型
        model = " MODEL001 "  # 带空格
        result = self.program_matcher.match_program(model)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["program"], "O0001")

    def test_match_program_multiple_matches(self):
        """测试多个匹配"""
        # 先加载数据
        self.program_matcher.load_program_data()
        
        # 添加重复数据
        self.program_matcher.program_data["MODEL001_ALT"] = ["O0005", "P1=30,P2=40"]
        
        # 测试多个匹配
        model = "MODEL001"
        result = self.program_matcher.match_program(model)
        
        self.assertTrue(result["success"])
        # 应该返回第一个匹配
        self.assertEqual(result["program"], "O0001")

    def test_get_program_parameters(self):
        """测试获取程序参数"""
        # 先加载数据
        self.program_matcher.load_program_data()
        
        # 测试获取参数
        parameters = self.program_matcher.get_program_parameters("MODEL001")
        
        self.assertEqual(parameters, "P1=10,P2=20")

    def test_get_program_parameters_no_match(self):
        """测试获取不存在的程序参数"""
        # 先加载数据
        self.program_matcher.load_program_data()
        
        # 测试获取不存在的参数
        parameters = self.program_matcher.get_program_parameters("UNKNOWN")
        
        self.assertEqual(parameters, "")

    def test_get_program_parameters_data_not_loaded(self):
        """测试获取程序参数数据未加载"""
        # 不加载数据，直接获取参数
        parameters = self.program_matcher.get_program_parameters("MODEL001")
        
        self.assertEqual(parameters, "")

    def test_parse_parameters_success(self):
        """测试成功解析参数"""
        # 先加载数据
        self.program_matcher.load_program_data()
        
        # 测试解析参数
        param_string = "P1=10,P2=20,P3=30"
        parameters = self.program_matcher._parse_parameters(param_string)
        
        self.assertEqual(len(parameters), 3)
        self.assertEqual(parameters["P1"], "10")
        self.assertEqual(parameters["P2"], "20")
        self.assertEqual(parameters["P3"], "30")

    def test_parse_parameters_empty(self):
        """测试解析空参数"""
        # 先加载数据
        self.program_matcher.load_program_data()
        
        # 测试解析空参数
        param_string = ""
        parameters = self.program_matcher._parse_parameters(param_string)
        
        self.assertEqual(len(parameters), 0)

    def test_parse_parameters_invalid_format(self):
        """测试解析无效格式参数"""
        # 先加载数据
        self.program_matcher.load_program_data()
        
        # 测试解析无效格式
        param_string = "invalid_format"
        parameters = self.program_matcher._parse_parameters(param_string)
        
        self.assertEqual(len(parameters), 0)

    def test_parse_parameters_partial_invalid(self):
        """测试解析部分无效参数"""
        # 先加载数据
        self.program_matcher.load_program_data()
        
        # 测试解析部分无效
        param_string = "P1=10,invalid,P2=20"
        parameters = self.program_matcher._parse_parameters(param_string)
        
        self.assertEqual(len(parameters), 2)
        self.assertEqual(parameters["P1"], "10")
        self.assertEqual(parameters["P2"], "20")

    def test_get_all_programs(self):
        """测试获取所有程序"""
        # 先加载数据
        self.program_matcher.load_program_data()
        
        programs = self.program_matcher.get_all_programs()
        
        self.assertIsInstance(programs, list)
        self.assertGreater(len(programs), 0)
        self.assertIn("MODEL001", programs)
        self.assertIn("MODEL002", programs)

    def test_get_all_programs_data_not_loaded(self):
        """测试获取所有程序数据未加载"""
        # 不加载数据，直接获取所有程序
        programs = self.program_matcher.get_all_programs()
        
        self.assertEqual(len(programs), 0)

    def test_get_program_count(self):
        """测试获取程序数量"""
        # 先加载数据
        self.program_matcher.load_program_data()
        
        count = self.program_matcher.get_program_count()
        
        self.assertEqual(count, 4)  # 4个程序

    def test_get_program_count_data_not_loaded(self):
        """测试获取程序数量数据未加载"""
        # 不加载数据，直接获取数量
        count = self.program_matcher.get_program_count()
        
        self.assertEqual(count, 0)

    def test_search_programs_by_keyword(self):
        """测试按关键字搜索程序"""
        # 先加载数据
        self.program_matcher.load_program_data()
        
        # 测试搜索
        results = self.program_matcher.search_programs_by_keyword("MODEL00")
        
        self.assertEqual(len(results), 4)  # 所有MODEL00开头的程序

    def test_search_programs_by_keyword_no_match(self):
        """测试按关键字搜索无匹配"""
        # 先加载数据
        self.program_matcher.load_program_data()
        
        # 测试无匹配搜索
        results = self.program_matcher.search_programs_by_keyword("UNKNOWN")
        
        self.assertEqual(len(results), 0)

    def test_search_programs_by_keyword_data_not_loaded(self):
        """测试按关键字搜索数据未加载"""
        # 不加载数据，直接搜索
        results = self.program_matcher.search_programs_by_keyword("MODEL")
        
        self.assertEqual(len(results), 0)

    def test_batch_match_programs(self):
        """测试批量匹配程序"""
        # 先加载数据
        self.program_matcher.load_program_data()
        
        # 测试批量匹配
        models = ["MODEL001", "MODEL002", "MODEL003"]
        results = self.program_matcher.batch_match_programs(models)
        
        self.assertEqual(len(results), 3)
        self.assertTrue(results[0]["success"])
        self.assertTrue(results[1]["success"])
        self.assertTrue(results[2]["success"])

    def test_batch_match_programs_with_errors(self):
        """测试批量匹配程序包含错误"""
        # 先加载数据
        self.program_matcher.load_program_data()
        
        # 测试包含错误的批量匹配
        models = ["MODEL001", "UNKNOWN", "MODEL003"]
        results = self.program_matcher.batch_match_programs(models)
        
        self.assertEqual(len(results), 3)
        self.assertTrue(results[0]["success"])
        self.assertFalse(results[1]["success"])
        self.assertTrue(results[2]["success"])

    def test_batch_match_programs_data_not_loaded(self):
        """测试批量匹配程序数据未加载"""
        # 不加载数据，直接批量匹配
        models = ["MODEL001", "MODEL002"]
        results = self.program_matcher.batch_match_programs(models)
        
        self.assertEqual(len(results), 2)
        self.assertFalse(results[0]["success"])
        self.assertFalse(results[1]["success"])

    def test_validate_program_data(self):
        """测试验证程序数据"""
        # 先加载数据
        self.program_matcher.load_program_data()
        
        result = self.program_matcher.validate_program_data()
        
        self.assertTrue(result["valid"])
        self.assertEqual(len(result["errors"]), 0)

    def test_validate_program_data_invalid(self):
        """测试验证无效程序数据"""
        # 先加载数据
        self.program_matcher.load_program_data()
        
        # 添加无效数据
        self.program_matcher.program_data["INVALID"] = []  # 空数据
        
        result = self.program_matcher.validate_program_data()
        
        self.assertFalse(result["valid"])
        self.assertGreater(len(result["errors"]), 0)

    def test_update_program_mapping(self):
        """测试更新程序映射"""
        # 先加载数据
        self.program_matcher.load_program_data()
        
        # 测试更新映射
        new_mapping = {
            "MODEL005": ["O0005", "P1=50,P2=60"]
        }
        
        result = self.program_matcher.update_program_mapping(new_mapping)
        
        self.assertTrue(result)
        # 验证新映射已添加
        match_result = self.program_matcher.match_program("MODEL005")
        self.assertTrue(match_result["success"])
        self.assertEqual(match_result["program"], "O0005")

    def test_update_program_mapping_data_not_loaded(self):
        """测试更新程序映射数据未加载"""
        # 不加载数据，直接更新映射
        new_mapping = {
            "MODEL005": ["O0005", "P1=50,P2=60"]
        }
        
        result = self.program_matcher.update_program_mapping(new_mapping)
        
        self.assertFalse(result)

    def test_remove_program_mapping(self):
        """测试删除程序映射"""
        # 先加载数据
        self.program_matcher.load_program_data()
        
        # 测试删除映射
        result = self.program_matcher.remove_program_mapping("MODEL001")
        
        self.assertTrue(result)
        # 验证映射已删除
        match_result = self.program_matcher.match_program("MODEL001")
        self.assertFalse(match_result["success"])

    def test_remove_program_mapping_not_exists(self):
        """测试删除不存在的程序映射"""
        # 先加载数据
        self.program_matcher.load_program_data()
        
        # 测试删除不存在的映射
        result = self.program_matcher.remove_program_mapping("UNKNOWN")
        
        self.assertFalse(result)

    def test_remove_program_mapping_data_not_loaded(self):
        """测试删除程序映射数据未加载"""
        # 不加载数据，直接删除映射
        result = self.program_matcher.remove_program_mapping("MODEL001")
        
        self.assertFalse(result)

    def test_clear_cache(self):
        """测试清理缓存"""
        # 先加载数据
        self.program_matcher.load_program_data()
        self.assertIsNotNone(self.program_matcher.program_data)
        
        # 清理缓存
        self.program_matcher.clear_cache()
        
        self.assertIsNone(self.program_matcher.program_data)

    def test_get_matching_statistics(self):
        """测试获取匹配统计信息"""
        # 先加载数据
        self.program_matcher.load_program_data()
        
        # 执行一些匹配操作
        self.program_matcher.match_program("MODEL001")
        self.program_matcher.match_program("MODEL002")
        self.program_matcher.match_program("UNKNOWN")
        
        stats = self.program_matcher.get_matching_statistics()
        
        self.assertIn("total_attempts", stats)
        self.assertIn("successful_matches", stats)
        self.assertIn("failed_matches", stats)
        self.assertIn("success_rate", stats)

    def test_reset_statistics(self):
        """测试重置统计信息"""
        # 先加载数据
        self.program_matcher.load_program_data()
        
        # 执行一些匹配操作
        self.program_matcher.match_program("MODEL001")
        
        # 重置统计
        self.program_matcher.reset_statistics()
        
        stats = self.program_matcher.get_matching_statistics()
        
        self.assertEqual(stats["total_attempts"], 0)
        self.assertEqual(stats["successful_matches"], 0)
        self.assertEqual(stats["failed_matches"], 0)

    def test_export_program_mappings(self):
        """测试导出程序映射"""
        # 先加载数据
        self.program_matcher.load_program_data()
        
        mappings = self.program_matcher.export_program_mappings()
        
        self.assertIsInstance(mappings, dict)
        self.assertGreater(len(mappings), 0)
        self.assertIn("MODEL001", mappings)
        self.assertIn("MODEL002", mappings)

    def test_export_program_mappings_data_not_loaded(self):
        """测试导出程序映射数据未加载"""
        # 不加载数据，直接导出映射
        mappings = self.program_matcher.export_program_mappings()
        
        self.assertEqual(len(mappings), 0)

    def test_import_program_mappings(self):
        """测试导入程序映射"""
        # 先加载数据
        self.program_matcher.load_program_data
