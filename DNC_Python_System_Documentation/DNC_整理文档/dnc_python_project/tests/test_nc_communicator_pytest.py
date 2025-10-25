"""
NC通信器测试
测试NCCommunicator类的功能
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import time

# 添加项目根目录到Python路径
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

from src.business.nc_communicator import NCCommunicator, NCCommand, NCResponse, CommunicationStatus


class TestNCCommunicator:
    """NC通信器测试类"""
    def test_connect_success_serial(self, nc_communicator):
        """测试成功连接串口"""
        # 模拟配置
        nc_communicator.com_config.com_type = 0  # 串口
        nc_communicator.com_config.com_port = "COM1"
        
        with patch.object(nc_communicator, '_connect_serial', return_value=True):
            with patch.object(nc_communicator, '_start_communication_thread'):
                result = nc_communicator.connect()
                
                assert result is True
                assert nc_communicator._connected is True
    def test_connect_success_socket(self, nc_communicator):
        """测试成功连接网络"""
        # 模拟配置
        nc_communicator.com_config.com_type = 1  # 网络
        nc_communicator.com_config.ip_address = "192.168.1.100"
        nc_communicator.com_config.port = 8080
        
        with patch.object(nc_communicator, '_connect_socket', return_value=True):
            with patch.object(nc_communicator, '_start_communication_thread'):
                result = nc_communicator.connect()
                
                assert result is True
                assert nc_communicator._connected is True
    def test_connect_failure(self, nc_communicator):
        """测试连接失败"""
        with patch.object(nc_communicator, '_connect_serial', return_value=False):
            result = nc_communicator.connect()
            
            assert result is False
            assert nc_communicator._connected is False
    
    def test_disconnect_success(self, nc_communicator):
        """测试成功断开连接"""
        nc_communicator._connected = True
        
        result = nc_communicator.disconnect()
        
        assert result is True
        assert nc_communicator._connected is False
    
    def test_disconnect_not_connected(self, nc_communicator):
        """测试断开未连接状态"""
        nc_communicator._connected = False
        
        result = nc_communicator.disconnect()
        
        assert result is True
    
    def test_send_command_success(self, nc_communicator):
        """测试成功发送命令"""
        nc_communicator._connected = True
        
        command = NCCommand(
            command_id="test_command",
            command_type="read",
            data={"address": "D100", "length": 1},
            parameters={},
            timeout=5.0
        )
        
        command_id = nc_communicator.send_command(command)
        
        assert command_id == "test_command"
        assert len(nc_communicator._command_queue) == 1
    
    def test_send_command_not_connected(self, nc_communicator):
        """测试未连接时发送命令"""
        nc_communicator._connected = False
        
        command = NCCommand(
            command_id="test_command",
            command_type="read",
            data={"address": "D100", "length": 1},
            parameters={},
            timeout=5.0
        )
        
        command_id = nc_communicator.send_command(command)
        
        assert command_id == ""
    
    def test_read_data_success(self, nc_communicator):
        """测试成功读取数据"""
        nc_communicator._connected = True
        
        with patch.object(nc_communicator, '_send_command_sync') as mock_send:
            mock_response = NCResponse(
                command_id="read_123",
                success=True,
                data="100.5",
                response_time=0.1
            )
            mock_send.return_value = mock_response
            
            response = nc_communicator.read_data("D100", 1)
            
            assert response is mock_response
            mock_send.assert_called_once()
    
    def test_write_data_success(self, nc_communicator):
        """测试成功写入数据"""
        nc_communicator._connected = True
        
        with patch.object(nc_communicator, '_send_command_sync') as mock_send:
            mock_response = NCResponse(
                command_id="write_123",
                success=True,
                data="WRITE_OK",
                response_time=0.1
            )
            mock_send.return_value = mock_response
            
            response = nc_communicator.write_data("D100", 100.5)
            
            assert response is mock_response
            mock_send.assert_called_once()
    
    def test_execute_program_success(self, nc_communicator):
        """测试成功执行程序"""
        nc_communicator._connected = True
        
        with patch.object(nc_communicator, '_send_command_sync') as mock_send:
            mock_response = NCResponse(
                command_id="execute_123",
                success=True,
                data="EXECUTE_OK",
                response_time=0.5
            )
            mock_send.return_value = mock_response
            
            parameters = {"VAR1": 100, "VAR2": 200}
            response = nc_communicator.execute_program(1001, parameters)
            
            assert response is mock_response
            mock_send.assert_called_once()
    
    def test_query_status_success(self, nc_communicator):
        """测试成功查询状态"""
        nc_communicator._connected = True
        
        with patch.object(nc_communicator, '_send_command_sync') as mock_send:
            mock_response = NCResponse(
                command_id="status_123",
                success=True,
                data={"status": "RUNNING", "position": {"X": 10.0, "Y": 20.0}},
                response_time=0.1
            )
            mock_send.return_value = mock_response
            
            response = nc_communicator.query_status()
            
            assert response is mock_response
            mock_send.assert_called_once()
    
    def test_is_connected_true(self, nc_communicator):
        """测试连接状态 - 已连接"""
        nc_communicator._connected = True
        
        result = nc_communicator.is_connected()
        
        assert result is True
    
    def test_is_connected_false(self, nc_communicator):
        """测试连接状态 - 未连接"""
        nc_communicator._connected = False
        
        result = nc_communicator.is_connected()
        
        assert result is False
    
    def test_get_connection_info(self, nc_communicator):
        """测试获取连接信息"""
        nc_communicator._connected = True
        nc_communicator.com_config.com_type = 0
        nc_communicator.com_config.com_port = "COM1"
        nc_communicator.device_config.device_name = "TestDevice"
        nc_communicator.device_config.device_model = "TestModel"
        
        info = nc_communicator.get_connection_info()
        
        assert info["connected"] is True
        assert info["com_type"] == 0
        assert info["com_port"] == "COM1"
        assert info["device_name"] == "TestDevice"
        assert info["device_model"] == "TestModel"
    
    def test_add_status_callback(self, nc_communicator):
        """测试添加状态回调函数"""
        def test_callback(status):
            pass
        
        nc_communicator.add_status_callback(test_callback)
        
        assert test_callback in nc_communicator._status_callbacks
    
    def test_remove_status_callback(self, nc_communicator):
        """测试移除状态回调函数"""
        def test_callback(status):
            pass
        
        nc_communicator.add_status_callback(test_callback)
        nc_communicator.remove_status_callback(test_callback)
        
        assert test_callback not in nc_communicator._status_callbacks


class TestNCCommunicatorAdvanced:
    """高级NC通信器测试类"""
    
    def test_advanced_communicator_initialization(self, nc_communicator):
        """测试高级通信器初始化"""
        from src.business.nc_communicator import AdvancedNCCommunicator
        
        advanced_communicator = AdvancedNCCommunicator(nc_communicator.config_manager)
        
        assert advanced_communicator._command_history == []
        assert advanced_communicator._max_history_size == 1000
        assert advanced_communicator._performance_stats["total_commands"] == 0
    
    def test_advanced_send_command_history(self, nc_communicator):
        """测试高级通信器命令历史记录"""
        from src.business.nc_communicator import AdvancedNCCommunicator
        
        advanced_communicator = AdvancedNCCommunicator(nc_communicator.config_manager)
        advanced_communicator._connected = True
        
        command = NCCommand(
            command_id="test_command",
            command_type="read",
            data={"address": "D100", "length": 1},
            parameters={},
            timeout=5.0
        )
        
        command_id = advanced_communicator.send_command(command)
        
        assert len(advanced_communicator._command_history) == 1
        assert advanced_communicator._command_history[0]["command_id"] == "test_command"
    
    def test_get_command_history(self, nc_communicator):
        """测试获取命令历史"""
        from src.business.nc_communicator import AdvancedNCCommunicator
        
        advanced_communicator = AdvancedNCCommunicator(nc_communicator.config_manager)
        
        # 添加一些历史记录
        for i in range(5):
            advanced_communicator._command_history.append({
                "command_id": f"command_{i}",
                "command_type": "read",
                "timestamp": time.time(),
                "status": "success"
            })
        
        history = advanced_communicator.get_command_history(limit=3)
        
        assert len(history) == 3
        assert history[0]["command_id"] == "command_2"
        assert history[2]["command_id"] == "command_4"
    
    def test_get_performance_statistics(self, nc_communicator):
        """测试获取性能统计"""
        from src.business.nc_communicator import AdvancedNCCommunicator
        
        advanced_communicator = AdvancedNCCommunicator(nc_communicator.config_manager)
        
        stats = advanced_communicator.get_performance_statistics()
        
        assert stats["total_commands"] == 0
        assert stats["successful_commands"] == 0
        assert stats["failed_commands"] == 0
        assert stats["average_response_time"] == 0.0
    
    def test_clear_command_history(self, nc_communicator):
        """测试清空命令历史"""
        from src.business.nc_communicator import AdvancedNCCommunicator
        
        advanced_communicator = AdvancedNCCommunicator(nc_communicator.config_manager)
        
        # 添加一些历史记录
        for i in range(5):
            advanced_communicator._command_history.append({
                "command_id": f"command_{i}",
                "command_type": "read",
                "timestamp": time.time(),
                "status": "success"
            })
        
        advanced_communicator.clear_command_history()
        
        assert len(advanced_communicator._command_history) == 0


@pytest.mark.parametrize("command_type,data,expected_success", [
    ("read", {"address": "D100", "length": 1}, True),
    ("write", {"address": "D100", "data": 100.5}, True),
    ("execute", {"program_no": 1001, "parameters": {}}, True),
    ("query", {"query_type": "status"}, True),
])
def test_nc_communicator_command_types(command_type, data, expected_success, nc_communicator):
    """测试不同命令类型"""
    nc_communicator._connected = True
    
    with patch.object(nc_communicator, '_send_command_sync') as mock_send:
        mock_response = NCResponse(
            command_id=f"{command_type}_123",
            success=expected_success,
            data=f"{command_type.upper()}_OK",
            response_time=0.1
        )
        mock_send.return_value = mock_response
        
        if command_type == "read":
            response = nc_communicator.read_data(data["address"], data["length"])
        elif command_type == "write":
            response = nc_communicator.write_data(data["address"], data["data"])
        elif command_type == "execute":
            response = nc_communicator.execute_program(data["program_no"], data["parameters"])
        elif command_type == "query":
            response = nc_communicator.query_status()
        
        assert response is mock_response
        assert response.success == expected_success