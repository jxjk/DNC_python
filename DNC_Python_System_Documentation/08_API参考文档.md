# DNC参数计算系统 - API参考文档

## 概述

DNC参数计算系统提供了一套完整的Python API，用于程序化访问系统的核心功能。这些API可以用于集成到其他系统、自动化脚本或自定义应用程序中。

## 核心模块

### DataManager 数据管理器

#### 类定义
```python
class DataManager:
    """数据管理器，负责加载和管理Master数据"""
    
    def __init__(self, master_directory: str = "data/master"):
        """
        初始化数据管理器
        
        Args:
            master_directory: Master数据目录路径
        """
```

#### 主要方法

##### load_master_data
```python
def load_master_data(self, file_pattern: str = "*.csv") -> Dict[str, pd.DataFrame]:
    """
    加载Master数据文件
    
    Args:
        file_pattern: 文件匹配模式，默认为所有CSV文件
        
    Returns:
        Dict[str, pd.DataFrame]: 文件名到DataFrame的映射
        
    Raises:
        FileNotFoundError: 当文件不存在时
        UnicodeDecodeError: 当编码错误时
    """
```

##### batch_read_large_csv
```python
def batch_read_large_csv(self, file_path: str, batch_size: int = 1000) -> pd.DataFrame:
    """
    分批读取大文件
    
    Args:
        file_path: 文件路径
        batch_size: 批次大小，默认1000行
        
    Returns:
        pd.DataFrame: 合并后的数据
    """
```

##### validate_data_integrity
```python
def validate_data_integrity(self) -> Dict[str, bool]:
    """
    验证数据完整性
    
    Returns:
        Dict[str, bool]: 文件名到验证结果的映射
    """
```

##### fix_encoding_issues
```python
def fix_encoding_issues(self, file_path: str) -> pd.DataFrame:
    """
    修复编码问题
    
    Args:
        file_path: 文件路径
        
    Returns:
        pd.DataFrame: 修复后的数据
    """
```

### CalculationEngine 计算引擎

#### 类定义
```python
class CalculationEngine:
    """计算引擎，负责执行参数计算和验证"""
    
    def __init__(self, data_manager: DataManager):
        """
        初始化计算引擎
        
        Args:
            data_manager: 数据管理器实例
        """
```

#### 主要方法

##### calculate_parameters
```python
def calculate_parameters(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    计算参数
    
    Args:
        input_data: 输入参数字典
        
    Returns:
        Dict[str, Any]: 计算结果字典
    """
```

##### validate_relations
```python
def validate_relations(self, calculated_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    验证关系条件
    
    Args:
        calculated_data: 计算后的数据
        
    Returns:
        Tuple[bool, List[str]]: (验证结果, 错误消息列表)
    """
```

##### generate_macro_variables
```python
def generate_macro_variables(self, params: Dict[str, Any]) -> List[str]:
    """
    生成宏变量
    
    Args:
        params: 参数字典
        
    Returns:
        List[str]: 宏变量列表
    """
```

### ProgramGenerator 程序生成器

#### 类定义
```python
class ProgramGenerator:
    """程序生成器，负责生成NC程序"""
    
    def __init__(self, data_manager: DataManager):
        """
        初始化程序生成器
        
        Args:
            data_manager: 数据管理器实例
        """
```

#### 主要方法

##### generate_nc_program
```python
def generate_nc_program(self, product_type: str, params: Dict[str, Any]) -> str:
    """
    生成NC程序
    
    Args:
        product_type: 产品类型
        params: 参数字典
        
    Returns:
        str: 生成的程序代码
    """
```

##### apply_program_template
```python
def apply_program_template(self, template: str, variables: Dict[str, Any]) -> str:
    """
    应用程序模板
    
    Args:
        template: 程序模板
        variables: 变量字典
        
    Returns:
        str: 替换后的程序代码
    """
```

##### validate_program_syntax
```python
def validate_program_syntax(self, program: str) -> Tuple[bool, List[str]]:
    """
    验证程序语法
    
    Args:
        program: 程序代码
        
    Returns:
        Tuple[bool, List[str]]: (验证结果, 错误消息列表)
    """
```

## 工具模块

### ConfigManager 配置管理器

#### 类定义
```python
class ConfigManager:
    """配置管理器，负责读取和管理配置"""
    
    def __init__(self, config_file: str = "config/config.ini"):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
```

#### 主要方法

##### get_config
```python
def get_config(self, section: str, key: str, default: Any = None) -> Any:
    """
    获取配置值
    
    Args:
        section: 配置节
        key: 配置键
        default: 默认值
        
    Returns:
        Any: 配置值
    """
```

##### set_config
```python
def set_config(self, section: str, key: str, value: Any) -> None:
    """
    设置配置值
    
    Args:
        section: 配置节
        key: 配置键
        value: 配置值
    """
```

##### save_config
```python
def save_config(self) -> None:
    """保存配置到文件"""
```

### Logger 日志管理器

#### 类定义
```python
class Logger:
    """日志管理器，负责记录系统日志"""
    
    def __init__(self, log_file: str = "logs/dnc_system.log"):
        """
        初始化日志管理器
        
        Args:
            log_file: 日志文件路径
        """
```

#### 主要方法

##### info
```python
def info(self, message: str, **kwargs) -> None:
    """
    记录信息日志
    
    Args:
        message: 日志消息
        **kwargs: 额外参数
    """
```

##### warning
```python
def warning(self, message: str, **kwargs) -> None:
    """
    记录警告日志
    
    Args:
        message: 日志消息
        **kwargs: 额外参数
    """
```

##### error
```python
def error(self, message: str, **kwargs) -> None:
    """
    记录错误日志
    
    Args:
        message: 日志消息
        **kwargs: 额外参数
    """
```

