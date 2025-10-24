# DNC系统Python项目完整文档

## 1. 项目概述

### 1.1 项目背景
本项目是基于VB.NET DNC2.05系统的Python重构版本，旨在提供更现代化、可维护性更好的数控设备参数管理解决方案。

### 1.2 重构目标
- **技术现代化**: 从VB.NET迁移到Python
- **架构优化**: 采用模块化、面向对象设计
- **性能提升**: 优化数据处理和计算性能
- **可扩展性**: 支持插件架构和配置驱动

### 1.3 项目特点
- **跨平台兼容**: 支持Windows、Linux、macOS
- **配置驱动**: 基于CSV配置文件的灵活系统
- **模块化设计**: 清晰的模块边界和接口定义
- **测试覆盖**: 完整的单元测试和集成测试

## 2. 项目结构

### 2.1 目录结构

```
dnc_python_project/
├── src/                          # 源代码目录
│   ├── core/                     # 核心模块
│   │   ├── __init__.py
│   │   ├── application.py        # 应用主类
│   │   ├── config.py             # 配置管理
│   │   └── event_dispatcher.py   # 事件分发器
│   ├── ui/                       # 用户界面模块
│   │   ├── __init__.py
│   │   ├── main_window.py        # 主窗口
│   │   ├── control_factory.py    # 控件工厂
│   │   └── widgets/              # 自定义控件
│   ├── business/                 # 业务逻辑模块
│   │   ├── __init__.py
│   │   ├── model_recognizer.py   # 型号识别
│   │   ├── program_matcher.py    # 程序匹配
│   │   ├── calculation_engine.py # 计算引擎
│   │   └── relation_validator.py # 关系验证
│   ├── data/                     # 数据访问模块
│   │   ├── __init__.py
│   │   ├── csv_processor.py      # CSV处理器
│   │   ├── data_validator.py     # 数据验证
│   │   └── file_manager.py       # 文件管理
│   ├── communication/            # 通信模块
│   │   ├── __init__.py
│   │   ├── nc_protocol.py        # NC协议
│   │   ├── named_pipe.py         # 命名管道
│   │   └── protocol_factory.py   # 协议工厂
│   └── utils/                    # 工具模块
│       ├── __init__.py
│       ├── logger.py             # 日志系统
│       ├── error_handler.py      # 错误处理
│       └── helpers.py            # 辅助函数
├── config/                       # 配置文件目录
│   ├── ini.csv                   # 系统配置
│   ├── header.csv                # 前缀处理
│   ├── type_define.csv           # 型号定义
│   ├── type_prg.csv              # 程序映射
│   ├── prg.csv                   # 程序信息
│   ├── load.csv                  # 参数加载
│   ├── cntrl.csv                 # 控件定义
│   ├── define.csv                # 变量定义
│   ├── chngValue.csv             # 值转换
│   ├── calc.csv                  # 计算逻辑
│   └── relation.csv              # 关系验证
├── tests/                        # 测试目录
│   ├── unit/                     # 单元测试
│   ├── integration/              # 集成测试
│   └── fixtures/                 # 测试数据
├── docs/                         # 文档目录
├── scripts/                      # 脚本目录
├── requirements.txt              # 依赖包列表
├── setup.py                      # 安装脚本
├── main.py                       # 程序入口
└── README.md                     # 项目说明
```

### 2.2 模块依赖关系

```
main.py
    ↓
application.py (核心应用)
    ├── ui.main_window (用户界面)
    ├── business.model_recognizer (型号识别)
    ├── business.program_matcher (程序匹配)
    ├── business.calculation_engine (计算引擎)
    ├── data.csv_processor (数据处理)
    ├── communication.nc_protocol (NC通信)
    └── utils.logger (日志系统)
```

## 3. 核心模块设计

### 3.1 应用核心模块 (core)

#### 3.1.1 Application类
```python
class Application:
    """应用主类，负责系统初始化和生命周期管理"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.event_dispatcher = EventDispatcher()
        self.ui_manager = UIManager()
        self.business_logic = BusinessLogic()
        self.data_manager = DataManager()
        self.communication_manager = CommunicationManager()
    
    def initialize(self):
        """系统初始化"""
        self.config.load_config()
        self.setup_logging()
        self.setup_ui()
        self.setup_business_logic()
        self.setup_communication()
    
    def run(self):
        """运行应用"""
        self.ui_manager.show_main_window()
```

#### 3.1.2 ConfigManager类
```python
class ConfigManager:
    """配置管理器"""
    
    def load_config(self, config_path: str = "config/"):
        """加载所有配置文件"""
        self.ini_config = self._load_csv(f"{config_path}ini.csv")
        self.header_config = self._load_csv(f"{config_path}header.csv")
        self.type_define_config = self._load_csv(f"{config_path}type_define.csv")
        # ... 其他配置文件
    
    def get_value(self, key: str, default=None):
        """获取配置值"""
        return self.ini_config.get(key, default)
```

