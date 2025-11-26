#!/usr/bin/env python3
"""
测试主窗口的型号匹配功能
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_main_window_model_matching():
    """测试主窗口中的型号匹配功能"""
    print("测试主窗口型号匹配功能...")
    print("="*50)
    
    from src.ui.main_window import MainWindow
    from src.config.config_manager import ConfigManager
    from src.data.data_manager import DataManager

    # 初始化组件
    config_manager = ConfigManager()
    config_manager.load_config()
    data_manager = DataManager(config_manager)
    data_manager.load_csv_files()
    
    # 创建主窗口实例（但不运行GUI）
    main_window = MainWindow(config_manager, data_manager)
    
    # 测试型号匹配功能
    test_cases = [
        "GPA18GT15040_A-XXX",  # 应该匹配到GPA18GT15040_A
        "GPA20GT15040_A",      # 应该完全匹配
        "NONEXISTENT_MODEL",    # 应该不匹配
    ]
    
    print("测试从后往前逐字符删除匹配逻辑:")
    for test_input in test_cases:
        print(f"\n输入: {test_input}")
        matched_model = main_window._find_matching_model(test_input)
        if matched_model:
            print(f"  ✓ 找到匹配: {matched_model}")
            # 获取匹配项的详细信息
            product_data = data_manager.get_product_data(matched_model)
            if product_data:
                print(f"    NO: {product_data.get('NO', 'N/A')}, TYPE: {product_data.get('TYPE', 'N/A')}")
        else:
            print(f"  ✗ 未找到匹配")
    
    print(f"\n测试完整的_process_model方法:")
    # 模拟_process_model方法的调用
    try:
        result = main_window._find_matching_model("GPA18GT15040_A-EXT")
        print(f"处理GPA18GT15040_A-EXT: {result}")
    except Exception as e:
        print(f"处理失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n型号匹配功能测试完成！")

if __name__ == "__main__":
    test_main_window_model_matching()