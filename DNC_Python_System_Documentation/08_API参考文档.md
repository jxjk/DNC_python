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

## 基于VB.NET功能的API扩展

### 控件系统API

#### ControlManager 控件管理器

```python
class ControlManager:
    """控件管理器，基于VB.NET Frm_main.vb的控件管理逻辑"""
    
    def __init__(self):
        self.controls = {}
        self.control_groups = {}
    
    def create_control(self, control_type: str, control_id: str, 
                      properties: Dict) -> QWidget:
        """
        动态创建控件 - 基于makeTextBox, makeLabel等VB.NET方法
        
        Args:
            control_type: 控件类型 (TextBox, Label, Button等)
            control_id: 控件ID
            properties: 控件属性字典
            
        Returns:
            QWidget: 创建的控件实例
        """
    
    def add_control(self, control_id: str, control: QWidget):
        """添加控件到管理器"""
    
    def remove_control(self, control_id: str):
        """移除控件"""
    
    def enable_controls(self, control_ids: List[str], enabled: bool):
        """批量启用/禁用控件"""
    
    def manage_control_group(self, group_name: str, control_ids: List[str]):
        """管理控件组"""
```

#### 8种核心控件类型API

**LoadControl API**
```python
class LoadControl:
    """Load控件 - 基于makeCntrlLoad"""
    
    def __init__(self, data_source: str, field_mapping: Dict):
        self.data_source = data_source
        self.field_mapping = field_mapping
    
    def load_data(self) -> pd.DataFrame:
        """从CSV文件加载数据"""
    
    def validate_data(self) -> bool:
        """验证数据完整性"""
    
    def get_field_value(self, field_name: str) -> Any:
        """获取字段值"""
```

**InputControl API**
```python
class InputControl:
    """Input控件 - 基于makeCntrlInput"""
    
    def __init__(self, control_id: str, data_type: str, validation_rules: Dict):
        self.control_id = control_id
        self.data_type = data_type
        self.validation_rules = validation_rules
    
    def handle_text_change(self, new_value: str):
        """处理文本变更事件"""
    
    def validate_input(self, value: str) -> bool:
        """验证输入值"""
    
    def get_value(self) -> Any:
        """获取控件值"""
```

### 计算引擎API扩展

#### ExpressionCalculator 表达式计算器

```python
class ExpressionCalculator:
    """表达式计算器 - 基于getCalcResult"""
    
    def __init__(self):
        self.variables = {}
        self.functions = {
            'MAX': max, 'MIN': min, 'ROUND': round, 'ABS': abs
        }
    
    def calculate(self, expression: str, variables: Dict) -> float:
        """
        计算表达式值
        
        Args:
            expression: 计算表达式
            variables: 变量字典
            
        Returns:
            float: 计算结果
        """
    
    def _replace_variables(self, expression: str, variables: Dict) -> str:
        """替换表达式中的变量"""
```

#### RelationJudge 关系判断器

```python
class RelationJudge:
    """关系判断器 - 基于judgeRelation"""
    
    def judge(self, condition: str, left_value: Any, right_value: Any) -> bool:
        """
        判断关系条件
        
        Args:
            condition: 条件运算符 (=, <>, >, <, >=, <=)
            left_value: 左值
            right_value: 右值
            
        Returns:
            bool: 判断结果
        """
```

#### PrecisionController 精度控制器

```python
class PrecisionController:
    """精度控制器 - 基于四舍五入处理"""
    
    def __init__(self, decimal_places: int = 4):
        self.decimal_places = decimal_places
    
    def round_value(self, value: float) -> float:
        """四舍五入处理"""
    
    def format_display(self, value: float) -> str:
        """格式化显示值"""
```

### 通信模块API

#### NCProtocolHandler NC协议处理器

```python
class NCProtocolHandler:
    """NC协议处理器 - 基于makeSendTxt"""
    
    def __init__(self, protocol_type: str):
        self.protocol_type = protocol_type
        self.message_formatters = {
            'rexroth': self._format_rexroth_message,
            'brother': self._format_brother_message
        }
    
    def format_message(self, command: str, parameters: Dict) -> str:
        """格式化NC命令消息"""
    
    def _format_rexroth_message(self, command: str, parameters: Dict) -> str:
        """格式化Rexroth协议消息"""
    
    def _format_brother_message(self, command: str, parameters: Dict) -> str:
        """格式化Brother协议消息"""
```

