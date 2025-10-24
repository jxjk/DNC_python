"""
型号识别器
负责QR码解析和型号识别
"""

import logging
import re
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass

from ..core.config import ConfigManager


@dataclass
class RecognitionResult:
    """识别结果"""
    qr_code: str
    model: str
    po: str
    quantity: str
    recognition_mode: str
    confidence: float
    error_message: Optional[str] = None


class ModelRecognizer:
    """型号识别器"""
    
    def __init__(self, config_manager: ConfigManager):
        """
        初始化型号识别器
        
        Args:
            config_manager: 配置管理器
        """
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        
    def recognize_model(self, qr_code: str) -> RecognitionResult:
        """
        识别型号
        
        Args:
            qr_code: QR码字符串
            
        Returns:
            RecognitionResult: 识别结果
        """
        try:
            self.logger.info(f"开始识别QR码: {qr_code}")
            
            # 获取QR码配置
            qr_config = self.config_manager.qr_config
            
            # 根据QR模式进行识别
            if qr_config.qr_mode == 0:
                # 模式0：直接解析
                result = self._parse_qr_mode_0(qr_code, qr_config)
            elif qr_config.qr_mode == 1:
                # 模式1：分隔符解析
                result = self._parse_qr_mode_1(qr_code, qr_config)
            else:
                result = RecognitionResult(
                    qr_code=qr_code,
                    model="",
                    po="",
                    quantity="",
                    recognition_mode="unknown",
                    confidence=0.0,
                    error_message=f"不支持的QR模式: {qr_config.qr_mode}"
                )
            
            # 验证识别结果
            if result.error_message is None:
                validation_result = self._validate_recognition_result(result)
                if not validation_result["valid"]:
                    result.error_message = validation_result["message"]
                    result.confidence = 0.0
            
            self.logger.info(f"型号识别完成: {result.model}, 置信度: {result.confidence}")
            return result
            
        except Exception as e:
            self.logger.error(f"型号识别失败: {e}")
            return RecognitionResult(
                qr_code=qr_code,
                model="",
                po="",
                quantity="",
                recognition_mode="error",
                confidence=0.0,
                error_message=str(e)
            )
    
    def _parse_qr_mode_0(self, qr_code: str, qr_config: Any) -> RecognitionResult:
        """
        解析QR模式0
        
        Args:
            qr_code: QR码字符串
            qr_config: QR码配置
            
        Returns:
            RecognitionResult: 识别结果
        """
        # 模式0：直接解析，假设QR码格式为固定长度
        try:
            # 根据配置的位置信息提取数据
            model = self._extract_by_position(qr_code, qr_config.model_place)
            po = self._extract_by_position(qr_code, qr_config.po_place)
            quantity = self._extract_by_position(qr_code, qr_config.qty_place)
            
            confidence = self._calculate_confidence(qr_code, model, po, quantity)
            
            return RecognitionResult(
                qr_code=qr_code,
                model=model,
                po=po,
                quantity=quantity,
                recognition_mode="mode_0",
                confidence=confidence
            )
            
        except Exception as e:
            return RecognitionResult(
                qr_code=qr_code,
                model="",
                po="",
                quantity="",
                recognition_mode="mode_0",
                confidence=0.0,
                error_message=f"模式0解析失败: {e}"
            )
    
    def _parse_qr_mode_1(self, qr_code: str, qr_config: Any) -> RecognitionResult:
        """
        解析QR模式1
        
        Args:
            qr_code: QR码字符串
            qr_config: QR码配置
            
        Returns:
            RecognitionResult: 识别结果
        """
        # 模式1：使用分隔符解析
        try:
            # 使用配置的分隔符分割QR码
            parts = qr_code.split(qr_config.qr_split_str)
            
            # 根据配置的位置信息提取数据
            model = self._extract_from_parts(parts, qr_config.model_place)
            po = self._extract_from_parts(parts, qr_config.po_place)
            quantity = self._extract_from_parts(parts, qr_config.qty_place)
            
            confidence = self._calculate_confidence(qr_code, model, po, quantity)
            
            return RecognitionResult(
                qr_code=qr_code,
                model=model,
                po=po,
                quantity=quantity,
                recognition_mode="mode_1",
                confidence=confidence
            )
            
        except Exception as e:
            return RecognitionResult(
                qr_code=qr_code,
                model="",
                po="",
                quantity="",
                recognition_mode="mode_1",
                confidence=0.0,
                error_message=f"模式1解析失败: {e}"
            )
    
    def _extract_by_position(self, qr_code: str, position: int) -> str:
        """
        根据位置提取数据
        
        Args:
            qr_code: QR码字符串
            position: 位置索引
            
        Returns:
            str: 提取的数据
        """
        if position <= 0 or position > len(qr_code):
            return ""
        
        # 位置从1开始，转换为0-based索引
        index = position - 1
        return qr_code[index] if index < len(qr_code) else ""
    
    def _extract_from_parts(self, parts: list, position: int) -> str:
        """
        从分割后的部分中提取数据
        
        Args:
            parts: 分割后的部分列表
            position: 位置索引
            
        Returns:
            str: 提取的数据
        """
        if position <= 0 or position > len(parts):
            return ""
        
        # 位置从1开始，转换为0-based索引
        index = position - 1
        return parts[index] if index < len(parts) else ""
    
    def _calculate_confidence(self, qr_code: str, model: str, po: str, quantity: str) -> float:
        """
        计算识别置信度
        
        Args:
            qr_code: 原始QR码
            model: 识别出的型号
            po: 识别出的PO号
            quantity: 识别出的数量
            
        Returns:
            float: 置信度 (0.0-1.0)
        """
        confidence = 1.0
        
        # 检查是否为空
        if not model:
            confidence *= 0.5
        if not po:
            confidence *= 0.7
        if not quantity:
            confidence *= 0.8
        
        # 检查型号格式（假设型号包含字母和数字）
        if model and not re.match(r'^[A-Za-z0-9\-_]+$', model):
            confidence *= 0.6
        
        # 检查PO号格式（假设PO号以特定前缀开头）
        if po and not re.match(r'^[A-Z]{2,3}\d+$', po):
            confidence *= 0.7
        
        # 检查数量格式（应该是数字）
        if quantity and not quantity.isdigit():
            confidence *= 0.8
        
        return round(confidence, 2)
    
    def _validate_recognition_result(self, result: RecognitionResult) -> Dict[str, Any]:
        """
        验证识别结果
        
        Args:
            result: 识别结果
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        errors = []
        
        # 检查型号
        if not result.model:
            errors.append("型号不能为空")
        elif len(result.model) > 50:
            errors.append("型号长度超过限制")
        
        # 检查PO号
        if not result.po:
            errors.append("PO号不能为空")
        elif len(result.po) > 20:
            errors.append("PO号长度超过限制")
        
        # 检查数量
        if not result.quantity:
            errors.append("数量不能为空")
        elif not result.quantity.isdigit():
            errors.append("数量必须是数字")
        elif int(result.quantity) <= 0:
            errors.append("数量必须大于0")
        
        return {
            "valid": len(errors) == 0,
            "message": "; ".join(errors) if errors else "验证通过"
        }
    
    def batch_recognize(self, qr_codes: list) -> list:
        """
        批量识别型号
        
        Args:
            qr_codes: QR码列表
            
        Returns:
            list: 识别结果列表
        """
        results = []
        for qr_code in qr_codes:
            result = self.recognize_model(qr_code)
            results.append(result)
        
        self.logger.info(f"批量识别完成，共处理{len(qr_codes)}个QR码")
        return results
    
    def get_recognition_statistics(self, results: list) -> Dict[str, Any]:
        """
        获取识别统计信息
        
        Args:
            results: 识别结果列表
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        total = len(results)
        successful = sum(1 for r in results if r.error_message is None)
        failed = total - successful
        
        avg_confidence = 0.0
        if successful > 0:
            avg_confidence = sum(r.confidence for r in results if r.error_message is None) / successful
        
        return {
            "total": total,
            "successful": successful,
            "failed": failed,
            "success_rate": round(successful / total * 100, 2) if total > 0 else 0.0,
            "average_confidence": round(avg_confidence, 2)
        }


