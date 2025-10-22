@echo off
chcp 65001 >nul
title DNC参数计算系统 v2.05

echo ========================================
echo    DNC参数计算系统 - Python版本
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查依赖包
echo 检查依赖包...
python -c "import pandas, openpyxl, configparser" >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo 依赖包安装失败，请手动运行: pip install -r requirements.txt
        pause
        exit /b 1
    )
)

REM 运行应用程序
echo 启动DNC参数计算系统...
python main.py

if errorlevel 1 (
    echo.
    echo 应用程序运行失败，请检查日志文件: logs\dnc_system.log
    pause
) else (
    echo.
    echo 应用程序已正常退出
)

pause
