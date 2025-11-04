# application.py
"""
DNC系统主应用程序模块
负责系统初始化、生命周期管理和模块协调
"""

import sys
import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import time  # 用于性能监控

# 绝对引用导入
from src.core.config import ConfigManager
from src.core.event_dispatcher import EventDispatcher
# from src.ui.main_window import MainWindow
from src.business.model_recognizer import ModelRecognizer
from src.business.program_matcher import ProgramMatcher
from src.business.calculation_engine import CalculationEngine
from src.business.relation_validator import RelationValidator
from src.business.nc_communicator import NCCommunicator
from src.business.macro_generator import MacroGenerator, FileGenerationFlow
from src.data.csv_processor import CSVProcessor
from src.data.data_validator import DataValidator
from src.data.file_manager import FileManager
from src.communication.nc_protocol import NCProtocol, NCProtocolType
from src.communication.named_pipe import NamedPipeServer as NamedPipeManager
from src.communication.protocol_factory import NCProtocolFactory as ProtocolFactory
from src.ui.control_factory import ControlFactory
from src.utils.logger import get_logger
from src.utils.error_handler import ErrorHandler, handle_errors
from src.core.cache_manager import get_global_cache_manager
from src.core.performance_monitor import get_global_performance_monitor
from src.utils.constants import (
    DEFAULT_CONFIG_PATH, 
    SUPPORTED_PROTOCOLS,
    EVENT_TYPES
)

# 新增导入
from src.ui.form_controller import FormController
from src.core.onoff_manager import OnOffManager


@dataclass
class InitializationResult:
    """系统初始化结果"""
    success: bool
    modules: Dict[str, Any] = None
    error: str = None
    
    @property
    def is_valid(self) -> bool:
        """检查初始化是否有效"""
        return self.success and self.modules is not None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'success': self.success,
            'modules': self.modules,
            'error': self.error,
            'is_valid': self.is_valid
        }


@dataclass
class ConfigValidationResult:
    """配置验证结果"""
    is_valid: bool
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'is_valid': self.is_valid,
            'errors': self.errors
        }


class ConfigError(Exception):
    """配置错误异常"""
    pass


class ConfigValidationError(Exception):
    """配置验证错误异常"""
    pass


