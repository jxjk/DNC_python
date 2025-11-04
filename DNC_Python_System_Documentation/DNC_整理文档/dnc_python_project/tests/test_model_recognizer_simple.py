"""
型号识别器简化测试
只测试核心功能，避免复杂依赖
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)
from src.business.model_recognizer import (
    ModelRecognizer, 
    RecognitionResult
)
from src.business.pattern_recognizer import PatternBasedRecognizer
class TestModelRecognizerSimple:
    """型号识别器简化测试类"""
    
    def test_recognize_model_success(self, model_recognizer):
        """测试成功识别型号"""
        qr_code = "AB123@PO456@10"
        result = model_recognizer.recognize_model(qr_code)
        
        # 检查结果对象结构
        assert hasattr(result, 'qr_code')
        assert hasattr(result, 'model')
        assert hasattr(result, 'po')
        assert hasattr(result, 'quantity')
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'error_message')
        
        # 检查成功条件：没有错误消息
        assert result.error_message is None
        assert result.confidence > 0.0
    
    def test_recognize_model_no_match(self, model_recognizer):
        """测试无匹配型号"""
        qr_code = "INVALIDQRCODE"
        result = model_recognizer.recognize_model(qr_code)
        
        # 检查结果对象结构
        assert hasattr(result, 'qr_code')
        assert hasattr(result, 'model')
        assert hasattr(result, 'po')
        assert hasattr(result, 'quantity')
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'error_message')
        
        # 检查失败条件：有错误消息
        assert result.error_message is not None
        assert result.confidence == 0.0
    
    def test_recognize_model_empty(self, model_recognizer):
        """测试空QR码识别"""
        qr_code = ""
        result = model_recognizer.recognize_model(qr_code)
        
        # 检查结果对象结构
        assert hasattr(result, 'qr_code')
        assert hasattr(result, 'model')
        assert hasattr(result, 'po')
        assert hasattr(result, 'quantity')
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'error_message')
        
        # 检查失败条件：有错误消息
        assert result.error_message is not None
        assert result.confidence == 0.0
    
    def test_batch_recognize(self, model_recognizer):
        """测试批量识别"""
        qr_codes = [
            "AB123@PO456@10",
            "CD789@PO123@5",
            "INVALIDQRCODE"
        ]
        
        results = model_recognizer.batch_recognize(qr_codes)
        
        assert len(results) == 3
        # 检查每个结果都有正确的结构
        for result in results:
            assert hasattr(result, 'qr_code')
            assert hasattr(result, 'model')
            assert hasattr(result, 'po')
            assert hasattr(result, 'quantity')
            assert hasattr(result, 'confidence')
            assert hasattr(result, 'error_message')
    
    def test_get_recognition_statistics(self, model_recognizer):
        """测试获取识别统计信息"""
        # 创建测试结果
        results = [
            RecognitionResult("AB123@PO456@10", "AB123", "PO456", "10", "mode_1", 0.9),
            RecognitionResult("CD789@PO123@5", "CD789", "PO123", "5", "mode_1", 0.8),
            RecognitionResult("INVALID", "", "", "", "error", 0.0, "解析失败")
        ]
        
        stats = model_recognizer.get_recognition_statistics(results)
        
        assert stats["total"] == 3
        assert stats["successful"] == 2
        assert stats["failed"] == 1
        assert stats["success_rate"] == pytest.approx(66.67, 0.01)
        assert stats["average_confidence"] == pytest.approx(0.85, 0.01)


class TestPatternBasedRecognizerSimple:
    """模式识别器简化测试类"""
    
    def test_pattern_based_recognizer_match(self):
        """测试模式匹配"""
        recognizer = PatternBasedRecognizer()
        qr_code = "AB123@PO456@10"
        result = recognizer.recognize(qr_code)
        
        # 检查成功匹配
        assert result is not None
        assert result.model == "AB123"
        assert result.po == "PO456"
        assert result.quantity == "10"
        assert result.confidence == 0.9
    
    def test_pattern_based_recognizer_no_match(self):
        """测试模式无匹配"""
        recognizer = PatternBasedRecognizer()
        qr_code = "INVALIDQRCODE"
        result = recognizer.recognize(qr_code)
        
        # 检查无匹配
        assert result is None
    
    def test_pattern_based_recognizer_with_standard_pattern(self):
        """测试标准模式匹配"""
        recognizer = PatternBasedRecognizer()
        qr_code = "AB123@PO456@10"
        result = recognizer.recognize(qr_code)
        
        # 检查标准模式匹配
        assert result is not None
        assert result.model == "AB123"
        assert result.po == "PO456"
        assert result.quantity == "10"
        assert result.recognition_mode == "pattern_standard"


@pytest.mark.parametrize("qr_code,expected_success", [
    ("AB123@PO456@10", True),
    ("CD789@PO123@5", True),
    ("INVALIDQRCODE", False),
    ("", False),
])
def test_model_recognizer_parametrized(qr_code, expected_success, model_recognizer):
    """参数化测试型号识别器"""
    result = model_recognizer.recognize_model(qr_code)
    
    if expected_success:
        # 成功条件：没有错误消息
        assert result.error_message is None
        assert result.confidence > 0.0
        assert result.model != ""
        assert result.po != ""
        assert result.quantity != ""
    else:
        # 失败条件：有错误消息
        assert result.error_message is not None
        assert result.confidence == 0.0