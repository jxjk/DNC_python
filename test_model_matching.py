#!/usr/bin/env python3
"""
测试新的型号匹配逻辑
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_model_matching():
    """测试从后往前逐字符删除的型号匹配逻辑"""
    print("测试新的型号匹配逻辑...")
    print("="*50)
    
    from src.config.config_manager import ConfigManager
    from src.data.data_manager import DataManager

    # 初始化组件
    config_manager = ConfigManager()
    config_manager.load_config()
    data_manager = DataManager(config_manager)
    data_manager.load_csv_files()
    
    # 获取type_define.csv数据
    type_define_data = data_manager.get_table_by_name('type_define.csv')
    print(f"从type_define.csv加载了 {len(type_define_data)} 条型号记录")
    print()
    
    # 测试用例
    test_cases = [
        "C-CCC10-20A-P5S-30",  # 按文档示例，应匹配到 C-CCC
        "GPA18GT15040_A-XXX",  # 应匹配到 GPA18GT15040_A
        "GPA20GT15040_A",      # 应完全匹配到 GPA20GT15040_A
        "TEST_NONEXISTENT",    # 应该不匹配任何型号
        "GPA18GT15040",        # 应该不匹配（缺少_A后缀）
    ]
    
    for test_input in test_cases:
        print(f"测试输入: {test_input}")
        # 实现从后往前逐字符删除的匹配逻辑
        search_string = test_input
        matched = False
        
        while len(search_string) > 0:
            for row in type_define_data:
                type_value = row.get('TYPE', '')
                if type_value and search_string == type_value:
                    print(f"  ✓ 匹配成功: {search_string} (从 {test_input} 匹配)")
                    print(f"    匹配项NO: {row.get('NO', 'N/A')}, 定义1: {row.get('DEFINE1', 'N/A')}, 定义2: {row.get('DEFINE2', 'N/A')}")
                    matched = True
                    break
            
            if matched:
                break
                
            # 删除最后一个字符，继续搜索
            search_string = search_string[:-1]
        
        if not matched:
            print(f"  ✗ 未找到匹配: {test_input}")
        print()
    
    print("型号匹配逻辑测试完成！")
    print()
    print("根据文档描述的匹配方法：")
    print("1. 从读取的型号从后开始一个字一个字的删除")
    print("2. 搜索type_define.csv的TYPE项目")
    print("3. 取得匹配的行的NO值")
    print()
    print("例如：C-CCC10-20A-P5S-30 会按以下顺序搜索：")
    print("  C-CCC10-20A-P5S-30 -> C-CCC10-20A-P5S-3 -> C-CCC10-20A-P5S- -> ... -> C-CCC -> 找到匹配！")

if __name__ == "__main__":
    test_model_matching()