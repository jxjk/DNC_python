"""
ON/OFF管理器模块
负责管理ON/OFF状态和switch控件值
"""

import os
import json
from typing import Dict, Any, Optional
from src.utils.logger import get_logger


class OnOffManager:
    """ON/OFF状态管理器"""
    
    def __init__(self, config_manager):
        """
        初始化ON/OFF管理器
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        self.logger = get_logger("OnOffManager")
        self.current_state = 0  # 默认状态
        self.switch_configs = {}  # switch配置
        self.state_file = "onoff_state.json"  # 状态持久化文件
        
    def load_onoff_state(self) -> bool:
        """
        加载ON/OFF状态配置
        
        Returns:
            bool: 加载是否成功
        """
        try:
            # 加载switch配置
            switch_config = self.config_manager.get_switch_config()
            if switch_config:
                self.switch_configs = self._parse_switch_config(switch_config)
                self.logger.info(f"成功加载switch配置，共 {len(self.switch_configs)} 个switch")
            else:
                self.logger.warning("switch配置为空或加载失败")
            
            # 加载持久化状态
            if self._load_persisted_state():
                self.logger.info(f"成功加载持久化状态: {self.current_state}")
            else:
                self.logger.info("使用默认状态: 0")
            
            return True
            
        except Exception as e:
            self.logger.error(f"ON/OFF状态加载失败: {e}")
            return False
    
    def _parse_switch_config(self, switch_config: list) -> Dict[str, Dict[str, Any]]:
        """
        解析switch配置
        
        Args:
            switch_config: switch配置列表
            
        Returns:
            Dict[str, Dict[str, Any]]: 解析后的switch配置字典
        """
        configs = {}
        for item in switch_config:
            name = item.get('NAME', '')
            if name:
                configs[name] = {
                    'display_values': self._parse_display_values(item.get('DISPLAY', '')),
                    'send_values': self._parse_send_values(item.get('SEND', '')),
                    'current_index': 0
                }
        return configs
    
    def _parse_display_values(self, display_str: str) -> list:
        """
        解析显示值
        
        Args:
            display_str: 显示值字符串，格式如 "ON,OFF"
            
        Returns:
            list: 显示值列表
        """
        if not display_str:
            return ["ON", "OFF"]
        return [val.strip() for val in display_str.split(',')]
    
    def _parse_send_values(self, send_str: str) -> list:
        """
        解析发送值
        
        Args:
            send_str: 发送值字符串，格式如 "1,0"
            
        Returns:
            list: 发送值列表
        """
        if not send_str:
            return [1, 0]
        
        values = []
        for val in send_str.split(','):
            try:
                values.append(int(val.strip()))
            except ValueError:
                values.append(0)
        return values
    
    def _load_persisted_state(self) -> bool:
        """
        加载持久化状态
        
        Returns:
            bool: 加载是否成功
        """
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.current_state = data.get('current_state', 0)
                    
                    # 恢复switch状态
                    switch_states = data.get('switch_states', {})
                    for switch_name, state in switch_states.items():
                        if switch_name in self.switch_configs:
                            self.switch_configs[switch_name]['current_index'] = state
                    
                    return True
        except Exception as e:
            self.logger.warning(f"持久化状态加载失败: {e}")
        
        return False
    
    def _save_persisted_state(self) -> bool:
        """
        保存持久化状态
        
        Returns:
            bool: 保存是否成功
        """
        try:
            data = {
                'current_state': self.current_state,
                'switch_states': {
                    name: config['current_index'] 
                    for name, config in self.switch_configs.items()
                }
            }
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            self.logger.warning(f"持久化状态保存失败: {e}")
            return False
    
    def get_current_state(self) -> int:
        """
        获取当前ON/OFF状态
        
        Returns:
            int: 当前状态值
        """
        return self.current_state
    
    def update_onoff_state(self, new_state: int) -> bool:
        """
        更新ON/OFF状态
        
        Args:
            new_state: 新状态值
            
        Returns:
            bool: 更新是否成功
        """
        try:
            old_state = self.current_state
            self.current_state = new_state
            
            # 保存状态
            self._save_persisted_state()
            
            self.logger.info(f"ON/OFF状态已更新: {old_state} -> {new_state}")
            return True
            
        except Exception as e:
            self.logger.error(f"ON/OFF状态更新失败: {e}")
            return False
    
    def cycle_next_state(self) -> bool:
        """
        循环到下一个状态
        
        Returns:
            bool: 循环是否成功
        """
        try:
            # 简单的状态循环：0 -> 1 -> 0
            new_state = 1 if self.current_state == 0 else 0
            return self.update_onoff_state(new_state)
            
        except Exception as e:
            self.logger.error(f"状态循环失败: {e}")
            return False
    
    def get_switch_values(self, switch_name: str) -> Dict[str, Any]:
        """
        获取switch控件的值
        
        Args:
            switch_name: switch名称
            
        Returns:
            Dict[str, Any]: 包含显示值和发送值的字典
        """
        if switch_name not in self.switch_configs:
            return {
                'display_value': '未知',
                'send_value': 0,
                'current_index': 0
            }
        
        config = self.switch_configs[switch_name]
        current_index = config['current_index']
        display_values = config['display_values']
        send_values = config['send_values']
        
        # 确保索引在有效范围内
        if current_index >= len(display_values):
            current_index = 0
        if current_index >= len(send_values):
            current_index = 0
        
        return {
            'display_value': display_values[current_index],
            'send_value': send_values[current_index],
            'current_index': current_index
        }
    
    def cycle_switch_state(self, switch_name: str) -> bool:
        """
        循环switch状态
        
        Args:
            switch_name: switch名称
            
        Returns:
            bool: 循环是否成功
        """
        if switch_name not in self.switch_configs:
            self.logger.warning(f"未知的switch: {switch_name}")
            return False
        
        try:
            config = self.switch_configs[switch_name]
            current_index = config['current_index']
            display_values = config['display_values']
            
            # 循环到下一个状态
            new_index = (current_index + 1) % len(display_values)
            config['current_index'] = new_index
            
            # 保存状态
            self._save_persisted_state()
            
            self.logger.info(f"switch {switch_name} 状态已更新: {current_index} -> {new_index}")
            return True
            
        except Exception as e:
            self.logger.error(f"switch状态循环失败: {e}")
            return False
    
    def set_switch_state(self, switch_name: str, state_index: int) -> bool:
        """
        设置switch状态
        
        Args:
            switch_name: switch名称
            state_index: 状态索引
            
        Returns:
            bool: 设置是否成功
        """
        if switch_name not in self.switch_configs:
            self.logger.warning(f"未知的switch: {switch_name}")
            return False
        
        try:
            config = self.switch_configs[switch_name]
            display_values = config['display_values']
            
            # 验证状态索引
            if state_index < 0 or state_index >= len(display_values):
                self.logger.warning(f"无效的状态索引: {state_index}")
                return False
            
            old_index = config['current_index']
            config['current_index'] = state_index
            
            # 保存状态
            self._save_persisted_state()
            
            self.logger.info(f"switch {switch_name} 状态已设置: {old_index} -> {state_index}")
            return True
            
        except Exception as e:
            self.logger.error(f"switch状态设置失败: {e}")
            return False
