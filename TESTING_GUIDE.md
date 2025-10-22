# DNC参数计算系统 - 测试指南

## 概述

本文档提供了DNC参数计算系统的完整测试指南，包括测试结构、运行方法、测试用例说明和最佳实践。

## 测试结构

```
tests/
├── unit/                    # 单元测试
│   ├── test_models.py      # 数据模型测试
│   ├── test_config.py      # 配置管理测试
│   ├── test_csv_processor.py # CSV处理器测试
│   └── test_calculation.py # 计算引擎测试
├── integration/            # 集成测试
│   └── test_data_flow.py  # 数据流集成测试
├── e2e/                   # 端到端测试
│   └── test_full_workflow.py # 完整工作流测试
├── conftest.py            # 测试配置和fixtures
└── __init__.py
```

## 测试类型说明

### 1. 单元测试 (Unit Tests)

**位置**: `tests/unit/`

**目的**: 测试单个组件或函数的独立功能

**包含的测试**:
- `test_models.py`: 数据模型验证和序列化测试
- `test_config.py`: 配置管理功能测试
- `test_csv_processor.py`: CSV文件读写和验证测试
- `test_calculation.py`: 计算引擎和公式计算测试

### 2. 集成测试 (Integration Tests)

**位置**: `tests/integration/`

**目的**: 测试多个组件之间的交互和数据流

**包含的测试**:
- `test_data_flow.py`: 从配置到计算的完整数据流测试

### 3. 端到端测试 (End-to-End Tests)

**位置**: `tests/e2e/`

**目的**: 测试完整的系统工作流

**包含的测试**:
- `test_full_workflow.py`: 从输入到输出的完整工作流测试

## 运行测试

### 运行所有测试

```bash
# 运行所有测试
pytest

# 运行测试并显示详细输出
pytest -v

# 运行测试并显示覆盖率
pytest --cov=src
```

### 运行特定类型的测试

```bash
# 只运行单元测试
pytest tests/unit/

# 只运行集成测试
pytest tests/integration/

# 只运行端到端测试
pytest tests/e2e/

# 运行标记为特定类型的测试
pytest -m unit
pytest -m integration
pytest -m e2e
```

### 运行单个测试文件

```bash
# 运行单个测试文件
pytest tests/unit/test_config.py

# 运行单个测试类
pytest tests/unit/test_config.py::TestConfigManager

# 运行单个测试方法
pytest tests/unit/test_config.py::TestConfigManager::test_load_config_success
```

### 测试覆盖率

```bash
# 生成覆盖率报告
pytest --cov=src --cov-report=html

# 生成终端覆盖率报告
pytest --cov=src --cov-report=term-missing
```

## 测试用例说明

### 配置管理测试 (test_config.py)

**测试场景**:
- 配置管理器创建和初始化
- 配置文件加载（成功和失败情况）
- 配置项获取和设置
- 配置保存功能
- 路径获取方法测试
- 默认配置创建

**关键断言**:
- 配置文件正确加载和解析
- 配置项正确获取和设置
- 路径方法返回正确的Path对象
- 默认配置包含所有必需部分

### CSV处理器测试 (test_csv_processor.py)

**测试场景**:
- CSV文件读取（各种情况）
- CSV文件写入
- 数据验证（有效和无效数据）
- 输入CSV处理
- 特殊字符和编码处理

**关键断言**:
- 正确读取CSV数据并转换为字典列表
- 正确写入数据到CSV文件
- 数据验证正确识别错误
- 处理包含特殊字符的数据

### 计算引擎测试 (test_calculation.py)

**测试场景**:
- 简单和复杂公式计算
- 带变量的公式计算
- 几何计算（体积、表面积、重量）
- 计算验证
- 边界情况和错误处理

**关键断言**:
- 公式计算正确性
- 几何计算符合数学公式
- 验证功能正确识别无效计算
- 错误处理机制正常工作

### 数据流集成测试 (test_data_flow.py)

**测试场景**:
- 完整数据流处理
- 包含无效输入的处理
- 缺少master数据的处理
- 包含计算错误的处理
- 性能测试

**关键断言**:
- 各组件正确交互
- 错误情况得到适当处理
- 性能在可接受范围内

### 完整工作流测试 (test_full_workflow.py)

**测试场景**:
- 完整成功工作流
- 包含部分失败的工作流
- 大数据集处理工作流

**关键断言**:
- 从输入到输出的完整流程正常工作
- 错误记录得到适当处理
- 汇总数据正确计算
- 输出文件正确生成

## 测试Fixtures

### 临时目录Fixtures

- `temp_config_dir`: 临时配置目录
- `temp_data_dir`: 临时数据目录
- `temp_workflow_dir`: 临时工作流目录

### 示例数据Fixtures

- `sample_config_content`: 示例配置内容
- `sample_master_data`: 示例master数据
- `sample_input_data`: 示例输入数据
- `sample_product_data`: 示例产品数据字典
- `sample_calculation_parameters`: 示例计算参数
- `sample_calculated_results`: 示例计算结果

### Mock对象Fixtures

- `mock_config_manager`: 模拟配置管理器
- `mock_csv_processor`: 模拟CSV处理器
- `mock_data_manager`: 模拟数据管理器
- `mock_calculation_engine`: 模拟计算引擎

## 测试最佳实践

### 1. 测试命名规范

- 测试类名: `Test{ComponentName}`
- 测试方法名: `test_{scenario}_{expected_result}`
- 使用描述性的测试名称

### 2. 测试结构

- 每个测试方法只测试一个场景
- 使用Arrange-Act-Assert模式
- 包含正面和负面测试用例

### 3. 测试数据管理

- 使用fixtures管理测试数据
- 避免硬编码路径和值
- 使用临时目录避免文件冲突

### 4. 错误处理测试

- 测试正常流程和异常流程
- 验证错误消息和异常类型
- 测试边界条件和极端情况

### 5. 性能考虑

- 单元测试应该快速运行
- 集成和端到端测试可以较慢
- 使用标记区分测试类型

## 测试标记

系统使用pytest标记来分类测试:

- `@pytest.mark.unit`: 单元测试
- `@pytest.mark.integration`: 集成测试
- `@pytest.mark.e2e`: 端到端测试
- `@pytest.mark.slow`: 慢速测试

## 持续集成

测试可以在CI/CD流水线中运行:

```yaml
# 示例GitHub Actions配置
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 故障排除

### 常见问题

1. **导入错误**: 确保PYTHONPATH包含项目根目录
2. **文件权限错误**: 使用临时目录避免权限问题
3. **测试数据冲突**: 每个测试使用独立的测试数据

### 调试技巧

- 使用 `pytest -s` 查看打印输出
- 使用 `pytest --pdb` 在失败时进入调试器
- 添加详细的断言消息

## 扩展测试

要添加新的测试:

1. 在适当的目录创建测试文件
2. 遵循现有的命名和结构约定
3. 添加必要的fixtures到conftest.py
4. 使用适当的测试标记
5. 确保测试覆盖正面和负面场景

## 贡献指南

- 为新功能添加相应的测试
- 确保所有测试通过后再提交
- 保持测试代码的清晰和可维护性
- 定期更新测试文档
