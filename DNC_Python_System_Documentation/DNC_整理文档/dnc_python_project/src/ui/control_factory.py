"""
控件工厂模块
根据配置创建不同类型的UI控件
"""

from typing import Dict, Any, Optional, List
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QCheckBox, QPushButton, QSpinBox, QDoubleSpinBox,
    QScrollArea, QGroupBox, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from src.utils.logger import get_logger


class ControlFactory:
    """控件工厂类"""
    
    def __init__(self):
        """初始化控件工厂"""
        self.logger = get_logger(__name__)
        self._control_cache = {}
    
    def create_control(self, control_config: Dict[str, Any], parent: Optional[QWidget] = None) -> QWidget:
        """
        根据配置创建控件
        
        Args:
            control_config: 控件配置字典
            parent: 父控件
            
        Returns:
            QWidget: 创建的控件
        """
        try:
            control_type = control_config.get('KIND', '').lower()
            macro_name = control_config.get('MACRO', '')
            
            self.logger.debug(f"创建控件: {macro_name}, 类型: {control_type}")
            
            if control_type == 'load':
                return self._create_load_control(control_config, parent)
            elif control_type == 'input':
                return self._create_input_control(control_config, parent)
            elif control_type == 'measure':
                return self._create_measure_control(control_config, parent)
            elif control_type == 'select':
                return self._create_select_control(control_config, parent)
            elif control_type == 'relation':
                return self._create_relation_control(control_config, parent)
            elif control_type == 'switch':
                return self._create_switch_control(control_config, parent)
            elif control_type == 'correct':
                return self._create_correct_control(control_config, parent)
            else:
                self.logger.warning(f"未知的控件类型: {control_type}")
                return self._create_default_control(control_config, parent)
                
        except Exception as e:
            self.logger.error(f"创建控件失败: {e}")
            return self._create_error_control(f"创建控件失败: {str(e)}", parent)
    
    def _create_load_control(self, config: Dict[str, Any], parent: Optional[QWidget] = None) -> QWidget:
        """
        创建只读显示控件
        
        Args:
            config: 控件配置
            parent: 父控件
            
        Returns:
            QWidget: 创建的控件
        """
        widget = QWidget(parent)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        
        macro_name = config.get('MACRO', '未知')
        label_text = f"{macro_name}:"
        
        label = QLabel(label_text, widget)
        label.setMinimumWidth(120)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        value_label = QLabel("待计算", widget)
        value_label.setMinimumWidth(100)
        value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        value_label.setStyleSheet("QLabel { background-color: #f0f0f0; border: 1px solid #ccc; padding: 2px; }")
        
        # 设置控件属性
        value_label.setProperty("control_type", "load")
        value_label.setProperty("macro_name", macro_name)
        
        layout.addWidget(label)
        layout.addWidget(value_label)
        layout.addStretch()
        
        return widget
    
    def _create_input_control(self, config: Dict[str, Any], parent: Optional[QWidget] = None) -> QWidget:
        """
        创建输入控件
        
        Args:
            config: 控件配置
            parent: 父控件
            
        Returns:
            QWidget: 创建的控件
        """
        widget = QWidget(parent)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        
        macro_name = config.get('MACRO', '未知')
        label_text = f"{macro_name}:"
        
        label = QLabel(label_text, widget)
        label.setMinimumWidth(120)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        input_field = QLineEdit(widget)
        input_field.setMinimumWidth(100)
        input_field.setPlaceholderText("请输入数值")
        
        # 设置控件属性
        input_field.setProperty("control_type", "input")
        input_field.setProperty("macro_name", macro_name)
        
        layout.addWidget(label)
        layout.addWidget(input_field)
        layout.addStretch()
        
        return widget
    
    def _create_measure_control(self, config: Dict[str, Any], parent: Optional[QWidget] = None) -> QWidget:
        """
        创建测量控件
        
        Args:
            config: 控件配置
            parent: 父控件
            
        Returns:
            QWidget: 创建的控件
        """
        widget = QWidget(parent)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        
        macro_name = config.get('MACRO', '未知')
        label_text = f"{macro_name}:"
        
        label = QLabel(label_text, widget)
        label.setMinimumWidth(120)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        value_label = QLabel("待测量", widget)
        value_label.setMinimumWidth(100)
        value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        value_label.setStyleSheet("QLabel { background-color: #fff8dc; border: 1px solid #ccc; padding: 2px; }")
        
        measure_button = QPushButton("测量", widget)
        measure_button.setFixedWidth(60)
        
        # 设置控件属性
        value_label.setProperty("control_type", "measure")
        value_label.setProperty("macro_name", macro_name)
        measure_button.setProperty("control_type", "measure_button")
        measure_button.setProperty("macro_name", macro_name)
        
        layout.addWidget(label)
        layout.addWidget(value_label)
        layout.addWidget(measure_button)
        layout.addStretch()
        
        return widget
    
    def _create_select_control(self, config: Dict[str, Any], parent: Optional[QWidget] = None) -> QWidget:
        """
        创建选择控件
        
        Args:
            config: 控件配置
            parent: 父控件
            
        Returns:
            QWidget: 创建的控件
        """
        widget = QWidget(parent)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        
        macro_name = config.get('MACRO', '未知')
        label_text = f"{macro_name}:"
        
        label = QLabel(label_text, widget)
        label.setMinimumWidth(120)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        combo_box = QComboBox(widget)
        combo_box.setMinimumWidth(120)
        
        # 添加默认选项
        combo_box.addItem("请选择")
        combo_box.addItem("选项1")
        combo_box.addItem("选项2")
        combo_box.addItem("选项3")
        
        # 设置控件属性
        combo_box.setProperty("control_type", "select")
        combo_box.setProperty("macro_name", macro_name)
        
        layout.addWidget(label)
        layout.addWidget(combo_box)
        layout.addStretch()
        
        return widget
    
    def _create_relation_control(self, config: Dict[str, Any], parent: Optional[QWidget] = None) -> QWidget:
        """
        创建关系验证控件
        
        Args:
            config: 控件配置
            parent: 父控件
            
        Returns:
            QWidget: 创建的控件
        """
        widget = QWidget(parent)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        
        macro_name = config.get('MACRO', '未知')
        label_text = f"{macro_name}:"
        
        label = QLabel(label_text, widget)
        label.setMinimumWidth(120)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        value_label = QLabel("待验证", widget)
        value_label.setMinimumWidth(100)
        value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        value_label.setStyleSheet("QLabel { background-color: #f0f8ff; border: 1px solid #ccc; padding: 2px; }")
        
        validate_button = QPushButton("验证", widget)
        validate_button.setFixedWidth(60)
        
        # 设置控件属性
        value_label.setProperty("control_type", "relation")
        value_label.setProperty("macro_name", macro_name)
        validate_button.setProperty("control_type", "relation_button")
        validate_button.setProperty("macro_name", macro_name)
        
        layout.addWidget(label)
        layout.addWidget(value_label)
        layout.addWidget(validate_button)
        layout.addStretch()
        
        return widget
    
    def _create_switch_control(self, config: Dict[str, Any], parent: Optional[QWidget] = None) -> QWidget:
        """
        创建开关控件
        
        Args:
            config: 控件配置
            parent: 父控件
            
        Returns:
            QWidget: 创建的控件
        """
        widget = QWidget(parent)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        
        macro_name = config.get('MACRO', '未知')
        label_text = f"{macro_name}:"
        
        label = QLabel(label_text, widget)
        label.setMinimumWidth(120)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        check_box = QCheckBox("启用", widget)
        
        # 设置控件属性
        check_box.setProperty("control_type", "switch")
        check_box.setProperty("macro_name", macro_name)
        
        layout.addWidget(label)
        layout.addWidget(check_box)
        layout.addStretch()
        
        return widget
    
    def _create_correct_control(self, config: Dict[str, Any], parent: Optional[QWidget] = None) -> QWidget:
        """
        创建修正控件
        
        Args:
            config: 控件配置
            parent: 父控件
            
        Returns:
            QWidget: 创建的控件
        """
        widget = QWidget(parent)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        
        macro_name = config.get('MACRO', '未知')
        label_text = f"{macro_name}:"
        
        label = QLabel(label_text, widget)
        label.setMinimumWidth(120)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        value_label = QLabel("待修正", widget)
        value_label.setMinimumWidth(100)
        value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        value_label.setStyleSheet("QLabel { background-color: #fff0f5; border: 1px solid #ccc; padding: 2px; }")
        
        correct_button = QPushButton("修正", widget)
        correct_button.setFixedWidth(60)
        
        # 设置控件属性
        value_label.setProperty("control_type", "correct")
        value_label.setProperty("macro_name", macro_name)
        correct_button.setProperty("control_type", "correct_button")
        correct_button.setProperty("macro_name", macro_name)
        
        layout.addWidget(label)
        layout.addWidget(value_label)
        layout.addWidget(correct_button)
        layout.addStretch()
        
        return widget
    
    def _create_default_control(self, config: Dict[str, Any], parent: Optional[QWidget] = None) -> QWidget:
        """
        创建默认控件
        
        Args:
            config: 控件配置
            parent: 父控件
            
        Returns:
            QWidget: 创建的控件
        """
        widget = QWidget(parent)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        
        macro_name = config.get('MACRO', '未知')
        control_type = config.get('KIND', '未知')
        label_text = f"{macro_name} ({control_type}):"
        
        label = QLabel(label_text, widget)
        label.setMinimumWidth(150)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        value_label = QLabel("未实现", widget)
        value_label.setMinimumWidth(100)
        value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        value_label.setStyleSheet("QLabel { background-color: #ffebee; border: 1px solid #ccc; padding: 2px; }")
        
        # 设置控件属性
        value_label.setProperty("control_type", "default")
        value_label.setProperty("macro_name", macro_name)
        
        layout.addWidget(label)
        layout.addWidget(value_label)
        layout.addStretch()
        
        return widget
    
    def _create_error_control(self, error_message: str, parent: Optional[QWidget] = None) -> QWidget:
        """
        创建错误显示控件
        
        Args:
            error_message: 错误消息
            parent: 父控件
            
        Returns:
            QWidget: 创建的控件
        """
        widget = QWidget(parent)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        
        label = QLabel("错误:", widget)
        label.setMinimumWidth(120)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        error_label = QLabel(error_message, widget)
        error_label.setStyleSheet("QLabel { color: red; background-color: #ffebee; border: 1px solid #f44336; padding: 2px; }")
        
        layout.addWidget(label)
        layout.addWidget(error_label)
        layout.addStretch()
        
        return widget
    
    def create_parameter_group(self, title: str, controls: List[QWidget], parent: Optional[QWidget] = None) -> QGroupBox:
        """
        创建参数组
        
        Args:
            title: 组标题
            controls: 控件列表
            parent: 父控件
            
        Returns:
            QGroupBox: 创建的参数组
        """
        group_box = QGroupBox(title, parent)
        layout = QVBoxLayout(group_box)
        
        for control in controls:
            layout.addWidget(control)
        
        layout.addStretch()
        return group_box
    
    def clear_cache(self) -> None:
        """清空控件缓存"""
        self._control_cache.clear()


# 全局控件工厂实例
_global_control_factory: Optional[ControlFactory] = None


def get_global_control_factory() -> ControlFactory:
    """
    获取全局控件工厂实例
    
    Returns:
        ControlFactory: 全局控件工厂实例
    """
    global _global_control_factory
    if _global_control_factory is None:
        _global_control_factory = ControlFactory()
    return _global_control_factory
