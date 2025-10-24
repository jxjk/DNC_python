"""
NC通信器
负责与数控设备进行通信
"""

import logging
import time
import threading
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
import serial
import socket

from ..core.config import ConfigManager


@dataclass
class CommunicationStatus:
    """通信状态"""
    status: str  # connected, disconnected, error, sending, receiving
    message: str
    device_info: Dict[str, Any]
    timestamp: float


@dataclass
class NCCommand:
    """NC命令"""
    command_id: str
    command_type: str  # read, write, execute, query
    data: Any
    parameters: Dict[str, Any]
    timeout: float


@dataclass
class NCResponse:
    """NC响应"""
    command_id: str
    success: bool
    data: Any
    error_message: Optional[str] = None
    response_time: Optional[float] = None


class NCCommunicator:
    """NC通信器"""
    
    def __init__(self, config_manager: ConfigManager):
        """
        初始化NC通信器
        
        Args:
            config_manager: 配置管理器
        """
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        
        # 通信配置
        self.com_config = self.config_manager.com_config
        self.device_config = self.config_manager.device_config
        
        # 通信状态
        self._connected = False
        self._connection_lock = threading.Lock()
        self._communication_thread = None
        self._stop_communication = False
        
        # 通信对象
        self._serial_connection = None
        self._socket_connection = None
        
        # 回调函数
        self._status_callbacks: List[Callable] = []
        self._response_callbacks: Dict[str, Callable] = {}
        
        # 命令队列
        self._command_queue = []
        self._command_lock = threading.Lock()
        
    def connect(self) -> bool:
        """
        连接到NC设备
        
        Returns:
            bool: 连接是否成功
        """
        with self._connection_lock:
            if self._connected:
                self.logger.warning("已经连接到NC设备")
                return True
            
            try:
                if self.com_config.com_type == 0:  # 串口通信
                    success = self._connect_serial()
                elif self.com_config.com_type == 1:  # 网络通信
                    success = self._connect_socket()
                else:
                    self.logger.error(f"不支持的通信类型: {self.com_config.com_type}")
                    return False
                
                if success:
                    self._connected = True
                    self._start_communication_thread()
                    self.logger.info("NC设备连接成功")
                else:
                    self.logger.error("NC设备连接失败")
                
                return success
                
            except Exception as e:
                self.logger.error(f"NC设备连接异常: {e}")
                return False
    
    def disconnect(self) -> bool:
        """
        断开与NC设备的连接
        
        Returns:
            bool: 断开是否成功
        """
        with self._connection_lock:
            if not self._connected:
                self.logger.warning("未连接到NC设备")
                return True
            
            try:
                self._stop_communication = True
                
                if self._communication_thread and self._communication_thread.is_alive():
                    self._communication_thread.join(timeout=5.0)
                
                if self.com_config.com_type == 0 and self._serial_connection:
                    self._serial_connection.close()
                    self._serial_connection = None
                elif self.com_config.com_type == 1 and self._socket_connection:
                    self._socket_connection.close()
                    self._socket_connection = None
                
                self._connected = False
                self.logger.info("NC设备断开连接成功")
                return True
                
            except Exception as e:
                self.logger.error(f"NC设备断开连接异常: {e}")
                return False
    
    def send_command(self, command: NCCommand, callback: Callable = None) -> str:
        """
        发送NC命令
        
        Args:
            command: NC命令
            callback: 响应回调函数
            
        Returns:
            str: 命令ID
        """
        if not self._connected:
            self.logger.error("未连接到NC设备，无法发送命令")
            return ""
        
        try:
            # 设置回调函数
            if callback:
                self._response_callbacks[command.command_id] = callback
            
            # 添加到命令队列
            with self._command_lock:
                self._command_queue.append(command)
            
            self.logger.info(f"NC命令已发送到队列: {command.command_id}")
            return command.command_id
            
        except Exception as e:
            self.logger.error(f"发送NC命令失败: {e}")
            return ""
    
    def read_data(self, address: str, length: int = 1) -> Optional[NCResponse]:
        """
        读取NC数据
        
        Args:
            address: 数据地址
            length: 数据长度
            
        Returns:
            Optional[NCResponse]: 读取响应
        """
        command = NCCommand(
            command_id=f"read_{int(time.time() * 1000)}",
            command_type="read",
            data={"address": address, "length": length},
            parameters={},
            timeout=self.com_config.timeout
        )
        
        return self._send_command_sync(command)
    
    def write_data(self, address: str, data: Any) -> Optional[NCResponse]:
        """
        写入NC数据
        
        Args:
            address: 数据地址
            data: 要写入的数据
            
        Returns:
            Optional[NCResponse]: 写入响应
        """
        command = NCCommand(
            command_id=f"write_{int(time.time() * 1000)}",
            command_type="write",
            data={"address": address, "data": data},
            parameters={},
            timeout=self.com_config.timeout
        )
        
        return self._send_command_sync(command)
    
    def execute_program(self, program_no: int, parameters: Dict[str, Any] = None) -> Optional[NCResponse]:
        """
        执行加工程序
        
        Args:
            program_no: 程序编号
            parameters: 程序参数
            
        Returns:
            Optional[NCResponse]: 执行响应
        """
        command = NCCommand(
            command_id=f"execute_{int(time.time() * 1000)}",
            command_type="execute",
            data={"program_no": program_no, "parameters": parameters or {}},
            parameters={},
            timeout=self.com_config.timeout * 2  # 执行程序需要更长时间
        )
        
        return self._send_command_sync(command)
    
    def query_status(self) -> Optional[NCResponse]:
        """
        查询NC设备状态
        
        Returns:
            Optional[NCResponse]: 状态查询响应
        """
        command = NCCommand(
            command_id=f"status_{int(time.time() * 1000)}",
            command_type="query",
            data={"query_type": "status"},
            parameters={},
            timeout=self.com_config.timeout
        )
        
        return self._send_command_sync(command)
    
    def add_status_callback(self, callback: Callable) -> None:
        """
        添加状态回调函数
        
        Args:
            callback: 状态回调函数
        """
        if callback not in self._status_callbacks:
            self._status_callbacks.append(callback)
    
    def remove_status_callback(self, callback: Callable) -> None:
        """
        移除状态回调函数
        
        Args:
            callback: 状态回调函数
        """
        if callback in self._status_callbacks:
            self._status_callbacks.remove(callback)
    
    def is_connected(self) -> bool:
        """
        检查是否连接到NC设备
        
        Returns:
            bool: 是否连接
        """
        return self._connected
    
    def get_connection_info(self) -> Dict[str, Any]:
        """
        获取连接信息
        
        Returns:
            Dict[str, Any]: 连接信息
        """
        return {
            "connected": self._connected,
            "com_type": self.com_config.com_type,
            "com_port": self.com_config.com_port if self.com_config.com_type == 0 else None,
            "ip_address": self.com_config.ip_address if self.com_config.com_type == 1 else None,
            "port": self.com_config.port if self.com_config.com_type == 1 else None,
            "device_name": self.device_config.device_name,
            "device_model": self.device_config.device_model
        }
    
    def _connect_serial(self) -> bool:
        """
        连接串口
        
        Returns:
            bool: 连接是否成功
        """
        try:
            self._serial_connection = serial.Serial(
                port=self.com_config.com_port,
                baudrate=self.com_config.baud_rate,
                bytesize=self.com_config.data_bits,
                parity=self.com_config.parity,
                stopbits=self.com_config.stop_bits,
                timeout=self.com_config.timeout
            )
            
            # 测试连接
            if self._serial_connection.is_open:
                self.logger.info(f"串口连接成功: {self.com_config.com_port}")
                return True
            else:
                self.logger.error(f"串口连接失败: {self.com_config.com_port}")
                return False
                
        except Exception as e:
            self.logger.error(f"串口连接异常: {e}")
            return False
    
    def _connect_socket(self) -> bool:
        """
        连接网络套接字
        
        Returns:
            bool: 连接是否成功
        """
        try:
            self._socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket_connection.settimeout(self.com_config.timeout)
            self._socket_connection.connect((self.com_config.ip_address, self.com_config.port))
            
            self.logger.info(f"网络连接成功: {self.com_config.ip_address}:{self.com_config.port}")
            return True
            
        except Exception as e:
            self.logger.error(f"网络连接异常: {e}")
            return False
    
    def _start_communication_thread(self) -> None:
        """启动通信线程"""
        self._stop_communication = False
        self._communication_thread = threading.Thread(target=self._communication_loop, daemon=True)
        self._communication_thread.start()
    
    def _communication_loop(self) -> None:
        """通信循环"""
        while not self._stop_communication:
            try:
                # 处理命令队列
                self._process_command_queue()
                
                # 检查连接状态
                self._check_connection_status()
                
                # 短暂休眠
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"通信循环异常: {e}")
                time.sleep(1.0)
    
    def _process_command_queue(self) -> None:
        """处理命令队列"""
        with self._command_lock:
            if not self._command_queue:
                return
            
            # 获取下一个命令
            command = self._command_queue.pop(0)
        
        try:
            # 发送命令
            start_time = time.time()
            response_data = self._send_raw_command(command)
            response_time = time.time() - start_time
            
            # 构建响应
            response = NCResponse(
                command_id=command.command_id,
                success=response_data is not None,
                data=response_data,
                response_time=response_time
            )
            
            # 调用回调函数
            if command.command_id in self._response_callbacks:
                try:
                    self._response_callbacks[command.command_id](response)
                    # 移除回调函数
                    del self._response_callbacks[command.command_id]
                except Exception as e:
                    self.logger.error(f"回调函数执行失败: {e}")
            
            self.logger.info(f"NC命令处理完成: {command.command_id}, 耗时: {response_time:.3f}s")
            
        except Exception as e:
            self.logger.error(f"处理NC命令失败: {command.command_id}, 错误: {e}")
            
            # 构建错误响应
            error_response = NCResponse(
                command_id=command.command_id,
                success=False,
                data=None,
                error_message=str(e)
            )
            
            # 调用回调函数
            if command.command_id in self._response_callbacks:
                try:
                    self._response_callbacks[command.command_id](error_response)
                    del self._response_callbacks[command.command_id]
                except Exception as e:
                    self.logger.error(f"错误回调函数执行失败: {e}")
    
    def _send_raw_command(self, command: NCCommand) -> Any:
        """
        发送原始命令
        
        Args:
            command: NC命令
            
        Returns:
            Any: 响应数据
        """
        if self.com_config.com_type == 0:  # 串口
            return self._send_serial_command(command)
        elif self.com_config.com_type == 1:  # 网络
            return self._send_socket_command(command)
        else:
            raise ValueError(f"不支持的通信类型: {self.com_config.com_type}")
    
    def _send_serial_command(self, command: NCCommand) -> Any:
        """
        发送串口命令
        
        Args:
            command: NC命令
            
        Returns:
            Any: 响应数据
        """
        if not self._serial_connection or not self._serial_connection.is_open:
            raise ConnectionError("串口未连接")
        
        # 构建命令数据
        command_data = self._build_command_data(command)
        
        # 发送命令
        self._serial_connection.write(command_data.encode())
        
        # 读取响应
        response_data = self._serial_connection.readline().decode().strip()
        
        return response_data
    
    def _send_socket_command(self, command: NCCommand) -> Any:
        """
        发送网络命令
        
        Args:
            command: NC命令
            
        Returns:
            Any: 响应数据
        """
        if not self._socket_connection:
            raise ConnectionError("网络未连接")
        
        # 构建命令数据
        command_data = self._build_command_data(command)
        
        # 发送命令
        self._socket_connection.send(command_data.encode())
        
        # 读取响应
        response_data = self._socket_connection.recv(1024).decode().strip()
        
        return response_data
    
    def _build_command_data(self, command: NCCommand) -> str:
        """
        构建命令数据
        
        Args:
            command: NC命令
            
        Returns:
            str: 命令数据字符串
        """
        # 根据命令类型构建不同的命令格式
        if command.command_type == "read":
            return f"READ {command.data['address']} {command.data['length']}\n"
        elif command.command_type == "write":
            return f"WRITE {command.data['address']} {command.data['data']}\n"
        elif command.command_type == "execute":
            params_str = " ".join([f"{k}={v}" for k, v in command.data['parameters'].items()])
            return f"EXECUTE {command.data['program_no']} {params_str}\n"
        elif command.command_type == "query":
            return f"QUERY {command.data['query_type']}\n"
        else:
            return f"COMMAND {command.command_type} {command.data}\n"
    
    def _send_command_sync(self, command: NCCommand) -> Optional[NCResponse]:
        """
        同步发送命令
        
        Args:
            command: NC命令
            
        Returns:
            Optional[NCResponse]: 命令响应
        """
        response_received = threading.Event()
        response_data = [None]
        
        def callback(response: NCResponse):
            response_data[0] = response
            response_received.set()
        
        # 发送命令
        command_id = self.send_command(command, callback)
        if not command_id:
            return None
        
        # 等待响应
        if response_received.wait(command.timeout):
            return response_data[0]
        else:
            self.logger.warning(f"NC命令超时: {command_id}")
            return NCResponse(
                command_id=command_id,
                success=False,
                data=None,
                error_message="命令超时"
            )
    
    def _check_connection_status(self) -> None:
        """检查连接状态"""
        try:
            if self.com_config.com_type == 0:  # 串口
                connected = self._serial_connection and self._serial_connection.is_open
            elif self.com_config.com_type == 1:  # 网络
                # 简单的连接检查
                connected = self._socket_connection is not None
            else:
                connected = False
            
            if connected != self._connected:
                self._connected = connected
                status_message = "连接成功" if connected else "连接断开"
                
                # 通知状态变化
                self._notify_status_change(status_message)
                
        except Exception as e:
            self.logger.error(f"检查连接状态异常: {e}")
    
    def _notify_status_change(self, message: str) -> None:
        """
        通知状态变化
        
        Args:
            message: 状态消息
        """
        status = CommunicationStatus(
            status="connected" if self._connected else "disconnected",
            message=message,
            device_info=self.get_connection_info(),
            timestamp=time.time()
        )
        
        for callback in self._status_callbacks:
            try:
                callback(status)
            except Exception as e:
                self.logger.error(f"状态回调函数执行失败: {e}")


