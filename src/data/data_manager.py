import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from .csv_processor import CSVProcessor
from .models import Product
from ..utils.calculation import CalculationEngine

class DataManager:
    """数据管理器，负责加载、管理和处理所有数据"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        self.csv_processor = CSVProcessor()
        self.calculation_engine = CalculationEngine()
        
        # 数据存储
        self.master_data = {}
        self.product_data = {}
        self.loaded_files = {}
        
    def load_csv_files(self) -> bool:
        """加载所有CSV文件"""
        try:
            master_path = self.config_manager.get_master_path()
            if not master_path.exists():
                self.logger.error(f"Master目录不存在: {master_path}")
                return False
                
            # 加载主要CSV文件
            csv_files = [
                'header.csv', 'ini.csv', 'math.csv', 'prg.csv',
                'type_chngvl.csv', 'type_define.csv', 'type_prg.csv', 'type_relation.csv'
            ]
            
            for csv_file in csv_files:
                file_path = master_path / csv_file
                if file_path.exists():
                    data = self.csv_processor.read_csv(str(file_path))
                    self.loaded_files[csv_file] = data
                    self.logger.info(f"加载CSV文件: {csv_file}, {len(data)} 条记录")
                else:
                    self.logger.warning(f"CSV文件不存在: {file_path}")
                    
            # 加载prg子目录
            prg_dirs = ['prg1', 'prg2', 'prg3']
            for prg_dir in prg_dirs:
                prg_path = master_path / prg_dir
                if prg_path.exists():
                    self._load_prg_directory(prg_dir, prg_path)
                    
            # 构建产品数据索引
            self._build_product_index()
            
            self.logger.info("所有CSV文件加载完成")
            return True
            
        except Exception as e:
            self.logger.error(f"加载CSV文件失败: {e}")
            return False
            
    def _load_prg_directory(self, prg_name: str, prg_path: Path):
        """加载prg子目录中的CSV文件"""
        try:
            prg_files = [
                'add.csv', 'calc.csv', 'chngValue.csv', 'cntrl_rex.csv',
                'cntrl.csv', 'correct.csv', 'define.csv', 'failed_matches.csv',
                'input.csv', 'load.csv', 'measure.csv', 'preset.csv',
                'relation.csv', 'select.csv', 'switch.csv', 'type_define.csv', 'type_prg.csv'
            ]
            
            for prg_file in prg_files:
                file_path = prg_path / prg_file
                if file_path.exists():
                    key = f"{prg_name}/{prg_file}"
                    data = self.csv_processor.read_csv(str(file_path))
                    self.loaded_files[key] = data
                    self.logger.info(f"加载PRG文件: {key}, {len(data)} 条记录")
                    
        except Exception as e:
            self.logger.error(f"加载PRG目录失败 {prg_name}: {e}")
            
    def _build_product_index(self):
        """构建产品数据索引"""
        try:
            # 从type_define.csv构建产品型号索引
            type_define_data = self.loaded_files.get('type_define.csv', [])
            for record in type_define_data:
                product_type = record.get('TYPE')
                if product_type:
                    self.product_data[product_type] = record
                    
            self.logger.info(f"产品数据索引构建完成: {len(self.product_data)} 种产品型号")
            
        except Exception as e:
            self.logger.error(f"构建产品数据索引失败: {e}")
            
    def get_product_data(self, product_type: str) -> Optional[Dict[str, Any]]:
        """获取指定产品型号的数据"""
        return self.product_data.get(product_type)
        
    def get_all_product_types(self) -> List[str]:
        """获取所有产品型号列表"""
        return list(self.product_data.keys())
        
    def calculate_parameters(self, product_type: str, input_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """计算产品参数"""
        try:
            product_data = self.get_product_data(product_type)
            if not product_data:
                self.logger.warning(f"产品型号不存在: {product_type}")
                return {}
                
            # 创建产品对象
            product = Product(
                product_id=product_data.get('NO', ''),
                product_type=product_type,
                parameters=product_data,
                drawing_path=product_data.get('DRAWING', '')
            )
            
            # 执行计算
            calculated_params = self.calculation_engine.calculate_geometry(product, input_params)
            
            self.logger.info(f"参数计算完成: {product_type}")
            return calculated_params
            
        except Exception as e:
            self.logger.error(f"计算参数失败 {product_type}: {e}")
            return {}
            
    def process_input_file(self, input_file_path: str = None) -> Tuple[List[Dict], List[str]]:
        """处理输入CSV文件"""
        try:
            if not input_file_path:
                input_file_path = str(self.config_manager.get_input_file_path())
                
            if not Path(input_file_path).exists():
                return [], [f"输入文件不存在: {input_file_path}"]
                
            # 处理输入文件
            valid_records, error_messages = self.csv_processor.process_input_csv(
                input_file_path, self.product_data
            )
            
            # 为有效记录计算参数
            for record in valid_records:
                model = record['model']
                calculated_params = self.calculate_parameters(model)
                record['calculated_params'] = calculated_params
                
            self.logger.info(f"输入文件处理完成: {len(valid_records)} 条有效记录")
            return valid_records, error_messages
            
        except Exception as e:
            error_msg = f"处理输入文件失败: {e}"
            self.logger.error(error_msg)
            return [], [error_msg]
            
    def save_data(self, data: List[Dict[str, Any]], file_path: str, 
                 file_type: str = 'csv') -> bool:
        """保存数据到文件"""
        try:
            if file_type.lower() == 'csv':
                return self.csv_processor.write_csv(data, file_path)
            elif file_type.lower() == 'excel':
                return self.csv_processor.export_to_excel(data, file_path)
            else:
                self.logger.error(f"不支持的文件类型: {file_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"保存数据失败: {e}")
            return False
            
    def get_master_file_data(self, file_name: str) -> List[Dict[str, Any]]:
        """获取指定master文件的数据"""
        return self.loaded_files.get(file_name, [])
        
    def update_master_data(self, file_name: str, new_data: List[Dict[str, Any]]) -> bool:
        """更新master数据"""
        try:
            if file_name not in self.loaded_files:
                self.logger.warning(f"文件不存在于已加载数据中: {file_name}")
                return False
                
            # 合并数据
            current_data = self.loaded_files[file_name]
            merged_data = self.csv_processor.merge_csv_data(current_data, new_data)
            self.loaded_files[file_name] = merged_data
            
            # 如果是type_define.csv，需要重新构建索引
            if file_name == 'type_define.csv':
                self._build_product_index()
                
            self.logger.info(f"Master数据更新完成: {file_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"更新master数据失败 {file_name}: {e}")
            return False
            
    def validate_product_model(self, model: str) -> Tuple[bool, str]:
        """验证产品型号"""
        if model in self.product_data:
            return True, "产品型号有效"
        else:
            return False, f"产品型号 '{model}' 不存在"
            
    def search_products(self, keyword: str) -> List[str]:
        """搜索产品型号"""
        try:
            keyword_lower = keyword.lower()
            matching_products = [
                product_type for product_type in self.product_data.keys()
                if keyword_lower in product_type.lower()
            ]
            return matching_products
        except Exception as e:
            self.logger.error(f"搜索产品失败: {e}")
            return []
            
    def get_statistics(self) -> Dict[str, Any]:
        """获取数据统计信息"""
        return {
            'total_product_types': len(self.product_data),
            'loaded_files': len(self.loaded_files),
            'total_records': sum(len(data) for data in self.loaded_files.values())
        }
