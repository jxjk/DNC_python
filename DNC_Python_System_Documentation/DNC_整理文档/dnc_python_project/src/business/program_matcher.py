# program_matcher.py
"""
程序匹配器
负责根据型号匹配对应的加工程序
"""

import logging
import os
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from src.core.config import ConfigManager
from src.data.csv_processor import CSVProcessor
from src.utils.logger import get_logger
from src.utils.error_handler import handle_errors
from src.core.cache_manager import get_global_cache_manager
from src.core.performance_monitor import get_global_performance_monitor


@dataclass
class ProgramMatchResult:
    """程序匹配结果"""
    success: bool
    program_no: str = None
    matched_string: str = None
    match_type: str = None
    confidence: float = 0.0
    program_sequence: List[str] = None
    error_message: str = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'success': self.success,
            'program_no': self.program_no,
            'matched_string': self.matched_string,
            'match_type': self.match_type,
            'confidence': self.confidence,
            'program_sequence': self.program_sequence,
            'error_message': self.error_message
        }


@dataclass
class ModelMatchingResult:
    """型号匹配结果"""
    success: bool
    type_no: str = None
    type_definition: Dict[str, Any] = None
    program_sequence: List[str] = None
    processed_segments: List[str] = None
    error_message: str = None
    
    @classmethod
    def success(cls, type_no: str, type_definition: Dict[str, Any], 
                program_sequence: List[str], processed_segments: List[str]) -> 'ModelMatchingResult':
        """创建成功结果"""
        return cls(
            success=True, 
            type_no=type_no,
            type_definition=type_definition,
            program_sequence=program_sequence,
            processed_segments=processed_segments
        )
    
    @classmethod
    def error(cls, error_message: str) -> 'ModelMatchingResult':
        """创建错误结果"""
        return cls(success=False, error_message=error_message)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'success': self.success,
            'type_no': self.type_no,
            'type_definition': self.type_definition,
            'program_sequence': self.program_sequence,
            'processed_segments': self.processed_segments,
            'error_message': self.error_message
        }


@dataclass
class TypeDefinition:
    """型号定义"""
    no: str
    type: str
    description: str = ""
    category: str = ""


class ModelMatchingError(Exception):
    """型号匹配错误异常"""
    pass


class ProgramSequenceError(Exception):
    """程序序列错误异常"""
    pass