class SystemInitializer:
    """系统初始化器 - 按照标准流程实现系统初始化"""
    
    def __init__(self, config_path: str):
        """
        初始化系统初始化器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.logger = get_logger("SystemInitializer")
        self.csv_processor = None
        self.config_manager = None
        self.cache = get_global_cache_manager()  # 添加缓存管理器
    
    def initialize_system(self) -> InitializationResult:
        """
        系统初始化主流程
        
        Returns:
            InitializationResult: 初始化结果
        """
        try:
            self.logger.info("开始系统初始化流程...")
            
            # 1. 加载基础配置
            base_config = self._load_base_config()
            
            # 2. 加载所有CSV配置文件
            configs = self._load_all_csv_configs()
            
            # 3. 验证配置依赖关系
            validation_result = self._validate_config_dependencies(configs)
            if not validation_result.is_valid:
                raise ConfigValidationError(f"配置验证失败: {validation_result.errors}")
            
            # 4. 构建配置缓存
            cache = self._build_config_cache(configs)
            
            # 5. 初始化各模块
            modules = self._initialize_modules(cache, base_config)
            
            self.logger.info("系统初始化完成")
            return InitializationResult(success=True, modules=modules)
            
        except Exception as e:
            error_msg = f"系统初始化失败: {e}"
            self.logger.error(error_msg)
            return InitializationResult(success=False, error=str(e))
    
    def _load_base_config(self) -> Dict[str, Any]:
        """加载基础配置"""
        self.logger.info("加载基础配置...")
        
        # 初始化配置管理器
        self.config_manager = ConfigManager(self.config_path)
        if not self.config_manager.load_config():
            raise ConfigError("基础配置文件加载失败")
        
        # 初始化CSV处理器
        self.csv_processor = CSVProcessor(self.config_manager)
        
        # 加载ini.csv配置 - 使用配置管理器获取完整路径
        ini_file_path = self.config_manager.get_csv_config_path('ini.csv')
        ini_config = self.csv_processor.load_csv(str(ini_file_path))
        if not ini_config:
            raise ConfigError("ini.csv配置文件加载失败")
        
        self.logger.info("基础配置加载完成")
        return ini_config
    
    def _load_all_csv_configs(self) -> Dict[str, Any]:
        """加载所有CSV配置文件"""
        self.logger.info("加载所有CSV配置文件...")
        
        config_files = [
            'ini.csv', 'header.csv', 'type_define.csv', 'type_relation.csv',
            'type_chngvl.csv', 'type_prg.csv', 'prg.csv',
            # 新增表单相关配置
            'cntrl.csv', 'load.csv', 'input.csv', 'correct.csv',
            'measure.csv', 'select.csv', 'switch.csv', 'relation.csv',
            'add.csv', 'changePRG.csv', 'selectPRG.csv'
        ]
        
        configs = {}
        for file in config_files:
            try:
                # 使用配置管理器获取完整路径
                file_path = self.config_manager.get_csv_config_path(file)
                config_data = self.csv_processor.load_csv(str(file_path))
                if config_data:
                    configs[file] = config_data
                    self.logger.debug(f"成功加载配置文件: {file}")
                else:
                    self.logger.warning(f"配置文件为空或加载失败: {file}")
            except Exception as e:
                self.logger.warning(f"配置文件加载异常 {file}: {e}")
        
        # 动态加载prg文件夹下的配置
        prg_configs = self._load_prg_configs()
        configs.update(prg_configs)
        
        self.logger.info(f"共加载 {len(configs)} 个配置文件")
        return configs

    
    def _load_prg_configs(self) -> Dict[str, Any]:
        """加载prg文件夹下的配置"""
        prg_configs = {}
        
        try:
            # 获取prg文件夹路径
            config_dir = os.path.dirname(self.config_path)
            prg_dir = os.path.join(config_dir, 'prg')
            
            if os.path.exists(prg_dir):
                for file in os.listdir(prg_dir):
                    if file.endswith('.csv'):
                        file_path = os.path.join(prg_dir, file)
                        config_data = self.csv_processor.load_csv(file_path)
                        if config_data:
                            prg_configs[file] = config_data
                            self.logger.debug(f"成功加载PRG配置文件: {file}")
        except Exception as e:
            self.logger.warning(f"PRG配置加载异常: {e}")
        
        return prg_configs
    
    def _validate_config_dependencies(self, configs: Dict[str, Any]) -> ConfigValidationResult:
        """验证配置依赖关系"""
        self.logger.info("验证配置依赖关系...")
        
        errors = []
        
        # 检查必需配置文件
        required_files = ['ini.csv', 'header.csv', 'type_define.csv', 'type_prg.csv']
        for file in required_files:
            if file not in configs or not configs[file]:
                errors.append(f"必需配置文件缺失或为空: {file}")
        
        # 验证type_define.csv结构
        if 'type_define.csv' in configs:
            type_define = configs['type_define.csv']
            if type_define:
                # 检查必需字段
                required_fields = ['NO', 'TYPE']
                for row in type_define:
                    for field in required_fields:
                        if field not in row or not row[field]:
                            errors.append(f"type_define.csv缺少必需字段: {field}")
        
        # 验证type_prg.csv结构
        if 'type_prg.csv' in configs:
            type_prg = configs['type_prg.csv']
            if type_prg:
                required_fields = ['NO']
                # 检查是否有至少一个prg字段（prg1, prg2, prg3等）
                has_prg_field = False
                for row in type_prg:
                    for field in required_fields:
                        if field not in row or not row[field]:
                            errors.append(f"type_prg.csv缺少必需字段: {field}")
                    # 检查是否有任何prg字段
                    for key in row.keys():
                        if key.startswith('prg'):
                            has_prg_field = True
                            break
                
                if not has_prg_field:
                    errors.append("type_prg.csv缺少prg字段（prg1, prg2等）")
        
        is_valid = len(errors) == 0
        if not is_valid:
            self.logger.error(f"配置验证失败: {errors}")
        else:
            self.logger.info("配置验证通过")
        
        return ConfigValidationResult(is_valid=is_valid, errors=errors)
    
    def _build_config_cache(self, configs: Dict[str, Any]) -> Dict[str, Any]:
        """构建配置缓存"""
        self.logger.info("构建配置缓存...")
        
        cache_key = "system_config_cache"
        cached_config = self.cache.get(cache_key)
        if cached_config is not None:
            self.logger.info("从缓存加载配置")
            return cached_config
        
        cache = {
            'configs': configs,
            'type_registry': self._build_type_registry(configs.get('type_define.csv', [])),
            'program_registry': self._build_program_registry(configs.get('type_prg.csv', [])),
            'header_rules': configs.get('header.csv', []),
            'relation_rules': configs.get('type_relation.csv', []),
            'change_value_rules': configs.get('type_chngvl.csv', [])
        }
        
        # 缓存配置，有效期1小时
        self.cache.set(cache_key, cache, ttl=3600)
        self.logger.info("配置缓存构建完成")
        return cache
    
    def _build_type_registry(self, type_define_data: List[Dict]) -> Dict[str, Dict]:
        """构建型号注册表"""
        registry = {}
        for row in type_define_data:
            if 'NO' in row and 'TYPE' in row:
                registry[row['TYPE']] = row
        return registry
    
    def _build_program_registry(self, type_prg_data: List[Dict]) -> Dict[str, List[str]]:
        """构建程序注册表"""
        registry = {}
        for row in type_prg_data:
            if 'NO' in row:
                no = row['NO']
                prg_list = []
                # 收集所有prg字段（prg1, prg2, prg3等）
                for key, value in row.items():
                    if key.startswith('prg') and value:
                        prg_list.append(str(value).strip())
                registry[no] = prg_list
        return registry
    
    def _initialize_modules(self, cache: Dict[str, Any], base_config: Dict[str, Any]) -> Dict[str, Any]:
        """初始化各模块"""
        self.logger.info("初始化系统模块...")
        
        modules = {}
        
        # 初始化事件分发器
        modules['event_dispatcher'] = EventDispatcher()
        
        # 初始化错误处理器
        modules['error_handler'] = ErrorHandler()
        
        # 初始化业务模块
        modules['model_recognizer'] = ModelRecognizer(self.config_manager)
        modules['program_matcher'] = ProgramMatcher(self.config_manager, self.csv_processor)
        modules['calculation_engine'] = CalculationEngine(self.config_manager, self.csv_processor)
        modules['relation_validator'] = RelationValidator(self.config_manager, self.csv_processor)
        modules['nc_communicator'] = NCCommunicator(self.config_manager)
        
        # 初始化数据模块
        modules['csv_processor'] = self.csv_processor  # 确保CSV处理器被包含在模块中
        modules['data_validator'] = DataValidator()
        modules['file_manager'] = FileManager()
        
        # 初始化通信模块
        modules['protocol_factory'] = ProtocolFactory()
        modules['named_pipe_manager'] = NamedPipeManager()
        
        # 初始化UI模块
        modules['control_factory'] = ControlFactory()
        
        # 初始化文件生成模块
        modules['file_generation_flow'] = FileGenerationFlow(
            config_manager=self.config_manager,
            csv_processor=self.csv_processor
        )
        modules['macro_generator'] = MacroGenerator(
            config_manager=self.config_manager,
            csv_processor=self.csv_processor
        )
        
        # 设置配置缓存
        for module_name, module in modules.items():
            if hasattr(module, 'set_config_cache'):
                module.set_config_cache(cache)
        
        self.logger.info("系统模块初始化完成")
        return modules


class DNCApplication(QObject):
    """
    DNC系统主应用程序类
    负责协调各个模块的工作流程和生命周期管理
    """
    
    # 信号定义
    model_recognized = pyqtSignal(dict)  # 型号识别完成
    program_matched = pyqtSignal(dict)   # 程序匹配完成
    parameters_calculated = pyqtSignal(dict)  # 参数计算完成
    data_sent = pyqtSignal(bool)         # 数据发送完成
    error_occurred = pyqtSignal(str)     # 错误发生
    nc_command_sent = pyqtSignal(dict)   # NC命令发送完成
    nc_response_received = pyqtSignal(dict)  # NC响应接收完成
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化DNC应用程序
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        super().__init__()
        
        # 基础配置
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        self.is_initialized = False
        self.is_running = False
        
        # 核心模块实例
        self.config_manager: Optional[ConfigManager] = None
        self.logger = get_logger("DNCApplication")  # 立即初始化日志记录器
        self.performance_monitor = get_global_performance_monitor()  # 添加性能监控器
        self.error_handler: Optional[ErrorHandler] = None
        
        # 业务逻辑模块
        self.model_recognizer: Optional[ModelRecognizer] = None
        self.program_matcher: Optional[ProgramMatcher] = None
        self.calculation_engine: Optional[CalculationEngine] = None
        self.relation_validator: Optional[RelationValidator] = None
        self.nc_communicator: Optional[NCCommunicator] = None
        self.macro_generator: Optional[MacroGenerator] = None
        self.file_generation_flow: Optional[FileGenerationFlow] = None
        
        # 数据访问模块
        self.csv_processor: Optional[CSVProcessor] = None
        self.data_validator: Optional[DataValidator] = None
        self.file_manager: Optional[FileManager] = None
        
        # 通信模块
        self.protocol_factory: Optional[ProtocolFactory] = None
        self.named_pipe_manager: Optional[NamedPipeManager] = None
        self.current_protocol: Optional[NCProtocol] = None
        
        # UI模块
        self.main_window: Optional[Any] = None
        self.control_factory: Optional[ControlFactory] = None
        
        # 当前状态
        self.current_model: Optional[str] = None
        self.current_program_no: Optional[int] = None
        self.current_program_match: Optional[Dict[str, Any]] = None
        self.current_parameters: Dict[str, Any] = {}
        
        # 初始化定时器
        self.initialization_timer = QTimer()
        self.initialization_timer.setSingleShot(True)
        self.initialization_timer.timeout.connect(self._on_initialization_timeout)
        
        # 新增属性
        self.form_controller = None
        self.onoff_manager = None
    
    @handle_errors
    def initialize(self) -> bool:
        """
        初始化DNC系统
        
        Returns:
            bool: 初始化是否成功
        """
        start_time = time.time()
        try:
            self.logger.info("开始初始化DNC系统...")
            
            # 使用SystemInitializer进行标准化初始化
            system_initializer = SystemInitializer(self.config_path)
            initialization_result = system_initializer.initialize_system()
            
            if not initialization_result.success:
                self.logger.error(f"系统初始化失败: {initialization_result.error}")
                self.performance_monitor.record_error_rate("initialize", 1, 1)
                return False
            
            # 从初始化结果中获取模块实例
            modules = initialization_result.modules
            self._setup_modules_from_initialization(modules)
            
            # 设置初始化超时保护
            self.initialization_timer.start(10000)  # 10秒超时
            
            # 新增初始化
            if not self._initialize_enhanced_features():
                self.logger.warning("增强功能初始化失败，但继续运行基础功能")
                
            self.is_initialized = True
            self.logger.info("DNC系统初始化完成")
            
            # 记录响应时间
            response_time = (time.time() - start_time) * 1000  # 毫秒
            self.performance_monitor.record_response_time("initialize", response_time)
            self.performance_monitor.record_error_rate("initialize", 0, 1)
            
            return True
            
        except Exception as e:
            # 记录错误
            self.performance_monitor.record_error_rate("initialize", 1, 1)
            error_msg = f"系统初始化失败: {str(e)}"
            # 如果logger还没有初始化，直接打印错误信息
            if self.logger:
                self.logger.error(error_msg)
            else:
                print(f"错误: {error_msg}")
            self._show_error_dialog("初始化错误", error_msg)
            return False

    def _setup_modules_from_initialization(self, modules: Dict[str, Any]) -> None:
        """从初始化结果设置模块实例"""
        # 核心模块实例
        self.event_dispatcher = modules.get('event_dispatcher')
        self.error_handler = modules.get('error_handler')
        
        # 业务逻辑模块
        self.model_recognizer = modules.get('model_recognizer')
        self.program_matcher = modules.get('program_matcher')
        self.calculation_engine = modules.get('calculation_engine')
        self.relation_validator = modules.get('relation_validator')
        self.nc_communicator = modules.get('nc_communicator')
        self.macro_generator = modules.get('macro_generator')
        self.file_generation_flow = modules.get('file_generation_flow')
        
        # 数据访问模块
        self.csv_processor = modules.get('csv_processor')
        self.data_validator = modules.get('data_validator')
        self.file_manager = modules.get('file_manager')
        
        # 通信模块
        self.protocol_factory = modules.get('protocol_factory')
        self.named_pipe_manager = modules.get('named_pipe_manager')
        
        # UI模块
        self.control_factory = modules.get('control_factory')
        
        # 关键修复：从CSV处理器获取配置管理器
        if self.csv_processor and hasattr(self.csv_processor, 'config_manager'):
            self.config_manager = self.csv_processor.config_manager
            self.logger.info("从CSV处理器获取配置管理器成功")
        else:
            self.logger.warning("无法从CSV处理器获取配置管理器，将创建新的实例")
            try:
                self.config_manager = ConfigManager(self.config_path)
                if not self.config_manager.load_config():
                    self.logger.error("配置管理器创建失败")
                else:
                    self.logger.info("配置管理器创建成功")
            except Exception as e:
                self.logger.error(f"配置管理器创建异常: {e}")
        
        # 设置事件处理器
        self._setup_event_handlers()
        
        # 确保CSV处理器已正确设置
        if not self.csv_processor:
            self.logger.warning("CSV处理器未正确初始化，尝试重新创建")
            try:
                self.csv_processor = CSVProcessor(self.config_manager)
                self.logger.info("CSV处理器重新创建成功")
            except Exception as e:
                self.logger.error(f"CSV处理器重新创建失败: {e}")
    
    def _setup_event_handlers(self) -> None:
        """设置事件处理器"""
        if self.event_dispatcher:
            self.event_dispatcher.subscribe(
                'model_recognized', 
                self._on_model_recognized
            )
            self.event_dispatcher.subscribe(
                'program_matched',
                self._on_program_matched
            )
            self.event_dispatcher.subscribe(
                'parameters_calculated',
                self._on_parameters_calculated
            )
            self.event_dispatcher.subscribe(
                'nc_communication_status',
                self._on_nc_communication_status
            )
    
    def _on_initialization_timeout(self) -> None:
        """初始化超时处理"""
        if not self.is_initialized:
            self.logger.warning("系统初始化超时")
            self._show_error_dialog("初始化超时", "系统初始化时间过长，请检查配置文件")
    
    @handle_errors
    def run(self) -> int:
        """
        运行DNC应用程序
        
        Returns:
            int: 应用程序退出代码
        """
        start_time = time.time()
        if not self.is_initialized:
            self.logger.error("系统未初始化，无法运行")
            self.performance_monitor.record_error_rate("run", 1, 1)
            return 1
        
        try:
            self.is_running = True
            self.logger.info("启动DNC应用程序...")
            
            # 将导入移到这里，避免循环导入
            from src.ui.main_window import MainWindow
            # 创建Qt应用程序实例
            app = QApplication(sys.argv)
            app.setApplicationName("DNC系统")
            app.setApplicationVersion("2.0.0")
            
            # 创建主窗口
            self.main_window = MainWindow(self)
            self.main_window.show()
            
            # 启动通信模块
            self._start_communication()
            
            self.logger.info("DNC应用程序启动成功")
            
            # 记录响应时间
            response_time = (time.time() - start_time) * 1000  # 毫秒
            self.performance_monitor.record_response_time("run", response_time)
            self.performance_monitor.record_error_rate("run", 0, 1)
            
            # 运行应用程序主循环
            return app.exec_()
            
        except Exception as e:
            # 记录错误
            self.performance_monitor.record_error_rate("run", 1, 1)
            error_msg = f"应用程序运行失败: {str(e)}"
            self.logger.error(error_msg)
            self._show_error_dialog("运行错误", error_msg)
            return 1
        finally:
            self.is_running = False
            self._cleanup()
    
    def _start_communication(self) -> None:
        """启动通信模块"""
        try:
            # 检查配置管理器是否可用
            if not self.config_manager:
                self.logger.warning("配置管理器不可用，使用默认通信配置")
                # 使用默认配置
                protocol_type = "rexroth"
                use_named_pipe = "0"
                pipe_name = "DNC_Pipe"
            else:
                # 初始化NC通信协议
                protocol_type = self.config_manager.get_config_value("nc", "protocol")
                if not protocol_type:
                    protocol_type = "rexroth"
                
                # 启动命名管道
                use_named_pipe = self.config_manager.get_config_value("system", "use_named_pipe")
                pipe_name = self.config_manager.get_config_value("system", "pipe_name")
                if not pipe_name:
                    pipe_name = "DNC_Pipe"
            
            # 初始化NC通信协议
            if self.protocol_factory:
                # 使用NCProtocolType枚举创建协议
                try:
                    protocol_enum = NCProtocolType(protocol_type.lower())
                    self.current_protocol = self.protocol_factory.create_protocol(protocol_enum)
                except ValueError:
                    self.logger.warning(f"不支持的协议类型: {protocol_type}，使用默认协议")
                    self.current_protocol = self.protocol_factory.create_protocol(NCProtocolType.REXROTH)
            
            self.logger.info(f"通信模块启动完成，使用协议: {protocol_type}")
            
        except Exception as e:
            self.logger.warning(f"通信模块启动失败: {str(e)}")
    
    @handle_errors
    def process_qr_code(self, qr_code: str) -> bool:
        """
        处理QR码输入
        
        Args:
            qr_code: QR码字符串
            
        Returns:
            bool: 处理是否成功
        """
        start_time = time.time()
        try:
            self.logger.info(f"开始处理QR码: {qr_code}")
            
            # 1. 型号识别
            model_info = self.model_recognizer.recognize_model(qr_code)
            if not model_info:
                self.logger.error("型号识别失败")
                self.performance_monitor.record_error_rate("process_qr_code", 1, 1)
                return False
            
            # 将 RecognitionResult 转换为字典以便发送信号
            model_info_dict = {
                'model': model_info.model,
                'qr_code': model_info.qr_code,
                'po': model_info.po,
                'quantity': model_info.quantity,
                'recognition_mode': model_info.recognition_mode,
                'confidence': model_info.confidence,
                'error_message': model_info.error_message
            }
            
            # self.current_model = model_info.model
            # self.model_recognized.emit(model_info_dict)
            self.event_dispatcher.dispatch(EVENT_TYPES["MODEL_RECOGNIZED"], model_info_dict)
            self.current_model = model_info.model
            self.model_recognized.emit(model_info_dict)
            # self.event_dispatcher.dispatch(EVENT_TYPES["MODEL_RECOGNIZED"], model_info_dict)
            
            # 2. 程序匹配
            program_info = self.program_matcher.match_program(self.current_model)
            if not program_info:
                self.logger.error("程序匹配失败")
                self.performance_monitor.record_error_rate("process_qr_code", 1, 1)
                return False
            
            self.current_program_no = program_info.program_no
            self.current_program_match = program_info
            self.program_matched.emit({
                'program_no': program_info.program_no,
                'matched_string': program_info.matched_string,
                'match_type': program_info.match_type,
                'confidence': program_info.confidence,
                'error_message': program_info.error_message
            })
            self.event_dispatcher.dispatch(EVENT_TYPES["PROGRAM_MATCHED"], {
                'program_no': program_info.program_no,
                'matched_string': program_info.matched_string,
                'match_type': program_info.match_type,
                'confidence': program_info.confidence,
                'error_message': program_info.error_message
            })
            
            # 3. 参数计算
            calc_result = self.calculation_engine.calculate_parameters(
                self.current_program_no
            )
            
            if not calc_result.success:
                self.logger.error("参数计算失败")
                self.performance_monitor.record_error_rate("process_qr_code", 1, 1)
                return False
            
            self.current_parameters = calc_result.parameters
            self.parameters_calculated.emit(calc_result.parameters)
            self.event_dispatcher.dispatch(EVENT_TYPES["PARAMETERS_CALCULATED"], calc_result.parameters)
            
            # 4. 关系验证
            validation_results = self.relation_validator.validate_relations(
                self.current_program_no,
                calc_result.parameters
            )
            
            # 5. 更新UI显示
            if self.main_window:
                self.main_window.update_display(
                    model_info_dict, 
                    {
                        'program_no': program_info.program_no,
                        'matched_string': program_info.matched_string,
                        'match_type': program_info.match_type,
                        'confidence': program_info.confidence,
                        'error_message': program_info.error_message
                    }, 
                    calc_result.parameters,
                    {
                        'valid': validation_results.valid,
                        'errors': validation_results.errors,
                        'warnings': validation_results.warnings
                    }
                )
            
            self.logger.info("QR码处理完成")
            
            # 记录响应时间
            response_time = (time.time() - start_time) * 1000  # 毫秒
            self.performance_monitor.record_response_time("process_qr_code", response_time)
            self.performance_monitor.record_error_rate("process_qr_code", 0, 1)
            
            return True
            
        except Exception as e:
            # 记录错误
            self.performance_monitor.record_error_rate("process_qr_code", 1, 1)
            error_msg = f"QR码处理失败: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False
    
    @handle_errors
    def send_parameters_to_nc(self) -> bool:
        """
        发送参数到NC机床
        
        Returns:
            bool: 发送是否成功
        """
        start_time = time.time()
        try:
            if not self.current_protocol:
                self.logger.error("NC通信协议未初始化")
                self.performance_monitor.record_error_rate("send_parameters_to_nc", 1, 1)
                return False
            
            if not self.current_parameters:
                self.logger.error("没有可发送的参数")
                self.performance_monitor.record_error_rate("send_parameters_to_nc", 1, 1)
                return False
            
            self.logger.info("开始发送参数到NC机床...")
            
            success = self.current_protocol.send_parameters(self.current_parameters)
            
            if success:
                self.logger.info("参数发送成功")
                self.data_sent.emit(True)
                self.event_dispatcher.dispatch(EVENT_TYPES["DATA_SENT"], {"success": True})
            else:
                self.logger.error("参数发送失败")
                self.data_sent.emit(False)
                self.event_dispatcher.dispatch(EVENT_TYPES["DATA_SENT"], {"success": False})
            
            # 记录响应时间
            response_time = (time.time() - start_time) * 1000  # 毫秒
            self.performance_monitor.record_response_time("send_parameters_to_nc", response_time)
            self.performance_monitor.record_error_rate("send_parameters_to_nc", 0 if success else 1, 1)
            
            return success
            
        except Exception as e:
            # 记录错误
            self.performance_monitor.record_error_rate("send_parameters_to_nc", 1, 1)
            error_msg = f"参数发送失败: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False
    
    def _on_pipe_data_received(self, data: str) -> None:
        """
        命名管道数据接收处理
        
        Args:
            data: 接收到的数据
        """
        try:
            self.logger.info(f"接收到管道数据: {data}")
            
            # 处理接收到的数据（可能是QR码或其他指令）
            if data.strip():
                self.process_qr_code(data.strip())
                
        except Exception as e:
            self.logger.error(f"管道数据处理失败: {str(e)}")
    
    def _on_model_recognized(self, data: Dict[str, Any]) -> None:
        """型号识别完成事件处理"""
        self.logger.info(f"型号识别完成: {data.get('model')}")
    
    def _on_program_matched(self, data: Dict[str, Any]) -> None:
        """程序匹配完成事件处理"""
        self.logger.info(f"程序匹配完成: 程序号 {data.get('program_no')}")
    
    def _on_parameters_calculated(self, data: Dict[str, Any]) -> None:
        """参数计算完成事件处理"""
        self.logger.info(f"参数计算完成，共 {len(data)} 个参数")
    
    def _on_data_sent(self, data: Dict[str, Any]) -> None:
        """数据发送完成事件处理"""
        success = data.get('success', False)
        status = "成功" if success else "失败"
        self.logger.info(f"数据发送{status}")
    
    def _on_nc_communication_status(self, data: Dict[str, Any]) -> None:
        """NC通信状态事件处理"""
        status = data.get('status', '')
        message = data.get('message', '')
        self.logger.info(f"NC通信状态: {status} - {message}")

    
    def _show_error_dialog(self, title: str, message: str) -> None:
        """显示错误对话框"""
        try:
            QMessageBox.critical(None, title, message)
        except Exception:
            # 如果Qt未初始化，直接打印错误信息
            print(f"错误: {title} - {message}")
    
    def _cleanup(self) -> None:
        """清理资源"""
        self.logger.info("开始清理系统资源...")
        
        # 停止通信模块
        if self.named_pipe_manager:
            self.named_pipe_manager.stop()
        
        # 关闭文件资源
        if self.file_manager:
            self.file_manager.close_all_files()
        
        self.logger.info("系统资源清理完成")
    
    def get_application_info(self) -> Dict[str, Any]:
        """
        获取应用程序信息
        
        Returns:
            Dict[str, Any]: 应用程序信息
        """
        return {
            "name": "DNC系统",
            "version": "2.0.0",
            "initialized": self.is_initialized,
            "running": self.is_running,
            "current_model": self.current_model,
            "current_program": self.current_program_no,
            "parameter_count": len(self.current_parameters)
        }

    def set_current_program(self, program_info: Dict[str, Any]) -> None:
        """设置当前程序"""
        self.current_program_no = program_info.get('program_no')
        self.program_matched.emit(program_info)
    
    def get_current_program(self) -> Optional[Dict[str, Any]]:
        """获取当前程序信息"""
        if self.current_program_no is None:
            return None
        return {
            'program_no': self.current_program_no,
            'name': f"程序 {self.current_program_no}"
        }

    def connect_to_device(self) -> bool:
        """连接到设备"""
        try:
            self.logger.info("开始连接设备...")
            
            # 这里应该实现设备连接逻辑
            # 暂时返回成功
            self.logger.info("设备连接成功")
            return True
            
        except Exception as e:
            error_msg = f"设备连接失败: {str(e)}"
            self.logger.error(error_msg)
            return False

    def disconnect_from_device(self) -> bool:
        """断开设备连接"""
        try:
            self.logger.info("开始断开设备连接...")
            
            # 这里应该实现设备断开逻辑
            # 暂时返回成功
            self.logger.info("设备已断开")
            return True
            
        except Exception as e:
            error_msg = f"设备断开失败: {str(e)}"
            self.logger.error(error_msg)
            return False

    def calculate_parameters(self) -> bool:
        """计算参数"""
        try:
            self.logger.info("开始计算参数...")
            
            # 这里应该实现参数计算逻辑
            # 暂时返回成功
            self.logger.info("参数计算完成")
            return True
            
        except Exception as e:
            error_msg = f"参数计算失败: {str(e)}"
            self.logger.error(error_msg)
            return False

    def update_parameters(self, parameters: Dict[str, Any]) -> None:
        """更新参数"""
        try:
            self.logger.info(f"更新参数: {parameters}")
            
            # 更新当前参数
            self.current_parameters.update(parameters)
            
            self.logger.info("参数更新完成")
            
        except Exception as e:
            error_msg = f"参数更新失败: {str(e)}"
            self.logger.error(error_msg)

    def update_model(self, model_info: Dict[str, Any]) -> None:
        """更新型号信息"""
        try:
            self.logger.info(f"更新型号信息: {model_info}")
            
            # 更新当前型号
            self.current_model = model_info.get('model')
            
            self.logger.info("型号信息更新完成")
            
        except Exception as e:
            error_msg = f"型号信息更新失败: {str(e)}"
            self.logger.error(error_msg)

    def recognize_model(self) -> bool:
        """基于当前参数进行型号识别"""
        try:
            self.logger.info("开始型号识别...")
            
            if not self.current_parameters:
                self.logger.warning("没有参数可用于型号识别")
                return False
            
            # 从参数中提取型号描述
            model_description = self.current_parameters.get('model', {}).get('model_description', '')
            if not model_description:
                self.logger.warning("没有型号描述可用于识别")
                return False
            
            # 使用型号识别器进行识别
            model_info = self.model_recognizer.recognize_model(model_description)
            if not model_info:
                self.logger.error("型号识别失败")
                return False
            
            # 更新当前型号并发送信号
            self.current_model = model_info.model
            # 将 RecognitionResult 转换为字典以便发送信号
            model_info_dict = {
                'model': model_info.model,
                'qr_code': model_info.qr_code,
                'po': model_info.po,
                'quantity': model_info.quantity,
                'recognition_mode': model_info.recognition_mode,
                'confidence': model_info.confidence,
                'error_message': model_info.error_message
            }
            self.model_recognized.emit(model_info_dict)
            self.event_dispatcher.dispatch(EVENT_TYPES["MODEL_RECOGNIZED"], model_info_dict)
            
            self.logger.info(f"型号识别完成: {self.current_model}")
            return True
            
        except Exception as e:
            error_msg = f"型号识别失败: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False

    def match_program(self) -> bool:
        """基于当前型号进行程序匹配"""
        try:
            self.logger.info("开始程序匹配...")
            
            if not self.current_model:
                self.logger.warning("没有当前型号可用于程序匹配")
                return False
            
            # 使用程序匹配器进行匹配
            program_info = self.program_matcher.match_program(self.current_model)
            if not program_info:
                self.logger.error("程序匹配失败")
                return False
            
            # 更新当前程序号并发送信号
            self.current_program_no = program_info.program_no
            self.current_program_match = program_info
            self.program_matched.emit({
                'program_no': program_info.program_no,
                'matched_string': program_info.matched_string,
                'match_type': program_info.match_type,
                'confidence': program_info.confidence,
                'error_message': program_info.error_message
            })
            self.event_dispatcher.dispatch(EVENT_TYPES["PROGRAM_MATCHED"], {
                'program_no': program_info.program_no,
                'matched_string': program_info.matched_string,
                'match_type': program_info.match_type,
                'confidence': program_info.confidence,
                'error_message': program_info.error_message
            })

            
            self.logger.info(f"程序匹配完成: 程序号 {self.current_program_no}")
            return True
            
        except Exception as e:
            error_msg = f"程序匹配失败: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False

    def get_current_program_sequence(self) -> Optional[List[str]]:
        """
        获取当前程序序列
        
        Returns:
            当前程序序列列表，如果没有则返回None
        """
        try:
            if hasattr(self, 'current_program_match') and self.current_program_match:
                # 获取匹配结果中的程序序列
                program_sequence = getattr(self.current_program_match, 'program_sequence', None)
                if program_sequence:
                    return program_sequence
                # 如果没有program_sequence，尝试从匹配的程序号构建
                program_no = getattr(self.current_program_match, 'program_no', None)
                if program_no:
                    return [f"prg{program_no}"]
            return None
        except Exception as e:
            self.logger.warning(f"获取当前程序序列失败: {e}")
            return None

    def execute_program(self, program_info: Dict[str, Any]) -> None:
        """执行程序"""
        # 这里应该实现程序执行逻辑
        self.logger.info(f"执行程序: {program_info}")
        
    def _initialize_enhanced_features(self) -> bool:
        """初始化增强功能（表单控制和ON/OFF）"""
        try:
            self.logger.info("初始化增强功能...")
            
            # 初始化表单控制器
            self.form_controller = FormController(self.config_manager)
            if not self.form_controller.load_relation_config():
                self.logger.warning("表单控制器初始化失败")
                return False
                
            # 初始化ON/OFF管理器
            self.onoff_manager = OnOffManager(self.config_manager)
            if not self.onoff_manager.load_onoff_state():
                self.logger.warning("ON/OFF管理器初始化失败")
                return False
                
            self.logger.info("增强功能初始化完成")
            return True
            
        except Exception as e:
            self.logger.error(f"增强功能初始化失败: {e}")
            return False
            
    def _load_all_csv_configs(self) -> Dict[str, Any]:
        """加载所有CSV配置文件"""
        self.logger.info("加载所有CSV配置文件...")
        
        config_files = [
            'ini.csv', 'header.csv', 'type_define.csv', 'type_relation.csv',
            'type_chngvl.csv', 'type_prg.csv', 'prg.csv',
            # 新增表单相关配置
            'cntrl.csv', 'load.csv', 'input.csv', 'correct.csv',
            'measure.csv', 'select.csv', 'switch.csv', 'relation.csv',
            'add.csv', 'changePRG.csv', 'selectPRG.csv'
        ]
        
        loaded_configs = {}
        for config_file in config_files:
            try:
                config_data = self.config_manager.get_config(config_file)
                if config_data:
                    loaded_configs[config_file] = config_data
                    self.logger.debug(f"成功加载配置文件: {config_file}")
                else:
                    self.logger.warning(f"配置文件为空或加载失败: {config_file}")
            except Exception as e:
                self.logger.error(f"加载配置文件失败 {config_file}: {e}")
        
        self.logger.info(f"共加载 {len(loaded_configs)} 个配置文件")
        return loaded_configs
        
    def process_form_inputs(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理表单输入数据
        
        Args:
            form_data: 表单数据字典
            
        Returns:
            Dict[str, Any]: 处理后的数据
        """
        try:
            self.logger.info("处理表单输入数据...")
            
            # 验证表单数据
            validation_result = self._validate_form_data(form_data)
            if not validation_result['valid']:
                self.logger.error(f"表单数据验证失败: {validation_result['errors']}")
                return {'success': False, 'errors': validation_result['errors']}
            
            # 更新表单控制器变量
            for key, value in form_data.items():
                if key.startswith('size'):
                    self.form_controller.update_variable(key, value)
            
            # 处理ON/OFF相关数据
            onoff_result = self._process_onoff_data(form_data)
            
            # 调用计算引擎
            calculation_result = self.calculation_engine.calculate_with_forms(
                self.program_matcher.current_program_no,
                form_data
            )
            
            self.logger.info("表单数据处理完成")
            return {
                'success': True,
                'calculation_result': calculation_result,
                'onoff_state': self.onoff_manager.get_current_state()
            }
            
        except Exception as e:
            self.logger.error(f"表单数据处理失败: {e}")
            return {'success': False, 'errors': [str(e)]}

    def _validate_form_data(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证表单数据"""
        errors = []
        
        # 验证数值范围
        for key, value in form_data.items():
            if isinstance(value, (int, float)):
                # 这里可以根据具体配置验证范围
                pass
        
        # 验证关系条件
        if self.form_controller:
            # 这里可以添加关系验证逻辑
            pass
        
        return {'valid': len(errors) == 0, 'errors': errors}

    def _process_onoff_data(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理ON/OFF相关数据"""
        try:
            # 检查是否有ON/OFF状态变更
            if 'onoff_state' in form_data:
                new_state = form_data['onoff_state']
                if self.onoff_manager.update_onoff_state(new_state):
                    self.logger.info(f"ON/OFF状态已更新为: {new_state}")
            
            # 处理switch控件值
            switch_updates = {}
            for key, value in form_data.items():
                if key.startswith('switch_'):
                    switch_name = key.replace('switch_', '')
                    switch_values = self.onoff_manager.get_switch_values(switch_name)
                    switch_updates[key] = switch_values
            
            return {'switch_updates': switch_updates}
            
        except Exception as e:
            self.logger.error(f"ON/OFF数据处理失败: {e}")
            return {'switch_updates': {}}
            
    def get_form_visibility(self, form_name: str, current_conditions: Dict[str, Any]) -> bool:
        """
        获取表单显示状态
        
        Args:
            form_name: 表单名称
            current_conditions: 当前条件变量
            
        Returns:
            bool: 是否显示表单
        """
        if not self.form_controller:
            return True  # 如果没有表单控制器，默认显示
        
        return self.form_controller.should_display_form(form_name, current_conditions)

    def update_form_conditions(self, conditions: Dict[str, Any]):
        """
        更新表单条件变量
        
        Args:
            conditions: 条件变量字典
        """
        if self.form_controller:
            for key, value in conditions.items():
                self.form_controller.update_variable(key, value)
                
    def get_onoff_state(self) -> int:
        """获取当前ON/OFF状态"""
        if not self.onoff_manager:
            return 0  # 默认状态
        
        return self.onoff_manager.get_current_state()

    def cycle_onoff_state(self) -> bool:
        """循环到下一个ON/OFF状态"""
        if not self.onoff_manager:
            return False
        
        return self.onoff_manager.cycle_next_state()

    def get_switch_display_value(self, switch_name: str) -> str:
        """获取switch控件的显示值"""
        if not self.onoff_manager:
            return "未知"
        
        values = self.onoff_manager.get_switch_values(switch_name)
        return values.get('display_value', '未知')

    def get_switch_send_value(self, switch_name: str) -> Any:
        """获取switch控件的发送值"""
        if not self.onoff_manager:
            return 0
        
        values = self.onoff_manager.get_switch_values(switch_name)
        return values.get('send_value', 0)


def create_application(config_path: Optional[str] = None) -> DNCApplication:
    """
    创建DNC应用程序实例的工厂函数
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        DNCApplication: 应用程序实例
    """
    return DNCApplication(config_path)


if __name__ == "__main__":
    # 测试代码
    app = create_application()
    
    if app.initialize():
        print("DNC系统初始化成功")
        print("应用程序信息:", app.get_application_info())
    else:
        print("DNC系统初始化失败")