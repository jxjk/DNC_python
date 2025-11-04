#!/usr/bin/env python3
"""
型号匹配功能测试脚本
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'dnc_python_project/src'))

from src.business.program_matcher import ModelMatchingFlow
from src.core.config import ConfigManager

def test_model_matching():
    """测试型号匹配功能"""
    print("=== 型号匹配功能测试 ===")
    
    try:
        # 初始化配置管理器
        config_manager = ConfigManager()
        config_manager.load_all_configs()
        
        # 初始化型号匹配流程
        matcher = ModelMatchingFlow(config_manager)
        
        # 测试用例1：完整型号匹配
        print("\n测试用例1：完整型号匹配")
        segments = ["GPA20GT15040_A"]
        result = matcher.match_model(segments)
        print(f"输入: {segments}")
        print(f"结果: {result}")
        
        # 测试用例2：带后缀的型号
        print("\n测试用例2：带后缀的型号")
        segments = ["GPA20GT15040_A", "H8"]
        result = matcher.match_model(segments)
        print(f"输入: {segments}")
        print(f"结果: {result}")
        
        # 测试用例3：不存在的型号
        print("\n测试用例3：不存在的型号")
        segments = ["INVALID_MODEL"]
        result = matcher.match_model(segments)
        print(f"输入: {segments}")
        print(f"结果: {result}")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_model_matching()