#!/usr/bin/env python3
"""
DNC程序改进后的QR码和型号匹配功能演示
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def demo_improved_functionality():
    print("DNC程序改进后的QR码和型号匹配功能演示")
    print("="*60)
    
    from src.config.config_manager import ConfigManager
    from src.data.data_manager import DataManager
    from src.ui.main_window import MainWindow

    # 初始化组件
    config_manager = ConfigManager()
    config_manager.load_config()
    data_manager = DataManager(config_manager)
    data_manager.load_csv_files()
    
    # 创建主窗口实例（但不运行GUI）
    main_window = MainWindow(config_manager, data_manager)
    
    print("1. QR码格式解析演示:")
    print("   支持格式: PO@型号@数量 (如: 12345@GPA18GT15040_A@10)")
    print()
    
    # 演示QR码解析
    qr_inputs = [
        "PO12345@GPA18GT15040_A-EXT@10",  # 该型号应匹配到GPA18GT15040_A
        "PO67890@GPA20GT15040_A@5",      # 该型号应完全匹配
    ]
    
    for qr_input in qr_inputs:
        print(f"输入QR码: {qr_input}")
        parts = qr_input.split('@')
        if len(parts) == 3:
            po, raw_model, qty = parts
            print(f"  → 解析: PO={po}, 原始型号={raw_model}, 数量={qty}")
            
            # 使用改进的型号匹配方法
            matched_model = main_window._find_matching_model(raw_model)
            if matched_model:
                print(f"  → 匹配到型号: {matched_model}")
                product_data = data_manager.get_product_data(matched_model)
                if product_data:
                    print(f"  → 产品NO: {product_data.get('NO', 'N/A')}")
            else:
                print(f"  → 未找到匹配型号")
        print()
    
    print("2. 从后往前逐字符删除匹配演示:")
    print("   根据系统规格.pdf文档描述的方法:")
    print("   从读取的型号从后开始一个字一个字的删除，搜索type_define.csv的TYPE项目")
    print()
    
    match_demos = [
        "GPA18GT15040_A-XXX",    # 应匹配到GPA18GT15040_A
        "GPA20GT15040_A-TEST",  # 应匹配到GPA20GT15040_A
        "GPA24GT15040_A-123",   # 应匹配到GPA24GT15040_A
    ]
    
    for demo_input in match_demos:
        print(f"原始输入: {demo_input}")
        print("  匹配过程:")
        search_str = demo_input
        matched = False
        
        while len(search_str) > 0:
            print(f"    尝试: '{search_str}'")
            product_data = data_manager.get_product_data(search_str)
            if product_data:
                print(f"    ✓ 找到匹配: {search_str} (NO: {product_data.get('NO', 'N/A')})")
                matched = True
                break
            search_str = search_str[:-1]
            if len(search_str) <= 10:  # 避免输出太长
                break
        
        if not matched:
            print("    ✗ 未找到匹配")
        print()
    
    print("3. 型号处理流程:")
    print("   1. 扫描QR码或输入型号 -> 解析得到原始型号字符串")
    print("   2. 从后往前逐字符删除 -> 匹配type_define.csv中的TYPE列")
    print("   3. 找到匹配项后获取产品NO -> 在type_prg.csv中查找程序顺序")
    print("   4. 根据程序顺序加载对应prg文件夹中的load.csv和cntrl.csv")
    print("   5. 生成相应的UI控件")
    print()
    
    print("4. UI控件生成演示:")
    sample_model = "GPA18GT15040_A"  # 已知存在的型号
    print(f"   以型号 '{sample_model}' 为例:")
    product_data = data_manager.get_product_data(sample_model)
    if product_data:
        print(f"   - 产品NO: {product_data.get('NO', 'N/A')}")
        print(f"   - 型号: {product_data.get('TYPE', 'N/A')}")
        print(f"   - 定义1: {product_data.get('DEFINE1', 'N/A')}")
        print(f"   - 定义2: {product_data.get('DEFINE2', 'N/A')}")
        
        # 尝试获取load数据
        prg_load_data = data_manager.get_program_table('1', 'load')
        if prg_load_data:
            for load_row in prg_load_data:
                if load_row.get('TYPE') == sample_model or load_row.get('NO') == product_data.get('NO'):
                    print(f"   - 找到load定义，宏变量示例:")
                    macro_count = 0
                    for key, value in load_row.items():
                        if key not in ['NO', 'TYPE', 'DRAWING', 'DISPFLG'] and value and macro_count < 5:
                            print(f"     * {key} = {value}")
                            macro_count += 1
                    break
    else:
        print(f"   - 未找到型号 '{sample_model}' 的定义")
    
    print("\n" + "="*60)
    print("改进后的功能演示完成！")
    print()
    print("新功能特点:")
    print("✓ 实现了文档中描述的型号匹配方法（从后往前逐字符删除匹配）")
    print("✓ 支持QR码格式解析（PO@型号@数量）")
    print("✓ 根据匹配到的型号自动生成相应的UI控件")
    print("✓ 与原始VB.NET功能保持兼容")

if __name__ == "__main__":
    demo_improved_functionality()