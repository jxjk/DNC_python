"""
核心模块单元测试
包含EventDispatcher、EventManager及相关事件类的测试
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from dnc_python_project.src.core.event_dispatcher import (
    EventDispatcher, EventManager, 
    ModelRecognizedEvent, ProgramMatchedEvent, ParametersCalculatedEvent,
    NCCommunicationEvent, ErrorEvent
)
from dnc_python_project.src.utils.constants import EVENT_TYPES


class TestEventClasses(unittest.TestCase):
    """事件类测试"""
    
    def test_model_recognized_event(self):
        """测试模型识别事件"""
        event = ModelRecognizedEvent(
            qr_code="QR123456",
            model="TEST-MODEL",
            po="PO001",
            quantity="100",
            recognition_mode="auto"
        )
        
        self.assertEqual(event.qr_code, "QR123456")
        self.assertEqual(event.model, "TEST-MODEL")
        self.assertEqual(event.po, "PO001")
        self.assertEqual(event.quantity, "100")
        self.assertEqual(event.recognition_mode, "auto")
        
    def test_program_matched_event(self):
        """测试程序匹配事件"""
        event = ProgramMatchedEvent(
            model="TEST-MODEL",
            program_no=1,
            matched_string="TEST-MODEL",
            match_type="exact"
        )
        
        self.assertEqual(event.model, "TEST-MODEL")
        self.assertEqual(event.program_no, 1)
        self.assertEqual(event.matched_string, "TEST-MODEL")
        self.assertEqual(event.match_type, "exact")
        
    def test_parameters_calculated_event(self):
        """测试参数计算事件"""
        parameters = {'#500': '10', '#501': '20'}
        calculation_steps = [
            {'step': 1, 'description': '计算参数#500', 'result': '10'},
            {'step': 2, 'description': '计算参数#501', 'result': '20'}
        ]
        
        event = ParametersCalculatedEvent(
            program_no=1,
            parameters=parameters,
            calculation_steps=calculation_steps
        )
        
        self.assertEqual(event.program_no, 1)
        self.assertEqual(event.parameters, parameters)
        self.assertEqual(event.calculation_steps, calculation_steps)
        
    def test_nc_communication_event(self):
        """测试NC通信事件"""
        device_info = {'device_id': 'NC001', 'status': 'connected'}
        event = NCCommunicationEvent(
            status="success",
            message="参数发送成功",
            device_info=device_info
        )
        
        self.assertEqual(event.status, "success")
        self.assertEqual(event.message, "参数发送成功")
        self.assertEqual(event.device_info, device_info)
        
    def test_error_event(self):
        """测试错误事件"""
        details = {'file': 'config.ini', 'line': 25}
        event = ErrorEvent(
            error_type="config_error",
            message="配置文件格式错误",
            details=details
        )
        
        self.assertEqual(event.error_type, "config_error")
        self.assertEqual(event.message, "配置文件格式错误")
        self.assertEqual(event.details, details)


class TestEventDispatcher(unittest.TestCase):
    """EventDispatcher类测试"""
    
    def setUp(self):
        """测试前准备"""
        self.dispatcher = EventDispatcher()
        self.mock_handler1 = Mock()
        self.mock_handler2 = Mock()
        
    def test_initialization(self):
        """测试初始化"""
        self.assertIsInstance(self.dispatcher, EventDispatcher)
        self.assertEqual(len(self.dispatcher._handlers), 0)
        
    def test_subscribe_success(self):
        """测试成功订阅事件"""
        # 订阅事件
        self.dispatcher.subscribe(EVENT_TYPES.MODEL_RECOGNIZED, self.mock_handler1)
        self.dispatcher.subscribe(EVENT_TYPES.MODEL_RECOGNIZED, self.mock_handler2)
        
        # 验证订阅
        handlers = self.dispatcher._handlers.get(EVENT_TYPES.MODEL_RECOGNIZED, [])
        self.assertEqual(len(handlers), 2)
        self.assertIn(self.mock_handler1, handlers)
        self.assertIn(self.mock_handler2, handlers)
        
    def test_unsubscribe_success(self):
        """测试成功取消订阅"""
        # 先订阅
        self.dispatcher.subscribe(EVENT_TYPES.MODEL_RECOGNIZED, self.mock_handler1)
        self.dispatcher.subscribe(EVENT_TYPES.MODEL_RECOGNIZED, self.mock_handler2)
        
        # 取消订阅
        self.dispatcher.unsubscribe(EVENT_TYPES.MODEL_RECOGNIZED, self.mock_handler1)
        
        # 验证取消订阅
        handlers = self.dispatcher._handlers.get(EVENT_TYPES.MODEL_RECOGNIZED, [])
        self.assertEqual(len(handlers), 1)
        self.assertNotIn(self.mock_handler1, handlers)
        self.assertIn(self.mock_handler2, handlers)
        
    def test_unsubscribe_nonexistent_handler(self):
        """测试取消订阅不存在的处理器"""
        # 取消订阅不存在的处理器
        self.dispatcher.unsubscribe(EVENT_TYPES.MODEL_RECOGNIZED, self.mock_handler1)
        
        # 验证没有错误发生
        handlers = self.dispatcher._handlers.get(EVENT_TYPES.MODEL_RECOGNIZED, [])
        self.assertEqual(len(handlers), 0)
        
    def test_clear_subscriptions_specific_event(self):
        """测试清除特定事件的所有订阅"""
        # 订阅多个事件
        self.dispatcher.subscribe(EVENT_TYPES.MODEL_RECOGNIZED, self.mock_handler1)
        self.dispatcher.subscribe(EVENT_TYPES.MODEL_RECOGNIZED, self.mock_handler2)
        self.dispatcher.subscribe(EVENT_TYPES.PROGRAM_MATCHED, self.mock_handler1)
        
        # 清除特定事件的订阅
        self.dispatcher.clear_subscriptions(EVENT_TYPES.MODEL_RECOGNIZED)
        
        # 验证清除结果
        model_handlers = self.dispatcher._handlers.get(EVENT_TYPES.MODEL_RECOGNIZED, [])
        program_handlers = self.dispatcher._handlers.get(EVENT_TYPES.PROGRAM_MATCHED, [])
        
        self.assertEqual(len(model_handlers), 0)
        self.assertEqual(len(program_handlers), 1)
        
    def test_clear_all_subscriptions(self):
        """测试清除所有订阅"""
        # 订阅多个事件
        self.dispatcher.subscribe(EVENT_TYPES.MODEL_RECOGNIZED, self.mock_handler1)
        self.dispatcher.subscribe(EVENT_TYPES.PROGRAM_MATCHED, self.mock_handler2)
        
        # 清除所有订阅
        self.dispatcher.clear_subscriptions()
        
        # 验证所有订阅都被清除
        self.assertEqual(len(self.dispatcher._handlers), 0)
        
    def test_publish_model_recognized(self):
        """测试发布模型识别事件"""
        # 订阅事件
        self.dispatcher.subscribe(EVENT_TYPES.MODEL_RECOGNIZED, self.mock_handler1)
        
        # 发布事件
        self.dispatcher.publish_model_recognized(
            qr_code="QR123456",
            model="TEST-MODEL",
            po="PO001",
            quantity="100",
            recognition_mode="auto"
        )
        
        # 验证处理器被调用
        self.mock_handler1.assert_called_once()
        event = self.mock_handler1.call_args[0][0]
        self.assertIsInstance(event, ModelRecognizedEvent)
        self.assertEqual(event.qr_code, "QR123456")
        self.assertEqual(event.model, "TEST-MODEL")
        
    def test_publish_program_matched(self):
        """测试发布程序匹配事件"""
        # 订阅事件
        self.dispatcher.subscribe(EVENT_TYPES.PROGRAM_MATCHED, self.mock_handler1)
        
        # 发布事件
        self.dispatcher.publish_program_matched(
            model="TEST-MODEL",
            program_no=1,
            matched_string="TEST-MODEL",
            match_type="exact"
        )
        
        # 验证处理器被调用
        self.mock_handler1.assert_called_once()
        event = self.mock_handler1.call_args[0][0]
        self.assertIsInstance(event, ProgramMatchedEvent)
        self.assertEqual(event.model, "TEST-MODEL")
        self.assertEqual(event.program_no, 1)
        
    def test_publish_parameters_calculated(self):
        """测试发布参数计算事件"""
        # 订阅事件
        self.dispatcher.subscribe(EVENT_TYPES.PARAMETERS_CALCULATED, self.mock_handler1)
        
        parameters = {'#500': '10', '#501': '20'}
        calculation_steps = [
            {'step': 1, 'description': '计算参数#500', 'result': '10'}
        ]
        
        # 发布事件
        self.dispatcher.publish_parameters_calculated(
            program_no=1,
            parameters=parameters,
            calculation_steps=calculation_steps
        )
        
        # 验证处理器被调用
        self.mock_handler1.assert_called_once()
        event = self.mock_handler1.call_args[0][0]
        self.assertIsInstance(event, ParametersCalculatedEvent)
        self.assertEqual(event.program_no, 1)
        self.assertEqual(event.parameters, parameters)
        
    def test_publish_nc_communication_status(self):
        """测试发布NC通信状态事件"""
        # 订阅事件
        self.dispatcher.subscribe(EVENT_TYPES.NC_COMMUNICATION_STATUS, self.mock_handler1)
        
        device_info = {'device_id': 'NC001', 'status': 'connected'}
        
        # 发布事件
        self.dispatcher.publish_nc_communication_status(
            status="success",
            message="参数发送成功",
            device_info=device_info
        )
        
        # 验证处理器被调用
        self.mock_handler1.assert_called_once()
        event = self.mock_handler1.call_args[0][0]
        self.assertIsInstance(event, NCCommunicationEvent)
        self.assertEqual(event.status, "success")
        self.assertEqual(event.message, "参数发送成功")
        
    def test_publish_error(self):
        """测试发布错误事件"""
        # 订阅事件
        self.dispatcher.subscribe(EVENT_TYPES.ERROR_OCCURRED, self.mock_handler1)
        
        details = {'file': 'config.ini', 'line': 25}
        
        # 发布事件
        self.dispatcher.publish_error(
            error_type="config_error",
            message="配置文件格式错误",
            details=details
        )
        
        # 验证处理器被调用
        self.mock_handler1.assert_called_once()
        event = self.mock_handler1.call_args[0][0]
        self.assertIsInstance(event, ErrorEvent)
        self.assertEqual(event.error_type, "config_error")
        self.assertEqual(event.message, "配置文件格式错误")
        
    def test_publish_system_started(self):
        """测试发布系统启动事件"""
        # 订阅事件
        self.dispatcher.subscribe(EVENT_TYPES.SYSTEM_STARTED, self.mock_handler1)
        
        # 发布事件
        self.dispatcher.publish_system_started()
        
        # 验证处理器被调用
        self.mock_handler1.assert_called_once()
        
    def test_publish_system_shutdown(self):
        """测试发布系统关闭事件"""
        # 订阅事件
        self.dispatcher.subscribe(EVENT_TYPES.SYSTEM_SHUTDOWN, self.mock_handler1)
        
        # 发布事件
        self.dispatcher.publish_system_shutdown()
        
        # 验证处理器被调用
        self.mock_handler1.assert_called_once()
        
    def test_publish_config_changed(self):
        """测试发布配置变更事件"""
        # 订阅事件
        self.dispatcher.subscribe(EVENT_TYPES.CONFIG_CHANGED, self.mock_handler1)
        
        # 发布事件
        self.dispatcher.publish_config_changed("ui_config")
        
        # 验证处理器被调用
        self.mock_handler1.assert_called_once()
        
    def test_publish_ui_control_created(self):
        """测试发布UI控件创建事件"""
        # 订阅事件
        self.dispatcher.subscribe(EVENT_TYPES.UI_CONTROL_CREATED, self.mock_handler1)
        
        mock_control = Mock()
        
        # 发布事件
        self.dispatcher.publish_ui_control_created("parameter_widget", mock_control)
        
        # 验证处理器被调用
        self.mock_handler1.assert_called_once()
        
    def test_multiple_handlers_for_same_event(self):
        """测试同一事件的多个处理器"""
        # 订阅多个处理器
        self.dispatcher.subscribe(EVENT_TYPES.MODEL_RECOGNIZED, self.mock_handler1)
        self.dispatcher.subscribe(EVENT_TYPES.MODEL_RECOGNIZED, self.mock_handler2)
        
        # 发布事件
        self.dispatcher.publish_model_recognized(
            qr_code="QR123456",
            model="TEST-MODEL",
            po="PO001",
            quantity="100",
            recognition_mode="auto"
        )
        
        # 验证所有处理器都被调用
        self.mock_handler1.assert_called_once()
        self.mock_handler2.assert_called_once()
        
    def test_no_handlers_for_event(self):
        """测试没有处理器的事件发布"""
        # 发布事件（没有订阅任何处理器）
        try:
            self.dispatcher.publish_model_recognized(
                qr_code="QR123456",
                model="TEST-MODEL",
                po="PO001",
                quantity="100",
                recognition_mode="auto"
            )
            # 应该不会抛出异常
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"发布事件时不应该抛出异常: {e}")


class TestEventManager(unittest.TestCase):
    """EventManager类测试"""
    
    def setUp(self):
        """测试前准备"""
        # 重置单例实例
        EventManager._instance = None
        
    def test_singleton_pattern(self):
        """测试单例模式"""
        manager1 = EventManager()
        manager2 = EventManager()
        
        self.assertIs(manager1, manager2)
        
    def test_get_dispatcher_default(self):
        """测试获取默认事件分发器"""
        manager = EventManager()
        dispatcher = manager.get_dispatcher()
        
        self.assertIsInstance(dispatcher, EventDispatcher)
        
    def test_set_dispatcher(self):
        """测试设置自定义事件分发器"""
        manager = EventManager()
        custom_dispatcher = EventDispatcher()
        
        manager.set_dispatcher(custom_dispatcher)
        retrieved_dispatcher = manager.get_dispatcher()
        
        self.assertIs(retrieved_dispatcher, custom_dispatcher)
        
    def test_get_dispatcher_after_set(self):
        """测试设置后获取事件分发器"""
        manager = EventManager()
        custom_dispatcher = EventDispatcher()
        
        manager.set_dispatcher(custom_dispatcher)
        retrieved_dispatcher = manager.get_dispatcher()
        
        self.assertIs(retrieved_dispatcher, custom_dispatcher)
        self.assertIsNot(retrieved_dispatcher, EventDispatcher())


class TestEventIntegration(unittest.TestCase):
    """事件集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.dispatcher = EventDispatcher()
        self.handler_calls = []
        
    def event_handler(self, event):
        """测试事件处理器"""
        self.handler_calls.append(event)
        
    def test_event_chain(self):
        """测试事件链"""
        # 订阅多个事件
        self.dispatcher.subscribe(EVENT_TYPES.MODEL_RECOGNIZED, self.event_handler)
        self.dispatcher.subscribe(EVENT_TYPES.PROGRAM_MATCHED, self.event_handler)
        self.dispatcher.subscribe(EVENT_TYPES.PARAMETERS_CALCULATED, self.event_handler)
        
        # 发布一系列事件
        self.dispatcher.publish_model_recognized(
            qr_code="QR123456",
            model="TEST-MODEL",
            po="PO001",
            quantity="100",
            recognition_mode="auto"
        )
        
        self.dispatcher.publish_program_matched(
            model="TEST-MODEL",
            program_no=1,
            matched_string="TEST-MODEL",
            match_type="exact"
        )
        
        parameters = {'#500': '10', '#501': '20'}
        calculation_steps = [{'step': 1, 'description': '计算参数#500', 'result': '10'}]
        
        self.dispatcher.publish_parameters_calculated(
            program_no=1,
            parameters=parameters,
            calculation_steps=calculation_steps
        )
        
        # 验证所有事件都被处理
        self.assertEqual(len(self.handler_calls), 3)
        self.assertIsInstance(self.handler_calls[0], ModelRecognizedEvent)
        self.assertIsInstance(self.handler_calls[1], ProgramMatchedEvent)
        self.assertIsInstance(self.handler_calls[2], ParametersCalculatedEvent)


if __name__ == '__main__':
    unittest.main()
