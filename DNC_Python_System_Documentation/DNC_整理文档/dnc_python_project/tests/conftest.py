"""
pytest配置文件
包含测试夹具和配置
"""

import pytest
import sys
import os
from unittest.mock import Mock, MagicMock

# 添加项目根目录到Python路径
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

from src.core.config import ConfigManager
from src.data.csv_processor import CSVProcessor
from src.business.model_recognizer import ModelRecognizer
from src.business.program_matcher import ProgramMatcher
from src.business.calculation_engine import CalculationEngine
from src.business.nc_communicator import NCCommunicator
from src.business.relation_validator import RelationValidator


@pytest.fixture
def mock_config_manager():
    """模拟配置管理器"""
    mock_config = Mock(spec=ConfigManager)
    
    # 模拟QR码配置
    mock_qr_config = Mock()
    mock_qr_config.qr_mode = 1
    mock_qr_config.qr_split_str = "@"
    mock_qr_config.model_place = 2
    mock_qr_config.po_place = 1
    mock_qr_config.qty_place = 3
    mock_qr_config.barcode_header_str_num = 11
    
    # 模拟通信配置
    mock_com_config = Mock()
    mock_com_config.com_type = 0  # 串口
    mock_com_config.com_port = "COM1"
    mock_com_config.baud_rate = 9600
    mock_com_config.data_bits = 8
    mock_com_config.parity = 'N'
    mock_com_config.stop_bits = 1
    mock_com_config.timeout = 5.0
    mock_com_config.ip_address = "192.168.1.100"
    mock_com_config.port = 8080
    
    # 模拟设备配置
    mock_device_config = Mock()
    mock_device_config.device_name = "TestDevice"
    mock_device_config.device_model = "TestModel"
    
    mock_config.qr_config = mock_qr_config
    mock_config.com_config = mock_com_config
    mock_config.device_config = mock_device_config
    mock_config.get_csv_config_path.return_value = "test_path.csv"
    
    return mock_config


@pytest.fixture
def mock_csv_processor():
    """模拟CSV处理器"""
    mock_processor = Mock(spec=CSVProcessor)
    
    # 模拟CSV数据
    mock_processor.read_csv.return_value = [
        ["1", "LOAD", "100"],
        ["2", "DEFINE", "TEST", "BEFORE", "AFTER", "CHANGE", "CALC"],
        ["3", "CALC", "VAR1", "+", "VAR2"]
    ]
    
    return mock_processor


@pytest.fixture
def model_recognizer(mock_config_manager):
    """型号识别器实例"""
    return ModelRecognizer(mock_config_manager)


@pytest.fixture
def program_matcher(mock_config_manager, mock_csv_processor):
    """程序匹配器实例"""
    return ProgramMatcher(mock_config_manager, mock_csv_processor)


@pytest.fixture
def calculation_engine(mock_config_manager, mock_csv_processor):
    """计算引擎实例"""
    return CalculationEngine(mock_config_manager, mock_csv_processor)


@pytest.fixture
def nc_communicator(mock_config_manager):
    """NC通信器实例"""
    return NCCommunicator(mock_config_manager)


@pytest.fixture
def relation_validator(mock_config_manager, mock_csv_processor):
    """关系验证器实例"""
    return RelationValidator(mock_config_manager, mock_csv_processor)


@pytest.fixture
def sample_qr_data():
    """样本QR码数据"""
    return "PO123@MODEL456@QTY10@OTHER_DATA"


@pytest.fixture
def sample_program_data():
    """样本程序数据"""
    return {
        "program_no": 1,
        "model": "MODEL456",
        "parameters": {
            "VAR1": 100,
            "VAR2": 200,
            "VAR3": 300
        }
    }


@pytest.fixture
def sample_calculation_input():
    """样本计算输入数据"""
    return {
        "VAR1": 100,
        "VAR2": 200,
        "VAR3": 300
    }


@pytest.fixture
def sample_nc_command():
    """样本NC命令"""
    return "G90 G54 G00 X0 Y0\nM30"


@pytest.fixture
def sample_relation_data():
    """样本关系数据"""
    return {
        "model": "MODEL456",
        "program": "PROGRAM001",
        "parameters": {
            "VAR1": 100,
            "VAR2": 200
        }
    }


@pytest.fixture(scope="session")
def test_config_dir():
    """测试配置目录"""
    return os.path.join(os.path.dirname(__file__), "unit", "config")


@pytest.fixture
def temp_csv_file(tmp_path):
    """临时CSV文件"""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("col1,col2,col3\nval1,val2,val3")
    return str(csv_file)


@pytest.fixture
def mock_event_dispatcher():
    """模拟事件分发器"""
    mock_dispatcher = Mock()
    mock_dispatcher.register = Mock()
    mock_dispatcher.emit = Mock()
    mock_dispatcher.unregister = Mock()
    return mock_dispatcher


@pytest.fixture
def mock_logger():
    """模拟日志记录器"""
    mock_log = Mock()
    mock_log.info = Mock()
    mock_log.error = Mock()
    mock_log.warning = Mock()
    mock_log.debug = Mock()
    return mock_log


@pytest.fixture(autouse=True)
def setup_test_environment():
    """自动设置测试环境"""
    # 设置测试环境变量
    os.environ["TEST_MODE"] = "true"
    
    # 执行测试前的设置
    yield
    
    # 执行测试后的清理
    if "TEST_MODE" in os.environ:
        del os.environ["TEST_MODE"]
