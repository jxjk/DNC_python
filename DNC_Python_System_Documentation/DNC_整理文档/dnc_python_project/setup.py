#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DNC Python 系统安装程序
"""

import os
import sys
import shutil
import platform
from setuptools import setup, find_packages
from pathlib import Path


def get_version():
    """获取版本号"""
    return "1.0.0"


def get_long_description():
    """获取长描述"""
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()


def create_requirements():
    """创建依赖文件"""
    requirements = [
        "PyQt5>=5.15.0",
        "pyserial>=3.5",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "openpyxl>=3.0.0",
        "pyyaml>=6.0",
        "requests>=2.25.0",
        "psutil>=5.8.0",
        "colorama>=0.4.4",
        "tqdm>=4.62.0",
        "pillow>=8.3.0",
        "matplotlib>=3.4.0",
        "scipy>=1.7.0"
    ]
    
    # 写入requirements.txt
    with open("requirements.txt", "w", encoding="utf-8") as f:
        for req in requirements:
            f.write(f"{req}\n")
    
    return requirements


def create_directories():
    """创建必要的目录结构"""
    directories = [
        "config",
        "logs",
        "data",
        "data/programs",
        "data/models",
        "data/templates",
        "temp",
        "backup"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ 创建目录: {directory}")


def copy_config_files():
    """复制配置文件"""
    config_files = {
        "config/default_config.yaml": "config/default_config.yaml",
        "config/device_config.yaml": "config/device_config.yaml",
        "config/ui_config.yaml": "config/ui_config.yaml"
    }
    
    for src, dst in config_files.items():
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"✓ 复制配置文件: {dst}")
        else:
            print(f"⚠ 配置文件不存在: {src}")


def create_shortcuts():
    """创建快捷方式"""
    system = platform.system()
    
    if system == "Windows":
        _create_windows_shortcut()
    elif system == "Linux":
        _create_linux_shortcut()
    elif system == "Darwin":  # macOS
        _create_macos_shortcut()
    else:
        print(f"⚠ 不支持的操作系统: {system}")


def _create_windows_shortcut():
    """创建Windows快捷方式"""
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        shortcut_path = os.path.join(desktop, "DNC Python 系统.lnk")
        
        target = sys.executable
        w_dir = os.path.dirname(os.path.abspath(__file__))
        icon = os.path.join(w_dir, "assets", "icon.ico")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target
        shortcut.Arguments = '-m src.main'
        shortcut.WorkingDirectory = w_dir
        if os.path.exists(icon):
            shortcut.IconLocation = icon
        shortcut.save()
        
        print("✓ 创建Windows桌面快捷方式")
    except ImportError:
        print("⚠ 无法创建Windows快捷方式，缺少必要的库")


def _create_linux_shortcut():
    """创建Linux快捷方式"""
    desktop_file = os.path.expanduser("~/.local/share/applications/dnc-python.desktop")
    
    desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=DNC Python 系统
Comment=DNC Python 数控系统
Exec={sys.executable} -m src.main
Path={os.path.dirname(os.path.abspath(__file__))}
Icon={os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.png")}
Terminal=false
StartupNotify=true
Categories=Development;
"""
    
    try:
        with open(desktop_file, "w", encoding="utf-8") as f:
            f.write(desktop_content)
        os.chmod(desktop_file, 0o755)
        print("✓ 创建Linux桌面快捷方式")
    except Exception as e:
        print(f"⚠ 创建Linux快捷方式失败: {e}")


def _create_macos_shortcut():
    """创建macOS快捷方式"""
    print("⚠ macOS快捷方式创建需要手动配置")


def check_dependencies():
    """检查依赖"""
    print("检查系统依赖...")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ Python版本需要3.8或更高")
        sys.exit(1)
    else:
        print(f"✓ Python版本: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # 检查操作系统
    system = platform.system()
    print(f"✓ 操作系统: {system} {platform.release()}")
    
    # 检查磁盘空间
    try:
        total, used, free = shutil.disk_usage(".")
        free_gb = free // (2**30)
        if free_gb < 1:
            print("⚠ 磁盘空间不足，建议至少有1GB可用空间")
        else:
            print(f"✓ 可用磁盘空间: {free_gb} GB")
    except:
        print("⚠ 无法检查磁盘空间")


def install_dependencies():
    """安装依赖"""
    print("安装Python依赖...")
    
    requirements_file = "requirements.txt"
    if os.path.exists(requirements_file):
        os.system(f"{sys.executable} -m pip install -r {requirements_file}")
        print("✓ 依赖安装完成")
    else:
        print("⚠ 依赖文件不存在")


def main():
    """主安装函数"""
    print("=" * 50)
    print("DNC Python 系统安装程序")
    print("=" * 50)
    
    # 检查依赖
    check_dependencies()
    
    # 创建目录结构
    print("\n创建目录结构...")
    create_directories()
    
    # 创建依赖文件
    print("\n生成依赖文件...")
    create_requirements()
    
    # 复制配置文件
    print("\n复制配置文件...")
    copy_config_files()
    
    # 安装依赖
    print("\n安装Python依赖...")
    install_dependencies()
    
    # 创建快捷方式
    print("\n创建快捷方式...")
    create_shortcuts()
    
    print("\n" + "=" * 50)
    print("安装完成！")
    print("=" * 50)
    print("\n使用方法:")
    print("1. 双击桌面快捷方式启动程序")
    print("2. 或运行命令: python -m src.main")
    print("3. 或运行命令: python main.py")
    print("\n配置目录: config/")
    print("数据目录: data/")
    print("日志目录: logs/")
    print("\n如需卸载，请运行: python setup.py uninstall")


def uninstall():
    """卸载程序"""
    print("=" * 50)
    print("DNC Python 系统卸载程序")
    print("=" * 50)
    
    confirm = input("确定要卸载DNC Python系统吗？(y/N): ")
    if confirm.lower() != 'y':
        print("取消卸载")
        return
    
    # 删除创建的目录
    directories_to_remove = [
        "config",
        "logs",
        "data",
        "temp",
        "backup",
        "__pycache__",
        "src/__pycache__",
        "src/core/__pycache__",
        "src/business/__pycache__",
        "src/ui/__pycache__",
        "tests/__pycache__"
    ]
    
    for directory in directories_to_remove:
        if os.path.exists(directory):
            try:
                shutil.rmtree(directory)
                print(f"✓ 删除目录: {directory}")
            except Exception as e:
                print(f"⚠ 删除目录失败 {directory}: {e}")
    
    # 删除生成的文件
    files_to_remove = [
        "requirements.txt",
        "dnc_python_system.log"
    ]
    
    for file in files_to_remove:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"✓ 删除文件: {file}")
            except Exception as e:
                print(f"⚠ 删除文件失败 {file}: {e}")
    
    print("\n卸载完成！")
    print("注意: Python包依赖需要手动卸载")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "uninstall":
        uninstall()
    else:
        main()