class AdvancedNCCommunicator(NCCommunicator):
    """高级NC通信器"""
    
    def __init__(self, config_manager: ConfigManager):
        """
        初始化高级NC通信器
        
        Args:
            config_manager: 配置管理器
        """
        super().__init__(config_manager)
        
        # 命令历史
        self._command_history: List[Dict[str, Any]] = []
        self._max_history_size = 1000
        
        # 性能统计
        self._performance_stats = {
            "total_commands": 0,
            "successful_commands": 0,
            "failed_commands": 0,
            "average_response_time": 0.0,
            "last_command_time": 0.0
        }
    
    def send_command(self, command: NCCommand, callback: Callable = None) -> str:
        """
        发送NC命令（带性能统计）
        
        Args:
            command: NC命令
            callback: 响应回调函数
            
        Returns:
            str: 命令ID
        """
        command_id = super().send_command(command, callback)
        
        # 记录命令历史
        if command_id:
            command_record = {
                "command_id": command_id,
                "command_type": command.command_type,
                "timestamp": time.time(),
                "status": "queued"
            }
            self._command_history.append(command_record)
            
            # 限制历史记录大小
            if len(self._command_history) > self._max_history_size:
                self._command_history.pop(0)
        
        return command_id
    
    def get_command_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取命令历史
        
        Args:
            limit: 返回记录数量限制
            
        Returns:
            List[Dict[str, Any]]: 命令历史
        """
        return self._command_history[-limit:] if self._command_history else []
    
    def get_performance_statistics(self) -> Dict[str, Any]:
        """
        获取性能统计信息
        
        Returns:
            Dict[str, Any]: 性能统计信息
        """
        return self._performance_stats.copy()
    
    def clear_command_history(self) -> None:
        """清空命令历史"""
        self._command_history.clear()
    
    def _update_performance_stats(self, response: NCResponse) -> None:
        """
        更新性能统计
        
        Args:
            response: NC响应
        """
        self._performance_stats["total_commands"] += 1
        
        if response.success:
            self._performance_stats["successful_commands"] += 1
        else:
            self._performance_stats["failed_commands"] += 1
        
        if response.response_time:
            # 更新平均响应时间
            current_avg = self._performance_stats["average_response_time"]
            total_successful = self._performance_stats["successful_commands"]
            
            if total_successful > 1:
                new_avg = (current_avg * (total_successful - 1) + response.response_time) / total_successful
            else:
                new_avg = response.response_time
            
            self._performance_stats["average_response_time"] = round(new_avg, 3)
            self._performance_stats["last_command_time"] = response.response_time
        
        # 更新命令历史状态
        for record in self._command_history:
            if record["command_id"] == response.command_id:
                record["status"] = "success" if response.success else "failed"
                record["response_time"] = response.response_time
                record["error_message"] = response.error_message
                break
    
    def _process_command_queue(self) -> None:
        """处理命令队列（重写以包含性能统计）"""
        with self._command_lock:
            if not self._command_queue:
                return
            
            # 获取下一个命令
            command = self._command_queue.pop(0)
        
        try:
            # 发送命令
            start_time = time.time()
            response_data = self._send_raw_command(command)
            response_time = time.time() - start_time
            
            # 构建响应
            response = NCResponse(
                command_id=command.command_id,
                success=response_data is not None,
                data=response_data,
                response_time=response_time
            )
            
            # 更新性能统计
            self._update_performance_stats(response)
            
            # 调用回调函数
            if command.command_id in self._response_callbacks:
                try:
                    self._response_callbacks[command.command_id](response)
                    # 移除回调函数
                    del self._response_callbacks[command.command_id]
                except Exception as e:
                    self.logger.error(f"回调函数执行失败: {e}")
            
            self.logger.info(f"NC命令处理完成: {command.command_id}, 耗时: {response_time:.3f}s")
            
        except Exception as e:
            self.logger.error(f"处理NC命令失败: {command.command_id}, 错误: {e}")
            
            # 构建错误响应
            error_response = NCResponse(
                command_id=command.command_id,
                success=False,
                data=None,
                error_message=str(e)
            )
            
            # 更新性能统计
            self._update_performance_stats(error_response)
            
            # 调用回调函数
            if command.command_id in self._response_callbacks:
                try:
                    self._response_callbacks[command.command_id](error_response)
                    del self._response_callbacks[command.command_id]
                except Exception as e:
                    self.logger.error(f"错误回调函数执行失败: {e}")
