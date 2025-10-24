@echo off
echo 正在安装DNC系统依赖...

:: 创建虚拟环境
python -m venv venv
call venv\Scripts\activate.bat

:: 安装依赖
pip install -r requirements.txt

echo 安装完成！
echo 请运行: python main.py 启动系统
pause
