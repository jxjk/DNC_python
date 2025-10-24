"""
DNC系统主应用程序模块
负责系统初始化、生命周期管理和模块协调
"""

import sys
import os
from typing import Optional, Dict, Any, List
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

# 绝对引用导入
from dnc_python_project.src.core.config import ConfigManager
from dnc_python_project.src.core.event_dispatcher import EventDispatcher
from dnc_python_project.src.ui.main_window import MainWindow
from dnc_python_project.src.business.model_recognizer import ModelRecognizer
from dnc_python_project.src.business.program_matcher import ProgramMatcher
from dnc_python_project.src.business.calculation_engine import CalculationEngine
from dnc_python_project.src.business.relation_validator import RelationValidator
from dnc_python_project.src.business.nc_communicator import NCCommunicator
from dnc_python_project.src.data.csv_processor import CSVProcessor
from dnc_python_project.src.data.data_validator import DataValidator
from dnc_python_project.src.data.file_manager import FileManager
from dnc_python_project.src.communication.nc_protocol import NCProtocol
from dnc_python_project.src.communication.named_pipe import NamedPipeManager
from dnc_python_project.src.communication.protocol_factory import ProtocolFactory
from dnc_python_project.src.ui.control_factory import ControlFactory
from dnc_python_project.src.utils.logger import Logger
from dnc_python_project.src.utils.error_handler import ErrorHandler
from dnc_python_project.src.utils.constants import (
    DEFAULT_CONFIG_PATH, 
    SUPPORTED_PROTOCOLS,
    EVENT_TYPES
)


