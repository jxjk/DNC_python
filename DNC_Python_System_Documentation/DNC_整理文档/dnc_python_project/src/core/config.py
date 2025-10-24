"""
配置管理器
负责系统配置的加载、保存和管理
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class QRCodeConfig:
    """QR码识别配置"""
    qr_mode: int = 1
    qr_split_str: str = "@"
    model_place: int = 2
    po_place: int = 1
    qty_place: int = 3
    barcode_header_str_num: int = 11


@dataclass
class NCCommunicationConfig:
    """NC通信配置"""
    protocol: str = "rexroth"
    host: str = "192.168.1.100"
    port: int = 502
    timeout: int = 30
    retry_count: int = 3


@dataclass
class UIConfig:
    """界面配置"""
    window_width: int = 1024
    window_height: int = 768
    theme: str = "default"
    language: str = "zh-CN"
    font_size: int = 10


@dataclass
class SystemConfig:
    """系统配置"""
    version: str = "1.0.0"
    log_level: str = "INFO"
    data_path: str = "data/"
    backup_path: str = "backup/"
    auto_save: bool = True
    auto_backup: bool = True


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = "config/"):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = Path(config_path)
        self.logger = logging.getLogger(__name__)
        
        # 配置对象
        self.qr_config = QRCodeConfig()
        self.nc_config = NCCommunicationConfig()
        self.ui_config = UIConfig()
        self.system_config = SystemConfig()
        
        # 配置文件路径
        self.config_file = self.config_path / "system_config.json"
        self.csv_config_dir = self.config_path / "csv"
        
        # 确保目录存在
        self.config_path.mkdir(parents=True, exist_ok=True)
        self.csv_config_dir.mkdir(parents=True, exist_ok=True)
        
    def load_config(self) -> bool:
        """
        加载配置
        
        Returns:
            bool: 加载是否成功
        """
        try:
            # 加载JSON配置
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                self._load_from_dict(config_data)
            
            # 加载CSV配置
            self._load_csv_configs()
            
            self.logger.info("配置加载成功")
            return True
            
        except Exception as e:
            self.logger.error(f"配置加载失败: {e}")
            # 使用默认配置
            self._create_default_configs()
            return False
    
    def save_config(self) -> bool:
        """
        保存配置
        
        Returns:
            bool: 保存是否成功
        """
        try:
            config_data = self._to_dict()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            # 保存CSV配置
            self._save_csv_configs()
            
            self.logger.info("配置保存成功")
            return True
            
        except Exception as e:
            self.logger.error(f"配置保存失败: {e}")
            return False
    
    def get_config_value(self, section: str, key: str) -> Any:
        """
        获取配置值
        
        Args:
            section: 配置节
            key: 配置键
            
        Returns:
            Any: 配置值
        """
        config_objects = {
            'qr': self.qr_config,
            'nc': self.nc_config,
            'ui': self.ui_config,
            'system': self.system_config
        }
        
        if section in config_objects:
            return getattr(config_objects[section], key, None)
        return None
    
    def set_config_value(self, section: str, key: str, value: Any) -> bool:
        """
        设置配置值
        
        Args:
            section: 配置节
            key: 配置键
            value: 配置值
            
        Returns:
            bool: 设置是否成功
        """
        config_objects = {
            'qr': self.qr_config,
            'nc': self.nc_config,
            'ui': self.ui_config,
            'system': self.system_config
        }
        
        if section in config_objects:
            if hasattr(config_objects[section], key):
                setattr(config_objects[section], key, value)
                return True
        return False
    
    def get_csv_config_path(self, filename: str) -> Path:
        """
        获取CSV配置文件路径
        
        Args:
            filename: CSV文件名
            
        Returns:
            Path: 完整文件路径
        """
        return self.csv_config_dir / filename
    
    def validate_config(self) -> Dict[str, List[str]]:
        """
        验证配置
        
        Returns:
            Dict[str, List[str]]: 验证结果，包含错误和警告
        """
        errors = []
        warnings = []
        
        # 验证QR码配置
        if self.qr_config.qr_mode not in [0, 1]:
            errors.append("QR模式必须为0或1")
        
        if not self.qr_config.qr_split_str:
            warnings.append("QR分隔符为空，使用默认值@")
        
        # 验证NC通信配置
        if not self.nc_config.host:
            errors.append("NC主机地址不能为空")
        
        if self.nc_config.port < 1 or self.nc_config.port > 65535:
            errors.append("NC端口号必须在1-65535范围内")
        
        # 验证系统配置
        if not Path(self.system_config.data_path).exists():
            warnings.append(f"数据路径不存在: {self.system_config.data_path}")
        
        return {
            'errors': errors,
            'warnings': warnings
        }
    
    def reset_to_defaults(self) -> None:
        """重置为默认配置"""
        self.qr_config = QRCodeConfig()
        self.nc_config = NCCommunicationConfig()
        self.ui_config = UIConfig()
        self.system_config = SystemConfig()
        self.logger.info("配置已重置为默认值")
    
    def _load_from_dict(self, config_data: Dict[str, Any]) -> None:
        """从字典加载配置"""
        if 'qr_config' in config_data:
            self.qr_config = QRCodeConfig(**config_data['qr_config'])
        if 'nc_config' in config_data:
            self.nc_config = NCCommunicationConfig(**config_data['nc_config'])
        if 'ui_config' in config_data:
            self.ui_config = UIConfig(**config_data['ui_config'])
        if 'system_config' in config_data:
            self.system_config = SystemConfig(**config_data['system_config'])
    
    def _to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'qr_config': asdict(self.qr_config),
            'nc_config': asdict(self.nc_config),
            'ui_config': asdict(self.ui_config),
            'system_config': asdict(self.system_config)
        }
    
    def _load_csv_configs(self) -> None:
        """加载CSV配置文件"""
        # 这里可以添加CSV配置文件的加载逻辑
        # 例如：ini.csv, header.csv, type_define.csv等
        pass
    
    def _save_csv_configs(self) -> None:
        """保存CSV配置文件"""
        # 这里可以添加CSV配置文件的保存逻辑
        pass
    
    def _create_default_configs(self) -> None:
        """创建默认配置文件"""
        default_csv_files = {
            'ini.csv': "QRmode,1\nQRspltStr,@\nMODELplc,2\nPOplc,1\nQTYplc,3",
            'header.csv': "C,del\nX,keep",
            'type_define.csv': "NO,TYPE\n1,AAA\n2,C-CCC\n3,C-CCC10",
            'type_prg.csv': "NO,prg1,prg2,prg3\n1,1,2,3\n2,4,5,6\n3,7,8,9",
            'load.csv': "NO,MACRO,VALUE\n1,#500,10\n2,#501,20A\n3,#502,6",
            'define.csv': "DEFINE,STR,BEFORE,AFTER,CHNGVL,CALC\ndefine3-2,P,P5,5,chngS,calc2-2",
            'chngValue.csv': "DEFINE,BEFORE,AFTER\nchngS,S,1",
            'calc.csv': "DEFINE,1,2,3,4,5,6,7,8,9,10\ncalc2-2,=,calc2-2,+,1",
            'relation.csv': "DEFINE,VALUE,1,2,3,4,5,6,7,8\nrelation10,1,and,#505M,>=,0,and,#505M,<=,1",
            'cntrl.csv': "NO,KIND,MACRO,DISPFLG,ROW,COLUMN\n1,load,#500,1,1,1\n2,input,#501,1,1,2"
        }
        
        for filename, content in default_csv_files.items():
            file_path = self.csv_config_dir / filename
            if not file_path.exists():
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
        
        self.logger.info("默认配置文件已创建")


class ConfigValidator:
    """配置验证器"""
    
    @staticmethod
    def validate_qr_config(config: QRCodeConfig) -> List[str]:
        """验证QR码配置"""
        errors = []
        
        if config.qr_mode not in [0, 1]:
            errors.append("QR模式必须为0或1")
        
        if not config.qr_split_str:
            errors.append("QR分隔符不能为空")
        
        if config.model_place < 1:
            errors.append("型号位置必须大于0")
        
        return errors
    
    @staticmethod
    def validate_nc_config(config: NCCommunicationConfig) -> List[str]:
        """验证NC通信配置"""
        errors = []
        
        if not config.host:
            errors.append("主机地址不能为空")
        
        if config.port < 1 or config.port > 65535:
            errors.append("端口号必须在1-65535范围内")
        
        if config.timeout < 1:
            errors.append("超时时间必须大于0")
        
        if config.retry_count < 0:
            errors.append("重试次数不能为负数")
        
        return errors
    
    @staticmethod
    def validate_system_config(config: SystemConfig) -> List[str]:
        """验证系统配置"""
        errors = []
        
        if not config.data_path:
            errors.append("数据路径不能为空")
        
        if not config.backup_path:
            errors.append("备份路径不能为空")
        
        return errors
