# DNC系统API参考文档

## 1. 概述

### 1.1 API设计原则

#### 1.1.1 设计理念
- **RESTful风格**: 遵循REST架构约束
- **一致性**: 统一的命名和响应格式
- **可扩展性**: 支持未来功能扩展
- **安全性**: 完善的认证和授权机制

#### 1.1.2 版本控制
- **URL版本**: `/api/v1/` 前缀
- **向后兼容**: 保证API的向后兼容性
- **弃用策略**: 明确的API弃用通知

### 1.2 基础信息

#### 1.2.1 基础URL
```
http://localhost:8080/api/v1/
```

#### 1.2.2 认证方式
- **API密钥**: `X-API-Key` 请求头
- **JWT令牌**: `Authorization: Bearer <token>`
- **基本认证**: `Authorization: Basic <credentials>`

#### 1.2.3 响应格式
```json
{
  "success": true,
  "data": {},
  "message": "操作成功",
  "code": 200,
  "timestamp": "2025-10-24T10:00:00Z"
}
```

## 2. 型号识别API

### 2.1 型号识别接口

#### 2.1.1 POST /models/recognize
**描述**: 识别QR码中的型号信息

**请求参数**:
```json
{
  "qr_code": "PO12345@C-CCC10-20A-P5-30@100",
  "config_override": {
    "QRmode": "1",
    "QRspltStr": "@"
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "model": "C-CCC10-20A-P5-30",
    "po": "PO12345",
    "quantity": "100",
    "recognition_mode": "splitter",
    "confidence": 0.95
  },
  "message": "型号识别成功"
}
```

**错误响应**:
```json
{
  "success": false,
  "data": null,
  "message": "QR码格式错误",
  "code": 400
}
```

#### 2.1.2 GET /models/recognition-modes
**描述**: 获取可用的型号识别模式

**响应**:
```json
{
  "success": true,
  "data": {
    "modes": [
      {
        "id": "fixed_char_delete",
        "name": "固定字符删除模式",
        "description": "删除固定长度的前缀字符",
        "config_keys": ["BarCodeHeaderStrNum"]
      },
      {
        "id": "splitter",
        "name": "分隔符分割模式", 
        "description": "使用分隔符分割QR码",
        "config_keys": ["QRspltStr", "MODELplc", "POplc", "QTYplc"]
      }
    ]
  }
}
```

### 2.2 型号处理接口

#### 2.2.1 POST /models/process
**描述**: 处理型号字符串，分割为部件

**请求参数**:
```json
{
  "model": "C-CCC10-20A-P5-30",
  "header_config": {
    "C": "del"
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "original_model": "C-CCC10-20A-P5-30",
    "processed_parts": ["CCC10", "20A", "P5", "30"],
    "definitions": ["-", "size1", "-", "size2"],
    "header_processed": true
  }
}
```

#### 2.2.2 GET /models/headers
**描述**: 获取型号前缀处理配置

**响应**:
```json
{
  "success": true,
  "data": {
    "headers": [
      {
        "prefix": "C",
        "action": "del",
        "description": "删除前缀C"
      },
      {
        "prefix": "X",
        "action": "keep", 
        "description": "保留前缀X"
      }
    ]
  }
}
```

## 3. 程序匹配API

### 3.1 程序匹配接口

#### 3.1.1 POST /programs/match
**描述**: 匹配型号对应的程序

**请求参数**:
```json
{
  "model": "C-CCC10-20A-P5-30",
  "type_define_data": [
    {"NO": "1", "TYPE": "AAA"},
    {"NO": "2", "TYPE": "C-CCC"},
    {"NO": "3", "TYPE": "C-CCC10"}
  ]
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "program_no": 3,
    "matched_string": "C-CCC10",
    "match_type": "exact",
    "confidence": 1.0,
    "alternative_matches": [
      {
        "program_no": 2,
        "matched_string": "C-CCC", 
        "confidence": 0.8
      }
    ]
  }
}
```

#### 3.1.2 GET /programs/{program_no}
**描述**: 获取指定程序的详细信息

**响应**:
```json
{
  "success": true,
  "data": {
    "program_no": 3,
    "name": "C-CCC10程序",
    "description": "用于C-CCC10系列型号的程序",
    "parameters": [
      {
        "macro": "#500",
        "name": "长度参数",
        "type": "numeric",
        "required": true
      }
    ],
    "created_at": "2025-10-24T08:00:00Z",
    "updated_at": "2025-10-24T09:30:00Z"
  }
}
```

### 3.2 程序管理接口

#### 3.2.1 GET /programs
**描述**: 获取所有程序列表

**查询参数**:
- `page`: 页码 (默认: 1)
- `limit`: 每页数量 (默认: 20)
- `search`: 搜索关键词

