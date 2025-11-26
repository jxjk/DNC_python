#!/usr/bin/env python3
"""
DNC程序QR码功能演示
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def demo_qr_functionality():
    print("DNC程序QR码解析和UI控件生成功能演示")
    print("="*50)
    
    from src.config.config_manager import ConfigManager
    from src.data.data_manager import DataManager
    from src.ui.main_window import MainWindow

    # 初始化组件
    config_manager = ConfigManager()
    config_manager.load_config()
    data_manager = DataManager(config_manager)
    data_manager.load_csv_files()
    
    print("1. QR码格式解析演示:")
    print("   支持两种格式:")
    print("   - 完整格式: PO@型号@数量 (如: 12345@GPA18GT15040_A@10)")
    print("   - 简单格式: 型号 (如: GPA18GT15040_A)")
    print()
    
    # 演示不同格式的解析
    test_inputs = [
        "PO12345@GPA18GT15040_A@10",  # QR码格式
        "GPA20GT15040_A",             # 直接型号
        "PO67890@GPA24GT15040_A@5"   # 另一个QR码
    ]
    
    for test_input in test_inputs:
        print(f"输入: {test_input}")
        parts = test_input.split('@')
        if len(parts) == 3:
            po, model, quantity = parts
            print(f"  → PO: {po}, 型号: {model}, 数量: {quantity}")
            
            # 检查型号是否存在
            product_data = data_manager.get_product_data(model)
            if product_data:
                print(f"  → ✓ 型号存在，找到 {len(product_data)} 个参数")
                # 尝试获取程序信息
                type_define_data = data_manager.get_table_by_name('type_define.csv')
                for row in type_define_data:
                    if row.get('TYPE') == model:
                        no = row.get('NO')
                        print(f"  → 产品编号: {no}")
                        
                        # 尝试获取程序配置
                        type_prg_data = data_manager.get_table_by_name('type_prg.csv')
                        for prg_row in type_prg_data:
                            if prg_row.get('NO') == no:
                                prg1 = prg_row.get('prg1', 'N/A')
                                print(f"  → 首选程序: prg{prg1}")
                                break
                        break
            else:
                print(f"  → ✗ 型号不存在或无法找到")
        elif len(parts) == 1:
            model = parts[0]
            print(f"  → 型号: {model}")
            
            product_data = data_manager.get_product_data(model)
            if product_data:
                print(f"  → ✓ 型号存在，找到 {len(product_data)} 个参数")
            else:
                print(f"  → ✗ 型号不存在")
        else:
            print(f"  → ? 未知格式，包含 {len(parts)} 部分")
        print()
    
    print("2. UI控件生成演示:")
    print("   当扫描QR码或输入型号后，程序将:")
    print("   - 解析输入的型号")
    print("   - 从type_define.csv找到对应的产品NO")
    print("   - 从type_prg.csv确定显示程序顺序")
    print("   - 从对应prg文件夹的load.csv获取控件定义")
    print("   - 从对应prg文件夹的cntrl.csv获取控件类型")
    print("   - 生成相应的UI控件（load, input, measure, select等）")
    print()
    
    print("3. 数据文件结构:")
    print("   - type_define.csv: 定义产品型号与NO的对应关系")
    print("   - type_prg.csv: 定义产品NO与程序显示顺序的对应关系")
    print("   - prg*/load.csv: 定义每个程序的控件值")
    print("   - prg*/cntrl.csv: 定义控件类型和显示属性")
    print()
    
    print("4. 实际控件生成流程:")
    test_model = "GPA18GT15040_A"
    print(f"   以型号 '{test_model}' 为例:")
    
    product_data = data_manager.get_product_data(test_model)
    if product_data:
        no = product_data.get('NO')
        print(f"   - 产品NO: {no}")
        
        # 获取load数据
        prg_load_data = data_manager.get_program_table('1', 'load')  # 假设使用程序1
        if prg_load_data:
            matching_load = None
            for load_row in prg_load_data:
                if load_row.get('TYPE') == test_model or load_row.get('NO') == no:
                    matching_load = load_row
                    break
            
            if matching_load:
                print(f"   - 找到load定义，包含以下宏变量:")
                for key, value in matching_load.items():
                    if key not in ['NO', 'TYPE', 'DRAWING', 'DISPFLG'] and value:
                        print(f"     * {key} = {value}")
            else:
                print(f"   - 未找到该型号的load定义")
        else:
            print("   - 无法获取load数据")
    else:
        print(f"   - 未找到型号 '{test_model}' 的定义")
    
    print("\n" + "="*50)
    print("QR码解析和UI控件生成功能演示完成！")
    print("\n使用方法:")
    print("1. 在条码输入框中扫描QR码或输入型号")
    print("2. 按回车键或点击发送按钮")
    print("3. 系统将自动解析型号并生成对应UI控件")

if __name__ == "__main__":
    demo_qr_functionality()
