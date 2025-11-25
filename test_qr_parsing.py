#!/usr/bin/env python3
"""
测试DNC程序的QR码解析和UI控件生成功能
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_qr_parsing():
    """测试QR码解析功能"""
    print("测试QR码解析功能...")
    
    # 导入主窗口
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
    
    # 测试QR码解析
    print("1. 测试完整QR码格式 (PO@型号@数量):")
    test_qr = "PO12345@GPA18GT15040_A@10"
    print(f"   输入: {test_qr}")
    parts = test_qr.split('@')
    if len(parts) == 3:
        po_number = parts[0]
        model = parts[1]
        quantity = parts[2]
        print(f"   解析结果 - PO: {po_number}, 型号: {model}, 数量: {quantity}")
    else:
        print("   解析失败")
    
    print("\n2. 测试直接型号输入:")
    test_model = "GPA20GT15040_A"
    print(f"   输入: {test_model}")
    parts = test_model.split('@')
    if len(parts) == 1:
        model = parts[0]
        print(f"   解析结果 - 型号: {model}")
    else:
        print(f"   意外的解析结果: {parts}")
    
    print("\n3. 测试型号处理功能:")
    try:
        test_model = "GPA18GT15040_A"
        product_data = data_manager.get_product_data(test_model)
        if product_data:
            print(f"   ✓ 找到产品数据: {test_model}")
            print(f"   - 产品参数数量: {len(product_data)}")
            print(f"   - 前几个参数: {dict(list(product_data.items())[:5])}")
        else:
            print(f"   ✗ 未找到产品数据: {test_model}")
    except Exception as e:
        print(f"   ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n4. 测试load.csv数据:")
    try:
        # 检查load.csv数据
        load_data = data_manager.get_table_by_name('load.csv')
        if load_data:
            print(f"   ✓ load.csv加载成功，记录数: {len(load_data)}")
            # 查找与测试型号相关的记录
            for load_row in load_data:
                if load_row.get('TYPE', '').startswith('GPA'):
                    print(f"   - 示例记录 (TYPE={load_row.get('TYPE')}): {list(load_row.keys())[:6]}")
                    break
        else:
            print("   ✗ load.csv加载失败")
    except Exception as e:
        print(f"   ✗ load.csv测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n5. 测试cntrl.csv数据:")
    try:
        # 检查cntrl.csv数据
        cntrl_data = data_manager.get_table_by_name('cntrl.csv')
        if cntrl_data:
            print(f"   ✓ cntrl.csv加载成功，记录数: {len(cntrl_data)}")
            # 显示前几个控件定义
            for i, cntrl_row in enumerate(cntrl_data[:3]):
                print(f"   - 控件 {i+1}: {cntrl_row.get('MACRO')} ({cntrl_row.get('KIND')})")
        else:
            print("   ✗ cntrl.csv加载失败")
    except Exception as e:
        print(f"   ✗ cntrl.csv测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n6. 测试type_prg.csv数据:")
    try:
        # 检查type_prg.csv数据
        type_prg_data = data_manager.get_table_by_name('type_prg.csv')
        if type_prg_data:
            print(f"   ✓ type_prg.csv加载成功，记录数: {len(type_prg_data)}")
            # 显示前几个记录
            for i, prg_row in enumerate(type_prg_data[:3]):
                print(f"   - 记录 {i+1}: NO={prg_row.get('NO')}, prg1={prg_row.get('prg1', 'N/A')}")
        else:
            print("   ✗ type_prg.csv加载失败")
    except Exception as e:
        print(f"   ✗ type_prg.csv测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nQR码解析功能测试完成！")

if __name__ == "__main__":
    test_qr_parsing()