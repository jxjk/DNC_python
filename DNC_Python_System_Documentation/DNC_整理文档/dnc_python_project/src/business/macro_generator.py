# src/business/macro_generator.py
"""
宏文件生成器
根据动态参数生成macro.txt文件
"""

import os
import csv
import re
import json
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

from ..utils.logger import get_logger


@dataclass
class FileGenerationResult:
    """文件生成结果"""
    success: bool
    file_path: str = None
    error_message: str = None
    details: Dict[str, Any] = None
    
    @classmethod
    def success(cls, file_path: str, details: Dict[str, Any] = None) -> 'FileGenerationResult':
        """创建成功结果"""
        return cls(success=True, file_path=file_path, details=details)
    
    @classmethod
    def error(cls, error_message: str, details: Dict[str, Any] = None) -> 'FileGenerationResult':
        """创建错误结果"""
        return cls(success=False, error_message=error_message, details=details)


@dataclass
class GenerationHistory:
    """生成历史记录"""
    timestamp: str
    file_path: str
    variables_count: int
    model_string: str = ""
    program_sequence: List[str] = None


@dataclass
class Variable:
    """变量定义"""
    name: str
    kind: str
    value: Any = None
    definition: str = None
    display_flag: bool = True
    send_flag: bool = True
    min_value: float = None
    max_value: float = None
    label_text: str = ""
    error_message: str = None


class FileGenerationError(Exception):
    """文件生成错误异常"""
    pass


class DeviceStatusError(Exception):
    """设备状态错误异常"""
    pass


class VariableValidationError(Exception):
    """变量验证错误异常"""
    pass


