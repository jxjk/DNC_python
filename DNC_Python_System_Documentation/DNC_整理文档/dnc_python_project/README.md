# DNC Python 数控系统

## 项目概述

DNC Python 系统是一个基于Python和PyQt5开发的数控设备管理和加工程序传输系统。该系统提供了完整的数控设备管理、加工程序匹配、参数计算和设备通信功能。

## 系统架构

### 模块结构

```
dnc_python_project/
├── src/                    # 源代码目录
│   ├── core/              # 核心模块
│   │   ├── application.py     # 应用程序主类
│   │   ├── config.py          # 配置管理器
│   │   └── event_dispatcher.py # 事件分发器
│   ├── business/          # 业务逻辑模块
│   │   ├── model_recognizer.py   # 型号识别器
│   │   ├── program_matcher.py    # 程序匹配器
│   │   ├── calculation_engine.py # 计算引擎
│   │   └── nc_communicator.py    # NC通信器
│   └── ui/                # 用户界面模块
│       ├── main_window.py        # 主窗口
│       ├── parameter_input.py    # 参数输入对话框
│       ├── program_display.py    # 程序显示组件
│       └── status_monitor.py     # 状态监控组件
├── tests/                 # 测试代码
│   ├── test_core.py      # 核心模块测试
│   ├── test_business.py  # 业务逻辑测试
│   └── test_ui.py        # 用户界面测试
├── config/               # 配置文件目录
├── data/                 # 数据文件目录
├── logs/                 # 日志文件目录
├── main.py               # 主程序入口
├── setup.py              # 安装部署程序
└── README.md             # 项目说明文档
```

## 功能特性

### 核心功能

1. **设备型号识别**
   - 根据几何参数自动识别设备型号
   - 支持多种材料类型识别
   - 智能参数匹配算法

2. **加工程序匹配**
   - 基于型号自动匹配加工程序
   - 程序库管理和搜索
   - 程序版本控制

3. **加工参数计算**
   - 自动计算加工参数
   - 参数验证和优化
   - 支持多种加工工艺

4. **NC设备通信**
   - 支持多种通信协议
   - 实时状态监控
   - 程序传输和接收

5. **用户界面**
   - 现代化的PyQt5界面
   - 参数输入和验证
   - 程序显示和编辑
   - 设备状态监控

## 安装部署

### 系统要求

- Python 3.8 或更高版本
- Windows 10/11, Linux, 或 macOS
- 至少 1GB 可用磁盘空间

### 安装步骤

1. **下载项目**
   ```bash
   git clone <项目地址>
   cd dnc_python_project
   ```

2. **运行安装程序**
   ```bash
   python setup.py
   ```

3. **手动安装（可选）**
   ```bash
   pip install -r requirements.txt
   ```

### 启动系统

1. **使用快捷方式**
   - 双击桌面快捷方式 "DNC Python 系统"

2. **使用命令行**
   ```bash
   python main.py
   # 或
   python -m src.main
   ```

## 使用说明

### 基本操作流程

1. **启动系统**
   - 系统启动后显示主窗口
   - 自动加载配置和设备信息

2. **输入加工参数**
   - 点击"参数输入"按钮
   - 填写工件几何参数
   - 选择材料和工艺类型

3. **识别设备型号**
   - 系统自动识别设备型号
   - 显示匹配的型号信息

4. **匹配加工程序**
   - 系统自动匹配加工程序
   - 显示程序内容和参数

5. **连接设备**
   - 配置设备通信参数
   - 建立与数控设备的连接

6. **传输程序**
   - 发送加工程序到设备
   - 监控传输状态

7. **监控运行**
   - 实时监控设备状态
   - 查看错误日志和报警信息

### 配置管理

系统配置文件位于 `config/` 目录：

- `default_config.yaml` - 默认系统配置
- `device_config.yaml` - 设备通信配置
- `ui_config.yaml` - 用户界面配置

## 测试

### 运行测试

```bash
# 运行所有测试
python -m unittest discover tests

# 运行特定测试模块
python -m unittest tests.test_core
python -m unittest tests.test_business
python -m unittest tests.test_ui
```

### 测试覆盖

- **核心模块测试**: 配置管理、事件分发、应用程序
- **业务逻辑测试**: 型号识别、程序匹配、参数计算、设备通信
- **用户界面测试**: 对话框、组件功能、信号连接

## 开发指南

### 代码规范

- **类名**: PascalCase (如: MainWindow, ParameterInputDialog)
- **方法名**: snake_case (如: _init_ui, get_parameters)
- **属性名**: snake_case (如: config_manager, logger)
- **信号名**: snake_case (如: parameters_changed, model_changed)

### 扩展开发

1. **添加新的业务模块**
   - 在 `src/business/` 目录创建新模块
   - 实现相应的接口和方法
   - 在 `application.py` 中注册模块

2. **添加新的UI组件**
   - 在 `src/ui/` 目录创建新组件
   - 继承相应的Qt基类
   - 在主窗口中集成组件

3. **添加新的通信协议**
   - 扩展 `NCCommunicator` 类
   - 实现新的通信方法
   - 更新配置文件

## 故障排除

### 常见问题

1. **无法启动程序**
   - 检查Python版本是否为3.8+
   - 检查依赖包是否安装完整
   - 查看日志文件 `logs/dnc_python_system.log`

2. **设备连接失败**
   - 检查设备IP地址和端口
   - 确认网络连接正常
   - 检查防火墙设置

3. **程序匹配失败**
   - 检查参数输入是否正确
   - 确认程序库文件存在
   - 查看型号识别日志

### 日志文件

系统日志位于 `logs/dnc_python_system.log`，包含：
- 系统启动和关闭信息
- 设备连接状态
- 程序传输记录
- 错误和警告信息

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

## 技术支持

如有问题或建议，请联系：
- 邮箱: support@example.com
- 项目地址: https://github.com/example/dnc-python-system

## 版本历史

### v1.0.0 (2024-10-24)
- 初始版本发布
- 完成核心功能模块
- 实现完整的用户界面
- 添加测试和部署程序
