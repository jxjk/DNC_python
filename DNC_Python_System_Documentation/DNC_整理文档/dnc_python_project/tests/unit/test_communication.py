"""
通信模块单元测试
测试NC通信相关的功能
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import tempfile

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from dnc_python_project.src.communication.nc_protocol import NCProtocol
from dnc_python_project.src.communication.named_pipe import NamedPipe
from dnc_python_project.src.communication.protocol_factory import ProtocolFactory
from dnc_python_project.src.utils.constants import PROTOCOL_TYPES


class TestNCProtocol(unittest.TestCase):
    """NCProtocol测试"""
    
    def setUp(self):
        """测试前准备"""
        self.protocol = NCProtocol()
        
    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.protocol)
        self.assertIsNotNone(self.protocol.logger)
        self.assertFalse(self.protocol.is_connected)
        
    def test_connect_success(self):
        """测试成功连接"""
        with patch.object(self.protocol, '_establish_connection', return_value=True):
            result = self.protocol.connect()
            
        self.assertTrue(result)
        self.assertTrue(self.protocol.is_connected)
        
    def test_connect_failure(self):
        """测试连接失败"""
        with patch.object(self.protocol, '_establish_connection', return_value=False):
            result = self.protocol.connect()
            
        self.assertFalse(result)
        self.assertFalse(self.protocol.is_connected)
        
    def test_disconnect(self):
        """测试断开连接"""
        # 先连接
        with patch.object(self.protocol, '_establish_connection', return_value=True):
            self.protocol.connect()
            
        # 断开连接
        with patch.object(self.protocol, '_close_connection', return_value=True):
            result = self.protocol.disconnect()
            
        self.assertTrue(result)
        self.assertFalse(self.protocol.is_connected)
        
    def test_send_parameters_success(self):
        """测试成功发送参数"""
        parameters = {
            "#500": "10.0",
            "#501": "20.0",
            "#502": "30.0"
        }
        
        # 模拟连接成功
        with patch.object(self.protocol, 'is_connected', True):
            with patch.object(self.protocol, '_send_data', return_value=True):
                result = self.protocol.send_parameters(parameters)
                
        self.assertTrue(result)
        
    def test_send_parameters_not_connected(self):
        """测试未连接时发送参数"""
        parameters = {"#500": "10.0"}
        
        result = self.protocol.send_parameters(parameters)
        
        self.assertFalse(result)
        
    def test_send_parameters_failure(self):
        """测试发送参数失败"""
        parameters = {"#500": "10.0"}
        
        # 模拟连接成功但发送失败
        with patch.object(self.protocol, 'is_connected', True):
            with patch.object(self.protocol, '_send_data', return_value=False):
                result = self.protocol.send_parameters(parameters)
                
        self.assertFalse(result)
        
    def test_format_parameters(self):
        """测试参数格式化"""
        parameters = {
            "#500": "10.0",
            "#501": "20.0",
            "#502": "30.0"
        }
        
        formatted = self.protocol._format_parameters(parameters)
        
        # 验证格式化结果
        self.assertIn("#500=10.0", formatted)
        self.assertIn("#501=20.0", formatted)
        self.assertIn("#502=30.0", formatted)
        
    def test_validate_parameters(self):
        """测试参数验证"""
        # 测试有效参数
        valid_parameters = {
            "#500": "10.0",
            "#501": "20.0"
        }
        self.assertTrue(self.protocol._validate_parameters(valid_parameters))
        
        # 测试无效参数（空字典）
        self.assertFalse(self.protocol._validate_parameters({}))
        
        # 测试无效参数（包含空值）
        invalid_parameters = {
            "#500": "",
            "#501": "20.0"
        }
        self.assertFalse(self.protocol._validate_parameters(invalid_parameters))
        
    def test_receive_data(self):
        """测试接收数据"""
        # 模拟连接成功
        with patch.object(self.protocol, 'is_connected', True):
            with patch.object(self.protocol, '_receive_raw_data', return_value="OK"):
                result = self.protocol.receive_data()
                
        self.assertEqual(result, "OK")
        
    def test_receive_data_not_connected(self):
        """测试未连接时接收数据"""
        result = self.protocol.receive_data()
        
        self.assertIsNone(result)
        
    def test_connection_status(self):
        """测试连接状态"""
        self.assertFalse(self.protocol.is_connected)
        
        # 模拟连接
        with patch.object(self.protocol, '_establish_connection', return_value=True):
            self.protocol.connect()
            self.assertTrue(self.protocol.is_connected)
            
        # 模拟断开
        with patch.object(self.protocol, '_close_connection', return_value=True):
            self.protocol.disconnect()
            self.assertFalse(self.protocol.is_connected)


class TestNamedPipe(unittest.TestCase):
    """NamedPipe测试"""
    
    def setUp(self):
        """测试前准备"""
        self.pipe_name = "test_pipe"
        self.named_pipe = NamedPipe(self.pipe_name)
        
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.named_pipe.pipe_name, self.pipe_name)
        self.assertIsNone(self.named_pipe.pipe_handle)
        self.assertFalse(self.named_pipe.is_connected)
        
    @patch('dnc_python_project.src.communication.named_pipe.win32pipe')
    @patch('dnc_python_project.src.communication.named_pipe.win32file')
    def test_create_pipe_success(self, mock_win32file, mock_win32pipe):
        """测试成功创建命名管道"""
        mock_handle = Mock()
        mock_win32pipe.CreateNamedPipe.return_value = mock_handle
        
        result = self.named_pipe.create_pipe()
        
        self.assertTrue(result)
        self.assertEqual(self.named_pipe.pipe_handle, mock_handle)
        mock_win32pipe.CreateNamedPipe.assert_called_once()
        
    @patch('dnc_python_project.src.communication.named_pipe.win32pipe')
    def test_create_pipe_failure(self, mock_win32pipe):
        """测试创建命名管道失败"""
        mock_win32pipe.CreateNamedPipe.side_effect = Exception("Create failed")
        
        result = self.named_pipe.create_pipe()
        
        self.assertFalse(result)
        self.assertIsNone(self.named_pipe.pipe_handle)
        
    @patch('dnc_python_project.src.communication.named_pipe.win32pipe')
    @patch('dnc_python_project.src.communication.named_pipe.win32file')
    def test_connect_to_pipe_success(self, mock_win32file, mock_win32pipe):
        """测试成功连接到命名管道"""
        mock_handle = Mock()
        mock_win32file.CreateFile.return_value = mock_handle
        
        result = self.named_pipe.connect_to_pipe()
        
        self.assertTrue(result)
        self.assertEqual(self.named_pipe.pipe_handle, mock_handle)
        self.assertTrue(self.named_pipe.is_connected)
        
    @patch('dnc_python_project.src.communication.named_pipe.win32file')
    def test_connect_to_pipe_failure(self, mock_win32file):
        """测试连接到命名管道失败"""
        mock_win32file.CreateFile.side_effect = Exception("Connect failed")
        
        result = self.named_pipe.connect_to_pipe()
        
        self.assertFalse(result)
        self.assertIsNone(self.named_pipe.pipe_handle)
        self.assertFalse(self.named_pipe.is_connected)
        
    @patch('dnc_python_project.src.communication.named_pipe.win32file')
    def test_write_data_success(self, mock_win32file):
        """测试成功写入数据"""
        # 模拟已连接
        self.named_pipe.is_connected = True
        self.named_pipe.pipe_handle = Mock()
        
        mock_win32file.WriteFile.return_value = (0, b"test")
        
        result = self.named_pipe.write_data("test data")
        
        self.assertTrue(result)
        mock_win32file.WriteFile.assert_called_once()
        
    def test_write_data_not_connected(self):
        """测试未连接时写入数据"""
        result = self.named_pipe.write_data("test data")
        
        self.assertFalse(result)
        
    @patch('dnc_python_project.src.communication.named_pipe.win32file')
    def test_read_data_success(self, mock_win32file):
        """测试成功读取数据"""
        # 模拟已连接
        self.named_pipe.is_connected = True
        self.named_pipe.pipe_handle = Mock()
        
        mock_win32file.ReadFile.return_value = (0, b"test data")
        
        result = self.named_pipe.read_data()
        
        self.assertEqual(result, "test data")
        
    def test_read_data_not_connected(self):
        """测试未连接时读取数据"""
        result = self.named_pipe.read_data()
        
        self.assertIsNone(result)
        
    @patch('dnc_python_project.src.communication.named_pipe.win32file')
    def test_close_pipe(self, mock_win32file):
        """测试关闭管道"""
        # 模拟已连接
        self.named_pipe.is_connected = True
        self.named_pipe.pipe_handle = Mock()
        
        self.named_pipe.close_pipe()
        
        self.assertFalse(self.named_pipe.is_connected)
        self.assertIsNone(self.named_pipe.pipe_handle)
        mock_win32file.CloseHandle.assert_called_once()


class TestProtocolFactory(unittest.TestCase):
    """ProtocolFactory测试"""
    
    def setUp(self):
        """测试前准备"""
        self.factory = ProtocolFactory()
        
    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.factory)
        self.assertIsNotNone(self.factory.logger)
        
    def test_create_named_pipe_protocol(self):
        """测试创建命名管道协议"""
        config = {
            'protocol_type': PROTOCOL_TYPES.NAMED_PIPE,
            'pipe_name': 'test_pipe'
        }
        
        protocol = self.factory.create_protocol(config)
        
        self.assertIsNotNone(protocol)
        self.assertEqual(protocol.pipe_name, 'test_pipe')
        
    def test_create_serial_protocol(self):
        """测试创建串口协议"""
        config = {
            'protocol_type': PROTOCOL_TYPES.SERIAL,
            'port': 'COM1',
            'baudrate': 9600
        }
        
        protocol = self.factory.create_protocol(config)
        
        self.assertIsNotNone(protocol)
        self.assertEqual(protocol.port, 'COM1')
        self.assertEqual(protocol.baudrate, 9600)
        
    def test_create_tcp_protocol(self):
        """测试创建TCP协议"""
        config = {
            'protocol_type': PROTOCOL_TYPES.TCP,
            'host': 'localhost',
            'port': 8080
        }
        
        protocol = self.factory.create_protocol(config)
        
        self.assertIsNotNone(protocol)
        self.assertEqual(protocol.host, 'localhost')
        self.assertEqual(protocol.port, 8080)
        
    def test_create_unknown_protocol(self):
        """测试创建未知协议类型"""
        config = {
            'protocol_type': 'UNKNOWN'
        }
        
        protocol = self.factory.create_protocol(config)
        
        # 应该返回None
        self.assertIsNone(protocol)
        
    def test_create_protocol_with_missing_config(self):
        """测试创建协议时缺少配置"""
        # 缺少protocol_type
        config = {}
        
        protocol = self.factory.create_protocol(config)
        
        self.assertIsNone(protocol)
        
    def test_get_supported_protocols(self):
        """测试获取支持的协议类型"""
        protocols = self.factory.get_supported_protocols()
        
        self.assertIsInstance(protocols, list)
        self.assertIn(PROTOCOL_TYPES.NAMED_PIPE, protocols)
        self.assertIn(PROTOCOL_TYPES.SERIAL, protocols)
        self.assertIn(PROTOCOL_TYPES.TCP, protocols)
        
    def test_validate_protocol_config(self):
        """测试验证协议配置"""
        # 测试有效配置
        valid_config = {
            'protocol_type': PROTOCOL_TYPES.NAMED_PIPE,
            'pipe_name': 'test_pipe'
        }
        self.assertTrue(self.factory._validate_protocol_config(valid_config))
        
        # 测试无效配置（缺少必要参数）
        invalid_config = {
            'protocol_type': PROTOCOL_TYPES.NAMED_PIPE
            # 缺少pipe_name
        }
        self.assertFalse(self.factory._validate_protocol_config(invalid_config))
        
        # 测试无效配置（未知协议类型）
        unknown_config = {
            'protocol_type': 'UNKNOWN'
        }
        self.assertFalse(self.factory._validate_protocol_config(unknown_config))


class TestCommunicationIntegration(unittest.TestCase):
    """通信集成测试"""
    
    def test_protocol_factory_with_nc_protocol(self):
        """测试协议工厂与NC协议集成"""
        factory = ProtocolFactory()
        
        config = {
            'protocol_type': PROTOCOL_TYPES.NAMED_PIPE,
            'pipe_name': 'test_pipe'
        }
        
        protocol = factory.create_protocol(config)
        
        self.assertIsNotNone(protocol)
        self.assertEqual(protocol.pipe_name, 'test_pipe')
        
    def test_nc_protocol_with_named_pipe(self):
        """测试NC协议与命名管道集成"""
        with patch('dnc_python_project.src.communication.nc_protocol.NamedPipe') as mock_named_pipe:
            mock_pipe_instance = Mock()
            mock_pipe_instance.connect_to_pipe.return_value = True
            mock_pipe_instance.is_connected = True
            mock_named_pipe.return_value = mock_pipe_instance
            
            protocol = NCProtocol()
            protocol.pipe_name = 'test_pipe'
            
            # 测试连接
            result = protocol.connect()
            self.assertTrue(result)
            
            # 测试发送参数
            parameters = {"#500": "10.0"}
            mock_pipe_instance.write_data.return_value = True
            result = protocol.send_parameters(parameters)
            self.assertTrue(result)
            
    def test_error_handling_in_communication(self):
        """测试通信中的错误处理"""
        with patch('dnc_python_project.src.communication.nc_protocol.NamedPipe') as mock_named_pipe:
            mock_pipe_instance = Mock()
            mock_pipe_instance.connect_to_pipe.return_value = False  # 连接失败
            mock_named_pipe.return_value = mock_pipe_instance
            
            protocol = NCProtocol()
            protocol.pipe_name = 'test_pipe'
            
            # 测试连接失败
            result = protocol.connect()
            self.assertFalse(result)
            
            # 测试发送参数时未连接
            parameters = {"#500": "10.0"}
            result = protocol.send_parameters(parameters)
            self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
