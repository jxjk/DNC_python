"""
表单控制器模块
负责表单显示控制和条件评估
"""

import re
from typing import Dict, Any, List, Optional
from src.utils.logger import get_logger


class FormController:
    """表单控制器"""
    
    def __init__(self, config_manager):
        """
        初始化表单控制器
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        self.logger = get_logger("FormController")
        self.relation_config = None
        self.variables = {}  # 存储当前变量值
        
    def load_relation_config(self) -> bool:
        """
        加载关系配置
        
        Returns:
            bool: 加载是否成功
        """
        try:
            self.relation_config = self.config_manager.get_relation_config()
            if self.relation_config:
                self.logger.info(f"成功加载关系配置，共 {len(self.relation_config)} 条规则")
                return True
            else:
                self.logger.warning("关系配置为空或加载失败")
                return False
        except Exception as e:
            self.logger.error(f"关系配置加载失败: {e}")
            return False
    
    def should_display_form(self, form_name: str, current_conditions: Dict[str, Any]) -> bool:
        """
        根据条件判断是否显示表单
        
        Args:
            form_name: 表单名称
            current_conditions: 当前条件变量
            
        Returns:
            bool: 是否显示表单
        """
        if not self.relation_config:
            return True  # 如果没有配置，默认显示
        
        # 更新变量
        self.variables.update(current_conditions)
        
        # 查找与表单相关的规则
        form_rules = []
        for rule in self.relation_config:
            if rule.get('FORM') == form_name:
                form_rules.append(rule)
        
        # 如果没有特定规则，默认显示
        if not form_rules:
            return True
        
        # 评估所有规则
        for rule in form_rules:
            condition = rule.get('CONDITION', '')
            value = rule.get('VALUE', '0')
            
            if condition and not self.evaluate_condition(condition):
                # 条件不满足，根据VALUE值决定行为
                if value == '-1':
                    return False  # 隐藏表单
                elif value == '0':
                    continue     # 继续检查其他规则
                elif value == '1':
                    return True  # 显示表单
        
        # 默认显示
        return True
    
    def evaluate_condition(self, condition_string: str) -> bool:
        """
        评估条件表达式
        
        Args:
            condition_string: 条件表达式字符串
            
        Returns:
            bool: 条件是否满足
        """
        try:
            # 替换变量
            expression = condition_string
            for var_name, var_value in self.variables.items():
                expression = expression.replace(var_name, str(var_value))
            
            # 简单的表达式评估
            # 注意：这里使用eval，实际生产环境应该使用更安全的表达式解析器
            result = eval(expression, {"__builtins__": {}}, {})
            return bool(result)
            
        except Exception as e:
            self.logger.warning(f"条件评估失败: {condition_string}, 错误: {e}")
            return False
    
    def update_variable(self, name: str, value: Any):
        """
        更新变量值
        
        Args:
            name: 变量名
            value: 变量值
        """
        self.variables[name] = value
    
    def get_variables(self) -> Dict[str, Any]:
        """
        获取当前所有变量
        
        Returns:
            Dict[str, Any]: 变量字典
        """
        return self.variables.copy()
