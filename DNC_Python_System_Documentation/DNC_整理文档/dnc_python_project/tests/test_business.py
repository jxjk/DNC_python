import sys
import os
import unittest
from unittest.mock import Mock, patch

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from business.model_recognizer import ModelRecognizer
from business.program_matcher import ProgramMatcher
from business.calculation_engine import CalculationEngine
from business.nc_communicator import NCCommunicator


class TestModelRecognizer(unittest.TestCase):
    """型号识别器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.recognizer = ModelRecognizer()
    
    def test_recognize_model(self):
        """测试型号识别"""
        # 测试基本参数识别
        parameters = {
            'geometry': {
                'length': 100,
                'width': 50,
                'height': 20
            },
            'material': {
                'material_type': '碳钢'
            }
        }
        
        model = self.recognizer.recognize_model(parameters)
        self.assertIsNotNone(model)
        self.assertIn('model_code', model)
        self.assertIn('model_name', model)
    
    def test_recognize_model_with_invalid_params(self):
        """测试无效参数识别"""
        parameters = {}
        model = self.recognizer.recognize_model(parameters)
        self.assertIsNone(model)
    
    def test_get_model_list(self):
        """测试获取型号列表"""
        model_list = self.recognizer.get_model_list()
        self.assertIsInstance(model_list, list)
        self.assertGreater(len(model_list), 0)


class TestProgramMatcher(unittest.TestCase):
    """程序匹配器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.matcher = ProgramMatcher()
    
    def test_match_program(self):
        """测试程序匹配"""
        model_info = {
            'model_code': 'TEST001',
            'model_name': '测试型号'
        }
        
        program = self.matcher.match_program(model_info)
        self.assertIsNotNone(program)
        self.assertIn('program_code', program)
        self.assertIn('program_name', program)
        self.assertIn('nc_code', program)
    
    def test_match_program_with_invalid_model(self):
        """测试无效型号匹配"""
        model_info = {}
        program = self.matcher.match_program(model_info)
        self.assertIsNone(program)
    
    def test_get_program_list(self):
        """测试获取程序列表"""
        program_list = self.matcher.get_program_list()
        self.assertIsInstance(program_list, list)
        self.assertGreater(len(program_list), 0)


class TestCalculationEngine(unittest.TestCase):
    """计算引擎测试"""
    
    def setUp(self):
        """测试前准备"""
        self.engine = CalculationEngine()
    
    def test_calculate_parameters(self):
        """测试参数计算"""
        input_params = {
            'geometry': {
                'length': 100,
                'width': 50,
                'height': 20
            },
            'material': {
                'material_type': '碳钢',
                'material_hardness': '中等'
            },
            'process': {
                'process_type': '铣削'
            }
        }
        
        result = self.engine.calculate_parameters(input_params)
        self.assertIsNotNone(result)
        self.assertIn('spindle_speed', result)
        self.assertIn('feed_rate', result)
        self.assertIn('cut_depth', result)
        self.assertIn('cut_width', result)
    
    def test_calculate_parameters_with_invalid_input(self):
        """测试无效输入计算"""
        input_params = {}
        result = self.engine.calculate_parameters(input_params)
        self.assertIsNone(result)
    
    def test_validate_parameters(self):
        """测试参数验证"""
        parameters = {
            'spindle_speed': 1000,
            'feed_rate': 200,
            'cut_depth': 2.0,
            'cut_width': 5.0
        }
        
        is_valid = self.engine.validate_parameters(parameters)
        self.assertTrue(is_valid)
    
    def test_validate_parameters_with_invalid_values(self):
        """测试无效参数验证"""
        parameters = {
            'spindle_speed': -1000,  # 负值
            'feed_rate': 0,          # 零值
            'cut_depth': 100,        # 过大值
            'cut_width': -5.0        # 负值
        }
        
        is_valid = self.engine.validate_parameters(parameters)
        self.assertFalse(is_valid)


class TestNCCommunicator(unittest.TestCase):
    """NC通信器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.communicator = NCCommunicator()
    
    def test_connect_disconnect(self):
        """测试连接和断开"""
        # 测试连接
        result = self.communicator.connect('192.168.1.100', 8080)
        self.assertTrue(result)
        self.assertTrue(self.communicator.is_connected)
        
        # 测试断开
        self.communicator.disconnect()
        self.assertFalse(self.communicator.is_connected)
    
    def test_send_program(self):
        """测试发送程序"""
        # 先连接
        self.communicator.connect('192.168.1.100', 8080)
        
        # 测试发送程序
        program = "O1001\nG90 G54 G00 X0 Y0\nM30"
        result = self.communicator.send_program(program)
        self.assertTrue(result)
    
    def test_send_program_without_connection(self):
        """测试未连接时发送程序"""
        program = "O1001\nG90 G54 G00 X0 Y0\nM30"
        result = self.communicator.send_program(program)
        self.assertFalse(result)
    
    def test_get_status(self):
        """测试获取状态"""
        # 先连接
        self.communicator.connect('192.168.1.100', 8080)
        
        status = self.communicator.get_status()
        self.assertIsNotNone(status)
        self.assertIn('connected', status)
        self.assertIn('running', status)
        self.assertIn('current_line', status)
    
    def test_get_status_without_connection(self):
        """测试未连接时获取状态"""
        status = self.communicator.get_status()
        self.assertIsNotNone(status)
        self.assertFalse(status['connected'])


if __name__ == '__main__':
    unittest.main()