**响应**:
```json
{
  "success": true,
  "data": {
    "programs": [
      {
        "program_no": 1,
        "name": "AAA程序",
        "description": "用于AAA系列型号",
        "parameter_count": 5
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 50,
      "pages": 3
    }
  }
}
```

#### 3.2.2 PUT /programs/{program_no}
**描述**: 更新程序信息

**请求参数**:
```json
{
  "name": "更新后的程序名",
  "description": "更新后的描述",
  "parameters": [
    {
      "macro": "#500",
      "name": "更新后的参数名",
      "type": "numeric"
    }
  ]
}
```

## 4. 参数计算API

### 4.1 参数计算接口

#### 4.1.1 POST /parameters/calculate
**描述**: 计算程序参数值

**请求参数**:
```json
{
  "program_no": 3,
  "model_parts": ["CCC10", "20A", "P5", "30"],
  "calculation_rules": {
    "define_rules": [
      {
        "DEFINE": "define3-2",
        "STR": "P",
        "BEFORE": "P5",
        "AFTER": "5",
        "CHNGVL": "chngS",
        "CALC": "calc2-2"
      }
    ],
    "chng_rules": [
      {
        "DEFINE": "chngS",
        "BEFORE": "S",
        "AFTER": "1"
      }
    ],
    "calc_rules": [
      {
        "DEFINE": "calc2-2",
        "1": "=",
        "2": "calc2-2",
        "3": "+",
        "4": "1"
      }
    ]
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "parameters": {
      "#500": "10",
      "#501": "20A",
      "#502": "6",
      "#503": "30"
    },
    "calculation_steps": [
      {
        "macro": "#502",
        "steps": [
          "Define处理: P5 → 5",
          "值转换: 5 → 5",
          "计算执行: 5 + 1 = 6"
        ]
      }
    ],
    "execution_time": "5ms"
  }
}
```

#### 4.1.2 GET /parameters/rules
**描述**: 获取参数计算规则

**查询参数**:
- `program_no`: 程序编号
- `rule_type`: 规则类型 (define, chng, calc, relation)

**响应**:
```json
{
  "success": true,
  "data": {
    "define_rules": [
      {
        "DEFINE": "define3-2",
        "STR": "P",
        "BEFORE": "P5",
        "AFTER": "5",
        "CHNGVL": "chngS",
        "CALC": "calc2-2",
        "description": "处理P前缀的参数"
      }
    ],
    "chng_rules": [
      {
        "DEFINE": "chngS",
        "BEFORE": "S", 
        "AFTER": "1",
        "description": "将S转换为1"
      }
    ]
  }
}
```

### 4.2 关系验证接口

#### 4.2.1 POST /parameters/validate-relations
**描述**: 验证参数间的关系

**请求参数**:
```json
{
  "parameters": {
    "#505M": "0.5",
    "#506M": "1.2"
  },
  "relation_rules": [
    {
      "DEFINE": "relation10",
      "VALUE": "1",
      "1": "and",
      "2": "#505M",
      "3": ">=",
      "4": "0",
      "5": "and",
      "6": "#505M",
      "7": "<=",
      "8": "1"
    }
  ]
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "valid": true,
    "violations": [],
    "applied_rules": [
      {
        "define": "relation10",
        "value": "1",
        "condition": "#505M >= 0 and #505M <= 1",
        "satisfied": true
      }
    ]
  }
}
```

## 5. NC通信API

### 5.1 设备通信接口

#### 5.1.1 POST /nc/send-parameters
**描述**: 发送参数到NC设备

**请求参数**:
```json
{
  "device_config": {
    "protocol": "rexroth",
    "host": "192.168.1.100",
    "port": 502,
    "timeout": 30
  },
  "parameters": {
    "#500": "10",
    "#501": "20A",
    "#502": "6"
  },
  "options": {
    "verify_response": true,
    "retry_count": 3
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "sent_count": 3,
    "failed_count": 0,
    "response_time": "150ms",
    "device_response": "参数设置成功",
    "sent_parameters": [
      {
        "macro": "#500",
        "value": "10",
        "status": "success"
      }
    ]
  }
}
```

#### 5.1.2 GET /nc/protocols
**描述**: 获取支持的NC协议列表

**响应**:
```json
{
  "success": true,
  "data": {
    "protocols": [
      {
        "id": "rexroth",
        "name": "Rexroth协议",
        "description": "博世力士乐NC协议",
        "supported_operations": ["read", "write", "monitor"]
      },
      {
        "id": "brother",
        "name": "Brother协议", 
        "description": "兄弟NC协议",
        "supported_operations": ["read", "write"]
      },
      {
        "id": "fanuc",
        "name": "Fanuc协议",
        "description": "发那科NC协议",
        "supported_operations": ["read", "write"]
      }
    ]
  }
}
```

