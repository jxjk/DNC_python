import sys
import os
import unittest
from unittest.mock import Mock, patch
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.ui.parameter_input import ParameterInputDialog
from src.ui.program_display import ProgramDisplayWidget
from src.ui.status_monitor import StatusMonitorWidget


class TestParameterInputDialog(unittest.TestCase):
    """参数输入对话框测试"""
    
    @classmethod
    def setUpClass(cls):
        """测试类设置"""
        cls.app = QApplication(sys.argv)
    
    def setUp(self):
        """测试前准备"""
        self.dialog = ParameterInputDialog()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.dialog)
        self.assertEqual(self.dialog.windowTitle(), "加工参数输入")
    
    def test_get_parameters(self):
        """测试获取参数"""
        parameters = self.dialog.get_parameters()
        self.assertIsInstance(parameters, dict)
        self.assertIn('basic', parameters)
        self.assertIn('geometry', parameters)
        self.assertIn('process', parameters)
        self.assertIn('material', parameters)
        self.assertIn('model', parameters)
    
    def test_set_parameters(self):
        """测试设置参数"""
        test_parameters = {
            'basic': {
                'workpiece_name': '测试工件',
                'workpiece_id': 'TEST001',
                'process_type': '铣削',
                'precision': '精密'
            },
            'geometry': {
                'length': 100.0,
                'width': 50.0,
                'height': 20.0,
                'diameter': 10.0,
                'angle': 45.0
            }
        }
        
        self.dialog.set_parameters(test_parameters)
        parameters = self.dialog.get_parameters()
        
        self.assertEqual(parameters['basic']['workpiece_name'], '测试工件')
        self.assertEqual(parameters['geometry']['length'], 100.0)
    
    def test_clear_parameters(self):
        """测试清空参数"""
        # 先设置一些参数
        test_parameters = {
            'basic': {
                'workpiece_name': '测试工件',
                'workpiece_id': 'TEST001'
            }
        }
        self.dialog.set_parameters(test_parameters)
        
        # 清空参数
        self.dialog.clear()
        
        # 验证参数已清空
        parameters = self.dialog.get_parameters()
        self.assertEqual(parameters['basic']['workpiece_name'], '')
        self.assertEqual(parameters['basic']['workpiece_id'], '')
    
    def tearDown(self):
        """测试后清理"""
        self.dialog.close()


class TestProgramDisplayWidget(unittest.TestCase):
    """程序显示组件测试"""
    
    @classmethod
    def setUpClass(cls):
        """测试类设置"""
        cls.app = QApplication(sys.argv)
    
    def setUp(self):
        """测试前准备"""
        self.widget = ProgramDisplayWidget()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.widget)
        self.assertEqual(self.widget.program_name_label.text(), "未加载程序")
        self.assertEqual(self.widget.program_size_label.text(), "0 行")
    
    def test_load_program(self):
        """测试加载程序"""
        program_name = "O1001"
        program_content = "O1001\nG90 G54 G00 X0 Y0\nM30"
        
        self.widget.load_program(program_name, program_content)
        
        self.assertEqual(self.widget.program_name_label.text(), program_name)
        self.assertEqual(self.widget.get_program_text(), program_content)
        self.assertEqual(self.widget.program_size_label.text(), "2 行")
    
    def test_set_current_line(self):
        """测试设置当前行"""
        # 先加载程序
        program_content = "O1001\nG90 G54 G00 X0 Y0\nM30"
        self.widget.load_program("O1001", program_content)
        
        # 设置当前行
        self.widget.set_current_line(1)
        self.assertEqual(self.widget.current_line_label.text(), "1")
    
    def test_clear_program(self):
        """测试清空程序"""
        # 先加载程序
        program_content = "O1001\nG90 G54 G00 X0 Y0\nM30"
        self.widget.load_program("O1001", program_content)
        
        # 清空程序
        self.widget.clear_program()
        
        # 验证程序已清空
        self.assertEqual(self.widget.program_name_label.text(), "未加载程序")
        self.assertEqual(self.widget.program_size_label.text(), "0 行")
        self.assertEqual(self.widget.get_program_text(), "")
    
    def tearDown(self):
        """测试后清理"""
        self.widget.close()


class TestStatusMonitorWidget(unittest.TestCase):
    """状态监控组件测试"""
    
    @classmethod
    def setUpClass(cls):
        """测试类设置"""
        cls.app = QApplication(sys.argv)
    
    def setUp(self):
        """测试前准备"""
        self.widget = StatusMonitorWidget()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.widget)
        self.assertEqual(self.widget.connection_label.text(), "未连接")
        self.assertFalse(self.widget.connection_status)
    
    def test_connect_disconnect(self):
        """测试连接和断开"""
        # 测试连接
        self.widget._on_connect_clicked()
        self.assertTrue(self.widget.connection_status)
        self.assertEqual(self.widget.connection_label.text(), "已连接")
        
        # 测试断开
        self.widget._on_disconnect_clicked()
        self.assertFalse(self.widget.connection_status)
        self.assertEqual(self.widget.connection_label.text(), "未连接")
    
    def test_add_error_log(self):
        """测试添加错误日志"""
        initial_row_count = self.widget.error_table.rowCount()
        
        # 添加错误日志
        self.widget.add_error_log("错误", "主轴", "温度过高")
        
        # 验证日志已添加
        self.assertEqual(self.widget.error_table.rowCount(), initial_row_count + 1)
        
        # 验证日志内容
        last_row = self.widget.error_table.rowCount() - 1
        level_item = self.widget.error_table.item(last_row, 1)
        module_item = self.widget.error_table.item(last_row, 2)
        description_item = self.widget.error_table.item(last_row, 3)
        
        self.assertEqual(level_item.text(), "错误")
        self.assertEqual(module_item.text(), "主轴")
        self.assertEqual(description_item.text(), "温度过高")
    
    def test_get_current_status(self):
        """测试获取当前状态"""
        status = self.widget.get_current_status()
        self.assertIsInstance(status, dict)
        self.assertIn("设备名称", status)
        self.assertIn("运行状态", status)
        self.assertIn("主轴转速", status)
    
    def test_get_error_log(self):
        """测试获取错误日志"""
        # 先添加一些错误日志
        self.widget.add_error_log("警告", "进给", "速度异常")
        self.widget.add_error_log("错误", "X轴", "位置偏差")
        
        error_log = self.widget.get_error_log()
        self.assertIsInstance(error_log, list)
        self.assertGreaterEqual(len(error_log), 2)
        
        # 验证日志内容
        last_log = error_log[-1]
        self.assertIn("timestamp", last_log)
        self.assertEqual(last_log["level"], "错误")
        self.assertEqual(last_log["module"], "X轴")
        self.assertEqual(last_log["description"], "位置偏差")
    
    def test_clear_status(self):
        """测试清空状态"""
        # 先连接并添加一些数据
        self.widget._on_connect_clicked()
        self.widget.add_error_log("警告", "测试", "测试错误")
        
        # 清空状态
        self.widget.clear_status()
        
        # 验证状态已清空
        self.assertFalse(self.widget.connection_status)
        self.assertEqual(self.widget.connection_label.text(), "未连接")
        self.assertEqual(self.widget.error_table.rowCount(), 0)
    
    def tearDown(self):
        """测试后清理"""
        self.widget.close()


if __name__ == '__main__':
    unittest.main()
