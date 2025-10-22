"""
DNC参数计算系统 - pytest配置
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent


@pytest.fixture
def temp_config_dir():
    """创建临时配置目录"""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = Path(temp_dir) / "config"
        config_dir.mkdir()
        
        # 复制配置文件
        original_config = PROJECT_ROOT / "config" / "config.ini"
        if original_config.exists():
            shutil.copy(original_config, config_dir / "config.ini")
        
        yield config_dir


@pytest.fixture
def temp_data_dir():
    """创建临时数据目录"""
    with tempfile.TemporaryDirectory() as temp_dir:
        data_dir = Path(temp_dir) / "data"
        master_dir = data_dir / "master"
        master_dir.mkdir(parents=True)
        
        # 创建测试数据文件
        test_csv_content = """product_id,model,quantity
P001,MODEL_A,10
P002,MODEL_B,5
P003,MODEL_C,8"""
        
        test_file = master_dir / "test_input.csv"
        test_file.write_text(test_csv_content, encoding='utf-8')
        
        yield data_dir


@pytest.fixture
def sample_product_data():
    """提供示例产品数据"""
    return {
        "product_id": "P001",
        "product_type": "MODEL_A",
        "parameters": {
            "length": 100.0,
            "width": 50.0,
            "height": 25.0,
            "density": 1.0
        },
        "quantity": 10
    }


@pytest.fixture
def sample_input_record():
    """提供示例输入记录"""
    return {
        "product_id": "P001",
        "model": "MODEL_A",
        "quantity": 10,
        "master_data": {
            "length": 100.0,
            "width": 50.0,
            "height": 25.0
        }
    }


@pytest.fixture
def sample_calculation_result():
    """提供示例计算结果"""
    return {
        "product_type": "MODEL_A",
        "input_parameters": {
            "length": 100.0,
            "width": 50.0,
            "height": 25.0
        },
        "calculated_parameters": {
            "volume": 125000.0,
            "surface_area": 17500.0,
            "weight": 125000.0
        },
        "success": True,
        "error_message": None,
        "calculation_time": 0.001
    }


@pytest.fixture(autouse=True)
def setup_test_environment():
    """设置测试环境"""
    # 保存原始环境
    original_cwd = os.getcwd()
    
    # 切换到项目根目录
    os.chdir(PROJECT_ROOT)
    
    yield
    
    # 恢复原始环境
    os.chdir(original_cwd)


def pytest_configure(config):
    """pytest配置钩子"""
    # 添加自定义标记
    config.addinivalue_line(
        "markers", "slow: 标记为慢速测试"
    )
    config.addinivalue_line(
        "markers", "integration: 标记为集成测试"
    )
    config.addinivalue_line(
        "markers", "unit: 标记为单元测试"
    )


def pytest_collection_modifyitems(config, items):
    """修改测试项集合"""
    # 根据标记重新排序测试
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(pytest.mark.slow)
        if "integration" in item.keywords:
            item.add_marker(pytest.mark.integration)
        if "unit" in item.keywords:
            item.add_marker(pytest.mark.unit)
