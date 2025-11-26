# 测试自动发送数据功能
import time
from pathlib import Path

# 测试接口文件路径
interface_path = Path("interface/input.txt")
interface_path.parent.mkdir(parents=True, exist_ok=True)

print(f"接口文件路径: {interface_path}")

# 写入测试内容 - QR码格式
test_content = "123@GPA20GT15040-A-H8@3"
print(f"写入测试内容: {test_content}")

with open(interface_path, 'w', encoding='utf-8') as f:
    f.write(test_content)

print("已写入接口文件，系统将在处理后1.5秒自动发送数据")

# 等待一段时间让系统处理
time.sleep(3)

# 检查文件是否被清空
with open(interface_path, 'r', encoding='utf-8') as f:
    current_content = f.read()

if current_content == "":
    print("✓ 接口文件已被清空，表示被系统处理")
else:
    print(f"✗ 接口文件未被清空，内容: '{current_content}'")

print("测试完成")