"""
ControlFactory模块单元测试
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from dnc_python_project.src.ui.control_factory import ControlFactory, get_global_control_factory
from PyQt5.QtWidgets import QApplication, QWidget


class TestControlFactory(unittest.TestCase):
    """ControlFactory类测试"""
    
    @classmethod
    def setUpClass(cls):
        """测试类设置"""
        # 创建QApplication实例（需要GUI环境）
        cls.app = QApplication([])
        
    def setUp(self):
        """测试前准备"""
        self.factory = ControlFactory()
        self.parent_widget = QWidget()
        
    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.factory)
        self.assertIsNotNone(self.factory.logger)
        self.assertEqual(self.factory._control_cache, {})
        
    def test_create_load_control(self):
        """测试创建只读显示控件"""
        config = {
            'KIND': 'load',
            'MACRO': 'TEST_MACRO'
        }
        
        control = self.factory.create_control(config, self.parent_widget)
        
        # 验证控件创建
        self.assertIsNotNone(control)
        self.assertEqual(control.property("control_type"), "load")
        self.assertEqual(control.property("macro_name"), "TEST_MACRO")
        
    def test_create_input_control(self):
        """测试创建输入控件"""
        config = {
            'KIND': 'input',
            'MACRO': 'INPUT_MACRO'
        }
        
        control = self.factory.create_control(config, self.parent_widget)
        
        # 验证控件创建
        self.assertIsNotNone(control)
        self.assertEqual(control.property("control_type"), "input")
        self.assertEqual(control.property("macro_name"), "INPUT_MACRO")
        
    def test_create_measure_control(self):
        """测试创建测量控件"""
        config = {
            'KIND': 'measure',
            'MACRO': 'MEASURE_MACRO'
        }
        
        control = self.factory.create_control(config, self.parent_widget)
        
        # 验证控件创建
        self.assertIsNotNone(control)
        self.assertEqual(control.property("control_type"), "measure")
        self.assertEqual(control.property("macro_name"), "MEASURE_MACRO")
        
    def test_create_select_control(self):
        """测试创建选择控件"""
        config = {
            'KIND': 'select',
            'MACRO': 'SELECT_MACRO'
        }
        
        control = self.factory.create_control(config, self.parent_widget)
        
        # 验证控件创建
        self.assertIsNotNone(control)
        self.assertEqual(control.property("control_type"), "select")
        self.assertEqual(control.property("macro_name"), "SELECT_MACRO")
        
    def test_create_relation_control(self):
        """测试创建关系验证控件"""
        config = {
            'KIND': 'relation',
            'MACRO': 'RELATION_MACRO'
        }
        
        control = self.factory.create_control(config, self.parent_widget)
        
        # 验证控件创建
        self.assertIsNotNone(control)
        self.assertEqual(control.property("control_type"), "relation")
        self.assertEqual(control.property("macro_name"), "RELATION_MACRO")
        
    def test_create_switch_control(self):
        """测试创建开关控件"""
        config = {
            'KIND': 'switch',
            'MACRO': 'SWITCH_MACRO'
        }
        
        control = self.factory.create_control(config, self.parent_widget)
        
        # 验证控件创建
        self.assertIsNotNone(control)
        self.assertEqual(control.property("control_type"), "switch")
        self.assertEqual(control.property("macro_name"), "SWITCH_MACRO")
        
    def test_create_correct_control(self):
        """测试创建修正控件"""
        config = {
            'KIND': 'correct',
            'MACRO': 'CORRECT_MACRO'
        }
        
        control = self.factory.create_control(config, self.parent_widget)
        
        # 验证控件创建
        self.assertIsNotNone(control)
        self.assertEqual(control.property("control_type"), "correct")
        self.assertEqual(control.property("macro_name"), "CORRECT_MACRO")
        
    def test_create_unknown_control_type(self):
        """测试创建未知控件类型"""
        config = {
            'KIND': 'unknown',
            'MACRO': 'UNKNOWN_MACRO'
        }
        
        control = self.factory.create_control(config, self.parent_widget)
        
        # 验证创建了默认控件
        self.assertIsNotNone(control)
        self.assertEqual(control.property("control_type"), "default")
        self.assertEqual(control.property("macro_name"), "UNKNOWN_MACRO")
        
    def test_create_control_with_exception(self):
        """测试创建控件时发生异常"""
        config = {
            'KIND': 'load',
            'MACRO': 'TEST_MACRO'
        }
        
        # 模拟异常
        with patch.object(self.factory, '_create_load_control', side_effect=Exception("Test error")):
            control = self.factory.create_control(config, self.parent_widget)
            
        # 验证创建了错误控件
        self.assertIsNotNone(control)
        
    def test_create_parameter_group(self):
        """测试创建参数组"""
        # 创建一些测试控件
        controls = []
        for i in range(3):
            config = {
                'KIND': 'load',
                'MACRO': f'MACRO_{i}'
            }
            control = self.factory.create_control(config, self.parent_widget)
            controls.append(control)
        
        # 创建参数组
        group = self.factory.create_parameter_group("测试组", controls, self.parent_widget)
        
        # 验证参数组创建
        self.assertIsNotNone(group)
        self.assertEqual(group.title(), "测试组")
        
    def test_clear_cache(self):
        """测试清空缓存"""
        # 添加一些控件到缓存
        self.factory._control_cache['test_key'] = Mock()
        
        # 清空缓存
        self.factory.clear_cache()
        
        # 验证缓存已清空
        self.assertEqual(self.factory._control_cache, {})
        
    def test_get_global_control_factory(self):
        """测试获取全局控件工厂"""
        factory1 = get_global_control_factory()
        factory2 = get_global_control_factory()
        
        # 验证是同一个实例
        self.assertIs(factory1, factory2)
        
    def test_control_properties(self):
        """测试控件属性设置"""
        config = {
            'KIND': 'load',
            'MACRO': 'TEST_MACRO'
        }
        
        control = self.factory.create_control(config, self.parent_widget)
        
        # 验证控件属性
        self.assertEqual(control.property("control_type"), "load")
        self.assertEqual(control.property("macro_name"), "TEST_MACRO")
        
    def test_control_layout(self):
        """测试控件布局"""
        config = {
            'KIND': 'load',
            'MACRO': 'TEST_MACRO'
        }
        
        control = self.factory.create_control(config, self.parent_widget)
        
        # 验证控件有布局
        self.assertIsNotNone(control.layout())
        
    def test_multiple_control_types(self):
        """测试多种控件类型"""
        control_types = ['load', 'input', 'measure', 'select', 'relation', 'switch', 'correct']
        
        for control_type in control_types:
            with self.subTest(control_type=control_type):
                config = {
                    'KIND': control_type,
                    'MACRO': f'{control_type.upper()}_MACRO'
                }
                
                control = self.factory.create_control(config, self.parent_widget)
                
                # 验证控件创建成功
                self.assertIsNotNone(control)
                self.assertEqual(control.property("control_type"), control_type)
                self.assertEqual(control.property("macro_name"), f'{control_type.upper()}_MACRO')
                
    def test_control_without_parent(self):
        """测试创建无父控件的控件"""
        config = {
            'KIND': 'load',
            'MACRO': 'TEST_MACRO'
        }
        
        control = self.factory.create_control(config)
        
        # 验证控件创建成功
        self.assertIsNotNone(control)
        self.assertIsNone(control.parent())
        
    def test_control_config_validation(self):
        """测试控件配置验证"""
        # 测试缺少MACRO的情况
        config = {
            'KIND': 'load'
        }
        
        control = self.factory.create_control(config, self.parent_widget)
        
        # 验证控件仍然创建成功
        self.assertIsNotNone(control)
        self.assertEqual(control.property("macro_name"), "未知")
        
    @patch('dnc_python_project.src.ui.control_factory.get_logger')
    def test_logging(self, mock_get_logger):
        """测试日志记录"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        factory = ControlFactory()
        
        config = {
            'KIND': 'load',
            'MACRO': 'TEST_MACRO'
        }
        
        factory.create_control(config, self.parent_widget)
        
        # 验证日志记录
        mock_logger.debug.assert_called_with("创建控件: TEST_MACRO, 类型: load")


if __name__ == '__main__':
    unittest.main()
