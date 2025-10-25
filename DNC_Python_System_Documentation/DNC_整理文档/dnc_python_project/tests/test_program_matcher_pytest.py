"""
程序匹配器测试
测试ProgramMatcher类的功能
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

from src.business.program_matcher import (
    ProgramMatcher, 
    MatchResult, 
    AdvancedProgramMatcher,
    FuzzyMatcher,
    PatternMatcher
)


class TestProgramMatcher:
    """程序匹配器测试类"""
    
    def test_match_program_success(self, program_matcher):
        """测试成功匹配程序"""
        # 设置模拟数据
        program_matcher.type_define_data = [
            ["1", "MODEL*"],
            ["2", "TEST*"],
            ["3", "SPECIAL*"]
        ]
        program_matcher.type_prg_data = [
            ["1", "1001"],
            ["2", "1002"],
            ["3", "1003"]
        ]
        
        result = program_matcher.match_program("MODEL456")
        
        assert result.program_no == 1001
        assert result.model == "MODEL456"
        assert result.match_type == "exact"
        assert result.confidence > 0.0
        assert result.error_message is None
    
    def test_match_program_no_type_match(self, program_matcher):
        """测试无类型匹配"""
        program_matcher.type_define_data = [
            ["1", "OTHER*"],
            ["2", "DIFFERENT*"]
        ]
        program_matcher.type_prg_data = [
            ["1", "1001"],
            ["2", "1002"]
        ]
        
        result = program_matcher.match_program("MODEL456")
        
        assert result.program_no == 0
        assert result.match_type == "no_match"
        assert result.confidence == 0.0
        assert "未找到型号" in result.error_message
    
    def test_match_program_no_program_match(self, program_matcher):
        """测试无程序匹配"""
        program_matcher.type_define_data = [
            ["1", "MODEL*"]
        ]
        program_matcher.type_prg_data = [
            ["2", "1002"]  # 类型编号不匹配
        ]
        
        result = program_matcher.match_program("MODEL456")
        
        assert result.program_no == 0
        assert result.match_type == "no_program"
        assert result.confidence == 0.0
        assert "未找到类型" in result.error_message
    
    def test_match_program_data_not_loaded(self, program_matcher):
        """测试数据未加载情况"""
        program_matcher.type_define_data = None
        program_matcher.type_prg_data = None
        
        result = program_matcher.match_program("MODEL456")
        
        assert result.program_no == 0
        assert result.match_type == "error"
        assert result.confidence == 0.0
        assert "匹配数据未加载" in result.error_message
    
    @pytest.mark.parametrize("model,expected_program", [
        ("MODEL001", 1001),
        ("MODEL002", 1001),
        ("TEST001", 1002),
        ("SPECIAL001", 1003),
    ])
    def test_match_program_parametrized(self, program_matcher, model, expected_program):
        """参数化测试程序匹配"""
        program_matcher.type_define_data = [
            ["1", "MODEL*"],
            ["2", "TEST*"],
            ["3", "SPECIAL*"]
        ]
        program_matcher.type_prg_data = [
            ["1", "1001"],
            ["2", "1002"],
            ["3", "1003"]
        ]
        
        result = program_matcher.match_program(model)
        
        assert result.program_no == expected_program
        assert result.model == model
    
    def test_find_type_no_success(self, program_matcher):
        """测试成功查找类型编号"""
        program_matcher.type_define_data = [
            ["1", "MODEL*"],
            ["2", "TEST*"]
        ]
        
        type_no = program_matcher._find_type_no("MODEL456")
        
        assert type_no == 1
    
    def test_find_type_no_no_match(self, program_matcher):
        """测试无匹配类型编号"""
        program_matcher.type_define_data = [
            ["1", "OTHER*"]
        ]
        
        type_no = program_matcher._find_type_no("MODEL456")
        
        assert type_no is None
    
    def test_find_type_no_invalid_data(self, program_matcher):
        """测试无效数据查找类型编号"""
        program_matcher.type_define_data = None
        
        type_no = program_matcher._find_type_no("MODEL456")
        
        assert type_no is None
    
    def test_match_type_pattern_exact(self, program_matcher):
        """测试精确匹配类型模式"""
        result = program_matcher._match_type_pattern("MODEL456", "MODEL456")
        assert result is True
    
    def test_match_type_pattern_wildcard(self, program_matcher):
        """测试通配符匹配类型模式"""
        result = program_matcher._match_type_pattern("MODEL456", "MODEL*")
        assert result is True
        
        result = program_matcher._match_type_pattern("MODEL456", "*456")
        assert result is True
    
    def test_match_type_pattern_no_match(self, program_matcher):
        """测试无匹配类型模式"""
        result = program_matcher._match_type_pattern("MODEL456", "OTHER*")
        assert result is False
    
    def test_match_type_pattern_invalid_regex(self, program_matcher):
        """测试无效正则表达式模式"""
        result = program_matcher._match_type_pattern("MODEL456", "[invalid")
        # 应该回退到精确匹配
        assert result is False
    
    def test_find_program_no_success(self, program_matcher):
        """测试成功查找程序编号"""
        program_matcher.type_prg_data = [
            ["1", "1001"],
            ["2", "1002"]
        ]
        
        program_no = program_matcher._find_program_no(1)
        
        assert program_no == 1001
    
    def test_find_program_no_no_match(self, program_matcher):
        """测试无匹配程序编号"""
        program_matcher.type_prg_data = [
            ["1", "1001"]
        ]
        
        program_no = program_matcher._find_program_no(2)
        
        assert program_no is None
    
    def test_find_program_no_invalid_data(self, program_matcher):
        """测试无效数据查找程序编号"""
        program_matcher.type_prg_data = None
        
        program_no = program_matcher._find_program_no(1)
        
        assert program_no is None
    
    def test_calculate_match_confidence_high(self, program_matcher):
        """测试高匹配置信度计算"""
        confidence = program_matcher._calculate_match_confidence(
            "MODEL456", 1, 1001
        )
        assert confidence > 0.67
    
    def test_calculate_match_confidence_low(self, program_matcher):
        """测试低匹配置信度计算"""
        confidence = program_matcher._calculate_match_confidence(
            "AB", -1, -1
        )
        assert confidence < 0.5
    
    def test_validate_matching_data_valid(self, program_matcher):
        """测试有效匹配数据验证"""
        program_matcher.type_define_data = [
            ["1", "PATTERN1"],
            ["2", "PATTERN2"]
        ]
        program_matcher.type_prg_data = [
            ["1", "1001"],
            ["2", "1002"]
        ]
        
        result = program_matcher._validate_matching_data()
        assert result is True
    
    def test_validate_matching_data_invalid(self, program_matcher):
        """测试无效匹配数据验证"""
        program_matcher.type_define_data = [
            ["INVALID", "PATTERN"]  # 类型编号不是数字
        ]
        program_matcher.type_prg_data = [
            ["1", "1001"]
        ]
        
        result = program_matcher._validate_matching_data()
        assert result is False
    
    def test_validate_matching_data_missing(self, program_matcher):
        """测试缺失匹配数据验证"""
        program_matcher.type_define_data = None
        program_matcher.type_prg_data = []
        
        result = program_matcher._validate_matching_data()
        assert result is False
    
    def test_batch_match(self, program_matcher):
        """测试批量匹配"""
        program_matcher.type_define_data = [
            ["1", "MODEL*"],
            ["2", "TEST*"]
        ]
        program_matcher.type_prg_data = [
            ["1", "1001"],
            ["2", "1002"]
        ]
        
        models = ["MODEL001", "TEST001", "UNKNOWN"]
        results = program_matcher.batch_match(models)
        
        assert len(results) == 3
        assert results[0].program_no == 1001
        assert results[1].program_no == 1002
        assert results[2].program_no == 0
    
    def test_get_matching_statistics(self, program_matcher):
        """测试获取匹配统计信息"""
        results = [
            MatchResult("MODEL1", 1001, "匹配1", "exact", 0.9),
            MatchResult("MODEL2", 1002, "匹配2", "exact", 0.8),
            MatchResult("MODEL3", 0, "", "no_match", 0.0, "错误"),
        ]
        
        stats = program_matcher.get_matching_statistics(results)
        
        assert stats["total"] == 3
        assert stats["successful"] == 2
        assert stats["failed"] == 1
        assert stats["success_rate"] == pytest.approx(66.67, 0.01)
        assert stats["average_confidence"] == pytest.approx(0.85, 0.01)
        assert stats["match_types"]["exact"] == 2
        assert stats["match_types"]["no_match"] == 1
    
    def test_reload_matching_data_success(self, program_matcher, mock_csv_processor):
        """测试成功重新加载匹配数据"""
        with patch.object(program_matcher, '_load_matching_data') as mock_load:
            mock_load.return_value = None
            
            result = program_matcher.reload_matching_data()
            
            assert result is True
            mock_load.assert_called_once()
    
    def test_reload_matching_data_failure(self, program_matcher):
        """测试重新加载匹配数据失败"""
        with patch.object(program_matcher, '_load_matching_data') as mock_load:
            mock_load.side_effect = Exception("加载失败")
            
            result = program_matcher.reload_matching_data()
            
            assert result is False
            mock_load.assert_called_once()


class TestAdvancedProgramMatcher:
    """高级程序匹配器测试类"""
    
    def test_advanced_match_exact_success(self, mock_config_manager, mock_csv_processor):
        """测试高级匹配器精确匹配成功"""
        matcher = AdvancedProgramMatcher(mock_config_manager, mock_csv_processor)
        
        # 设置基础数据
        matcher.type_define_data = [["1", "MODEL*"]]
        matcher.type_prg_data = [["1", "1001"]]
        
        # 模拟模糊匹配器和模式匹配器返回无结果
        with patch.object(matcher.fuzzy_matcher, 'match') as mock_fuzzy, \
             patch.object(matcher.pattern_matcher, 'match') as mock_pattern:
            mock_fuzzy.return_value = MatchResult("MODEL456", 0, "", "no_fuzzy_match", 0.0)
            mock_pattern.return_value = MatchResult("MODEL456", 0, "", "no_pattern_match", 0.0)
            
            result = matcher.match_program("MODEL456")
            
            assert result.program_no == 1001
            assert result.match_type == "exact"
    
    def test_advanced_match_fuzzy_success(self, mock_config_manager, mock_csv_processor):
        """测试高级匹配器模糊匹配成功"""
        matcher = AdvancedProgramMatcher(mock_config_manager, mock_csv_processor)
        
        # 设置基础数据（无精确匹配）
        matcher.type_define_data = [["1", "OTHER*"]]
        matcher.type_prg_data = [["1", "1001"]]
        
        # 模拟模糊匹配器返回成功结果
        with patch.object(matcher.fuzzy_matcher, 'match') as mock_fuzzy, \
             patch.object(matcher.pattern_matcher, 'match') as mock_pattern:
            mock_fuzzy.return_value = MatchResult("MODEL456", 1002, "模糊匹配", "fuzzy", 0.7)
            mock_pattern.return_value = MatchResult("MODEL456", 0, "", "no_pattern_match", 0.0)
            
            result = matcher.match_program("MODEL456")
            
            assert result.program_no == 1002
            assert result.match_type == "fuzzy"
    
    def test_advanced_match_pattern_success(self, mock_config_manager, mock_csv_processor):
        """测试高级匹配器模式匹配成功"""
        matcher = AdvancedProgramMatcher(mock_config_manager, mock_csv_processor)
        
        # 设置基础数据（无精确匹配）
        matcher.type_define_data = [["1", "OTHER*"]]
        matcher.type_prg_data = [["1", "1001"]]
        
        # 模拟模糊匹配器和模式匹配器返回结果
        with patch.object(matcher.fuzzy_matcher, 'match') as mock_fuzzy, \
             patch.object(matcher.pattern_matcher, 'match') as mock_pattern:
            mock_fuzzy.return_value = MatchResult("MODEL456", 0, "", "no_fuzzy_match", 0.0)
            mock_pattern.return_value = MatchResult("MODEL456", 1003, "模式匹配", "pattern", 0.7)
            
            result = matcher.match_program("MODEL456")
            
            assert result.program_no == 1003
            assert result.match_type == "pattern"
    
    def test_advanced_match_all_failed(self, mock_config_manager, mock_csv_processor):
        """测试高级匹配器所有方法都失败"""
        matcher = AdvancedProgramMatcher(mock_config_manager, mock_csv_processor)
        
        # 设置基础数据（无精确匹配）
        matcher.type_define_data = [["1", "OTHER*"]]
        matcher.type_prg_data = [["1", "1001"]]
        
        # 模拟所有匹配器都返回无结果
        with patch.object(matcher.fuzzy_matcher, 'match') as mock_fuzzy, \
             patch.object(matcher.pattern_matcher, 'match') as mock_pattern:
            mock_fuzzy.return_value = MatchResult("MODEL456", 0, "", "no_fuzzy_match", 0.0)
            mock_pattern.return_value = MatchResult("MODEL456", 0, "", "no_pattern_match", 0.0)
            
            result = matcher.match_program("MODEL456")
            
            assert result.program_no == 0
            assert result.match_type == "no_match"
            assert "所有匹配方法都失败" in result.error_message


class TestFuzzyMatcher:
    """模糊匹配器测试类"""
    
    def test_fuzzy_match_success(self):
        """测试模糊匹配成功"""
        matcher = FuzzyMatcher()
        type_define_data = [["1", "MODEL"], ["2", "TEST"]]
        type_prg_data = [["1", "1001"], ["2", "1002"]]
        
        result = matcher.match("MODEL456", type_define_data, type_prg_data)
        
        assert result.program_no == 1001
        assert result.match_type == "fuzzy"
        assert result.confidence > 0.0
    
    def test_fuzzy_match_no_match(self):
        """测试模糊匹配无结果"""
        matcher = FuzzyMatcher()
        type_define_data = [["1", "OTHER"], ["2", "DIFFERENT"]]
        type_prg_data = [["1", "1001"], ["2", "1002"]]
        
        result = matcher.match("MODEL456", type_define_data, type_prg_data)
        
        assert result.program_no == 0
        assert result.match_type == "no_fuzzy_match"
        assert result.confidence == 0.0
    
    def test_calculate_similarity_high(self):
        """测试高相似度计算"""
        matcher = FuzzyMatcher()
        similarity = matcher._calculate_similarity("MODEL456", "MODEL456")
        assert similarity == 1.0
    
    def test_calculate_similarity_low(self):
        """测试低相似度计算"""
        matcher = FuzzyMatcher()
        similarity = matcher._calculate_similarity("ABC", "XYZ")
        assert similarity == 0.0
    
    def test_calculate_similarity_partial(self):
        """测试部分相似度计算"""
        matcher = FuzzyMatcher()
        similarity = matcher._calculate_similarity("MODEL456", "MODEL")
        assert similarity > 0.0
        assert similarity < 1.0


class TestPatternMatcher:
    """模式匹配器测试类"""
    
    def test_pattern_match_success(self):
        """测试模式匹配成功"""
        matcher = PatternMatcher()
        type_define_data = [["1", "MODEL123"], ["2", "TEST456"]]
        type_prg_data = [["1", "1001"], ["2", "1002"]]
        
        result = matcher.match("MODEL123", type_define_data, type_prg_data)
        
        assert result.program_no == 1001
        assert result.match_type == "pattern"
        assert result.confidence == 0.7
    
    def test_pattern_match_no_match(self):
        """测试模式匹配无结果"""
        matcher = PatternMatcher()
        type_define_data = [["1", "OTHER"], ["2", "DIFFERENT"]]
        type_prg_data = [["1", "1001"], ["2", "1002"]]
        
        result = matcher.match("MODEL456", type_define_data, type_prg_data)
        
        assert result.program_no == 0
        assert result.match_type == "no_pattern_match"
        assert result.confidence == 0.0
    
    def test_contains_pattern_success(self):
        """测试成功包含模式"""
        matcher = PatternMatcher()
        numbers = ["456"]
        letters = ["MODEL"]
        
        result = matcher._contains_pattern("MODEL456", "MODEL123", numbers, letters)
        assert result is True
    
    def test_contains_pattern_failure(self):
        """测试不包含模式"""
        matcher = PatternMatcher()
        numbers = ["789"]
        letters = ["OTHER"]
        
        result = matcher._contains_pattern("MODEL456", "DIFFERENT", numbers, letters)
        assert result is False
    
    def test_find_program_no_success(self):
        """测试成功查找程序编号"""
        matcher = PatternMatcher()
        type_prg_data = [["1", "1001"], ["2", "1002"]]
        
        program_no = matcher._find_program_no("1", type_prg_data)
        assert program_no == 1001
    
    def test_find_program_no_no_match(self):
        """测试无匹配程序编号"""
        matcher = PatternMatcher()
        type_prg_data = [["1", "1001"]]
        
        program_no = matcher._find_program_no("2", type_prg_data)
        assert program_no is None


class TestProgramMatcherIntegration:
    """程序匹配器集成测试"""
    
    def test_program_matcher_with_mock_logger(self, program_matcher, mock_logger):
        """测试带模拟日志的程序匹配器"""
        with patch.object(program_matcher, 'logger', mock_logger):
            program_matcher.type_define_data = [["1", "MODEL*"]]
            program_matcher.type_prg_data = [["1", "1001"]]
            
            result = program_matcher.match_program("MODEL456")
            
            # 验证日志调用
            mock_logger.info.assert_called()
            assert result.program_no == 1001
    
    def test_program_matcher_exception_handling(self, program_matcher):
        """测试异常处理"""
        # 模拟数据加载异常
        program_matcher.type_define_data = [["INVALID", "PATTERN"]]
        program_matcher.type_prg_data = [["1", "1001"]]
        
        result = program_matcher.match_program("MODEL456")
        
        # 应该能够处理异常并返回错误结果
        assert result.error_message is not None


@pytest.mark.parametrize("model,type_pattern,expected_program", [
    ("MODEL001", "MODEL*", 1001),
    ("TEST001", "TEST*", 1002),
    ("SPECIAL001", "SPECIAL*", 1003),
    ("UNKNOWN", "OTHER*", 0),
])
def test_program_matcher_comprehensive(model, type_pattern, expected_program, program_matcher):
    """综合测试程序匹配器"""
    program_matcher.type_define_data = [
        ["1", "MODEL*"],
        ["2", "TEST*"],
        ["3", "SPECIAL*"]
    ]
    program_matcher.type_prg_data = [
        ["1", "1001"],
        ["2", "1002"],
        ["3", "1003"]
    ]
    
    result = program_matcher.match_program(model)
    
    if expected_program > 0:
        assert result.program_no == expected_program
        assert result.error_message is None
    else:
        assert result.program_no == 0
        assert result.error_message is not None
