"""
程序匹配器
负责根据型号匹配对应的加工程序
"""

import logging
import re
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass

from ..core.config import ConfigManager
from ..data.csv_processor import CSVProcessor


@dataclass
class MatchResult:
    """匹配结果"""
    model: str
    program_no: int
    matched_string: str
    match_type: str
    confidence: float
    error_message: Optional[str] = None


class ProgramMatcher:
    """程序匹配器"""
    
    def __init__(self, config_manager: ConfigManager, csv_processor: CSVProcessor):
        """
        初始化程序匹配器
        
        Args:
            config_manager: 配置管理器
            csv_processor: CSV处理器
        """
        self.config_manager = config_manager
        self.csv_processor = csv_processor
        self.logger = logging.getLogger(__name__)
        
        # 加载匹配数据
        self.type_define_data = None
        self.type_prg_data = None
        self._load_matching_data()
    
    def _load_matching_data(self) -> None:
        """加载匹配数据"""
        try:
            # 加载型号定义数据
            type_define_path = self.config_manager.get_csv_config_path("type_define.csv")
            self.type_define_data = self.csv_processor.read_csv(type_define_path)
            
            # 加载型号程序数据
            type_prg_path = self.config_manager.get_csv_config_path("type_prg.csv")
            self.type_prg_data = self.csv_processor.read_csv(type_prg_path)
            
            self.logger.info("程序匹配数据加载成功")
            
        except Exception as e:
            self.logger.error(f"程序匹配数据加载失败: {e}")
    
    def match_program(self, model: str) -> MatchResult:
        """
        匹配加工程序
        
        Args:
            model: 型号字符串
            
        Returns:
            MatchResult: 匹配结果
        """
        try:
            self.logger.info(f"开始匹配程序，型号: {model}")
            
            if not self.type_define_data or not self.type_prg_data:
                return MatchResult(
                    model=model,
                    program_no=0,
                    matched_string="",
                    match_type="error",
                    confidence=0.0,
                    error_message="匹配数据未加载"
                )
            
            # 查找型号对应的类型编号
            type_no = self._find_type_no(model)
            if not type_no:
                return MatchResult(
                    model=model,
                    program_no=0,
                    matched_string="",
                    match_type="no_match",
                    confidence=0.0,
                    error_message=f"未找到型号 {model} 对应的类型"
                )
            
            # 根据类型编号查找程序编号
            program_no = self._find_program_no(type_no)
            if not program_no:
                return MatchResult(
                    model=model,
                    program_no=0,
                    matched_string="",
                    match_type="no_program",
                    confidence=0.0,
                    error_message=f"未找到类型 {type_no} 对应的程序"
                )
            
            # 计算匹配置信度
            confidence = self._calculate_match_confidence(model, type_no, program_no)
            
            result = MatchResult(
                model=model,
                program_no=program_no,
                matched_string=f"类型{type_no}->程序{program_no}",
                match_type="exact",
                confidence=confidence
            )
            
            self.logger.info(f"程序匹配成功: 型号{model} -> 程序{program_no}, 置信度: {confidence}")
            return result
            
        except Exception as e:
            self.logger.error(f"程序匹配失败: {e}")
            return MatchResult(
                model=model,
                program_no=0,
                matched_string="",
                match_type="error",
                confidence=0.0,
                error_message=str(e)
            )
    
    def _find_type_no(self, model: str) -> Optional[int]:
        """
        查找型号对应的类型编号
        
        Args:
            model: 型号字符串
            
        Returns:
            Optional[int]: 类型编号
        """
        if not self.type_define_data:
            return None
        
        # 遍历型号定义数据
        for row in self.type_define_data:
            if len(row) >= 2:
                type_no = row[0]
                type_pattern = row[1]
                
                # 检查是否匹配
                if self._match_type_pattern(model, type_pattern):
                    try:
                        return int(type_no)
                    except (ValueError, TypeError):
                        continue
        
        return None
    
    def _match_type_pattern(self, model: str, type_pattern: str) -> bool:
        """
        匹配型号模式
        
        Args:
            model: 型号字符串
            type_pattern: 类型模式
            
        Returns:
            bool: 是否匹配
        """
        # 处理通配符和特殊字符
        pattern = type_pattern.replace('*', '.*').replace('?', '.')
        
        # 添加边界匹配
        if not pattern.startswith('^'):
            pattern = '^' + pattern
        if not pattern.endswith('$'):
            pattern = pattern + '$'
        
        try:
            return bool(re.match(pattern, model, re.IGNORECASE))
        except re.error:
            # 如果正则表达式有误，使用精确匹配
            return model.lower() == type_pattern.lower()
    
    def _find_program_no(self, type_no: int) -> Optional[int]:
        """
        查找类型对应的程序编号
        
        Args:
            type_no: 类型编号
            
        Returns:
            Optional[int]: 程序编号
        """
        if not self.type_prg_data:
            return None
        
        # 查找第一列匹配的行
        for row in self.type_prg_data:
            if len(row) > 0:
                try:
                    current_type_no = int(row[0])
                    if current_type_no == type_no and len(row) > 1:
                        # 返回第一个程序编号
                        return int(row[1])
                except (ValueError, TypeError, IndexError):
                    continue
        
        return None
    
    def _calculate_match_confidence(self, model: str, type_no: int, program_no: int) -> float:
        """
        计算匹配置信度
        
        Args:
            model: 型号字符串
            type_no: 类型编号
            program_no: 程序编号
            
        Returns:
            float: 置信度 (0.0-1.0)
        """
        confidence = 1.0
        
        # 检查型号长度
        if len(model) < 3:
            confidence *= 0.8
        
        # 检查类型编号有效性
        if type_no <= 0:
            confidence *= 0.5
        
        # 检查程序编号有效性
        if program_no <= 0:
            confidence *= 0.5
        
        # 检查数据完整性
        if not self._validate_matching_data():
            confidence *= 0.7
        
        return round(confidence, 2)
    
    def _validate_matching_data(self) -> bool:
        """
        验证匹配数据
        
        Returns:
            bool: 数据是否有效
        """
        if not self.type_define_data or not self.type_prg_data:
            return False
        
        # 检查型号定义数据格式
        for row in self.type_define_data:
            if len(row) < 2:
                return False
            try:
                int(row[0])  # 类型编号应该是数字
            except (ValueError, TypeError):
                return False
        
        # 检查型号程序数据格式
        for row in self.type_prg_data:
            if len(row) < 2:
                return False
            try:
                int(row[0])  # 类型编号应该是数字
                int(row[1])  # 程序编号应该是数字
            except (ValueError, TypeError):
                return False
        
        return True
    
    def batch_match(self, models: list) -> list:
        """
        批量匹配程序
        
        Args:
            models: 型号列表
            
        Returns:
            list: 匹配结果列表
        """
        results = []
        for model in models:
            result = self.match_program(model)
            results.append(result)
        
        self.logger.info(f"批量匹配完成，共处理{len(models)}个型号")
        return results
    
    def get_matching_statistics(self, results: list) -> Dict[str, Any]:
        """
        获取匹配统计信息
        
        Args:
            results: 匹配结果列表
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        total = len(results)
        successful = sum(1 for r in results if r.error_message is None and r.program_no > 0)
        failed = total - successful
        
        avg_confidence = 0.0
        if successful > 0:
            avg_confidence = sum(r.confidence for r in results if r.error_message is None) / successful
        
        match_types = {}
        for result in results:
            if result.match_type:
                match_types[result.match_type] = match_types.get(result.match_type, 0) + 1
        
        return {
            "total": total,
            "successful": successful,
            "failed": failed,
            "success_rate": round(successful / total * 100, 2) if total > 0 else 0.0,
            "average_confidence": round(avg_confidence, 2),
            "match_types": match_types
        }
    
    def reload_matching_data(self) -> bool:
        """
        重新加载匹配数据
        
        Returns:
            bool: 重新加载是否成功
        """
        try:
            self._load_matching_data()
            self.logger.info("程序匹配数据重新加载成功")
            return True
        except Exception as e:
            self.logger.error(f"程序匹配数据重新加载失败: {e}")
            return False


class AdvancedProgramMatcher(ProgramMatcher):
    """高级程序匹配器"""
    
    def __init__(self, config_manager: ConfigManager, csv_processor: CSVProcessor):
        """
        初始化高级程序匹配器
        
        Args:
            config_manager: 配置管理器
            csv_processor: CSV处理器
        """
        super().__init__(config_manager, csv_processor)
        self.fuzzy_matcher = FuzzyMatcher()
        self.pattern_matcher = PatternMatcher()
    
    def match_program(self, model: str) -> MatchResult:
        """
        高级程序匹配（支持模糊匹配和模式匹配）
        
        Args:
            model: 型号字符串
            
        Returns:
            MatchResult: 匹配结果
        """
        # 首先尝试精确匹配
        exact_result = super().match_program(model)
        if exact_result.program_no > 0:
            return exact_result
        
        # 尝试模糊匹配
        fuzzy_result = self.fuzzy_matcher.match(model, self.type_define_data, self.type_prg_data)
        if fuzzy_result.program_no > 0:
            return fuzzy_result
        
        # 尝试模式匹配
        pattern_result = self.pattern_matcher.match(model, self.type_define_data, self.type_prg_data)
        if pattern_result.program_no > 0:
            return pattern_result
        
        # 所有匹配方法都失败
        return MatchResult(
            model=model,
            program_no=0,
            matched_string="",
            match_type="no_match",
            confidence=0.0,
            error_message="所有匹配方法都失败"
        )


class FuzzyMatcher:
    """模糊匹配器"""
    
    def __init__(self):
        """初始化模糊匹配器"""
        self.logger = logging.getLogger(__name__)
    
    def match(self, model: str, type_define_data: list, type_prg_data: list) -> MatchResult:
        """
        模糊匹配
        
        Args:
            model: 型号字符串
            type_define_data: 型号定义数据
            type_prg_data: 型号程序数据
            
        Returns:
            MatchResult: 匹配结果
        """
        best_match = None
        best_score = 0.0
        
        for row in type_define_data:
            if len(row) >= 2:
                type_no = row[0]
                type_pattern = row[1]
                
                # 计算相似度分数
                score = self._calculate_similarity(model, type_pattern)
                
                if score > best_score and score > 0.6:  # 相似度阈值
                    best_score = score
                    best_match = (type_no, type_pattern)
        
        if best_match:
            type_no, type_pattern = best_match
            program_no = self._find_program_no(type_no, type_prg_data)
            
            if program_no:
                return MatchResult(
                    model=model,
                    program_no=program_no,
                    matched_string=f"模糊匹配: {type_pattern}",
                    match_type="fuzzy",
                    confidence=best_score * 0.8  # 模糊匹配置信度较低
                )
        
        return MatchResult(
            model=model,
            program_no=0,
            matched_string="",
            match_type="no_fuzzy_match",
            confidence=0.0
        )
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        计算字符串相似度
        
        Args:
            str1: 字符串1
            str2: 字符串2
            
        Returns:
            float: 相似度分数 (0.0-1.0)
        """
        # 简单的相似度计算（可以替换为更复杂的算法）
        str1_lower = str1.lower()
        str2_lower = str2.lower()
        
        if str1_lower == str2_lower:
            return 1.0
        
        # 计算公共子序列长度
        common_chars = set(str1_lower) & set(str2_lower)
        if not common_chars:
            return 0.0
        
        return len(common_chars) / max(len(str1_lower), len(str2_lower))
    
    def _find_program_no(self, type_no: str, type_prg_data: list) -> Optional[int]:
        """
        查找程序编号
        
        Args:
            type_no: 类型编号
            type_prg_data: 型号程序数据
            
        Returns:
            Optional[int]: 程序编号
        """
        for row in type_prg_data:
            if len(row) > 0 and row[0] == type_no and len(row) > 1:
                try:
                    return int(row[1])
                except (ValueError, TypeError):
                    continue
        return None


