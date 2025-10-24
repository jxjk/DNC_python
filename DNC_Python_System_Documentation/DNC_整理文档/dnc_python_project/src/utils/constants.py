"""
常量定义模块
定义系统使用的各种常量
"""

from enum import Enum


class NCCommandType(Enum):
    """NC命令类型枚举"""
    MOVEMENT = "movement"
    TOOL = "tool"
    SPINDLE = "spindle"
    COOLANT = "coolant"
    PROGRAM = "program"
    MISC = "miscellaneous"


class MachineStatus(Enum):
    """机床状态枚举"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"
    OFFLINE = "offline"


class CommunicationProtocol(Enum):
    """通信协议枚举"""
    REXROTH = "rexroth"
    FANUC = "fanuc"
    SIEMENS = "siemens"
    MITSUBISHI = "mitsubishi"
    HEIDENHAIN = "heidenhain"
    CUSTOM = "custom"


class FileType(Enum):
    """文件类型枚举"""
    NC_PROGRAM = "nc_program"
    CONFIG = "config"
    LOG = "log"
    DATA = "data"
    BACKUP = "backup"
    TEMP = "temp"


# NC命令常量
NC_COMMANDS = {
    # 运动命令
    "G00": {"type": NCCommandType.MOVEMENT, "description": "快速定位"},
    "G01": {"type": NCCommandType.MOVEMENT, "description": "直线插补"},
    "G02": {"type": NCCommandType.MOVEMENT, "description": "顺时针圆弧插补"},
    "G03": {"type": NCCommandType.MOVEMENT, "description": "逆时针圆弧插补"},
    "G04": {"type": NCCommandType.MOVEMENT, "description": "暂停"},
    
    # 平面选择
    "G17": {"type": NCCommandType.MOVEMENT, "description": "XY平面选择"},
    "G18": {"type": NCCommandType.MOVEMENT, "description": "ZX平面选择"},
    "G19": {"type": NCCommandType.MOVEMENT, "description": "YZ平面选择"},
    
    # 单位设置
    "G20": {"type": NCCommandType.MOVEMENT, "description": "英制单位"},
    "G21": {"type": NCCommandType.MOVEMENT, "description": "公制单位"},
    
    # 参考点
    "G28": {"type": NCCommandType.MOVEMENT, "description": "返回参考点"},
    "G29": {"type": NCCommandType.MOVEMENT, "description": "从参考点返回"},
    
    # 刀具补偿
    "G40": {"type": NCCommandType.TOOL, "description": "取消刀具半径补偿"},
    "G41": {"type": NCCommandType.TOOL, "description": "左侧刀具半径补偿"},
    "G42": {"type": NCCommandType.TOOL, "description": "右侧刀具半径补偿"},
    "G43": {"type": NCCommandType.TOOL, "description": "刀具长度正补偿"},
    "G44": {"type": NCCommandType.TOOL, "description": "刀具长度负补偿"},
    "G49": {"type": NCCommandType.TOOL, "description": "取消刀具长度补偿"},
    
    # 坐标系
    "G54": {"type": NCCommandType.MOVEMENT, "description": "工件坐标系1"},
    "G55": {"type": NCCommandType.MOVEMENT, "description": "工件坐标系2"},
    "G56": {"type": NCCommandType.MOVEMENT, "description": "工件坐标系3"},
    "G57": {"type": NCCommandType.MOVEMENT, "description": "工件坐标系4"},
    "G58": {"type": NCCommandType.MOVEMENT, "description": "工件坐标系5"},
    "G59": {"type": NCCommandType.MOVEMENT, "description": "工件坐标系6"},
    
    # 主轴命令
    "M03": {"type": NCCommandType.SPINDLE, "description": "主轴正转"},
    "M04": {"type": NCCommandType.SPINDLE, "description": "主轴反转"},
    "M05": {"type": NCCommandType.SPINDLE, "description": "主轴停止"},
    "M19": {"type": NCCommandType.SPINDLE, "description": "主轴定向"},
    
    # 冷却液命令
    "M07": {"type": NCCommandType.COOLANT, "description": "雾状冷却液开"},
    "M08": {"type": NCCommandType.COOLANT, "description": "液状冷却液开"},
    "M09": {"type": NCCommandType.COOLANT, "description": "冷却液关"},
    
    # 程序控制
    "M00": {"type": NCCommandType.PROGRAM, "description": "程序暂停"},
    "M01": {"type": NCCommandType.PROGRAM, "description": "选择停止"},
    "M02": {"type": NCCommandType.PROGRAM, "description": "程序结束"},
    "M30": {"type": NCCommandType.PROGRAM, "description": "程序结束并返回"},
    "M98": {"type": NCCommandType.PROGRAM, "description": "调用子程序"},
    "M99": {"type": NCCommandType.PROGRAM, "description": "子程序结束"},
    
    # 刀具命令
    "M06": {"type": NCCommandType.TOOL, "description": "换刀"},
    
    # 其他命令
    "M17": {"type": NCCommandType.MISC, "description": "主轴夹紧"},
    "M18": {"type": NCCommandType.MISC, "description": "主轴松开"},
}

# 文件扩展名常量
FILE_EXTENSIONS = {
    FileType.NC_PROGRAM: ['.nc', '.cnc', '.tap', '.mpf', '.txt'],
    FileType.CONFIG: ['.csv', '.ini', '.cfg', '.json', '.xml'],
    FileType.LOG: ['.log', '.txt'],
    FileType.DATA: ['.dat', '.db', '.sqlite'],
    FileType.BACKUP: ['.bak', '.backup'],
    FileType.TEMP: ['.tmp', '.temp']
}

# 错误代码常量
ERROR_CODES = {
    # 系统错误 (1000-1999)
    1000: "系统初始化失败",
    1001: "配置文件加载失败",
    1002: "日志系统初始化失败",
    1003: "数据库连接失败",
    1004: "内存不足",
    1005: "磁盘空间不足",
    
    # 通信错误 (2000-2999)
    2000: "通信连接失败",
    2001: "通信超时",
    2002: "协议解析错误",
    2003: "数据发送失败",
    2004: "数据接收失败",
    2005: "连接参数无效",
    2006: "设备未响应",
    2007: "通信协议不支持",
    
    # 文件操作错误 (3000-3999)
    3000: "文件不存在",
    3001: "文件访问被拒绝",
    3002: "文件格式错误",
    3003: "文件大小超出限制",
    3004: "文件读取失败",
    3005: "文件写入失败",
    3006: "文件删除失败",
    3007: "目录创建失败",
    3008: "路径无效",
    
    # NC程序错误 (4000-4999)
    4000: "NC程序语法错误",
    4001: "NC程序格式错误",
    4002: "NC程序验证失败",
    4003: "NC程序发送失败",
    4004: "NC程序接收失败",
    4005: "NC程序执行失败",
    4006: "刀具路径计算错误",
    4007: "坐标转换错误",
    
    # 业务逻辑错误 (5000-5999)
    5000: "参数验证失败",
    5001: "数据计算错误",
    5002: "模型识别失败",
    5003: "程序匹配失败",
    5004: "关系验证失败",
    5005: "配置参数错误",
    5006: "业务规则冲突",
    
    # 用户界面错误 (6000-6999)
    6000: "界面初始化失败",
    6001: "控件创建失败",
    6002: "事件处理错误",
    6003: "数据显示错误",
    6004: "用户输入无效",
    6005: "界面刷新失败",
    
    # 网络错误 (7000-7999)
    7000: "网络连接失败",
    7001: "DNS解析失败",
    7002: "SSL证书错误",
    7003: "HTTP请求失败",
    7004: "网络超时",
    7005: "代理服务器错误",
}

# 默认配置常量
DEFAULT_CONFIG = {
    "system": {
        "name": "DNC Python System",
        "version": "1.0.0",
        "language": "zh-CN",
        "timezone": "Asia/Shanghai"
    },
    "logging": {
        "level": "INFO",
        "max_file_size": 10485760,  # 10MB
        "backup_count": 5,
        "log_to_console": True,
        "log_to_file": True
    },
    "communication": {
        "default_protocol": "rexroth",
        "timeout": 30,
        "retry_count": 3,
        "retry_delay": 1
    },
    "file": {
        "max_file_size": 52428800,  # 50MB
        "allowed_extensions": ['.nc', '.cnc', '.txt', '.csv'],
        "backup_enabled": True,
        "backup_count": 10
    },
    "ui": {
        "theme": "default",
        "font_size": 10,
        "window_width": 1200,
        "window_height": 800,
        "auto_save": True,
        "auto_save_interval": 300  # 5分钟
    }
}

# 通信协议默认端口
PROTOCOL_PORTS = {
    CommunicationProtocol.REXROTH: 102,
    CommunicationProtocol.FANUC: 8193,
    CommunicationProtocol.SIEMENS: 102,
    CommunicationProtocol.MITSUBISHI: 5007,
    CommunicationProtocol.HEIDENHAIN: 8000,
    CommunicationProtocol.CUSTOM: 8080
}

# 机床状态颜色映射
STATUS_COLORS = {
    MachineStatus.IDLE: "#4CAF50",      # 绿色
    MachineStatus.RUNNING: "#2196F3",   # 蓝色
    MachineStatus.PAUSED: "#FF9800",    # 橙色
    MachineStatus.STOPPED: "#F44336",   # 红色
    MachineStatus.ERROR: "#9C27B0",     # 紫色
    MachineStatus.OFFLINE: "#9E9E9E"    # 灰色
}

# 时间格式常量
TIME_FORMATS = {
    "display": "%Y-%m-%d %H:%M:%S",
    "file": "%Y%m%d_%H%M%S",
    "log": "%Y-%m-%d %H:%M:%S,%f",
    "short": "%H:%M:%S",
    "date_only": "%Y-%m-%d"
}

# 单位转换常量
UNIT_CONVERSIONS = {
    "mm_to_inch": 0.0393701,
    "inch_to_mm": 25.4,
    "degree_to_radian": 0.0174533,
    "radian_to_degree": 57.2958
}

# 数学常量
MATH_CONSTANTS = {
    "PI": 3.141592653589793,
    "E": 2.718281828459045,
    "GOLDEN_RATIO": 1.618033988749895
}

# 正则表达式模式
REGEX_PATTERNS = {
    "ip_address": r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$',
    "email": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    "filename": r'^[^<>:"/\\|?*\x00-\x1f]+$',
    "nc_line": r'^[NO]\d+\s+[GMXYZFSTIJDKRPQ\s\.\-]+$',
    "number": r'^-?\d+(\.\d+)?$'
}

# 系统路径常量
SYSTEM_PATHS = {
    "config": "config/",
    "logs": "logs/",
    "data": "data/",
    "backup": "backup/",
    "temp": "temp/",
    "programs": "programs/"
}

# 版本信息
VERSION_INFO = {
    "major": 1,
    "minor": 0,
    "patch": 0,
    "build": "20241024",
    "compatibility": "Python 3.8+"
}
