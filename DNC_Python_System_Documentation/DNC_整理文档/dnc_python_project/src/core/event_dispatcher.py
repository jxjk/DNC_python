"""
事件分发器
负责系统内部事件的发布和订阅
"""

import logging
from typing import Any, Dict, Callable, List
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot


class ModelRecognizedEvent:
    """型号识别事件"""
    
    def __init__(self, qr_code: str, model: str, po: str, quantity: str, recognition_mode: str):
        """
        初始化型号识别事件
        
        Args:
            qr_code: 原始QR码
            model: 识别出的型号
            po: 识别出的PO号
            quantity: 识别出的数量
            recognition_mode: 识别模式
        """
        self.qr_code = qr_code
        self.model = model
        self.po = po
        self.quantity = quantity
        self.recognition_mode = recognition_mode


class ProgramMatchedEvent:
    """程序匹配事件"""
    
    def __init__(self, model: str, program_no: int, matched_string: str, match_type: str):
        """
        初始化程序匹配事件
        
        Args:
            model: 型号
            program_no: 匹配的程序编号
            matched_string: 匹配的字符串
            match_type: 匹配类型
        """
        self.model = model
        self.program_no = program_no
        self.matched_string = matched_string
        self.match_type = match_type


class ParametersCalculatedEvent:
    """参数计算事件"""
    
    def __init__(self, program_no: int, parameters: Dict[str, Any], calculation_steps: List[Dict]):
        """
        初始化参数计算事件
        
        Args:
            program_no: 程序编号
            parameters: 计算出的参数
            calculation_steps: 计算步骤
        """
        self.program_no = program_no
        self.parameters = parameters
        self.calculation_steps = calculation_steps


class NCCommunicationEvent:
    """NC通信事件"""
    
    def __init__(self, status: str, message: str, device_info: Dict[str, Any] = None):
        """
        初始化NC通信事件
        
        Args:
            status: 通信状态
            message: 通信消息
            device_info: 设备信息
        """
        self.status = status
        self.message = message
        self.device_info = device_info or {}


class ErrorEvent:
    """错误事件"""
    
    def __init__(self, error_type: str, message: str, details: Dict[str, Any] = None):
        """
        初始化错误事件
        
        Args:
            error_type: 错误类型
            message: 错误消息
            details: 错误详情
        """
        self.error_type = error_type
        self.message = message
        self.details = details or {}


