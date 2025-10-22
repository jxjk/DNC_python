# DNC参数计算系统 - 安装指南

## 系统要求

### 操作系统
- Windows 10/11 (推荐)
- Linux (Ubuntu 18.04+ / CentOS 7+)
- macOS 10.15+

### Python版本
- Python 3.8 或更高版本

### 硬件要求
- 内存: 4GB RAM (推荐8GB)
- 存储空间: 500MB 可用空间
- 显示器: 1280x720 分辨率或更高

## 安装步骤

### 1. 安装Python
如果系统中没有安装Python，请从 [Python官网](https://www.python.org/downloads/) 下载并安装。

### 2. 下载项目
```bash
# 从Git仓库克隆
git clone <repository-url>
cd DNC_Python_Project

# 或者直接下载ZIP文件并解压
```

### 3. 安装依赖包
```bash
# 使用pip安装依赖
pip install -r requirements.txt

# 或者使用conda
conda install --file requirements.txt
```

### 4. 配置环境
项目会自动创建必要的目录结构：
- `data/` - 数据文件目录
- `logs/` - 日志文件目录  
- `output/` - 输出文件目录
- `config/` - 配置文件目录

### 5. 复制Master数据
系统会自动从原始VB.NET项目的master目录复制数据文件。如果自动复制失败，请手动将 `ID67(2024731)addE/master/` 目录下的所有文件复制到 `DNC_Python_Project/data/master/` 目录。

## 运行应用程序

### 方法1: 直接运行Python脚本
```bash
python main.py
```

### 方法2: 使用批处理文件 (Windows)
双击运行 `run.bat` 文件

### 方法3: 使用启动脚本 (Linux/macOS)
```bash
chmod +x run.sh
./run.sh
```

## 首次使用配置

### 1. 检查数据加载
首次运行时，系统会：
- 自动加载master数据文件
- 验证数据完整性
- 显示产品目录

### 2. 输入文件格式
创建输入CSV文件，格式如下：
```csv
product_id,model,quantity
P001,MODEL_A,10
P002,MODEL_B,5
P003,MODEL_C,8
```

### 3. 处理流程
1. 选择输入CSV文件
2. 系统自动匹配产品型号
3. 计算几何参数
4. 显示计算结果
5. 导出结果文件

## 故障排除

### 常见问题

#### 1. 依赖包安装失败
```bash
# 尝试使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 2. 数据文件找不到
- 检查 `data/master/` 目录是否存在
- 确认原始master数据文件已正确复制

#### 3. 界面显示异常
- 检查系统字体是否支持中文字体
- 尝试调整窗口大小

#### 4. 计算错误
- 检查输入文件格式是否正确
- 验证产品型号是否在master数据中定义

### 日志文件
系统运行日志保存在 `logs/dnc_system.log` 文件中，可用于故障诊断。

## 开发环境设置

### 1. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### 2. 安装开发依赖
```bash
pip install -r requirements.txt
```

### 3. 代码格式化
```bash
# 使用black格式化代码
black src/

# 使用pylint检查代码质量
pylint src/
```

### 4. 运行测试
```bash
pytest tests/
```

## 打包发布

### 创建可执行文件
```bash
pyinstaller --onefile --windowed main.py
```

### 创建安装包
```bash
python setup.py sdist bdist_wheel
```

## 技术支持

如果遇到问题，请：
1. 查看日志文件 `logs/dnc_system.log`
2. 检查系统要求是否满足
3. 确认依赖包版本兼容性
4. 联系技术支持团队

## 更新日志

### v2.05 (当前版本)
- 基于原始VB.NET项目DNC2.05重写
- 增加CSV输入文件支持
- 改进用户界面
- 增强错误处理
- 支持批量处理
