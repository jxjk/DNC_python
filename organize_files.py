import os
import shutil
from pathlib import Path

def organize_project():
    project_dir = Path(r'C:\Users\Lenovo\Desktop\DNC_python')
    
    print("开始整理项目文件...")
    
    # 1. 确保dev目录存在
    dev_dir = project_dir / 'dev'
    dev_dir.mkdir(exist_ok=True)
    print(f"创建目录: {dev_dir}")
    
    # 2. 移动所有test_*.py文件到dev目录
    test_files = list(project_dir.glob('test_*.py'))
    print(f"找到 {len(test_files)} 个测试文件")
    for test_file in test_files:
        dest_path = dev_dir / test_file.name
        shutil.move(str(test_file), str(dest_path))
        print(f"  移动: {test_file.name} -> dev/")
    
    # 3. 移动所有demo*.py文件到dev目录
    demo_files = list(project_dir.glob('demo*.py'))
    demo_files.append(project_dir / 'process_input_demo.py')  # 添加特定文件
    demo_files = [f for f in demo_files if f.exists()]  # 确保文件存在
    print(f"找到 {len(demo_files)} 个演示文件")
    for demo_file in demo_files:
        dest_path = dev_dir / demo_file.name
        shutil.move(str(demo_file), str(dest_path))
        print(f"  移动: {demo_file.name} -> dev/")
    
    # 4. 移动开发文档到docs/dev目录
    docs_dev_dir = project_dir / 'docs' / 'dev'
    sw_doc = project_dir / '软件开发文档.md'
    if sw_doc.exists():
        dest_path = docs_dev_dir / sw_doc.name
        shutil.move(str(sw_doc), str(dest_path))
        print(f"  移动: {sw_doc.name} -> docs/dev/")
    
    # 5. 移动用户说明书到docs/user目录
    docs_user_dir = project_dir / 'docs' / 'user'
    user_doc = project_dir / '用户说明书.md'
    if user_doc.exists():
        dest_path = docs_user_dir / user_doc.name
        shutil.move(str(user_doc), str(dest_path))
        print(f"  移动: {user_doc.name} -> docs/user/")
    
    print("\n整理完成！")
    
    # 显示整理后的结构
    print("\n当前根目录文件 (不包括目录):")
    for item in project_dir.iterdir():
        if item.is_file():
            print(f"  {item.name}")
    
    print(f"\ndev/ 目录内容:")
    if dev_dir.exists():
        for item in dev_dir.iterdir():
            print(f"  {item.name}")
    else:
        print("  目录不存在")
    
    print(f"\ndocs/dev/ 目录内容:")
    if docs_dev_dir.exists():
        for item in docs_dev_dir.iterdir():
            print(f"  {item.name}")
    else:
        print("  目录不存在")
    
    print(f"\ndocs/user/ 目录内容:")
    if docs_user_dir.exists():
        for item in docs_user_dir.iterdir():
            print(f"  {item.name}")
    else:
        print("  目录不存在")

if __name__ == "__main__":
    organize_project()