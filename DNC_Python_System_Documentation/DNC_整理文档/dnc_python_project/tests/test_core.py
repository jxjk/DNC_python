import sys
import os
import unittest
from unittest.mock import Mock, patch

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.application import DNCApplication
from core.config import ConfigManager
from core.event_dispatcher import EventDispatcher


class TestConfigManager(unittest.TestCase):
    """配置管理器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.config = ConfigManager()
    
    def test_default_config(self):
        """测试默认配置"""
        self.assertIsNotNone(self.config.get('system'))
        self.assertIsNotNone(self.config.get('ui'))
        self.assertIsNotNone(self.config.get('communication'))
    
    def test_set_get_config(self):
        """测试设置和获取配置"""
        test_value = "test_value"
        self.config.set('test_key', test_value)
        self.assertEqual(self.config.get('test_key'), test_value)
    
    def test_save_load_config(self):
        """测试保存和加载配置"""
        # 测试保存配置
        self.config.save_config()
        
        # 测试加载配置
        new_config = ConfigManager()
        self.assertEqual(self.config.get('system'), new_config.get('system'))


class TestEventDispatcher(unittest.TestCase):
    """事件分发器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.dispatcher = EventDispatcher()
        self.callback_called = False
        self.callback_data = None
    
    def test_register_event(self):
        """测试注册事件"""
        def test_callback(data):
            self.callback_called = True
            self.callback_data = data
        
        self.dispatcher.register('test_event', test_callback)
        self.assertIn('test_event', self.dispatcher._listeners)
    
    def test_emit_event(self):
        """测试触发事件"""
        def test_callback(data):
            self.callback_called = True
            self.callback_data = data
        
        self.dispatcher.register('test_event', test_callback)
        test_data = {'key': 'value'}
        self.dispatcher.emit('test_event', test_data)
        
        self.assertTrue(self.callback_called)
        self.assertEqual(self.callback_data, test_data)
    
    def test_unregister_event(self):
        """测试注销事件"""
        def test_callback(data):
            pass
        
        self.dispatcher.register('test_event', test_callback)
        self.dispatcher.unregister('test_event', test_callback)
        self.assertNotIn(test_callback, self.dispatcher._listeners['test_event'])


class TestDNCApplication(unittest.TestCase):
    """DNC应用程序测试"""
    
    def setUp(self):
        """测试前准备"""
        self.app = DNCApplication()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.app.config_manager)
        self.assertIsNotNone(self.app.event_dispatcher)
        self.assertIsNotNone(self.app.model_recognizer)
        self.assertIsNotNone(self.app.program_matcher)
        self.assertIsNotNone(self.app.calculation_engine)
        self.assertIsNotNone(self.app.nc_communicator)
    
    def test_start_stop(self):
        """测试启动和停止"""
        # 测试启动
        self.app.start()
        self.assertTrue(self.app.is_running)
        
        # 测试停止
        self.app.stop()
        self.assertFalse(self.app.is_running)
    
    @patch('core.application.MainWindow')
    def test_show_main_window(self, mock_main_window):
        """测试显示主窗口"""
        self.app.show_main_window()
        mock_main_window.assert_called_once()


if __name__ == '__main__':
    unittest.main()
