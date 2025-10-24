"""
命名管道通信模块
负责通过命名管道与外部系统通信
"""

import os
import time
import threading
import logging
from typing import Optional, Callable, Dict, Any
from pathlib import Path


class NamedPipeClient:
    """命名管道客户端"""
    
    def __init__(self, pipe_name: str = "dnc_pipe"):
        """
        初始化命名管道客户端
        
        Args:
            pipe_name: 管道名称
        """
        self.pipe_name = pipe_name
        self.pipe_path = f"\\\\.\\pipe\\{pipe_name}"
        self.logger = logging.getLogger(__name__)
        self.is_connected = False
        self._pipe_handle = None
    
    def connect(self, timeout: float = 10.0) -> bool:
        """
        连接到命名管道
        
        Args:
            timeout: 连接超时时间（秒）
            
        Returns:
            bool: 连接是否成功
        """
        try:
            self.logger.info(f"尝试连接到命名管道: {self.pipe_path}")
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    # 在Windows上使用win32pipe或类似库
                    # 这里使用模拟实现
                    self._pipe_handle = f"pipe_handle_{self.pipe_name}"
                    self.is_connected = True
                    self.logger.info(f"命名管道连接成功: {self.pipe_path}")
                    return True
                    
                except Exception as e:
                    self.logger.debug(f"连接尝试失败: {e}")
                    time.sleep(0.1)
            
            self.logger.error(f"连接命名管道超时: {self.pipe_path}")
            return False
            
        except Exception as e:
            self.logger.error(f"连接命名管道异常: {e}")
            return False
    
    def disconnect(self) -> bool:
        """
        断开命名管道连接
        
        Returns:
            bool: 断开是否成功
        """
        try:
            if self.is_connected:
                self._pipe_handle = None
                self.is_connected = False
                self.logger.info(f"命名管道连接已断开: {self.pipe_path}")
            return True
        except Exception as e:
            self.logger.error(f"断开命名管道连接异常: {e}")
            return False
    
    def send_message(self, message: str, timeout: float = 5.0) -> bool:
        """
        发送消息到命名管道
        
        Args:
            message: 消息内容
            timeout: 发送超时时间（秒）
            
        Returns:
            bool: 发送是否成功
        """
        if not self.is_connected:
            self.logger.error("未连接到命名管道")
            return False
        
        try:
            self.logger.debug(f"发送消息到命名管道: {message}")
            
            # 模拟发送过程
            # 在实际实现中，这里应该使用Windows API写入管道
            time.sleep(0.01)  # 模拟网络延迟
            
            self.logger.debug("消息发送成功")
            return True
            
        except Exception as e:
            self.logger.error(f"发送消息到命名管道失败: {e}")
            return False
    
    def receive_message(self, timeout: float = 5.0) -> Optional[str]:
        """
        从命名管道接收消息
        
        Args:
            timeout: 接收超时时间（秒）
            
        Returns:
            Optional[str]: 接收到的消息，接收失败返回None
        """
        if not self.is_connected:
            self.logger.error("未连接到命名管道")
            return None
        
        try:
            self.logger.debug("等待从命名管道接收消息")
            
            # 模拟接收过程
            # 在实际实现中，这里应该使用Windows API读取管道
            start_time = time.time()
            while time.time() - start_time < timeout:
                # 检查是否有可用数据
                # 这里返回模拟数据
                sample_message = f"模拟响应消息 - {time.time()}"
                self.logger.debug(f"接收到消息: {sample_message}")
                return sample_message
            
            self.logger.warning("接收消息超时")
            return None
            
        except Exception as e:
            self.logger.error(f"从命名管道接收消息失败: {e}")
            return None
    
    def send_command(self, command: str, parameters: Dict[str, Any] = None, 
                    timeout: float = 5.0) -> Dict[str, Any]:
        """
        发送命令到命名管道
        
        Args:
            command: 命令名称
            parameters: 命令参数
            timeout: 超时时间（秒）
            
        Returns:
            Dict[str, Any]: 命令执行结果
        """
        try:
            parameters = parameters or {}
            message_data = {
                "command": command,
                "parameters": parameters,
                "timestamp": time.time()
            }
            
            # 将消息转换为字符串格式
            import json
            message_str = json.dumps(message_data)
            
            if self.send_message(message_str, timeout):
                response = self.receive_message(timeout)
                if response:
                    try:
                        return json.loads(response)
                    except json.JSONDecodeError:
                        return {"success": False, "error": "响应格式错误"}
                else:
                    return {"success": False, "error": "接收响应超时"}
            else:
                return {"success": False, "error": "发送命令失败"}
                
        except Exception as e:
            self.logger.error(f"发送命令异常: {e}")
            return {"success": False, "error": str(e)}


