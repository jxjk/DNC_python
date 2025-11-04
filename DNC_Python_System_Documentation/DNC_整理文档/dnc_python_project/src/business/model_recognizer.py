# src/business/model_recognizer.py
"""
型号识别器
负责识别和解析QR码中的型号信息
"""

import re
import logging
import time
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Tuple
from src.utils.logger import get_logger
from src.utils.error_handler import handle_errors
from src.core.cache_manager import get_global_cache_manager
from src.core.performance_monitor import get_global_performance_monitor

# 使用条件导入处理可能不存在的模块
try:
    from src.business.pattern_recognizer import PatternBasedRecognizer
    PatternBasedRecognizerAvailable = True
except ImportError:
    PatternBasedRecognizer = None
    PatternBasedRecognizerAvailable = False


@dataclass
class RecognitionResult:
    """型号识别结果"""
    success: bool
    model: str = ""
    qr_code: str = ""
    po: str = ""
    quantity: str = ""
    recognition_mode: str = ""
    confidence: float = 0.0
    error_message: Optional[str] = None
    segments: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'success': self.success,
            'model': self.model,
            'qr_code': self.qr_code,
            'po': self.po,
            'quantity': self.quantity,
            'recognition_mode': self.recognition_mode,
            'confidence': self.confidence,
            'error_message': self.error_message,
            'segments': self.segments
        }


@dataclass
class QRProcessingResult:
    """二维码处理结果"""
    success: bool
    model_string: str = None
    segments: List[str] = None
    error_message: str = None
    po: str = ""  # 新增：PO字段
    quantity: str = ""  # 新增：数量字段
    raw_parts: List[str] = None  # 新增：原始分割部分
    
    @classmethod
    def success(cls, model_string: str, segments: List[str], po: str = "", quantity: str = "", raw_parts: List[str] = None) -> 'QRProcessingResult':
        """创建成功结果"""
        return cls(success=True, model_string=model_string, segments=segments, po=po, quantity=quantity, raw_parts=raw_parts)
    
    @classmethod
    def error(cls, error_message: str) -> 'QRProcessingResult':
        """创建错误结果"""
        return cls(success=False, error_message=error_message)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'success': self.success,
            'model_string': self.model_string,
            'segments': self.segments,
            'error_message': self.error_message,
            'po': self.po,
            'quantity': self.quantity,
            'raw_parts': self.raw_parts
        }


@dataclass
class QRConfig:
    """二维码配置"""
    qr_mode: int = 1
    barcode_header_str_num: int = 0
    qr_split_str: str = "@"
    model_place: int = 1
    decimal_place: int = 2


class QRParseError(Exception):
    """二维码解析错误异常"""
    pass


class QRValidationError(Exception):
    """二维码验证错误异常"""
    pass


