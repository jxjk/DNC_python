# DNC系统Python项目文档

## 项目概述

DNC系统是基于Python重构的数控设备参数管理系统，用于从二维码识别型号、匹配程序、计算参数，并通过NC协议发送到数控机床。

## 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行系统
```bash
python main.py
```

## 系统架构

### 模块结构
- **core/**: 核心应用模块
- **ui/**: 用户界面模块
- **business/**: 业务逻辑模块
- **data/**: 数据访问模块
- **communication/**: 通信模块
- **utils/**: 工具模块

### 配置文件
- **config/ini.csv**: 系统配置
- **config/type_define.csv**: 型号定义
- **config/load.csv**: 程序参数
- **config/calc.csv**: 计算逻辑
- **config/relation.csv**: 关系验证

## 开发指南

### 代码规范
- 使用类型注解
- 遵循PEP8规范
- 编写单元测试

### 测试
```bash
pytest tests/
```

## 部署说明

### 环境要求
- Python 3.8+
- Windows/Linux/macOS

### 配置说明
编辑config/ini.csv文件配置系统参数：
- QRmode: 二维码识别模式
- QRspltStr: 分隔符
- MODELplc: 型号位置
- AutoSend: 自动发送
