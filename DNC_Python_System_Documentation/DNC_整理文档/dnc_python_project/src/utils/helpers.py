"""
辅助工具模块
提供各种通用辅助函数
"""

import os
import re
import time
import hashlib
import functools
from pathlib import Path
from typing import Any, Callable, Optional, Dict, List, Union
from datetime import datetime, timedelta


def format_size(size_bytes: int) -> str:
    """
    格式化文件大小
    
    Args:
        size_bytes: 文件大小（字节）
        
    Returns:
        str: 格式化后的文件大小
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"


def validate_path(path: Union[str, Path], 
                 check_exists: bool = False,
                 check_writable: bool = False,
                 create_if_missing: bool = False) -> Dict[str, Any]:
    """
    验证路径
    
    Args:
        path: 要验证的路径
        check_exists: 是否检查路径存在
        check_writable: 是否检查可写权限
        create_if_missing: 如果路径不存在是否创建
        
    Returns:
        Dict[str, Any]: 验证结果
    """
    result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "path": str(path),
        "exists": False,
        "is_file": False,
        "is_dir": False,
        "writable": False
    }
    
    try:
        path_obj = Path(path)
        
        # 检查路径存在
        if path_obj.exists():
            result["exists"] = True
            result["is_file"] = path_obj.is_file()
            result["is_dir"] = path_obj.is_dir()
        else:
            if check_exists:
                result["valid"] = False
                result["errors"].append("路径不存在")
            
            # 如果路径不存在但需要创建
            if create_if_missing:
                try:
                    if path.endswith(('/', '\\')) or '.' not in path_obj.name:
                        # 可能是目录
                        path_obj.mkdir(parents=True, exist_ok=True)
                        result["exists"] = True
                        result["is_dir"] = True
                        result["warnings"].append("目录已自动创建")
                    else:
                        # 可能是文件，创建父目录
                        path_obj.parent.mkdir(parents=True, exist_ok=True)
                        result["exists"] = False
                        result["is_file"] = True
                        result["warnings"].append("文件父目录已创建")
                except Exception as e:
                    result["valid"] = False
                    result["errors"].append(f"创建路径失败: {e}")
        
        # 检查可写权限
        if check_writable and result["exists"]:
            try:
                if result["is_dir"]:
                    # 检查目录是否可写
                    test_file = path_obj / ".write_test"
                    test_file.touch()
                    test_file.unlink()
                else:
                    # 检查文件是否可写
                    with open(path_obj, 'a'):
                        pass
                result["writable"] = True
            except Exception:
                result["writable"] = False
                if check_writable:
                    result["valid"] = False
                    result["errors"].append("路径不可写")
        
    except Exception as e:
        result["valid"] = False
        result["errors"].append(f"路径验证异常: {e}")
    
    return result


def safe_execute(func: Callable, *args, default: Any = None, 
                error_message: str = None, **kwargs) -> Any:
    """
    安全执行函数，捕获异常
    
    Args:
        func: 要执行的函数
        *args: 函数参数
        default: 出错时的默认返回值
        error_message: 自定义错误消息
        **kwargs: 函数关键字参数
        
    Returns:
        Any: 函数执行结果或默认值
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if error_message:
            print(f"{error_message}: {e}")
        else:
            print(f"执行函数 {func.__name__} 时出错: {e}")
        return default


def retry_on_failure(max_attempts: int = 3, delay: float = 1.0, 
                    backoff: float = 2.0, exceptions: tuple = (Exception,)):
    """
    重试装饰器
    
    Args:
        max_attempts: 最大尝试次数
        delay: 初始延迟时间（秒）
        backoff: 延迟倍数
        exceptions: 要捕获的异常类型
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        raise last_exception
            
            raise last_exception  # 这行通常不会执行
        
        return wrapper
    return decorator


def calculate_file_hash(file_path: Union[str, Path], 
                       algorithm: str = "md5") -> Optional[str]:
    """
    计算文件哈希值
    
    Args:
        file_path: 文件路径
        algorithm: 哈希算法（md5, sha1, sha256）
        
    Returns:
        Optional[str]: 文件哈希值，计算失败返回None
    """
    try:
        file_path = Path(file_path)
        if not file_path.exists() or not file_path.is_file():
            return None
        
        hash_func = getattr(hashlib, algorithm)()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()
    
    except Exception:
        return None


def parse_nc_program(program_data: str) -> Dict[str, Any]:
    """
    解析NC程序
    
    Args:
        program_data: NC程序数据
        
    Returns:
        Dict[str, Any]: 解析结果
    """
    result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "line_count": 0,
        "commands": [],
        "program_name": "",
        "tool_calls": []
    }
    
    if not program_data:
        result["valid"] = False
        result["errors"].append("程序数据为空")
        return result
    
    lines = program_data.strip().split('\n')
    result["line_count"] = len(lines)
    
    # 检查程序头
    if lines and lines[0].startswith('%'):
        result["program_name"] = lines[0].strip('%').strip()
    
    # 解析程序内容
    for i, line in enumerate(lines):
        line = line.strip()
        if not line or line.startswith(';') or line.startswith('('):
            continue  # 跳过空行和注释
        
        # 解析G代码和M代码
        g_match = re.findall(r'G(\d+)', line)
        m_match = re.findall(r'M(\d+)', line)
        
        if g_match or m_match:
            command_info = {
                "line_number": i + 1,
                "content": line,
                "g_codes": g_match,
                "m_codes": m_match
            }
            result["commands"].append(command_info)
        
        # 检测刀具调用
        if 'T' in line:
            tool_match = re.search(r'T(\d+)', line)
            if tool_match:
                result["tool_calls"].append({
                    "line_number": i + 1,
                    "tool_number": int(tool_match.group(1))
                })
    
    return result


def format_timestamp(timestamp: Union[float, datetime] = None, 
                    format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    格式化时间戳
    
    Args:
        timestamp: 时间戳或datetime对象
        format_str: 时间格式字符串
        
    Returns:
        str: 格式化后的时间字符串
    """
    if timestamp is None:
        timestamp = time.time()
    
    if isinstance(timestamp, datetime):
        dt = timestamp
    else:
        dt = datetime.fromtimestamp(timestamp)
    
    return dt.strftime(format_str)


