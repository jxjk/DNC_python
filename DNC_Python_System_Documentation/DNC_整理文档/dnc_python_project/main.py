#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DNC Python 系统主程序入口
"""

import sys
import os
import logging
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.application import DNCApplication


def setup_logging():
    """设置日志系统"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / "dnc_python_system.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger("DNCSystem")
    logger.info("DNC Python 系统启动")
    
    return logger


def check_environment():
    """检查运行环境"""
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("错误: Python版本需要3.8或更高")
        sys.exit(1)
    
    # 检查必要的目录
    required_dirs = ["config", "data", "logs"]
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"创建目录: {dir_name}")
    
    # 检查配置文件
    config_files = ["config/default_config.yaml", "config/device_config.yaml"]
    for config_file in config_files:
        if not Path(config_file).exists():
            print(f"警告: 配置文件不存在: {config_file}")


def main():
    """主函数"""
    print("=" * 50)
    print("DNC Python 数控系统")
    print("版本: 1.0.0")
    print("=" * 50)
    
    # 检查环境
    check_environment()
    
    # 设置日志
    logger = setup_logging()
    
    try:
        # 创建应用程序
        app = DNCApplication()
        
        # 启动应用程序
        app.start()
        
        # 显示主窗口
        app.show_main_window()
        
        logger.info("DNC Python 系统启动成功")
        
        # 运行应用程序
        return app.run()
        
    except Exception as e:
        logger.error(f"系统启动失败: {e}")
        print(f"系统启动失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
