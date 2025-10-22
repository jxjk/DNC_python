"""
DNC参数计算系统 - 配置管理单元测试
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from src.config.config_manager import ConfigManager


class TestConfigManager:
    """配置管理器测试"""
    
    def test_config_manager_creation(self):
        """测试配置管理器创建"""
        config_manager = ConfigManager("config/test_config.ini")
        assert config_manager.config_path == Path("config/test_config.ini")
        assert config_manager.config_data == {}
    
    def test_load_config_success(self, temp_config_dir):
        """测试成功加载配置文件"""
        config_path = temp_config_dir / "config.ini"
        
        # 创建测试配置文件
        config_content = """
[PATHS]
master_directory = data/master
log_directory = logs

[APPLICATION]
version = 2.05
language = zh-CN
"""
        config_path.write_text(config_content, encoding='utf-8')
        
        config_manager = ConfigManager(str(config_path))
        success = config_manager.load_config()
        
        assert success is True
        assert "PATHS" in config_manager.config_data
        assert "APPLICATION" in config_manager.config_data
        assert config_manager.config_data["PATHS"]["master_directory"] == "data/master"
        assert config_manager.config_data["APPLICATION"]["version"] == "2.05"
    
    def test_load_config_file_not_found(self, temp_config_dir):
        """测试配置文件不存在时创建默认配置"""
        config_path = temp_config_dir / "nonexistent.ini"
        config_manager = ConfigManager(str(config_path))
        
        success = config_manager.load_config()
        
        assert success is True
        assert config_path.exists()  # 应该创建了默认配置文件
        assert "PATHS" in config_manager.config_data
        assert "APPLICATION" in config_manager.config_data
    
    def test_get_setting(self, temp_config_dir):
        """测试获取配置项"""
        config_path = temp_config_dir / "config.ini"
        
        # 创建测试配置文件
        config_content = """
[PATHS]
master_directory = data/master
log_directory = logs

[APPLICATION]
version = 2.05
"""
        config_path.write_text(config_content, encoding='utf-8')
        
        config_manager = ConfigManager(str(config_path))
        config_manager.load_config()
        
        # 测试获取存在的配置项
        master_dir = config_manager.get_setting("PATHS", "master_directory")
        assert master_dir == "data/master"
        
        # 测试获取不存在的配置项（使用默认值）
        nonexistent = config_manager.get_setting("PATHS", "nonexistent", "default_value")
        assert nonexistent == "default_value"
        
        # 测试获取不存在的section
        section_nonexistent = config_manager.get_setting("NONE", "key", "default")
        assert section_nonexistent == "default"
    
    def test_set_setting(self, temp_config_dir):
        """测试设置配置项"""
        config_path = temp_config_dir / "config.ini"
        config_content = """
[PATHS]
master_directory = data/master
"""
        config_path.write_text(config_content, encoding='utf-8')
        
        config_manager = ConfigManager(str(config_path))
        config_manager.load_config()
        
        # 测试设置新配置项
        success = config_manager.set_setting("PATHS", "new_directory", "data/new")
        assert success is True
        assert config_manager.config_data["PATHS"]["new_directory"] == "data/new"
        
        # 测试更新现有配置项
        success = config_manager.set_setting("PATHS", "master_directory", "data/updated")
        assert success is True
        assert config_manager.config_data["PATHS"]["master_directory"] == "data/updated"
        
        # 测试设置到新section
        success = config_manager.set_setting("NEW_SECTION", "key", "value")
        assert success is True
        assert config_manager.config_data["NEW_SECTION"]["key"] == "value"
    
    def test_save_config(self, temp_config_dir):
        """测试保存配置"""
        config_path = temp_config_dir / "config.ini"
        config_manager = ConfigManager(str(config_path))
        
        # 设置一些配置项
        config_manager.set_setting("PATHS", "master_directory", "data/master")
        config_manager.set_setting("APPLICATION", "version", "2.05")
        
        # 保存配置
        success = config_manager.save_config()
        
        assert success is True
        assert config_path.exists()
        
        # 验证保存的内容
        saved_content = config_path.read_text(encoding='utf-8')
        assert "[PATHS]" in saved_content
        assert "master_directory = data/master" in saved_content
        assert "[APPLICATION]" in saved_content
        assert "version = 2.05" in saved_content
    
    def test_get_master_path(self, temp_config_dir):
        """测试获取master目录路径"""
        config_path = temp_config_dir / "config.ini"
        config_content = """
[PATHS]
master_directory = data/master
"""
        config_path.write_text(config_content, encoding='utf-8')
        
        config_manager = ConfigManager(str(config_path))
        config_manager.load_config()
        
        # 测试获取基础路径
        master_path = config_manager.get_master_path()
        assert master_path == Path("data/master")
        
        # 测试获取子目录路径
        sub_path = config_manager.get_master_path("subdirectory")
        assert sub_path == Path("data/master/subdirectory")
        
        # 测试默认值
        config_manager.config_data["PATHS"]["master_directory"] = ""
        default_path = config_manager.get_master_path()
        assert default_path == Path("data/master")
    
    def test_get_input_file_path(self, temp_config_dir):
        """测试获取输入文件路径"""
        config_path = temp_config_dir / "config.ini"
        config_content = """
[PATHS]
input_file = data/input.csv
"""
        config_path.write_text(config_content, encoding='utf-8')
        
        config_manager = ConfigManager(str(config_path))
        config_manager.load_config()
        
        input_path = config_manager.get_input_file_path()
        assert input_path == Path("data/input.csv")
        
        # 测试默认值
        config_manager.config_data["PATHS"]["input_file"] = ""
        default_path = config_manager.get_input_file_path()
        assert default_path == Path("data/input.csv")
    
    def test_get_log_directory(self, temp_config_dir):
        """测试获取日志目录路径"""
        config_path = temp_config_dir / "config.ini"
        config_content = """
[PATHS]
log_directory = logs
"""
        config_path.write_text(config_content, encoding='utf-8')
        
        config_manager = ConfigManager(str(config_path))
        config_manager.load_config()
        
        log_dir = config_manager.get_log_directory()
        assert log_dir == Path("logs")
        
        # 测试默认值
        config_manager.config_data["PATHS"]["log_directory"] = ""
        default_dir = config_manager.get_log_directory()
        assert default_dir == Path("logs")
    
    def test_create_default_config(self, temp_config_dir):
        """测试创建默认配置"""
        config_path = temp_config_dir / "default_config.ini"
        config_manager = ConfigManager(str(config_path))
        
        # 调用内部方法创建默认配置
        config_manager._create_default_config()
        
        assert config_path.exists()
        
        # 验证默认配置内容
        config_manager.load_config()
        assert "PATHS" in config_manager.config_data
        assert "APPLICATION" in config_manager.config_data
        assert "UI" in config_manager.config_data
        assert "CALCULATION" in config_manager.config_data
        
        # 验证具体配置项
        assert config_manager.config_data["PATHS"]["master_directory"] == "data/master"
        assert config_manager.config_data["APPLICATION"]["version"] == "2.05"
        assert config_manager.config_data["UI"]["theme"] == "default"
        assert config_manager.config_data["CALCULATION"]["precision"] == "4"


if __name__ == "__main__":
    pytest.main([__file__])
