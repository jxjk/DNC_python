#!/bin/bash

echo "正在安装DNC系统依赖..."

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

echo "安装完成！"
echo "请运行: python main.py 启动系统"