class QRProcessingFlow:
    """二维码处理流程 - 按照标准流程实现二维码解析"""
    
    def __init__(self, config_manager):
        """
        初始化二维码处理流程
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        self.logger = get_logger("QRProcessingFlow")
        self.cache = get_global_cache_manager()  # 添加缓存管理器
    
    @handle_errors
    def process_qr_code(self, raw_qr_string: str) -> QRProcessingResult:
        """
        处理二维码的完整流程
        
        Args:
            raw_qr_string: 原始二维码字符串
            
        Returns:
            QRProcessingResult: 处理结果
        """
        start_time = time.time()
        self.logger.info(f"开始处理二维码: {raw_qr_string}")
        
        # 1. 基本验证
        if not self._validate_qr_string(raw_qr_string):
            return QRProcessingResult.error("无效的QR字符串")
        
        # 2. 获取QR配置
        qr_config = self._get_qr_config()
        
        # 3. 根据模式解析
        if qr_config.qr_mode == 0:
            model_string = self._parse_qr_mode_0(raw_qr_string, qr_config)
            po = ""
            quantity = ""
            raw_parts = []
        elif qr_config.qr_mode == 1:
            # 对于模式1，提取PO和QUANTITY
            model_string, po, quantity, raw_parts = self._parse_qr_mode_1_with_po_quantity(raw_qr_string, qr_config)
        else:
            return QRProcessingResult.error(f"不支持的QR模式: {qr_config.qr_mode}")
        
        # 4. 分割型号字符串
        segments = self._split_model_string(model_string)
        
        # 5. 应用例外规则
        filtered_segments = self._apply_exception_rules(segments)
        
        end_time = time.time()
        self.logger.info(f"二维码处理完成: {model_string}, PO: {po}, QUANTITY: {quantity}, 耗时: {end_time - start_time:.4f}秒")
        return QRProcessingResult.success(
            model_string=model_string,
            segments=filtered_segments,
            po=po,
            quantity=quantity,
            raw_parts=raw_parts
        )
    
    def _validate_qr_string(self, qr_string: str) -> bool:
        """验证QR字符串"""
        if not qr_string or not isinstance(qr_string, str):
            return False
        
        # 检查字符串长度
        if len(qr_string.strip()) == 0:
            return False
        
        # 检查是否包含非法字符
        # 可以根据实际需求添加更多验证规则
        return True
    
    def _get_qr_config(self) -> QRConfig:
        """获取QR配置"""
        try:
            # 检查缓存
            cache_key = "qr_config_cache"
            cached_config = self.cache.get(cache_key)
            if cached_config is not None:
                self.logger.debug("从缓存加载QR配置")
                return cached_config
            
            qr_config = QRConfig()
            
            # 直接从ConfigManager获取配置（使用统一属性名）
            qr_config.qr_mode = self.config_manager.qr_config.qr_mode
            qr_config.barcode_header_str_num = self.config_manager.qr_config.barcode_header_str_num
            qr_config.qr_split_str = self.config_manager.qr_config.qr_split_str
            qr_config.model_place = self.config_manager.qr_config.model_place
            qr_config.decimal_place = self.config_manager.qr_config.decimal_place
            
            # 缓存配置，有效期30分钟
            self.cache.set(cache_key, qr_config, ttl=1800)
            
            # 添加详细的调试日志（使用INFO级别确保输出）
            self.logger.info(f"QR配置详情: qr_mode={qr_config.qr_mode}, model_place={qr_config.model_place}, split_str='{qr_config.qr_split_str}'")
            self.logger.info(f"ConfigManager QR配置: qr_mode={self.config_manager.qr_config.qr_mode}, model_place={self.config_manager.qr_config.model_place}")
            
            return qr_config
            
        except Exception as e:
            raise QRParseError(f"QR配置加载失败: {str(e)}")
    
    def _parse_qr_mode_0(self, raw_string: str, config: QRConfig) -> str:
        """QR模式0解析 - 去除头部"""
        self.logger.debug(f"使用模式0解析: {raw_string}")
        
        header_length = config.barcode_header_str_num
        if header_length > 0:
            if len(raw_string) <= header_length:
                raise QRParseError(f"QR字符串长度不足，无法去除头部: {raw_string}")
            result = raw_string[header_length:]
            self.logger.debug(f"模式0解析结果: {result}")
            return result
        return raw_string
    
    def _parse_qr_mode_1(self, raw_string: str, config: QRConfig) -> str:
        """QR模式1解析 - 分割提取"""
        self.logger.info(f"使用模式1解析: {raw_string}")
        
        delimiter = config.qr_split_str
        if not delimiter:
            raise QRParseError("模式1需要设置分隔符")
        
        # 处理多行二维码内容（如果有换行符）
        if '\n' in raw_string:
            # 取第一行作为主要解析内容
            first_line = raw_string.split('\n')[0].strip()
            self.logger.info(f"检测到多行内容，使用第一行: {first_line}")
            parts = first_line.split(delimiter)
        else:
            parts = raw_string.split(delimiter)
        
        self.logger.info(f"分割结果: {parts}")
        
        # 主要索引计算 - 配置位置从1开始，Python索引从0开始
        model_place_index = config.model_place - 1
        self.logger.info(f"配置: model_place={config.model_place}, 计算索引={model_place_index}")
        self.logger.info(f"分割后数组长度: {len(parts)}")
        
        if len(parts) > model_place_index:
            result = parts[model_place_index]
            self.logger.info(f"模式1解析结果: {result}")
            return result
        else:
            # 如果按配置分隔符分割失败，尝试使用'@'作为分隔符
            if '@' in raw_string:
                at_parts = raw_string.split('@')
                if len(at_parts) >= 3:
                    # 备用解析逻辑 - 保持一致性
                    result = at_parts[config.model_place - 1]
                    self.logger.info(f"使用'@'分隔符解析结果: {result}")
                    return result
            
            raise QRParseError(f"QR字符串分割后找不到型号位置: {raw_string}")
            
    def _parse_qr_mode_1_with_po_quantity(self, raw_string: str, config: QRConfig) -> Tuple[str, str, str, List[str]]:
        """
        QR模式1解析 - 提取PO和QUANTITY
        
        Args:
            raw_string: 原始字符串
            config: QR配置
            
        Returns:
            tuple: (model_string, po, quantity, raw_parts)
        """
        self.logger.info(f"使用模式1解析（含PO/QUANTITY）: {raw_string}")
        
        delimiter = config.qr_split_str
        if not delimiter:
            raise QRParseError("模式1需要设置分隔符")
        
        # 处理多行二维码内容
        if '\n' in raw_string:
            # 取第一行作为主要解析内容
            first_line = raw_string.split('\n')[0].strip()
            self.logger.info(f"检测到多行内容，使用第一行: {first_line}")
            raw_parts = first_line.split(delimiter)
        else:
            raw_parts = raw_string.split(delimiter)
        
        self.logger.info(f"分割结果: {raw_parts}")
        
        # 提取PO、型号、QUANTITY
        po = ""
        model_string = ""
        quantity = ""
        
        # 根据分割结果提取字段
        if len(raw_parts) >= 3:
            # 标准格式：po@model@quantity
            po = raw_parts[0]  # 第一个是PO
            model_place_index = config.model_place - 1
            if len(raw_parts) > model_place_index:
                model_string = raw_parts[model_place_index]
            quantity = raw_parts[-1]  # 最后一个是QUANTITY
        elif len(raw_parts) == 2:
            # 只有两个部分的情况
            po = raw_parts[0]
            model_string = raw_parts[1]
            quantity = "1"  # 默认数量为1
        else:
            # 只有一个部分的情况
            model_string = raw_parts[0] if raw_parts else ""
        
        self.logger.info(f"提取结果 - PO: {po}, 型号: {model_string}, QUANTITY: {quantity}")
        return model_string, po, quantity, raw_parts
    
    def _split_model_string(self, model_string: str) -> List[str]:
        """分割型号字符串"""
        if not model_string:
            return []
        
        # 根据常见的分隔符进行分割
        separators = ['-', '_', '/', '\\', '@']
        
        # 尝试使用不同的分隔符
        for separator in separators:
            if separator in model_string:
                segments = model_string.split(separator)
                self.logger.debug(f"使用分隔符 '{separator}' 分割结果: {segments}")
                return segments
        
        # 如果没有找到分隔符，返回整个字符串作为单个segment
        self.logger.debug(f"未找到分隔符，返回单个segment: {[model_string]}")
        return [model_string]
    
    def _apply_exception_rules(self, segments: List[str]) -> List[str]:
        """应用例外规则"""
        if not segments:
            return segments
        
        try:
            # 获取header.csv中的例外规则
            header_config = self.config_manager.get_config('header.csv')
            if not header_config:
                return segments
            
            first_segment = segments[0]
            
            for rule in header_config:
                if rule.get('DEFINE') == first_segment:
                    rule_kind = rule.get('KIND', '')
                    
                    if rule_kind == 'del':
                        # 删除该segment
                        self.logger.debug(f"应用删除规则: 删除 {first_segment}")
                        return segments[1:]
                    
                    elif rule_kind == 'add' and len(segments) > 1:
                        # 合并前两个segments
                        merged = f"{segments[0]}-{segments[1]}"
                        self.logger.debug(f"应用合并规则: 合并为 {merged}")
                        return [merged] + segments[2:]
            
            return segments
            
        except Exception as e:
            self.logger.warning(f"例外规则应用失败: {str(e)}")
            return segments


class ModelRecognizer:
    """型号识别器"""
    
    def __init__(self, config_manager):
        """
        初始化型号识别器
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        self.logger = get_logger("ModelRecognizer")
        self.qr_processor = QRProcessingFlow(config_manager)
        self.performance_monitor = get_global_performance_monitor()  # 添加性能监控器
        self.cache = get_global_cache_manager()  # 添加缓存管理器
        # 加载型号定义配置
        self.type_definitions = self.config_manager.get_config('type_define.csv')
        # 加载型号关系配置
        self.type_relations = self.config_manager.get_config('type_relation.csv')
        # 加载型号变化值配置
        self.type_chngvl = self.config_manager.get_config('type_chngvl.csv')
    
    @handle_errors
    def recognize_model(self, qr_code: str) -> RecognitionResult:
        """
        识别型号
        
        Args:
            qr_code: 二维码字符串
            
        Returns:
            RecognitionResult: 识别结果
        """
        start_time = time.time()
        self.logger.info(f"开始型号识别: {qr_code}")
        
        # 使用QRProcessingFlow处理二维码
        qr_result = self.qr_processor.process_qr_code(qr_code)
        
        if not qr_result.success:
            return RecognitionResult(
                success=False,
                error_message=qr_result.error_message
            )
        
        # 使用DEFINE字段进行型号匹配
        matched_no = self.match_model(qr_result.model_string)
        
        end_time = time.time()
        # 构建识别结果 - 包含PO和QUANTITY
        result = RecognitionResult(
            success=True,
            model=qr_result.model_string,
            qr_code=qr_code,
            po=qr_result.po,
            quantity=qr_result.quantity,
            segments=qr_result.segments,
            recognition_mode="QR",
            confidence=1.0 if matched_no else 0.0
        )
        
        self.logger.info(f"型号识别完成: {qr_result.model_string}, 耗时: {end_time - start_time:.4f}秒")
        return result
    
    @handle_errors
    def match_model(self, model_string: str) -> Optional[int]:
        """
        使用DEFINE字段进行型号匹配
        
        Args:
            model_string: 型号字符串
            
        Returns:
            Optional[int]: 匹配到的型号编号，未匹配则返回None
        """
        if not model_string or not self.type_definitions:
            return None
        
        # 尝试完整匹配
        matched_no = self._match_by_define_fields(model_string)
        if matched_no is not None:
            return matched_no
        
        # 递归匹配：从后往前逐个字符删除
        return self._recursive_match(model_string)
    
    def _match_by_define_fields(self, model_string: str) -> Optional[int]:
        """
        使用DEFINE字段进行匹配
        
        Args:
            model_string: 型号字符串
            
        Returns:
            Optional[int]: 匹配到的型号编号，未匹配则返回None
        """
        for definition in self.type_definitions:
            # 优先级：DEFINE > DEFINE1 > DEFINE2 > TYPE
            if definition.get('DEFINE') == model_string:
                return definition.get('NO')
            elif definition.get('DEFINE1') == model_string:
                return definition.get('NO')
            elif definition.get('DEFINE2') == model_string:
                return definition.get('NO')
            elif definition.get('TYPE') == model_string:
                return definition.get('NO')
        
        return None
    
    def _recursive_match(self, model_string: str) -> Optional[int]:
        """
        递归匹配算法
        
        Args:
            model_string: 型号字符串
            
        Returns:
            Optional[int]: 匹配到的型号编号，未匹配则返回None
        """
        # 从完整字符串开始，逐步缩短
        for i in range(len(model_string), 0, -1):
            substring = model_string[:i]
            matched_no = self._match_by_define_fields(substring)
            if matched_no is not None:
                return matched_no
        
        return None
    
    def _validate_model(self, model: str) -> bool:
        """验证型号格式"""
        if not model or not isinstance(model, str):
            return False
        
        # 基本验证：型号不能为空
        return len(model.strip()) > 0
    
    def batch_recognize(self, qr_codes: List[str]) -> List[RecognitionResult]:
        """批量识别型号"""
        results = []
        for qr_code in qr_codes:
            result = self.recognize_model(qr_code)
            results.append(result)
        return results
    
    def get_recognition_statistics(self, results: List[RecognitionResult]) -> Dict[str, Any]:
        """获取识别统计信息"""
        total = len(results)
        successful = sum(1 for r in results if r.error_message is None and r.confidence > 0)
        failed = total - successful
        
        if total > 0:
            success_rate = (successful / total) * 100
            avg_confidence = sum(r.confidence for r in results if r.confidence > 0) / successful if successful > 0 else 0
        else:
            success_rate = 0
            avg_confidence = 0
        
        return {
            "total": total,
            "successful": successful,
            "failed": failed,
            "success_rate": success_rate,
            "average_confidence": avg_confidence
        }