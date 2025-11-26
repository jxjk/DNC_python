# 测试接口文件监控功能
import time
from pathlib import Path
import hashlib

# 测试接口文件路径
interface_path = Path("interface/input.txt")
interface_path.parent.mkdir(parents=True, exist_ok=True)

print(f"接口文件路径: {interface_path}")
print(f"接口文件是否存在: {interface_path.exists()}")

# 获取初始修改时间和内容哈希
if interface_path.exists():
    initial_mtime = interface_path.stat().st_mtime
    with open(interface_path, 'r', encoding='utf-8') as f:
        initial_content = f.read()
    initial_hash = hashlib.md5(initial_content.encode('utf-8')).hexdigest()
    
    print(f"初始修改时间: {initial_mtime}")
    print(f"初始内容哈希: {initial_hash}")
    print(f"初始内容: '{initial_content}'")
else:
    print("接口文件不存在，将被创建")

# 写入测试内容
test_content = "123@GPA20GT15040-A-H8@3"
print(f"\n写入测试内容: {test_content}")

with open(interface_path, 'w', encoding='utf-8') as f:
    f.write(test_content)

# 等待一小段时间让监控检测到变化
time.sleep(0.1)

# 检查文件是否被清空（表示被监控程序处理了）
with open(interface_path, 'r', encoding='utf-8') as f:
    current_content = f.read()

print(f"写入后文件内容: '{current_content}'")

if current_content == "":
    print("✓ 接口文件已被清空，表示被监控程序处理")
else:
    print("✗ 接口文件未被清空，监控程序可能未工作")

# 再次写入内容测试
print(f"\n再次写入测试内容: {test_content}")
with open(interface_path, 'w', encoding='utf-8') as f:
    f.write(test_content)

time.sleep(0.1)

with open(interface_path, 'r', encoding='utf-8') as f:
    current_content = f.read()

print(f"再次写入后文件内容: '{current_content}'")

if current_content == "":
    print("✓ 接口文件再次被清空，监控程序工作正常")
else:
    print("✗ 接口文件未被清空，监控程序可能未工作")

print("\n测试完成")