"""
完整工作流集成测试
测试从QR码识别到参数发送的完整流程
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import tempfile

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from dnc_python_project.src.core.application import DNCApplication
from dnc_python_project.src.core.config import ConfigManager
from dnc_python_project.src.business.model_recognizer import ModelRecognizer
from dnc_python_project.src.business.program_matcher import ProgramMatcher
from dnc_python_project.src.business.calculation_engine import CalculationEngine
from dnc_python_project.src.business.relation_validator import RelationValidator
from dnc_python_project.src.communication.nc_protocol import NCProtocol
from dnc_python_project.src.utils.constants import EVENT_TYPES


class TestFullWorkflow(unittest.TestCase):
    """完整工作流集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.app = DNCApplication()
        
        # 创建测试配置文件
        self._create_test_configs()
        
    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir)
        
    def _create_test_configs(self):
        """创建测试配置文件"""
        config_dir = os.path.join(self.temp_dir, "config")
        os.makedirs(config_dir, exist_ok=True)
        
        # 创建ini.csv
        ini_content = """DEFINE,VALUE
BarCodeHeaderStrNum,11
QRmode,0
QRspltStr,@
MODELplc,2
POplc,1
QTYplc,3
OperatorID,OP001
AutoSend,1
"""
        with open(os.path.join(config_dir, "ini.csv"), "w", encoding="utf-8") as f:
            f.write(ini_content)
            
        # 创建type_define.csv
        type_define_content = """NO,TYPE,DEFINE1,DEFINE2
1,C-CCC10,define1-1,define1-2
2,C-CCC20,define2-1,define2-2
3,C-CCC30,define3-1,define3-2
"""
        with open(os.path.join(config_dir, "type_define.csv"), "w", encoding="utf-8") as f:
            f.write(type_define_content)
            
        # 创建type_prg.csv
        type_prg_content = """NO,TYPE,PRG
1,C-CCC10,1001
2,C-CCC20,1002
3,C-CCC30,1003
"""
        with open(os.path.join(config_dir, "type_prg.csv"), "w", encoding="utf-8") as f:
            f.write(type_prg_content)
            
        # 创建load.csv
        load_content = """NO,TYPE,DRAWING,DISPFLG,#500,#501,#502,#503,#504,#505,#506,#507,#508,#509
1,C-CCC10,test1.jpg,1,10,size1,define1-1,define1-2,5,measure1,select1,relation1,switch1,correct1
2,C-CCC20,test2.jpg,1,20,size2,define2-1,define2-2,5,measure2,select2,relation2,switch2,correct2
3,C-CCC30,test3.jpg,1,30,size3,define3-1,define3-2,5,measure3,select3,relation3,switch3,correct3
"""
        with open(os.path.join(config_dir, "load.csv"), "w", encoding="utf-8") as f:
            f.write(load_content)
            
        # 创建define.csv
        define_content = """NO,STR,BEFORE,AFTER,CHNGVL,CALC
1,define1-1,10,20,,,
2,define1-2,20,30,,,
3,define2-1,30,40,,,
4,define2-2,40,50,,,
5,define3-1,50,60,,,
6,define3-2,60,70,,,
"""
        with open(os.path.join(config_dir, "define.csv"), "w", encoding="utf-8") as f:
            f.write(define_content)
            
        # 设置应用配置路径
        self.app.config_manager.set_config_path(config_dir)
        
    @patch('dnc_python_project.src.core.application.QApplication')
    @patch('dnc_python_project.src.core.application.MainWindow')
    def test_complete_workflow_success(self, mock_main_window, mock_qapp):
        """测试完整工作流成功"""
        # 设置mock
        mock_qapp_instance = Mock()
        mock_qapp_instance.exec_.return_value = 0
        mock_qapp.return_value = mock_qapp_instance
        
        mock_main_window_instance = Mock()
        mock_main_window.return_value = mock_main_window_instance
        
        # 初始化应用
        result = self.app.initialize()
        self.assertTrue(result)
        
        # 处理QR码
        qr_code = "PO@C-CCC10-20A-P5-30"
        result = self.app.process_qr_code(qr_code)
        self.assertTrue(result)
        
        # 验证型号识别
        self.assertEqual(self.app.current_model, "C-CCC10")
        
        # 验证程序匹配
        self.assertEqual(self.app.current_program_no, 1)
        
        # 验证参数计算
        self.assertIsNotNone(self.app.current_parameters)
        self.assertIn("#500", self.app.current_parameters)
        self.assertIn("#501", self.app.current_parameters)
        
        # 验证关系验证
        self.assertIsNotNone(self.app.current_validation_results)
        
    @patch('dnc_python_project.src.core.application.QApplication')
    @patch('dnc_python_project.src.core.application.MainWindow')
    def test_workflow_with_invalid_qr_code(self, mock_main_window, mock_qapp):
        """测试无效QR码处理"""
        # 设置mock
        mock_qapp_instance = Mock()
        mock_qapp_instance.exec_.return_value = 0
        mock_qapp.return_value = mock_qapp_instance
        
        mock_main_window_instance = Mock()
        mock_main_window.return_value = mock_main_window_instance
        
        # 初始化应用
        result = self.app.initialize()
        self.assertTrue(result)
        
        # 处理无效QR码
        invalid_qr_code = "INVALID-QR-CODE"
        result = self.app.process_qr_code(invalid_qr_code)
        self.assertFalse(result)
        
        # 验证应用状态
        self.assertIsNone(self.app.current_model)
        self.assertIsNone(self.app.current_program_no)
        self.assertIsNone(self.app.current_parameters)
        
    @patch('dnc_python_project.src.core.application.QApplication')
    @patch('dnc_python_project.src.core.application.MainWindow')
    @patch('dnc_python_project.src.communication.protocol_factory.ProtocolFactory')
    def test_workflow_with_parameter_sending(self, mock_protocol_factory, mock_main_window, mock_qapp):
        """测试包含参数发送的完整工作流"""
        # 设置mock
        mock_qapp_instance = Mock()
        mock_qapp_instance.exec_.return_value = 0
        mock_qapp.return_value = mock_qapp_instance
        
        mock_main_window_instance = Mock()
        mock_main_window.return_value = mock_main_window_instance
        
        mock_protocol_instance = Mock()
        mock_protocol_instance.send_parameters.return_value = True
        mock_protocol_factory.create_protocol.return_value = mock_protocol_instance
        
        # 初始化应用
        result = self.app.initialize()
        self.assertTrue(result)
        
        # 设置通信协议
        self.app.current_protocol = mock_protocol_instance
        
        # 处理QR码
        qr_code = "PO@C-CCC10-20A-P5-30"
        result = self.app.process_qr_code(qr_code)
        self.assertTrue(result)
        
        # 发送参数到NC
        send_result = self.app.send_parameters_to_nc()
        self.assertTrue(send_result)
        
        # 验证参数发送
        mock_protocol_instance.send_parameters.assert_called_once_with(
            self.app.current_parameters
        )
        
    @patch('dnc_python_project.src.core.application.QApplication')
    @patch('dnc_python_project.src.core.application.MainWindow')
    def test_workflow_with_multiple_models(self, mock_main_window, mock_qapp):
        """测试多个型号的处理"""
        # 设置mock
        mock_qapp_instance = Mock()
        mock_qapp_instance.exec_.return_value = 0
        mock_qapp.return_value = mock_qapp_instance
        
        mock_main_window_instance = Mock()
        mock_main_window.return_value = mock_main_window_instance
        
        # 初始化应用
        result = self.app.initialize()
        self.assertTrue(result)
        
        # 测试多个型号
        test_cases = [
            ("PO@C-CCC10-20A-P5-30", "C-CCC10", 1),
            ("PO@C-CCC20-25B-P6-35", "C-CCC20", 2),
            ("PO@C-CCC30-30C-P7-40", "C-CCC30", 3)
        ]
        
        for qr_code, expected_model, expected_program in test_cases:
            with self.subTest(qr_code=qr_code):
                result = self.app.process_qr_code(qr_code)
                self.assertTrue(result)
                self.assertEqual(self.app.current_model, expected_model)
                self.assertEqual(self.app.current_program_no, expected_program)
                
    @patch('dnc_python_project.src.core.application.QApplication')
    @patch('dnc_python_project.src.core.application.MainWindow')
    def test_workflow_with_event_handling(self, mock_main_window, mock_qapp):
        """测试事件处理"""
        # 设置mock
        mock_qapp_instance = Mock()
        mock_qapp_instance.exec_.return_value = 0
        mock_qapp.return_value = mock_qapp_instance
        
        mock_main_window_instance = Mock()
        mock_main_window.return_value = mock_main_window_instance
        
        # 初始化应用
        result = self.app.initialize()
        self.assertTrue(result)
        
        # 设置事件处理器
        event_calls = []
        
        def mock_event_handler(event_type, data):
            event_calls.append((event_type, data))
            
        self.app.event_dispatcher.register_handler(EVENT_TYPES.MODEL_RECOGNIZED, mock_event_handler)
        self.app.event_dispatcher.register_handler(EVENT_TYPES.PROGRAM_MATCHED, mock_event_handler)
        self.app.event_dispatcher.register_handler(EVENT_TYPES.PARAMETERS_CALCULATED, mock_event_handler)
        
        # 处理QR码
        qr_code = "PO@C-CCC10-20A-P5-30"
        result = self.app.process_qr_code(qr_code)
        self.assertTrue(result)
        
        # 验证事件触发
        self.assertGreater(len(event_calls), 0)
        
        # 验证事件类型
        event_types = [call[0] for call in event_calls]
        self.assertIn(EVENT_TYPES.MODEL_RECOGNIZED, event_types)
        self.assertIn(EVENT_TYPES.PROGRAM_MATCHED, event_types)
        self.assertIn(EVENT_TYPES.PARAMETERS_CALCULATED, event_types)
        
    @patch('dnc_python_project.src.core.application.QApplication')
    @patch('dnc_python_project.src.core.application.MainWindow')
    def test_workflow_with_error_recovery(self, mock_main_window, mock_qapp):
        """测试错误恢复"""
        # 设置mock
        mock_qapp_instance = Mock()
        mock_qapp_instance.exec_.return_value = 0
        mock_qapp.return_value = mock_qapp_instance
        
        mock_main_window_instance = Mock()
        mock_main_window.return_value = mock_main_window_instance
        
        # 初始化应用
        result = self.app.initialize()
        self.assertTrue(result)
        
        # 先处理一个有效的QR码
        valid_qr_code = "PO@C-CCC10-20A-P5-30"
        result = self.app.process_qr_code(valid_qr_code)
        self.assertTrue(result)
        
        # 再处理一个无效的QR码
        invalid_qr_code = "INVALID-QR-CODE"
        result = self.app.process_qr_code(invalid_qr_code)
        self.assertFalse(result)
        
        # 验证应用状态没有因为错误而崩溃
        self.assertIsNotNone(self.app.config_manager)
        self.assertIsNotNone(self.app.event_dispatcher)
        self.assertTrue(self.app.is_initialized)
        
        # 再次处理有效的QR码
        result = self.app.process_qr_code(valid_qr_code)
        self.assertTrue(result)
        
    @patch('dnc_python_project.src.core.application.QApplication')
    @patch('dnc_python_project.src.core.application.MainWindow')
    def test_workflow_performance(self, mock_main_window, mock_qapp):
        """测试工作流性能"""
        import time
        
        # 设置mock
        mock_qapp_instance = Mock()
        mock_qapp_instance.exec_.return_value = 0
        mock_qapp.return_value = mock_qapp_instance
        
        mock_main_window_instance = Mock()
        mock_main_window.return_value = mock_main_window_instance
        
        # 初始化应用
        result = self.app.initialize()
        self.assertTrue(result)
        
        # 性能测试
        qr_codes = [
            "PO@C-CCC10-20A-P5-30",
            "PO@C-CCC20-25B-P6-35", 
            "PO@C-CCC30-30C-P7-40"
        ]
        
        start_time = time.time()
        
        for qr_code in qr_codes:
            result = self.app.process_qr_code(qr_code)
            self.assertTrue(result)
            
        end_time = time.time()
        total_time = end_time - start_time
        
        # 验证性能要求（每个QR码处理不超过1秒）
        self.assertLess(total_time, 3.0)  # 3个QR码总共不超过3秒
        
    @patch('dnc_python_project.src.core.application.QApplication')
    @patch('dnc_python_project.src.core.application.MainWindow')
    def test_workflow_with_config_reload(self, mock_main_window, mock_qapp):
        """测试配置重新加载后的工作流"""
        # 设置mock
        mock_qapp_instance = Mock()
        mock_qapp_instance.exec_.return_value = 0
        mock_qapp.return_value = mock_qapp_instance
        
        mock_main_window_instance = Mock()
        mock_main_window.return_value = mock_main_window_instance
        
        # 初始化应用
        result = self.app.initialize()
        self.assertTrue(result)
        
        # 处理QR码
        qr_code = "PO@C-CCC10-20A-P5-30"
        result = self.app.process_qr_code(qr_code)
        self.assertTrue(result)
        
        # 重新加载配置
        reload_result = self.app.config_manager.load_all_configs()
        self.assertTrue(reload_result)
        
        # 再次处理QR码
        result = self.app.process_qr_code(qr_code)
        self.assertTrue(result)
        
        # 验证处理结果一致
        self.assertEqual(self.app.current_model, "C-CCC10")
        self.assertEqual(self.app.current_program_no, 1)


if __name__ == '__main__':
    unittest.main()
