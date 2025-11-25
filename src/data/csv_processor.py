import csv
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging
import os

class CSVProcessor:
    """CSV文件处理器，负责读取、写入和验证CSV数据，与VB.NET版本功能对应"""
    
    def __init__(self, file_path: str = None):
        self.file_path = Path(file_path) if file_path else None
        self.logger = logging.getLogger(__name__)
        
    def read_csv(self, file_path: str = None, encoding: str = 'utf-8') -> List[Dict[str, Any]]:
        """读取CSV文件并返回字典列表，与VB.NET的LoadFileToTBL功能对应"""
        try:
            path = Path(file_path) if file_path else self.file_path
            if not path or not path.exists():
                self.logger.warning(f"CSV文件不存在: {path}")
                return []
                
            # 读取CSV文件，实现类似VB.NET的LoadFileToTBL功能
            data = []
            header_count = 0  # 对应VB.NET的headerStrNum
            file_error_count = 0  # 对应VB.NET的fileErrCnt
            
            # 尝试多种编码格式读取文件
            encodings = ['utf-8', 'gbk', 'gb2312', 'cp932', 'shift_jis']
            lines = None
            
            for enc in encodings:
                try:
                    with open(path, 'r', encoding=enc, newline='') as f:
                        lines = f.readlines()
                    self.logger.debug(f"文件 {path} 使用编码 {enc} 成功读取")
                    break
                except UnicodeDecodeError:
                    continue
            
            if lines is None:
                self.logger.error(f"无法使用常见编码读取文件: {path}")
                return []
                
            for i, line in enumerate(lines):
                line = line.strip()
                if line:  # 非空行
                    # 分割CSV行，对应VB.NET的Split(tmpStr, ",")
                    row_values = [val.strip() for val in line.split(',')]
                    
                    if i == 0:  # 首行作为标题
                        header_count = len(row_values)
                        headers = row_values
                    else:  # 数据行
                        row_count = len(row_values)  # 对应VB.NET的tmpStrNum
                        
                        # 检查列数是否与标题行一致，对应VB.NET的错误检查逻辑
                        if row_count != header_count:
                            self.logger.warning(f"CSV文件错误: {path}, 行 {i+1}: 列数不匹配 ({row_count} vs {header_count})")
                            file_error_count += 1
                            # 继续处理，但记录错误
                            
                        # 创建行数据，对应VB.NET的rw(k) = tmpArray(k)
                        row_dict = {}
                        for j, header in enumerate(headers):
                            if j < len(row_values):
                                row_dict[header] = row_values[j]
                            else:
                                row_dict[header] = ""  # 缺失值设为空字符串
                        data.append(row_dict)
            
            self.logger.info(f"CSV文件读取成功: {path}, 共 {len(data)} 条记录")
            return data
            
        except Exception as e:
            self.logger.error(f"读取CSV文件失败 {path}: {e}")
            return []
            
    def write_csv(self, data: List[Dict[str, Any]], file_path: str = None, 
                  fieldnames: List[str] = None, encoding: str = 'utf-8') -> bool:
        """将数据写入CSV文件"""
        try:
            path = Path(file_path) if file_path else self.file_path
            if not path:
                self.logger.error("未指定文件路径")
                return False
                
            path.parent.mkdir(parents=True, exist_ok=True)
            
            if not fieldnames and data:
                fieldnames = list(data[0].keys())
                
            with open(path, 'w', encoding=encoding, newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
                
            self.logger.info(f"CSV文件写入成功: {path}, 共 {len(data)} 条记录")
            return True
            
        except Exception as e:
            self.logger.error(f"写入CSV文件失败 {path}: {e}")
            return False
            
    def process_input_csv(self, input_file_path: str, 
                         product_master_data: Dict[str, Any]) -> Tuple[List[Dict], List[str]]:
        """处理输入CSV文件，验证产品型号并返回处理结果"""
        try:
            input_data = self.read_csv(input_file_path)
            if not input_data:
                return [], ["输入文件为空或读取失败"]
                
            valid_records = []
            error_messages = []
            
            required_fields = ['product_id', 'model', 'quantity']
            
            for i, record in enumerate(input_data, 1):
                # 检查必需字段
                missing_fields = [field for field in required_fields if field not in record or not record[field]]
                if missing_fields:
                    error_messages.append(f"第{i}行: 缺少必需字段 {missing_fields}")
                    continue
                    
                product_id = record['product_id'].strip()
                model = record['model'].strip()
                quantity = record['quantity'].strip()
                
                # 验证产品型号
                if model not in product_master_data:
                    error_messages.append(f"第{i}行: 产品型号 '{model}' 不存在于主数据中")
                    continue
                    
                # 验证数量
                try:
                    quantity_int = int(quantity)
                    if quantity_int <= 0:
                        error_messages.append(f"第{i}行: 数量必须为正整数")
                        continue
                except ValueError:
                    error_messages.append(f"第{i}行: 数量 '{quantity}' 不是有效的整数")
                    continue
                    
                # 验证产品编号格式
                if not self._validate_product_id(product_id):
                    error_messages.append(f"第{i}行: 产品编号 '{product_id}' 格式无效")
                    continue
                    
                # 添加验证通过的记录
                valid_record = {
                    'product_id': product_id,
                    'model': model,
                    'quantity': quantity_int,
                    'master_data': product_master_data[model]
                }
                valid_records.append(valid_record)
                
            self.logger.info(f"输入CSV处理完成: {len(valid_records)} 条有效记录, {len(error_messages)} 条错误")
            return valid_records, error_messages
            
        except Exception as e:
            error_msg = f"处理输入CSV文件失败: {e}"
            self.logger.error(error_msg)
            return [], [error_msg]
            
    def _validate_product_id(self, product_id: str) -> bool:
        """验证产品编号格式"""
        # 这里可以根据实际需求定义验证规则
        # 示例: 产品编号应为数字或字母数字组合
        if not product_id:
            return False
        # 可以添加更复杂的验证逻辑
        return True
        
    def validate_data(self, data: List[Dict[str, Any]], 
                     required_fields: List[str] = None) -> Tuple[bool, List[str]]:
        """验证数据完整性"""
        if not data:
            return False, ["数据为空"]
            
        if not required_fields:
            required_fields = list(data[0].keys()) if data else []
            
        errors = []
        
        for i, record in enumerate(data, 1):
            # 检查必需字段
            missing_fields = [field for field in required_fields if field not in record or not record[field]]
            if missing_fields:
                errors.append(f"第{i}行: 缺少字段 {missing_fields}")
                
            # 检查数据类型
            for field, value in record.items():
                if field == 'quantity' and value:
                    try:
                        int(value)
                    except ValueError:
                        errors.append(f"第{i}行: 字段 '{field}' 的值 '{value}' 不是有效的整数")
                        
        is_valid = len(errors) == 0
        return is_valid, errors
        
    def merge_csv_data(self, base_data: List[Dict], new_data: List[Dict], 
                      key_field: str = 'NO') -> List[Dict]:
        """合并CSV数据，基于关键字段去重"""
        try:
            merged_data = []
            existing_keys = set()
            
            # 添加基础数据
            for record in base_data:
                key = record.get(key_field)
                if key and key not in existing_keys:
                    merged_data.append(record)
                    existing_keys.add(key)
                    
            # 添加新数据（去重）
            for record in new_data:
                key = record.get(key_field)
                if key and key not in existing_keys:
                    merged_data.append(record)
                    existing_keys.add(key)
                    
            self.logger.info(f"CSV数据合并完成: 基础数据 {len(base_data)} 条, 新数据 {len(new_data)} 条, 合并后 {len(merged_data)} 条")
            return merged_data
            
        except Exception as e:
            self.logger.error(f"合并CSV数据失败: {e}")
            return base_data
            
    def export_to_excel(self, data: List[Dict[str, Any]], 
                       output_path: str, sheet_name: str = 'Data') -> bool:
        """将数据导出为Excel文件"""
        try:
            if not data:
                self.logger.warning("没有数据可导出")
                return False
                
            df = pd.DataFrame(data)
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
            self.logger.info(f"数据导出成功: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"导出Excel文件失败: {e}")
            return False
