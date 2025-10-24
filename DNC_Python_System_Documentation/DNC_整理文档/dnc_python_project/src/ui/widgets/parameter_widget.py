"""
参数输入控件
用于显示和编辑参数值
"""

from typing import Optional, Callable
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QDoubleSpinBox
from PyQt5.QtCore import pyqtSignal, Qt


class ParameterWidget(QWidget):
    """参数控件基类"""
    
    value_changed = pyqtSignal(str, object)  # macro, value
    
    def __init__(self, macro: str, description: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.macro = macro
        self.description = description
        self._value = None
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 标签
        self.label = QLabel(f"{self.description}:")
        self.label.setMinimumWidth(120)
        layout.addWidget(self.label)
        
        # 值显示/编辑控件
        self.value_widget = self.create_value_widget()
        layout.addWidget(self.value_widget)
        
        layout.addStretch()
    
    def create_value_widget(self) -> QWidget:
        """创建值控件（子类重写）"""
        return QLabel("待计算")
    
    def set_value(self, value):
        """设置值"""
        self._value = value
        self.update_display()
    
    def get_value(self):
        """获取值"""
        return self._value
    
    def update_display(self):
        """更新显示（子类重写）"""
        pass
    
    def set_readonly(self, readonly: bool):
        """设置只读状态"""
        pass


class LoadWidget(ParameterWidget):
    """只读显示控件"""
    
    def create_value_widget(self) -> QWidget:
        return QLabel("待计算")
    
    def update_display(self):
        if self._value is not None:
            self.value_widget.setText(str(self._value))
        else:
            self.value_widget.setText("待计算")


class InputWidget(ParameterWidget):
    """输入控件"""
    
    def create_value_widget(self) -> QWidget:
        self.spin_box = QDoubleSpinBox()
        self.spin_box.setMinimum(0)
        self.spin_box.setMaximum(10000)
        self.spin_box.setDecimals(2)
        self.spin_box.valueChanged.connect(self.on_value_changed)
        return self.spin_box
    
    def update_display(self):
        if self._value is not None:
            self.spin_box.setValue(float(self._value))
    
    def on_value_changed(self, value):
        self._value = value
        self.value_changed.emit(self.macro, value)
    
    def set_readonly(self, readonly: bool):
        self.spin_box.setReadOnly(readonly)


class MeasureWidget(ParameterWidget):
    """测量控件"""
    
    def create_value_widget(self) -> QWidget:
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("输入测量值")
        self.line_edit.textChanged.connect(self.on_text_changed)
        return self.line_edit
    
    def update_display(self):
        if self._value is not None:
            self.line_edit.setText(str(self._value))
        else:
            self.line_edit.clear()
    
    def on_text_changed(self, text):
        try:
            value = float(text) if text else None
            self._value = value
            self.value_changed.emit(self.macro, value)
        except ValueError:
            pass
    
    def set_readonly(self, readonly: bool):
        self.line_edit.setReadOnly(readonly)
