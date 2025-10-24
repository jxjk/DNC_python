"""
修正控件
用于参数修正和补偿
"""

from typing import Optional
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QDoubleSpinBox, QPushButton
from PyQt5.QtCore import pyqtSignal


class CorrectWidget(QWidget):
    """修正控件"""
    
    value_changed = pyqtSignal(str, object)  # macro, value
    
    def __init__(self, macro: str, description: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.macro = macro
        self.description = description
        self._value = 0.0
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 标签
        self.label = QLabel(f"{self.description}:")
        self.label.setMinimumWidth(120)
        layout.addWidget(self.label)
        
        # 修正值输入框
        self.spin_box = QDoubleSpinBox()
        self.spin_box.setMinimum(-100)
        self.spin_box.setMaximum(100)
        self.spin_box.setDecimals(3)
        self.spin_box.setSuffix(" mm")
        self.spin_box.valueChanged.connect(self.on_value_changed)
        layout.addWidget(self.spin_box)
        
        # 重置按钮
        self.reset_button = QPushButton("重置")
        self.reset_button.clicked.connect(self.on_reset_clicked)
        layout.addWidget(self.reset_button)
        
        layout.addStretch()
    
    def on_value_changed(self, value):
        """值改变事件"""
        self._value = value
        self.value_changed.emit(self.macro, value)
    
    def on_reset_clicked(self):
        """重置按钮点击事件"""
        self.spin_box.setValue(0.0)
    
    def set_value(self, value):
        """设置值"""
        try:
            self._value = float(value) if value is not None else 0.0
            self.spin_box.setValue(self._value)
        except (ValueError, TypeError):
            self._value = 0.0
            self.spin_box.setValue(0.0)
    
    def get_value(self):
        """获取值"""
        return self._value
    
    def set_readonly(self, readonly: bool):
        """设置只读状态"""
        self.spin_box.setReadOnly(readonly)
        self.reset_button.setEnabled(not readonly)