### 5.2 设备状态接口

#### 5.2.1 GET /nc/device-status
**描述**: 获取NC设备状态

**查询参数**:
- `device_id`: 设备标识符

**响应**:
```json
{
  "success": true,
  "data": {
    "device_id": "nc_device_001",
    "status": "connected",
    "protocol": "rexroth",
    "last_communication": "2025-10-24T10:15:30Z",
    "response_time": "120ms",
    "error_count": 0,
    "parameters_sent_today": 150
  }
}
```

#### 5.2.2 POST /nc/test-connection
**描述**: 测试NC设备连接

**请求参数**:
```json
{
  "device_config": {
    "protocol": "rexroth",
    "host": "192.168.1.100",
    "port": 502
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "connected": true,
    "response_time": "110ms",
    "protocol_version": "1.2",
    "device_info": "Rexroth IndraMotion MLC"
  }
}
```

## 6. 配置管理API

### 6.1 配置文件接口

#### 6.1.1 GET /config/files
**描述**: 获取配置文件列表

**响应**:
```json
{
  "success": true,
  "data": {
    "files": [
      {
        "name": "ini.csv",
        "description": "系统主配置文件",
        "size": "2.1KB",
        "last_modified": "2025-10-24T09:00:00Z",
        "required": true
      },
      {
        "name": "header.csv",
        "description": "型号前缀处理配置",
        "size": "1.5KB", 
        "last_modified": "2025-10-24T08:30:00Z",
        "required": true
      }
    ]
  }
}
```

#### 6.1.2 GET /config/files/{filename}
**描述**: 获取配置文件内容

**响应**:
```json
{
  "success": true,
  "data": {
    "filename": "ini.csv",
    "content": "QRmode,1\nQRspltStr,@\nMODELplc,2\nPOplc,1\nQTYplc,3",
    "format": "csv",
    "columns": ["QRmode", "QRspltStr", "MODELplc", "POplc", "QTYplc"],
    "row_count": 1
  }
}
```

#### 6.1.3 PUT /config/files/{filename}
**描述**: 更新配置文件

**请求参数**:
```json
{
  "content": "QRmode,1\nQRspltStr,@\nMODELplc,2\nPOplc,1\nQTYplc,3",
  "backup_existing": true
}
```

### 6.2 配置验证接口

#### 6.2.1 POST /config/validate
**描述**: 验证配置文件的完整性和正确性

**请求参数**:
```json
{
  "files_to_validate": ["ini.csv", "header.csv", "type_define.csv"]
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "validation_results": [
      {
        "filename": "ini.csv",
        "valid": true,
        "errors": [],
        "warnings": []
      },
      {
        "filename": "header.csv", 
        "valid": true,
        "errors": [],
        "warnings": ["缺少必需的列: action"]
      }
    ],
    "overall_valid": true
  }
}
```

## 7. 系统管理API

### 7.1 系统状态接口

#### 7.1.1 GET /system/status
**描述**: 获取系统状态信息

**响应**:
```json
{
  "success": true,
  "data": {
    "system": {
      "version": "1.0.0",
      "uptime": "2天3小时15分",
      "start_time": "2025-10-22T07:45:00Z"
    },
    "performance": {
      "cpu_usage": 15.2,
      "memory_usage": 145.3,
      "disk_usage": 45.8,
      "active_connections": 3
    },
    "modules": {
      "model_recognizer": "running",
      "program_matcher": "running", 
      "calculation_engine": "running",
      "nc_communicator": "connected"
    }
  }
}
```

#### 7.1.2 GET /system/logs
**描述**: 获取系统日志

**查询参数**:
- `level`: 日志级别 (DEBUG, INFO, WARN, ERROR)
- `start_time`: 开始时间
- `end_time`: 结束时间
- `limit`: 返回条数 (默认: 100)