#### NamedPipeClient 命名管道客户端

```python
class NamedPipeClient:
    """命名管道客户端 - 基于NamedPipeAsyncClient"""
    
    def __init__(self, pipe_name: str):
        self.pipe_name = pipe_name
        self.connected = False
    
    async def connect(self):
        """异步连接命名管道"""
    
    async def send_data(self, data: str):
        """异步发送数据"""
    
    def add_data_received_callback(self, callback: Callable):
        """添加数据接收回调"""
```

#### ConnectionManager 连接管理器

```python
class ConnectionManager:
    """连接管理器 - 基于ConnectionChange"""
    
    def __init__(self):
        self.connections = {}
        self.connection_callbacks = []
    
    def add_connection(self, connection_id: str, connection: object):
        """添加连接"""
    
    def remove_connection(self, connection_id: str):
        """移除连接"""
    
    def _notify_connection_change(self, connection_id: str, status: str):
        """通知连接状态变更"""
```

### 数据处理API扩展

#### CSVLoader CSV文件加载器

```python
class CSVLoader:
    """CSV文件加载器 - 基于LoadFileToTBL"""
    
    def __init__(self, encoding_detector: EncodingDetector):
        self.encoding_detector = encoding_detector
    
    def load_file(self, file_path: str) -> pd.DataFrame:
        """加载CSV文件"""
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """数据清理"""
```

#### TableSearcher 表搜索引擎

```python
class TableSearcher:
    """表搜索引擎 - 基于searchT_relation"""
    
    def __init__(self, data_tables: Dict[str, pd.DataFrame]):
        self.data_tables = data_tables
        self.search_cache = {}
    
    def search_table(self, table_name: str, search_criteria: Dict) -> pd.DataFrame:
        """搜索数据表"""
```

#### DataConverter 数据转换器

```python
class DataConverter:
    """数据转换器 - 基于searchT_ChngValue"""
    
    def __init__(self, conversion_rules: Dict):
        self.conversion_rules = conversion_rules
    
    def convert_value(self, value: Any, conversion_type: str) -> Any:
        """转换数据值"""
    
    def add_conversion_rule(self, conversion_type: str, rule: Callable):
        """添加转换规则"""
```

### 系统管理API

#### SystemInitializer 系统初始化器

```python
class SystemInitializer:
    """系统初始化器 - 基于Frm_main_Load"""
    
    def __init__(self, config_manager: ConfigManager, data_manager: DataManager):
        self.config_manager = config_manager
        self.data_manager = data_manager
    
    async def initialize_system(self):
        """异步初始化系统"""
    
    async def _load_configuration(self):
        """加载系统配置"""
    
    async def _load_master_data(self):
        """加载Master数据"""
    
    async def _initialize_ui(self):
        """初始化用户界面"""
    
    async def _setup_communication(self):
        """设置通信连接"""
```

#### ControlStateManager 控件状态管理器

```python
class ControlStateManager:
    """控件状态管理器"""
    
    def __init__(self):
        self.control_states = {}
        self.control_groups = {}
    
    def set_controls_enabled(self, control_ids: List[str], enabled: bool):
        """设置控件启用状态"""
    
    def set_controls_visible(self, control_ids: List[str], visible: bool):
        """设置控件可见性"""
    
    def add_control_group(self, group_name: str, control_ids: List[str]):
        """添加控件组"""
    
    def set_group_enabled(self, group_name: str, enabled: bool):
        """设置控件组启用状态"""
```

#### IniConfigManager INI配置管理器

```python
class IniConfigManager:
    """INI配置管理器"""
    
    def __init__(self, ini_file_path: str):
        self.ini_file_path = ini_file_path
        self.config = {}
    
    def load_config(self) -> Dict:
        """加载INI配置文件"""
    
    def save_config(self, config: Dict):
        """保存INI配置文件"""
    
    def get_value(self, section: str, key: str, default=None):
        """获取配置值"""
```

### 工具方法API

#### StringUtils 字符串工具类

