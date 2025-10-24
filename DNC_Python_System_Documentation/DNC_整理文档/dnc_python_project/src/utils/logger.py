"""
日志工具模块
提供统一的日志配置和管理功能
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any


class DncLogger:
    """DNC系统日志管理器"""
    
    def __init__(self):
        """初始化日志管理器"""
        self._loggers = {}
        self._default_level = logging.INFO
        self._log_dir = self._get_default_log_dir()
    
    def _get_default_log_dir(self) -> Path:
        """
        获取默认日志目录
        
        Returns:
            Path: 日志目录路径
        """
        # 尝试在项目根目录创建logs文件夹
        project_root = Path(__file__).parent.parent.parent
        log_dir = project_root / "logs"
        log_dir.mkdir(exist_ok=True)
        return log_dir
    
    def setup_logger(self, name: str = "dnc", 
                    level: int = None,
                    log_to_file: bool = True,
                    log_to_console: bool = True,
                    max_file_size: int = 10 * 1024 * 1024,  # 10MB
                    backup_count: int = 5) -> logging.Logger:
        """
        设置日志记录器
        
        Args:
            name: 日志记录器名称
            level: 日志级别
            log_to_file: 是否记录到文件
            log_to_console: 是否输出到控制台
            max_file_size: 日志文件最大大小（字节）
            backup_count: 备份文件数量
            
        Returns:
            logging.Logger: 配置好的日志记录器
        """
        if name in self._loggers:
            return self._loggers[name]
        
        level = level or self._default_level
        
        # 创建日志记录器
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.handlers.clear()  # 清除现有处理器
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 添加控制台处理器
        if log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # 添加文件处理器
        if log_to_file:
            log_file = self._log_dir / f"{name}.log"
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        # 防止日志传播到根记录器
        logger.propagate = False
        
        self._loggers[name] = logger
        return logger
    
    def get_logger(self, name: str = "dnc") -> logging.Logger:
        """
        获取日志记录器
        
        Args:
            name: 日志记录器名称
            
        Returns:
            logging.Logger: 日志记录器
        """
        if name in self._loggers:
            return self._loggers[name]
        else:
            return self.setup_logger(name)
    
    def set_log_level(self, name: str, level: int) -> None:
        """
        设置日志级别
        
        Args:
            name: 日志记录器名称
            level: 日志级别
        """
        logger = self.get_logger(name)
        logger.setLevel(level)
        for handler in logger.handlers:
            handler.setLevel(level)
    
    def get_log_file_path(self, name: str = "dnc") -> Optional[Path]:
        """
        获取日志文件路径
        
        Args:
            name: 日志记录器名称
            
        Returns:
            Optional[Path]: 日志文件路径，如果不存在则返回None
        """
        log_file = self._log_dir / f"{name}.log"
        return log_file if log_file.exists() else None
    
    def get_log_stats(self, name: str = "dnc") -> Dict[str, Any]:
        """
        获取日志统计信息
        
        Args:
            name: 日志记录器名称
            
        Returns:
            Dict[str, Any]: 日志统计信息
        """
        logger = self.get_logger(name)
        log_file = self.get_log_file_path(name)
        
        stats = {
            "name": name,
            "level": logging.getLevelName(logger.level),
            "handlers": len(logger.handlers),
            "log_file": str(log_file) if log_file else None
        }
        
        if log_file:
            try:
                file_size = log_file.stat().st_size
                stats["file_size"] = file_size
                stats["file_size_human"] = self._format_file_size(file_size)
            except OSError:
                stats["file_size"] = 0
                stats["file_size_human"] = "0 B"
        
        return stats
    
    def _format_file_size(self, size_bytes: int) -> str:
        """
        格式化文件大小
        
        Args:
            size_bytes: 文件大小（字节）
            
        Returns:
            str: 格式化后的文件大小
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def clear_logs(self, name: str = None) -> bool:
        """
        清除日志文件
        
        Args:
            name: 日志记录器名称，如果为None则清除所有日志
            
        Returns:
            bool: 清除是否成功
        """
        try:
            if name:
                log_file = self._log_dir / f"{name}.log"
                if log_file.exists():
                    log_file.unlink()
                    # 同时删除备份文件
                    for i in range(1, 10):  # 假设最多10个备份
                        backup_file = self._log_dir / f"{name}.log.{i}"
                        if backup_file.exists():
                            backup_file.unlink()
            else:
                # 清除所有日志文件
                for log_file in self._log_dir.glob("*.log*"):
                    log_file.unlink()
            
            return True
        except Exception as e:
            error_logger = self.get_logger("dnc_error")
            error_logger.error(f"清除日志文件失败: {e}")
            return False


# 全局日志管理器实例
_logger_manager = DncLogger()


def setup_logger(name: str = "dnc", **kwargs) -> logging.Logger:
    """
    设置日志记录器（便捷函数）
    
    Args:
        name: 日志记录器名称
        **kwargs: 其他参数
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    return _logger_manager.setup_logger(name, **kwargs)


def get_logger(name: str = "dnc") -> logging.Logger:
    """
    获取日志记录器（便捷函数）
    
    Args:
        name: 日志记录器名称
        
    Returns:
        logging.Logger: 日志记录器
    """
    return _logger_manager.get_logger(name)


def set_log_level(name: str, level: int) -> None:
    """
    设置日志级别（便捷函数）
    
    Args:
        name: 日志记录器名称
        level: 日志级别
    """
    _logger_manager.set_log_level(name, level)


def get_log_stats(name: str = "dnc") -> Dict[str, Any]:
    """
    获取日志统计信息（便捷函数）
    
    Args:
        name: 日志记录器名称
        
    Returns:
        Dict[str, Any]: 日志统计信息
    """
    return _logger_manager.get_log_stats(name)


def clear_logs(name: str = None) -> bool:
    """
    清除日志文件（便捷函数）
    
    Args:
        name: 日志记录器名称，如果为None则清除所有日志
        
    Returns:
        bool: 清除是否成功
    """
    return _logger_manager.clear_logs(name)


# 预定义的日志记录器
MAIN_LOGGER = setup_logger("dnc_main")
BUSINESS_LOGGER = setup_logger("dnc_business")
UI_LOGGER = setup_logger("dnc_ui")
COMMUNICATION_LOGGER = setup_logger("dnc_communication")
DATA_LOGGER = setup_logger("dnc_data")
ERROR_LOGGER = setup_logger("dnc_error", level=logging.ERROR)