### 3.2 用户界面模块 (ui)

#### 3.2.1 MainWindow类
```python
class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.control_factory = ControlFactory()
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("DNC系统")
        self.setGeometry(100, 100, 1200, 800)
        self.create_central_widget()
        self.create_toolbar()
        self.create_statusbar()
    
    def create_central_widget(self):
        """创建中心部件"""
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # 型号显示区域
        self.model_display = QLabel("型号: ")
        layout.addWidget(self.model_display)
        
        # 参数显示区域
        self.parameter_area = QScrollArea()
        layout.addWidget(self.parameter_area)
        
        self.setCentralWidget(central_widget)
```

#### 3.2.2 ControlFactory类
```python
class ControlFactory:
    """控件工厂，根据配置创建不同类型的控件"""
    
    def create_control(self, control_config: Dict) -> QWidget:
        """根据配置创建控件"""
        control_type = control_config.get('KIND')
        
        if control_type == 'load':
            return self._create_load_control(control_config)
        elif control_type == 'input':
            return self._create_input_control(control_config)
        elif control_type == 'measure':
            return self._create_measure_control(control_config)
        # ... 其他控件类型
    
    def _create_load_control(self, config: Dict) -> QWidget:
        """创建只读显示控件"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        label = QLabel(f"{config.get('MACRO')}: ")
        value_label = QLabel("待计算")
        
        layout.addWidget(label)
        layout.addWidget(value_label)
        
        return widget
```

### 3.3 业务逻辑模块 (business)

#### 3.3.1 ModelRecognizer类
```python
class ModelRecognizer:
    """型号识别器"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
    
    def recognize_model(self, qr_code: str) -> ModelInfo:
        """识别型号"""
        qr_mode = self.config.get_value('QRmode', '0')
        
        if qr_mode == '0':
            return self._fixed_char_delete_mode(qr_code)
        elif qr_mode == '1':
            return self._splitter_mode(qr_code)
        else:
            raise ValueError(f"不支持的QR模式: {qr_mode}")
    
    def _fixed_char_delete_mode(self, qr_code: str) -> ModelInfo:
        """固定字符删除模式"""
        delete_chars = int(self.config.get_value('BarCodeHeaderStrNum', '11'))
        model = qr_code[delete_chars:]
        return self._process_model(model)
    
    def _splitter_mode(self, qr_code: str) -> ModelInfo:
        """分隔符分割模式"""
        splitter = self.config.get_value('QRspltStr', '@')
        parts = qr_code.split(splitter)
        
        model_place = int(self.config.get_value('MODELplc', '2'))
        po_place = int(self.config.get_value('POplc', '1'))
        qty_place = int(self.config.get_value('QTYplc', '3'))
        
        return ModelInfo(
            model=parts[model_place - 1],
            po=parts[po_place - 1],
            quantity=parts[qty_place - 1]
        )
```

#### 3.3.2 ProgramMatcher类
```python
class ProgramMatcher:
    """程序匹配器"""
    
    def match_program(self, model: str) -> ProgramInfo:
        """匹配程序"""
        # 反向字符删除匹配算法
        for i in range(len(model), 0, -1):
            search_str = model[:i]
            matched_no = self._search_type_define(search_str)
            
            if matched_no:
                program_order = self._get_program_order(matched_no)
                return ProgramInfo(
                    program_no=matched_no,
                    program_order=program_order,
                    matched_string=search_str
                )
        
        raise ValueError(f"未找到匹配的程序: {model}")
    
    def _search_type_define(self, search_str: str) -> Optional[int]:
        """在type_define.csv中搜索"""
        for row in self.type_define_data:
            if row['TYPE'] == search_str:
                return int(row['NO'])
        return None
```

#### 3.3.3 CalculationEngine类
```python
class CalculationEngine:
    """计算引擎"""
    
    def calculate(self, program_no: int, model_parts: List[str]) -> Dict[str, Any]:
        """执行计算"""
        parameters = self._load_parameters(program_no)
        results = {}
        
        for macro, value in parameters.items():
            if value.startswith('define'):
                calculated_value = self._process_define(value, model_parts)
                results[macro] = calculated_value
            else:
                results[macro] = value
        
        return results
    
    def _process_define(self, define_name: str, model_parts: List[str]) -> str:
        """处理define定义"""
        define_rules = self._get_define_rules(define_name)
        
        for rule in define_rules:
            for part in model_parts:
                if part.startswith(rule['STR']):
                    result = part.replace(rule['BEFORE'], rule['AFTER'])
                    
                    if rule['CHNGVL']:
                        result = self._process_chng_value(rule['CHNGVL'], result)
                    
                    if rule['CALC']:
                        result = self._process_calc(rule['CALC'], result)
                    
                    return result
        
        return ""
```

### 3.4 数据访问模块 (data)

