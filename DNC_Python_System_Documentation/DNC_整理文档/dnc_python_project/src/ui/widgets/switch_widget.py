"""
开关控件
用于布尔值的开关选择
"""

from typing import Optional
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QCheckBox
from PyQt5.QtCore import pyqtSignal


class SwitchWidget(QWidget):
    """开关控件"""
    
    value_changed = pyqtSignal(str, object)  # macro, value
    
    def __init__(self, macro: str, description: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.macro = macro
        self.description = description
        self._value = False
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 标签
        self.label = QLabel(f"{self.description}:")
        self.label.setMinimumWidth(120)
        layout.addWidget(self.label)
        
        # 复选框
        self.check_box = QCheckBox("启用")
        self.check_box.stateChanged.connect(self.on_state_changed)
        layout.addWidget(self.check_box)
        
        layout.addStretch()
    
    def on_state_changed(self, state):
        """状态改变事件"""
        self._value = (state == 2)  # Qt.Checked = 2
        self.value_changed.emit(self.macro, self._value)
    
    def set_value(self, value):
        """设置值"""
        if isinstance(value, bool):
            self._value = value
        elif isinstance(value, str):
            self._value = value.lower() in ('true', '1', 'yes', 'on')
        else:
            self._value = bool(value)
        
        self.check_box.setChecked(self._value)
    
    def get_value(self):
        """获取值"""
        return self._value
    
    def set_readonly(self, readonly: bool):
        """设置只读状态"""
        self.check_box.setEnabled(not readonly)
