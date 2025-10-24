"""
文件管理器模块
负责文件操作和资源管理
"""

import os
import logging
import shutil
from typing import Optional, List, Dict, Any
from pathlib import Path


class FileManager:
    """文件管理器类"""
    
    def __init__(self):
        """初始化文件管理器"""
        self.logger = logging.getLogger(__name__)
        self.base_path = Path.cwd()
        
    def set_base_path(self, path: str) -> bool:
        """
        设置基础路径
        
        Args:
            path: 基础路径
            
        Returns:
            bool: 设置是否成功
        """
        try:
            self.base_path = Path(path)
            if not self.base_path.exists():
                self.base_path.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"基础路径设置为: {self.base_path}")
            return True
        except Exception as e:
            self.logger.error(f"设置基础路径失败: {e}")
            return False
    
    def ensure_directory(self, directory: str) -> bool:
        """
        确保目录存在，如果不存在则创建
        
        Args:
            directory: 目录路径
            
        Returns:
            bool: 操作是否成功
        """
        try:
            dir_path = self.base_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            self.logger.error(f"创建目录失败: {directory}, 错误: {e}")
            return False
    
    def file_exists(self, file_path: str) -> bool:
        """
        检查文件是否存在
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 文件是否存在
        """
        try:
            full_path = self.base_path / file_path
            return full_path.exists() and full_path.is_file()
        except Exception as e:
            self.logger.error(f"检查文件存在性失败: {file_path}, 错误: {e}")
            return False
    
    def directory_exists(self, directory: str) -> bool:
        """
        检查目录是否存在
        
        Args:
            directory: 目录路径
            
        Returns:
            bool: 目录是否存在
        """
        try:
            full_path = self.base_path / directory
            return full_path.exists() and full_path.is_dir()
        except Exception as e:
            self.logger.error(f"检查目录存在性失败: {directory}, 错误: {e}")
            return False
    
    def read_file(self, file_path: str, encoding: str = 'utf-8') -> Optional[str]:
        """
        读取文件内容
        
        Args:
            file_path: 文件路径
            encoding: 文件编码
            
        Returns:
            Optional[str]: 文件内容，读取失败返回None
        """
        try:
            full_path = self.base_path / file_path
            with open(full_path, 'r', encoding=encoding) as f:
                content = f.read()
            self.logger.debug(f"文件读取成功: {file_path}")
            return content
        except Exception as e:
            self.logger.error(f"读取文件失败: {file_path}, 错误: {e}")
            return None
    
    def write_file(self, file_path: str, content: str, encoding: str = 'utf-8') -> bool:
        """
        写入文件内容
        
        Args:
            file_path: 文件路径
            content: 文件内容
            encoding: 文件编码
            
        Returns:
            bool: 写入是否成功
        """
        try:
            full_path = self.base_path / file_path
            # 确保目录存在
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding=encoding) as f:
                f.write(content)
            self.logger.debug(f"文件写入成功: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"写入文件失败: {file_path}, 错误: {e}")
            return False
    
    def copy_file(self, source_path: str, destination_path: str) -> bool:
        """
        复制文件
        
        Args:
            source_path: 源文件路径
            destination_path: 目标文件路径
            
        Returns:
            bool: 复制是否成功
        """
        try:
            source_full = self.base_path / source_path
            dest_full = self.base_path / destination_path
            
            # 确保目标目录存在
            dest_full.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(source_full, dest_full)
            self.logger.debug(f"文件复制成功: {source_path} -> {destination_path}")
            return True
        except Exception as e:
            self.logger.error(f"复制文件失败: {source_path} -> {destination_path}, 错误: {e}")
            return False
    
    def delete_file(self, file_path: str) -> bool:
        """
        删除文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 删除是否成功
        """
        try:
            full_path = self.base_path / file_path
            if full_path.exists() and full_path.is_file():
                full_path.unlink()
                self.logger.debug(f"文件删除成功: {file_path}")
                return True
            else:
                self.logger.warning(f"文件不存在: {file_path}")
                return False
        except Exception as e:
            self.logger.error(f"删除文件失败: {file_path}, 错误: {e}")
            return False
    
    def list_files(self, directory: str, pattern: str = "*") -> List[str]:
        """
        列出目录中的文件
        
        Args:
            directory: 目录路径
            pattern: 文件匹配模式
            
        Returns:
            List[str]: 文件路径列表
        """
        try:
            dir_path = self.base_path / directory
            if not dir_path.exists():
                return []
            
            files = []
            for file_path in dir_path.glob(pattern):
                if file_path.is_file():
                    # 返回相对于基础路径的相对路径
                    rel_path = file_path.relative_to(self.base_path)
                    files.append(str(rel_path))
            
            return files
        except Exception as e:
            self.logger.error(f"列出文件失败: {directory}, 错误: {e}")
            return []
    
    def get_file_size(self, file_path: str) -> Optional[int]:
        """
        获取文件大小
        
        Args:
            file_path: 文件路径
            
        Returns:
            Optional[int]: 文件大小（字节），获取失败返回None
        """
        try:
            full_path = self.base_path / file_path
            if full_path.exists() and full_path.is_file():
                return full_path.stat().st_size
            else:
                return None
        except Exception as e:
            self.logger.error(f"获取文件大小失败: {file_path}, 错误: {e}")
            return None
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        获取文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            Optional[Dict[str, Any]]: 文件信息字典，获取失败返回None
        """
        try:
            full_path = self.base_path / file_path
            if not full_path.exists() or not full_path.is_file():
                return None
            
            stat_info = full_path.stat()
            return {
                'path': str(full_path),
                'size': stat_info.st_size,
                'created_time': stat_info.st_ctime,
                'modified_time': stat_info.st_mtime,
                'is_file': True,
                'is_directory': False
            }
        except Exception as e:
            self.logger.error(f"获取文件信息失败: {file_path}, 错误: {e}")
            return None
    
    def create_backup(self, file_path: str, backup_suffix: str = ".bak") -> bool:
        """
        创建文件备份
        
        Args:
            file_path: 文件路径
            backup_suffix: 备份文件后缀
            
        Returns:
            bool: 备份是否成功
        """
        try:
            if not self.file_exists(file_path):
                self.logger.warning(f"无法备份不存在的文件: {file_path}")
                return False
            
            backup_path = file_path + backup_suffix
            return self.copy_file(file_path, backup_path)
        except Exception as e:
            self.logger.error(f"创建文件备份失败: {file_path}, 错误: {e}")
            return False
    
    def cleanup_old_backups(self, directory: str, pattern: str = "*.bak", keep_count: int = 5) -> bool:
        """
        清理旧的备份文件
        
        Args:
            directory: 目录路径
            pattern: 备份文件模式
            keep_count: 保留的备份数量
            
        Returns:
            bool: 清理是否成功
        """
        try:
            backup_files = self.list_files(directory, pattern)
            if len(backup_files) <= keep_count:
                return True
            
            # 按修改时间排序，删除最旧的备份
            file_info_list = []
            for file_path in backup_files:
                info = self.get_file_info(file_path)
                if info:
                    file_info_list.append((file_path, info['modified_time']))
            
            # 按修改时间排序（从旧到新）
            file_info_list.sort(key=lambda x: x[1])
            
            # 删除超出保留数量的旧备份
            files_to_delete = file_info_list[:len(file_info_list) - keep_count]
            success = True
            for file_path, _ in files_to_delete:
                if not self.delete_file(file_path):
                    success = False
            
            return success
        except Exception as e:
            self.logger.error(f"清理备份文件失败: {directory}, 错误: {e}")
            return False
