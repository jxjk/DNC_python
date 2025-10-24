"""
DNC系统应用主类
负责系统初始化和生命周期管理
"""

import logging
from typing import Optional, Dict, Any
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject

from .config import ConfigManager
from .event_dispatcher import EventDispatcher
from ..ui.main_window import MainWindow
from ..business.model_recognizer import ModelRecognizer
from ..business.program_matcher import ProgramMatcher
from ..business.calculation_engine import CalculationEngine
from ..business.relation_validator import RelationValidator
from ..data.csv_processor import CSVProcessor
from ..data.file_manager import FileManager
from ..communication.nc_protocol import NCProtocolFactory
from ..utils.logger import setup_logging
from ..utils.error_handler import ErrorHandler


class Application(QObject):
    """DNC系统应用主类"""
    
    def __init__(self, config_path: str = "config/"):
        """
        初始化应用
        
        Args:
            config_path: 配置文件路径
        """
        super().__init__()
        self.config_path = config_path
        self._initialized = False
        
        # 核心组件
        self.config_manager: Optional[ConfigManager] = None
        self.event_dispatcher: Optional[EventDispatcher] = None
        self.main_window: Optional[MainWindow] = None
        self.model_recognizer: Optional[ModelRecognizer] = None
        self.program_matcher: Optional[ProgramMatcher] = None
        self.calculation_engine: Optional[CalculationEngine] = None
        self.relation_validator: Optional[RelationValidator] = None
        self.csv_processor: Optional[CSVProcessor] = None
        self.file_manager: Optional[FileManager] = None
        self.nc_protocol_factory: Optional[NCProtocolFactory] = None
        self.error_handler: Optional[ErrorHandler] = None
        
        # 应用状态
        self.is_running = False
        
    def initialize(self) -> bool:
        """
        系统初始化
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            # 设置日志系统
            setup_logging()
            self.logger = logging.getLogger(__name__)
            
            # 初始化错误处理器
            self.error_handler = ErrorHandler()
            
            # 初始化配置管理器
            self.config_manager = ConfigManager(self.config_path)
            if not self.config_manager.load_config():
                self.logger.error("配置加载失败")
                return False
            
            # 初始化事件分发器
            self.event_dispatcher = EventDispatcher()
            
            # 初始化数据处理器
            self.csv_processor = CSVProcessor()
            self.file_manager = FileManager()
            
            # 初始化业务逻辑组件
            self.model_recognizer = ModelRecognizer(self.config_manager)
            self.program_matcher = ProgramMatcher(self.config_manager, self.csv_processor)
            self.calculation_engine = CalculationEngine(self.config_manager, self.csv_processor)
            self.relation_validator = RelationValidator(self.config_manager, self.csv_processor)
            
            # 初始化通信组件
            self.nc_protocol_factory = NCProtocolFactory(self.config_manager)
            
            # 初始化用户界面
            self.main_window = MainWindow(
                config_manager=self.config_manager,
                event_dispatcher=self.event_dispatcher,
                model_recognizer=self.model_recognizer,
                program_matcher=self.program_matcher,
                calculation_engine=self.calculation_engine,
                relation_validator=self.relation_validator,
                nc_protocol_factory=self.nc_protocol_factory
            )
            
            # 连接事件
            self._connect_events()
            
            self._initialized = True
            self.logger.info("DNC系统初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"系统初始化失败: {e}")
            if self.error_handler:
                self.error_handler.handle_error(e, "系统初始化")
            return False
    
    def _connect_events(self) -> None:
        """连接系统事件"""
        if not self.event_dispatcher or not self.main_window:
            return
            
        # 连接型号识别事件
        self.event_dispatcher.model_recognized.connect(
            self.main_window.on_model_recognized
        )
        
        # 连接程序匹配事件
        self.event_dispatcher.program_matched.connect(
            self.main_window.on_program_matched
        )
        
        # 连接参数计算事件
        self.event_dispatcher.parameters_calculated.connect(
            self.main_window.on_parameters_calculated
        )
        
        # 连接NC通信事件
        self.event_dispatcher.nc_communication_status.connect(
            self.main_window.on_nc_communication_status
        )
        
        # 连接错误事件
        self.event_dispatcher.error_occurred.connect(
            self.main_window.on_error_occurred
        )
    
    def run(self) -> int:
        """
        运行应用
        
        Returns:
            int: 应用退出代码
        """
        if not self._initialized:
            self.logger.error("应用未初始化，无法运行")
            return 1
        
        try:
            self.is_running = True
            self.logger.info("DNC系统启动")
            
            # 显示主窗口
            if self.main_window:
                self.main_window.show()
            
            # 进入应用主循环
            app = QApplication.instance()
            if app:
                return app.exec_()
            else:
                self.logger.error("QApplication实例不存在")
                return 1
                
        except Exception as e:
            self.logger.error(f"应用运行失败: {e}")
            if self.error_handler:
                self.error_handler.handle_error(e, "应用运行")
            return 1
    
    def shutdown(self) -> None:
        """关闭应用"""
        self.is_running = False
        
        # 关闭NC通信
        if self.nc_protocol_factory:
            self.nc_protocol_factory.close_all_connections()
        
        # 保存配置
        if self.config_manager:
            self.config_manager.save_config()
        
        # 清理资源
        if self.csv_processor:
            self.csv_processor.clear_cache()
        
        self.logger.info("DNC系统已关闭")
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        获取系统信息
        
        Returns:
            Dict[str, Any]: 系统信息字典
        """
        return {
            "version": "1.0.0",
            "initialized": self._initialized,
            "running": self.is_running,
            "components": {
                "config_manager": self.config_manager is not None,
                "event_dispatcher": self.event_dispatcher is not None,
                "main_window": self.main_window is not None,
                "model_recognizer": self.model_recognizer is not None,
                "program_matcher": self.program_matcher is not None,
                "calculation_engine": self.calculation_engine is not None,
                "csv_processor": self.csv_processor is not None,
                "nc_protocol_factory": self.nc_protocol_factory is not None
            }
        }


class ApplicationManager:
    """应用管理器（单例模式）"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._application = None
        return cls._instance
    
    def create_application(self, config_path: str = "config/") -> Application:
        """
        创建应用实例
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            Application: 应用实例
        """
        if self._application is None:
            self._application = Application(config_path)
        return self._application
    
    def get_application(self) -> Optional[Application]:
        """
        获取当前应用实例
        
        Returns:
            Optional[Application]: 应用实例
        """
        return self._application
    
    def shutdown_application(self) -> None:
        """关闭应用"""
        if self._application:
            self._application.shutdown()
            self._application = None
