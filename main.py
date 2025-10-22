#!/usr/bin/env python3
"""
DNC 参数计算系统 - 主程序入口
基于原始VB.NET项目DNC2.05重写的Python版本
"""

import os
import sys
import logging
from pathlib import Path

# 添加项目路径到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config.config_manager import ConfigManager
from src.data.data_manager import DataManager
from src.ui.main_window import MainWindow

def setup_logging():
    """设置日志配置"""
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "dnc_system.log", encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def check_dependencies():
    """检查依赖项"""
    required_packages = [
        'pandas',
        'openpyxl',
        'tkinter'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'tkinter':
                import tkinter
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
            
    if missing_packages:
        logger = logging.getLogger(__name__)
        logger.error(f"缺少必要的依赖包: {', '.join(missing_packages)}")
        print(f"错误: 缺少必要的依赖包: {', '.join(missing_packages)}")
        print("请使用以下命令安装: pip install pandas openpyxl")
        return False
        
    return True

def initialize_directories():
    """初始化必要的目录"""
    directories = [
        project_root / "data",
        project_root / "logs",
        project_root / "output",
        project_root / "config"
    ]
    
    for directory in directories:
        directory.mkdir(exist_ok=True)
        
    return True

def copy_master_data():
    """复制master数据文件"""
    try:
        # 检查原始master目录
        original_master_dir = project_root.parent / "ID67(2024731)addE" / "master"
        target_master_dir = project_root / "data" / "master"
        
        if original_master_dir.exists():
            import shutil
            
            # 如果目标目录已存在，先删除
            if target_master_dir.exists():
                shutil.rmtree(target_master_dir)
                
            # 复制master数据
            shutil.copytree(original_master_dir, target_master_dir)
            logger = logging.getLogger(__name__)
            logger.info("已成功复制master数据文件")
            return True
        else:
            logger = logging.getLogger(__name__)
            logger.warning("未找到原始master数据目录，将使用空目录")
            target_master_dir.mkdir(exist_ok=True)
            return True
            
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"复制master数据失败: {e}")
        return False

def main():
    """主函数"""
    # 设置日志
    logger = setup_logging()
    logger.info("启动DNC参数计算系统")
    
    # 检查依赖项
    if not check_dependencies():
        logger.error("依赖项检查失败，程序退出")
        return 1
        
    # 初始化目录
    if not initialize_directories():
        logger.error("目录初始化失败，程序退出")
        return 1
        
    # 复制master数据
    if not copy_master_data():
        logger.warning("master数据复制失败，程序将继续运行")
        
    try:
        # 初始化配置管理器
        config_manager = ConfigManager()
        
        # 初始化数据管理器
        data_manager = DataManager(config_manager)
        
        # 创建主窗口
        main_window = MainWindow(config_manager, data_manager)
        
        # 运行应用程序
        logger.info("启动用户界面")
        main_window.run()
        
        logger.info("应用程序正常退出")
        return 0
        
    except Exception as e:
        logger.error(f"应用程序运行失败: {e}")
        print(f"错误: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
