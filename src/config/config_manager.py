import configparser
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    """配置管理器，负责读取和解析应用程序配置"""
    
    def __init__(self, config_path: str = "config/app_config.ini"):
        self.config_path = Path(config_path)
        self.config_data = {}
        self.logger = logging.getLogger(__name__)
        
    def load_config(self) -> bool:
        """加载配置文件"""
        try:
            if not self.config_path.exists():
                self.logger.warning(f"配置文件不存在: {self.config_path}")
                self._create_default_config()
                return True
                
            config = configparser.ConfigParser()
            config.read(self.config_path, encoding='utf-8')
            
            # 转换为字典格式
            for section in config.sections():
                self.config_data[section] = dict(config.items(section))
                
            self.logger.info(f"配置文件加载成功: {self.config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {e}")
            return False
            
    def _create_default_config(self):
        """创建默认配置文件"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            config = configparser.ConfigParser()
            
            # 路径配置
            config['PATHS'] = {
                'master_directory': 'data/master',
                'log_directory': 'logs',
                'input_file': 'data/input.csv',
                'output_directory': 'output'
            }
            
            # 应用程序设置
            config['APPLICATION'] = {
                'version': '2.05',
                'language': 'zh-CN',
                'auto_save': 'true',
                'backup_enabled': 'true'
            }
            
            # 界面设置
            config['UI'] = {
                'theme': 'default',
                'font_size': '10',
                'window_width': '1024',
                'window_height': '768'
            }
            
            # 计算参数
            config['CALCULATION'] = {
                'precision': '4',
                'rounding_method': 'round',
                'auto_validate': 'true'
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                config.write(f)
                
            self.logger.info(f"默认配置文件已创建: {self.config_path}")
            
            # 修复: 创建默认配置后加载配置数据
            self.load_config()
            
        except Exception as e:
            self.logger.error(f"创建默认配置文件失败: {e}")
            
    def get_setting(self, section: str, key: str, default: Any = None) -> Any:
        """获取配置项"""
        try:
            return self.config_data.get(section, {}).get(key, default)
        except Exception as e:
            self.logger.warning(f"获取配置项失败 [{section}.{key}]: {e}")
            return default
            
    def set_setting(self, section: str, key: str, value: Any) -> bool:
        """设置配置项"""
        try:
            if section not in self.config_data:
                self.config_data[section] = {}
                
            self.config_data[section][key] = str(value)
            return True
        except Exception as e:
            self.logger.error(f"设置配置项失败 [{section}.{key}]: {e}")
            return False
            
    def save_config(self) -> bool:
        """保存配置到文件"""
        try:
            config = configparser.ConfigParser()
            
            for section, settings in self.config_data.items():
                config[section] = settings
                
            with open(self.config_path, 'w', encoding='utf-8') as f:
                config.write(f)
                
            self.logger.info(f"配置文件已保存: {self.config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存配置文件失败: {e}")
            return False
            
    def get_master_path(self, subdirectory: str = "") -> Path:
        """获取master目录路径"""
        master_dir = self.get_setting('PATHS', 'master_directory')
        # 修复: 当配置值为空时使用默认值
        if not master_dir:
            master_dir = 'data/master'
        base_path = Path(master_dir)
        if subdirectory:
            return base_path / subdirectory
        return base_path
        
    def get_input_file_path(self) -> Path:
        """获取输入文件路径"""
        input_file = self.get_setting('PATHS', 'input_file')
        # 修复: 当配置值为空时使用默认值
        if not input_file:
            input_file = 'data/input.csv'
        return Path(input_file)
        
    def get_log_directory(self) -> Path:
        """获取日志目录路径"""
        log_dir = self.get_setting('PATHS', 'log_directory')
        # 修复: 当配置值为空时使用默认值
        if not log_dir:
            log_dir = 'logs'
        return Path(log_dir)
