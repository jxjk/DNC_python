from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from pathlib import Path

@dataclass
class Product:
    """产品数据模型"""
    product_id: str
    product_type: str
    parameters: Dict[str, Any]
    drawing_path: Optional[str] = None
    quantity: int = 1
    
    def get_parameter(self, key: str, default: Any = None) -> Any:
        """获取参数值"""
        return self.parameters.get(key, default)
        
    def update_parameter(self, key: str, value: Any):
        """更新参数值"""
        self.parameters[key] = value
        
    def validate_parameters(self) -> List[str]:
        """验证参数完整性"""
        errors = []
        required_fields = ['NO', 'TYPE']
        
        for field in required_fields:
            if field not in self.parameters or not self.parameters[field]:
                errors.append(f"缺少必需字段: {field}")
                
        return errors

@dataclass
class InputRecord:
    """输入记录模型"""
    product_id: str
    model: str
    quantity: int
    master_data: Dict[str, Any]
    calculated_params: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'product_id': self.product_id,
            'model': self.model,
            'quantity': self.quantity,
            'master_data': self.master_data,
            'calculated_params': self.calculated_params or {}
        }

@dataclass
class CalculationResult:
    """计算结果模型"""
    product_type: str
    input_parameters: Dict[str, Any]
    calculated_parameters: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None
    calculation_time: Optional[float] = None
    
    def is_valid(self) -> bool:
        """检查计算结果是否有效"""
        return self.success and not self.error_message

@dataclass
class MasterFile:
    """Master文件模型"""
    file_name: str
    file_path: Path
    data: List[Dict[str, Any]]
    description: Optional[str] = None
    
    def get_record_count(self) -> int:
        """获取记录数量"""
        return len(self.data)
        
    def find_records(self, field: str, value: Any) -> List[Dict[str, Any]]:
        """根据字段值查找记录"""
        return [record for record in self.data if record.get(field) == value]
        
    def update_record(self, key_field: str, key_value: Any, updates: Dict[str, Any]) -> bool:
        """更新记录"""
        for record in self.data:
            if record.get(key_field) == key_value:
                record.update(updates)
                return True
        return False

@dataclass
class ProgramData:
    """程序数据模型"""
    program_id: str
    program_name: str
    parameters: Dict[str, Any]
    calculation_rules: List[Dict[str, Any]]
    input_requirements: List[str]
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> List[str]:
        """验证输入参数"""
        errors = []
        for requirement in self.input_requirements:
            if requirement not in inputs:
                errors.append(f"缺少必需输入参数: {requirement}")
        return errors

@dataclass
class GeometryParameters:
    """几何参数模型"""
    # 基本几何参数
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    diameter: Optional[float] = None
    radius: Optional[float] = None
    angle: Optional[float] = None
    
    # 计算参数
    volume: Optional[float] = None
    surface_area: Optional[float] = None
    weight: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {k: v for k, v in self.__dict__.items() if v is not None}

@dataclass
class BatchProcessingResult:
    """批处理结果模型"""
    total_records: int
    successful_records: int
    failed_records: int
    processing_time: float
    results: List[CalculationResult]
    error_messages: List[str]
    
    def success_rate(self) -> float:
        """计算成功率"""
        if self.total_records == 0:
            return 0.0
        return (self.successful_records / self.total_records) * 100

@dataclass
class ExportConfiguration:
    """导出配置模型"""
    output_format: str  # 'csv', 'excel', 'json'
    include_calculated_params: bool = True
    include_master_data: bool = False
    include_errors: bool = True
    file_name_template: str = "output_{timestamp}"
    
    def validate(self) -> List[str]:
        """验证配置"""
        errors = []
        valid_formats = ['csv', 'excel', 'json']
        if self.output_format not in valid_formats:
            errors.append(f"不支持的输出格式: {self.output_format}")
        return errors

@dataclass
class SystemConfiguration:
    """系统配置模型"""
    # 路径配置
    master_directory: str
    log_directory: str
    input_directory: str
    output_directory: str
    
    # 应用程序设置
    version: str
    language: str
    auto_save: bool
    backup_enabled: bool
    
    # 计算设置
    calculation_precision: int
    rounding_method: str
    auto_validation: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'master_directory': self.master_directory,
            'log_directory': self.log_directory,
            'input_directory': self.input_directory,
            'output_directory': self.output_directory,
            'version': self.version,
            'language': self.language,
            'auto_save': self.auto_save,
            'backup_enabled': self.backup_enabled,
            'calculation_precision': self.calculation_precision,
            'rounding_method': self.rounding_method,
            'auto_validation': self.auto_validation
        }
