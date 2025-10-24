"""
CSV处理器
负责CSV文件的读取和写入操作
"""

import csv
import logging
from typing import List, Optional, Dict, Any


class CSVProcessor:
    """CSV处理器类"""
    
    def __init__(self):
        """初始化CSV处理器"""
        self.logger = logging.getLogger(__name__)
    
    def read_csv(self, file_path: str, encoding: str = 'utf-8') -> List[List[str]]:
        """
        读取CSV文件
        
        Args:
            file_path: CSV文件路径
            encoding: 文件编码
            
        Returns:
            List[List[str]]: CSV数据，每行作为一个字符串列表
        """
        try:
            data = []
            with open(file_path, 'r', encoding=encoding, newline='') as file:
                reader = csv.reader(file)
                for row in reader:
                    data.append(row)
            
            self.logger.info(f"CSV文件读取成功: {file_path}, 共{len(data)}行")
            return data
            
        except FileNotFoundError:
            self.logger.warning(f"CSV文件不存在: {file_path}")
            return []
        except Exception as e:
            self.logger.error(f"CSV文件读取失败: {file_path}, 错误: {e}")
            return []
    
    def write_csv(self, file_path: str, data: List[List[str]], encoding: str = 'utf-8') -> bool:
        """
        写入CSV文件
        
        Args:
            file_path: CSV文件路径
            data: 要写入的数据
            encoding: 文件编码
            
        Returns:
            bool: 写入是否成功
        """
        try:
            with open(file_path, 'w', encoding=encoding, newline='') as file:
                writer = csv.writer(file)
                writer.writerows(data)
            
            self.logger.info(f"CSV文件写入成功: {file_path}, 共{len(data)}行")
            return True
            
        except Exception as e:
            self.logger.error(f"CSV文件写入失败: {file_path}, 错误: {e}")
            return False
    
    def read_csv_as_dict(self, file_path: str, encoding: str = 'utf-8') -> List[Dict[str, str]]:
        """
        读取CSV文件为字典列表
        
        Args:
            file_path: CSV文件路径
            encoding: 文件编码
            
        Returns:
            List[Dict[str, str]]: CSV数据，每行作为一个字典
        """
        try:
            data = []
            with open(file_path, 'r', encoding=encoding, newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    data.append(dict(row))
            
            self.logger.info(f"CSV文件读取为字典成功: {file_path}, 共{len(data)}行")
            return data
            
        except FileNotFoundError:
            self.logger.warning(f"CSV文件不存在: {file_path}")
            return []
        except Exception as e:
            self.logger.error(f"CSV文件读取为字典失败: {file_path}, 错误: {e}")
            return []
    
    def write_dict_to_csv(self, file_path: str, data: List[Dict[str, str]], 
                         fieldnames: Optional[List[str]] = None, encoding: str = 'utf-8') -> bool:
        """
        将字典列表写入CSV文件
        
        Args:
            file_path: CSV文件路径
            data: 要写入的数据
            fieldnames: 字段名列表
            encoding: 文件编码
            
        Returns:
            bool: 写入是否成功
        """
        try:
            if not fieldnames and data:
                fieldnames = list(data[0].keys())
            
            with open(file_path, 'w', encoding=encoding, newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            self.logger.info(f"字典数据写入CSV成功: {file_path}, 共{len(data)}行")
            return True
            
        except Exception as e:
            self.logger.error(f"字典数据写入CSV失败: {file_path}, 错误: {e}")
            return False
    
    def get_csv_info(self, file_path: str) -> Dict[str, Any]:
        """
        获取CSV文件信息
        
        Args:
            file_path: CSV文件路径
            
        Returns:
            Dict[str, Any]: CSV文件信息
        """
        try:
            data = self.read_csv(file_path)
            if not data:
                return {
                    "file_path": file_path,
                    "row_count": 0,
                    "column_count": 0,
                    "headers": [],
                    "status": "empty_or_not_found"
                }
            
            return {
                "file_path": file_path,
                "row_count": len(data),
                "column_count": len(data[0]) if data else 0,
                "headers": data[0] if data else [],
                "status": "success"
            }
            
        except Exception as e:
            self.logger.error(f"获取CSV文件信息失败: {file_path}, 错误: {e}")
            return {
                "file_path": file_path,
                "row_count": 0,
                "column_count": 0,
                "headers": [],
                "status": "error",
                "error_message": str(e)
            }
