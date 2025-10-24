"""
协议工厂模块
负责创建和管理NC协议实例
"""

import logging
from typing import Optional, Dict, Any
from src.communication.nc_protocol import NCProtocol, NCProtocolType, RexrothProtocol, FanucProtocol


class NCProtocolFactory:
    """NC协议工厂类"""
    
    def __init__(self):
        """初始化协议工厂"""
        self.logger = logging.getLogger(__name__)
        self._protocol_cache = {}
    
    def create_protocol(self, protocol_type: NCProtocolType, 
                       connection_params: Dict[str, Any] = None) -> Optional[NCProtocol]:
        """
        创建NC协议实例
        
        Args:
            protocol_type: 协议类型
            connection_params: 连接参数
            
        Returns:
            Optional[NCProtocol]: 协议实例，创建失败返回None
        """
        try:
            connection_params = connection_params or {}
            
            # 检查缓存中是否已有实例
            cache_key = self._get_cache_key(protocol_type, connection_params)
            if cache_key in self._protocol_cache:
                self.logger.debug(f"从缓存获取协议实例: {protocol_type.value}")
                return self._protocol_cache[cache_key]
            
            # 创建新的协议实例
            protocol = self._create_protocol_instance(protocol_type)
            if protocol:
                # 尝试连接
                if connection_params and protocol.connect(connection_params):
                    self._protocol_cache[cache_key] = protocol
                    self.logger.info(f"创建并连接协议实例成功: {protocol_type.value}")
                else:
                    self.logger.warning(f"创建协议实例但连接失败: {protocol_type.value}")
            
            return protocol
            
        except Exception as e:
            self.logger.error(f"创建协议实例失败: {protocol_type.value}, 错误: {e}")
            return None
    
    def _create_protocol_instance(self, protocol_type: NCProtocolType) -> Optional[NCProtocol]:
        """
        创建协议实例
        
        Args:
            protocol_type: 协议类型
            
        Returns:
            Optional[NCProtocol]: 协议实例
        """
        try:
            if protocol_type == NCProtocolType.REXROTH:
                return RexrothProtocol()
            elif protocol_type == NCProtocolType.FANUC:
                return FanucProtocol()
            elif protocol_type == NCProtocolType.SIEMENS:
                # 西门子协议实现（待实现）
                self.logger.warning("西门子协议尚未实现")
                return None
            elif protocol_type == NCProtocolType.MITSUBISHI:
                # 三菱协议实现（待实现）
                self.logger.warning("三菱协议尚未实现")
                return None
            else:
                self.logger.error(f"不支持的协议类型: {protocol_type}")
                return None
        except Exception as e:
            self.logger.error(f"创建协议实例异常: {protocol_type}, 错误: {e}")
            return None
    
    def _get_cache_key(self, protocol_type: NCProtocolType, 
                      connection_params: Dict[str, Any]) -> str:
        """
        生成缓存键
        
        Args:
            protocol_type: 协议类型
            connection_params: 连接参数
            
        Returns:
            str: 缓存键
        """
        # 基于协议类型和关键连接参数生成缓存键
        key_parts = [protocol_type.value]
        
        # 添加关键连接参数
        if 'ip_address' in connection_params:
            key_parts.append(connection_params['ip_address'])
        if 'port' in connection_params:
            key_parts.append(str(connection_params['port']))
        
        return '_'.join(key_parts)
    
    def get_protocol(self, protocol_type: NCProtocolType, 
                    connection_params: Dict[str, Any] = None) -> Optional[NCProtocol]:
        """
        获取协议实例（如果不存在则创建）
        
        Args:
            protocol_type: 协议类型
            connection_params: 连接参数
            
        Returns:
            Optional[NCProtocol]: 协议实例
        """
        return self.create_protocol(protocol_type, connection_params)
    
    def disconnect_protocol(self, protocol_type: NCProtocolType,
                           connection_params: Dict[str, Any] = None) -> bool:
        """
        断开协议连接
        
        Args:
            protocol_type: 协议类型
            connection_params: 连接参数
            
        Returns:
            bool: 断开是否成功
        """
        try:
            cache_key = self._get_cache_key(protocol_type, connection_params)
            if cache_key in self._protocol_cache:
                protocol = self._protocol_cache[cache_key]
                if protocol.disconnect():
                    del self._protocol_cache[cache_key]
                    self.logger.info(f"协议连接已断开: {protocol_type.value}")
                    return True
                else:
                    self.logger.error(f"断开协议连接失败: {protocol_type.value}")
                    return False
            else:
                self.logger.warning(f"协议实例不存在: {protocol_type.value}")
                return True
        except Exception as e:
            self.logger.error(f"断开协议连接异常: {protocol_type.value}, 错误: {e}")
            return False
    
    def disconnect_all(self) -> bool:
        """
        断开所有协议连接
        
        Returns:
            bool: 断开是否成功
        """
        try:
            success = True
            protocols_to_disconnect = list(self._protocol_cache.keys())
            
            for cache_key in protocols_to_disconnect:
                protocol = self._protocol_cache[cache_key]
                if not protocol.disconnect():
                    success = False
                    self.logger.error(f"断开协议连接失败: {cache_key}")
                else:
                    self.logger.info(f"协议连接已断开: {cache_key}")
            
            # 清空缓存
            self._protocol_cache.clear()
            self.logger.info("所有协议连接已断开")
            return success
            
        except Exception as e:
            self.logger.error(f"断开所有协议连接异常: {e}")
            return False
    
    def get_connected_protocols(self) -> Dict[str, NCProtocol]:
        """
        获取所有已连接的协议
        
        Returns:
            Dict[str, NCProtocol]: 已连接的协议字典
        """
        connected_protocols = {}
        for cache_key, protocol in self._protocol_cache.items():
            if protocol.is_connected:
                connected_protocols[cache_key] = protocol
        
        return connected_protocols
    
    def get_protocol_status(self, protocol_type: NCProtocolType,
                           connection_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        获取协议状态
        
        Args:
            protocol_type: 协议类型
            connection_params: 连接参数
            
        Returns:
            Dict[str, Any]: 协议状态信息
        """
        try:
            cache_key = self._get_cache_key(protocol_type, connection_params)
            if cache_key in self._protocol_cache:
                protocol = self._protocol_cache[cache_key]
                machine_status = protocol.get_machine_status()
                
                return {
                    'protocol_type': protocol_type.value,
                    'is_connected': protocol.is_connected,
                    'machine_status': machine_status,
                    'cache_key': cache_key
                }
            else:
                return {
                    'protocol_type': protocol_type.value,
                    'is_connected': False,
                    'machine_status': {'error': '协议实例不存在'},
                    'cache_key': cache_key
                }
        except Exception as e:
            self.logger.error(f"获取协议状态失败: {protocol_type.value}, 错误: {e}")
            return {
                'protocol_type': protocol_type.value,
                'is_connected': False,
                'machine_status': {'error': str(e)},
                'cache_key': self._get_cache_key(protocol_type, connection_params)
            }
    
    def clear_cache(self) -> None:
        """清理协议缓存"""
        self._protocol_cache.clear()
        self.logger.info("协议缓存已清理")
    
    def get_supported_protocols(self) -> Dict[str, str]:
        """
        获取支持的协议列表
        
        Returns:
            Dict[str, str]: 支持的协议字典（名称: 描述）
        """
        return {
            NCProtocolType.REXROTH.value: "力士乐NC协议",
            NCProtocolType.FANUC.value: "发那科NC协议",
            NCProtocolType.SIEMENS.value: "西门子NC协议（待实现）",
            NCProtocolType.MITSUBISHI.value: "三菱NC协议（待实现）"
        }
    
    def validate_connection_params(self, protocol_type: NCProtocolType,
                                 connection_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证连接参数
        
        Args:
            protocol_type: 协议类型
            connection_params: 连接参数
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        errors = []
        warnings = []
        
        if not connection_params:
            errors.append("连接参数为空")
            return {"valid": False, "errors": errors, "warnings": warnings}
        
        # 检查必需参数
        required_params = ['ip_address']
        for param in required_params:
            if param not in connection_params:
                errors.append(f"缺少必需参数: {param}")
        
        # 检查IP地址格式
        ip_address = connection_params.get('ip_address')
        if ip_address:
            import re
            ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
            if not re.match(ip_pattern, ip_address):
                errors.append("IP地址格式不正确")
        
        # 检查端口范围
        port = connection_params.get('port')
        if port and (port < 1 or port > 65535):
            errors.append("端口号必须在1-65535范围内")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
