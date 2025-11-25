#!/usr/bin/env python3
"""
DNC Python程序使用示例
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config.config_manager import ConfigManager
from src.data.data_manager import DataManager
from src.utils.calculation import CalculationEngine

def main():
    print("DNC Python程序使用示例")
    print("="*50)
    
    # 1. 初始化配置管理器
    print("1. 初始化配置管理器...")
    config_manager = ConfigManager()
    config_manager.load_config()
    print(f"   ✓ 配置加载成功")
    
    # 2. 初始化数据管理器
    print("\n2. 初始化数据管理器...")
    data_manager = DataManager(config_manager)
    data_manager.load_csv_files()
    print(f"   ✓ CSV文件加载成功，加载了 {len(data_manager.get_all_product_types())} 种产品类型")
    
    # 3. 查看一些产品类型
    print("\n3. 产品类型示例（前10个）...")
    product_types = data_manager.get_all_product_types()[:10]
    for i, pt in enumerate(product_types, 1):
        print(f"   {i:2d}. {pt}")
    
    # 4. 获取特定产品数据
    print("\n4. 获取第一个产品类型的数据...")
    if product_types:
        first_product = product_types[0]
        product_data = data_manager.get_product_data(first_product)
        if product_data:
            print(f"   产品类型: {first_product}")
            print(f"   参数数量: {len(product_data)}")
            print(f"   前5个参数: {list(product_data.keys())[:5]}")
    
    # 5. 使用计算引擎
    print("\n5. 使用计算引擎进行几何计算...")
    calc_engine = CalculationEngine()
    
    # 计算体积
    volume = calc_engine._calculate_volume({'length': 10, 'width': 5, 'height': 3})
    print(f"   长方体体积 (10×5×3): {volume}")
    
    # 计算表面积
    surface_area = calc_engine._calculate_surface_area({'length': 10, 'width': 5, 'height': 3})
    print(f"   长方体表面积: {surface_area}")
    
    # 计算重量（假设密度为1）
    if volume:
        weight = calc_engine._calculate_weight({'volume': volume, 'density': 1.0})
        print(f"   重量（密度1.0）: {weight}")
    
    # 6. 演示表达式计算
    print("\n6. 表达式计算示例...")
    variables = {'length': 10, 'width': 5, 'height': 3, 'pi': 3.14159}
    expr_result = calc_engine.evaluate_expression('length * width * height', variables)
    print(f"   计算 'length * width * height': {expr_result}")
    
    # 7. 搜索功能演示
    print("\n7. 产品搜索功能...")
    search_results = data_manager.search_products("SC209")
    print(f"   搜索 'SC209' 得到 {len(search_results)} 个结果（前5个）:")
    for result in search_results[:5]:
        print(f"   - {result}")
    
    # 8. 数据统计
    print("\n8. 数据统计信息...")
    stats = data_manager.get_statistics()
    print(f"   - 总产品类型数: {stats['total_product_types']}")
    print(f"   - 加载文件数: {stats['loaded_files']}")
    print(f"   - 总记录数: {stats['total_records']}")
    
    print("\n" + "="*50)
    print("DNC Python程序功能演示完成！")

if __name__ == "__main__":
    main()