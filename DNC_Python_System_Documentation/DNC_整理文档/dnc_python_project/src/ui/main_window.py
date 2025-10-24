"""
主窗口
DNC系统的主界面，集成所有功能模块
"""

import sys
import logging
from typing import Dict, Any, Optional
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QTabWidget, QStatusBar, QMessageBox, QAction, 
                           QMenu, QToolBar, QSplitter, QLabel)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QFont

from ..core.application import DNCApplication
from ..core.config import ConfigManager
from .parameter_input import ParameterInputDialog
from .program_display import ProgramDisplayWidget
from .status_monitor import StatusMonitorWidget


class MainWindow(QMainWindow):
    """DNC系统主窗口"""
    
    # 信号定义
    status_changed = pyqtSignal(str)
    connection_changed = pyqtSignal(bool)
    
    def __init__(self, app: DNCApplication):
        """
        初始化主窗口
        
        Args:
            app: DNC应用程序实例
        """
        super().__init__()
        self.app = app
        self.config_manager = app.config_manager
        self.logger = logging.getLogger(__name__)
        
        # UI组件
        self.parameter_input = None
        self.program_display = None
        self.status_monitor = None
        self.tab_widget = None
        
        # 状态更新定时器
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_status)
        
        self._init_ui()
        self._connect_signals()
        
    def _init_ui(self) -> None:
        """初始化用户界面"""
        self.setWindowTitle("DNC数控系统")
        self.setMinimumSize(1200, 800)
        
        # 设置窗口图标
        # self.setWindowIcon(QIcon("resources/icon.png"))
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：参数输入
        self.parameter_input = ParameterInputDialog(self.app)
        splitter.addWidget(self.parameter_input)
        
        # 右侧：标签页
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 程序显示标签页
        self.program_display = ProgramDisplayWidget(self.app)
        self.tab_widget.addTab(self.program_display, "程序显示")
        
        # 状态监控标签页
        self.status_monitor = StatusMonitorWidget(self.app)
        self.tab_widget.addTab(self.status_monitor, "状态监控")
        
        right_layout.addWidget(self.tab_widget)
        splitter.addWidget(right_widget)
        
        # 设置分割比例
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        main_layout.addWidget(splitter)
        
        # 创建菜单栏
        self._create_menus()
        
        # 创建工具栏
        self._create_toolbar()
        
        # 创建状态栏
        self._create_statusbar()
        
        # 启动状态更新定时器
        self.status_timer.start(1000)  # 每秒更新一次
        
    def _create_menus(self) -> None:
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        
        new_action = QAction("新建(&N)", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("打开(&O)", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("保存(&S)", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_file)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 设备菜单
        device_menu = menubar.addMenu("设备(&D)")
        
        connect_action = QAction("连接设备(&C)", self)
        connect_action.setShortcut("Ctrl+C")
        connect_action.triggered.connect(self._connect_device)
        device_menu.addAction(connect_action)
        
        disconnect_action = QAction("断开设备(&D)", self)
        disconnect_action.setShortcut("Ctrl+D")
        disconnect_action.triggered.connect(self._disconnect_device)
        device_menu.addAction(disconnect_action)
        
        device_menu.addSeparator()
        
        config_action = QAction("设备配置(&S)", self)
        config_action.triggered.connect(self._show_device_config)
        device_menu.addAction(config_action)
        
        # 工具菜单
        tool_menu = menubar.addMenu("工具(&T)")
        
        import_action = QAction("导入程序(&I)", self)
        import_action.triggered.connect(self._import_program)
        tool_menu.addAction(import_action)
        
        export_action = QAction("导出程序(&E)", self)
        export_action.triggered.connect(self._export_program)
        tool_menu.addAction(export_action)
        
        tool_menu.addSeparator()
        
        calc_action = QAction("参数计算(&C)", self)
        calc_action.triggered.connect(self._calculate_parameters)
        tool_menu.addAction(calc_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        
        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        
    def _create_toolbar(self) -> None:
        """创建工具栏"""
        toolbar = QToolBar("主工具栏")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # 连接设备按钮
        connect_action = QAction("连接", self)
        connect_action.triggered.connect(self._connect_device)
        toolbar.addAction(connect_action)
        
        # 断开设备按钮
        disconnect_action = QAction("断开", self)
        disconnect_action.triggered.connect(self._disconnect_device)
        toolbar.addAction(disconnect_action)
        
        toolbar.addSeparator()
        
        # 导入程序按钮
        import_action = QAction("导入", self)
        import_action.triggered.connect(self._import_program)
        toolbar.addAction(import_action)
        
        # 导出程序按钮
        export_action = QAction("导出", self)
        export_action.triggered.connect(self._export_program)
        toolbar.addAction(export_action)
        
        toolbar.addSeparator()
        
        # 计算参数按钮
        calc_action = QAction("计算", self)
        calc_action.triggered.connect(self._calculate_parameters)
        toolbar.addAction(calc_action)
        
    def _create_statusbar(self) -> None:
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 连接状态标签
        self.connection_label = QLabel("未连接")
        self.status_bar.addWidget(self.connection_label)
        
        # 设备状态标签
        self.device_label = QLabel("设备: 未知")
        self.status_bar.addWidget(self.device_label)
        
        # 程序状态标签
        self.program_label = QLabel("程序: 无")
        self.status_bar.addWidget(self.program_label)
        
    def _connect_signals(self) -> None:
        """连接信号"""
        # 连接参数输入信号
        self.parameter_input.parameters_changed.connect(self._on_parameters_changed)
        self.parameter_input.model_changed.connect(self._on_model_changed)
        
        # 连接程序显示信号
        self.program_display.program_selected.connect(self._on_program_selected)
        self.program_display.program_executed.connect(self._on_program_executed)
        
        # 连接状态监控信号
        self.status_monitor.status_updated.connect(self._on_status_updated)
        
        # 连接应用信号
        self.app.model_recognized.connect(self._on_model_recognized)
        self.app.program_matched.connect(self._on_program_matched)
        self.app.parameters_calculated.connect(self._on_parameters_calculated)
        self.app.nc_command_sent.connect(self._on_nc_command_sent)
        self.app.nc_response_received.connect(self._on_nc_response_received)
        
    def _update_status(self) -> None:
        """更新状态显示"""
        # 更新连接状态
        if self.app.nc_communicator and self.app.nc_communicator.is_connected():
            self.connection_label.setText("已连接")
            self.connection_label.setStyleSheet("color: green;")
        else:
            self.connection_label.setText("未连接")
            self.connection_label.setStyleSheet("color: red;")
        
        # 更新设备信息
        if self.app.nc_communicator:
            conn_info = self.app.nc_communicator.get_connection_info()
            device_text = f"设备: {conn_info.get('device_name', '未知')}"
            self.device_label.setText(device_text)
        
        # 更新程序信息
        current_program = self.app.get_current_program()
        if current_program:
            program_text = f"程序: {current_program.get('name', '未知')}"
            self.program_label.setText(program_text)
        else:
            self.program_label.setText("程序: 无")
    
    def _on_parameters_changed(self, parameters: Dict[str, Any]) -> None:
        """
        处理参数变化
        
        Args:
            parameters: 新的参数值
        """
        self.logger.info(f"参数已更新: {parameters}")
        
        # 更新应用参数
        self.app.update_parameters(parameters)
        
        # 触发型号识别
        self.app.recognize_model()
        
    def _on_model_changed(self, model_info: Dict[str, Any]) -> None:
        """
        处理型号变化
        
        Args:
            model_info: 型号信息
        """
        self.logger.info(f"型号已更新: {model_info}")
        
        # 更新应用型号
        self.app.update_model(model_info)
        
        # 触发程序匹配
        self.app.match_program()
        
    def _on_model_recognized(self, model_info: Dict[str, Any]) -> None:
        """
        处理型号识别完成
        
        Args:
            model_info: 识别的型号信息
        """
        self.logger.info(f"型号识别完成: {model_info}")
        
        # 更新参数输入界面
        self.parameter_input.update_model_info(model_info)
        
        # 显示识别结果
        model_name = model_info.get('model_name', '未知型号')
        self.status_bar.showMessage(f"型号识别完成: {model_name}", 3000)
        
    def _on_program_matched(self, match_result: Dict[str, Any]) -> None:
        """
        处理程序匹配完成
        
        Args:
            match_result: 匹配结果
        """
        self.logger.info(f"程序匹配完成: {match_result}")
        
        # 更新程序显示界面
        self.program_display.update_programs(match_result)
        
        # 显示匹配结果
        program_count = len(match_result.get('matched_programs', []))
        self.status_bar.showMessage(f"找到 {program_count} 个匹配程序", 3000)
        
    def _on_parameters_calculated(self, calc_result: Dict[str, Any]) -> None:
        """
        处理参数计算完成
        
        Args:
            calc_result: 计算结果
        """
        self.logger.info(f"参数计算完成: {calc_result}")
        
        # 更新参数输入界面
        self.parameter_input.update_calculated_parameters(calc_result)
        
        # 显示计算结果
        self.status_bar.showMessage("参数计算完成", 3000)
        
    def _on_nc_command_sent(self, command_info: Dict[str, Any]) -> None:
        """
        处理NC命令发送
        
        Args:
            command_info: 命令信息
        """
        self.logger.info(f"NC命令已发送: {command_info}")
        
        # 更新状态监控
        self.status_monitor.update_command_status(command_info)
        
    def _on_nc_response_received(self, response_info: Dict[str, Any]) -> None:
        """
        处理NC响应接收
        
        Args:
            response_info: 响应信息
        """
        self.logger.info(f"NC响应已接收: {response_info}")
        
        # 更新状态监控
        self.status_monitor.update_response_status(response_info)
        
        # 显示响应结果
        if response_info.get('success'):
            self.status_bar.showMessage("NC命令执行成功", 3000)
        else:
            error_msg = response_info.get('error_message', '未知错误')
            self.status_bar.showMessage(f"NC命令执行失败: {error_msg}", 5000)
            
    def _on_program_selected(self, program_info: Dict[str, Any]) -> None:
        """
        处理程序选择
        
        Args:
            program_info: 程序信息
        """
        self.logger.info(f"程序已选择: {program_info}")
        
        # 更新当前程序
        self.app.set_current_program(program_info)
        
        # 显示选择结果
        program_name = program_info.get('name', '未知程序')
        self.status_bar.showMessage(f"已选择程序: {program_name}", 3000)
        
    def _on_program_executed(self, program_info: Dict[str, Any]) -> None:
        """
        处理程序执行
        
        Args:
            program_info: 程序信息
        """
        self.logger.info(f"程序执行请求: {program_info}")
        
        # 执行程序
        self.app.execute_program(program_info)
        
    def _on_status_updated(self, status_info: Dict[str, Any]) -> None:
        """
        处理状态更新
        
        Args:
            status_info: 状态信息
        """
        self.logger.debug(f"状态已更新: {status_info}")
        
        # 更新状态栏
        status_msg = status_info.get('message', '')
        if status_msg:
            self.status_bar.showMessage(status_msg, 2000)
    
    def _new_file(self) -> None:
        """新建文件"""
        reply = QMessageBox.question(self, "新建", "确定要新建文件吗？所有未保存的更改将丢失。",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.app.reset()
            self.parameter_input.clear()
            self.program_display.clear()
            self.status_bar.showMessage("已新建文件", 2000)
    
    def _open_file(self) -> None:
        """打开文件"""
        # TODO: 实现文件打开功能
        QMessageBox.information(self, "打开", "文件打开功能待实现")
        
    def _save_file(self) -> None:
        """保存文件"""
        # TODO: 实现文件保存功能
        QMessageBox.information(self, "保存", "文件保存功能待实现")
        
    def _connect_device(self) -> None:
        """连接设备"""
        try:
            if self.app.connect_to_device():
                self.status_bar.showMessage("设备连接成功", 3000)
            else:
                QMessageBox.warning(self, "连接失败", "无法连接到设备，请检查连接设置")
        except Exception as e:
            self.logger.error(f"连接设备失败: {e}")
            QMessageBox.critical(self, "连接错误", f"连接设备时发生错误: {str(e)}")
    
    def _disconnect_device(self) -> None:
        """断开设备"""
        try:
            if self.app.disconnect_from_device():
                self.status_bar.showMessage("设备已断开", 3000)
            else:
                QMessageBox.warning(self, "断开失败", "断开设备连接失败")
        except Exception as e:
            self.logger.error(f"断开设备失败: {e}")
            QMessageBox.critical(self, "断开错误", f"断开设备时发生错误: {str(e)}")
    
    def _show_device_config(self) -> None:
        """显示设备配置"""
        # TODO: 实现设备配置对话框
        QMessageBox.information(self, "设备配置", "设备配置功能待实现")
    
    def _import_program(self) -> None:
        """导入程序"""
        # TODO: 实现程序导入功能
        QMessageBox.information(self, "导入程序", "程序导入功能待实现")
    
    def _export_program(self) -> None:
        """导出程序"""
        # TODO: 实现程序导出功能
        QMessageBox.information(self, "导出程序", "程序导出功能待实现")
    
    def _calculate_parameters(self) -> None:
        """计算参数"""
        try:
            self.app.calculate_parameters()
        except Exception as e:
            self.logger.error(f"计算参数失败: {e}")
            QMessageBox.critical(self, "计算错误", f"计算参数时发生错误: {str(e)}")
    
    def _show_about(self) -> None:
        """显示关于信息"""
        about_text = """
        DNC数控系统
        
        版本: 1.0.0
        开发团队: DNC开发组
        
        功能特性:
        - 型号自动识别
        - 程序智能匹配
        - 参数自动计算
        - NC设备通信
        - 实时状态监控
        """
        QMessageBox.about(self, "关于 DNC系统", about_text)
    
    def closeEvent(self, event) -> None:
        """关闭事件处理"""
        reply = QMessageBox.question(self, "退出", "确定要退出系统吗？",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 停止状态定时器
            self.status_timer.stop()
