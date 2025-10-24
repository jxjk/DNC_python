"""
Application模块单元测试
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from dnc_python_project.src.core.application import DNCApplication, create_application
from dnc_python_project.src.core.config import ConfigManager
from dnc_python_project.src.core.event_dispatcher import EventDispatcher
from dnc_python_project.src.utils.constants import EVENT_TYPES


class TestDNCApplication(unittest.TestCase):
    """DNCApplication类测试"""
    
    def setUp(self):
        """测试前准备"""
        self.mock_config_path = "test_config.ini"
        self.app = DNCApplication(self.mock_config_path)
        
        # Mock所有依赖模块
        self.mock_config_manager = Mock(spec=ConfigManager)
        self.mock_event_dispatcher = Mock(spec=EventDispatcher)
        
    def test_initialization(self):
        """测试应用初始化"""
        # 测试初始化状态
        self.assertEqual(self.app.config_path, self.mock_config_path)
        self.assertFalse(self.app.is_initialized)
        self.assertFalse(self.app.is_running)
        
    @patch('dnc_python_project.src.core.application.ConfigManager')
    @patch('dnc_python_project.src.core.application.EventDispatcher')
    @patch('dnc_python_project.src.core.application.Logger')
    def test_initialize_success(self, mock_logger, mock_event_dispatcher, mock_config_manager):
        """测试成功初始化"""
        # 设置mock
        mock_config_instance = Mock()
        mock_config_instance.load_all_configs.return_value = True
        mock_config_manager.return_value = mock_config_instance
        
        mock_event_instance = Mock()
        mock_event_dispatcher.return_value = mock_event_instance
        
        mock_logger_instance = Mock()
        mock_logger.get_logger.return_value = mock_logger_instance
        
        # 执行初始化
        result = self.app.initialize()
        
        # 验证结果
        self.assertTrue(result)
        self.assertTrue(self.app.is_initialized)
        mock_logger_instance.info.assert_called_with("DNC系统初始化完成")
        
    @patch('dnc_python_project.src.core.application.ConfigManager')
    @patch('dnc_python_project.src.core.application.Logger')
    def test_initialize_failure(self, mock_logger, mock_config_manager):
        """测试初始化失败"""
        # 设置mock
        mock_config_instance = Mock()
        mock_config_instance.load_all_configs.return_value = False
        mock_config_manager.return_value = mock_config_instance
        
        mock_logger_instance = Mock()
        mock_logger.get_logger.return_value = mock_logger_instance
        
        # 执行初始化
        result = self.app.initialize()
        
        # 验证结果
        self.assertFalse(result)
        self.assertFalse(self.app.is_initialized)
        mock_logger_instance.error.assert_called_with("配置文件加载失败")
        
    def test_setup_event_handlers(self):
        """测试事件处理器设置"""
        # 设置mock事件分发器
        self.app.event_dispatcher = Mock()
        
        # 执行设置
        self.app._setup_event_handlers()
        
        # 验证事件处理器注册
        self.app.event_dispatcher.register_handler.assert_any_call(
            EVENT_TYPES.MODEL_RECOGNIZED, 
            self.app._on_model_recognized
        )
        self.app.event_dispatcher.register_handler.assert_any_call(
            EVENT_TYPES.PROGRAM_MATCHED,
            self.app._on_program_matched
        )
        self.app.event_dispatcher.register_handler.assert_any_call(
            EVENT_TYPES.PARAMETERS_CALCULATED,
            self.app._on_parameters_calculated
        )
        self.app.event_dispatcher.register_handler.assert_any_call(
            EVENT_TYPES.DATA_SENT,
            self.app._on_data_sent
        )
        
    @patch('dnc_python_project.src.core.application.QApplication')
    def test_run_without_initialization(self, mock_qapp):
        """测试未初始化时运行"""
        # 确保应用未初始化
        self.app.is_initialized = False
        
        # 执行运行
        result = self.app.run()
        
        # 验证结果
        self.assertEqual(result, 1)
        
    @patch('dnc_python_project.src.core.application.QApplication')
    @patch('dnc_python_project.src.core.application.MainWindow')
    def test_run_success(self, mock_main_window, mock_qapp):
        """测试成功运行"""
        # 设置应用为已初始化状态
        self.app.is_initialized = True
        
        # 设置mock
        mock_qapp_instance = Mock()
        mock_qapp_instance.exec_.return_value = 0
        mock_qapp.return_value = mock_qapp_instance
        
        mock_main_window_instance = Mock()
        mock_main_window.return_value = mock_main_window_instance
        
        # 执行运行
        result = self.app.run()
        
        # 验证结果
        self.assertEqual(result, 0)
        self.assertTrue(self.app.is_running)
        mock_main_window_instance.show.assert_called_once()
        
    def test_process_qr_code_success(self):
        """测试QR码处理成功"""
        # 设置mock
        self.app.is_initialized = True
        self.app.model_recognizer = Mock()
        self.app.program_matcher = Mock()
        self.app.calculation_engine = Mock()
        self.app.relation_validator = Mock()
        self.app.event_dispatcher = Mock()
        
        # 设置mock返回值
        model_info = {'model': 'TEST-MODEL', 'processed_parts': ['PART1', 'PART2']}
        program_info = {'program_no': 1}
        parameters = {'#500': '10', '#501': '20'}
        validation_results = {'valid': True}
        
        self.app.model_recognizer.recognize_model.return_value = model_info
        self.app.program_matcher.match_program.return_value = program_info
        self.app.calculation_engine.calculate.return_value = parameters
        self.app.relation_validator.validate_relations.return_value = validation_results
        
        # 执行QR码处理
        result = self.app.process_qr_code("TEST-QR-CODE")
        
        # 验证结果
        self.assertTrue(result)
        self.assertEqual(self.app.current_model, 'TEST-MODEL')
        self.assertEqual(self.app.current_program_no, 1)
        self.assertEqual(self.app.current_parameters, parameters)
        
    def test_process_qr_code_failure(self):
        """测试QR码处理失败"""
        # 设置mock
        self.app.is_initialized = True
        self.app.model_recognizer = Mock()
        self.app.event_dispatcher = Mock()
        
        # 设置mock返回值
        self.app.model_recognizer.recognize_model.return_value = None
        
        # 执行QR码处理
        result = self.app.process_qr_code("INVALID-QR-CODE")
        
        # 验证结果
        self.assertFalse(result)
        
    def test_send_parameters_to_nc_success(self):
        """测试发送参数到NC成功"""
        # 设置mock
        self.app.current_protocol = Mock()
        self.app.current_parameters = {'#500': '10', '#501': '20'}
        self.app.event_dispatcher = Mock()
        
        # 设置mock返回值
        self.app.current_protocol.send_parameters.return_value = True
        
        # 执行发送
        result = self.app.send_parameters_to_nc()
        
        # 验证结果
        self.assertTrue(result)
        self.app.current_protocol.send_parameters.assert_called_with(
            self.app.current_parameters
        )
        
    def test_send_parameters_to_nc_no_protocol(self):
        """测试发送参数时协议未初始化"""
        # 设置mock
        self.app.current_protocol = None
        self.app.current_parameters = {'#500': '10', '#501': '20'}
        
        # 执行发送
        result = self.app.send_parameters_to_nc()
        
        # 验证结果
        self.assertFalse(result)
        
    def test_send_parameters_to_nc_no_parameters(self):
        """测试发送参数时无参数"""
        # 设置mock
        self.app.current_protocol = Mock()
        self.app.current_parameters = {}
        
        # 执行发送
        result = self.app.send_parameters_to_nc()
        
        # 验证结果
        self.assertFalse(result)
        
    def test_get_application_info(self):
        """测试获取应用信息"""
        # 设置应用状态
        self.app.is_initialized = True
        self.app.is_running = False
        self.app.current_model = 'TEST-MODEL'
        self.app.current_program_no = 1
        self.app.current_parameters = {'#500': '10', '#501': '20'}
        
        # 获取应用信息
        info = self.app.get_application_info()
        
        # 验证信息内容
        expected_info = {
            "name": "DNC系统",
            "version": "2.0.0",
            "initialized": True,
            "running": False,
            "current_model": 'TEST-MODEL',
            "current_program": 1,
            "parameter_count": 2
        }
        
        self.assertEqual(info, expected_info)
        
    def test_create_application_factory(self):
        """测试应用工厂函数"""
        # 使用工厂函数创建应用
        app = create_application("test_config.ini")
        
        # 验证应用实例
        self.assertIsInstance(app, DNCApplication)
        self.assertEqual(app.config_path, "test_config.ini")
        
    def test_cleanup(self):
        """测试资源清理"""
        # 设置mock
        self.app.named_pipe_manager = Mock()
        self.app.file_manager = Mock()
        self.app.logger = Mock()
        
        # 执行清理
        self.app._cleanup()
        
        # 验证清理操作
        self.app.named_pipe_manager.stop_server.assert_called_once()
        self.app.file_manager.close_all_files.assert_called_once()
        self.app.logger.info.assert_called_with("系统资源清理完成")


if __name__ == '__main__':
    unittest.main()
