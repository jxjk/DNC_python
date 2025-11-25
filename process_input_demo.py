#!/usr/bin/env python3
"""
处理输入CSV文件的示例
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config.config_manager import ConfigManager
from src.data.data_manager import DataManager

def main():
    print("DNC Python程序 - 输入文件处理示例")
    print("="*50)
    
    # 初始化
    print("1. 初始化配置和数据管理器...")
    config_manager = ConfigManager()
    config_manager.load_config()
    data_manager = DataManager(config_manager)
    data_manager.load_csv_files()
    print(f"   ✓ 加载了 {len(data_manager.get_all_product_types())} 种产品类型")
    
    # 处理输入文件
    print("\n2. 处理输入文件 sample_input.csv...")
    valid_records, error_messages = data_manager.process_input_file("sample_input.csv")
    
    print(f"   ✓ 有效记录数: {len(valid_records)}")
    print(f"   ✓ 错误消息数: {len(error_messages)}")
    
    if error_messages:
        print("   错误详情:")
        for msg in error_messages:
            print(f"     - {msg}")
    
    # 显示处理结果
    print("\n3. 处理结果:")
    for i, record in enumerate(valid_records, 1):
        print(f"   记录 {i}:")
        print(f"     产品编号: {record['product_id']}")
        print(f"     型号: {record['model']}")
        print(f"     数量: {record['quantity']}")
        print(f"     计算参数: {list(record['calculated_params'].keys()) if record['calculated_params'] else '无'}")
        if record['calculated_params']:
            calc_params = record['calculated_params']
            print(f"     - 体积: {calc_params.get('volume', 'N/A')}")
            print(f"     - 表面积: {calc_params.get('surface_area', 'N/A')}")
            print(f"     - 重量: {calc_params.get('weight', 'N/A')}")
        print()
    
    # 尝试保存结果
    print("4. 保存处理结果到 output.csv...")
    try:
        success = data_manager.save_data(valid_records, "output.csv", "csv")
        if success:
            print("   ✓ 结果保存成功")
        else:
            print("   ✗ 结果保存失败")
    except Exception as e:
        print(f"   ✗ 保存结果时出错: {e}")
    
    print("\n"+"="*50)
    print("输入文件处理示例完成！")

if __name__ == "__main__":
    main()
