# error_handler.py
"""
错误处理模块
提供统一的错误处理机制
"""

import logging
import traceback
import json
from typing import Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal

from src.utils.logger import get_logger

class ErrorHandlingResult:
    """错误处理结果"""
    
    def __init__(self, should_stop: bool, error_message: str, recovery_action: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.should_stop = should_stop
        self.error_message = error_message
        self.recovery_action = recovery_action
        self.details = details
    
    def __repr__(self):
        return f"ErrorHandlingResult(should_stop={self.should_stop}, error_message='{self.error_message}', recovery_action={self.recovery_action}, details={self.details})"
    
    @classmethod
    def should_stop(cls, error_message: str, details: Dict[str, Any] = None) -> 'ErrorHandlingResult':
        """创建停止流程的结果"""
        return cls(should_stop=True, error_message=error_message, details=details)
    
    @classmethod
    def can_continue(cls, error_message: str, recovery_action: str = None, details: Dict[str, Any] = None) -> 'ErrorHandlingResult':
        """创建可继续流程的结果"""
        return cls(should_stop=False, error_message=error_message, recovery_action=recovery_action, details=details)
@dataclass
class ErrorContext:
    """错误上下文"""
    error_type: str
    module: str
    function: str
    timestamp: str
    user_action: str = ""
    system_state: Dict[str, Any] = None
    stack_trace: str = ""


class ErrorType(Enum):
    """错误类型枚举"""
    CONFIG_ERROR = "配置错误"
    CALCULATION_ERROR = "计算错误"
    DEVICE_ERROR = "设备错误"
    VALIDATION_ERROR = "验证错误"
    FILE_ERROR = "文件错误"
    NETWORK_ERROR = "网络错误"
    UNKNOWN_ERROR = "未知错误"


class ErrorHandlingError(Exception):
    """错误处理错误异常"""
    pass


class LoggingError(Exception):
    """日志记录错误异常"""
    pass


class ErrorHandlingFlow:
    """错误处理流程 - 按照标准流程实现统一错误处理"""
    
    def __init__(self, config_manager=None):
        """
        初始化错误处理流程
        
        Args:
            config_manager: 配置管理器实例（可选）
        """
        self.config_manager = config_manager
        self.logger = get_logger("ErrorHandlingFlow")
        self.error_history = []
        self.max_history_size = 1000
    
    def handle_error(self, error: Exception, context: Dict[str, Any]) -> ErrorHandlingResult:
        """
        统一错误处理流程
        
        Args:
            error: 异常对象
            context: 错误上下文信息
            
        Returns:
            ErrorHandlingResult: 处理结果
        """
        try:
            # 1. 记录错误日志
            self._log_error(error, context)
            
            # 2. 分类错误类型
            error_type = self._classify_error(error)
            
            # 3. 记录错误历史
            self._record_error_history(error, error_type, context)
            
            # 4. 根据错误类型采取不同策略
            if error_type == ErrorType.CONFIG_ERROR:
                return self._handle_config_error(error, context)
            elif error_type == ErrorType.CALCULATION_ERROR:
                return self._handle_calculation_error(error, context)
            elif error_type == ErrorType.DEVICE_ERROR:
                return self._handle_device_error(error, context)
            elif error_type == ErrorType.VALIDATION_ERROR:
                return self._handle_validation_error(error, context)
            elif error_type == ErrorType.FILE_ERROR:
                return self._handle_file_error(error, context)
            elif error_type == ErrorType.NETWORK_ERROR:
                return self._handle_network_error(error, context)
            else:
                return self._handle_unknown_error(error, context)
                
        except Exception as e:
            # 错误处理本身出错时的兜底处理
            self.logger.critical(f"错误处理流程失败: {str(e)}")
            return ErrorHandlingResult.should_stop(f"系统错误处理失败: {str(e)}")
    
    def _log_error(self, error: Exception, context: Dict[str, Any]) -> None:
        """记录错误日志"""
        try:
            error_context = self._build_error_context(error, context)
            
            # 根据错误级别记录日志
            if isinstance(error, (ValueError, TypeError)):
                self.logger.warning(f"{error_context.error_type}: {str(error)}", extra=context)
            elif isinstance(error, (FileNotFoundError, IOError)):
                self.logger.error(f"{error_context.error_type}: {str(error)}", extra=context)
            else:
                self.logger.critical(f"{error_context.error_type}: {str(error)}", extra=context)
                
        except Exception as e:
            self.logger.error(f"错误日志记录失败: {str(e)}")
    
    def _build_error_context(self, error: Exception, context: Dict[str, Any]) -> ErrorContext:
        """构建错误上下文"""
        import traceback
        
        return ErrorContext(
            error_type=type(error).__name__,
            module=context.get('module', 'unknown'),
            function=context.get('function', 'unknown'),
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            user_action=context.get('user_action', ''),
            system_state=context.get('system_state', {}),
            stack_trace=traceback.format_exc()
        )
    
    def _classify_error(self, error: Exception) -> ErrorType:
        """分类错误类型"""
        error_type_mapping = {
            'ConfigError': ErrorType.CONFIG_ERROR,
            'CalculationError': ErrorType.CALCULATION_ERROR,
            'DeviceError': ErrorType.DEVICE_ERROR,
            'ValidationError': ErrorType.VALIDATION_ERROR,
            'FileError': ErrorType.FILE_ERROR,
            'NetworkError': ErrorType.NETWORK_ERROR,
            'FileNotFoundError': ErrorType.FILE_ERROR,
            'IOError': ErrorType.FILE_ERROR,
            'ValueError': ErrorType.VALIDATION_ERROR,
            'TypeError': ErrorType.VALIDATION_ERROR,
        }
        
        error_name = type(error).__name__
        return error_type_mapping.get(error_name, ErrorType.UNKNOWN_ERROR)
    
    def _record_error_history(self, error: Exception, error_type: ErrorType, context: Dict[str, Any]) -> None:
        """记录错误历史"""
        try:
            error_record = {
                'timestamp': datetime.now().isoformat(),
                'error_type': error_type.value,
                'error_message': str(error),
                'module': context.get('module', 'unknown'),
                'function': context.get('function', 'unknown'),
                'user_action': context.get('user_action', '')
            }
            
            self.error_history.append(error_record)
            
            # 限制历史记录大小
            if len(self.error_history) > self.max_history_size:
                self.error_history = self.error_history[-self.max_history_size:]
                
        except Exception as e:
            self.logger.warning(f"错误历史记录失败: {str(e)}")
    
    def _handle_config_error(self, error: Exception, context: Dict[str, Any]) -> ErrorHandlingResult:
        """处理配置错误"""
        self.logger.error(f"配置错误处理: {str(error)}")
        
        # 配置错误通常需要停止流程
        return ErrorHandlingResult.should_stop(
            f"配置错误: {str(error)}",
            details={
                'config_file': context.get('config_file', 'unknown'),
                'config_key': context.get('config_key', 'unknown')
            }
        )
    
    def _handle_calculation_error(self, error: Exception, context: Dict[str, Any]) -> ErrorHandlingResult:
        """处理计算错误"""
        self.logger.warning(f"计算错误处理: {str(error)}")
        
        # 决定是否继续流程
        if self._is_critical_calculation_error(error):
            return ErrorHandlingResult.should_stop(f"关键计算错误: {str(error)}")
        else:
            recovery_action = "跳过该变量计算，使用默认值"
            return ErrorHandlingResult.can_continue(
                f"计算错误: {str(error)}",
                recovery_action=recovery_action,
                details={'variable_name': context.get('variable_name')}
            )
    
    def _is_critical_calculation_error(self, error: Exception) -> bool:
        """判断是否为关键计算错误"""
        critical_errors = [
            "除数不能为零",
            "无效的数学运算",
            "关键变量计算失败"
        ]
        
        error_message = str(error).lower()
        return any(critical_error in error_message for critical_error in critical_errors)
    
    def _handle_device_error(self, error: Exception, context: Dict[str, Any]) -> ErrorHandlingResult:
        """处理设备错误"""
        self.logger.error(f"设备错误处理: {str(error)}")
        
        # 设备错误通常需要停止流程
        recovery_action = "检查设备连接状态，重新初始化设备"
        return ErrorHandlingResult.should_stop(
            f"设备错误: {str(error)}",
            recovery_action=recovery_action,
            details={'device_id': context.get('device_id', 'unknown')}
        )
    
    def _handle_validation_error(self, error: Exception, context: Dict[str, Any]) -> ErrorHandlingResult:
        """处理验证错误"""
        self.logger.warning(f"验证错误处理: {str(error)}")
        
        # 验证错误通常可以继续，但需要用户确认
        recovery_action = "使用默认值或请求用户输入"
        return ErrorHandlingResult.can_continue(
            f"验证错误: {str(error)}",
            recovery_action=recovery_action,
            details={
                'validation_type': context.get('validation_type', 'unknown'),
                'invalid_value': context.get('invalid_value', 'unknown')
            }
        )
    
    def _handle_file_error(self, error: Exception, context: Dict[str, Any]) -> ErrorHandlingResult:
        """处理文件错误"""
        self.logger.error(f"文件错误处理: {str(error)}")
        
        # 文件错误根据严重程度决定是否停止
        if self._is_critical_file_error(error):
            return ErrorHandlingResult.should_stop(f"关键文件错误: {str(error)}")
        else:
            recovery_action = "使用备用文件或创建新文件"
            return ErrorHandlingResult.can_continue(
                f"文件错误: {str(error)}",
                recovery_action=recovery_action,
                details={'file_path': context.get('file_path', 'unknown')}
            )
    
    def _is_critical_file_error(self, error: Exception) -> bool:
        """判断是否为关键文件错误"""
        critical_errors = [
            "配置文件不存在",
            "无法读取配置文件",
            "关键文件写入失败"
        ]
        
        error_message = str(error).lower()
        return any(critical_error in error_message for critical_error in critical_errors)
    
    def _handle_network_error(self, error: Exception, context: Dict[str, Any]) -> ErrorHandlingResult:
        """处理网络错误"""
        self.logger.error(f"网络错误处理: {str(error)}")
        
        # 网络错误通常可以重试
        recovery_action = "重试连接或使用离线模式"
        return ErrorHandlingResult.can_continue(
            f"网络错误: {str(error)}",
            recovery_action=recovery_action,
            details={
                'endpoint': context.get('endpoint', 'unknown'),
                'retry_count': context.get('retry_count', 0)
            }
        )
    
    def _handle_unknown_error(self, error: Exception, context: Dict[str, Any]) -> ErrorHandlingResult:
        """处理未知错误"""
        self.logger.critical(f"未知错误处理: {str(error)}")
        
        # 未知错误通常需要停止流程
        return ErrorHandlingResult.should_stop(
            f"系统未知错误: {str(error)}",
            details={'error_type': type(error).__name__}
        )
    
    def get_error_statistics(self, time_range: str = "today") -> Dict[str, Any]:
        """获取错误统计信息"""
        try:
            now = datetime.now()
            
            if time_range == "today":
                start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif time_range == "week":
                start_time = now - timedelta(days=7)
            elif time_range == "month":
                start_time = now - timedelta(days=30)
            else:
                start_time = now - timedelta(days=1)  # 默认昨天
            
            filtered_errors = [
                error for error in self.error_history
                if datetime.fromisoformat(error['timestamp']) >= start_time
            ]
            
            statistics = {
                'total_errors': len(filtered_errors),
                'error_types': {},
                'modules': {},
                'time_range': time_range
            }
            
            for error in filtered_errors:
                # 统计错误类型
                error_type = error['error_type']
                statistics['error_types'][error_type] = statistics['error_types'].get(error_type, 0) + 1
                
                # 统计模块
                module = error['module']
                statistics['modules'][module] = statistics['modules'].get(module, 0) + 1
            
            return statistics
            
        except Exception as e:
            self.logger.error(f"错误统计获取失败: {str(e)}")
            return {'total_errors': 0, 'error_types': {}, 'modules': {}, 'time_range': time_range}
    
    def clear_error_history(self) -> None:
        """清空错误历史"""
        self.error_history.clear()
        self.logger.info("错误历史已清空")
    
    def export_error_report(self, file_path: str) -> bool:
        """导出错误报告"""
        try:
            report_data = {
                'export_time': datetime.now().isoformat(),
                'total_errors': len(self.error_history),
                'errors': self.error_history
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"错误报告已导出: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"错误报告导出失败: {str(e)}")
            return False


class ErrorHandler(QObject):
    """错误处理器"""
    
    error_occurred = pyqtSignal(str, str)  # error_message, context
    
    def __init__(self, config_manager=None):
        """
        初始化错误处理器
        
        Args:
            config_manager: 配置管理器实例（可选）
        """
        super().__init__()
        self.logger = get_logger("ErrorHandler")
        self.error_flow = ErrorHandlingFlow(config_manager)
    
    def handle(self, error: Exception, **context) -> ErrorHandlingResult:
        """
        处理错误
        
        Args:
            error: 异常对象
            **context: 错误上下文信息
            
        Returns:
            ErrorHandlingResult: 处理结果
        """
        try:
            self.logger.debug(f"处理错误: {type(error).__name__}")
            
            # 使用ErrorHandlingFlow处理错误
            result = self.error_flow.handle_error(error, context)
            
            if result.should_stop:
                self.logger.error(f"流程需要停止: {result.error_message}")
            else:
                self.logger.warning(f"流程可以继续: {result.error_message}")
            
            return result
            
        except Exception as e:
            self.logger.critical(f"错误处理失败: {str(e)}")
            return ErrorHandlingResult.should_stop(f"错误处理系统异常: {str(e)}")
    
    def handle_error(self, error: Exception, context: str = "未知操作") -> None:
        """
        处理错误（兼容旧接口）
        
        Args:
            error: 异常对象
            context: 错误发生的上下文
        """
        error_message = str(error)
        error_traceback = traceback.format_exc()
        
        # 记录错误日志
        self.logger.error(f"在 {context} 中发生错误: {error_message}")
        self.logger.debug(f"错误堆栈: {error_traceback}")
        
        # 发送错误信号
        self.error_occurred.emit(error_message, context)
        
        # 显示错误对话框
        self._show_error_dialog(error_message, context)
    
    def handle_warning(self, warning_message: str, context: str = "未知操作") -> None:
        """
        处理警告
        
        Args:
            warning_message: 警告消息
            context: 警告发生的上下文
        """
        self.logger.warning(f"在 {context} 中发生警告: {warning_message}")
    
    def handle_info(self, info_message: str, context: str = "未知操作") -> None:
        """
        处理信息
        
        Args:
            info_message: 信息消息
            context: 信息发生的上下文
        """
        self.logger.info(f"在 {context} 中: {info_message}")
    
    def _show_error_dialog(self, error_message: str, context: str) -> None:
        """
        显示错误对话框
        
        Args:
            error_message: 错误消息
            context: 错误发生的上下文
        """
        try:
            from PyQt5.QtWidgets import QApplication
            
            app = QApplication.instance()
            if app:
                # 在主线程中显示对话框
                QMessageBox.critical(
                    None,
                    f"错误 - {context}",
                    f"发生错误: {error_message}\n\n请检查系统配置或联系技术支持。",
                    QMessageBox.Ok
                )
        except Exception as e:
            # 如果无法显示对话框，则记录日志
            self.logger.error(f"无法显示错误对话框: {e}")
    
    def validate_config(self, config_data: Dict[str, Any]) -> bool:
        """
        验证配置数据
        
        Args:
            config_data: 配置数据字典
            
        Returns:
            bool: 配置是否有效
        """
        required_keys = ['BarCodeHeaderStrNum', 'QRmode']
        
        for key in required_keys:
            if key not in config_data:
                self.handle_error(
                    ValueError(f"缺少必需的配置项: {key}"),
                    "配置验证"
                )
                return False
        
        try:
            # 验证数值配置
            barcode_header_num = int(config_data.get('BarCodeHeaderStrNum', '0'))
            qr_mode = int(config_data.get('QRmode', '0'))
            
            if barcode_header_num < 0:
                self.handle_error(
                    ValueError("BarCodeHeaderStrNum 必须为非负数"),
                    "配置验证"
                )
                return False
            
            if qr_mode not in [0, 1]:
                self.handle_error(
                    ValueError("QRmode 必须为 0 或 1"),
                    "配置验证"
                )
                return False
                
        except ValueError as e:
            self.handle_error(e, "配置验证")
            return False
        
        return True
    
    def validate_model_string(self, model_string: str) -> bool:
        """
        验证型号字符串
        
        Args:
            model_string: 型号字符串
            
        Returns:
            bool: 型号字符串是否有效
        """
        if not model_string or not isinstance(model_string, str):
            self.handle_error(
                ValueError("型号字符串不能为空"),
                "型号验证"
            )
            return False
        
        if len(model_string.strip()) == 0:
            self.handle_error(
                ValueError("型号字符串不能只包含空白字符"),
                "型号验证"
            )
            return False
        
        return True
    
    def validate_program_data(self, program_data: Dict[str, Any]) -> bool:
        """
        验证程序数据
        
        Args:
            program_data: 程序数据字典
            
        Returns:
            bool: 程序数据是否有效
        """
        required_keys = ['NO', 'TYPE']
        
        for key in required_keys:
            if key not in program_data:
                self.handle_error(
                    ValueError(f"程序数据缺少必需的字段: {key}"),
                    "程序数据验证"
                )
                return False
        
        try:
            program_no = int(program_data['NO'])
            if program_no <= 0:
                self.handle_error(
                    ValueError("程序编号必须为正整数"),
                    "程序数据验证"
                )
                return False
        except ValueError as e:
            self.handle_error(e, "程序数据验证")
            return False
        
        return True
    
    def get_statistics(self, time_range: str = "today") -> Dict[str, Any]:
        """获取错误统计"""
        return self.error_flow.get_error_statistics(time_range)
    
    def clear_history(self) -> None:
        """清空错误历史"""
        self.error_flow.clear_error_history()
    
    def export_report(self, file_path: str) -> bool:
        """导出错误报告"""
        return self.error_flow.export_error_report(file_path)


# 全局错误处理器实例
_global_error_handler: Optional[ErrorHandler] = None


def get_global_error_handler() -> ErrorHandler:
    """
    获取全局错误处理器实例
    
    Returns:
        ErrorHandler: 全局错误处理器实例
    """
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()
    return _global_error_handler


def handle_global_error(error: Exception, context: str = "未知操作") -> None:
    """
    使用全局错误处理器处理错误
    
    Args:
        error: 异常对象
        context: 错误发生的上下文
    """
    error_handler = get_global_error_handler()
    error_handler.handle_error(error, context)


def handle_errors(func):
    """
    错误处理装饰器
    用于统一处理函数中的异常
    
    Args:
        func: 被装饰的函数
        
    Returns:
        装饰后的函数
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # 获取函数名和模块信息
            func_name = func.__name__
            module_name = func.__module__
            
            # 构建错误上下文
            context = {
                'module': module_name,
                'function': func_name,
                'args': str(args),
                'kwargs': str(kwargs)
            }
            
            # 使用全局错误处理器处理错误
            error_handler = get_global_error_handler()
            result = error_handler.handle(e, **context)
            
            # 根据处理结果决定是否重新抛出异常
            if result.should_stop:
                # 对于需要停止的严重错误，重新抛出异常
                raise e
            else:
                # 对于可以继续的错误，返回默认值或None
                return None
                
    return wrapper
