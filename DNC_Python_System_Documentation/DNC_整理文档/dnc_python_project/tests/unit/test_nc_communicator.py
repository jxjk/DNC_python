"""
NC通信器单元测试
测试NC通信器的各种功能
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.business.nc_communicator import NCCommunicator
from src.core.config import ConfigManager
from src.communication.protocol_factory import ProtocolFactory
from src.communication.nc_protocol import NCProtocol


class TestNCCommunicator(unittest.TestCase):
    """NC通信器测试类"""

    def setUp(self):
        """测试前准备"""
        # 创建模拟对象
        self.mock_config_manager = Mock(spec=ConfigManager)
        self.mock_protocol_factory = Mock(spec=ProtocolFactory)
        self.mock_nc_protocol = Mock(spec=NCProtocol)
        
        # 设置模拟返回值
        self.mock_config_manager.get_value.return_value = "test_config"
        self.mock_protocol_factory.create_protocol.return_value = self.mock_nc_protocol
        
        # 模拟协议方法
        self.mock_nc_protocol.connect.return_value = True
        self.mock_nc_protocol.disconnect.return_value = True
        self.mock_nc_protocol.send_data.return_value = True
        self.mock_nc_protocol.receive_data.return_value = "response_data"
        self.mock_nc_protocol.is_connected.return_value = True
        
        # 创建NC通信器实例
        self.nc_communicator = NCCommunicator(
            self.mock_config_manager, 
            self.mock_protocol_factory
        )

    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.nc_communicator)
        self.assertEqual(self.nc_communicator.config_manager, self.mock_config_manager)
        self.assertEqual(self.nc_communicator.protocol_factory, self.mock_protocol_factory)
        self.assertIsNone(self.nc_communicator.protocol)

    def test_connect_success(self):
        """测试成功连接"""
        result = self.nc_communicator.connect()
        
        self.assertTrue(result["success"])
        self.assertIsNotNone(self.nc_communicator.protocol)
        self.mock_protocol_factory.create_protocol.assert_called_once()
        self.mock_nc_protocol.connect.assert_called_once()

    def test_connect_failure(self):
        """测试连接失败"""
        # 模拟连接失败
        self.mock_nc_protocol.connect.return_value = False
        
        result = self.nc_communicator.connect()
        
        self.assertFalse(result["success"])
        self.assertIn("连接失败", result["error_message"])

    def test_connect_already_connected(self):
        """测试重复连接"""
        # 先连接一次
        self.nc_communicator.connect()
        
        # 再次连接
        result = self.nc_communicator.connect()
        
        self.assertFalse(result["success"])
        self.assertIn("已经连接", result["error_message"])

    def test_disconnect_success(self):
        """测试成功断开连接"""
        # 先连接
        self.nc_communicator.connect()
        
        # 断开连接
        result = self.nc_communicator.disconnect()
        
        self.assertTrue(result["success"])
        self.mock_nc_protocol.disconnect.assert_called_once()
        self.assertIsNone(self.nc_communicator.protocol)

    def test_disconnect_not_connected(self):
        """测试断开未连接"""
        # 不连接，直接断开
        result = self.nc_communicator.disconnect()
        
        self.assertFalse(result["success"])
        self.assertIn("未连接", result["error_message"])

    def test_disconnect_failure(self):
        """测试断开连接失败"""
        # 先连接
        self.nc_communicator.connect()
        
        # 模拟断开失败
        self.mock_nc_protocol.disconnect.return_value = False
        
        result = self.nc_communicator.disconnect()
        
        self.assertFalse(result["success"])
        self.assertIn("断开失败", result["error_message"])

    def test_send_data_success(self):
        """测试成功发送数据"""
        # 先连接
        self.nc_communicator.connect()
        
        # 发送数据
        data = "test_data"
        result = self.nc_communicator.send_data(data)
        
        self.assertTrue(result["success"])
        self.mock_nc_protocol.send_data.assert_called_once_with(data)

    def test_send_data_not_connected(self):
        """测试发送数据未连接"""
        # 不连接，直接发送数据
        data = "test_data"
        result = self.nc_communicator.send_data(data)
        
        self.assertFalse(result["success"])
        self.assertIn("未连接", result["error_message"])

    def test_send_data_failure(self):
        """测试发送数据失败"""
        # 先连接
        self.nc_communicator.connect()
        
        # 模拟发送失败
        self.mock_nc_protocol.send_data.return_value = False
        
        data = "test_data"
        result = self.nc_communicator.send_data(data)
        
        self.assertFalse(result["success"])
        self.assertIn("发送失败", result["error_message"])

    def test_receive_data_success(self):
        """测试成功接收数据"""
        # 先连接
        self.nc_communicator.connect()
        
        # 接收数据
        result = self.nc_communicator.receive_data()
        
        self.assertTrue(result["success"])
        self.assertEqual(result["data"], "response_data")
        self.mock_nc_protocol.receive_data.assert_called_once()

    def test_receive_data_not_connected(self):
        """测试接收数据未连接"""
        # 不连接，直接接收数据
        result = self.nc_communicator.receive_data()
        
        self.assertFalse(result["success"])
        self.assertIn("未连接", result["error_message"])

    def test_receive_data_failure(self):
        """测试接收数据失败"""
        # 先连接
        self.nc_communicator.connect()
        
        # 模拟接收失败
        self.mock_nc_protocol.receive_data.return_value = None
        
        result = self.nc_communicator.receive_data()
        
        self.assertFalse(result["success"])
        self.assertIn("接收失败", result["error_message"])

    def test_send_and_receive_success(self):
        """测试成功发送和接收"""
        # 先连接
        self.nc_communicator.connect()
        
        # 发送和接收
        data = "test_data"
        result = self.nc_communicator.send_and_receive(data)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["response"], "response_data")
        self.mock_nc_protocol.send_data.assert_called_once_with(data)
        self.mock_nc_protocol.receive_data.assert_called_once()

    def test_send_and_receive_not_connected(self):
        """测试发送和接收未连接"""
        # 不连接，直接发送和接收
        data = "test_data"
        result = self.nc_communicator.send_and_receive(data)
        
        self.assertFalse(result["success"])
        self.assertIn("未连接", result["error_message"])

    def test_send_and_receive_send_failure(self):
        """测试发送和接收发送失败"""
        # 先连接
        self.nc_communicator.connect()
        
        # 模拟发送失败
        self.mock_nc_protocol.send_data.return_value = False
        
        data = "test_data"
        result = self.nc_communicator.send_and_receive(data)
        
        self.assertFalse(result["success"])
        self.assertIn("发送失败", result["error_message"])

    def test_send_and_receive_receive_failure(self):
        """测试发送和接收接收失败"""
        # 先连接
        self.nc_communicator.connect()
        
        # 模拟接收失败
        self.mock_nc_protocol.receive_data.return_value = None
        
        data = "test_data"
        result = self.nc_communicator.send_and_receive(data)
        
        self.assertFalse(result["success"])
        self.assertIn("接收失败", result["error_message"])

    def test_is_connected_true(self):
        """测试连接状态为真"""
        # 先连接
        self.nc_communicator.connect()
        
        is_connected = self.nc_communicator.is_connected()
        
        self.assertTrue(is_connected)
        self.mock_nc_protocol.is_connected.assert_called_once()

    def test_is_connected_false(self):
        """测试连接状态为假"""
        # 不连接
        is_connected = self.nc_communicator.is_connected()
        
        self.assertFalse(is_connected)

    def test_get_connection_status(self):
        """测试获取连接状态"""
        # 先连接
        self.nc_communicator.connect()
        
        status = self.nc_communicator.get_connection_status()
        
        self.assertTrue(status["connected"])
        self.assertIn("protocol_type", status)
        self.assertIn("connection_time", status)

    def test_get_connection_status_not_connected(self):
        """测试获取未连接状态"""
        # 不连接
        status = self.nc_communicator.get_connection_status()
        
        self.assertFalse(status["connected"])
        self.assertIn("protocol_type", status)
        self.assertIn("connection_time", status)

    def test_send_program_success(self):
        """测试成功发送程序"""
        # 先连接
        self.nc_communicator.connect()
        
        # 发送程序
        program_data = "O0001\nG01 X10 Y10\nM30"
        result = self.nc_communicator.send_program(program_data)
        
        self.assertTrue(result["success"])
        self.mock_nc_protocol.send_data.assert_called_once()

    def test_send_program_not_connected(self):
        """测试发送程序未连接"""
        # 不连接，直接发送程序
        program_data = "O0001\nG01 X10 Y10\nM30"
        result = self.nc_communicator.send_program(program_data)
        
        self.assertFalse(result["success"])
        self.assertIn("未连接", result["error_message"])

    def test_send_program_empty_data(self):
        """测试发送空程序"""
        # 先连接
        self.nc_communicator.connect()
        
        # 发送空程序
        program_data = ""
        result = self.nc_communicator.send_program(program_data)
        
        self.assertFalse(result["success"])
        self.assertIn("程序数据为空", result["error_message"])

    def test_send_program_large_data(self):
        """测试发送大程序"""
        # 先连接
        self.nc_communicator.connect()
        
        # 发送大程序
        program_data = "O0001\n" + "G01 X10 Y10\n" * 1000
        result = self.nc_communicator.send_program(program_data)
        
        self.assertTrue(result["success"])
        self.mock_nc_protocol.send_data.assert_called_once()

    def test_receive_status_success(self):
        """测试成功接收状态"""
        # 先连接
        self.nc_communicator.connect()
        
        # 模拟状态数据
        self.mock_nc_protocol.receive_data.return_value = "STATUS:READY"
        
        result = self.nc_communicator.receive_status()
        
        self.assertTrue(result["success"])
        self.assertEqual(result["status"], "STATUS:READY")

    def test_receive_status_not_connected(self):
        """测试接收状态未连接"""
        # 不连接，直接接收状态
        result = self.nc_communicator.receive_status()
        
        self.assertFalse(result["success"])
        self.assertIn("未连接", result["error_message"])

    def test_receive_status_failure(self):
        """测试接收状态失败"""
        # 先连接
        self.nc_communicator.connect()
        
        # 模拟接收失败
        self.mock_nc_protocol.receive_data.return_value = None
        
        result = self.nc_communicator.receive_status()
        
        self.assertFalse(result["success"])
        self.assertIn("接收失败", result["error_message"])

    def test_send_emergency_stop(self):
        """测试发送紧急停止"""
        # 先连接
        self.nc_communicator.connect()
        
        result = self.nc_communicator.send_emergency_stop()
        
        self.assertTrue(result["success"])
        self.mock_nc_protocol.send_data.assert_called_once()

    def test_send_emergency_stop_not_connected(self):
        """测试发送紧急停止未连接"""
        # 不连接，直接发送紧急停止
        result = self.nc_communicator.send_emergency_stop()
        
        self.assertFalse(result["success"])
        self.assertIn("未连接", result["error_message"])

    def test_send_control_command_success(self):
        """测试成功发送控制命令"""
        # 先连接
        self.nc_communicator.connect()
        
        command = "START"
        result = self.nc_communicator.send_control_command(command)
        
        self.assertTrue(result["success"])
        self.mock_nc_protocol.send_data.assert_called_once()

    def test_send_control_command_not_connected(self):
        """测试发送控制命令未连接"""
        # 不连接，直接发送控制命令
        command = "START"
        result = self.nc_communicator.send_control_command(command)
        
        self.assertFalse(result["success"])
        self.assertIn("未连接", result["error_message"])

    def test_send_control_command_invalid(self):
        """测试发送无效控制命令"""
        # 先连接
        self.nc_communicator.connect()
        
        command = ""
        result = self.nc_communicator.send_control_command(command)
        
        self.assertFalse(result["success"])
        self.assertIn("命令为空", result["error_message"])

    def test_batch_send_data_success(self):
        """测试成功批量发送数据"""
        # 先连接
        self.nc_communicator.connect()
        
        data_list = ["data1", "data2", "data3"]
        results = self.nc_communicator.batch_send_data(data_list)
        
        self.assertEqual(len(results), 3)
        self.assertTrue(results[0]["success"])
        self.assertTrue(results[1]["success"])
        self.assertTrue(results[2]["success"])

    def test_batch_send_data_not_connected(self):
        """测试批量发送数据未连接"""
        # 不连接，直接批量发送数据
        data_list = ["data1", "data2", "data3"]
        results = self.nc_communicator.batch_send_data(data_list)
        
        self.assertEqual(len(results), 3)
        self.assertFalse(results[0]["success"])
        self.assertFalse(results[1]["success"])
        self.assertFalse(results[2]["success"])

    def test_batch_send_data_partial_failure(self):
        """测试批量发送数据部分失败"""
        # 先连接
        self.nc_communicator.connect()
        
        # 模拟部分发送失败
        self.mock_nc_protocol.send_data.side_effect = [True, False, True]
        
        data_list = ["data1", "data2", "data3"]
        results = self.nc_communicator.batch_send_data(data_list)
        
        self.assertEqual(len(results), 3)
        self.assertTrue(results[0]["success"])
        self.assertFalse(results[1]["success"])
        self.assertTrue(results[2]["success"])

    def test_get_communication_statistics(self):
        """测试获取通信统计信息"""
        # 先连接
        self.nc_communicator.connect()
        
        # 执行一些操作
        self.nc_communicator.send_data("test1")
        self.nc_communicator.send_data("test2")
        self.nc_communicator.receive_data()
        
        stats = self.nc_communicator.get_communication_statistics()
        
        self.assertIn("total_sent", stats)
        self.assertIn("total_received", stats)
        self.assertIn("success_rate", stats)
        self.assertIn("connection_time", stats)

    def test_reset_statistics(self):
        """测试重置统计信息"""
        # 先连接
        self.nc_communicator.connect()
        
        # 执行一些操作
        self.nc_communicator.send_data("test1")
        
        # 重置统计
        self.nc_communicator.reset_statistics()
        
        stats = self.nc_communicator.get_communication_statistics()
        
        self.assertEqual(stats["total_sent"], 0)
        self.assertEqual(stats["total_received"], 0)

    def test_validate_protocol_configuration(self):
        """测试验证协议配置"""
        result = self.nc_communicator.validate_protocol_configuration()
        
        self.assertTrue(result["valid"])
        self.assertEqual(len(result["errors"]), 0)

    def test_validate_protocol_configuration_invalid(self):
        """测试验证无效协议配置"""
        # 模拟无效配置
        self.mock_config_manager.get_value.return_value = None
        
        result = self.nc_communicator.validate_protocol_configuration()
        
        self.assertFalse(result["valid"])
        self.assertGreater(len(result["errors"]), 0)

    def test_reconnect_success(self):
        """测试成功重连"""
        # 先连接
        self.nc_communicator.connect()
        
        # 重连
        result = self.nc_communicator.reconnect()
        
        self.assertTrue(result["success"])
        # 应该先断开再连接
        self.mock_nc_protocol.disconnect.assert_called_once()
        self.mock_nc_protocol.connect.assert_called()

    def test_reconnect_not_connected(self):
        """测试重连未连接"""
        # 不连接，直接重连
        result = self.nc_communicator.reconnect()
        
        self.assertTrue(result["success"])  # 重连应该成功连接
        self.mock_nc_protocol.connect.assert_called_once()

    def test_handle_communication_error(self):
        """测试处理通信错误"""
        # 先连接
        self.nc_communicator.connect()
        
        # 模拟通信错误
        self.mock_nc_protocol.send_data.side_effect = Exception("通信错误")
        
        result = self.nc_communicator.send_data("test_data")
        
        self.assertFalse(result["success"])
        self.assertIn("通信错误", result["error_message"])

    def test_handle_protocol_factory_error(self):
        """测试处理协议工厂错误"""
        # 模拟协议
