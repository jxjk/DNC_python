"""
业务逻辑模块
包含型号识别、程序匹配、参数计算、NC通信等核心业务功能
"""

from .model_recognizer import ModelRecognizer, PatternBasedRecognizer
from .program_matcher import ProgramMatcher, AdvancedProgramMatcher, MatchResult
from .calculation_engine import CalculationEngine, AdvancedCalculationEngine, CalculationResult
from .nc_communicator import NCCommunicator, AdvancedNCCommunicator, NCCommand, NCResponse

__all__ = [
    # 型号识别器
    "ModelRecognizer",
    "PatternBasedRecognizer",
    
    # 程序匹配器
    "ProgramMatcher", 
    "AdvancedProgramMatcher",
    "MatchResult",
    
    # 计算引擎
    "CalculationEngine",
    "AdvancedCalculationEngine", 
    "CalculationResult",
    
    # NC通信器
    "NCCommunicator",
    "AdvancedNCCommunicator",
    "NCCommand", 
    "NCResponse"
]
