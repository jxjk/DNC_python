"""
错误处理模块
提供统一的错误处理机制
"""

import logging
import traceback
from typing import Optional, Dict, Any
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal

from src.utils.logger import get_logger


class ErrorHandler(QObject):
    """错误处理器"""
    
    error_occurred = pyqtSignal(str, str)  # error_message, context
    
    def __init__(self):
        """初始化错误处理器"""
        super().__init__()
        self.logger = get_logger(__name__)
    
    def handle_error(self, error: Exception, context: str = "未知操作") -> None:
        """
        处理错误
        
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
            from PyQt5.QtWidgets import QApplication, QMessageBox
            
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
