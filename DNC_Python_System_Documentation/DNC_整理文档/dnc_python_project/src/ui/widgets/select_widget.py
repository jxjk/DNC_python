"""
选择控件
用于从预定义选项中选择值
"""

from typing import Optional, List, Dict
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox
from PyQt5.QtCore import pyqtSignal


class SelectWidget(QWidget):
    """选择控件"""
    
    value_changed = pyqtSignal(str, object)  # macro, value
    
    def __init__(self, macro: str, description: str, options: List[Dict], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.macro = macro
        self.description = description
        self.options = options
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
        
        # 下拉选择框
        self.combo_box = QComboBox()
        self.populate_options()
        self.combo_box.currentTextChanged.connect(self.on_selection_changed)
        layout.addWidget(self.combo_box)
        
        layout.addStretch()
    
    def populate_options(self):
        """填充选项"""
        self.combo_box.clear()
        self.combo_box.addItem("请选择", None)
        
        for option in self.options:
            display_text = option.get('display', option.get('value', ''))
            value = option.get('value', '')
            self.combo_box.addItem(display_text, value)
    
    def on_selection_changed(self, text):
        """选择改变事件"""
        value = self.combo_box.currentData()
        self._value = value
        self.value_changed.emit(self.macro, value)
    
    def set_value(self, value):
        """设置值"""
        self._value = value
        for i in range(self.combo_box.count()):
            if self.combo_box.itemData(i) == value:
                self.combo_box.setCurrentIndex(i)
                break
    
    def get_value(self):
        """获取值"""
        return self._value
    
    def set_readonly(self, readonly: bool):
        """设置只读状态"""
        self.combo_box.setEnabled(not readonly)
