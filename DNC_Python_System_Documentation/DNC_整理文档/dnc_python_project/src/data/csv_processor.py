# src/data/csv_processor.py
"""
CSV处理器
负责CSV文件的读取和写入操作
"""

import csv
import logging
import re
import ast
from typing import List, Optional, Dict, Any
from pathlib import Path
from ..core.config import ConfigManager


class CSVProcessor:
    """增强的CSV处理器类"""
    
    def __init__(self, config_manager: ConfigManager = None):
        """
        初始化CSV处理器
        
        Args:
            config_manager: 配置管理器实例
        """
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager
        
        # 配置数据缓存
        self.define_data = {}          # 参数定义数据
        self.relation_data = {}        # 关系定义数据
        self.calc_data = {}            # 计算公式数据
        self.chngvalue_data = {}       # 变化值数据
        self.type_relation_data = {}   # 型号关系数据
        self.type_chngvl_data = {}     # 型号变化值数据
        self.data_cache = {}           # 通用数据缓存
    
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
                # 智能注释行过滤：只过滤真正的注释行
                lines = file.readlines()
                reader_lines = []
                
                for line in lines:
                    stripped_line = line.strip()
                    # 真正的注释行：以#开头且后面跟着非数字字符（如# ini.csv）
                    # 数据行：以#开头但后面跟着数字（如#1,load,0,0,0,,,）
                    if stripped_line.startswith('#') and len(stripped_line) > 1:
                        # 检查#后面的第一个字符是否为数字
                        first_char_after_hash = stripped_line[1]
                        if first_char_after_hash.isdigit():
                            # 这是数据行（如#1,load,0,0,0,,,），保留
                            reader_lines.append(line)
                        else:
                            # 这是真正的注释行（如# ini.csv），跳过
                            continue
                    else:
                        # 不以#开头的行，保留
                        reader_lines.append(line)
                
                # 使用csv.DictReader读取过滤后的行
                if reader_lines:
                    reader = csv.DictReader(reader_lines)
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
            
    def read_config_csv(self, filename: str, program_no: int = None, encoding: str = 'utf-8') -> List[List[str]]:
        """
        读取配置CSV文件（支持动态路径查找）
        
        Args:
            filename: CSV文件名
            program_no: 程序编号（可选）
            encoding: 文件编码
            
        Returns:
            List[List[str]]: CSV数据，每行作为一个字符串列表
        """
        if not self.config_manager:
            self.logger.error("配置管理器未设置，无法使用动态路径查找")
            return []
        
        try:
            file_path = self.config_manager.get_csv_config_path(filename, program_no)
            return self.read_csv(str(file_path), encoding)
        except Exception as e:
            self.logger.error(f"读取配置CSV文件失败: {filename}, 程序编号: {program_no}, 错误: {e}")
            return []
    
    def read_config_csv_as_dict(self, filename: str, program_no: int = None, encoding: str = 'utf-8') -> List[Dict[str, str]]:
        """
        读取配置CSV文件为字典列表（支持动态路径查找）
        
        Args:
            filename: CSV文件名
            program_no: 程序编号（可选）
            encoding: 文件编码
            
        Returns:
            List[Dict[str, str]]: CSV数据，每行作为一个字典
        """
        if not self.config_manager:
            self.logger.error("配置管理器未设置，无法使用动态路径查找")
            return []
        
        try:
            file_path = self.config_manager.get_csv_config_path(filename, program_no)
            return self.read_csv_as_dict(str(file_path), encoding)
        except Exception as e:
            self.logger.error(f"读取配置CSV文件为字典失败: {filename}, 程序编号: {program_no}, 错误: {e}")
            return []

    def load_csv(self, file_path: str, encoding: str = 'utf-8') -> List[Dict[str, str]]:
        """
        加载CSV文件（兼容旧接口）
        
        Args:
            file_path: CSV文件路径
            encoding: 文件编码
            
        Returns:
            List[Dict[str, str]]: CSV数据，每行作为一个字典
        """
        return self.read_csv_as_dict(file_path, encoding)
    
    def load_define_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """
        加载define.csv参数定义文件
        
        Args:
            file_path: define.csv文件路径
            
        Returns:
            List[Dict[str, Any]]: 参数定义数据
        """
        try:
            data = self.read_csv_as_dict(file_path)
            validated_data = self._validate_define_data(data)
            self.define_data = validated_data
            self.data_cache['define'] = validated_data
            self.logger.info(f"define.csv加载成功: {file_path}, 共{len(validated_data)}条记录")
            return validated_data
        except Exception as e:
            self.logger.error(f"加载define.csv失败: {file_path}, 错误: {e}")
            raise
    
    def load_relation_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """
        加载relation.csv关系定义文件
        
        Args:
            file_path: relation.csv文件路径
            
        Returns:
            List[Dict[str, Any]]: 关系定义数据
        """
        try:
            data = self.read_csv_as_dict(file_path)
            validated_data = self._validate_relation_data(data)
            self.relation_data = validated_data
            self.data_cache['relation'] = validated_data
            self.logger.info(f"relation.csv加载成功: {file_path}, 共{len(validated_data)}条记录")
            return validated_data
        except Exception as e:
            self.logger.error(f"加载relation.csv失败: {file_path}, 错误: {e}")
            raise
    
    def load_calc_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """
        加载calc.csv计算公式文件
        
        Args:
            file_path: calc.csv文件路径
            
        Returns:
            List[Dict[str, Any]]: 计算公式数据
        """
        try:
            data = self.read_csv_as_dict(file_path)
            validated_data = self._validate_calc_data(data)
            self.calc_data = validated_data
            self.data_cache['calc'] = validated_data
            self.logger.info(f"calc.csv加载成功: {file_path}, 共{len(validated_data)}条记录")
            return validated_data
        except Exception as e:
            self.logger.error(f"加载calc.csv失败: {file_path}, 错误: {e}")
            raise
    
    def load_chngvalue_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """
        加载chngValue.csv变化值定义文件
        
        Args:
            file_path: chngValue.csv文件路径
            
        Returns:
            List[Dict[str, Any]]: 变化值定义数据
        """
        try:
            data = self.read_csv_as_dict(file_path)
            validated_data = self._validate_chngvalue_data(data)
            self.chngvalue_data = validated_data
            self.data_cache['chngvalue'] = validated_data
            self.logger.info(f"chngValue.csv加载成功: {file_path}, 共{len(validated_data)}条记录")
            return validated_data
        except Exception as e:
            self.logger.error(f"加载chngValue.csv失败: {file_path}, 错误: {e}")
            raise
    
    def load_type_relation_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """
        加载type_relation.csv型号关系定义文件
        
        Args:
            file_path: type_relation.csv文件路径
            
        Returns:
            List[Dict[str, Any]]: 型号关系定义数据
        """
        try:
            data = self.read_csv_as_dict(file_path)
            validated_data = self._validate_type_relation_data(data)
            self.type_relation_data = validated_data
            self.data_cache['type_relation'] = validated_data
            self.logger.info(f"type_relation.csv加载成功: {file_path}, 共{len(validated_data)}条记录")
            return validated_data
        except Exception as e:
            self.logger.error(f"加载type_relation.csv失败: {file_path}, 错误: {e}")
            raise
    
    def load_type_chngvl_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """
        加载type_chngvl.csv型号变化值定义文件
        
        Args:
            file_path: type_chngvl.csv文件路径
            
        Returns:
            List[Dict[str, Any]]: 型号变化值定义数据
        """
        try:
            data = self.read_csv_as_dict(file_path)
            validated_data = self._validate_type_chngvl_data(data)
            self.type_chngvl_data = validated_data
            self.data_cache['type_chngvl'] = validated_data
            self.logger.info(f"type_chngvl.csv加载成功: {file_path}, 共{len(validated_data)}条记录")
            return validated_data
        except Exception as e:
            self.logger.error(f"加载type_chngvl.csv失败: {file_path}, 错误: {e}")
            raise
    
    def _validate_define_data(self, data: List[Dict]) -> List[Dict]:
        """
        验证参数定义数据
        
        Args:
            data: 原始数据
            
        Returns:
            List[Dict]: 验证后的数据
        """
        required_fields = ['NO', 'DEFINE']
        validated_data = []
        
        for row in data:
            # 检查必需字段
            if not all(field in row and row[field] for field in required_fields):
                self.logger.warning(f"跳过无效的参数定义行: {row}")
                continue
            
            # 验证数据类型
            try:
                # 验证NO字段
                no_value = str(row['NO']).strip()
                if not no_value:
                    continue
                
                # 验证数值字段
                if 'MIN' in row and row['MIN']:
                    float(row['MIN'])
                if 'MAX' in row and row['MAX']:
                    float(row['MAX'])
                if 'DECIMAL' in row and row['DECIMAL']:
                    int(row['DECIMAL'])
                
                validated_data.append(row)
                
            except (ValueError, TypeError) as e:
                self.logger.warning(f"参数定义数据验证失败: {row}, error={e}")
                continue
        
        return validated_data
    
    def _validate_relation_data(self, data: List[Dict]) -> List[Dict]:
        """
        验证关系定义数据
        
        Args:
            data: 原始数据
            
        Returns:
            List[Dict]: 验证后的数据
        """
        required_fields = ['NO', 'RELATION']
        validated_data = []
        
        for row in data:
            # 检查必需字段
            if not all(field in row and row[field] for field in required_fields):
                self.logger.warning(f"跳过无效的关系定义行: {row}")
                continue
            
            # 验证NO字段
            no_value = str(row['NO']).strip()
            if not no_value:
                continue
            
            validated_data.append(row)
        
        return validated_data
    
    def _validate_calc_data(self, data: List[Dict]) -> List[Dict]:
        """
        验证计算公式数据
        
        Args:
            data: 原始数据
            
        Returns:
            List[Dict]: 验证后的数据
        """
        required_fields = ['NO', 'FORMULA']
        validated_data = []
        
        for row in data:
            # 检查必需字段
            if not all(field in row and row[field] for field in required_fields):
                self.logger.warning(f"跳过无效的计算公式行: {row}")
                continue
            
            # 验证NO字段
            no_value = str(row['NO']).strip()
            if not no_value:
                continue
            
            # 验证公式语法
            formula = row.get('FORMULA', '')
            if formula and not self._validate_formula_syntax(formula):
                self.logger.warning(f"公式语法无效: {formula}")
                continue
            
            validated_data.append(row)
        
        return validated_data
    
    def _validate_chngvalue_data(self, data: List[Dict]) -> List[Dict]:
        """
        验证变化值数据
        
        Args:
            data: 原始数据
            
        Returns:
            List[Dict]: 验证后的数据
        """
        required_fields = ['NO']
        validated_data = []
        
        for row in data:
            # 检查必需字段
            if not all(field in row and row[field] for field in required_fields):
                self.logger.warning(f"跳过无效的变化值定义行: {row}")
                continue
            
            # 验证NO字段
            no_value = str(row['NO']).strip()
            if not no_value:
                continue
            
            validated_data.append(row)
        
        return validated_data
    
    def _validate_type_relation_data(self, data: List[Dict]) -> List[Dict]:
        """
        验证型号关系数据
        
        Args:
            data: 原始数据
            
        Returns:
            List[Dict]: 验证后的数据
        """
        required_fields = ['NO']
        validated_data = []
        
        for row in data:
            # 检查必需字段
            if not all(field in row and row[field] for field in required_fields):
                self.logger.warning(f"跳过无效的型号关系定义行: {row}")
                continue
            
            # 验证NO字段
            no_value = str(row['NO']).strip()
            if not no_value:
                continue
            
            validated_data.append(row)
        
        return validated_data
    
    def _validate_type_chngvl_data(self, data: List[Dict]) -> List[Dict]:
        """
        验证型号变化值数据
        
        Args:
            data: 原始数据
            
        Returns:
            List[Dict]: 验证后的数据
        """
        required_fields = ['NO']
        validated_data = []
        
        for row in data:
            # 检查必需字段
            if not all(field in row and row[field] for field in required_fields):
                self.logger.warning(f"跳过无效的型号变化值定义行: {row}")
                continue
            
            # 验证NO字段
            no_value = str(row['NO']).strip()
            if not no_value:
                continue
            
            validated_data.append(row)
        
        return validated_data
    
    def _validate_formula_syntax(self, formula: str) -> bool:
        """
        验证公式语法
        
        Args:
            formula: 公式字符串
            
        Returns:
            bool: 语法是否有效
        """
        try:
            # 替换变量为占位符进行语法验证
            test_formula = re.sub(r'#\d+', '1', formula)
            ast.parse(test_formula, mode='eval')
            return True
        except SyntaxError:
            return False
    
    def load_all_config_files(self, config_dir: str) -> bool:
        """
        加载所有配置文件
        
        Args:
            config_dir: 配置文件目录
            
        Returns:
            bool: 是否加载成功
        """
        try:
            # 加载参数定义
            define_path = Path(config_dir) / 'define.csv'
            if define_path.exists():
                self.load_define_csv(str(define_path))
            
            # 加载关系定义
            relation_path = Path(config_dir) / 'relation.csv'
            if relation_path.exists():
                self.load_relation_csv(str(relation_path))
            
            # 加载计算公式
            calc_path = Path(config_dir) / 'calc.csv'
            if calc_path.exists():
                self.load_calc_csv(str(calc_path))
            
            # 加载变化值定义
            chngvalue_path = Path(config_dir) / 'chngValue.csv'
            if chngvalue_path.exists():
                self.load_chngvalue_csv(str(chngvalue_path))
            
            # 加载型号关系定义
            type_relation_path = Path(config_dir) / 'type_relation.csv'
            if type_relation_path.exists():
                self.load_type_relation_csv(str(type_relation_path))
            
            # 加载型号变化值定义
            type_chngvl_path = Path(config_dir) / 'type_chngvl.csv'
            if type_chngvl_path.exists():
                self.load_type_chngvl_csv(str(type_chngvl_path))
            
            self.logger.info("所有配置文件加载完成")
            return True
            
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {e}")
            return False
    
    def get_parameter_definition(self, macro_no: str) -> Optional[Dict]:
        """
        获取参数定义
        
        Args:
            macro_no: 参数编号
            
        Returns:
            Optional[Dict]: 参数定义
        """
        for definition in self.define_data:
            if str(definition.get('NO')) == str(macro_no):
                return definition
        return None
    
    def get_relation_definition(self, macro_no: str) -> Optional[Dict]:
        """
        获取关系定义
        
        Args:
            macro_no: 关系编号
            
        Returns:
            Optional[Dict]: 关系定义
        """
        for definition in self.relation_data:
            if str(definition.get('NO')) == str(macro_no):
                return definition
        return None