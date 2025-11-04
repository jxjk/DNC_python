"""
基于模式的识别器
使用正则表达式模式识别QR码中的型号信息
"""

import re
from typing import Optional
from dataclasses import dataclass
from .model_recognizer import RecognitionResult


@dataclass
class PatternMatch:
    """模式匹配结果"""
    model: str
    po: str
    quantity: str
    pattern_type: str
    confidence: float


class PatternBasedRecognizer:
    """基于模式的识别器"""
    
    def __init__(self):
        """初始化模式识别器"""
        self.patterns = [
            {
                "name": "standard",
                "pattern": r'^([A-Z]{2,3}\d+)@([A-Z]{2}\d+)@(\d+)$',
                "model_group": 1,
                "po_group": 2,
                "quantity_group": 3,
                "confidence": 0.9
            },
            {
                "name": "extended",
                "pattern": r'^([A-Z]{3}-\d+)@([A-Z]{2}\d+)@(\d+)$',
                "model_group": 1,
                "po_group": 2,
                "quantity_group": 3,
                "confidence": 0.8
            },
            {
                "name": "simple",
                "pattern": r'^([A-Za-z0-9]+)@([A-Za-z0-9]+)@(\d+)$',
                "model_group": 1,
                "po_group": 2,
                "quantity_group": 3,
                "confidence": 0.7
            }
        ]
    
    def recognize(self, qr_code: str) -> Optional[RecognitionResult]:
        """
        识别QR码
        
        Args:
            qr_code: QR码字符串
            
        Returns:
            Optional[RecognitionResult]: 识别结果，如果不匹配返回None
        """
        if not qr_code:
            return None
            
        for pattern_config in self.patterns:
            match = self._match_pattern(qr_code, pattern_config)
            if match:
                return self._create_recognition_result(qr_code, match)
        
        return None
    
    def _match_pattern(self, qr_code: str, pattern_config: dict) -> Optional[PatternMatch]:
        """
        匹配单个模式
        
        Args:
            qr_code: QR码字符串
            pattern_config: 模式配置
            
        Returns:
            Optional[PatternMatch]: 匹配结果
        """
        pattern = pattern_config["pattern"]
        match = re.match(pattern, qr_code)
        
        if match:
            model = match.group(pattern_config["model_group"])
            po = match.group(pattern_config["po_group"])
            quantity = match.group(pattern_config["quantity_group"])
            
            return PatternMatch(
                model=model,
                po=po,
                quantity=quantity,
                pattern_type=pattern_config["name"],
                confidence=pattern_config["confidence"]
            )
        
        return None
    
    def _create_recognition_result(self, qr_code: str, match: PatternMatch) -> RecognitionResult:
        """
        创建识别结果
        
        Args:
            qr_code: QR码字符串
            match: 模式匹配结果
            
        Returns:
            RecognitionResult: 识别结果
        """
        return RecognitionResult(
            qr_code=qr_code,
            model=match.model,
            po=match.po,
            quantity=match.quantity,
            recognition_mode=f"pattern_{match.pattern_type}",
            confidence=match.confidence
        )
    
    def add_pattern(self, name: str, pattern: str, model_group: int, 
                   po_group: int, quantity_group: int, confidence: float = 0.7):
        """
        添加自定义模式
        
        Args:
            name: 模式名称
            pattern: 正则表达式模式
            model_group: 型号匹配组
            po_group: PO号匹配组
            quantity_group: 数量匹配组
            confidence: 置信度
        """
        self.patterns.append({
            "name": name,
            "pattern": pattern,
            "model_group": model_group,
            "po_group": po_group,
            "quantity_group": quantity_group,
            "confidence": confidence
        })
    
    def get_patterns(self) -> list:
        """
        获取所有模式
        
        Returns:
            list: 模式列表
        """
        return self.patterns.copy()
