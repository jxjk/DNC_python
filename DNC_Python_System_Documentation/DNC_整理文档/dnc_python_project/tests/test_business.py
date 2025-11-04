# file: c:\Users\Lenovo\Desktop\DNC_python\DNC_Python_System_Documentation\DNC_整理文档\dnc_python_project\tests\test_business.py
import sys
import os
import unittest
from unittest.mock import Mock, patch

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.business.model_recognizer import ModelRecognizer
from src.business.program_matcher import ProgramMatcher, MatchResult
from src.business.calculation_engine import CalculationEngine
from src.business.nc_communicator import NCCommunicator


class TestModelRecognizer(unittest.TestCase):
    """型号识别器测试"""
    
    def setUp(self):
        """测试前准备"""
        # 创建模拟配置管理器
        self.mock_config_manager = Mock()
        self.mock_config_manager.qr_config.qr_mode = 1
        self.mock_config_manager.qr_config.qr_split_str = "@"
        self.mock_config_manager.qr_config.model_place = 2
        self.mock_config_manager.qr_config.po_place = 1
        self.mock_config_manager.qr_config.qty_place = 3
        
        self.recognizer = ModelRecognizer(self.mock_config_manager)
    
    def test_recognize_model(self):
        """测试型号识别"""
        # 测试QR码识别
        qr_code = "PO123@MODEL456@QTY10"
        
        result = self.recognizer.recognize_model(qr_code)
        self.assertIsNotNone(result)
        self.assertEqual(result.model, "MODEL456")
        self.assertEqual(result.po, "PO123")
        self.assertEqual(result.quantity, "QTY10")
    
    def test_recognize_model_with_invalid_params(self):
        """测试无效参数识别"""
        qr_code = ""
        result = self.recognizer.recognize_model(qr_code)
        self.assertIsNotNone(result)
        self.assertEqual(result.model, "")
        self.assertEqual(result.confidence, 0.0)


class TestProgramMatcher(unittest.TestCase):
    """程序匹配器测试"""
    
    def setUp(self):
        """测试前准备"""
        # 创建模拟配置管理器和CSV处理器
        self.mock_config_manager = Mock()
        self.mock_config_manager.get_csv_config_path.return_value = "test_path.csv"
        self.mock_csv_processor = Mock()
        
        # 设置CSV处理器的read_csv方法返回正确的数据结构
        self.mock_csv_processor.read_csv.return_value = [
            ["1", "MODEL456"],  # type_define_data
            ["1", "1001"]       # type_prg_data
        ]
        
        self.matcher = ProgramMatcher(self.mock_config_manager, self.mock_csv_processor)
 
    def test_match_program(self):
        """测试程序匹配"""
        # 设置模拟数据 - 确保返回的是列表而不是Mock对象
        self.mock_csv_processor.read_csv.side_effect = [
            [["1", "MODEL456"]],  # type_define_data
            [["1", "1001"]]       # type_prg_data
        ]
        
        result = self.matcher.match_program("MODEL456")
        self.assertIsNotNone(result)
        self.assertEqual(result.program_no, 1001)
        self.assertEqual(result.match_type, "exact")
    
    def test_match_program_with_invalid_model(self):
        """测试无效型号匹配"""
        # 设置模拟数据 - 确保返回的是列表而不是Mock对象
        self.mock_csv_processor.read_csv.side_effect = [
            [["1", "OTHER_MODEL"]],  # type_define_data
            [["1", "1001"]]          # type_prg_data
        ]
        
        result = self.matcher.match_program("INVALID_MODEL")
        self.assertIsNotNone(result)
        self.assertEqual(result.program_no, 0)
        self.assertEqual(result.match_type, "no_match")
    
    def test_batch_match(self):
        """测试批量匹配"""
        # 设置模拟数据 - 确保返回的是列表而不是Mock对象
        self.mock_csv_processor.read_csv.side_effect = [
            [["1", "MODEL456"]],  # type_define_data
            [["1", "1001"]]       # type_prg_data
        ]
        
        models = ["MODEL456", "MODEL789"]
        results = self.matcher.batch_match(models)
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].program_no, 1001)
        self.assertEqual(results[1].program_no, 0)


class TestCalculationEngine(unittest.TestCase):
    """计算引擎测试"""
    
    def setUp(self):
        """测试前准备"""
        # 创建模拟配置管理器和CSV处理器
        self.mock_config_manager = Mock()
        self.mock_config_manager.get_csv_config_path.return_value = "test_path.csv"
        self.mock_csv_processor = Mock()
        
        self.engine = CalculationEngine(self.mock_config_manager, self.mock_csv_processor)
    
    def test_calculate_parameters(self):
        """测试参数计算"""
        # 设置模拟数据
        self.mock_csv_processor.read_csv.side_effect = [
            [],  # load.csv
            [],  # define.csv
            [],  # chngValue.csv
            []   # calc.csv
        ]
        
        result = self.engine.calculate_parameters(1001, {})
        self.assertIsNotNone(result)
        self.assertEqual(result.program_no, 1001)
    
    def test_calculate_parameters_with_invalid_input(self):
        """测试无效输入计算"""
        # 设置模拟数据
        self.mock_csv_processor.read_csv.side_effect = [
            [],  # load.csv
            [],  # define.csv
            [],  # chngValue.csv
            []   # calc.csv
        ]
        
        result = self.engine.calculate_parameters(0, {})
        self.assertIsNotNone(result)
        self.assertFalse(result.success)


class TestNCCommunicator(unittest.TestCase):
    """NC通信器测试"""
    
    def setUp(self):
        """测试前准备"""
        # 创建模拟配置管理器
        self.mock_config_manager = Mock()
        self.mock_config_manager.com_config.com_type = 1  # 网络通信
        self.mock_config_manager.com_config.ip_address = "192.168.1.100"
        self.mock_config_manager.com_config.port = 8080
        self.mock_config_manager.com_config.timeout = 5.0
        self.mock_config_manager.device_config.device_name = "Test Device"
        self.mock_config_manager.device_config.device_model = "Test Model"
        
        self.communicator = NCCommunicator(self.mock_config_manager)
    
    def test_connect_disconnect(self):
        """测试连接和断开"""
        # 测试连接（由于是模拟，连接会失败）
        result = self.communicator.connect()
        self.assertFalse(result)  # 模拟连接会失败
        self.assertFalse(self.communicator.is_connected())
        
        # 测试断开
        result = self.communicator.disconnect()
        self.assertTrue(result)
    
    def test_is_connected(self):
        """测试连接状态检查"""
        connected = self.communicator.is_connected()
        self.assertFalse(connected)
    
    def test_get_connection_info(self):
        """测试获取连接信息"""
        info = self.communicator.get_connection_info()
        self.assertIsNotNone(info)
        self.assertIn('connected', info)
        self.assertIn('com_type', info)
        self.assertIn('device_name', info)
        self.assertIn('device_model', info)
    
    def test_query_status(self):
        """测试查询状态"""
        # 由于未连接，查询状态应该返回None
        status = self.communicator.query_status()
        self.assertIsNone(status)  # 或者根据实际实现调整
    
    def test_execute_program(self):
        """测试执行程序"""
        # 由于未连接，执行程序应该返回None
        result = self.communicator.execute_program(1001)
        self.assertIsNone(result)
    
    def test_read_data(self):
        """测试读取数据"""
        # 由于未连接，读取数据应该返回None
        result = self.communicator.read_data("D100", 1)
        self.assertIsNone(result)
    
    def test_write_data(self):
        """测试写入数据"""
        # 由于未连接，写入数据应该返回None
        result = self.communicator.write_data("D100", 123.45)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()