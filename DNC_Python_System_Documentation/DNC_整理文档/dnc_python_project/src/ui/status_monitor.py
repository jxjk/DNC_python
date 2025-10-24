import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                            QLabel, QProgressBar, QTableWidget, QTableWidgetItem,
                            QHeaderView, QSplitter, QFrame, QPushButton)
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QBrush
from typing import Dict, Any, List
from datetime import datetime


class StatusMonitorWidget(QWidget):
    """状态监控组件"""
    
    # 信号定义
    status_updated = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    connection_changed = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_status = {}
        self.error_log = []
        self.connection_status = False
        self._init_ui()
        self._connect_signals()
        self._start_monitoring()
    
    def _init_ui(self) -> None:
        """初始化用户界面"""
        main_layout = QVBoxLayout(self)
        
        # 创建分割器
        splitter = QSplitter(Qt.Vertical)
        
        # 设备状态组
        device_group = self._create_device_group()
        splitter.addWidget(device_group)
        
        # 错误日志组
        error_group = self._create_error_group()
        splitter.addWidget(error_group)
        
        # 设置分割比例
        splitter.setSizes([300, 200])
        
        main_layout.addWidget(splitter)
        
        # 控制按钮
        button_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("刷新状态")
        self.clear_log_button = QPushButton("清空日志")
        self.connect_button = QPushButton("连接设备")
        self.disconnect_button = QPushButton("断开连接")
        
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.clear_log_button)
        button_layout.addStretch()
        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(self.disconnect_button)
        
        main_layout.addLayout(button_layout)
    
    def _create_device_group(self) -> QGroupBox:
        """创建设备状态组"""
        group = QGroupBox("设备状态监控")
        layout = QVBoxLayout()
        
        # 连接状态
        connection_layout = QHBoxLayout()
        connection_layout.addWidget(QLabel("连接状态:"))
        self.connection_label = QLabel("未连接")
        self.connection_label.setStyleSheet("color: red; font-weight: bold;")
        connection_layout.addWidget(self.connection_label)
        connection_layout.addStretch()
        
        layout.addLayout(connection_layout)
        
        # 创建表格显示详细状态
        self.status_table = QTableWidget()
        self.status_table.setColumnCount(3)
        self.status_table.setHorizontalHeaderLabels(["参数", "值", "状态"])
        
        # 设置表格属性
        self.status_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.status_table.setAlternatingRowColors(True)
        self.status_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # 初始化状态数据
        self._init_status_data()
        
        layout.addWidget(self.status_table)
        
        group.setLayout(layout)
        return group
    
    def _create_error_group(self) -> QGroupBox:
        """创建错误日志组"""
        group = QGroupBox("错误日志")
        layout = QVBoxLayout()
        
        # 错误日志表格
        self.error_table = QTableWidget()
        self.error_table.setColumnCount(4)
        self.error_table.setHorizontalHeaderLabels(["时间", "级别", "模块", "描述"])
        
        # 设置表格属性
        self.error_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.error_table.setAlternatingRowColors(True)
        self.error_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.error_table)
        
        group.setLayout(layout)
        return group
    
    def _init_status_data(self) -> None:
        """初始化状态数据"""
        # 定义状态参数
        status_params = [
            ("设备名称", "未连接", "未知"),
            ("设备型号", "未连接", "未知"),
            ("IP地址", "未连接", "未知"),
            ("端口", "未连接", "未知"),
            ("运行状态", "停止", "停止"),
            ("主轴转速", "0 rpm", "正常"),
            ("进给速度", "0 mm/min", "正常"),
            ("X轴位置", "0.000 mm", "正常"),
            ("Y轴位置", "0.000 mm", "正常"),
            ("Z轴位置", "0.000 mm", "正常"),
            ("程序行号", "0", "正常"),
            ("加工时间", "00:00:00", "正常"),
            ("剩余时间", "00:00:00", "正常"),
            ("报警代码", "无", "正常"),
            ("温度", "0°C", "正常")
        ]
        
        self.status_table.setRowCount(len(status_params))
        
        for row, (param, value, status) in enumerate(status_params):
            self.status_table.setItem(row, 0, QTableWidgetItem(param))
            self.status_table.setItem(row, 1, QTableWidgetItem(value))
            self.status_table.setItem(row, 2, QTableWidgetItem(status))
            
            # 设置状态颜色
            self._set_status_color(row, 2, status)
    
    def _set_status_color(self, row: int, column: int, status: str) -> None:
        """设置状态颜色"""
        item = self.status_table.item(row, column)
        if not item:
            return
            
        if status == "正常":
            item.setBackground(QBrush(QColor(144, 238, 144)))  # 浅绿色
        elif status == "警告":
            item.setBackground(QBrush(QColor(255, 255, 0)))    # 黄色
        elif status == "错误":
            item.setBackground(QBrush(QColor(255, 0, 0)))      # 红色
        elif status == "停止":
            item.setBackground(QBrush(QColor(192, 192, 192)))  # 灰色
        else:
            item.setBackground(QBrush(QColor(255, 255, 255)))  # 白色
    
    def _connect_signals(self) -> None:
        """连接信号和槽"""
        self.refresh_button.clicked.connect(self._on_refresh_clicked)
        self.clear_log_button.clicked.connect(self._on_clear_log_clicked)
        self.connect_button.clicked.connect(self._on_connect_clicked)
        self.disconnect_button.clicked.connect(self._on_disconnect_clicked)
    
    def _start_monitoring(self) -> None:
        """开始监控"""
        # 创建定时器用于定期更新状态
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self._update_status)
        self.monitor_timer.start(1000)  # 每秒更新一次
    
    def _on_refresh_clicked(self) -> None:
        """刷新状态按钮点击处理"""
        self._update_status()
    
    def _on_clear_log_clicked(self) -> None:
        """清空日志按钮点击处理"""
        self.error_table.setRowCount(0)
        self.error_log.clear()
    
    def _on_connect_clicked(self) -> None:
        """连接设备按钮点击处理"""
        self.connection_status = True
        self._update_connection_status()
        self.connection_changed.emit(True)
        
        # 添加连接日志
        self.add_error_log("信息", "状态监控", "设备连接成功")
    
    def _on_disconnect_clicked(self) -> None:
        """断开连接按钮点击处理"""
        self.connection_status = False
        self._update_connection_status()
        self.connection_changed.emit(False)
        
        # 添加断开日志
        self.add_error_log("信息", "状态监控", "设备断开连接")
    
    def _update_connection_status(self) -> None:
        """更新连接状态显示"""
        if self.connection_status:
            self.connection_label.setText("已连接")
            self.connection_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.connection_label.setText("未连接")
            self.connection_label.setStyleSheet("color: red; font-weight: bold;")
    
    def _update_status(self) -> None:
        """更新状态信息"""
        if not self.connection_status:
            return
        
        # 模拟状态更新
        import random
        current_time = datetime.now().strftime("%H:%M:%S")
        
        # 更新状态数据
        status_updates = {
            "运行状态": ("运行", "正常") if random.random() > 0.1 else ("停止", "停止"),
            "主轴转速": (f"{random.randint(1000, 5000)} rpm", "正常"),
            "进给速度": (f"{random.randint(100, 2000)} mm/min", "正常"),
            "X轴位置": (f"{random.uniform(-100, 100):.3f} mm", "正常"),
            "Y轴位置": (f"{random.uniform(-100, 100):.3f} mm", "正常"),
            "Z轴位置": (f"{random.uniform(-50, 50):.3f} mm", "正常"),
            "程序行号": (str(random.randint(1, 100)), "正常"),
            "加工时间": (current_time, "正常"),
            "温度": (f"{random.randint(20, 60)}°C", "正常" if random.random() > 0.05 else "警告")
        }
        
        # 应用更新
        for row in range(self.status_table.rowCount()):
            param_item = self.status_table.item(row, 0)
            if not param_item:
                continue
                
            param_name = param_item.text()
            if param_name in status_updates:
                value, status = status_updates[param_name]
                self.status_table.item(row, 1).setText(value)
                self.status_table.item(row, 2).setText(status)
                self._set_status_color(row, 2, status)
        
        # 随机生成错误日志（模拟）
        if random.random() < 0.02:  # 2% 概率生成错误
            error_types = ["警告", "错误"]
            modules = ["主轴", "进给", "X轴", "Y轴", "Z轴", "系统"]
            descriptions = [
                "温度过高", "速度异常", "位置偏差", "通信超时",
                "过载保护", "急停触发", "程序错误", "参数异常"
            ]
            
            error_type = random.choice(error_types)
            module = random.choice(modules)
            description = random.choice(descriptions)
            
            self.add_error_log(error_type, module, description)
    
    def add_error_log(self, level: str, module: str, description: str) -> None:
        """添加错误日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 添加到日志列表
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "module": module,
            "description": description
        }
        self.error_log.append(log_entry)
        
        # 更新表格
        row = self.error_table.rowCount()
        self.error_table.insertRow(row)
        
        self.error_table.setItem(row, 0, QTableWidgetItem(timestamp))
        self.error_table.setItem(row, 1, QTableWidgetItem(level))
        self.error_table.setItem(row, 2, QTableWidgetItem(module))
        self.error_table.setItem(row, 3, QTableWidgetItem(description))
        
        # 设置级别颜色
        level_item = self.error_table.item(row, 1)
        if level == "错误":
            level_item.setBackground(QBrush(QColor(255, 200, 200)))  # 浅红色
        elif level == "警告":
            level_item.setBackground(QBrush(QColor(255, 255, 200)))  # 浅黄色
        else:
            level_item.setBackground(QBrush(QColor(200, 255, 200)))  # 浅绿色
        
        # 滚动到最后一行
        self.error_table.scrollToBottom()
        
        # 发出错误信号
        if level == "错误":
            self.error_occurred.emit(f"{module}: {description}")
    
    def get_current_status(self) -> Dict[str, Any]:
        """获取当前状态"""
        status = {}
        for row in range(self.status_table.rowCount()):
            param_item = self.status_table.item(row, 0)
            value_item = self.status_table.item(row, 1)
            status_item = self.status_table.item(row, 2)
            
            if param_item and value_item and status_item:
                param_name = param_item.text()
                status[param_name] = {
                    "value": value_item.text(),
                    "status": status_item.text()
                }
        
        return status
    
    def get_error_log(self) -> List[Dict[str, str]]:
        """获取错误日志"""
        return self.error_log.copy()
    
    def clear_status(self) -> None:
        """清空状态"""
        self._init_status_data()
        self._on_clear_log_clicked()
        self.connection_status = False
        self._update_connection_status()


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    widget = StatusMonitorWidget()
    widget.show()
    
    sys.exit(app.exec_())