class RecognitionPattern:
    """识别模式基类"""
    
    def __init__(self, name: str, pattern: str):
        """
        初始化识别模式
        
        Args:
            name: 模式名称
            pattern: 正则表达式模式
        """
        self.name = name
        self.pattern = re.compile(pattern)
    
    def match(self, qr_code: str) -> Optional[Dict[str, str]]:
        """
        匹配QR码
        
        Args:
            qr_code: QR码字符串
            
        Returns:
            Optional[Dict[str, str]]: 匹配结果
        """
        match = self.pattern.match(qr_code)
        if match:
            return match.groupdict()
        return None


class StandardRecognitionPattern(RecognitionPattern):
    """标准识别模式"""
    
    def __init__(self):
        """初始化标准识别模式"""
        super().__init__(
            name="standard",
            pattern=r'^(?P<model>[A-Z]{2,3}\d+[A-Z]?)@(?P<po>[A-Z]{2,3}\d+)@(?P<quantity>\d+)$'
        )


class ExtendedRecognitionPattern(RecognitionPattern):
    """扩展识别模式"""
    
    def __init__(self):
        """初始化扩展识别模式"""
        super().__init__(
            name="extended",
            pattern=r'^(?P<prefix>[A-Z]{3})-(?P<model>\d+[A-Z]?)@(?P<po>[A-Z]{2,3}\d+)@(?P<quantity>\d+)$'
        )


class PatternBasedRecognizer:
    """基于模式的识别器"""
    
    def __init__(self):
        """初始化基于模式的识别器"""
        self.patterns = [
            StandardRecognitionPattern(),
            ExtendedRecognitionPattern()
        ]
        self.logger = logging.getLogger(__name__)
    
    def recognize(self, qr_code: str) -> Optional[RecognitionResult]:
        """
        使用模式识别QR码
        
        Args:
            qr_code: QR码字符串
            
        Returns:
            Optional[RecognitionResult]: 识别结果
        """
        for pattern in self.patterns:
            match_result = pattern.match(qr_code)
            if match_result:
                self.logger.info(f"使用模式 {pattern.name} 识别成功")
                
                model = match_result.get('model', '')
                po = match_result.get('po', '')
                quantity = match_result.get('quantity', '')
                
                confidence = 0.9  # 模式匹配的置信度较高
                
                return RecognitionResult(
                    qr_code=qr_code,
                    model=model,
                    po=po,
                    quantity=quantity,
                    recognition_mode=f"pattern_{pattern.name}",
                    confidence=confidence
                )
        
        return None