#### 3.4.1 CSVProcessor类
```python
class CSVProcessor:
    """CSV处理器"""
    
    def __init__(self):
        self.cache = {}
    
    def load_csv_to_dataframe(self, file_path: str) -> pd.DataFrame:
        """加载CSV文件到DataFrame"""
        if file_path in self.cache:
            return self.cache[file_path]
        
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            self.cache[file_path] = df
            return df
        except Exception as e:
            logger.error(f"加载CSV文件失败: {file_path}, 错误: {e}")
            raise
    
    def search_in_dataframe(self, df: pd.DataFrame, 
                          column: str, value: str) -> Optional[Dict]:
        """在DataFrame中搜索"""
        result = df[df[column] == value]
        if not result.empty:
            return result.iloc[0].to_dict()
        return None
```

### 3.5 通信模块 (communication)

#### 3.5.1 NCProtocol类
```python
class NCProtocol(ABC):
    """NC协议抽象基类"""
    
    @abstractmethod
    def send_parameters(self, parameters: Dict[str, Any]) -> bool:
        """发送参数到NC机床"""
        pass
    
    @abstractmethod
    def receive_data(self) -> Optional[str]:
        """接收数据"""
        pass

class RexrothProtocol(NCProtocol):
    """Rexroth协议实现"""
    
    def send_parameters(self, parameters: Dict[str, Any]) -> bool:
        """发送参数到Rexroth NC机床"""
        commands = []
        
        for macro, value in parameters.items():
            command = f"{macro}={value}"
            commands.append(command)
        
        return self._send_commands(commands)
```

## 4. 配置文件说明

### 4.1 系统配置文件 (ini.csv)

```csv
DEFINE,VALUE
BarCodeHeaderStrNum,11
QRmode,1
QRspltStr,@
MODELplc,2
POplc,1
QTYplc,3
OperatorID,OP001
AutoSend,1
```

### 4.2 型号定义文件 (type_define.csv)

```csv
NO,TYPE,DEFINE1,DEFINE2
1,AAA,define1-1,define1-2
2,AAA,define2-1,define2-2
3,C-CCC,,,
4,C-CCC10,define3-1,define3-2
```

### 4.3 程序参数文件 (load.csv)

```csv
NO,TYPE,DRAWING,DISPFLG,#500,#501,#502,#503,#504,#505,#506,#507,#508,#509
1,AAA,test1.jpg,1,10,size1,define1-1,define1-2,5,measure1,select1,relation1,switch1,correct1
2,AAA,test1.jpg,1,20,size1,define2-1,define2-2,5,measure1,select2,relation2,switch1,correct1
3,C-CCC,test1.jpg,1,30,size1,define3-1,define3-2,5,measure1,select3,relation3,switch1,correct3
```

## 5. 安装和部署

### 5.1 环境要求

#### 5.1.1 Python版本
- Python 3.8或更高版本

#### 5.1.2 系统依赖
```bash
# Windows
# 无特殊系统依赖

# Linux
sudo apt-get install python3-tk

# macOS
# 无特殊系统依赖
```

### 5.2 安装步骤

#### 5.2.1 克隆项目
```bash
git clone https://github.com/jxjk/dnc-python-project.git
cd dnc-python-project
```

#### 5.2.2 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

#### 5.2.3 安装依赖
```bash
pip install -r requirements.txt
```

#### 5.2.4 配置系统
```bash
# 复制配置文件模板
cp config/template/* config/

# 编辑配置文件
# 修改config/ini.csv中的系统配置
```

#### 5.2.5 运行系统
```bash
python main.py
```

### 5.3 依赖包列表 (requirements.txt)

```
PyQt5==5.15.7
pandas==1.5.3
numpy==1.24.3
pyserial==3.5
pywin32==305; sys_platform == 'win32'
pytest==7.3.1
black==23.3.0
flake8==6.0.0
mypy==1.3.0
```

## 6. 开发指南

### 6.1 代码规范

#### 6.1.1 命名约定
- **类名**: 使用大驼峰命名法，如 `ModelRecognizer`
- **函数名**: 使用小写字母和下划线，如 `recognize_model`
- **变量名**: 使用小写字母和下划线，如 `model_info`
- **常量**: 使用大写字母和下划线，如 `DEFAULT_CONFIG_PATH`

#### 6.1.2 类型注解
```python
def calculate_parameters(
    program_no: int,
    model_parts: List[str],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Union[str, int, float]]:
    """计算参数
    
    Args:
        program_no: 程序编号
        model_parts: 型号分割部分
        config: 可选配置
        
    Returns:
        计算后的参数字典
    """
    # 实现代码
```

### 6.2 测试指南

#### 6.2.1 单元测试
```python
class TestModelRecognizer(unittest.TestCase):
    
    def setUp(self):
        self.recognizer = ModelRecognizer()
    
    def test_fixed_char_delete_mode(self):
        qr_code = "PO@C-CCC10-20A-P5-30"