class PatternMatcher:
    """模式匹配器"""
    
    def __init__(self):
        """初始化模式匹配器"""
        self.logger = logging.getLogger(__name__)
    
    def match(self, model: str, type_define_data: list, type_prg_data: list) -> MatchResult:
        """
        模式匹配
        
        Args:
            model: 型号字符串
            type_define_data: 型号定义数据
            type_prg_data: 型号程序数据
            
        Returns:
            MatchResult: 匹配结果
        """
        # 提取型号中的数字和字母部分
        numbers = re.findall(r'\d+', model)
        letters = re.findall(r'[A-Za-z]+', model)
        
        for row in type_define_data:
            if len(row) >= 2:
                type_no = row[0]
                type_pattern = row[1]
                
                # 检查是否包含相同的数字或字母模式
                if self._contains_pattern(model, type_pattern, numbers, letters):
                    program_no = self._find_program_no(type_no, type_prg_data)
                    
                    if program_no:
                        return MatchResult(
                            model=model,
                            program_no=program_no,
                            matched_string=f"模式匹配: {type_pattern}",
                            match_type="pattern",
                            confidence=0.7
                        )
        
        return MatchResult(
            model=model,
            program_no=0,
            matched_string="",
            match_type="no_pattern_match",
            confidence=0.0
        )
    
    def _contains_pattern(self, model: str, pattern: str, numbers: list, letters: list) -> bool:
        """
        检查是否包含模式
        
        Args:
            model: 型号字符串
            pattern: 模式字符串
            numbers: 数字列表
            letters: 字母列表
            
        Returns:
            bool: 是否包含模式
        """
        # 检查模式是否包含型号中的关键部分
        for number in numbers:
            if number in pattern:
                return True
        
        for letter in letters:
            if letter.lower() in pattern.lower():
                return True
        
        return False
    
    def _find_program_no(self, type_no: str, type_prg_data: list) -> Optional[int]:
        """
        查找程序编号
        
        Args:
            type_no: 类型编号
            type_prg_data: 型号程序数据
            
        Returns:
            Optional[int]: 程序编号
        """
        for row in type_prg_data:
            if len(row) > 0 and row[0] == type_no and len(row) > 1:
                try:
                    return int(row[1])
                except (ValueError, TypeError):
                    continue
        return None
