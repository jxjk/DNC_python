#!/usr/bin/env python3
"""
DNC系统验证测试脚本
用于验证系统的基本功能是否正常
"""

import sys
import os
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试模块导入"""
    print("=" * 50)
    print("测试模块导入...")
    print("=" * 50)
    
    modules_to_test = [
        "src.core.application",
        "src.business.model_recognizer", 
        "src.business.program_matcher",
        "src.business.calculation_engine",
        "src.utils.error_handler",
        "src.utils.logger"
    ]
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✓ {module_name} - 导入成功")
        except ImportError as e:
            print(f"✗ {module_name} - 导入失败: {e}")
        except Exception as e:
            print(f"✗ {module_name} - 导入异常: {e}")

def test_config_loading():
    """测试配置加载"""
    print("\n" + "=" * 50)
    print("测试配置加载...")
    print("=" * 50)
    
    try:
        # 检查实际的配置文件
        config_files_to_check = [
            "config/master/header.csv",
            "config/master/ini.csv",
            "config/master/math.csv",
            "config/master/prg.csv",
            "config/master/type_define.csv",
            "config/master/type_prg.csv",
            "config/master/type_relation.csv"
        ]
        
        for config_file in config_files_to_check:
            if os.path.exists(config_file):
                print(f"✓ {config_file} - 存在")
            else:
                print(f"✗ {config_file} - 不存在")
                
        # 检查程序配置文件
        prg_dirs = ["prg1", "prg2", "prg3"]
        for prg_dir in prg_dirs:
            prg_path = f"config/master/{prg_dir}"
            if os.path.exists(prg_path):
                print(f"✓ {prg_path} - 存在")
            else:
                print(f"✗ {prg_path} - 不存在")
                
    except Exception as e:
        print(f"✗ 配置加载失败: {e}")

def test_error_handler():
    """测试错误处理"""
    print("\n" + "=" * 50)
    print("测试错误处理...")
    print("=" * 50)
    
    try:
        from src.utils.error_handler import get_global_error_handler, handle_errors
        
        error_handler = get_global_error_handler()
        print("✓ 全局错误处理器 - 获取成功")
        
        # 测试错误处理装饰器
        @handle_errors
        def test_function():
            return "测试成功"
        
        result = test_function()
        print(f"✓ 错误处理装饰器 - 测试成功: {result}")
        
    except Exception as e:
        print(f"✗ 错误处理测试失败: {e}")

def test_logger():
    """测试日志系统"""
    print("\n" + "=" * 50)
    print("测试日志系统...")
    print("=" * 50)
    
    try:
        from src.utils.logger import get_logger
        
        logger = get_logger("TestLogger")
        print("✓ 日志系统 - 初始化成功")
        
        # 测试日志记录
        logger.info("测试信息日志")
        logger.warning("测试警告日志")
        logger.error("测试错误日志")
        print("✓ 日志记录 - 测试成功")
        
    except Exception as e:
        print(f"✗ 日志系统测试失败: {e}")

def test_business_components():
    """测试业务组件"""
    print("\n" + "=" * 50)
    print("测试业务组件...")
    print("=" * 50)
    
    try:
        from src.business.model_recognizer import ModelRecognizer
        from src.business.program_matcher import ProgramMatcher
        from src.business.calculation_engine import CalculationEngine
        
        # 测试ModelRecognizer
        try:
            model_recognizer = ModelRecognizer()
            print("✓ ModelRecognizer - 初始化成功")
        except Exception as e:
            print(f"✗ ModelRecognizer - 初始化失败: {e}")
        
        # 测试ProgramMatcher
        try:
            program_matcher = ProgramMatcher()
            print("✓ ProgramMatcher - 初始化成功")
        except Exception as e:
            print(f"✗ ProgramMatcher - 初始化失败: {e}")
        
        # 测试CalculationEngine
        try:
            calculation_engine = CalculationEngine()
            print("✓ CalculationEngine - 初始化成功")
        except Exception as e:
            print(f"✗ CalculationEngine - 初始化失败: {e}")
            
    except Exception as e:
        print(f"✗ 业务组件测试失败: {e}")

def test_data_files():
    """测试数据文件"""
    print("\n" + "=" * 50)
    print("测试数据文件...")
    print("=" * 50)
    
    data_files_to_check = [
        "data/calculation_data.csv",
        "data/model_patterns.csv", 
        "data/program_templates.csv"
    ]
    
    for file_path in data_files_to_check:
        if os.path.exists(file_path):
            print(f"✓ {file_path} - 存在")
        else:
            print(f"✗ {file_path} - 不存在")

def main():
    """主测试函数"""
    print("DNC Python系统验证测试")
    print("=" * 50)
    
    # 运行各项测试
    test_imports()
    test_config_loading()
    test_error_handler()
    test_logger()
    test_business_components()
    test_data_files()
    
    print("\n" + "=" * 50)
    print("验证测试完成")
    print("=" * 50)

if __name__ == "__main__":
    main()