def parse_timestamp(time_str: str, 
                   format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """
    解析时间字符串
    
    Args:
        time_str: 时间字符串
        format_str: 时间格式字符串
        
    Returns:
        Optional[datetime]: 解析后的datetime对象，解析失败返回None
    """
    try:
        return datetime.strptime(time_str, format_str)
    except ValueError:
        return None


def get_time_difference(start_time: Union[float, datetime],
                       end_time: Union[float, datetime] = None) -> timedelta:
    """
    计算时间差
    
    Args:
        start_time: 开始时间
        end_time: 结束时间，如果为None则使用当前时间
        
    Returns:
        timedelta: 时间差
    """
    if end_time is None:
        end_time = time.time()
    
    if isinstance(start_time, datetime):
        start_dt = start_time
    else:
        start_dt = datetime.fromtimestamp(start_time)
    
    if isinstance(end_time, datetime):
        end_dt = end_time
    else:
        end_dt = datetime.fromtimestamp(end_time)
    
    return end_dt - start_dt


def format_time_difference(delta: timedelta) -> str:
    """
    格式化时间差
    
    Args:
        delta: 时间差
        
    Returns:
        str: 格式化后的时间差
    """
    total_seconds = int(delta.total_seconds())
    
    if total_seconds < 60:
        return f"{total_seconds}秒"
    elif total_seconds < 3600:
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}分{seconds}秒"
    else:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours}时{minutes}分{seconds}秒"


def validate_ip_address(ip: str) -> bool:
    """
    验证IP地址格式
    
    Args:
        ip: IP地址字符串
        
    Returns:
        bool: 是否为有效的IP地址
    """
    pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
    if not re.match(pattern, ip):
        return False
    
    parts = ip.split('.')
    for part in parts:
        if not 0 <= int(part) <= 255:
            return False
    
    return True


def validate_port(port: int) -> bool:
    """
    验证端口号
    
    Args:
        port: 端口号
        
    Returns:
        bool: 是否为有效的端口号
    """
    return 1 <= port <= 65535


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除非法字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        str: 清理后的文件名
    """
    # 移除Windows文件名中的非法字符
    illegal_chars = r'[<>:"/\\|?*\x00-\x1f]'
    sanitized = re.sub(illegal_chars, '_', filename)
    
    # 移除开头和结尾的点号及空格
    sanitized = sanitized.strip('. ')
    
    # 如果文件名为空，使用默认名称
    if not sanitized:
        sanitized = "unnamed_file"
    
    return sanitized


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    将列表分块
    
    Args:
        lst: 要分块的列表
        chunk_size: 每块的大小
        
    Returns:
        List[List[Any]]: 分块后的列表
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def flatten_list(nested_list: List[Any]) -> List[Any]:
    """
    展平嵌套列表
    
    Args:
        nested_list: 嵌套列表
        
    Returns:
        List[Any]: 展平后的列表
    """
    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result


def deep_get(dictionary: Dict, keys: str, default: Any = None) -> Any:
    """
    深度获取字典值
    
    Args:
        dictionary: 字典对象
        keys: 键路径，用点号分隔
        default: 默认值
        
    Returns:
        Any: 获取的值或默认值
    """
    try:
        keys_list = keys.split('.')
        current = dictionary
        for key in keys_list:
            current = current[key]
        return current
    except (KeyError, TypeError):
        return default


def deep_set(dictionary: Dict, keys: str, value: Any) -> None:
    """
    深度设置字典值
    
    Args:
        dictionary: 字典对象
        keys: 键路径，用点号分隔
        value: 要设置的值
    """
    keys_list = keys.split('.')
    current = dictionary
    
    for key in keys_list[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    
    current[keys_list[-1]] = value
