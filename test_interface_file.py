# 测试接口文件监控功能
import sys
import os
import time
from pathlib import Path

# 创建测试接口文件
interface_path = Path("interface/input.txt")
interface_path.parent.mkdir(parents=True, exist_ok=True)

print(f"创建测试接口文件: {interface_path}")

# 测试写入内容
test_content = "GPT25GT3060-A-H8"
interface_path.write_text(test_content, encoding='utf-8')
print(f"已写入测试内容: {test_content}")

# 检查文件内容
content = interface_path.read_text(encoding='utf-8')
print(f"读取到的内容: '{content}'")

# 清空文件
interface_path.write_text("", encoding='utf-8')
print("已清空接口文件")

print("接口文件功能测试完成")