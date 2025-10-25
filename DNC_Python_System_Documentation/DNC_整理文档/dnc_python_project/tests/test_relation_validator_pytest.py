"""
关系验证器测试
测试RelationValidator类的功能
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

from src.business.relation_validator import RelationValidator


class TestRelationValidator:
    """关系验证器测试类"""
    
    def test_validate_relations_success(self, relation_validator):
        """测试成功验证关系"""
        relation_validator.relation_data = [
            ["1", "param1", "param2", "==", "5", "参数关系验证失败"],
            ["2", "param1", "param2", ">", "3", "参数关系验证失败"]
        ]
        
        program_no = 1
        parameters = {"param1": 5, "param2": 5}
        result = relation_validator.validate_relations(program_no, parameters)
        
        assert result.valid is True
        assert result.program_no == 1
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
    
    def test_validate_relations_no_match(self, relation_validator):
        """测试无匹配关系验证"""
        relation_validator.relation_data = [
            ["1", "param1", "param2", "==", "5", "参数关系验证失败"]
        ]
        
        program_no = 999
        parameters = {"param1": 5, "param2": 5}
        result = relation_validator.validate_relations(program_no, parameters)
        
        assert result.valid is True  # 没有匹配的规则，应该通过
        assert result.program_no == 999
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
    
    def test_validate_relations_data_not_loaded(self, relation_validator):
        """测试数据未加载关系验证"""
        relation_validator.relation_data = None
        
        program_no = 1
        parameters = {"param1": 5, "param2": 10}
        result = relation_validator.validate_relations(program_no, parameters)
        
        assert result.valid is False
        assert result.program_no == 1
        assert "关系数据未加载" in result.errors[0]
        assert len(result.warnings) == 0
    
    def test_validate_relations_failure(self, relation_validator):
        """测试关系验证失败"""
        relation_validator.relation_data = [
            ["1", "param1", "param2", "==", "10", "参数必须相等"]
        ]
        
        program_no = 1
        parameters = {"param1": 5, "param2": 10}
        result = relation_validator.validate_relations(program_no, parameters)
        
        assert result.valid is False
        assert result.program_no == 1
        assert len(result.errors) > 0
        assert "参数必须相等" in result.errors[0]
    
    def test_get_relation_rules_success(self, relation_validator):
        """测试成功获取关系规则"""
        relation_validator.relation_data = [
            ["1", "param1", "param2", "==", "5", "参数关系验证失败"],
            ["1", "param3", "param4", ">", "3", "参数关系验证失败"],
            ["2", "param1", "param2", "==", "10", "参数关系验证失败"]
        ]
        
        rules = relation_validator.get_relation_rules(1)
        
        assert len(rules) == 2
        assert rules[0]["program_no"] == 1
        assert rules[0]["param1"] == "param1"
        assert rules[0]["param2"] == "param2"
        assert rules[0]["operator"] == "=="
        assert rules[0]["expected_value"] == "5"
    
    def test_get_relation_rules_no_match(self, relation_validator):
        """测试无匹配关系规则"""
        relation_validator.relation_data = [
            ["1", "param1", "param2", "==", "5", "参数关系验证失败"]
        ]
        
        rules = relation_validator.get_relation_rules(999)
        
        assert len(rules) == 0
    
    def test_get_relation_rules_data_not_loaded(self, relation_validator):
        """测试数据未加载获取关系规则"""
        relation_validator.relation_data = None
        
        rules = relation_validator.get_relation_rules(1)
        
        assert len(rules) == 0
    
    def test_reload_relation_data_success(self, relation_validator):
        """测试成功重新加载关系数据"""
        with patch.object(relation_validator, '_load_relation_data') as mock_load:
            mock_load.return_value = None
            
            result = relation_validator.reload_relation_data()
            
            assert result is True
            mock_load.assert_called_once()
    
    def test_reload_relation_data_failure(self, relation_validator):
        """测试重新加载关系数据失败"""
        with patch.object(relation_validator, '_load_relation_data') as mock_load:
            mock_load.side_effect = Exception("加载失败")
            
            result = relation_validator.reload_relation_data()
            
            assert result is False
            mock_load.assert_called_once()
    
    def test_clear_cache(self, relation_validator):
        """测试清理缓存"""
        relation_validator.relation_data = [
            ["1", "param1", "param2", "==", "5", "参数关系验证失败"]
        ]
        
        relation_validator.clear_cache()
        
        assert relation_validator.relation_data is None


@pytest.mark.parametrize("program_no,parameters,expected_valid", [
    (1, {"param1": 5, "param2": 5}, True),
    (1, {"param1": 5, "param2": 10}, False),
    (999, {"param1": 5, "param2": 5}, True),
])
def test_relation_validator_comprehensive(program_no, parameters, expected_valid, relation_validator):
    """综合测试关系验证器"""
    relation_validator.relation_data = [
        ["1", "param1", "param2", "==", "5", "参数必须相等"]
    ]
    
    result = relation_validator.validate_relations(program_no, parameters)
    
    assert result.valid == expected_valid
    if not expected_valid:
        assert len(result.errors) > 0
    else:
        assert len(result.errors) == 0
