"""
测量控件模块
提供测量相关的UI控件
"""

from typing import Optional, Callable
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import pyqtSignal, Qt


class MeasureWidget(QWidget):
    """
    测量控件
    用于显示和编辑测量参数
    """
    
    value_changed = pyqtSignal(str, float)
    
    def __init__(self, parameter_name: str, default_value: float = 0.0, 
                 unit: str = "mm", parent: Optional[QWidget] = None):
        """
        初始化测量控件
        
        Args:
            parameter_name: 参数名称
            default_value: 默认值
            unit: 单位
            parent: 父控件
        """
        super().__init__(parent)
        
        self.parameter_name = parameter_name
        self.default_value = default_value
        self.unit = unit
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self) -> None:
        """设置UI界面"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 参数名称标签
        self.name_label = QLabel(f"{self.parameter_name}:")
        self.name_label.setMinimumWidth(80)
        layout.addWidget(self.name_label)
        
        # 值输入框
        self.value_edit = QLineEdit()
        self.value_edit.setText(str(self.default_value))
        self.value_edit.setPlaceholderText("输入测量值")
        self.value_edit.setMaximumWidth(100)
        layout.addWidget(self.value_edit)
        
        # 单位标签
        self.unit_label = QLabel(self.unit)
        self.unit_label.setMinimumWidth(30)
        layout.addWidget(self.unit_label)
        
        # 测量按钮
        self.measure_button = QPushButton("测量")
        self.measure_button.setMaximumWidth(60)
        layout.addWidget(self.measure_button)
        
        layout.addStretch()
    
    def _connect_signals(self) -> None:
        """连接信号"""
        self.value_edit.textChanged.connect(self._on_value_changed)
        self.measure_button.clicked.connect(self._on_measure_clicked)
    
    def _on_value_changed(self, text: str) -> None:
        """值改变时的处理"""
        try:
            value = float(text)
            self.value_changed.emit(self.parameter_name, value)
        except ValueError:
            # 输入无效时忽略
            pass
    
    def _on_measure_clicked(self) -> None:
        """测量按钮点击处理"""
        # 这里可以添加实际的测量逻辑
        # 暂时模拟测量结果
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "测量", f"正在测量 {self.parameter_name}...")
    
    def get_value(self) -> float:
        """
        获取当前值
        
        Returns:
            float: 当前值
        """
        try:
            return float(self.value_edit.text())
        except ValueError:
            return self.default_value
    
    def set_value(self, value: float) -> None:
        """
        设置值
        
        Args:
            value: 要设置的值
        """
        self.value_edit.setText(str(value))
    
    def set_read_only(self, read_only: bool) -> None:
        """
        设置只读模式
        
        Args:
            read_only: 是否只读
        """
        self.value_edit.setReadOnly(read_only)
        self.measure_button.setEnabled(not read_only)
    
    def set_unit(self, unit: str) -> None:
        """
        设置单位
        
        Args:
            unit: 单位
        """
        self.unit = unit
        self.unit_label.setText(unit)
    
    def reset(self) -> None:
        """重置为默认值"""
        self.value_edit.setText(str(self.default_value))


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget
    
    def on_value_changed(name: str, value: float):
        print(f"参数 {name} 值改变为: {value}")
    
    app = QApplication(sys.argv)
    
    window = QWidget()
    layout = QVBoxLayout(window)
    
    # 创建测量控件示例
    measure_widget1 = MeasureWidget("长度", 100.0, "mm")
    measure_widget1.value_changed.connect(on_value_changed)
    layout.addWidget(measure_widget1)
    
    measure_widget2 = MeasureWidget("直径", 50.0, "mm")
    measure_widget2.value_changed.connect(on_value_changed)
    layout.addWidget(measure_widget2)
    
    measure_widget3 = MeasureWidget("角度", 90.0, "°")
    measure_widget3.value_changed.connect(on_value_changed)
    layout.addWidget(measure_widget3)
    
    window.setWindowTitle("测量控件示例")
    window.resize(400, 200)
    window.show()
    
    sys.exit(app.exec_())