##### debug
```python
def debug(self, message: str, **kwargs) -> None:
    """
    记录调试日志
    
    Args:
        message: 日志消息
        **kwargs: 额外参数
    """
```

## 数据模型

### ProductType 产品类型

```python
@dataclass
class ProductType:
    """产品类型数据模型"""
    
    no: int
    type_code: str
    define1: str
    define2: str
    description: str = ""
```

### CalculationParameter 计算参数

```python
@dataclass
class CalculationParameter:
    """计算参数数据模型"""
    
    name: str
    value: float
    unit: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    description: str = ""
```

### NCProgram NC程序

```python
@dataclass
class NCProgram:
    """NC程序数据模型"""
    
    program_code: str
    program_name: str
    product_type: str
    parameters: Dict[str, float]
    generated_code: str
    generation_time: datetime
```

## 使用示例

### 基本使用

```python
# 导入模块
from src.data.data_manager import DataManager
from src.utils.calculation import CalculationEngine
from src.data.models import ProductType

# 初始化数据管理器
data_manager = DataManager("data/master")

# 加载Master数据
master_data = data_manager.load_master_data()

# 初始化计算引擎
calc_engine = CalculationEngine(data_manager)

# 执行计算
input_params = {
    "Teeth_num": 20,
    "Module": 2.5,
    "Pressure_angle": 20.0
}

results = calc_engine.calculate_parameters(input_params)
print(f"计算结果: {results}")
```

### 批量处理

```python
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

def batch_calculate_products(product_list: List[Dict]) -> List[Dict]:
    """批量计算产品参数"""
    
    def calculate_single(product):
        try:
            results = calc_engine.calculate_parameters(product)
            return {"status": "success", "data": results}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(calculate_single, product_list))
    
    return results

# 使用示例
products = [
    {"Teeth_num": 20, "Module": 2.5},
    {"Teeth_num": 30, "Module": 3.0},
    {"Teeth_num": 40, "Module": 2.0}
]

batch_results = batch_calculate_products(products)
```

### 自定义计算

```python
# 自定义计算函数
def custom_calculation_function(params: Dict) -> Dict:
    """自定义计算逻辑"""
    
    # 获取计算引擎
    calc_engine = CalculationEngine(data_manager)
    
    # 执行标准计算
    base_results = calc_engine.calculate_parameters(params)
    
    # 添加自定义计算
    custom_results = {
        "custom_value1": base_results["value1"] * 1.1,
        "custom_value2": base_results["value2"] + 5.0
    }
    
    # 合并结果
    return {**base_results, **custom_results}

# 使用自定义计算
custom_params = {"Teeth_num": 25, "Module": 2.0}
custom_results = custom_calculation_function(custom_params)
```

## 错误处理

### 自定义异常

```python
class DNCSystemError(Exception):
    """DNC系统基础异常"""
    pass

class DataLoadError(DNCSystemError):
    """数据加载异常"""
    pass

class CalculationError(DNCSystemError):
    """计算异常"""
    pass

class ProgramGenerationError(DNCSystemError):
    """程序生成异常"""
    pass
```

### 错误处理示例

```python
try:
    # 尝试加载数据
    data = data_manager.load_master_data()
    
    # 尝试执行计算
    results = calc_engine.calculate_parameters(input_params)
    
    # 尝试生成程序
    program = program_generator.generate_nc_program("GPA18", results)
    
except DataLoadError as e:
    print(f"数据加载失败: {e}")
    # 处理数据加载错误
    
except CalculationError as e:
    print(f"计算失败: {e}")
    # 处理计算错误
    
except ProgramGenerationError as e:
    print(f"程序生成失败: {e}")
    # 处理程序生成错误
    
except Exception as e:
    print(f"未知错误: {e}")
    # 处理其他错误
```

## 性能优化

### 缓存机制

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_calculation(calculation_hash: str) -> Optional[Dict]:
    """获取缓存的计算结果"""
    pass

def cache_calculation_result(calculation_hash: str, result: Dict) -> None:
    """缓存计算结果"""
    pass
```

### 异步处理

```python
import asyncio

async def async_calculate_parameters(params: Dict) -> Dict:
    """异步计算参数"""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, calc_engine.calculate_parameters, params)
    return result

# 使用异步计算
async def main():
    tasks = [
        async_calculate_parameters(params1),
        async_calculate_parameters(params2),
        async_calculate_parameters(params3)
    ]
    
    results = await asyncio.gather(*tasks)
    return results
```

## 扩展开发

### 添加新的计算模块

```python
class CustomCalculationModule:
    """自定义计算模块"""
    
    def __init__(self, base_engine: CalculationEngine):
        self.base_engine = base_engine
    
    def custom_calculation(self, params: Dict) -> Dict:
        """自定义计算逻辑"""
        # 调用基础计算
        base_results = self.base_engine.calculate_parameters(params)
        
        # 添加自定义逻辑
        custom_results = self._apply_custom_logic(base_results)
        
        return custom_results
    
    def _apply_custom_logic(self, base_results: Dict) -> Dict:
        """应用自定义逻辑"""
        # 实现自定义计算逻辑
        pass
```

### 集成外部系统

```python
class ExternalSystemIntegration:
    """外部系统集成"""
    
    def __init__(self, api_endpoint: str, api_key: str):
        self.api_endpoint = api_endpoint
        self.api_key = api_key
    
    def export_to_external_system(self, program_data: Dict) -> bool:
        """导出数据到外部系统"""
        # 实现外部系统集成逻辑
        pass
    
    def import_from_external_system(self, external_id: str) -> Dict:
        """从外部系统导入数据"""
        # 实现数据导入逻辑
        pass
```

---

**API版本**: 1.0  
**最后更新**: 2025/10/23  
**维护者**: DNC开发团队
