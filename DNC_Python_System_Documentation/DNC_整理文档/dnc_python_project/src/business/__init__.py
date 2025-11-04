"""
业务逻辑模块
包含型号识别、程序匹配、参数计算、NC通信等核心业务功能
"""

# 修改前的导入语句：
# from .program_matcher import ProgramMatcher, AdvancedProgramMatcher, MatchResult

# 修改后的导入语句（按照指示）：
from .program_matcher import ProgramMatcher, ProgramMatchResult
from .calculation_engine import CalculationEngine, CalculationResult
from .nc_communicator import NCCommunicator, AdvancedNCCommunicator, NCCommand, NCResponse
from .model_recognizer import ModelRecognizer, RecognitionResult
from .pattern_recognizer import PatternBasedRecognizer
from .relation_validator import RelationValidator

__all__ = [
    # 型号识别器
    "ModelRecognizer",
    "RecognitionResult",
    "PatternBasedRecognizer",
    
    # 程序匹配器
    "ProgramMatcher", 
    # 修改前的内容：
    # "AdvancedProgramMatcher",
    # "MatchResult",
    
    # 修改后的内容（按照指示）：
    "ProgramMatchResult",
    
    # 计算引擎
    "CalculationEngine",
    "CalculationResult",
    
    # NC通信器
    "NCCommunicator",
    "AdvancedNCCommunicator",
    "NCCommand", 
    "NCResponse",
    
    # 关系验证器
    "RelationValidator"
]
