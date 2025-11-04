# dynamic_loader.py
"""
动态界面加载模块
根据load.csv和cntrl.csv文件动态生成界面控件
"""

import os
import csv
from typing import Dict, List, Any, Optional
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                            QLabel, QLineEdit, QComboBox, QDoubleSpinBox,
                            QPushButton, QFormLayout, QCheckBox, QSpinBox)
from PyQt5.QtCore import pyqtSignal, Qt
import logging


class DynamicControlLoader:
    """动态控件加载器"""
    
    def __init__(self, config_dir: str):
        """
        初始化动态控件加载器
        
        Args:
            config_dir: 配置文件目录路径
        """
        self.config_dir = config_dir
        self.load_data = []
        self.cntrl_data = []
        self.logger = logging.getLogger(__name__)
        
    def load_config_files(self) -> bool:
        """加载配置文件"""
        try:
            # 加载load.csv
            load_path = os.path.join(self.config_dir, "load.csv")
            if os.path.exists(load_path):
                with open(load_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    self.load_data = list(reader)
            
            # 加载cntrl.csv
            cntrl_path = os.path.join(self.config_dir, "cntrl.csv")
            if os.path.exists(cntrl_path):
                with open(cntrl_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    self.cntrl_data = list(reader)
            
            return True
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {e}")
            return False
    
    def create_dynamic_controls(self, parent: QWidget) -> QWidget:
        """
        创建动态控件
        
        Args:
            parent: 父控件
            
        Returns:
            包含动态控件的QWidget
        """
        container = QWidget(parent)
        layout = QVBoxLayout(container)
        
        # 根据cntrl.csv创建控件
        for cntrl_item in self.cntrl_data:
            # 不再过滤DISPFLG，创建所有控件但控制可见性
            control = self._create_control_from_cntrl(cntrl_item)
            if control:
                # 根据DISPFLG设置可见性
                dispflg = cntrl_item.get('DISPFLG', '0')
                if dispflg == '0':
                    control.setVisible(False)
                layout.addWidget(control)
        
        layout.addStretch()
        return container
    
    def _create_control_from_cntrl(self, cntrl_item: Dict[str, str]) -> Optional[QWidget]:
        """
        根据cntrl.csv项创建控件
        
        Args:
            cntrl_item: cntrl.csv中的一行数据
            
        Returns:
            创建的控件，如果无法创建则返回None
        """
        macro = cntrl_item.get('MACRO', '')
        kind = cntrl_item.get('KIND', '')
        btnname = cntrl_item.get('BTNNAME', '')
        
        if kind == 'input':
            return self._create_input_control(macro, btnname)
        elif kind == 'load':
            return self._create_load_control(macro)
        elif kind == 'relation':
            return self._create_relation_control(macro)
        elif kind == 'select':
            return self._create_select_control(macro)
        elif kind == 'switch':
            return self._create_switch_control(macro)
        
        return None
    
    def _create_input_control(self, macro: str, label: str) -> QWidget:
        """创建输入控件"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        layout.addWidget(QLabel(f"{label}:"))
        line_edit = QLineEdit()
        line_edit.setObjectName(f"input_{macro}")
        layout.addWidget(line_edit)
        
        return widget
    
    def _create_relation_control(self, macro: str) -> QWidget:
        """创建关系控件"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        layout.addWidget(QLabel(f"关系参数{macro}:"))
        combo = QComboBox()
        combo.setObjectName(f"relation_{macro}")
        
        # 从load.csv中获取实际的关系选项
        load_item = self._find_load_item_by_macro(macro)
        if load_item:
            # 获取该参数在所有型号中的可能值
            possible_values = set()
            for item in self.load_data:
                value = item.get(macro.lstrip('#'), '')
                if value and value not in ['0', '']:
                    possible_values.add(value)
            
            # 添加实际的关系选项
            if possible_values:
                combo.addItems(sorted(possible_values))
            else:
                # 如果没有找到实际值，使用默认选项
                combo.addItems(["关系1", "关系2", "关系3"])
            
            # 设置默认值
            default_value = load_item.get(macro.lstrip('#'), '')
            if default_value:
                index = combo.findText(default_value)
                if index >= 0:
                    combo.setCurrentIndex(index)
        else:
            # 如果没有找到对应的load项，使用默认选项
            combo.addItems(["关系1", "关系2", "关系3"])
        
        layout.addWidget(combo)
        
        return widget
    
    def _create_select_control(self, macro: str) -> QWidget:
        """创建选择控件"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        layout.addWidget(QLabel(f"选择参数{macro}:"))
        combo = QComboBox()
        combo.setObjectName(f"select_{macro}")
        combo.addItems(["选项1", "选项2", "选项3"])
        layout.addWidget(combo)
        
        return widget
    
    def _create_switch_control(self, macro: str) -> QWidget:
        """创建开关控件"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        checkbox = QCheckBox(f"开关{macro}")
        checkbox.setObjectName(f"switch_{macro}")
        layout.addWidget(checkbox)
        
        return widget
    
    def _create_load_control(self, macro: str) -> QWidget:
        """创建加载控件"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # 根据macro从load.csv中查找对应的数据
        load_item = self._find_load_item_by_macro(macro)
        if load_item:
            label_text = load_item.get('TYPE', f"参数{macro}")
            layout.addWidget(QLabel(f"{label_text}:"))
            
            # 检查参数的实际类型
            actual_value = load_item.get(macro.lstrip('#'), '')
            
            # 根据实际值类型创建合适的控件
            if self._is_numeric_value(actual_value):
                # 数值参数
                spinbox = QDoubleSpinBox()
                spinbox.setRange(0, 1000)
                spinbox.setDecimals(2)
                try:
                    spinbox.setValue(float(actual_value))
                except ValueError:
                    spinbox.setValue(0.0)
                spinbox.setObjectName(f"load_{macro}")
                layout.addWidget(spinbox)
            elif actual_value.startswith('relation'):
                # 关系类型参数，使用组合框
                combo = QComboBox()
                combo.setObjectName(f"load_{macro}")
                # 获取所有可能的关系值
                possible_values = set()
                for item in self.load_data:
                    value = item.get(macro.lstrip('#'), '')
                    if value and value.startswith('relation'):
                        possible_values.add(value)
                
                if possible_values:
                    combo.addItems(sorted(possible_values))
                    # 设置默认值
                    index = combo.findText(actual_value)
                    if index >= 0:
                        combo.setCurrentIndex(index)
                else:
                    combo.addItem(actual_value)
                layout.addWidget(combo)
            else:
                # 其他类型使用文本输入
                line_edit = QLineEdit(actual_value)
                line_edit.setObjectName(f"load_{macro}")
                layout.addWidget(line_edit)
        
        return widget

    def _is_numeric_value(self, value: str) -> bool:
        """检查值是否为数值"""
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def _find_load_item_by_macro(self, macro: str) -> Optional[Dict[str, str]]:
        """根据macro在load.csv中查找对应的项"""
        for item in self.load_data:
            if item.get('NO') == macro.lstrip('#'):
                return item
        return None
    
    def get_control_values(self, container: QWidget) -> Dict[str, Any]:
        """
        获取所有动态控件的值
        
        Args:
            container: 包含动态控件的容器
            
        Returns:
            控件值的字典
        """
        values = {}
        
        # 首先添加load.csv中的所有默认值
        for load_item in self.load_data:
            for key, value in load_item.items():
                if key.startswith('#'):
                    # 使用原始列名，不添加前缀
                    values[key] = value
    
        # 然后覆盖界面上的控件值
        for child in container.findChildren(QWidget):
            obj_name = child.objectName()
            if not obj_name:
                continue
                
            # 提取参数编号（去掉前缀）
            if obj_name.startswith('input_'):
                param_no = obj_name.replace('input_', '')
                if isinstance(child, QLineEdit):
                    values[param_no] = child.text()
            elif obj_name.startswith('load_'):
                param_no = obj_name.replace('load_', '')
                if isinstance(child, QDoubleSpinBox):
                    values[param_no] = child.value()
                elif isinstance(child, QComboBox):
                    values[param_no] = child.currentText()
                elif isinstance(child, QLineEdit):
                    values[param_no] = child.text()
            elif obj_name.startswith('relation_'):
                param_no = obj_name.replace('relation_', '')
                if isinstance(child, QComboBox):
                    values[param_no] = child.currentText()
            elif obj_name.startswith('select_'):
                param_no = obj_name.replace('select_', '')
                if isinstance(child, QComboBox):
                    values[param_no] = child.currentText()
            elif obj_name.startswith('switch_'):
                param_no = obj_name.replace('switch_', '')
                if isinstance(child, QCheckBox):
                    values[param_no] = child.isChecked()
        
        return values


class DynamicParameterWidget(QWidget):
    """动态参数输入部件"""
    
    # 信号定义
    parameters_changed = pyqtSignal(dict)
    transfer_requested = pyqtSignal(dict)
    
    def __init__(self, config_dir: str, parent=None):
        super().__init__(parent)
        self.config_dir = config_dir
        self.dynamic_loader = DynamicControlLoader(config_dir)
        self._init_ui()
        self._connect_signals()
        self.logger = logging.getLogger(__name__)
    
    def _init_ui(self) -> None:
        """初始化用户界面"""
        main_layout = QVBoxLayout(self)
        
        # 加载配置文件
        if not self.dynamic_loader.load_config_files():
            error_label = QLabel("加载配置文件失败")
            main_layout.addWidget(error_label)
            return
        
        # 创建动态控件组
        dynamic_group = QGroupBox("动态参数")
        dynamic_layout = QVBoxLayout(dynamic_group)
        
        # 创建动态控件
        self.dynamic_container = self.dynamic_loader.create_dynamic_controls(self)
        dynamic_layout.addWidget(self.dynamic_container)
        
        main_layout.addWidget(dynamic_group)
        
        # 转让按钮
        self.transfer_button = QPushButton("转让")
        main_layout.addWidget(self.transfer_button)
        
        main_layout.addStretch()
    
    def _connect_signals(self) -> None:
        """连接信号和槽"""
        self.transfer_button.clicked.connect(self._on_transfer_clicked)
    
    def _on_transfer_clicked(self) -> None:
        """转让按钮点击处理"""
        # 获取所有动态控件的值
        values = self.dynamic_loader.get_control_values(self.dynamic_container)
        
        # 发出转让请求信号
        self.transfer_requested.emit(values)
    
    def get_parameters(self) -> Dict[str, Any]:
        """获取所有参数值"""
        return self.dynamic_loader.get_control_values(self.dynamic_container)
        
    def update_config_directory(self, config_dir: str) -> None:
        """
        更新配置目录
        
        Args:
            config_dir: 新的配置目录路径
        """
        try:
            if config_dir != self.config_dir:
                self.config_dir = config_dir
                self.dynamic_loader = DynamicControlLoader(config_dir)
                self._reload_ui()
        except Exception as e:
            self.logger.error(f"更新配置目录失败: {e}")

    def _reload_ui(self) -> None:
        """重新加载UI"""
        # 清除现有布局
        layout = self.layout()
        if layout:
            # 移除所有子控件
            for i in reversed(range(layout.count())):
                widget = layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)
        
        # 重新初始化UI
        self._init_ui()
        self._connect_signals()