**响应**:
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "timestamp": "2025-10-24T10:00:00Z",
        "level": "INFO",
        "module": "model_recognizer",
        "message": "型号识别成功: C-CCC10-20A-P5-30",
        "details": {}
      },
      {
        "timestamp": "2025-10-24T10:01:00Z",
        "level": "WARN",
        "module": "nc_communicator", 
        "message": "NC设备连接超时",
        "details": {"device": "192.168.1.100", "timeout": 30}
      }
    ],
    "total_count": 150,
    "filtered_count": 2
  }
}
```

### 7.2 系统管理接口

#### 7.2.1 POST /system/restart
**描述**: 重启系统服务

**请求参数**:
```json
{
  "modules": ["all"],
  "graceful": true,
  "timeout": 30
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "restarted_modules": [
      {
        "module": "model_recognizer",
        "status": "restarted",
        "restart_time": "2s"
      },
      {
        "module": "calculation_engine",
        "status": "restarted", 
        "restart_time": "1s"
      }
    ],
    "total_time": "5s"
  }
}
```

#### 7.2.2 GET /system/backup
**描述**: 创建系统备份

**查询参数**:
- `include_config`: 是否包含配置 (默认: true)
- `include_data`: 是否包含数据 (默认: true)
- `include_logs`: 是否包含日志 (默认: false)

**响应**:
```json
{
  "success": true,
  "data": {
    "backup_id": "backup_202510241100",
    "filename": "dnc_backup_202510241100.zip",
    "size": "15.2MB",
    "created_at": "2025-10-24T11:00:00Z",
    "included_files": [
      "config/ini.csv",
      "config/header.csv",
      "data/programs.db"
    ]
  }
}
```

## 8. 错误处理

### 8.1 错误代码

#### 8.1.1 通用错误代码
- `400`: 请求参数错误
- `401`: 未授权访问
- `403`: 禁止访问
- `404`: 资源未找到
- `500`: 服务器内部错误
- `503`: 服务不可用

#### 8.1.2 业务错误代码
- `1001`: 型号识别失败
- `1002`: 程序匹配失败
- `1003`: 参数计算错误
- `1004`: NC通信失败
- `1005`: 配置验证失败

### 8.2 错误响应格式

```json
{
  "success": false,
  "data": null,
  "message": "详细的错误描述",
  "code": 1001,
  "timestamp": "2025-10-24T10:00:00Z",
  "details": {
    "error_type": "model_recognition_error",
    "suggested_action": "检查QR码格式",
    "reference": "docs/errors/1001"
  }
}
```

## 9. 使用示例

### 9.1 Python客户端示例

```python
import requests

class DNCClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
    
    def recognize_model(self, qr_code):
        """识别型号"""
        url = f"{self.base_url}/models/recognize"
        data = {"qr_code": qr_code}
        response = requests.post(url, json=data, headers=self.headers)
        return response.json()
    
    def calculate_parameters(self, program_no, model_parts):
        """计算参数"""
        url = f"{self.base_url}/parameters/calculate"
        data = {
            "program_no": program_no,
            "model_parts": model_parts
        }
        response = requests.post(url, json=data, headers=self.headers)
        return response.json()
    
    def send_to_nc(self, device_config, parameters):
        """发送到NC设备"""
        url = f"{self.base_url}/nc/send-parameters"
        data = {
            "device_config": device_config,
            "parameters": parameters
        }
        response = requests.post(url, json=data, headers=self.headers)
        return response.json()

# 使用示例
client = DNCClient("http://localhost:8080/api/v1", "your-api-key")

# 完整工作流程
result = client.recognize_model("PO12345@C-CCC10-20A-P5-30@100")
model = result['data']['model']

program_result = client.calculate_parameters(3, ["CCC10", "20A", "P5", "30"])
parameters = program_result['data']['parameters']

nc_result = client.send_to_nc(
    {"protocol": "rexroth", "host": "192.168.1.100", "port": 502},
    parameters
)
```

### 9.2 cURL示例

```bash
# 型号识别
curl -X POST "http://localhost:8080/api/v1/models/recognize" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"qr_code": "PO12345@C-CCC10-20A-P5-30@100"}'

# 参数计算
curl -X POST "http://localhost:8080/api/v1/parameters/calculate" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"program_no": 3, "model_parts": ["CCC10", "20A", "P5", "30"]}'

# 系统状态
curl -X GET "http://localhost:8080/api/v1/system/status" \
  -H "X-API-Key: your-api-key"
```

## 10. 最佳实践

### 10.1 性能优化

#### 10.1.1 批量操作
- 使用批量API减少请求次数
- 合理设置超时时间
- 使用连接池管理HTTP连接

#### 10.1.2 缓存策略
- 缓存频繁访问的数据
- 使用ETag进行条件请求
- 合理设置缓存过期时间

### 10.2 错误处理

#### 10.2.1 重试机制
```python
def api_call_with_retry(func, max_retries=3, backoff_factor=1):
    """带重试的API调用"""
    for attempt in range(max_retries):
        try:
            return func()
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(backoff_factor * (2 ** attempt))
```

#### 10.2.2 优雅降级
- 关键功能失败时的备用方案
- 部分失败时的部分成功响应
- 用户友好的错误消息

### 10.3 安全实践

#### 10.3.1 API密钥管理
- 定期轮换API密钥
- 使用环境变量存储密钥
- 限制API密钥的权限范围

#### 10.3.2 请求验证
- 验证所有输入参数
- 限制请求频率
- 使用HTTPS加密通信

---

**文档版本**: v1.0  
**最后更新**: 2025年10月24日  
**API版本**: v1  
**支持**: api-support@dnc-system.com
