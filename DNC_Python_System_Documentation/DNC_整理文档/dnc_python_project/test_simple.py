#!/usr/bin/env python3
"""
简单测试脚本
"""

import sys
import os

print("Python版本:", sys.version)
print("当前工作目录:", os.getcwd())
print("Python路径:", sys.path)

# 测试基本导入
try:
    import pytest
    print("✓ pytest导入成功")
except ImportError as e:
    print("✗ pytest导入失败:", e)

try:
    import unittest
    print("✓ unittest导入成功")
except ImportError as e:
    print("✗ unittest导入失败:", e)

# 测试项目模块导入
try:
    from src.core.config import ConfigManager
    print("✓ ConfigManager导入成功")
except ImportError as e:
    print("✗ ConfigManager导入失败:", e)

try:
    from src.data.csv_processor import CSVProcessor
    print("✓ CSVProcessor导入成功")
except ImportError as e:
    print("✗ CSVProcessor导入失败:", e)

print("简单测试完成")