```python
class StringUtils:
    """字符串工具类 - 基于VB.NET字符串处理函数"""
    
    @staticmethod
    def len_b(text: str) -> int:
        """计算字符串字节长度（兼容VB.NET的LenB函数）"""
    
    @staticmethod
    def make_format_str(format_pattern: str, *args) -> str:
        """创建格式化字符串"""
    
    @staticmethod
    def to_half_adjust(value: float, decimal_places: int = 0) -> float:
        """四舍五入处理（兼容VB.NET的ToHalfAdjust）"""
    
    @staticmethod
    def get_operator_name(operator_id: str) -> str:
        """获取操作员名称"""
```

#### SystemUtils 系统工具类

```python
class SystemUtils:
    """系统工具类"""
    
    @staticmethod
    def get_all_controls(parent_widget: QWidget) -> List[QWidget]:
        """获取所有子控件"""
    
    @staticmethod
    def change_form_size(form: QWidget, width: int, height: int):
        """改变窗体大小"""
    
    @staticmethod
    def show_info_form(title: str, message: str):
        """显示信息窗体"""
```

#### ToleranceCalculator 公差计算器

```python
class ToleranceCalculator:
    """公差计算器"""
    
    @staticmethod
    def get_shafts_tolerance(diameter: float, tolerance_class: str) -> Tuple[float, float]:
        """获取轴公差"""
    
    @staticmethod
    def get_length_tolerance(length: float, tolerance_class: str) -> Tuple[float, float]:
        """获取长度公差"""
```

### 事件处理API

#### EventDispatcher 事件分发器

```python
class EventDispatcher:
    """事件分发器"""
    
    def __init__(self):
        self.event_handlers = {}
        self.text_change_handlers = {}
    
    def register_handler(self, event_type: str, handler: Callable):
        """注册事件处理器"""
    
    def register_text_change_handler(self, control_id: str, handler: Callable):
        """注册文本变更处理器 - 基于txt_change"""
    
    def dispatch_event(self, event_type: str, event_data: Dict):
        """分发事件"""
```

#### TextChangeHandler 文本变更处理器

```python
class TextChangeHandler:
    """文本变更处理器 - 基于txt_change"""
    
    def __init__(self, validation_rules: Dict, calculation_trigger: Callable):
        self.validation_rules = validation_rules
        self.calculation_trigger = calculation_trigger
        self.change_event_flag = False
    
    def handle_text_change(self, control_id: str, new_text: str):
        """处理文本变更"""
    
    def _validate_text(self, control_id: str, text: str) -> bool:
        """验证文本内容"""
```

### 验证模块API

#### NumericValidator 数值验证器

```python
class NumericValidator:
    """数值验证器 - 基于chkTxtIsNumeric"""
    
    def validate(self, text: str, min_value: float = None, 
                max_value: float = None, decimal_places: int = None) -> bool:
        """验证数值文本"""
```

#### BusinessRuleValidator 业务规则验证器

```python
class BusinessRuleValidator:
    """业务规则验证器 - 基于chkAddControls"""
    
    def __init__(self, validation_rules: Dict):
        self.validation_rules = validation_rules
    
    def validate_controls(self, control_values: Dict) -> Dict[str, str]:
        """验证控件组业务规则"""
    
    def add_validation_rule(self, rule_name: str, rule: Callable):
        """添加验证规则"""
```

#### ValidationErrorHandler 验证错误处理器

```python
class ValidationErrorHandler:
    """验证错误处理器"""
    
    def __init__(self):
        self.error_messages = {}
    
    def add_error(self, control_id: str, message: str):
        """添加错误信息"""
    
    def clear_errors(self, control_id: str = None):
        """清除错误信息"""
    
    def has_errors(self) -> bool:
        """检查是否有错误"""
```

### 操作员管理API

#### OperatorManager 操作员管理器

```python
class OperatorManager:
    """操作员管理器 - 基于TB_OpeID_TextChanged"""
    
    def __init__(self):
        self.current_operator = None
        self.operator_database = {}
    
    def set_operator(self, operator_id: str):
        """设置当前操作员"""
    
    def get_operator_name(self, operator_id: str) -> str:
        """获取操作员名称"""
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

**API版本**: 2.0  
**最后更新**: 2025/10/23  
**维护者**: DNC开发团队  
**基于VB.NET源码**: DNC2.05labo/Frm_main.vb