class DNCApplication(QObject):
    """
    DNC系统主应用程序类
    负责协调各个模块的工作流程和生命周期管理
    """
    
    # 信号定义
    model_recognized = pyqtSignal(dict)  # 型号识别完成
    program_matched = pyqtSignal(dict)   # 程序匹配完成
    parameters_calculated = pyqtSignal(dict)  # 参数计算完成
    data_sent = pyqtSignal(bool)         # 数据发送完成
    error_occurred = pyqtSignal(str)     # 错误发生
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化DNC应用程序
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        super().__init__()
        
        # 基础配置
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        self.is_initialized = False
        self.is_running = False
        
        # 核心模块实例
        self.config_manager: Optional[ConfigManager] = None
        self.event_dispatcher: Optional[EventDispatcher] = None
        self.logger: Optional[Logger] = None
        self.error_handler: Optional[ErrorHandler] = None
        
        # 业务逻辑模块
        self.model_recognizer: Optional[ModelRecognizer] = None
        self.program_matcher: Optional[ProgramMatcher] = None
        self.calculation_engine: Optional[CalculationEngine] = None
        self.relation_validator: Optional[RelationValidator] = None
        self.nc_communicator: Optional[NCCommunicator] = None
        
        # 数据访问模块
        self.csv_processor: Optional[CSVProcessor] = None
        self.data_validator: Optional[DataValidator] = None
        self.file_manager: Optional[FileManager] = None
        
        # 通信模块
        self.protocol_factory: Optional[ProtocolFactory] = None
        self.named_pipe_manager: Optional[NamedPipeManager] = None
        self.current_protocol: Optional[NCProtocol] = None
        
        # UI模块
        self.main_window: Optional[MainWindow] = None
        self.control_factory: Optional[ControlFactory] = None
        
        # 当前状态
        self.current_model: Optional[str] = None
        self.current_program_no: Optional[int] = None
        self.current_parameters: Dict[str, Any] = {}
        
        # 初始化定时器
        self.initialization_timer = QTimer()
        self.initialization_timer.setSingleShot(True)
        self.initialization_timer.timeout.connect(self._on_initialization_timeout)
    
    def initialize(self) -> bool:
        """
        初始化DNC系统
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            self.logger = Logger.get_logger("DNCApplication")
            self.logger.info("开始初始化DNC系统...")
            
            # 1. 初始化配置管理器
            self.config_manager = ConfigManager(self.config_path)
            if not self.config_manager.load_all_configs():
                self.logger.error("配置文件加载失败")
                return False
            
            # 2. 初始化事件分发器
            self.event_dispatcher = EventDispatcher()
            self._setup_event_handlers()
            
            # 3. 初始化错误处理器
            self.error_handler = ErrorHandler()
            
            # 4. 初始化数据访问模块
            self.csv_processor = CSVProcessor()
            self.data_validator = DataValidator()
            self.file_manager = FileManager()
            
            # 5. 初始化业务逻辑模块
            self.model_recognizer = ModelRecognizer(self.config_manager)
            self.program_matcher = ProgramMatcher(self.config_manager, self.csv_processor)
            self.calculation_engine = CalculationEngine(self.config_manager, self.csv_processor)
            self.relation_validator = RelationValidator(self.config_manager, self.csv_processor)
            self.nc_communicator = NCCommunicator(self.config_manager)
            
            # 6. 初始化通信模块
            self.protocol_factory = ProtocolFactory()
            self.named_pipe_manager = NamedPipeManager()
            
            # 7. 初始化UI模块
            self.control_factory = ControlFactory()
            
            # 8. 设置初始化超时保护
            self.initialization_timer.start(10000)  # 10秒超时
            
            self.is_initialized = True
            self.logger.info("DNC系统初始化完成")
            
            return True
            
        except Exception as e:
            error_msg = f"系统初始化失败: {str(e)}"
            self.logger.error(error_msg)
            self._show_error_dialog("初始化错误", error_msg)
            return False
    
    def _setup_event_handlers(self) -> None:
        """设置事件处理器"""
        if self.event_dispatcher:
            self.event_dispatcher.register_handler(
                EVENT_TYPES.MODEL_RECOGNIZED, 
                self._on_model_recognized
            )
            self.event_dispatcher.register_handler(
                EVENT_TYPES.PROGRAM_MATCHED,
                self._on_program_matched
            )
            self.event_dispatcher.register_handler(
                EVENT_TYPES.PARAMETERS_CALCULATED,
                self._on_parameters_calculated
            )
            self.event_dispatcher.register_handler(
                EVENT_TYPES.DATA_SENT,
                self._on_data_sent
            )
    
    def _on_initialization_timeout(self) -> None:
        """初始化超时处理"""
        if not self.is_initialized:
            self.logger.warning("系统初始化超时")
            self._show_error_dialog("初始化超时", "系统初始化时间过长，请检查配置文件")
    
    def run(self) -> int:
        """
        运行DNC应用程序
        
        Returns:
            int: 应用程序退出代码
        """
        if not self.is_initialized:
            self.logger.error("系统未初始化，无法运行")
            return 1
        
        try:
            self.is_running = True
            self.logger.info("启动DNC应用程序...")
            
            # 创建Qt应用程序实例
            app = QApplication(sys.argv)
            app.setApplicationName("DNC系统")
            app.setApplicationVersion("2.0.0")
            
            # 创建主窗口
            self.main_window = MainWindow(self)
            self.main_window.show()
            
            # 启动通信模块
            self._start_communication()
            
            self.logger.info("DNC应用程序启动成功")
            
            # 运行应用程序主循环
            return app.exec_()
            
        except Exception as e:
            error_msg = f"应用程序运行失败: {str(e)}"
            self.logger.error(error_msg)
            self._show_error_dialog("运行错误", error_msg)
            return 1
        finally:
            self.is_running = False
            self._cleanup()
    
    def _start_communication(self) -> None:
        """启动通信模块"""
        try:
            # 初始化NC通信协议
            protocol_type = self.config_manager.get_value("ProtocolType", "rexroth")
            self.current_protocol = self.protocol_factory.create_protocol(protocol_type)
            
            # 启动命名管道
            if self.config_manager.get_value("UseNamedPipe", "0") == "1":
                pipe_name = self.config_manager.get_value("PipeName", "DNC_Pipe")
                self.named_pipe_manager.start_server(pipe_name)
                self.named_pipe_manager.data_received.connect(self._on_pipe_data_received)
            
            self.logger.info(f"通信模块启动完成，使用协议: {protocol_type}")
            
        except Exception as e:
            self.logger.warning(f"通信模块启动失败: {str(e)}")
    
    def process_qr_code(self, qr_code: str) -> bool:
        """
        处理QR码输入
        
        Args:
            qr_code: QR码字符串
            
        Returns:
            bool: 处理是否成功
        """
        try:
            self.logger.info(f"开始处理QR码: {qr_code}")
            
            # 1. 型号识别
            model_info = self.model_recognizer.recognize_model(qr_code)
            if not model_info:
                self.logger.error("型号识别失败")
                return False
            
            self.current_model = model_info.get('model')
            self.model_recognized.emit(model_info)
            self.event_dispatcher.dispatch(EVENT_TYPES.MODEL_RECOGNIZED, model_info)
            
            # 2. 程序匹配
            program_info = self.program_matcher.match_program(self.current_model)
            if not program_info:
                self.logger.error("程序匹配失败")
                return False
            
            self.current_program_no = program_info.get('program_no')
            self.program_matched.emit(program_info)
            self.event_dispatcher.dispatch(EVENT_TYPES.PROGRAM_MATCHED, program_info)
            
            # 3. 参数计算
            model_parts = model_info.get('processed_parts', [])
            parameters = self.calculation_engine.calculate(
                self.current_program_no, 
                model_parts
            )
            
            if not parameters:
                self.logger.error("参数计算失败")
                return False
            
            self.current_parameters = parameters
            self.parameters_calculated.emit(parameters)
            self.event_dispatcher.dispatch(EVENT_TYPES.PARAMETERS_CALCULATED, parameters)
            
            # 4. 关系验证
            validation_results = self.relation_validator.validate_relations(
                self.current_program_no,
                parameters
            )
            
            # 5. 更新UI显示
            if self.main_window:
                self.main_window.update_display(
                    model_info, 
                    program_info, 
                    parameters,
                    validation_results
                )
            
            self.logger.info("QR码处理完成")
            return True
            
        except Exception as e:
            error_msg = f"QR码处理失败: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False
    
    def send_parameters_to_nc(self) -> bool:
        """
        发送参数到NC机床
        
        Returns:
            bool: 发送是否成功
        """
        try:
            if not self.current_protocol:
                self.logger.error("NC通信协议未初始化")
                return False
            
            if not self.current_parameters:
                self.logger.error("没有可发送的参数")
                return False
            
            self.logger.info("开始发送参数到NC机床...")
            
            success = self.current_protocol.send_parameters(self.current_parameters)
            
            if success:
                self.logger.info("参数发送成功")
                self.data_sent.emit(True)
                self.event_dispatcher.dispatch(EVENT_TYPES.DATA_SENT, {"success": True})
            else:
                self.logger.error("参数发送失败")
                self.data_sent.emit(False)
                self.event_dispatcher.dispatch(EVENT_TYPES.DATA_SENT, {"success": False})
            
            return success
            
        except Exception as e:
            error_msg = f"参数发送失败: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False
    
    def _on_pipe_data_received(self, data: str) -> None:
        """
        命名管道数据接收处理
        
        Args:
            data: 接收到的数据
        """
        try:
            self.logger.info(f"接收到管道数据: {data}")
            
            # 处理接收到的数据（可能是QR码或其他指令）
            if data.strip():
                self.process_qr_code(data.strip())
                
        except Exception as e:
            self.logger.error(f"管道数据处理失败: {str(e)}")
    
    def _on_model_recognized(self, data: Dict[str, Any]) -> None:
        """型号识别完成事件处理"""
        self.logger.info(f"型号识别完成: {data.get('model')}")
    
    def _on_program_matched(self, data: Dict[str, Any]) -> None:
        """程序匹配完成事件处理"""
        self.logger.info(f"程序匹配完成: 程序号 {data.get('program_no')}")
    
    def _on_parameters_calculated(self, data: Dict[str, Any]) -> None:
        """参数计算完成事件处理"""
        self.logger.info(f"参数计算完成，共 {len(data)} 个参数")
    
    def _on_data_sent(self, data: Dict[str, Any]) -> None:
        """数据发送完成事件处理"""
        success = data.get('success', False)
        status = "成功" if success else "失败"
        self.logger.info(f"数据发送{status}")
    
    def _show_error_dialog(self, title: str, message: str) -> None:
        """显示错误对话框"""
        try:
            QMessageBox.critical(None, title, message)
        except Exception:
            # 如果Qt未初始化，直接打印错误信息
            print(f"错误: {title} - {message}")
    
    def _cleanup(self) -> None:
        """清理资源"""
        self.logger.info("开始清理系统资源...")
        
        # 停止通信模块
        if self.named_pipe_manager:
            self.named_pipe_manager.stop_server()
        
        # 关闭文件资源
        if self.file_manager:
            self.file_manager.close_all_files()
        
        self.logger.info("系统资源清理完成")
    
    def get_application_info(self) -> Dict[str, Any]:
        """
        获取应用程序信息
        
        Returns:
            Dict[str, Any]: 应用程序信息
        """
        return {
            "name": "DNC系统",
            "version": "2.0.0",
            "initialized": self.is_initialized,
            "running": self.is_running,
            "current_model": self.current_model,
            "current_program": self.current_program_no,
            "parameter_count": len(self.current_parameters)
        }


def create_application(config_path: Optional[str] = None) -> DNCApplication:
    """
    创建DNC应用程序实例的工厂函数
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        DNCApplication: 应用程序实例
    """
    return DNCApplication(config_path)


if __name__ == "__main__":
    # 测试代码
    app = create_application()
    
    if app.initialize():
        print("DNC系统初始化成功")
        print("应用程序信息:", app.get_application_info())
    else:
        print("DNC系统初始化失败")