class EventDispatcher(QObject):
    """事件分发器"""
    
    # 定义信号
    model_recognized = pyqtSignal(object)  # ModelRecognizedEvent
    program_matched = pyqtSignal(object)   # ProgramMatchedEvent
    parameters_calculated = pyqtSignal(object)  # ParametersCalculatedEvent
    nc_communication_status = pyqtSignal(object)  # NCCommunicationEvent
    error_occurred = pyqtSignal(object)    # ErrorEvent
    
    # 系统事件
    system_started = pyqtSignal()
    system_shutdown = pyqtSignal()
    config_changed = pyqtSignal(str)  # config_section
    
    # 界面事件
    ui_control_created = pyqtSignal(str, object)  # control_type, control
    ui_control_updated = pyqtSignal(str, object)  # control_type, control
    ui_control_deleted = pyqtSignal(str, object)  # control_type, control
    
    def __init__(self):
        """初始化事件分发器"""
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self._event_handlers = {}
        
    def publish_model_recognized(self, qr_code: str, model: str, po: str, quantity: str, recognition_mode: str) -> None:
        """
        发布型号识别事件
        
        Args:
            qr_code: 原始QR码
            model: 识别出的型号
            po: 识别出的PO号
            quantity: 识别出的数量
            recognition_mode: 识别模式
        """
        event = ModelRecognizedEvent(qr_code, model, po, quantity, recognition_mode)
        self.model_recognized.emit(event)
        self.logger.info(f"型号识别事件发布: {model}")
    
    def publish_program_matched(self, model: str, program_no: int, matched_string: str, match_type: str) -> None:
        """
        发布程序匹配事件
        
        Args:
            model: 型号
            program_no: 匹配的程序编号
            matched_string: 匹配的字符串
            match_type: 匹配类型
        """
        event = ProgramMatchedEvent(model, program_no, matched_string, match_type)
        self.program_matched.emit(event)
        self.logger.info(f"程序匹配事件发布: 程序{program_no} 匹配型号{model}")
    
    def publish_parameters_calculated(self, program_no: int, parameters: Dict[str, Any], calculation_steps: List[Dict]) -> None:
        """
        发布参数计算事件
        
        Args:
            program_no: 程序编号
            parameters: 计算出的参数
            calculation_steps: 计算步骤
        """
        event = ParametersCalculatedEvent(program_no, parameters, calculation_steps)
        self.parameters_calculated.emit(event)
        self.logger.info(f"参数计算事件发布: 程序{program_no} 参数数量{len(parameters)}")
    
    def publish_nc_communication_status(self, status: str, message: str, device_info: Dict[str, Any] = None) -> None:
        """
        发布NC通信事件
        
        Args:
            status: 通信状态
            message: 通信消息
            device_info: 设备信息
        """
        event = NCCommunicationEvent(status, message, device_info)
        self.nc_communication_status.emit(event)
        self.logger.info(f"NC通信事件发布: {status} - {message}")
    
    def publish_error(self, error_type: str, message: str, details: Dict[str, Any] = None) -> None:
        """
        发布错误事件
        
        Args:
            error_type: 错误类型
            message: 错误消息
            details: 错误详情
        """
        event = ErrorEvent(error_type, message, details)
        self.error_occurred.emit(event)
        self.logger.error(f"错误事件发布: {error_type} - {message}")
    
    def publish_system_started(self) -> None:
        """发布系统启动事件"""
        self.system_started.emit()
        self.logger.info("系统启动事件发布")
    
    def publish_system_shutdown(self) -> None:
        """发布系统关闭事件"""
        self.system_shutdown.emit()
        self.logger.info("系统关闭事件发布")
    
    def publish_config_changed(self, config_section: str) -> None:
        """
        发布配置变更事件
        
        Args:
            config_section: 配置节名称
        """
        self.config_changed.emit(config_section)
        self.logger.info(f"配置变更事件发布: {config_section}")
    
    def publish_ui_control_created(self, control_type: str, control: Any) -> None:
        """
        发布UI控件创建事件
        
        Args:
            control_type: 控件类型
            control: 控件对象
        """
        self.ui_control_created.emit(control_type, control)
        self.logger.debug(f"UI控件创建事件发布: {control_type}")
    
    def publish_ui_control_updated(self, control_type: str, control: Any) -> None:
        """
        发布UI控件更新事件
        
        Args:
            control_type: 控件类型
            control: 控件对象
        """
        self.ui_control_updated.emit(control_type, control)
        self.logger.debug(f"UI控件更新事件发布: {control_type}")
    
    def publish_ui_control_deleted(self, control_type: str, control: Any) -> None:
        """
        发布UI控件删除事件
        
        Args:
            control_type: 控件类型
            control: 控件对象
        """
        self.ui_control_deleted.emit(control_type, control)
        self.logger.debug(f"UI控件删除事件发布: {control_type}")
    
    def subscribe(self, event_type: str, handler: Callable) -> None:
        """
        订阅事件
        
        Args:
            event_type: 事件类型
            handler: 事件处理函数
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        
        if handler not in self._event_handlers[event_type]:
            self._event_handlers[event_type].append(handler)
            self.logger.debug(f"事件订阅: {event_type}")
    
    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """
        取消订阅事件
        
        Args:
            event_type: 事件类型
            handler: 事件处理函数
        """
        if event_type in self._event_handlers and handler in self._event_handlers[event_type]:
            self._event_handlers[event_type].remove(handler)
            self.logger.debug(f"事件取消订阅: {event_type}")
    
    def clear_subscriptions(self, event_type: str = None) -> None:
        """
        清除事件订阅
        
        Args:
            event_type: 事件类型，如果为None则清除所有
        """
        if event_type:
            if event_type in self._event_handlers:
                del self._event_handlers[event_type]
                self.logger.debug(f"清除事件订阅: {event_type}")
        else:
            self._event_handlers.clear()
            self.logger.debug("清除所有事件订阅")
    
    @pyqtSlot(object)
    def on_model_recognized(self, event: ModelRecognizedEvent) -> None:
        """型号识别事件处理槽"""
        self._call_handlers('model_recognized', event)
    
    @pyqtSlot(object)
    def on_program_matched(self, event: ProgramMatchedEvent) -> None:
        """程序匹配事件处理槽"""
        self._call_handlers('program_matched', event)
    
    @pyqtSlot(object)
    def on_parameters_calculated(self, event: ParametersCalculatedEvent) -> None:
        """参数计算事件处理槽"""
        self._call_handlers('parameters_calculated', event)
    
    @pyqtSlot(object)
    def on_nc_communication_status(self, event: NCCommunicationEvent) -> None:
        """NC通信事件处理槽"""
        self._call_handlers('nc_communication_status', event)
    
    @pyqtSlot(object)
    def on_error_occurred(self, event: ErrorEvent) -> None:
        """错误事件处理槽"""
        self._call_handlers('error_occurred', event)
    
    def _call_handlers(self, event_type: str, event: Any) -> None:
        """
        调用事件处理函数
        
        Args:
            event_type: 事件类型
            event: 事件对象
        """
        if event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    self.logger.error(f"事件处理函数执行失败: {event_type}, 错误: {e}")


class EventManager:
    """事件管理器（单例模式）"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._dispatcher = None
        return cls._instance
    
    def get_dispatcher(self) -> EventDispatcher:
        """
        获取事件分发器
        
        Returns:
            EventDispatcher: 事件分发器实例
        """
        if self._dispatcher is None:
            self._dispatcher = EventDispatcher()
        return self._dispatcher
    
    def set_dispatcher(self, dispatcher: EventDispatcher) -> None:
        """
        设置事件分发器
        
        Args:
            dispatcher: 事件分发器实例
        """
        self._dispatcher = dispatcher
