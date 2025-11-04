#!/usr/bin/env python3
"""
测试配置加载过程
"""

import sys
import os
sys.path.append('.')

from src.core.config import ConfigManager
from src.data.csv_processor import CSVProcessor

def test_config_loading():
    """测试配置加载过程"""
    print("=== 测试配置加载过程 ===")
    
    # 1. 初始化配置管理器
    config_manager = ConfigManager('config/')
    
    # 2. 直接测试CSV文件读取
    print("\n1. 直接读取ini.csv文件:")
    csv_processor = CSVProcessor(config_manager)
    ini_data = csv_processor.read_config_csv_as_dict('ini.csv')
    print(f"ini.csv数据行数: {len(ini_data)}")
    
    # 查找MODELplc配置
    model_plc_found = False
    for row in ini_data:
        define = row.get('DEFINE')
        value = row.get('VALUE')
        print(f"  DEFINE: {define}, VALUE: {value}")
        if define == 'MODELplc':
            model_plc_found = True
            print(f"  *** 找到MODELplc配置: {value} ***")
    
    if not model_plc_found:
        print("  *** 未找到MODELplc配置 ***")
    
    # 3. 测试配置管理器加载
    print("\n2. 配置管理器加载:")
    success = config_manager.load_config()
    print(f"配置加载结果: {success}")
    
    # 4. 检查最终配置值
    print("\n3. 最终配置值:")
    print(f"QR模式: {config_manager.qr_config.qr_mode}")
    print(f"型号位置: {config_manager.qr_config.model_place}")
    print(f"分隔符: '{config_manager.qr_config.qr_split_str}'")
    print(f"PO位置: {config_manager.qr_config.po_place}")
    print(f"数量位置: {config_manager.qr_config.qty_place}")
    
    # 5. 验证配置一致性
    print("\n4. 配置一致性验证:")
    consistency = config_manager.validate_config_consistency()
    for issue in consistency.get('consistency_issues', []):
        print(f"  ! {issue}")

if __name__ == "__main__":
    test_config_loading()
