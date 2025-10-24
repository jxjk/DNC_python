"""
UI组件单元测试
测试各种UI控件的功能
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

from dnc_python_project.src.ui.widgets.parameter_widget import ParameterWidget
from dnc_python_project.src.ui.widgets.measure_widget import MeasureWidget
from dnc_python_project.src.ui.widgets.select_widget import SelectWidget
from dnc_python_project.src.ui.widgets.relation_widget import RelationWidget
from dnc_python_project.src.ui.widgets.switch_widget import SwitchWidget
from dnc_python_project.src.ui.widgets.correct_widget import CorrectWidget


class TestParameterWidget(unittest.TestCase):
    """ParameterWidget测试"""
    
    @classmethod
    def setUpClass(cls):
        """测试类设置"""
        cls.app = QApplication([])
        
    def setUp(self):
        """测试前准备"""
        self.parent = QWidget()
        self.widget = ParameterWidget("测试参数", "TEST_MACRO", self.parent)
        
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.widget.macro_name, "TEST_MACRO")
        self.assertEqual(self.widget.label.text(), "测试参数")
        self.assertIsNotNone(self.widget.value_edit)
        
    def test_set_value(self):
        """测试设置值"""
        self.widget.set_value("123.45")
        self.assertEqual(self.widget.value_edit.text(), "123.45")
        
    def test_get_value(self):
        """测试获取值"""
        self.widget.value_edit.setText("67.89")
        self.assertEqual(self.widget.get_value(), "67.89")
        
    def test_set_readonly(self):
        """测试设置只读"""
        self.widget.set_readonly(True)
        self.assertTrue(self.widget.value_edit.isReadOnly())
        
        self.widget.set_readonly(False)
        self.assertFalse(self.widget.value_edit.isReadOnly())
        
    def test_validation(self):
        """测试验证"""
        # 测试有效值
        self.widget.value_edit.setText("123.45")
        self.assertTrue(self.widget.validate())
        
        # 测试无效值
        self.widget.value_edit.setText("invalid")
        self.assertFalse(self.widget.validate())
        
    def test_clear(self):
        """测试清空"""
        self.widget.value_edit.setText("123.45")
        self.widget.clear()
        self.assertEqual(self.widget.value_edit.text(), "")
        
    def test_signal_emission(self):
        """测试信号发射"""
        mock_handler = Mock()
        self.widget.value_changed.connect(mock_handler)
        
        self.widget.value_edit.setText("new_value")
        QTest.keyPress(self.widget.value_edit, Qt.Key_Enter)
        
        mock_handler.assert_called_once_with("TEST_MACRO", "new_value")


class TestMeasureWidget(unittest.TestCase):
    """MeasureWidget测试"""
    
    @classmethod
    def setUpClass(cls):
        """测试类设置"""
        cls.app = QApplication([])
        
    def setUp(self):
        """测试前准备"""
        self.parent = QWidget()
        self.widget = MeasureWidget("测试测量", "MEASURE_MACRO", self.parent)
        
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.widget.macro_name, "MEASURE_MACRO")
        self.assertEqual(self.widget.label.text(), "测试测量")
        self.assertIsNotNone(self.widget.value_label)
        self.assertIsNotNone(self.widget.measure_button)
        
    def test_set_value(self):
        """测试设置值"""
        self.widget.set_value("45.67")
        self.assertEqual(self.widget.value_label.text(), "45.67")
        
    def test_get_value(self):
        """测试获取值"""
        self.widget.set_value("78.90")
        self.assertEqual(self.widget.get_value(), "78.90")
        
    def test_measure_button_click(self):
        """测试测量按钮点击"""
        mock_handler = Mock()
        self.widget.measure_requested.connect(mock_handler)
        
        QTest.mouseClick(self.widget.measure_button, Qt.LeftButton)
        
        mock_handler.assert_called_once_with("MEASURE_MACRO")
        
    def test_set_readonly(self):
        """测试设置只读"""
        self.widget.set_readonly(True)
        self.assertFalse(self.widget.measure_button.isEnabled())
        
        self.widget.set_readonly(False)
        self.assertTrue(self.widget.measure_button.isEnabled())


class TestSelectWidget(unittest.TestCase):
    """SelectWidget测试"""
    
    @classmethod
    def setUpClass(cls):
        """测试类设置"""
        cls.app = QApplication([])
        
    def setUp(self):
        """测试前准备"""
        self.parent = QWidget()
        self.widget = SelectWidget("测试选择", "SELECT_MACRO", self.parent)
        
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.widget.macro_name, "SELECT_MACRO")
        self.assertEqual(self.widget.label.text(), "测试选择")
        self.assertIsNotNone(self.widget.combo_box)
        
    def test_set_options(self):
        """测试设置选项"""
        options = ["选项1", "选项2", "选项3"]
        self.widget.set_options(options)
        
        self.assertEqual(self.widget.combo_box.count(), 3)
        self.assertEqual(self.widget.combo_box.itemText(0), "选项1")
        self.assertEqual(self.widget.combo_box.itemText(1), "选项2")
        self.assertEqual(self.widget.combo_box.itemText(2), "选项3")
        
    def test_set_value(self):
        """测试设置值"""
        options = ["选项1", "选项2", "选项3"]
        self.widget.set_options(options)
        self.widget.set_value("选项2")
        
        self.assertEqual(self.widget.combo_box.currentText(), "选项2")
        
    def test_get_value(self):
        """测试获取值"""
        options = ["选项1", "选项2", "选项3"]
        self.widget.set_options(options)
        self.widget.combo_box.setCurrentIndex(1)
        
        self.assertEqual(self.widget.get_value(), "选项2")
        
    def test_signal_emission(self):
        """测试信号发射"""
        mock_handler = Mock()
        self.widget.value_changed.connect(mock_handler)
        
        options = ["选项1", "选项2", "选项3"]
        self.widget.set_options(options)
        self.widget.combo_box.setCurrentIndex(2)
        
        mock_handler.assert_called_once_with("SELECT_MACRO", "选项3")


class TestRelationWidget(unittest.TestCase):
    """RelationWidget测试"""
    
    @classmethod
    def setUpClass(cls):
        """测试类设置"""
        cls.app = QApplication([])
        
    def setUp(self):
        """测试前准备"""
        self.parent = QWidget()
        self.widget = RelationWidget("测试关系", "RELATION_MACRO", self.parent)
        
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.widget.macro_name, "RELATION_MACRO")
        self.assertEqual(self.widget.label.text(), "测试关系")
        self.assertIsNotNone(self.widget.status_label)
        self.assertIsNotNone(self.widget.validate_button)
        
    def test_set_validation_result(self):
        """测试设置验证结果"""
        # 测试通过
        self.widget.set_validation_result(True, "验证通过")
        self.assertEqual(self.widget.status_label.text(), "✓ 验证通过")
        
        # 测试失败
        self.widget.set_validation_result(False, "验证失败")
        self.assertEqual(self.widget.status_label.text(), "✗ 验证失败")
        
    def test_validate_button_click(self):
        """测试验证按钮点击"""
        mock_handler = Mock()
        self.widget.validation_requested.connect(mock_handler)
        
        QTest.mouseClick(self.widget.validate_button, Qt.LeftButton)
        
        mock_handler.assert_called_once_with("RELATION_MACRO")


class TestSwitchWidget(unittest.TestCase):
    """SwitchWidget测试"""
    
    @classmethod
    def setUpClass(cls):
        """测试类设置"""
        cls.app = QApplication([])
        
    def setUp(self):
        """测试前准备"""
        self.parent = QWidget()
        self.widget = SwitchWidget("测试开关", "SWITCH_MACRO", self.parent)
        
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.widget.macro_name, "SWITCH_MACRO")
        self.assertEqual(self.widget.label.text(), "测试开关")
        self.assertIsNotNone(self.widget.check_box)
        
    def test_set_value(self):
        """测试设置值"""
        # 测试设置为True
        self.widget.set_value(True)
        self.assertTrue(self.widget.check_box.isChecked())
        
        # 测试设置为False
        self.widget.set_value(False)
        self.assertFalse(self.widget.check_box.isChecked())
        
    def test_get_value(self):
        """测试获取值"""
        # 测试获取True
        self.widget.check_box.setChecked(True)
        self.assertEqual(self.widget.get_value(), True)
        
        # 测试获取False
        self.widget.check_box.setChecked(False)
        self.assertEqual(self.widget.get_value(), False)
        
    def test_signal_emission(self):
        """测试信号发射"""
        mock_handler = Mock()
        self.widget.value_changed.connect(mock_handler)
        
        self.widget.check_box.setChecked(True)
        
        mock_handler.assert_called_once_with("SWITCH_MACRO", True)


class TestCorrectWidget(unittest.TestCase):
    """CorrectWidget测试"""
    
    @classmethod
    def setUpClass(cls):
        """测试类设置"""
        cls.app = QApplication([])
        
    def setUp(self):
        """测试前准备"""
        self.parent = QWidget()
        self.widget = CorrectWidget("测试修正", "CORRECT_MACRO", self.parent)
        
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.widget.macro_name, "CORRECT_MACRO")
        self.assertEqual(self.widget.label.text(), "测试修正")
        self.assertIsNotNone(self.widget.value_edit)
        self.assertIsNotNone(self.widget.correct_button)
        
    def test_set_value(self):
        """测试设置值"""
        self.widget.set_value("12.34")
        self.assertEqual(self.widget.value_edit.text(), "12.34")
        
    def test_get_value(self):
        """测试获取值"""
        self.widget.value_edit.setText("56.78")
        self.assertEqual(self.widget.get_value(), "56.78")
        
    def test_correct_button_click(self):
        """测试修正按钮点击"""
        mock_handler = Mock()
        self.widget.correction_requested.connect(mock_handler)
        
        self.widget.value_edit.setText("90.12")
        QTest.mouseClick(self.widget.correct_button, Qt.LeftButton)
        
        mock_handler.assert_called_once_with("CORRECT_MACRO", "90.12")
        
    def test_validation(self):
        """测试验证"""
        # 测试有效值
        self.widget.value_edit.setText("123.45")
        self.assertTrue(self.widget.validate())
        
        # 测试无效值
        self.widget.value_edit.setText("invalid")
        self.assertFalse(self.widget.validate())


class TestWidgetIntegration(unittest.TestCase):
    """组件集成测试"""
    
    @classmethod
    def setUpClass(cls):
        """测试类设置"""
        cls.app = QApplication([])
        
    def test_widget_properties(self):
        """测试组件属性"""
        parent = QWidget()
        
        widgets = [
            ParameterWidget("参数", "PARAM_MACRO", parent),
            MeasureWidget("测量", "MEASURE_MACRO", parent),
            SelectWidget("选择", "SELECT_MACRO", parent),
            RelationWidget("关系", "RELATION_MACRO", parent),
            SwitchWidget("开关", "SWITCH_MACRO", parent),
            CorrectWidget("修正", "CORRECT_MACRO", parent)
        ]
        
        for widget in widgets:
            with self.subTest(widget_type=type(widget).__name__):
                # 验证基本属性
                self.assertIsNotNone(widget.macro_name)
                self.assertIsNotNone(widget.label)
                
                # 验证值操作
                widget.set_value("test_value")
                returned_value = widget.get_value()
                self.assertIsNotNone(returned_value)
                
                # 验证只读设置
                widget.set_readonly(True)
                widget.set_readonly(False)
                
    def test_widget_signals(self):
        """测试组件信号"""
        parent = QWidget()
        
        # 测试参数控件信号
        param_widget = ParameterWidget("参数", "PARAM_MACRO", parent)
        param_handler = Mock()
        param_widget.value_changed.connect(param_handler)
        
        param_widget.value_edit.setText("new_param")
        QTest.keyPress(param_widget.value_edit, Qt.Key_Enter)
        param_handler.assert_called_once_with("PARAM_MACRO", "new_param")
        
        # 测试选择控件信号
        select_widget = SelectWidget("选择", "SELECT_MACRO", parent)
        select_handler = Mock()
        select_widget.value_changed.connect(select_handler)
        
        select_widget.set_options(["A", "B", "C"])
        select_widget.combo_box.setCurrentIndex(1)
        select_handler.assert_called_once_with("SELECT_MACRO", "B")
        
        # 测试开关控件信号
        switch_widget = SwitchWidget("开关", "SWITCH_MACRO", parent)
        switch_handler = Mock()
        switch_widget.value_changed.connect(switch_handler)
        
        switch_widget.check_box.setChecked(True)
        switch_handler.assert_called_once_with("SWITCH_MACRO", True)


if __name__ == '__main__':
    unittest.main()
