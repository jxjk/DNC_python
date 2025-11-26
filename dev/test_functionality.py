#!/usr/bin/env python3
"""
测试DNC Python程序核心功能的脚本
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试各个模块是否可以正确导入"""
    print("测试模块导入...")
    try:
        from src.config.config_manager import ConfigManager
        print("✓ ConfigManager 导入成功")
    except Exception as e:
        print(f"✗ ConfigManager 导入失败: {e}")
        return False

    try:
        from src.data.data_manager import DataManager
        print("✓ DataManager 导入成功")
    except Exception as e:
        print(f"✗ DataManager 导入失败: {e}")
        return False

    try:
        from src.utils.calculation import CalculationEngine
        print("✓ CalculationEngine 导入成功")
    except Exception as e:
        print(f"✗ CalculationEngine 导入失败: {e}")
        return False

    try:
        from src.data.csv_processor import CSVProcessor
        print("✓ CSVProcessor 导入成功")
    except Exception as e:
        print(f"✗ CSVProcessor 导入失败: {e}")
        return False

    return True

def test_config_loading():
    """测试配置加载"""
    print("\n测试配置加载...")
    try:
        from src.config.config_manager import ConfigManager
        config_manager = ConfigManager()
        success = config_manager.load_config()
        if success:
            print("✓ 配置加载成功")
            return True
        else:
            print("✗ 配置加载失败")
            return False
    except Exception as e:
        print(f"✗ 配置加载异常: {e}")
        return False

def test_data_loading():
    """测试数据加载"""
    print("\n测试数据加载...")
    try:
        from src.config.config_manager import ConfigManager
        from src.data.data_manager import DataManager

        config_manager = ConfigManager()
        config_manager.load_config()
        data_manager = DataManager(config_manager)
        success = data_manager.load_csv_files()
        if success:
            print("✓ CSV文件加载成功")
            print(f"  - 产品类型数量: {len(data_manager.get_all_product_types())}")
            stats = data_manager.get_statistics()
            print(f"  - 加载文件数: {stats['loaded_files']}")
            print(f"  - 总记录数: {stats['total_records']}")
            return True
        else:
            print("✗ CSV文件加载失败")
            return False
    except Exception as e:
        print(f"✗ 数据加载异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_calculation_engine():
    """测试计算引擎"""
    print("\n测试计算引擎...")
    try:
        from src.utils.calculation import CalculationEngine

        calc_engine = CalculationEngine()
        # 测试基本计算
        result = calc_engine._calculate_volume({'length': 10, 'width': 5, 'height': 3})
        if result == 150:
            print("✓ 体积计算成功")
        else:
            print(f"✗ 体积计算结果异常: {result}")

        # 测试表达式计算
        variables = {'length': 10, 'width': 5}
        result = calc_engine.evaluate_expression('length * width', variables)
        if result == 50:
            print("✓ 表达式计算成功")
        else:
            print(f"✗ 表达式计算结果异常: {result}")

        return True
    except Exception as e:
        print(f"✗ 计算引擎异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始测试DNC Python程序核心功能...")
    print("="*50)

    success_count = 0
    total_tests = 4

    if test_imports():
        success_count += 1

    if test_config_loading():
        success_count += 1

    if test_data_loading():
        success_count += 1

    if test_calculation_engine():
        success_count += 1

    print("\n"+"="*50)
    print(f"测试完成: {success_count}/{total_tests} 项测试通过")

    if success_count == total_tests:
        print("🎉 所有测试都通过了！程序核心功能正常。")
    else:
        print("⚠️  部分测试未通过，请检查相关模块。")

if __name__ == "__main__":
    main()
