"""
动态配置加载器
支持多环境配置和热重载机制
"""

import os
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging

from src.utils.logger import get_logger


class EnvironmentType(Enum):
    """环境类型枚举"""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"
    DEFAULT = "default"


@dataclass
class ConfigLoadResult:
    """配置加载结果"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    source: Optional[str] = None
    timestamp: float = 0.0
    
    @property
    def is_valid(self) -> bool:
        """检查配置是否有效"""
        return self.success and self.data is not None


@dataclass
class ConfigFileInfo:
    """配置文件信息"""
    path: Path
    last_modified: float
    size: int
    checksum: Optional[str] = None


class DynamicConfigLoader:
    """
    动态配置加载器
    支持多环境配置、配置回退和热重载
    """
    
    def __init__(self, base_config_path: str):
        """
        初始化动态配置加载器
        
        Args:
            base_config_path: 基础配置路径
        """
        self.base_path = Path(base_config_path)
        self.logger = get_logger("DynamicConfigLoader")
        self.environment = self._detect_environment()
        self.config_cache: Dict[str, ConfigLoadResult] = {}
        self.file_watchers: Dict[str, ConfigFileInfo] = {}
        self.fallback_order = self._get_fallback_order()
        
        self.logger.info(f"初始化动态配置加载器，环境: {self.environment.value}")
    
    def _detect_environment(self) -> EnvironmentType:
        """
        检测运行环境
        
        Returns:
            EnvironmentType: 检测到的环境类型
        """
        # 1. 检查环境变量
        env_var = os.getenv('DNC_ENV')
        if env_var:
            try:
                return EnvironmentType(env_var.lower())
            except ValueError:
                self.logger.warning(f"未知环境变量值: {env_var}，使用默认环境")
        
        # 2. 检查配置文件目录
        for env_type in [EnvironmentType.DEVELOPMENT, EnvironmentType.PRODUCTION, EnvironmentType.TESTING]:
            env_path = self.base_path / env_type.value
            if env_path.exists() and env_path.is_dir():
                return env_type
        
        # 3. 默认环境
        return EnvironmentType.DEFAULT
    
    def _get_fallback_order(self) -> List[EnvironmentType]:
        """
        获取配置回退顺序
        
        Returns:
            List[EnvironmentType]: 回退顺序列表
        """
        if self.environment == EnvironmentType.DEVELOPMENT:
            return [EnvironmentType.DEVELOPMENT, EnvironmentType.DEFAULT]
        elif self.environment == EnvironmentType.PRODUCTION:
            return [EnvironmentType.PRODUCTION, EnvironmentType.DEFAULT]
        elif self.environment == EnvironmentType.TESTING:
            return [EnvironmentType.TESTING, EnvironmentType.DEFAULT]
        else:
            return [EnvironmentType.DEFAULT]
    
    def get_config_path(self, filename: str, program_no: Optional[int] = None) -> Path:
        """
        获取配置文件路径（支持回退机制）
        
        Args:
            filename: 配置文件名
            program_no: 程序编号（可选）
            
        Returns:
            Path: 配置文件路径
        """
        # 按回退顺序查找文件
        for env_type in self.fallback_order:
            env_path = self.base_path / env_type.value
            candidate_path = env_path / filename
            
            # 如果指定了程序编号，检查prg目录
            if program_no is not None:
                prg_dir = self._get_prg_directory(program_no, env_type)
                if prg_dir:
                    prg_path = env_path / prg_dir / filename
                    if prg_path.exists():
                        self.logger.debug(f"找到程序特定配置: {prg_path}")
                        return prg_path
            
            if candidate_path.exists():
                self.logger.debug(f"找到环境配置: {candidate_path}")
                return candidate_path
        
        # 如果都找不到，返回默认环境的路径
        default_path = self.base_path / EnvironmentType.DEFAULT.value / filename
        self.logger.debug(f"使用默认配置路径: {default_path}")
        return default_path
    
    def _get_prg_directory(self, program_no: int, env_type: EnvironmentType) -> Optional[str]:
        """
        根据程序编号获取对应的prg目录
        
        Args:
            program_no: 程序编号
            env_type: 环境类型
            
        Returns:
            Optional[str]: prg目录名称，如果找不到返回None
        """
        try:
            prg_csv_path = self.base_path / env_type.value / "prg.csv"
            if not prg_csv_path.exists():
                return None
            
            import csv
            with open(prg_csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if 'PRGNO' in row and int(row['PRGNO']) == program_no:
                        return row.get('PRGNAME')
            
            return None
            
        except Exception as e:
            self.logger.warning(f"获取prg目录映射失败: {e}")
            return None
    
    def load_config_with_fallback(self, filename: str, program_no: Optional[int] = None) -> ConfigLoadResult:
        """
        加载配置（支持回退机制）
        
        Args:
            filename: 配置文件名
            program_no: 程序编号（可选）
            
        Returns:
            ConfigLoadResult: 配置加载结果
        """
        cache_key = f"{filename}_{program_no}" if program_no else filename
        
        # 检查缓存
        if cache_key in self.config_cache:
            cached_result = self.config_cache[cache_key]
            if self._is_cache_valid(cached_result, filename, program_no):
                self.logger.debug(f"使用缓存配置: {filename}")
                return cached_result
        
        # 按回退顺序加载配置
        for env_type in self.fallback_order:
            env_path = self.base_path / env_type.value
            
            # 尝试加载程序特定配置
            if program_no is not None:
                prg_dir = self._get_prg_directory(program_no, env_type)
                if prg_dir:
                    prg_path = env_path / prg_dir / filename
                    if prg_path.exists():
                        result = self._load_single_config(prg_path, f"{env_type.value}/{prg_dir}")
                        if result.success:
                            self.config_cache[cache_key] = result
                            return result
            
            # 尝试加载环境配置
            config_path = env_path / filename
            if config_path.exists():
                result = self._load_single_config(config_path, env_type.value)
                if result.success:
                    self.config_cache[cache_key] = result
                    return result
        
        # 所有回退都失败
        error_msg = f"无法加载配置文件: {filename}"
        self.logger.error(error_msg)
        result = ConfigLoadResult(success=False, error=error_msg)
        self.config_cache[cache_key] = result
        return result
    
    def _load_single_config(self, file_path: Path, source: str) -> ConfigLoadResult:
        """
        加载单个配置文件
        
        Args:
            file_path: 文件路径
            source: 配置来源
            
        Returns:
            ConfigLoadResult: 加载结果
        """
        try:
            if not file_path.exists():
                return ConfigLoadResult(success=False, error=f"文件不存在: {file_path}", source=source)
            
            # 根据文件类型选择加载方式
            if file_path.suffix.lower() == '.csv':
                data = self._load_csv_file(file_path)
            elif file_path.suffix.lower() in ['.json', '.ini', '.conf']:
                data = self._load_structured_file(file_path)
            else:
                data = self._load_text_file(file_path)
            
            if data is not None:
                # 记录文件信息用于监控
                self._record_file_info(file_path)
                return ConfigLoadResult(
                    success=True, 
                    data=data, 
                    source=source,
                    timestamp=time.time()
                )
            else:
                return ConfigLoadResult(success=False, error=f"文件内容为空: {file_path}", source=source)
                
        except Exception as e:
            error_msg = f"配置文件加载失败 {file_path}: {e}"
            self.logger.error(error_msg)
            return ConfigLoadResult(success=False, error=error_msg, source=source)
    
    def _load_csv_file(self, file_path: Path) -> List[Dict[str, str]]:
        """加载CSV文件"""
        try:
            import csv
            data = []
            
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    data.append(dict(row))
            
            self.logger.debug(f"加载CSV文件: {file_path}, 共{len(data)}行")
            return data
            
        except Exception as e:
            self.logger.error(f"CSV文件加载失败 {file_path}: {e}")
            return []
    
    def _load_structured_file(self, file_path: Path) -> Dict[str, Any]:
        """加载结构化文件（JSON/INI等）"""
        try:
            if file_path.suffix.lower() == '.json':
                import json
                with open(file_path, 'r', encoding='utf-8') as file:
                    return json.load(file)
            else:
                # 对于其他格式，暂时返回空字典
                self.logger.warning(f"不支持的文件格式: {file_path.suffix}")
                return {}
                
        except Exception as e:
            self.logger.error(f"结构化文件加载失败 {file_path}: {e}")
            return {}
    
    def _load_text_file(self, file_path: Path) -> str:
        """加载文本文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            self.logger.error(f"文本文件加载失败 {file_path}: {e}")
            return ""
    
    def _record_file_info(self, file_path: Path) -> None:
        """记录文件信息用于监控"""
        try:
            stat = file_path.stat()
            self.file_watchers[str(file_path)] = ConfigFileInfo(
                path=file_path,
                last_modified=stat.st_mtime,
                size=stat.st_size
            )
        except Exception as e:
            self.logger.warning(f"记录文件信息失败 {file_path}: {e}")
    
    def _is_cache_valid(self, cached_result: ConfigLoadResult, filename: str, program_no: Optional[int] = None) -> bool:
        """
        检查缓存是否有效
        
        Args:
            cached_result: 缓存结果
            filename: 配置文件名
            program_no: 程序编号
            
        Returns:
            bool: 缓存是否有效
        """
        # 检查缓存时间（5分钟有效期）
        if time.time() - cached_result.timestamp > 300:
            return False
        
        # 检查文件是否被修改
        config_path = self.get_config_path(filename, program_no)
        if config_path.exists():
            try:
                current_mtime = config_path.stat().st_mtime
                cached_mtime = self.file_watchers.get(str(config_path), ConfigFileInfo(config_path, 0, 0)).last_modified
                return current_mtime <= cached_mtime
            except Exception:
                return False
        
        return True
    
    def reload_config(self, filename: str, program_no: Optional[int] = None) -> ConfigLoadResult:
        """
        重新加载配置
        
        Args:
            filename: 配置文件名
            program_no: 程序编号（可选）
            
        Returns:
            ConfigLoadResult: 重新加载结果
        """
        cache_key = f"{filename}_{program_no}" if program_no else filename
        
        # 清除缓存
        if cache_key in self.config_cache:
            del self.config_cache[cache_key]
        
        # 重新加载
        return self.load_config_with_fallback(filename, program_no)
    
    def clear_cache(self) -> None:
        """清空配置缓存"""
        self.config_cache.clear()
        self.logger.info("配置缓存已清空")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        total = len(self.config_cache)
        valid = sum(1 for result in self.config_cache.values() if result.success)
        invalid = total - valid
        
        return {
            'total_configs': total,
            'valid_configs': valid,
            'invalid_configs': invalid,
            'environment': self.environment.value,
            'fallback_order': [env.value for env in self.fallback_order]
        }
    
    def set_environment(self, environment: EnvironmentType) -> None:
        """
        设置环境类型
        
        Args:
            environment: 环境类型
        """
        if self.environment != environment:
            self.environment = environment
            self.fallback_order = self._get_fallback_order()
            self.clear_cache()
            self.logger.info(f"环境已切换至: {environment.value}")
    
    def get_environment_info(self) -> Dict[str, Any]:
        """获取环境信息"""
        return {
            'current_environment': self.environment.value,
            'fallback_order': [env.value for env in self.fallback_order],
            'base_path': str(self.base_path),
            'cache_size': len(self.config_cache)
        }


# 全局配置加载器实例
_global_config_loader: Optional[DynamicConfigLoader] = None


def get_global_config_loader(base_config_path: str = "config/") -> DynamicConfigLoader:
    """
    获取全局配置加载器实例
    
    Args:
        base_config_path: 基础配置路径
        
    Returns:
        DynamicConfigLoader: 全局配置加载器实例
    """
    global _global_config_loader
    if _global_config_loader is None:
        _global_config_loader = DynamicConfigLoader(base_config_path)
    return _global_config_loader


def set_global_environment(environment: EnvironmentType) -> None:
    """
    设置全局环境
    
    Args:
        environment: 环境类型
    """
    global _global_config_loader
    if _global_config_loader:
        _global_config_loader.set_environment(environment)
    else:
        raise RuntimeError("全局配置加载器未初始化")
