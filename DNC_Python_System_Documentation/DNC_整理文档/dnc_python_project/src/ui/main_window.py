# main_window.py
"""
主窗口
DNC系统的主界面，集成所有功能模块
"""

import sys
import os
import logging
from typing import Dict, Any, Optional, List
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QTabWidget, QStatusBar, QMessageBox, QAction, 
                           QMenu, QToolBar, QSplitter, QLabel, QLineEdit)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QIcon, QFont

from src.core.application import DNCApplication
from src.core.config import ConfigManager
from src.data.csv_processor import CSVProcessor
from src.ui.parameter_input import ParameterInputWidget
from src.ui.program_display import ProgramDisplayWidget
from src.ui.status_monitor import StatusMonitorWidget
from src.ui.dynamic_loader import DynamicParameterWidget
from src.business.macro_generator import MacroGenerator


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
        self.dynamic_parameter = None
        self.tab_widget = None
        self.macro_generator = None
        # 状态更新定时器
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_status)
        
        self._init_ui()
        self._init_macro_generator()  # 添加这行
        self._connect_signals()
        
    def _init_macro_generator(self) -> None:
        """初始化宏文件生成器"""
        try:
            # 从app中获取config_manager和csv_processor
            config_manager = self.app.config_manager
            csv_processor = self.app.csv_processor
            
            # 检查CSV处理器是否可用
            if not csv_processor:
                self.logger.warning("CSV处理器不可用，尝试重新创建")
                try:
                    csv_processor = CSVProcessor(config_manager)
                    self.logger.info("CSV处理器重新创建成功")
                except Exception as e:
                    self.logger.error(f"CSV处理器重新创建失败: {e}")
                    self.macro_generator = None
                    return
            
            # 初始化宏文件生成器
            self.macro_generator = MacroGenerator(config_manager, csv_processor)
            self.logger.info("宏文件生成器初始化成功")
        except Exception as e:
            self.logger.error(f"宏文件生成器初始化失败: {e}")
            self.macro_generator = None
        
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
        self.parameter_input = ParameterInputWidget()
        splitter.addWidget(self.parameter_input)
        
        # 右侧：标签页
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 程序显示标签页
        self.program_display = ProgramDisplayWidget()
        self.tab_widget.addTab(self.program_display, "程序显示")
        
        # 状态监控标签页
        self.status_monitor = StatusMonitorWidget()
        self.tab_widget.addTab(self.status_monitor, "状态监控")
        
        # 动态参数标签页 - 使用动态配置目录
        config_dir = self._get_current_program_directory() or os.path.join("config", "master", "prg1")
        self.dynamic_parameter = DynamicParameterWidget(config_dir)
        self.tab_widget.addTab(self.dynamic_parameter, "动态参数")
        
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
        
    def _get_current_program_directory(self) -> Optional[str]:
        """
        获取当前程序的配置目录
        
        Returns:
            当前程序目录路径，如果无法确定则返回None
        """
        try:
            # 获取当前程序序列
            current_program_sequence = self.app.get_current_program_sequence()
            if not current_program_sequence:
                self.logger.warning("无法获取当前程序序列，使用默认目录")
                return os.path.join("config", "master", "prg1")
            
            # 使用第一个程序作为当前程序
            current_program = current_program_sequence[0] if current_program_sequence else "prg1"
            
            # 构建程序目录路径
            program_dir = os.path.join("config", "master", current_program)
            
            # 检查目录是否存在
            if os.path.exists(program_dir):
                self.logger.debug(f"使用程序目录: {program_dir}")
                return program_dir
            else:
                self.logger.warning(f"程序目录不存在: {program_dir}，使用默认目录")
                return os.path.join("config", "master", "prg1")
                
        except Exception as e:
            self.logger.warning(f"获取当前程序目录失败: {e}，使用默认目录")
            return os.path.join("config", "master", "prg1")
        
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
        
        # 连接动态参数信号
        self.dynamic_parameter.transfer_requested.connect(self._on_transfer_requested)
        
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
        model_name = model_info.get('model', '未知型号')
        self.status_bar.showMessage(f"型号识别完成: {model_name}", 3000)
        
        # 更新界面显示PO和QUANTITY
        if hasattr(self, 'parameter_input') and hasattr(self.parameter_input, 'po_input') and model_info.get('po'):
            self.parameter_input.po_input.setText(model_info['po'])
        
        if hasattr(self, 'parameter_input') and hasattr(self.parameter_input, 'quantity_input') and model_info.get('quantity'):
            self.parameter_input.quantity_input.setText(model_info['quantity'])
        
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
        program_count = 1 if match_result.get('program_no') else 0
        self.status_bar.showMessage(f"找到 {program_count} 个匹配程序", 3000)
        
        # 更新动态参数界面的配置目录
        config_dir = self._get_current_program_directory() or os.path.join("config", "master", "prg1")
        if self.dynamic_parameter:
            self.dynamic_parameter.update_config_directory(config_dir)
        
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
            
    def _get_parameter_kind_from_load_csv(self, macro: str) -> str:
        """
        从load.csv中获取参数类型
        
        Args:
            macro: 参数宏名称（如 #500, #503 等）
            
        Returns:
            参数类型字符串
        """
        try:
            # 检查csv_processor是否可用
            if not hasattr(self.app, 'csv_processor') or self.app.csv_processor is None:
                self.logger.warning("CSV处理器不可用，使用默认类型推断")
                return self._get_default_kind(macro)
            
            # 获取当前程序目录
            current_program_dir = self._get_current_program_directory()
            if not current_program_dir:
                return self._get_default_kind(macro)
            
            # 从当前程序的load.csv中读取参数类型
            load_csv_path = os.path.join(current_program_dir, 'load.csv')
            load_data = self.app.csv_processor.read_csv_as_dict(load_csv_path)
            if not load_data:
                return self._get_default_kind(macro)
            
            # 遍历数据行，查找对应宏的值
            for row in load_data:
                if macro in row:
                    actual_value = row[macro].strip()
                    
                    # 根据实际值类型判断
                    if actual_value == '':
                        return 'STRING'
                    elif self._is_numeric_value(actual_value):
                        return 'FLOAT'
                    elif actual_value.startswith('relation'):
                        return 'STRING'
                    elif actual_value.startswith('define'):
                        return 'STRING'
                    elif actual_value.startswith('switch'):
                        return 'BOOLEAN'
                    else:
                        return 'STRING'
            
            return self._get_default_kind(macro)
            
        except Exception as e:
            self.logger.warning(f"从load.csv获取参数类型失败: {e}")
            return self._get_default_kind(macro)

    def _get_default_kind(self, macro: str) -> str:
        """获取默认参数类型"""
        # 根据cntrl.csv中的KIND字段推断默认类型
        try:
            # 检查csv_processor是否可用
            if not hasattr(self.app, 'csv_processor') or self.app.csv_processor is None:
                self.logger.warning("CSV处理器不可用，使用备用默认类型")
                return self._get_fallback_kind(macro)
            
            # 获取当前程序目录
            current_program_dir = self._get_current_program_directory()
            if not current_program_dir:
                return self._get_fallback_kind(macro)
            
            cntrl_csv_path = os.path.join(current_program_dir, 'cntrl.csv')
            cntrl_data = self.app.csv_processor.read_csv_as_dict(cntrl_csv_path)
            
            # 遍历数据行查找对应的宏
            if cntrl_data:
                for row in cntrl_data:
                    if 'MACRO' in row and row['MACRO'] == macro:
                        if 'KIND' in row:
                            kind = row['KIND'].strip()
                            if kind == 'input':
                                return 'STRING'
                            elif kind == 'load':
                                return 'FLOAT'
                            elif kind == 'relation':
                                return 'STRING'
                            elif kind == 'select':
                                return 'STRING'
                            elif kind == 'switch':
                                return 'BOOLEAN'
        except Exception as e:
            self.logger.warning(f"从cntrl.csv获取参数类型失败: {e}")
        
        # 使用备用默认类型推断
        return self._get_fallback_kind(macro)

    def _get_fallback_kind(self, macro: str) -> str:
        """备用默认类型推断"""
        # 根据参数名称模式推断类型
        if macro in ['#1', '#2', '#3', '#4', '#5', '#6', '#7', '#8', '#9', '#10', '#11', '#12']:
            return 'FLOAT'
        elif macro.startswith('#5') and len(macro) == 4:  # #500-#599
            return 'STRING'
        elif macro.startswith('#6') and len(macro) == 4:  # #600-#699
            return 'STRING'
        else:
            return 'STRING'

    def _is_numeric_value(self, value: str) -> bool:
        """检查值是否为数值"""
        try:
            float(value)
            return True
        except ValueError:
            return False

    def _convert_parameters_to_variables(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        将动态参数转换为Variable对象
        
        Args:
            parameters: 动态参数字典
            
        Returns:
            Dict[str, Any]: Variable对象字典
        """
        from src.business.macro_generator import Variable
        
        variables = {}
        for param_name, param_value in parameters.items():
            # 参数名称现在直接是load.csv中的列名（如 #500, #503 等）
            # 从load.csv中获取实际参数类型
            kind = self._get_parameter_kind_from_load_csv(param_name)
            
            # 处理空值
            if param_value is None or param_value == '':
                if kind in ['FLOAT', 'INTEGER']:
                    param_value = 0.0
                elif kind == 'BOOLEAN':
                    param_value = False
                else:
                    param_value = ''
            
            # 类型转换 - 修复：优先检查是否为关系、定义或开关类型
            try:
                if isinstance(param_value, str) and param_value.strip():
                    # 检查是否为关系、定义或开关类型
                    if param_value.startswith('relation'):
                        kind = 'STRING'  # 强制设置为字符串类型
                        param_value = str(param_value)
                    elif param_value.startswith('define'):
                        kind = 'STRING'  # 强制设置为字符串类型
                        param_value = str(param_value)
                    elif param_value.startswith('switch'):
                        kind = 'BOOLEAN'  # 强制设置为布尔类型
                        param_value = param_value.lower() in ['true', '1', 'yes', 'on', 'switchjd']
                    elif kind == 'FLOAT':
                        # 只有明确是数值类型时才尝试转换
                        if self._is_numeric_value(param_value):
                            param_value = float(param_value)
                        else:
                            # 无法转换为数值，保持为字符串
                            kind = 'STRING'
                            param_value = str(param_value)
                    elif kind == 'INTEGER':
                        if self._is_numeric_value(param_value):
                            param_value = int(float(param_value))  # 先转float再转int
                        else:
                            kind = 'STRING'
                            param_value = str(param_value)
                    elif kind == 'BOOLEAN':
                        param_value = param_value.lower() in ['true', '1', 'yes', 'on']
                    else:
                        # 其他情况保持为字符串
                        param_value = str(param_value)
                else:
                    # 非字符串类型的处理
                    if kind == 'FLOAT':
                        param_value = float(param_value) if param_value else 0.0
                    elif kind == 'INTEGER':
                        param_value = int(param_value) if param_value else 0
                    elif kind == 'BOOLEAN':
                        param_value = bool(param_value)
                    else:
                        param_value = str(param_value) if param_value else ''
            except (ValueError, TypeError) as e:
                self.logger.warning(f"参数 {param_name} 类型转换失败: {e}, 值: {param_value}")
                # 转换失败时使用默认值
                if kind == 'FLOAT':
                    param_value = 0.0
                elif kind == 'INTEGER':
                    param_value = 0
                elif kind == 'BOOLEAN':
                    param_value = False
                else:
                    param_value = str(param_value)
            
            # 创建Variable对象
            variable = Variable(
                name=param_name,
                kind=kind,
                value=param_value,
                definition="",
                display_flag=True,
                send_flag=True
            )
            variables[param_name] = variable
        
        return variables

    def _on_transfer_requested(self, parameters: Dict[str, Any]) -> None:
        """
        处理转让按钮点击事件
        
        Args:
            parameters: 动态加载的参数值
        """
        self.logger.info(f"转让按钮点击，参数: {parameters}")
        
        try:
            # 检查宏文件生成器是否已初始化
            if not self.macro_generator:
                self.logger.error("宏文件生成器未初始化")
                QMessageBox.warning(self, "错误", "宏文件生成器未初始化")
                return
                
            # 检查CSV处理器是否可用
            if not hasattr(self.app, 'csv_processor') or self.app.csv_processor is None:
                self.logger.error("CSV处理器不可用")
                QMessageBox.warning(self, "错误", "CSV处理器不可用，无法进行参数类型推断")
                return
                
            # 获取当前型号
            current_model = self.app.current_model
            
            # 将参数转换为Variable对象
            variables = self._convert_parameters_to_variables(parameters)
            
            # 检查变量转换结果
            if not variables:
                self.logger.error("参数转换失败，没有生成有效的变量")
                QMessageBox.warning(self, "错误", "参数转换失败，请检查参数格式")
                return
            
            # 生成宏文件，使用正确的方法名和参数
            result = self.macro_generator.generate_macro(variables, current_model)
            
            if result.success:
                self.status_bar.showMessage("macro.txt文件生成成功", 3000)
                
                # 读取并显示生成的宏文件内容
                with open(result.file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 在界面上显示计算结果
                self._display_calculation_results(content)
                
                QMessageBox.information(self, "成功", f"macro.txt文件已成功生成: {result.file_path}")
            else:
                self.status_bar.showMessage("macro.txt文件生成失败", 5000)
                error_details = f"宏文件生成失败: {result.error_message}"
                if hasattr(result, 'validation_errors') and result.validation_errors:
                    error_details += f"\n验证错误: {result.validation_errors}"
                QMessageBox.warning(self, "失败", error_details)
                
        except Exception as e:
            self.logger.error(f"生成macro.txt文件失败: {e}")
            QMessageBox.critical(self, "错误", f"生成macro.txt文件时发生错误: {str(e)}")
    
    def _display_calculation_results(self, macro_content: str) -> None:
        """
        在界面上显示计算结果
        """
        try:
            # 解析宏文件内容
            lines = macro_content.split('\n')
            calculation_results = []
            
            for line in lines:
                if line.strip() and not line.startswith(';') and '=' in line:
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        param_name = parts[0].strip()
                        param_value = parts[1].strip()
                        calculation_results.append(f"{param_name} = {param_value}")
            
            # 在界面上显示结果（可以根据需要调整显示方式）
            if hasattr(self, 'calculation_display'):
                self.calculation_display.setText('\n'.join(calculation_results))
            else:
                # 如果没有专门的显示控件，可以在日志中显示
                self.logger.info("计算结果显示:")
                for result in calculation_results:
                    self.logger.info(result)
                    
        except Exception as e:
            self.logger.error(f"显示计算结果失败: {e}")
    
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
            event.accept()
        else:
            event.ignore()
    
    def update_display(self, model_info: Dict[str, Any], program_info: Dict[str, Any], 
                      parameters: Dict[str, Any], validation_results: Dict[str, Any]) -> None:
        """
        更新显示界面
        
        Args:
            model_info: 型号信息
            program_info: 程序信息
            parameters: 参数信息
            validation_results: 验证结果
        """
        try:
            # 更新参数输入界面
            self.parameter_input.update_model_info(model_info)
            self.parameter_input.update_calculated_parameters(parameters)
            
            # 更新程序显示界面
            self.program_display.update_programs(program_info)
            
            # 更新状态监控界面
            self.status_monitor.update_validation_results(validation_results)
            
            # 显示状态信息
            model_name = model_info.get('model', '未知')
            program_no = program_info.get('program_no', '未知')
            self.status_bar.showMessage(f"处理完成: 型号={model_name}, 程序={program_no}", 3000)
            
        except Exception as e:
            self.logger.error(f"更新显示界面失败: {e}")
