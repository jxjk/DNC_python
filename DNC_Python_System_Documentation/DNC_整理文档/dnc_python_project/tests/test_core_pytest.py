"""
核心模块pytest测试
使用pytest框架测试所有核心功能
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from src.core.application import DNCApplication
from src.core.config import ConfigManager
from src.core.event_dispatcher import EventDispatcher


class TestConfigManagerPytest:
    """配置管理器pytest测试"""

    def test_config_manager_initialization(self):
        """测试配置管理器初始化"""
        config = ConfigManager()
        assert config is not None
        assert hasattr(config, 'system_config')
        assert hasattr(config, 'ui_config')
        assert hasattr(config, 'communication_config')

    def test_get_set_config(self):
        """测试获取和设置配置"""
        config = ConfigManager()
        
        # 测试设置配置
        config.set('test_key', 'test_value')
        
        # 测试获取配置
        value = config.get('test_key')
        assert value == 'test_value'

    def test_get_nonexistent_config(self):
        """测试获取不存在的配置"""
        config = ConfigManager()
        value = config.get('nonexistent_key')
        assert value is None

    def test_save_load_config(self, tmp_path):
        """测试保存和加载配置"""
        config_file = tmp_path / "test_config.json"
        
        config = ConfigManager()
        config.set('test_key', 'test_value')
        
        # 测试保存配置
        result = config.save_config(str(config_file))
        assert result is True
        assert config_file.exists()
        
        # 测试加载配置
        new_config = ConfigManager()
        result = new_config.load_config(str(config_file))
        assert result is True
        assert new_config.get('test_key') == 'test_value'

    def test_load_nonexistent_config(self):
        """测试加载不存在的配置文件"""
        config = ConfigManager()
        result = config.load_config('nonexistent_file.json')
        assert result is False

    def test_get_all_config(self):
        """测试获取所有配置"""
        config = ConfigManager()
        all_config = config.get_all_config()
        
        assert isinstance(all_config, dict)
        assert 'system' in all_config
        assert 'ui' in all_config
        assert 'communication' in all_config

    def test_update_config(self):
        """测试更新配置"""
        config = ConfigManager()
        
        # 更新系统配置
        new_system_config = {
            'name': 'DNC系统',
            'version': '2.0.0',
            'debug': True
        }
        
        result = config.update_config('system', new_system_config)
        assert result is True
        
        # 验证更新
        system_config = config.get('system')
        assert system_config['name'] == 'DNC系统'
        assert system_config['version'] == '2.0.0'
        assert system_config['debug'] is True

    def test_update_nonexistent_section(self):
        """测试更新不存在的配置节"""
        config = ConfigManager()
        result = config.update_config('nonexistent_section', {})
        assert result is False

    def test_reset_config(self):
        """测试重置配置"""
        config = ConfigManager()
        
        # 修改配置
        config.set('test_key', 'test_value')
        
        # 重置配置
        result = config.reset_config()
        assert result is True
        
        # 验证配置已重置
        value = config.get('test_key')
        assert value is None

    @pytest.mark.parametrize("section,key,expected_type", [
        ("system", "name", str),
        ("system", "version", str),
        ("system", "debug", bool),
        ("ui", "theme", str),
        ("ui", "language", str),
        ("communication", "protocol", str),
        ("communication", "timeout", int),
    ])
    def test_config_types(self, section, key, expected_type):
        """测试配置项类型"""
        config = ConfigManager()
        section_config = config.get(section)
        
        if section_config and key in section_config:
            value = section_config[key]
            assert isinstance(value, expected_type), f"{section}.{key} 应该是 {expected_type} 类型"


class TestEventDispatcherPytest:
    """事件分发器pytest测试"""

    def test_event_dispatcher_initialization(self):
        """测试事件分发器初始化"""
        dispatcher = EventDispatcher()
        assert dispatcher is not None
        assert hasattr(dispatcher, '_listeners')

    def test_register_event(self):
        """测试注册事件"""
        dispatcher = EventDispatcher()
        
        def test_callback(data):
            pass
        
        result = dispatcher.register('test_event', test_callback)
        assert result is True
        assert 'test_event' in dispatcher._listeners
        assert test_callback in dispatcher._listeners['test_event']

    def test_register_multiple_callbacks(self):
        """测试注册多个回调函数"""
        dispatcher = EventDispatcher()
        
        def callback1(data):
            pass
        
        def callback2(data):
            pass
        
        dispatcher.register('test_event', callback1)
        dispatcher.register('test_event', callback2)
        
        assert len(dispatcher._listeners['test_event']) == 2
        assert callback1 in dispatcher._listeners['test_event']
        assert callback2 in dispatcher._listeners['test_event']

    def test_emit_event(self):
        """测试触发事件"""
        dispatcher = EventDispatcher()
        callback_called = False
        callback_data = None
        
        def test_callback(data):
            nonlocal callback_called, callback_data
            callback_called = True
            callback_data = data
        
        dispatcher.register('test_event', test_callback)
        
        test_data = {'key': 'value'}
        dispatcher.emit('test_event', test_data)
        
        assert callback_called is True
        assert callback_data == test_data

    def test_emit_event_multiple_callbacks(self):
        """测试触发事件（多个回调函数）"""
        dispatcher = EventDispatcher()
        call_count = 0
        
        def callback1(data):
            nonlocal call_count
            call_count += 1
        
        def callback2(data):
            nonlocal call_count
            call_count += 1
        
        dispatcher.register('test_event', callback1)
        dispatcher.register('test_event', callback2)
        
        dispatcher.emit('test_event', {})
        
        assert call_count == 2

    def test_emit_nonexistent_event(self):
        """测试触发不存在的事件"""
        dispatcher = EventDispatcher()
        
        # 不应该抛出异常
        dispatcher.emit('nonexistent_event', {})

    def test_unregister_event(self):
        """测试注销事件"""
        dispatcher = EventDispatcher()
        
        def test_callback(data):
            pass
        
        dispatcher.register('test_event', test_callback)
        assert test_callback in dispatcher._listeners['test_event']
        
        result = dispatcher.unregister('test_event', test_callback)
        assert result is True
        assert test_callback not in dispatcher._listeners['test_event']

    def test_unregister_nonexistent_event(self):
        """测试注销不存在的事件"""
        dispatcher = EventDispatcher()
        
        def test_callback(data):
            pass
        
        result = dispatcher.unregister('nonexistent_event', test_callback)
        assert result is False

    def test_unregister_nonexistent_callback(self):
        """测试注销不存在的回调函数"""
        dispatcher = EventDispatcher()
        
        def callback1(data):
            pass
        
        def callback2(data):
            pass
        
        dispatcher.register('test_event', callback1)
        result = dispatcher.unregister('test_event', callback2)
        assert result is False

    def test_clear_events(self):
        """测试清除所有事件"""
        dispatcher = EventDispatcher()
        
        def callback1(data):
            pass
        
        def callback2(data):
            pass
        
        dispatcher.register('event1', callback1)
        dispatcher.register('event2', callback2)
        
        assert len(dispatcher._listeners) == 2
        
        dispatcher.clear_events()
        
        assert len(dispatcher._listeners) == 0

    def test_get_registered_events(self):
        """测试获取已注册的事件"""
        dispatcher = EventDispatcher()
        
        def callback1(data):
            pass
        
        def callback2(data):
            pass
        
        dispatcher.register('event1', callback1)
        dispatcher.register('event2', callback2)
        
        events = dispatcher.get_registered_events()
        
        assert 'event1' in events
        assert 'event2' in events
        assert len(events) == 2

    def test_get_listeners_count(self):
        """测试获取监听器数量"""
        dispatcher = EventDispatcher()
        
        def callback1(data):
            pass
        
        def callback2(data):
            pass
        
        dispatcher.register('test_event', callback1)
        dispatcher.register('test_event', callback2)
        
        count = dispatcher.get_listeners_count('test_event')
        assert count == 2

    def test_get_listeners_count_nonexistent_event(self):
        """测试获取不存在事件的监听器数量"""
        dispatcher = EventDispatcher()
        count = dispatcher.get_listeners_count('nonexistent_event')
        assert count == 0


class TestDNCApplicationPytest:
    """DNC应用程序pytest测试"""

    def test_application_initialization(self):
        """测试应用程序初始化"""
        app = DNCApplication()
        assert app is not None
        assert hasattr(app, 'config_manager')
        assert hasattr(app, 'event_dispatcher')
        assert hasattr(app, 'model_recognizer')
        assert hasattr(app, 'program_matcher')
        assert hasattr(app, 'calculation_engine')
        assert hasattr(app, 'nc_communicator')

    def test_application_start_stop(self):
        """测试应用程序启动和停止"""
        app = DNCApplication()
        
        # 测试启动
        result = app.start()
        assert result is True
        assert app.is_running is True
        
        # 测试停止
        result = app.stop()
        assert result is True
        assert app.is_running is False

    def test_application_double_start(self):
        """测试重复启动应用程序"""
        app = DNCApplication()
        
        # 第一次启动
        result1 = app.start()
        assert result1 is True
        
        # 第二次启动
        result2 = app.start()
        assert result2 is False  # 应该返回False，因为已经在运行

    def test_application_double_stop(self):
        """测试重复停止应用程序"""
        app = DNCApplication()
        
        # 启动应用程序
        app.start()
        
        # 第一次停止
        result1 = app.stop()
        assert result1 is True
        
        # 第二次停止
        result2 = app.stop()
        assert result2 is False  # 应该返回False，因为已经停止

    @patch('src.core.application.MainWindow')
    def test_show_main_window(self, mock_main_window):
        """测试显示主窗口"""
        app = DNCApplication()
        
        # 启动应用程序
        app.start()
        
        # 测试显示主窗口
        result = app.show_main_window()
        assert result is True
        mock_main_window.assert_called_once()

    def test_show_main_window_not_running(self):
        """测试未运行时显示主窗口"""
        app = DNCApplication()
        
        # 不启动应用程序，直接显示主窗口
        result = app.show_main_window()
        assert result is False

    def test_get_application_status(self):
        """测试获取应用程序状态"""
        app = DNCApplication()
        
        status = app.get_application_status()
        
        assert isinstance(status, dict)
        assert 'running' in status
        assert 'components' in status
        assert 'start_time' in status
        
        # 验证组件状态
        components = status['components']
        assert 'config_manager' in components
        assert 'event_dispatcher' in components
        assert 'model_recognizer' in components
        assert 'program_matcher' in components
        assert 'calculation_engine' in components
        assert 'nc_communicator' in components

    def test_handle_system_event(self):
        """测试处理系统事件"""
        app = DNCApplication()
        
        # 注册事件监听器
        event_received = False
        event_data = None
        
        def event_handler(data):
            nonlocal event_received, event_data
            event_received = True
            event_data = data
        
        app.event_dispatcher.register('system_event', event_handler)
        
        # 触发系统事件
        test_data = {'action': 'test'}
        app._handle_system_event(test_data)
        
        assert event_received is True
        assert event_data == test_data

    def test_application_restart(self):
        """测试应用程序重启"""
        app = DNCApplication()
        
        # 启动应用程序
        app.start()
        assert app.is_running is True
        
        # 重启应用程序
        result = app.restart()
        assert result is True
        assert app.is_running is True

    def test_application_restart_from_stopped(self):
        """测试从停止状态重启应用程序"""
        app = DNCApplication()
        
        # 应用程序未启动，直接重启
        result = app.restart()
        assert result is True
        assert app.is_running is True

    @pytest.mark.parametrize("component_name", [
        "config_manager",
        "event_dispatcher", 
        "model_recognizer",
        "program_matcher",
        "calculation_engine",
        "nc_communicator"
    ])
    def test_application_components(self, component_name):
        """测试应用程序组件"""
        app = DNCApplication()
        
        component = getattr(app, component_name)
        assert component is not None

    def test_application_error_handling(self):
        """测试应用程序错误处理"""
        app = DNCApplication()
        
        # 模拟组件初始化失败
        with patch.object(app, '_initialize_components') as mock_init:
            mock_init.side_effect = Exception("初始化失败")
            
            # 应该能够处理异常
            result = app.start()
            assert result is False
            assert app.is_running is False


if __name__ == '__main__':
    pytest.main([__file__])
