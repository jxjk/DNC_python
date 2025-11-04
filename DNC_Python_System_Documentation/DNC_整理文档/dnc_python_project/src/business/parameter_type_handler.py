"""
参数类型处理器
负责处理不同类型的参数（load、input、select、switch、relation、define）的显示和交互逻辑
"""

from enum import Enum
from typing import Dict, List, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)


class ParameterType(Enum):
    """参数类型枚举"""
    LOAD = "load"
    INPUT = "input"
    SELECT = "select"
    SWITCH = "switch"
    RELATION = "relation"
    DEFINE = "define"


class ParameterTypeHandler:
    """参数类型处理器"""
    
    # 参数类型映射
    kind_mapping = {
        "load": ParameterType.LOAD,
        "input": ParameterType.INPUT,
        "select": ParameterType.SELECT,
        "switch": ParameterType.SWITCH,
        "relation": ParameterType.RELATION,
        "define": ParameterType.DEFINE
    }
    
    def __init__(self):
        """初始化参数类型处理器"""
        self.parameter_definitions = {}  # 参数定义字典
        self.relation_definitions = {}   # 关系定义字典
        self.calculation_engine = None   # 计算引擎引用
        self.select_options_cache = {}   # 选择框选项缓存
        
        logger.info("参数类型处理器初始化完成")
    
    def set_calculation_engine(self, calculation_engine):
        """设置计算引擎实例"""
        self.calculation_engine = calculation_engine
        logger.info("计算引擎已设置")
    
    def load_parameter_definitions(self, define_data: List[Dict]) -> bool:
        """从define.csv加载参数定义"""
        try:
            self.parameter_definitions = {}
            for row in define_data:
                if 'NO' in row and 'DEFINE' in row:
                    self.parameter_definitions[row['NO']] = row
            
            logger.info(f"已加载 {len(self.parameter_definitions)} 个参数定义")
            return True
        except Exception as e:
            logger.error(f"加载参数定义失败: {e}")
            return False
    
    def load_relation_definitions(self, relation_data: List[Dict]) -> bool:
        """从relation.csv加载关系定义"""
        try:
            self.relation_definitions = {}
            for row in relation_data:
                if 'NO' in row and 'RELATION' in row:
                    self.relation_definitions[row['NO']] = row
            
            logger.info(f"已加载 {len(self.relation_definitions)} 个关系定义")
            return True
        except Exception as e:
            logger.error(f"加载关系定义失败: {e}")
            return False
    
    def get_parameter_type(self, kind_str: str) -> ParameterType:
        """根据宏类型字符串返回对应的ParameterType枚举"""
        kind_lower = kind_str.lower() if kind_str else "load"
        return self.kind_mapping.get(kind_lower, ParameterType.LOAD)
    
    def process_parameter_value(self, macro_no: str, parameter_type: ParameterType, 
                              raw_value: str, context: Dict = None) -> Dict[str, Any]:
        """根据参数类型处理原始值"""
        if context is None:
            context = {}
        
        try:
            if parameter_type == ParameterType.LOAD:
                return self._process_load_type(macro_no, raw_value, context)
            elif parameter_type == ParameterType.INPUT:
                return self._process_input_type(macro_no, raw_value, context)
            elif parameter_type == ParameterType.SELECT:
                return self._process_select_type(macro_no, raw_value, context)
            elif parameter_type == ParameterType.SWITCH:
                return self._process_switch_type(macro_no, raw_value, context)
            elif parameter_type == ParameterType.RELATION:
                return self._process_relation_type(macro_no, raw_value, context)
            elif parameter_type == ParameterType.DEFINE:
                return self._process_define_type(macro_no, raw_value, context)
            else:
                # 默认处理为LOAD类型
                return self._process_load_type(macro_no, raw_value, context)
                
        except Exception as e:
            logger.error(f"处理参数值失败: macro_no={macro_no}, type={parameter_type}, error={e}")
            return self._create_default_result(macro_no, parameter_type, raw_value)
    
    def _process_load_type(self, macro_no: str, raw_value: str, context: Dict) -> Dict[str, Any]:
        """处理直接加载类型的参数"""
        return {
            "macro_no": macro_no,
            "parameter_type": ParameterType.LOAD,
            "raw_value": raw_value,
            "display_value": raw_value,
            "is_editable": False,
            "options": [],
            "validation_rules": {}
        }
    
    def _process_input_type(self, macro_no: str, raw_value: str, context: Dict) -> Dict[str, Any]:
        """处理输入框类型的参数"""
        # 获取参数定义中的验证规则
        validation_rules = self._get_input_validation_rules(macro_no)
        
        return {
            "macro_no": macro_no,
            "parameter_type": ParameterType.INPUT,
            "raw_value": raw_value,
            "display_value": raw_value,
            "is_editable": True,
            "options": [],
            "validation_rules": validation_rules
        }
    
    def _process_select_type(self, macro_no: str, raw_value: str, context: Dict) -> Dict[str, Any]:
        """处理下拉选择类型的参数"""
        options = self._get_select_options(macro_no)
        
        return {
            "macro_no": macro_no,
            "parameter_type": ParameterType.SELECT,
            "raw_value": raw_value,
            "display_value": raw_value,
            "is_editable": True,
            "options": options,
            "validation_rules": {"allowed_values": options}
        }
    
    def _process_switch_type(self, macro_no: str, raw_value: str, context: Dict) -> Dict[str, Any]:
        """处理开关按钮类型的参数"""
        # 将字符串值转换为布尔值
        display_value = raw_value.strip().lower() in ['1', 'true', 'yes', 'on']
        
        return {
            "macro_no": macro_no,
            "parameter_type": ParameterType.SWITCH,
            "raw_value": raw_value,
            "display_value": display_value,
            "is_editable": True,
            "options": [True, False],
            "validation_rules": {"allowed_values": [True, False]}
        }
    
    def _process_relation_type(self, macro_no: str, raw_value: str, context: Dict) -> Dict[str, Any]:
        """处理计算关系类型的参数"""
        if not self.calculation_engine:
            logger.warning(f"计算引擎未设置，无法处理关系类型参数: {macro_no}")
            return self._create_default_result(macro_no, ParameterType.RELATION, raw_value)
        
        try:
            # 获取关系定义
            relation_def = self.relation_definitions.get(macro_no, {})
            formula_name = relation_def.get('RELATION', '')
            
            if not formula_name:
                logger.warning(f"未找到关系定义: {macro_no}")
                return self._create_default_result(macro_no, ParameterType.RELATION, raw_value)
            
            # 使用计算引擎计算结果
            calculated_value = self.calculation_engine.calculate_relation(
                macro_no, formula_name, context
            )
            
            return {
                "macro_no": macro_no,
                "parameter_type": ParameterType.RELATION,
                "raw_value": str(calculated_value) if calculated_value is not None else raw_value,
                "display_value": str(calculated_value) if calculated_value is not None else raw_value,
                "is_editable": False,  # 关系类型参数通常不可编辑
                "options": [],
                "validation_rules": {}
            }
            
        except Exception as e:
            logger.error(f"计算关系参数失败: {macro_no}, error={e}")
            return self._create_default_result(macro_no, ParameterType.RELATION, raw_value)
    
    def _process_define_type(self, macro_no: str, raw_value: str, context: Dict) -> Dict[str, Any]:
        """处理定义值类型的参数"""
        # 获取参数定义
        param_def = self.parameter_definitions.get(macro_no, {})
        define_value = param_def.get('DEFINE', raw_value)
        
        return {
            "macro_no": macro_no,
            "parameter_type": ParameterType.DEFINE,
            "raw_value": raw_value,
            "display_value": define_value,
            "is_editable": False,  # 定义值通常不可编辑
            "options": [],
            "validation_rules": {}
        }
    
    def _get_select_options(self, macro_no: str) -> List[str]:
        """获取选择框的选项列表"""
        if macro_no in self.select_options_cache:
            return self.select_options_cache[macro_no]
        
        # 从参数定义中获取选项
        param_def = self.parameter_definitions.get(macro_no, {})
        options_str = param_def.get('OPTIONS', '')
        
        if options_str:
            options = [opt.strip() for opt in options_str.split(',')]
        else:
            options = []
        
        self.select_options_cache[macro_no] = options
        return options
    
    def _get_input_validation_rules(self, macro_no: str) -> Dict[str, Any]:
        """获取输入框的验证规则"""
        param_def = self.parameter_definitions.get(macro_no, {})
        
        validation_rules = {
            "min_value": param_def.get('MIN', None),
            "max_value": param_def.get('MAX', None),
            "decimal_places": param_def.get('DECIMAL', 0),
            "required": param_def.get('REQUIRED', True)
        }
        
        # 清理None值
        return {k: v for k, v in validation_rules.items() if v is not None}
    
    def validate_parameter_value(self, macro_no: str, value: str, 
                               parameter_type: ParameterType) -> bool:
        """验证参数值的有效性"""
        try:
            if parameter_type == ParameterType.INPUT:
                return self._validate_input_value(macro_no, value)
            elif parameter_type == ParameterType.SELECT:
                return self._validate_select_value(macro_no, value)
            elif parameter_type == ParameterType.SWITCH:
                return self._validate_switch_value(value)
            else:
                return True  # 其他类型默认验证通过
                
        except Exception as e:
            logger.error(f"验证参数值失败: {macro_no}, value={value}, error={e}")
            return False
    
    def _validate_input_value(self, macro_no: str, value: str) -> bool:
        """验证输入框值"""
        try:
            validation_rules = self._get_input_validation_rules(macro_no)
            
            # 检查是否为数字
            numeric_value = float(value)
            
            # 检查最小值
            if 'min_value' in validation_rules and numeric_value < float(validation_rules['min_value']):
                return False
            
            # 检查最大值
            if 'max_value' in validation_rules and numeric_value > float(validation_rules['max_value']):
                return False
            
            return True
            
        except ValueError:
            # 如果无法转换为数字，检查是否为字符串验证
            return True  # 暂时允许所有字符串
    
    def _validate_select_value(self, macro_no: str, value: str) -> bool:
        """验证选择框值"""
        options = self._get_select_options(macro_no)
        return value in options
    
    def _validate_switch_value(self, value: str) -> bool:
        """验证开关值"""
        return value.lower() in ['0', '1', 'true', 'false', 'yes', 'no', 'on', 'off']
    
    def get_parameter_display_config(self, macro_no: str, parameter_type: ParameterType) -> Dict[str, Any]:
        """获取参数的显示配置"""
        param_def = self.parameter_definitions.get(macro_no, {})
        
        config = {
            "label": param_def.get('LABEL', macro_no),
            "description": param_def.get('DESCRIPTION', ''),
            "unit": param_def.get('UNIT', ''),
            "format": param_def.get('FORMAT', ''),
            "readonly": parameter_type in [ParameterType.LOAD, ParameterType.RELATION, ParameterType.DEFINE]
        }
        
        return config
    
    def _create_default_result(self, macro_no: str, parameter_type: ParameterType, 
                             raw_value: str) -> Dict[str, Any]:
        """创建默认的处理结果"""
        return {
            "macro_no": macro_no,
            "parameter_type": parameter_type,
            "raw_value": raw_value,
            "display_value": raw_value,
            "is_editable": False,
            "options": [],
            "validation_rules": {}
        }