class ModelMatchingFlow:
    """型号匹配流程 - 按照标准流程实现型号匹配"""
    
    def __init__(self, config_manager, csv_processor):
        """
        初始化型号匹配流程
        
        Args:
            config_manager: 配置管理器实例
            csv_processor: CSV处理器实例
        """
        self.config_manager = config_manager
        self.csv_processor = csv_processor
        self.logger = get_logger("ModelMatchingFlow")
        self.cache = get_global_cache_manager()  # 添加缓存管理器
        self.performance_monitor = get_global_performance_monitor()  # 添加性能监控器
        self.type_registry = None
        self.program_registry = None
    
    @handle_errors
    def match_model(self, segments: List[str]) -> ModelMatchingResult:
        """
        型号匹配完整流程
        
        Args:
            segments: 分割后的型号片段
            
        Returns:
            ModelMatchingResult: 匹配结果
        """
        self.logger.info(f"开始型号匹配: {segments}")
        
        # 1. 加载配置注册表
        self._load_registries()
        
        # 2. 应用header规则处理
        processed_segments = self._apply_header_rules(segments)
        
        # 3. 递归匹配类型定义
        matched_type = self._recursive_match_type(processed_segments)
        
        if not matched_type:
            return ModelMatchingResult.error("未找到匹配的型号定义")
        
        # 4. 获取程序序列
        program_sequence = self._get_program_sequence(matched_type.no)
        
        # 5. 构建结果
        self.logger.info(f"型号匹配完成: {matched_type.no}")
        return ModelMatchingResult.success(
            type_no=matched_type.no,
            type_definition=matched_type,
            program_sequence=program_sequence,
            processed_segments=processed_segments
        )
    
    def _load_registries(self) -> None:
        """加载配置注册表"""
        try:
            # 检查缓存
            cache_key = "type_registry_cache"
            cached_registry = self.cache.get(cache_key)
            if cached_registry is not None:
                self.logger.debug("从缓存加载型号注册表")
                self.type_registry = cached_registry.get('type_registry', {})
                self.program_registry = cached_registry.get('program_registry', {})
                return
            
            # 加载type_define.csv
            type_define_data = self.config_manager.get_config('type_define.csv')
            if not type_define_data:
                raise ModelMatchingError("无法加载type_define.csv配置")
            
            # 构建型号注册表
            self.type_registry = {}
            for row in type_define_data:
                if 'NO' in row and 'TYPE' in row:
                    # 修改3：修复注册表加载逻辑，支持DEFINE1, DEFINE2字段
                    type_def = TypeDefinition(
                        no=row['NO'],
                        type=row['TYPE'],
                        description=row.get('DEFINE1', row.get('DESCRIPTION', '')),
                        category=row.get('DEFINE2', row.get('CATEGORY', ''))
                    )
                    self.type_registry[row['TYPE']] = type_def
            
            # 加载type_prg.csv
            type_prg_data = self.config_manager.get_config('type_prg.csv')
            if not type_prg_data:
                raise ModelMatchingError("无法加载type_prg.csv配置")
            
            # 修改4：重构程序注册表构建逻辑，收集所有prg字段
            # 构建程序注册表（使用新的程序序列获取逻辑）
            self.program_registry = {}
            for row in type_prg_data:
                if 'NO' in row:
                    no = row['NO']
                    prg_list = []
                    # 收集所有prg字段（prg1, prg2等）
                    for key, value in row.items():
                        if key.startswith('prg') and value and str(value).strip():
                            prg_list.append(str(value).strip())
                    self.program_registry[no] = prg_list
            
            # 缓存注册表，有效期30分钟
            registry_data = {
                'type_registry': self.type_registry,
                'program_registry': self.program_registry
            }
            self.cache.set(cache_key, registry_data, ttl=1800)
            
            self.logger.debug(f"注册表加载完成: {len(self.type_registry)} 个型号, {len(self.program_registry)} 个程序序列")
            
        except Exception as e:
            raise ModelMatchingError(f"注册表加载失败: {str(e)}")
    
    def _apply_header_rules(self, segments: List[str]) -> List[str]:
        """应用header.csv规则"""
        if not segments:
            return segments
        
        try:
            first_segment = segments[0]
            header_rules = self.config_manager.get_config('header.csv')
            
            if not header_rules:
                return segments
            
            for rule in header_rules:
                if rule.get('DEFINE') == first_segment:
                    rule_kind = rule.get('KIND', '')
                    
                    if rule_kind == 'del':
                        # 删除该segment
                        self.logger.debug(f"应用header删除规则: 删除 {first_segment}")
                        return segments[1:]
                    
                    elif rule_kind == 'add' and len(segments) > 1:
                        # 合并前两个segments
                        merged = f"{segments[0]}-{segments[1]}"
                        self.logger.debug(f"应用header合并规则: 合并为 {merged}")
                        return [merged] + segments[2:]
            
            return segments
            
        except Exception as e:
            self.logger.warning(f"header规则应用失败: {str(e)}")
            return segments
    
    def _recursive_match_type(self, segments: List[str]) -> Optional[TypeDefinition]:
        """递归匹配型号定义"""
        if not segments:
            return None
        
        # 从完整型号开始尝试匹配
        full_model = '-'.join(segments)
        self.logger.debug(f"开始递归匹配: {full_model}")
        
        # 从后往前逐个字符删除进行匹配
        for i in range(len(full_model), 0, -1):
            test_string = full_model[:i]
            matched_type = self._find_by_type(test_string)
            if matched_type:
                self.logger.debug(f"找到匹配型号: {test_string} -> {matched_type.no}")
                return matched_type
        
        # 如果完整型号没有匹配，尝试部分匹配
        if len(segments) > 1:
            # 尝试去掉最后一个segment
            partial_segments = segments[:-1]
            return self._recursive_match_type(partial_segments)
        
        self.logger.debug(f"未找到匹配型号: {full_model}")
        return None
    
    def _find_by_type(self, type_string: str) -> Optional[TypeDefinition]:
        """根据型号字符串查找定义"""
        return self.type_registry.get(type_string)
    
    def _get_program_sequence(self, type_no: str) -> List[str]:
        """获取程序序列"""
        try:
            # 修改1：从type_prg.csv获取程序编号
            program_numbers = []
            type_prg_data = self.config_manager.get_config('type_prg.csv')
            if type_prg_data:
                for row in type_prg_data:
                    if row.get('NO') == type_no:
                        # 收集所有prg字段（prg1, prg2等）
                        for key, value in row.items():
                            if key.startswith('prg') and value and str(value).strip():
                                program_numbers.append(str(value).strip())
                        break
            
            if not program_numbers:
                raise ProgramSequenceError(f"未找到型号 {type_no} 对应的程序序列")
            
            # 将程序编号映射为程序名称
            valid_programs = []
            for program_no in program_numbers:
                program_name = self._map_program_number_to_name(program_no)
                if program_name:
                    # 验证程序配置是否存在
                    program_config = self._load_program_config(program_name)
                    if program_config:
                        valid_programs.append(program_name)
                    else:
                        self.logger.warning(f"程序配置不存在: {program_name}")
                else:
                    self.logger.warning(f"程序编号 {program_no} 无法映射到程序名称")
            
            if not valid_programs:
                raise ProgramSequenceError(f"型号 {type_no} 的程序序列全部无效")
            
            self.logger.debug(f"获取程序序列: {type_no} -> {valid_programs}")
            return valid_programs
            
        except Exception as e:
            raise ProgramSequenceError(f"程序序列获取失败: {str(e)}")
    
    def _map_program_number_to_name(self, program_no: str) -> Optional[str]:
        """修改2：将程序编号映射为程序名称"""
        try:
            # 从prg.csv中查找程序名称
            prg_config = self.config_manager.get_config('prg.csv')
            if prg_config:
                for row in prg_config:
                    if row.get('PRGNO') == program_no:
                        return row.get('PRGNAME')
            
            # 如果找不到，返回默认名称（如 "prg" + 编号）
            return f"prg{program_no}"
            
        except Exception as e:
            self.logger.warning(f"程序编号映射失败 {program_no}: {str(e)}")
            return None
    
    def _load_program_config(self, program_name: str) -> Optional[Dict[str, Any]]:
        """加载程序配置"""
        try:
            # 首先尝试从prg.csv加载
            prg_config = self.config_manager.get_config('prg.csv')
            if prg_config:
                program_row = next((row for row in prg_config if row.get('PRG') == program_name), None)
                if program_row:
                    return program_row
            
            # 然后尝试从prg文件夹加载
            prg_dir_configs = self._load_prg_directory_configs()
            if program_name in prg_dir_configs:
                return prg_dir_configs[program_name]
            
            return None
            
        except Exception as e:
            self.logger.warning(f"程序配置加载失败 {program_name}: {str(e)}")
            return None
    
    def _load_prg_directory_configs(self) -> Dict[str, Dict[str, Any]]:
        """加载prg文件夹下的配置"""
        prg_configs = {}
        
        try:
            # 获取prg文件夹路径
            config_dir = self.config_manager.get_config_directory()
            prg_dir = os.path.join(config_dir, 'prg')
            
            if os.path.exists(prg_dir):
                for file in os.listdir(prg_dir):
                    if file.endswith('.csv'):
                        file_path = os.path.join(prg_dir, file)
                        config_data = self.csv_processor.load_csv(file_path)
                        if config_data:
                            # 假设文件名就是程序名（去掉.csv后缀）
                            program_name = file[:-4]
                            prg_configs[program_name] = config_data
        except Exception as e:
            self.logger.warning(f"PRG目录配置加载异常: {e}")
        
        return prg_configs


