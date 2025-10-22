#!/bin/bash

# DNC参数计算系统 - Linux/macOS启动脚本

echo "========================================"
echo "   DNC参数计算系统 - Python版本"
echo "========================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python 3.8或更高版本"
    echo "下载地址: https://www.python.org/downloads/"
    exit 1
fi

# 检查Python版本
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "错误: Python版本需要3.8或更高，当前版本: $PYTHON_VERSION"
    exit 1
fi

# 检查依赖包
echo "检查依赖包..."
python3 -c "import pandas, openpyxl, configparser" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "正在安装依赖包..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "依赖包安装失败，请手动运行: pip3 install -r requirements.txt"
        exit 1
    fi
fi

# 创建必要的目录
mkdir -p data logs output config

# 运行应用程序
echo "启动DNC参数计算系统..."
python3 main.py

if [ $? -ne 0 ]; then
    echo ""
    echo "应用程序运行失败，请检查日志文件: logs/dnc_system.log"
else
    echo ""
    echo "应用程序已正常退出"
fi
