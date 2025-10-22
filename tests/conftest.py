"""
DNC参数计算系统 - 测试配置和fixtures
"""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_config_dir():
    """创建临时配置目录"""
    temp_dir = tempfile.mkdtemp()
    config_dir = Path(temp_dir) / "config"
    config_dir.mkdir(parents=True)
    
    yield config_dir
    
    # 清理临时目录
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_data_dir():
    """创建临时数据目录"""
    temp_dir = tempfile.mkdtemp()
    data_dir = Path(temp_dir) / "data"
    data_dir.mkdir(parents=True)
    
    yield data_dir
    
    # 清理临时目录
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_workflow_dir():
    """创建临时工作流目录"""
    temp_dir = tempfile.mkdtemp()
    workflow_dir = Path(temp_dir)
    
    yield workflow_dir
    
    # 清理临时目录
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_config_content():
    """提供示例配置内容"""
    return """
[PATHS]
master_directory = data/master
input_file = data/input.csv
output_directory = output
log_directory = logs

[APPLICATION]
version = 2.05
language = zh-CN
auto_save = true
backup_enabled = true

[UI]
theme = default
font_size = 10
window_width = 1024
window_height = 768

[CALCULATION]
precision = 4
rounding_method = round
auto_validate = true
"""


@pytest.fixture
def sample_master_data():
    """提供示例master数据"""
    return """product_id,model,length,width,height,density,material
P001,MODEL_A,100.0,50.0,25.0,1.0,Steel
P002,MODEL_B,150.0,75.0,30.0,1.2,Aluminum
P003,MODEL_C,80.0,40.0,20.0,0.8,Plastic
P004,MODEL_D,120.0,60.0,35.0,1.5,Bronze
P005,MODEL_E,90.0,45.0,22.0,0.9,Copper"""


@pytest.fixture
def sample_input_data():
    """提供示例输入数据"""
    return """product_id,model,quantity,priority
P001,MODEL_A,10,High
P002,MODEL_B,5,Medium
P003,MODEL_C,8,Low
P004,MODEL_D,3,High
P005,MODEL_E,12,Medium"""


@pytest.fixture
def invalid_input_data():
    """提供包含错误的输入数据"""
    return """product_id,model,quantity
P001,MODEL_A,10
,MODEL_B,5  # 缺少product_id
P003,,8     # 缺少model
P004,MODEL_D,invalid  # 无效数量"""


@pytest.fixture
def sample_product_data():
    """提供示例产品数据字典"""
    return {
        "product_id": "P001",
        "model": "MODEL_A",
        "length": 100.0,
        "width": 50.0,
        "height": 25.0,
        "density": 1.0,
        "material": "Steel"
    }


@pytest.fixture
def sample_calculation_parameters():
    """提供示例计算参数"""
    return {
        "length": 100.0,
        "width": 50.0,
        "height": 25.0,
        "density": 1.0
    }


@pytest.fixture
def sample_calculated_results():
    """提供示例计算结果"""
    return {
        "volume": 125000.0,
        "surface_area": 17500.0,
        "weight": 125000.0
    }


@pytest.fixture
def mock_config_manager():
    """创建模拟配置管理器"""
    from unittest.mock import Mock
    from src.config.config_manager import ConfigManager
    
    mock_manager = Mock(spec=ConfigManager)
    mock_manager.config_data = {
        "PATHS": {
            "master_directory": "data/master",
            "input_file": "data/input.csv",
            "output_directory": "output",
            "log_directory": "logs"
        },
        "APPLICATION": {
            "version": "2.05",
            "language": "zh-CN",
            "auto_save": "true",
            "backup_enabled": "true"
        },
        "UI": {
            "theme": "default",
            "font_size": "10",
            "window_width": "1024",
            "window_height": "768"
        },
        "CALCULATION": {
            "precision": "4",
            "rounding_method": "round",
            "auto_validate": "true"
        }
    }
    
    mock_manager.get_setting.side_effect = lambda section, key, default=None: (
        mock_manager.config_data.get(section, {}).get(key, default)
    )
    mock_manager.get_master_path.return_value = Path("data/master")
    mock_manager.get_input_file_path.return_value = Path("data/input.csv")
    mock_manager.get_log_directory.return_value = Path("logs")
    
    return mock_manager