class ProgramMatcher:
    """程序匹配器"""
    
    def __init__(self, config_manager, csv_processor):
        """
        初始化程序匹配器
        
        Args:
            config_manager: 配置管理器实例
            csv_processor: CSV处理器实例
        """
        self.config_manager = config_manager
        self.csv_processor = csv_processor
        self.logger = get_logger("ProgramMatcher")
        self.model_matcher = ModelMatchingFlow(config_manager, csv_processor)
        self.performance_monitor = get_global_performance_monitor()  # 添加性能监控器
        self.cache = get_global_cache_manager()  # 添加缓存管理器
    
    @handle_errors
    def match_program(self, model_string: str) -> ProgramMatchResult:
        """
        匹配程序
        
        Args:
            model_string: 型号字符串
            
        Returns:
            ProgramMatchResult: 匹配结果
        """
        start_time = time.time()
        self.logger.info(f"开始程序匹配: {model_string}")
        
        try:
            # 首先分割型号字符串
            segments = self._split_model_string(model_string)
            
            # 使用ModelMatchingFlow进行型号匹配
            matching_result = self.model_matcher.match_model(segments)
            
            if not matching_result.success:
                return ProgramMatchResult(
                    success=False,
                    error_message=matching_result.error_message
                )
            
            # 构建程序匹配结果
            result = ProgramMatchResult(
                success=True,
                program_no=matching_result.type_no,
                matched_string=model_string,
                match_type="TYPE_DEFINE",
                confidence=1.0,
                program_sequence=matching_result.program_sequence
            )
            
            # 记录性能指标
            execution_time = time.time() - start_time
            self.performance_monitor.record_metric(
                "program_matching_time",
                execution_time,
                tags={"model": model_string, "success": True}
            )
            
            return result
            
        except Exception as e:
            # 记录错误性能指标
            execution_time = time.time() - start_time
            self.performance_monitor.record_metric(
                "program_matching_time",
                execution_time,
                tags={"model": model_string, "success": False, "error": str(e)}
            )
            
            error_msg = f"程序匹配失败: {str(e)}"
            self.logger.error(error_msg)
            return ProgramMatchResult(
                success=False,
                error_message=error_msg
            )
    
    def _split_model_string(self, model_string: str) -> List[str]:
        """分割型号字符串"""
        if not model_string:
            return []
        
        # 根据常见的分隔符进行分割
        separators = ['-', '_', '/', '\\']
        
        for separator in separators:
            if separator in model_string:
                return model_string.split(separator)
        
        return [model_string]