class FileGenerationFlow:
    """文件生成流程 - 按照标准流程实现宏文件生成"""
    
    def __init__(self, config_manager, csv_processor):
        """
        初始化文件生成流程
        
        Args:
            config_manager: 配置管理器实例
            csv_processor: CSV处理器实例
        """
        self.config_manager = config_manager
        self.csv_processor = csv_processor
        self.logger = get_logger("FileGenerationFlow")
        self.output_directory = "output"
        self.history_file = "generation_history.json"
    
    def generate_macro_file(self, variables: Dict[str, Variable], 
                           model_string: str = "",
                           program_sequence: List[str] = None) -> FileGenerationResult:
        """
        生成宏文件的完整流程
        
        Args:
            variables: 变量字典
            model_string: 型号字符串
            program_sequence: 程序序列
            
        Returns:
            FileGenerationResult: 生成结果
        """
        try:
            self.logger.info(f"开始生成宏文件: {len(variables)} 个变量")
            
            # 1. 检查设备状态
            if not self._check_device_status():
                return FileGenerationResult.error("设备正在运行中，无法生成文件")
            
            # 2. 过滤需要发送的变量
            send_variables = self._filter_send_variables(variables)
            
            # 3. 验证变量值
            validation_errors = self._validate_variable_values(send_variables)
            if validation_errors:
                return FileGenerationResult.error("变量验证失败", details=validation_errors)
            
            # 4. 生成文件内容
            file_content = self._generate_file_content(send_variables)
            
            # 5. 写入文件
            file_path = self._write_to_file(file_content)
            
            # 6. 记录生成历史
            self._record_generation_history(file_path, send_variables, model_string, program_sequence)
            
            self.logger.info(f"宏文件生成成功: {file_path}")
            return FileGenerationResult.success(file_path, details={
                'variables_count': len(send_variables),
                'model_string': model_string,
                'program_sequence': program_sequence
            })
            
        except Exception as e:
            error_msg = f"文件生成失败: {str(e)}"
            self.logger.error(error_msg)
            return FileGenerationResult.error(error_msg)
    
    def _check_device_status(self) -> bool:
        """检查设备状态"""
        try:
            # 检查设备连接状态
            if hasattr(self.config_manager, 'get_device_status'):
                device_status = self.config_manager.get_device_status()
                if device_status and device_status.get('running', False):
                    self.logger.warning("设备正在运行中，无法生成文件")
                    return False
            
            # 检查NC通信状态
            if hasattr(self.config_manager, 'get_nc_communication_status'):
                nc_status = self.config_manager.get_nc_communication_status()
                if nc_status and nc_status.get('busy', False):
                    self.logger.warning("NC通信繁忙，无法生成文件")
                    return False
            
            self.logger.debug("设备状态检查通过")
            return True
            
        except Exception as e:
            self.logger.error(f"设备状态检查失败: {str(e)}")
            return False
    
    def _filter_send_variables(self, variables: Dict[str, Variable]) -> Dict[str, Variable]:
        """过滤需要发送的变量"""
        send_variables = {
            var_name: variable 
            for var_name, variable in variables.items() 
            if variable.send_flag and variable.value is not None
        }
        
        self.logger.debug(f"过滤发送变量: {len(variables)} -> {len(send_variables)}")
        return send_variables
    
    def _validate_variable_values(self, variables: Dict[str, Variable]) -> List[str]:
        """验证变量值"""
        errors = []
        
        for var_name, variable in variables.items():
            # 跳过空值验证
            if variable.value is None or variable.value == '':
                continue
                
            # 检查数值范围
            if variable.min_value is not None and variable.value < variable.min_value:
                errors.append(f"变量 {var_name} 值 {variable.value} 小于最小值 {variable.min_value}")
            
            if variable.max_value is not None and variable.value > variable.max_value:
                errors.append(f"变量 {var_name} 值 {variable.value} 大于最大值 {variable.max_value}")
            
            # 检查变量类型
            if variable.kind and not self._validate_variable_kind(variable.value, variable.kind):
                errors.append(f"变量 {var_name} 值 {variable.value} 不符合类型 {variable.kind}")
        
        if errors:
            self.logger.warning(f"变量验证发现 {len(errors)} 个错误")
        
        return errors
    
    def _validate_variable_kind(self, value: Any, kind: str) -> bool:
        """验证变量类型"""
        try:
            if kind == 'INTEGER':
                return isinstance(value, int) or (isinstance(value, float) and value.is_integer())
            elif kind == 'FLOAT':
                return isinstance(value, (int, float))
            elif kind == 'STRING':
                return isinstance(value, str)
            elif kind == 'BOOLEAN':
                return isinstance(value, bool) or value in [0, 1, '0', '1', 'true', 'false', True, False]
            else:
                return True  # 未知类型不验证
                
        except Exception as e:
            self.logger.warning(f"变量类型验证失败: {str(e)}")
            return False
    
    def _generate_file_content(self, variables: Dict[str, Variable]) -> str:
        """生成文件内容"""
        lines = []
        
        for var_name, variable in variables.items():
            # 剥离#号，生成宏变量号
            macro_number = self._strip_hash_symbol(var_name)
            
            # 格式化值
            formatted_value = self._format_variable_value(variable.value)
            
            # 生成行
            line = f"{macro_number}={formatted_value}"
            lines.append(line)
        
        # 添加文件头注释
        header_lines = self._generate_file_header()
        content_lines = header_lines + lines
        
        self.logger.debug(f"生成文件内容: {len(lines)} 行")
        return '\n'.join(content_lines)
    
    def _strip_hash_symbol(self, var_name: str) -> str:
        """剥离#号"""
        return var_name.lstrip('#')
    
    def _format_variable_value(self, value: Any) -> str:
        """格式化变量值"""
        try:
            if isinstance(value, float):
                # 根据ini.csv的DecimalPlace设置格式化小数位数
                decimal_places = self._get_decimal_places()
                return f"{value:.{decimal_places}f}"
            elif isinstance(value, bool):
                return "1" if value else "0"
            else:
                return str(value)
                
        except Exception as e:
            self.logger.warning(f"变量值格式化失败 {value}: {str(e)}")
            return str(value)
    
    def _get_decimal_places(self) -> int:
        """获取小数位数配置"""
        try:
            # 检查配置管理器是否可用
            if not self.config_manager:
                self.logger.warning("配置管理器不可用，使用默认小数位数")
                return 2
            
            # 尝试获取ini.csv配置
            ini_config = self.config_manager.get_config('ini.csv')
            if ini_config:
                for row in ini_config:
                    if row.get('DEFINE') == 'DecimalPlace':
                        decimal_places = row.get('VALUE', 2)
                        try:
                            return int(decimal_places)
                        except (ValueError, TypeError):
                            self.logger.warning(f"小数位数配置值无效: {decimal_places}")
                            return 2
            
            # 如果未找到配置，使用默认值
            self.logger.debug("未找到小数位数配置，使用默认值2")
            return 2
            
        except Exception as e:
            self.logger.warning(f"小数位数配置获取失败: {str(e)}")
            return 2  # 默认2位小数
    
    def _generate_file_header(self) -> List[str]:
        """生成文件头注释"""
        header = [
            "# =========================================",
            "# 宏文件 - 自动生成",
            f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "# =========================================",
            ""
        ]
        return header
    
    def _write_to_file(self, content: str) -> str:
        """写入文件"""
        try:
            # 确保输出目录存在
            os.makedirs(self.output_directory, exist_ok=True)
            
            # 根据配置决定文件名
            file_name = self._get_output_filename()
            file_path = os.path.join(self.output_directory, file_name)
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.debug(f"文件写入成功: {file_path}")
            return file_path
            
        except Exception as e:
            raise FileGenerationError(f"文件写入失败: {str(e)}")

    def _get_output_filename(self) -> str:
        """获取输出文件名"""
        try:
            # 检查是否使用固定文件名
            if hasattr(self.config_manager, 'get_config'):
                ini_config = self.config_manager.get_config('ini.csv')
                if ini_config:
                    for row in ini_config:
                        if row.get('DEFINE') == 'UseFixedFilename':
                            if row.get('VALUE', '0') == '1':
                                return "macro.txt"
            
            # 默认使用时间戳命名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"macro_{timestamp}.txt"
            
        except Exception as e:
            self.logger.warning(f"获取输出文件名失败，使用默认命名: {str(e)}")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"macro_{timestamp}.txt"
    
    def _record_generation_history(self, file_path: str, variables: Dict[str, Variable],
                                 model_string: str, program_sequence: List[str]) -> None:
        """记录生成历史"""
        try:
            history_file_path = os.path.join(self.output_directory, self.history_file)
            
            # 读取现有历史
            history_data = []
            if os.path.exists(history_file_path):
                with open(history_file_path, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
            
            # 添加新记录
            new_record = {
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "file_path": file_path,
                "variables_count": len(variables),
                "model_string": model_string,
                "program_sequence": program_sequence
            }
            
            history_data.append(new_record)
            
            # 限制历史记录数量（保留最近100条）
            if len(history_data) > 100:
                history_data = history_data[-100:]
            
            # 写入历史文件
            with open(history_file_path, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False)
            
            self.logger.debug("生成历史记录已保存")
            
        except Exception as e:
            self.logger.warning(f"生成历史记录失败: {str(e)}")
    
    def get_generation_history(self) -> List[GenerationHistory]:
        """获取生成历史"""
        try:
            history_file_path = os.path.join(self.output_directory, self.history_file)
            
            if not os.path.exists(history_file_path):
                return []
            
            with open(history_file_path, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
            
            # 转换为GenerationHistory对象列表
            history_objects = []
            for record in history_data:
                history_obj = GenerationHistory(
                    timestamp=record.get("timestamp", ""),
                    file_path=record.get("file_path", ""),
                    variables_count=record.get("variables_count", 0),
                    model_string=record.get("model_string", ""),
                    program_sequence=record.get("program_sequence")
                )
                history_objects.append(history_obj)
            
            return history_objects
            
        except Exception as e:
            self.logger.error(f"获取生成历史失败: {str(e)}")
            return []
    
    def cleanup_old_files(self, days_to_keep: int = 30) -> int:
        """清理旧文件"""
        try:
            if not os.path.exists(self.output_directory):
                return 0
            
            cutoff_time = datetime.now() - timedelta(days=days_to_keep)
            deleted_count = 0
            
            for file_name in os.listdir(self.output_directory):
                if file_name.startswith("macro_") and file_name.endswith(".txt"):
                    file_path = os.path.join(self.output_directory, file_name)
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    
                    if file_time < cutoff_time:
                        os.remove(file_path)
                        deleted_count += 1
                        self.logger.debug(f"删除旧文件: {file_name}")
            
            self.logger.info(f"清理完成: 删除了 {deleted_count} 个旧文件")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"文件清理失败: {str(e)}")
            return 0


class MacroGenerator:
    """宏文件生成器"""
    
    def __init__(self, config_manager, csv_processor):
        """
        初始化宏文件生成器
        
        Args:
            config_manager: 配置管理器实例
            csv_processor: CSV处理器实例
        """
        self.config_manager = config_manager
        self.csv_processor = csv_processor
        self.logger = get_logger("MacroGenerator")
        self.file_generator = FileGenerationFlow(config_manager, csv_processor)
    
    def generate_macro(self, variables: Dict[str, Variable], 
                      model_string: str = "",
                      program_sequence: List[str] = None) -> FileGenerationResult:
        """
        生成宏文件
        
        Args:
            variables: 变量字典
            model_string: 型号字符串
            program_sequence: 程序序列
            
        Returns:
            FileGenerationResult: 生成结果
        """
        try:
            self.logger.info(f"生成宏文件: {len(variables)} 个变量")
            
            # 使用FileGenerationFlow生成文件
            result = self.file_generator.generate_macro_file(
                variables, model_string, program_sequence
            )
            
            if result.success:
                self.logger.info(f"宏文件生成成功: {result.file_path}")
            else:
                self.logger.error(f"宏文件生成失败: {result.error_message}")
            
            return result
            
        except Exception as e:
            error_msg = f"宏文件生成异常: {str(e)}"
            self.logger.error(error_msg)
            return FileGenerationResult.error(error_msg)
    
    def get_generation_history(self) -> List[GenerationHistory]:
        """获取生成历史"""
        return self.file_generator.get_generation_history()
    
    def cleanup_old_files(self, days_to_keep: int = 30) -> int:
        """清理旧文件"""
        return self.file_generator.cleanup_old_files(days_to_keep)