class NamedPipeServer:
    """命名管道服务器"""
    
    def __init__(self, pipe_name: str = "dnc_pipe", max_connections: int = 1):
        """
        初始化命名管道服务器
        
        Args:
            pipe_name: 管道名称
            max_connections: 最大连接数
        """
        self.pipe_name = pipe_name
        self.pipe_path = f"\\\\.\\pipe\\{pipe_name}"
        self.max_connections = max_connections
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        self._server_thread = None
        self._message_handler = None
        self._clients = {}
    
    def start(self, message_handler: Callable[[str], str] = None) -> bool:
        """
        启动命名管道服务器
        
        Args:
            message_handler: 消息处理函数
            
        Returns:
            bool: 启动是否成功
        """
        try:
            if self.is_running:
                self.logger.warning("命名管道服务器已在运行")
                return True
            
            self._message_handler = message_handler or self._default_message_handler
            self.is_running = True
            
            # 启动服务器线程
            self._server_thread = threading.Thread(
                target=self._server_loop,
                daemon=True,
                name=f"NamedPipeServer-{self.pipe_name}"
            )
            self._server_thread.start()
            
            self.logger.info(f"命名管道服务器已启动: {self.pipe_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"启动命名管道服务器失败: {e}")
            return False
    
    def stop(self) -> bool:
        """
        停止命名管道服务器
        
        Returns:
            bool: 停止是否成功
        """
        try:
            if not self.is_running:
                self.logger.warning("命名管道服务器未在运行")
                return True
            
            self.is_running = False
            
            # 等待服务器线程结束
            if self._server_thread and self._server_thread.is_alive():
                self._server_thread.join(timeout=5.0)
            
            self.logger.info("命名管道服务器已停止")
            return True
            
        except Exception as e:
            self.logger.error(f"停止命名管道服务器异常: {e}")
            return False
    
    def _server_loop(self) -> None:
        """服务器主循环"""
        self.logger.info("命名管道服务器主循环开始")
        
        while self.is_running:
            try:
                # 模拟服务器循环
                # 在实际实现中，这里应该创建管道并等待客户端连接
                time.sleep(1)
                
                # 检查是否有新消息
                # 这里处理模拟消息
                if self._simulate_client_connection():
                    self.logger.debug("处理模拟客户端连接")
                
            except Exception as e:
                self.logger.error(f"服务器循环异常: {e}")
                time.sleep(1)
        
        self.logger.info("命名管道服务器主循环结束")
    
    def _simulate_client_connection(self) -> bool:
        """
        模拟客户端连接
        
        Returns:
            bool: 是否处理了连接
        """
        # 在实际实现中，这里应该处理真实的客户端连接
        # 这里返回False表示没有真实连接
        return False
    
    def _default_message_handler(self, message: str) -> str:
        """
        默认消息处理函数
        
        Args:
            message: 接收到的消息
            
        Returns:
            str: 响应消息
        """
        try:
            import json
            message_data = json.loads(message)
            
            command = message_data.get("command")
            parameters = message_data.get("parameters", {})
            
            self.logger.info(f"处理命令: {command}, 参数: {parameters}")
            
            # 处理不同类型的命令
            if command == "get_status":
                response = {
                    "success": True,
                    "status": "运行中",
                    "timestamp": time.time()
                }
            elif command == "send_program":
                program_name = parameters.get("program_name")
                response = {
                    "success": True,
                    "message": f"程序 {program_name} 发送成功",
                    "timestamp": time.time()
                }
            elif command == "receive_program":
                program_name = parameters.get("program_name")
                response = {
                    "success": True,
                    "program_data": f"模拟程序数据 - {program_name}",
                    "timestamp": time.time()
                }
            else:
                response = {
                    "success": False,
                    "error": f"未知命令: {command}",
                    "timestamp": time.time()
                }
            
            return json.dumps(response)
            
        except Exception as e:
            self.logger.error(f"处理消息异常: {e}")
            error_response = {
                "success": False,
                "error": f"消息处理失败: {str(e)}",
                "timestamp": time.time()
            }
            import json
            return json.dumps(error_response)
    
    def set_message_handler(self, handler: Callable[[str], str]) -> None:
        """
        设置自定义消息处理函数
        
        Args:
            handler: 消息处理函数
        """
        self._message_handler = handler
        self.logger.info("自定义消息处理函数已设置")
    
    def get_server_status(self) -> Dict[str, Any]:
        """
        获取服务器状态
        
        Returns:
            Dict[str, Any]: 服务器状态信息
        """
        return {
            "pipe_name": self.pipe_name,
            "pipe_path": self.pipe_path,
            "is_running": self.is_running,
            "max_connections": self.max_connections,
            "active_clients": len(self._clients),
            "server_thread_alive": self._server_thread.is_alive() if self._server_thread else False
        }
    
    def broadcast_message(self, message: str) -> bool:
        """
        广播消息到所有连接的客户端
        
        Args:
            message: 广播消息
            
        Returns:
            bool: 广播是否成功
        """
        try:
            if not self.is_running:
                self.logger.error("服务器未运行，无法广播消息")
                return False
            
            self.logger.info(f"广播消息: {message}")
            
            # 在实际实现中，这里应该向所有连接的客户端发送消息
            # 这里只是记录日志
            for client_id in self._clients:
                self.logger.debug(f"向客户端 {client_id} 发送广播消息")
            
            return True
            
        except Exception as e:
            self.logger.error(f"广播消息异常: {e}")
            return False
