"""
模型识别器单元测试
测试模型识别器的各种功能
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.business.model_recognizer import ModelRecognizer
from src.core.config import ConfigManager
from src.data.csv_processor import CSVProcessor


class TestModelRecognizer(unittest.TestCase):
    """模型识别器测试类"""

    def setUp(self):
        """测试前准备"""
        # 创建模拟对象
        self.mock_config_manager = Mock(spec=ConfigManager)
        self.mock_csv_processor = Mock(spec=CSVProcessor)
        
        # 设置模拟返回值
        self.mock_config_manager.get_csv_config_path.return_value = "test_path.csv"
        
        # 模拟QR码配置
        self.mock_qr_config = Mock()
        self.mock_qr_config.qr_mode = 1
        self.mock_qr_config.qr_split_str = "@"
        self.mock_qr_config.model_place = 2
        self.mock_qr_config.po_place = 1
        self.mock_qr_config.qty_place = 3
        self.mock_qr_config.barcode_header_str_num = 11
        
        self.mock_config_manager.qr_config = self.mock_qr_config
        
        # 创建模型识别器实例
        self.model_recognizer = ModelRecognizer(
            self.mock_config_manager, 
            self.mock_csv_processor
        )

    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.model_recognizer)
        self.assertEqual(self.model_recognizer.config_manager, self.mock_config_manager)
        self.assertEqual(self.model_recognizer.csv_processor, self.mock_csv_processor)
        self.assertEqual(self.model_recognizer.qr_split_str, "@")
        self.assertEqual(self.model_recognizer.model_place, 2)
        self.assertEqual(self.model_recognizer.po_place, 1)
        self.assertEqual(self.model_recognizer.qty_place, 3)

    def test_recognize_model_success(self):
        """测试成功识别模型"""
        # 测试标准QR码格式
        qr_data = "PO123@MODEL456@QTY10@OTHER_DATA"
        result = self.model_recognizer.recognize_model(qr_data)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["model"], "MODEL456")
        self.assertEqual(result["po"], "PO123")
        self.assertEqual(result["qty"], "QTY10")
        self.assertEqual(result["other_data"], ["OTHER_DATA"])

    def test_recognize_model_with_different_splitter(self):
        """测试使用不同分隔符识别模型"""
        # 修改分隔符
        self.model_recognizer.qr_split_str = "#"
        
        # 测试使用#分隔符的QR码
        qr_data = "PO123#MODEL456#QTY10#OTHER_DATA"
        result = self.model_recognizer.recognize_model(qr_data)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["model"], "MODEL456")
        self.assertEqual(result["po"], "PO123")
        self.assertEqual(result["qty"], "QTY10")

    def test_recognize_model_with_different_positions(self):
        """测试使用不同位置识别模型"""
        # 修改位置配置
        self.model_recognizer.model_place = 1
        self.model_recognizer.po_place = 2
        self.model_recognizer.qty_place = 3
        
        # 测试不同位置的QR码
        qr_data = "MODEL456@PO123@QTY10@OTHER_DATA"
        result = self.model_recognizer.recognize_model(qr_data)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["model"], "MODEL456")
        self.assertEqual(result["po"], "PO123")
        self.assertEqual(result["qty"], "QTY10")

    def test_recognize_model_insufficient_parts(self):
        """测试识别模型部分不足"""
        # 测试部分不足的QR码
        qr_data = "PO123@MODEL456"  # 只有2部分，需要至少3部分
        result = self.model_recognizer.recognize_model(qr_data)
        
        self.assertFalse(result["success"])
        self.assertIn("QR码数据格式错误", result["error_message"])

    def test_recognize_model_empty_data(self):
        """测试识别空数据"""
        # 测试空数据
        result = self.model_recognizer.recognize_model("")
        
        self.assertFalse(result["success"])
        self.assertIn("QR码数据为空", result["error_message"])

    def test_recognize_model_none_data(self):
        """测试识别None数据"""
        # 测试None数据
        result = self.model_recognizer.recognize_model(None)
        
        self.assertFalse(result["success"])
        self.assertIn("QR码数据为空", result["error_message"])

    def test_recognize_model_with_extra_parts(self):
        """测试识别带额外部分的模型"""
        # 测试带额外部分的QR码
        qr_data = "PO123@MODEL456@QTY10@EXTRA1@EXTRA2@EXTRA3"
        result = self.model_recognizer.recognize_model(qr_data)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["model"], "MODEL456")
        self.assertEqual(result["po"], "PO123")
        self.assertEqual(result["qty"], "QTY10")
        self.assertEqual(result["other_data"], ["EXTRA1", "EXTRA2", "EXTRA3"])

    def test_recognize_model_with_special_characters(self):
        """测试识别带特殊字符的模型"""
        # 测试带特殊字符的QR码
        qr_data = "PO-123@MODEL-456@QTY-10@SPECIAL_CHAR"
        result = self.model_recognizer.recognize_model(qr_data)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["model"], "MODEL-456")
        self.assertEqual(result["po"], "PO-123")
        self.assertEqual(result["qty"], "QTY-10")

    def test_recognize_model_with_spaces(self):
        """测试识别带空格的模型"""
        # 测试带空格的QR码
        qr_data = "PO 123@MODEL 456@QTY 10@WITH SPACES"
        result = self.model_recognizer.recognize_model(qr_data)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["model"], "MODEL 456")
        self.assertEqual(result["po"], "PO 123")
        self.assertEqual(result["qty"], "QTY 10")

    def test_validate_qr_data_format(self):
        """测试验证QR数据格式"""
        # 测试有效格式
        qr_data = "PO123@MODEL456@QTY10"
        is_valid = self.model_recognizer._validate_qr_data_format(qr_data)
        self.assertTrue(is_valid)
        
        # 测试无效格式（部分不足）
        qr_data = "PO123@MODEL456"
        is_valid = self.model_recognizer._validate_qr_data_format(qr_data)
        self.assertFalse(is_valid)
        
        # 测试无效格式（空数据）
        qr_data = ""
        is_valid = self.model_recognizer._validate_qr_data_format(qr_data)
        self.assertFalse(is_valid)

    def test_extract_qr_parts(self):
        """测试提取QR码部分"""
        # 测试标准QR码
        qr_data = "PO123@MODEL456@QTY10@OTHER_DATA"
        parts = self.model_recognizer._extract_qr_parts(qr_data)
        
        self.assertEqual(len(parts), 4)
        self.assertEqual(parts[0], "PO123")
        self.assertEqual(parts[1], "MODEL456")
        self.assertEqual(parts[2], "QTY10")
        self.assertEqual(parts[3], "OTHER_DATA")

    def test_extract_qr_parts_with_different_splitter(self):
        """测试使用不同分隔符提取QR码部分"""
        # 修改分隔符
        self.model_recognizer.qr_split_str = "#"
        
        # 测试使用#分隔符的QR码
        qr_data = "PO123#MODEL456#QTY10#OTHER_DATA"
        parts = self.model_recognizer._extract_qr_parts(qr_data)
        
        self.assertEqual(len(parts), 4)
        self.assertEqual(parts[0], "PO123")
        self.assertEqual(parts[1], "MODEL456")
        self.assertEqual(parts[2], "QTY10")
        self.assertEqual(parts[3], "OTHER_DATA")

    def test_extract_qr_parts_empty(self):
        """测试提取空QR码部分"""
        # 测试空数据
        parts = self.model_recognizer._extract_qr_parts("")
        
        self.assertEqual(len(parts), 0)

    def test_get_model_from_parts(self):
        """测试从部分获取模型"""
        # 测试标准位置
        parts = ["PO123", "MODEL456", "QTY10", "OTHER_DATA"]
        model = self.model_recognizer._get_model_from_parts(parts)
        
        self.assertEqual(model, "MODEL456")

    def test_get_model_from_parts_different_position(self):
        """测试从不同位置获取模型"""
        # 修改模型位置
        self.model_recognizer.model_place = 1
        
        # 测试不同位置
        parts = ["MODEL456", "PO123", "QTY10", "OTHER_DATA"]
        model = self.model_recognizer._get_model_from_parts(parts)
        
        self.assertEqual(model, "MODEL456")

    def test_get_model_from_parts_invalid_position(self):
        """测试从无效位置获取模型"""
        # 设置无效位置
        self.model_recognizer.model_place = 10  # 超出范围
        
        parts = ["PO123", "MODEL456", "QTY10"]
        model = self.model_recognizer._get_model_from_parts(parts)
        
        # 无效位置应该返回空字符串
        self.assertEqual(model, "")

    def test_get_po_from_parts(self):
        """测试从部分获取PO"""
        # 测试标准位置
        parts = ["PO123", "MODEL456", "QTY10", "OTHER_DATA"]
        po = self.model_recognizer._get_po_from_parts(parts)
        
        self.assertEqual(po, "PO123")

    def test_get_qty_from_parts(self):
        """测试从部分获取数量"""
        # 测试标准位置
        parts = ["PO123", "MODEL456", "QTY10", "OTHER_DATA"]
        qty = self.model_recognizer._get_qty_from_parts(parts)
        
        self.assertEqual(qty, "QTY10")

    def test_get_other_data_from_parts(self):
        """测试从部分获取其他数据"""
        # 测试标准位置
        parts = ["PO123", "MODEL456", "QTY10", "EXTRA1", "EXTRA2"]
        other_data = self.model_recognizer._get_other_data_from_parts(parts)
        
        self.assertEqual(len(other_data), 2)
        self.assertEqual(other_data[0], "EXTRA1")
        self.assertEqual(other_data[1], "EXTRA2")

    def test_get_other_data_from_parts_no_extra(self):
        """测试从部分获取无额外数据"""
        # 测试无额外数据
        parts = ["PO123", "MODEL456", "QTY10"]
        other_data = self.model_recognizer._get_other_data_from_parts(parts)
        
        self.assertEqual(len(other_data), 0)

    def test_parse_numeric_value(self):
        """测试解析数值"""
        # 测试整数
        value = self.model_recognizer._parse_numeric_value("123")
        self.assertEqual(value, 123)
        
        # 测试浮点数
        value = self.model_recognizer._parse_numeric_value("123.45")
        self.assertEqual(value, 123.45)
        
        # 测试非数值
        value = self.model_recognizer._parse_numeric_value("ABC")
        self.assertEqual(value, "ABC")
        
        # 测试空值
        value = self.model_recognizer._parse_numeric_value("")
        self.assertEqual(value, "")

    def test_clean_model_string(self):
        """测试清理模型字符串"""
        # 测试标准字符串
        cleaned = self.model_recognizer._clean_model_string("MODEL456")
        self.assertEqual(cleaned, "MODEL456")
        
        # 测试带空格的字符串
        cleaned = self.model_recognizer._clean_model_string(" MODEL 456 ")
        self.assertEqual(cleaned, "MODEL 456")
        
        # 测试带特殊字符的字符串
        cleaned = self.model_recognizer._clean_model_string("MODEL-456_SPECIAL")
        self.assertEqual(cleaned, "MODEL-456_SPECIAL")

    def test_batch_recognize_models(self):
        """测试批量识别模型"""
        # 测试批量识别
        qr_data_list = [
            "PO123@MODEL456@QTY10",
            "PO124@MODEL457@QTY20",
            "PO125@MODEL458@QTY30"
        ]
        
        results = self.model_recognizer.batch_recognize_models(qr_data_list)
        
        self.assertEqual(len(results), 3)
        self.assertTrue(results[0]["success"])
        self.assertTrue(results[1]["success"])
        self.assertTrue(results[2]["success"])
        
        self.assertEqual(results[0]["model"], "MODEL456")
        self.assertEqual(results[1]["model"], "MODEL457")
        self.assertEqual(results[2]["model"], "MODEL458")

    def test_batch_recognize_models_with_errors(self):
        """测试批量识别模型包含错误"""
        # 测试包含错误的批量识别
        qr_data_list = [
            "PO123@MODEL456@QTY10",  # 有效
            "PO124@MODEL457",         # 无效（部分不足）
            "PO125@MODEL458@QTY30"   # 有效
        ]
        
        results = self.model_recognizer.batch_recognize_models(qr_data_list)
        
        self.assertEqual(len(results), 3)
        self.assertTrue(results[0]["success"])
        self.assertFalse(results[1]["success"])
        self.assertTrue(results[2]["success"])

    def test_get_recognition_statistics(self):
        """测试获取识别统计信息"""
        # 创建一些识别结果
        results = [
            {"success": True, "model": "MODEL456"},
            {"success": True, "model": "MODEL457"},
            {"success": False, "error_message": "格式错误"},
            {"success": True, "model": "MODEL458"}
        ]
        
        stats = self.model_recognizer.get_recognition_statistics(results)
        
        self.assertEqual(stats["total"], 4)
        self.assertEqual(stats["successful"], 3)
        self.assertEqual(stats["failed"], 1)
        self.assertEqual(stats["success_rate"], 0.75)
        self.assertIn("models", stats)

    def test_update_configuration(self):
        """测试更新配置"""
        # 测试更新配置
        new_config = {
            "qr_split_str": "#",
            "model_place": 1,
            "po_place": 2,
            "qty_place": 3
        }
        
        result = self.model_recognizer.update_configuration(new_config)
        
        self.assertTrue(result)
        self.assertEqual(self.model_recognizer.qr_split_str, "#")
        self.assertEqual(self.model_recognizer.model_place, 1)
        self.assertEqual(self.model_recognizer.po_place, 2)
        self.assertEqual(self.model_recognizer.qty_place, 3)

    def test_update_configuration_partial(self):
        """测试部分更新配置"""
        # 测试部分更新配置
        new_config = {
            "qr_split_str": "#"
        }
        
        result = self.model_recognizer.update_configuration(new_config)
        
        self.assertTrue(result)
        self.assertEqual(self.model_recognizer.qr_split_str, "#")
        # 其他配置应该保持不变
        self.assertEqual(self.model_recognizer.model_place, 2)

    def test_update_configuration_invalid(self):
        """测试更新无效配置"""
        # 测试更新无效配置
        new_config = {
            "invalid_key": "value"
        }
        
        result = self.model_recognizer.update_configuration(new_config)
        
        # 无效配置应该返回False
        self.assertFalse(result)

    def test_validate_configuration(self):
        """测试验证配置"""
        # 测试有效配置
        config = {
            "qr_split_str": "@",
            "model_place": 2,
            "po_place": 1,
            "qty_place": 3
        }
        
        result = self.model_recognizer.validate_configuration(config)
        
        self.assertTrue(result["valid"])
        self.assertEqual(len(result["errors"]), 0)

    def test_validate_configuration_invalid(self):
        """测试验证无效配置"""
        # 测试无效配置
        config = {
            "qr_split_str": "",  # 空分隔符
            "model_place": 0,    # 无效位置
            "po_place": -1,      # 无效位置
            "qty_place": 100     # 过大位置
        }
        
        result = self.model_recognizer.validate_configuration(config)
        
        self.assertFalse(result["valid"])
        self.assertGreater(len(result["errors"]), 0)


if __name__ == '__main__':
    unittest.main()
