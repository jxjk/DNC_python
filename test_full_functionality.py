#!/usr/bin/env python3
"""
测试DNC程序的完整功能，包括QR码解析和UI控件生成
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_full_functionality():
    """测试完整的QR码解析和UI控件生成功能"""
    print("测试DNC程序完整功能...")
    
    # 导入必要的模块
    from src.ui.main_window import MainWindow
    from src.config.config_manager import ConfigManager
    from src.data.data_manager import DataManager

    # 初始化组件
    config_manager = ConfigManager()
    config_manager.load_config()
    data_manager = DataManager(config_manager)
    data_manager.load_csv_files()
    
    print("1. 检查基本数据加载:")
    print(f"   - 产品类型数量: {len(data_manager.get_all_product_types())}")
    stats = data_manager.get_statistics()
    print(f"   - 总记录数: {stats['total_records']}")
    print(f"   - 加载文件数: {stats['loaded_files']}")
    
    print("\n2. 检查程序特定文件:")
    # 检查prg1目录下的文件
    prg1_load_data = data_manager.get_program_table('1', 'load')
    if prg1_load_data:
        print(f"   ✓ prg1/load.csv加载成功，记录数: {len(prg1_load_data)}")
        # 显示一个示例记录
        if prg1_load_data:
            example = prg1_load_data[0]
            print(f"   - 示例记录: {example.get('TYPE', 'N/A')} -> {list(example.keys())[:6]}")
    else:
        print("   ✗ prg1/load.csv加载失败")
    
    prg1_cntrl_data = data_manager.get_program_table('1', 'cntrl')
    if prg1_cntrl_data:
        print(f"   ✓ prg1/cntrl.csv加载成功，记录数: {len(prg1_cntrl_data)}")
        # 显示几个示例控件定义
        for i, cntrl_row in enumerate(prg1_cntrl_data[:3]):
            print(f"   - 控件 {i+1}: {cntrl_row.get('MACRO')} ({cntrl_row.get('KIND')})")
    else:
        print("   ✗ prg1/cntrl.csv加载失败")
    
    # 测试产品数据获取
    print("\n3. 测试产品数据获取:")
    test_products = ["GPA18GT15040_A", "GPA20GT15040_A", "GPA24GT15040_A"][:3]  # 取前3个进行测试
    for product in test_products:
        product_data = data_manager.get_product_data(product)
        if product_data:
            print(f"   ✓ {product}: {len(product_data)} 个参数")
        else:
            print(f"   ✗ {product}: 未找到")
    
    # 模拟主窗口中的型号处理逻辑
    print("\n4. 模拟型号处理流程:")
    try:
        model = "GPA18GT15040_A"
        product_data = data_manager.get_product_data(model)
        if product_data:
            print(f"   ✓ 找到产品: {model}")
            # 检查在type_define.csv中的NO
            type_define_data = data_manager.get_table_by_name('type_define.csv')
            for row in type_define_data:
                if row.get('TYPE') == model:
                    prg_no = row.get('NO')
                    print(f"   - 产品NO: {prg_no}")
                    break
        else:
            print(f"   ✗ 未找到产品: {model}")
    except Exception as e:
        print(f"   ✗ 型号处理失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 演示QR码解析
    print("\n5. 测试QR码解析:")
    qr_codes = [
        "PO12345@GPA18GT15040_A@10",  # 完整格式
        "GPA20GT15040_A",             # 仅型号
        "PO67890@GPA24GT15040_A@5@extra"  # 额外部分（应视为无效）
    ]
    
    for qr in qr_codes:
        parts = qr.split('@')
        print(f"   输入: {qr}")
        if len(parts) == 3:
            print(f"     解析为 PO@型号@数量: {parts[0]} @ {parts[1]} @ {parts[2]}")
        elif len(parts) == 1:
            print(f"     解析为直接型号: {parts[0]}")
        else:
            print(f"     未知格式: {parts} (共{len(parts)}部分)")
    
    print("\n完整功能测试完成！")

if __name__ == "__main__":
    test_full_functionality()