import sys
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, 
                            QLabel, QLineEdit, QComboBox, QDoubleSpinBox,
                            QPushButton, QFormLayout, QTextEdit)
from PyQt5.QtCore import pyqtSignal, Qt
from typing import Dict, Any, Optional


class ParameterInputDialog(QDialog):
    """参数输入对话框"""
    
    # 信号定义
    parameters_changed = pyqtSignal(dict)
    model_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_model = None
        self._init_ui()
        self._connect_signals()
    
    def _init_ui(self) -> None:
        """初始化用户界面"""
        self.setWindowTitle("加工参数输入")
        self.setMinimumSize(600, 700)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        
        # 基本信息组
        basic_group = self._create_basic_group()
        main_layout.addWidget(basic_group)
        
        # 几何参数组
        geometry_group = self._create_geometry_group()
        main_layout.addWidget(geometry_group)
        
        # 工艺参数组
        process_group = self._create_process_group()
        main_layout.addWidget(process_group)
        
        # 材料参数组
        material_group = self._create_material_group()
        main_layout.addWidget(material_group)
        
        # 型号信息组
        model_group = self._create_model_group()
        main_layout.addWidget(model_group)
        
        # 按钮组
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("确定")
        self.cancel_button = QPushButton("取消")
        self.clear_button = QPushButton("清空")
        
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        
        main_layout.addLayout(button_layout)
    
    def _create_basic_group(self) -> QGroupBox:
        """创建基本信息组"""
        group = QGroupBox("基本信息")
        layout = QFormLayout()
        
        self.workpiece_name = QLineEdit()
        self.workpiece_id = QLineEdit()
        self.process_type = QComboBox()
        self.precision = QComboBox()
        
        # 添加选项
        self.process_type.addItems(["铣削", "车削", "钻孔", "磨削"])
        self.precision.addItems(["普通", "精密", "高精密"])
        
        layout.addRow("工件名称:", self.workpiece_name)
        layout.addRow("工件编号:", self.workpiece_id)
        layout.addRow("加工类型:", self.process_type)
        layout.addRow("精度要求:", self.precision)
        
        group.setLayout(layout)
        return group
    
    def _create_geometry_group(self) -> QGroupBox:
        """创建几何参数组"""
        group = QGroupBox("几何参数 (mm)")
        layout = QFormLayout()
        
        self.length = QDoubleSpinBox()
        self.width = QDoubleSpinBox()
        self.height = QDoubleSpinBox()
        self.diameter = QDoubleSpinBox()
        self.angle = QDoubleSpinBox()
        
        # 设置范围
        for spinbox in [self.length, self.width, self.height, self.diameter]:
            spinbox.setRange(0, 10000)
            spinbox.setDecimals(2)
        
        self.angle.setRange(0, 360)
        self.angle.setDecimals(1)
        
        layout.addRow("长度:", self.length)
        layout.addRow("宽度:", self.width)
        layout.addRow("高度:", self.height)
        layout.addRow("直径:", self.diameter)
        layout.addRow("角度:", self.angle)
        
        group.setLayout(layout)
        return group
    
    def _create_process_group(self) -> QGroupBox:
        """创建工艺参数组"""
        group = QGroupBox("工艺参数")
        layout = QFormLayout()
        
        self.spindle_speed = QDoubleSpinBox()
        self.feed_rate = QDoubleSpinBox()
        self.cut_depth = QDoubleSpinBox()
        self.cut_width = QDoubleSpinBox()
        
        # 设置范围
        self.spindle_speed.setRange(0, 10000)
        self.spindle_speed.setSuffix(" rpm")
        
        self.feed_rate.setRange(0, 5000)
        self.feed_rate.setSuffix(" mm/min")
        
        self.cut_depth.setRange(0, 50)
        self.cut_depth.setDecimals(2)
        self.cut_depth.setSuffix(" mm")
        
        self.cut_width.setRange(0, 20)
        self.cut_width.setDecimals(2)
        self.cut_width.setSuffix(" mm")
        
        layout.addRow("主轴转速:", self.spindle_speed)
        layout.addRow("进给速度:", self.feed_rate)
        layout.addRow("切削深度:", self.cut_depth)
        layout.addRow("切削宽度:", self.cut_width)
        
        group.setLayout(layout)
        return group
    
    def _create_material_group(self) -> QGroupBox:
        """创建材料参数组"""
        group = QGroupBox("材料参数")
        layout = QFormLayout()
        
        self.material_type = QComboBox()
        self.material_hardness = QComboBox()
        self.material_strength = QDoubleSpinBox()
        
        # 添加选项
        self.material_type.addItems(["碳钢", "不锈钢", "铝合金", "铜合金", "钛合金"])
        self.material_hardness.addItems(["软", "中等", "硬", "超硬"])
        
        self.material_strength.setRange(0, 2000)
        self.material_strength.setSuffix(" MPa")
        
        layout.addRow("材料类型:", self.material_type)
        layout.addRow("材料硬度:", self.material_hardness)
        layout.addRow("材料强度:", self.material_strength)
        
        group.setLayout(layout)
        return group
    
    def _create_model_group(self) -> QGroupBox:
        """创建型号信息组"""
        group = QGroupBox("设备型号")
        layout = QVBoxLayout()
        
        model_layout = QHBoxLayout()
        self.model_combo = QComboBox()
        self.model_combo.addItems(["自动识别", "手动选择", "自定义输入"])
        
        self.model_description = QTextEdit()
        self.model_description.setMaximumHeight(80)
        self.model_description.setPlaceholderText("请选择或输入型号")
        
        model_layout.addWidget(QLabel("型号选择:"))
        model_layout.addWidget(self.model_combo)
        
        layout.addLayout(model_layout)
        layout.addWidget(QLabel("型号描述:"))
        layout.addWidget(self.model_description)
        
        group.setLayout(layout)
        return group
    
    def _connect_signals(self) -> None:
        """连接信号和槽"""
        self.ok_button.clicked.connect(self._on_ok_clicked)
        self.cancel_button.clicked.connect(self.reject)
        self.clear_button.clicked.connect(self.clear)
        
        # 连接参数变化信号
        self.model_combo.currentTextChanged.connect(self._on_model_changed)
    
    def _on_ok_clicked(self) -> None:
        """确定按钮点击处理"""
        parameters = self.get_parameters()
        self.parameters_changed.emit(parameters)
        self.accept()
    
    def _on_model_changed(self, model: str) -> None:
        """型号变化处理"""
        self.current_model = model
        self.model_changed.emit(model)
    
    def get_parameters(self) -> Dict[str, Any]:
        """获取所有参数"""
        return {
            "basic": {
                "workpiece_name": self.workpiece_name.text(),
                "workpiece_id": self.workpiece_id.text(),
                "process_type": self.process_type.currentText(),
                "precision": self.precision.currentText()
            },
            "geometry": {
                "length": self.length.value(),
                "width": self.width.value(),
                "height": self.height.value(),
                "diameter": self.diameter.value(),
                "angle": self.angle.value()
            },
            "process": {
                "spindle_speed": self.spindle_speed.value(),
                "feed_rate": self.feed_rate.value(),
                "cut_depth": self.cut_depth.value(),
                "cut_width": self.cut_width.value()
            },
            "material": {
                "material_type": self.material_type.currentText(),
                "material_hardness": self.material_hardness.currentText(),
                "material_strength": self.material_strength.value()
            },
            "model": {
                "model_type": self.model_combo.currentText(),
                "model_description": self.model_description.toPlainText(),
                "current_model": self.current_model
            }
        }
    
    def set_parameters(self, parameters: Dict[str, Any]) -> None:
        """设置参数"""
        if not parameters:
            return
        
        # 阻塞信号，避免触发变化事件
        self.blockSignals(True)
        
        try:
            # 设置基本参数
            if "basic" in parameters:
                basic = parameters["basic"]
                self.workpiece_name.setText(basic.get("workpiece_name", ""))
                self.workpiece_id.setText(basic.get("workpiece_id", ""))
                self._set_combo_text(self.process_type, basic.get("process_type"))
                self._set_combo_text(self.precision, basic.get("precision"))
            
            # 设置几何参数
            if "geometry" in parameters:
                geometry = parameters["geometry"]
                self.length.setValue(geometry.get("length", 0))
                self.width.setValue(geometry.get("width", 0))
                self.height.setValue(geometry.get("height", 0))
                self.diameter.setValue(geometry.get("diameter", 0))
                self.angle.setValue(geometry.get("angle", 0))
            
            # 设置工艺参数
            if "process" in parameters:
                process = parameters["process"]
                self.spindle_speed.setValue(process.get("spindle_speed", 0))
                self.feed_rate.setValue(process.get("feed_rate", 0))
                self.cut_depth.setValue(process.get("cut_depth", 0))
                self.cut_width.setValue(process.get("cut_width", 0))
            
            # 设置材料参数
            if "material" in parameters:
                material = parameters["material"]
                self._set_combo_text(self.material_type, material.get("material_type"))
                self._set_combo_text(self.material_hardness, material.get("material_hardness"))
                self.material_strength.setValue(material.get("material_strength", 0))
            
            # 设置型号信息
            if "model" in parameters:
                model = parameters["model"]
                self._set_combo_text(self.model_combo, model.get("model_type"))
                self.model_description.setPlainText(model.get("model_description", ""))
                self.current_model = model.get("current_model")
                
        finally:
            self.blockSignals(False)
    
    def _set_combo_text(self, combo: QComboBox, text: Optional[str]) -> None:
        """设置组合框文本"""
        if text:
            index = combo.findText(text)
            if index >= 0:
                combo.setCurrentIndex(index)
            else:
                combo.setCurrentIndex(0)
    
    def clear(self) -> None:
        """清空所有参数"""
        # 阻塞信号，避免触发变化事件
        self.blockSignals(True)
        
        try:
            # 清空基本参数
            self.workpiece_name.clear()
            self.workpiece_id.clear()
            self.process_type.setCurrentIndex(0)
            self.precision.setCurrentIndex(0)
            
            # 清空几何参数
            self.length.setValue(0)
            self.width.setValue(0)
            self.height.setValue(0)
            self.diameter.setValue(0)
            self.angle.setValue(0)
            
            # 清空工艺参数
            self.spindle_speed.setValue(0)
            self.feed_rate.setValue(0)
            self.cut_depth.setValue(0)
            self.cut_width.setValue(0)
            
            # 清空材料参数
            self.material_type.setCurrentIndex(0)
            self.material_hardness.setCurrentIndex(0)
            self.material_strength.setValue(0)
            
            # 清空型号信息
            self.model_combo.setCurrentIndex(0)
            self.model_description.setText("请选择或输入型号")
            self.current_model = None
            
        finally:
            self.blockSignals(False)


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = ParameterInputDialog()
    dialog.show()
    sys.exit(app.exec_())