@pytest.fixture
def mock_csv_processor():
    """创建模拟CSV处理器"""
    from unittest.mock import Mock
    from src.data.csv_processor import CSVProcessor
    
    mock_processor = Mock(spec=CSVProcessor)
    
    # 模拟读取CSV数据
    sample_data = [
        {"product_id": "P001", "model": "MODEL_A", "quantity": "10"},
        {"product_id": "P002", "model": "MODEL_B", "quantity": "5"},
        {"product_id": "P003", "model": "MODEL_C", "quantity": "8"}
    ]
    
    mock_processor.read_csv.return_value = sample_data
    mock_processor.process_input_csv.return_value = sample_data
    mock_processor.write_csv.return_value = True
    mock_processor.validate_data.return_value = []
    
    return mock_processor


@pytest.fixture
def mock_data_manager():
    """创建模拟数据管理器"""
    from unittest.mock import Mock
    from src.data.data_manager import DataManager
    
    mock_manager = Mock(spec=DataManager)
    
    # 模拟产品数据
    product_data = {
        "MODEL_A": {
            "product_id": "P001",
            "model": "MODEL_A",
            "length": 100.0,
            "width": 50.0,
            "height": 25.0,
            "density": 1.0,
            "material": "Steel"
        },
        "MODEL_B": {
            "product_id": "P002",
            "model": "MODEL_B",
            "length": 150.0,
            "width": 75.0,
            "height": 30.0,
            "density": 1.2,
            "material": "Aluminum"
        }
    }
    
    mock_manager.get_product_data.side_effect = lambda model: product_data.get(model)
    mock_manager.load_csv_files.return_value = True
    mock_manager.master_data = product_data
    
    return mock_manager


@pytest.fixture
def mock_calculation_engine():
    """创建模拟计算引擎"""
    from unittest.mock import Mock
    from src.utils.calculation import CalculationEngine
    
    mock_engine = Mock(spec=CalculationEngine)
    
    # 模拟计算函数
    mock_engine.evaluate_formula.side_effect = lambda formula, variables: eval(formula, {}, variables)
    mock_engine.calculate_geometry.side_effect = lambda calc_type, parameters: {
        "volume": parameters.get("length", 0) * parameters.get("width", 0) * parameters.get("height", 0),
        "surface_area": 2 * (parameters.get("length", 0) * parameters.get("width", 0) + 
                           parameters.get("length", 0) * parameters.get("height", 0) + 
                           parameters.get("width", 0) * parameters.get("height", 0)),
        "weight": (parameters.get("length", 0) * parameters.get("width", 0) * parameters.get("height", 0)) * 
                 parameters.get("density", 1.0)
    }.get(calc_type)
    
    mock_engine.validate_calculation.return_value = True
    
    return mock_engine


@pytest.fixture
def test_logger():
    """创建测试日志记录器"""
    import logging
    
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.DEBUG)
    
    # 如果没有处理器，添加一个
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


@pytest.fixture(autouse=True)
def setup_test_environment():
    """自动设置测试环境"""
    # 设置测试环境变量
    import os
    original_env = os.environ.copy()
    
    # 设置测试特定的环境变量
    os.environ["TEST_MODE"] = "true"
    os.environ["PYTHONPATH"] = str(Path(__file__).parent.parent)
    
    yield
    
    # 恢复原始环境
    os.environ.clear()
    os.environ.update(original_env)


def pytest_configure(config):
    """配置pytest"""
    # 添加自定义标记
    config.addinivalue_line(
        "markers", "slow: 标记为慢速测试（需要较长时间运行）"
    )
    config.addinivalue_line(
        "markers", "integration: 标记为集成测试"
    )
    config.addinivalue_line(
        "markers", "e2e: 标记为端到端测试"
    )
    config.addinivalue_line(
        "markers", "unit: 标记为单元测试"
    )


def pytest_collection_modifyitems(config, items):
    """修改测试项集合"""
    # 根据标记重新排序测试
    unit_tests = []
    integration_tests = []
    e2e_tests = []
    slow_tests = []
    other_tests = []
    
    for item in items:
        if item.get_closest_marker("slow"):
            slow_tests.append(item)
        elif item.get_closest_marker("e2e"):
            e2e_tests.append(item)
        elif item.get_closest_marker("integration"):
            integration_tests.append(item)
        elif item.get_closest_marker("unit"):
            unit_tests.append(item)
        else:
            other_tests.append(item)
    
    # 重新排序：单元测试 -> 集成测试 -> 端到端测试 -> 慢速测试 -> 其他测试
    items[:] = unit_tests + integration_tests + e2e_tests + slow_tests + other_tests
