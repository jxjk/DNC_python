# file: c:\Users\Lenovo\Desktop\DNC_python\DNC_Python_System_Documentation\DNC_整理文档\dnc_python_project\src\core\config.py
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
class DeviceConfig:
    """设备配置"""
    device_name: str = "DefaultDevice"
    device_model: str = "DefaultModel"
    manufacturer: str = "DefaultManufacturer"
    firmware_version: str = "1.0.0"
    serial_number: str = "00000000"

@dataclass
class QRCodeConfig:
    """QR码识别配置"""
    qr_mode: int = 1
    qr_split_str: str = "@"
    model_place: int = 1
    po_place: int = 0
    qty_place: int = 2
    barcode_header_str_num: int = 11
    decimal_place: int = 2

@dataclass
class NCCommunicationConfig:
    """NC通信配置"""
    protocol: str = "rexroth"
    host: str = "192.168.1.100"
    port: int = 502
    timeout: int = 30
    retry_count: int = 3

@dataclass
class CommunicationConfig:
    """通信配置"""
    com_type: int = 0  # 0: 串口, 1: 网络
    com_port: str = "COM1"
    baud_rate: int = 9600
    data_bits: int = 8
    parity: str = 'N'
    stop_bits: int = 1
    ip_address: str = "192.168.1.100"
    port: int = 8080

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
        self.com_config = CommunicationConfig()
        self.device_config = DeviceConfig()
        self.ui_config = UIConfig()
        self.system_config = SystemConfig()
        
        # 配置文件路径
        self.config_file = self.config_path / "system_config.json"
        # 使用master文件夹而不是创建csv文件夹
        self.csv_config_dir = self.config_path / "master"
        
        # 确保目录存在
        self.config_path.mkdir(parents=True, exist_ok=True)
        # 不创建csv文件夹，直接使用master文件夹
        
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
            
            # 加载CSV配置 - 覆盖默认值
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
            
    def get_config(self, filename: str) -> List[Dict[str, str]]:
        """
        获取CSV配置文件数据
        
        Args:
            filename: CSV文件名
            
        Returns:
            List[Dict[str, str]]: CSV数据，每行作为一个字典
        """
        try:
            # 使用CSV处理器读取配置文件
            from src.data.csv_processor import CSVProcessor
            csv_processor = CSVProcessor(self)
            
            # 读取CSV文件为字典列表
            data = csv_processor.read_config_csv_as_dict(filename)
            
            self.logger.debug(f"加载配置文件: {filename}, 共{len(data)}行")
            return data
            
        except Exception as e:
            self.logger.error(f"获取配置文件失败: {filename}, 错误: {e}")
            return []

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
            'com': self.com_config,
            'device': self.device_config,
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
            'com': self.com_config,
            'device': self.device_config,
            'ui': self.ui_config,
            'system': self.system_config
        }
        
        if section in config_objects:
            if hasattr(config_objects[section], key):
                setattr(config_objects[section], key, value)
                return True
        return False
        
    def get_csv_config_path(self, filename: str, program_no: int = None) -> Path:
        """
        获取CSV配置文件路径
        
        Args:
            filename: CSV文件名
            program_no: 程序编号（可选）
            
        Returns:
            Path: 完整文件路径
        """
        base_path = self.csv_config_dir
        
        # 首先在master根目录查找
        root_path = base_path / filename
        if root_path.exists():
            return root_path
        
        # 如果指定了程序编号，尝试在对应的prg目录中查找
        if program_no is not None:
            # 根据prg.csv映射关系查找对应的prg目录
            prg_dir = self._get_prg_directory(program_no)
            if prg_dir:
                prg_path = base_path / prg_dir / filename
                if prg_path.exists():
                    return prg_path
        
        # 如果都找不到，返回根目录路径（用于创建新文件）
        return root_path

    def _get_prg_directory(self, program_no: int) -> Optional[str]:
        """
        根据程序编号获取对应的prg目录
        
        Args:
            program_no: 程序编号
            
        Returns:
            Optional[str]: prg目录名称，如果找不到返回None
        """
        try:
            # 读取prg.csv文件获取映射关系
            prg_csv_path = self.csv_config_dir / "prg.csv"
            if not prg_csv_path.exists():
                return None
            
            import csv
            with open(prg_csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if int(row['PRGNO']) == program_no:
                        return row['PRGNAME']
            
            return None
            
        except Exception as e:
            self.logger.error(f"获取prg目录映射失败: {e}")
            return None
    
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
        self.com_config = CommunicationConfig()
        self.device_config = DeviceConfig()
        self.ui_config = UIConfig()
        self.system_config = SystemConfig()
        self.logger.info("配置已重置为默认值")
    
    def _load_from_dict(self, config_data: Dict[str, Any]) -> None:
        """从字典加载配置"""
        if 'qr_config' in config_data:
            self.qr_config = QRCodeConfig(**config_data['qr_config'])
        if 'nc_config' in config_data:
            self.nc_config = NCCommunicationConfig(**config_data['nc_config'])
        if 'com_config' in config_data:
            self.com_config = CommunicationConfig(**config_data['com_config'])
        if 'device_config' in config_data:
            self.device_config = DeviceConfig(**config_data['device_config'])
        if 'ui_config' in config_data:
            self.ui_config = UIConfig(**config_data['ui_config'])
        if 'system_config' in config_data:
            self.system_config = SystemConfig(**config_data['system_config'])
    
    def _to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'qr_config': asdict(self.qr_config),
            'nc_config': asdict(self.nc_config),
            'com_config': asdict(self.com_config),
            'device_config': asdict(self.device_config),
            'ui_config': asdict(self.ui_config),
            'system_config': asdict(self.system_config)
        }
    
    def _load_csv_configs(self) -> None:
        """加载CSV配置文件并更新配置对象"""
        try:
            # 加载ini.csv配置
            ini_config = self.get_config('ini.csv')
            self.logger.info(f"加载ini.csv配置: {len(ini_config)}行")
            
            if ini_config:
                for row in ini_config:
                    define = row.get('DEFINE')
                    value = row.get('VALUE')
                    
                    self.logger.info(f"处理配置项: DEFINE={define}, VALUE={value}")
                    
                    if define == 'QRmode':
                        self.qr_config.qr_mode = int(value)
                        self.logger.info(f"设置QR模式: {value}")
                    elif define == 'QRspltStr':
                        self.qr_config.qr_split_str = value
                        self.logger.info(f"设置QR分隔符: {value}")
                    elif define == 'MODELplc':
                        self.qr_config.model_place = int(value)
                        self.logger.info(f"设置型号位置: {value}")
                    elif define == 'POplc':
                        self.qr_config.po_place = int(value)
                        self.logger.info(f"设置PO位置: {value}")
                    elif define == 'QTYplc':
                        self.qr_config.qty_place = int(value)
                        self.logger.info(f"设置数量位置: {value}")
                    elif define == 'BarCodeHeaderStrNum':
                        self.qr_config.barcode_header_str_num = int(value)
                        self.logger.info(f"设置条码头长度: {value}")
                    # 添加缺失的配置项加载
                    elif define == 'DecimalPlace':
                        self.qr_config.decimal_place = int(value)
                        self.logger.info(f"设置小数位数: {value}")
                        
            # 记录最终配置状态
            self.logger.info(f"最终QR配置: qr_mode={self.qr_config.qr_mode}, model_place={self.qr_config.model_place}, split_str='{self.qr_config.qr_split_str}'")
                        
        except Exception as e:
            self.logger.error(f"加载CSV配置失败: {e}")
    
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

    def get_device_status(self) -> Dict[str, Any]:
        """获取设备状态"""
        try:
            # 这里实现实际的设备状态检查逻辑
            # 例如检查NC设备连接状态
            return {
                'running': False,  # 示例值，需要根据实际情况实现
                'connected': True,
                'error': None
            }
        except Exception as e:
            self.logger.error(f"获取设备状态失败: {str(e)}")
            return {'running': False, 'connected': False, 'error': str(e)}

    def get_nc_communication_status(self) -> Dict[str, Any]:
        """获取NC通信状态"""
        try:
            # 这里实现实际的NC通信状态检查逻辑
            return {
                'busy': False,  # 示例值，需要根据实际情况实现
                'connected': True,
                'last_communication': None
            }
        except Exception as e:
            self.logger.error(f"获取NC通信状态失败: {str(e)}")
            return {'busy': False, 'connected': False, 'error': str(e)}

    def validate_config_consistency(self) -> Dict[str, List[str]]:
        """验证配置一致性"""
        issues = []
        
        # 检查QR配置一致性
        ini_config = self.get_config('ini.csv')
        if ini_config:
            # 检查QRmode
            qr_mode_from_ini = next((row for row in ini_config if row.get('DEFINE') == 'QRmode'), None)
            if qr_mode_from_ini and int(qr_mode_from_ini.get('VALUE')) != self.qr_config.qr_mode:
                issues.append(f"QR模式不一致: ini.csv={qr_mode_from_ini.get('VALUE')}, ConfigManager={self.qr_config.qr_mode}")
                
            # 检查MODELplc
            model_plc_from_ini = next((row for row in ini_config if row.get('DEFINE') == 'MODELplc'), None)
            if model_plc_from_ini and int(model_plc_from_ini.get('VALUE')) != self.qr_config.model_place:
                issues.append(f"型号位置不一致: ini.csv={model_plc_from_ini.get('VALUE')}, ConfigManager={self.qr_config.model_place}")
        
        # 检查属性完整性
        required_attrs = ['qr_mode', 'qr_split_str', 'model_place', 'po_place', 'qty_place', 'barcode_header_str_num', 'decimal_place']
        for attr in required_attrs:
            if not hasattr(self.qr_config, attr):
                issues.append(f"QRCodeConfig缺少属性: {attr}")
        
        return {'consistency_issues': issues}

    # 新增表单相关配置方法
    def get_form_control_config(self) -> List[Dict[str, str]]:
        """获取表单控制配置"""
        return self.get_config('cntrl.csv')

    def get_load_config(self) -> List[Dict[str, str]]:
        """获取load配置"""
        return self.get_config('load.csv')

    def get_input_config(self) -> List[Dict[str, str]]:
        """获取input配置"""
        return self.get_config('input.csv')

    def get_correct_config(self) -> List[Dict[str, str]]:
        """获取correct配置"""
        return self.get_config('correct.csv')

    def get_measure_config(self) -> List[Dict[str, str]]:
        """获取measure配置"""
        return self.get_config('measure.csv')

    def get_select_config(self) -> List[Dict[str, str]]:
        """获取select配置"""
        return self.get_config('select.csv')

    def get_switch_config(self) -> List[Dict[str, str]]:
        """获取switch配置"""
        return self.get_config('switch.csv')

    def get_relation_config(self) -> List[Dict[str, str]]:
        """获取relation配置"""
        return self.get_config('relation.csv')

    def get_add_config(self) -> List[Dict[str, str]]:
        """获取add配置"""
        return self.get_config('add.csv')

    def get_change_prg_config(self) -> List[Dict[str, str]]:
        """获取changePRG配置"""
        return self.get_config('changePRG.csv')

    def get_select_prg_config(self) -> List[Dict[str, str]]:
        """获取selectPRG配置"""
        return self.get_config('selectPRG.csv')


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
