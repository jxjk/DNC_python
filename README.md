# DNC参数计算系统

## 项目概述

DNC参数计算系统是一个基于Python的参数化计算工具，用于处理产品数据、计算几何参数并生成宏变量输出。系统支持从CSV文件导入数据，匹配产品型号，并根据预定义规则计算输出宏变量。

## 功能特性

### 核心功能
- **型号匹配**：支持从后往前逐字符删除的型号匹配算法，兼容连字符和下划线格式
- **数据处理**：支持从CSV文件导入和导出数据
- **几何计算**：自动计算产品几何参数（体积、表面积、重量等）
- **宏变量输出**：根据配置规则生成macro.txt文件

### 界面功能
- **条码/QR码输入**：支持PO@型号@数量格式的QR码输入
- **程序控制**：支持多程序（prg1, prg2, prg3）切换
- **控件类型**：支持load、input、measure、select、relation、switch、correct等多种控件类型
- **状态监控**：实时状态显示和错误提示

### 接口功能
- **上位调度软件接口**：监控interface/input.txt文件变更，自动处理输入数据
- **自动发送数据**：接口文件输入自动触发数据发送，扫码枪输入不自动发送

## 系统架构

### 核心模块
- `MainWindow`：用户界面核心类
- `DataManager`：数据管理核心类  
- `CalculationEngine`：计算引擎核心类
- `ConfigManager`：配置管理类
- `CSVProcessor`：CSV文件处理类

### 目录结构
```
DNC_python/
├── main.py                 # 主程序入口
├── config/                 # 配置文件
├── data/                   # 数据文件
│   └── master/             # 主数据目录
├── dev/                    # 开发和测试文件
├── docs/                   # 文档
│   ├── dev/                # 开发文档
│   └── user/               # 用户文档
├── interface/              # 接口文件目录
│   └── input.txt           # 接口输入文件
├── logs/                   # 日志文件
├── output/                 # 输出文件
│   └── macro.txt           # 宏变量输出文件
├── src/                    # 源代码
│   ├── config/             # 配置模块
│   ├── data/               # 数据模块
│   ├── ui/                 # 界面模块
│   └── utils/              # 工具模块
└── tests/                  # 测试文件
```

## 快速开始

### 环境要求
- Python 3.7+
- 依赖包见requirements.txt

### 安装依赖
```bash
pip install -r requirements.txt
```

### 启动程序
```bash
python main.py
```

或者使用启动脚本：
```bash
# Windows
run.bat

# Linux/Mac
./run.sh
```

## 使用说明

### 1. 型号输入
- 直接输入型号：`GPA20GT15040_A`
- QR码格式：`PO123@GPA20GT15040_A@5`
- 通过接口文件：将内容写入`interface/input.txt`

### 2. 数据处理
- 选择输入文件并处理
- 查看计算结果
- 导出结果到CSV或Excel

### 3. 程序切换
- 根据type_prg.csv配置自动加载对应程序
- 支持动态加载程序特定控件

### 4. 宏变量输出
- 点击"发送数据"按钮生成macro.txt
- 接口文件输入会自动触发数据发送（延迟1.5秒）

## 数据文件说明

### 主要CSV文件
- `type_define.csv`：产品型号定义
- `load.csv`：负载数据定义
- `cntrl.csv`：控件类型和发送标志
- `relation.csv`：关系表达式定义
- `calc.csv`：计算公式定义
- `input.csv`：输入控件定义
- `switch.csv`：开关控件定义

### 程序配置
- 程序数据存储在`data/master/prg[1-3]/`目录中
- 支持多程序配置和切换

## 接口文件说明

### interface/input.txt
- 自动监控文件变化
- 支持QR码格式输入
- 处理后自动清空文件内容
- 触发自动数据发送功能

## 常见问题

### Q: 型号无法匹配？
A: 检查型号格式，系统支持连字符转下划线匹配

### Q: macro.txt中缺少某些宏变量？
A: 检查cntrl.csv中SENDFLG标志是否设置为1

### Q: 接口文件不工作？
A: 确保interface/input.txt文件存在且有写入权限

## 扩展功能

### 自定义控件类型
- 在cntrl.csv中定义新的控件类型
- 配置对应的显示和发送规则

### 计算公式扩展
- 在calc.csv中添加新的计算公式
- 使用宏变量编号和数学运算符定义公式

## 许可证

[根据项目需要添加许可证信息]