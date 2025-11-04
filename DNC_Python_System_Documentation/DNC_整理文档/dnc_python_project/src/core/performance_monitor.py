# src/core/performance_monitor.py
"""
性能监控器
提供系统性能监控和统计功能
"""

import time
import threading
import psutil
import gc
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import statistics
from collections import deque

from src.utils.logger import get_logger


class MetricType(Enum):
    """指标类型枚举"""
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    CACHE_HIT_RATE = "cache_hit_rate"
    GARBAGE_COLLECTION = "garbage_collection"


@dataclass
class PerformanceMetric:
    """性能指标"""
    metric_type: MetricType
    value: float
    timestamp: float
    tags: Dict[str, str]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'metric_type': self.metric_type.value,
            'value': self.value,
            'timestamp': self.timestamp,
            'tags': self.tags
        }


@dataclass
class PerformanceStats:
    """性能统计"""
    metric_type: MetricType
    count: int
    average: float
    min_value: float
    max_value: float
    median: float
    p95: float
    p99: float
    std_dev: float
    timestamp: float
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'metric_type': self.metric_type.value,
            'count': self.count,
            'average': self.average,
            'min': self.min_value,
            'max': self.max_value,
            'median': self.median,
            'p95': self.p95,
            'p99': self.p99,
            'std_dev': self.std_dev,
            'timestamp': self.timestamp
        }


class PerformanceMonitor:
    """
    性能监控器
    提供系统性能监控和统计功能
    """
    
    def __init__(self, history_size: int = 1000, collection_interval: int = 5):
        """
        初始化性能监控器
        
        Args:
            history_size: 历史数据大小
            collection_interval: 收集间隔（秒）
        """
        self.history_size = history_size
        self.collection_interval = collection_interval
        self.logger = get_logger("PerformanceMonitor")
        
        # 指标存储
        self.metrics: Dict[MetricType, deque] = {
            metric_type: deque(maxlen=history_size)
            for metric_type in MetricType
        }
        
        # 自定义指标
        self.custom_metrics: Dict[str, deque] = {}
        
        # 统计信息
        self.stats_history: Dict[MetricType, deque] = {
            metric_type: deque(maxlen=100)
            for metric_type in MetricType
        }
        
        # 线程安全
        self._lock = threading.RLock()
        
        # 监控线程
        self._monitor_thread = None
        self._running = False
        
        # 系统基准
        self._system_baseline = self._capture_system_baseline()
        
        # 回调函数
        self._alert_callbacks: List[Callable] = []
        
        # 告警阈值
        self.alert_thresholds = {
            MetricType.CPU_USAGE: 80.0,  # CPU使用率超过80%
            MetricType.MEMORY_USAGE: 85.0,  # 内存使用率超过85%
            MetricType.RESPONSE_TIME: 1000.0,  # 响应时间超过1000ms
            MetricType.ERROR_RATE: 5.0,  # 错误率超过5%
        }
        
        self.logger.info(f"初始化性能监控器，历史大小: {history_size}, 收集间隔: {collection_interval}s")
    
    def _capture_system_baseline(self) -> Dict[str, float]:
        """捕获系统基准"""
        try:
            return {
                'cpu_count': psutil.cpu_count(),
                'total_memory': psutil.virtual_memory().total,
                'available_memory': psutil.virtual_memory().available,
                'disk_usage': psutil.disk_usage('.').total,
            }
        except Exception as e:
            self.logger.warning(f"无法捕获系统基准: {e}")
            return {}
    
    def start_monitoring(self) -> None:
        """启动监控"""
        if self._monitor_thread is None or not self._monitor_thread.is_alive():
            self._running = True
            self._monitor_thread = threading.Thread(
                target=self._monitoring_worker,
                daemon=True,
                name="PerformanceMonitor"
            )
            self._monitor_thread.start()
            self.logger.info("性能监控线程已启动")
    
    def stop_monitoring(self) -> None:
        """停止监控"""
        self._running = False
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5)
            self.logger.info("性能监控线程已停止")
    
    def _monitoring_worker(self) -> None:
        """监控工作线程"""
        while self._running:
            try:
                # 收集系统指标
                self._collect_system_metrics()
                
                # 计算统计信息
                self._calculate_statistics()
                
                # 检查告警
                self._check_alerts()
                
                time.sleep(self.collection_interval)
                
            except Exception as e:
                self.logger.error(f"性能监控线程异常: {e}")
                time.sleep(self.collection_interval)
    
    def _collect_system_metrics(self) -> None:
        """收集系统指标"""
        timestamp = time.time()
        
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=None)
            self.record_metric(
                MetricType.CPU_USAGE,
                cpu_percent,
                timestamp,
                {'source': 'system'}
            )
            
            # 内存使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self.record_metric(
                MetricType.MEMORY_USAGE,
                memory_percent,
                timestamp,
                {'source': 'system'}
            )
            
            # 磁盘IO
            disk_io = psutil.disk_io_counters()
            if disk_io:
                disk_usage = (disk_io.read_bytes + disk_io.write_bytes) / 1024 / 1024  # MB
                self.record_metric(
                    MetricType.DISK_IO,
                    disk_usage,
                    timestamp,
                    {'source': 'system', 'type': 'total'}
                )
            
            # 网络IO
            net_io = psutil.net_io_counters()
            if net_io:
                net_usage = (net_io.bytes_sent + net_io.bytes_recv) / 1024 / 1024  # MB
                self.record_metric(
                    MetricType.NETWORK_IO,
                    net_usage,
                    timestamp,
                    {'source': 'system', 'type': 'total'}
                )
            
            # 垃圾回收统计
            gc_stats = gc.get_stats()
            if gc_stats:
                total_collections = sum(stat['collections'] for stat in gc_stats)
                self.record_metric(
                    MetricType.GARBAGE_COLLECTION,
                    total_collections,
                    timestamp,
                    {'source': 'python'}
                )
            
        except Exception as e:
            self.logger.error(f"收集系统指标失败: {e}")
    
    def record_metric(self, metric_type: MetricType, value: float, timestamp: Optional[float] = None, tags: Optional[Dict[str, str]] = None) -> None:
        """
        记录性能指标
        
        Args:
            metric_type: 指标类型
            value: 指标值
            timestamp: 时间戳（可选）
            tags: 标签（可选）
        """
        if timestamp is None:
            timestamp = time.time()
        
        if tags is None:
            tags = {}
        
        metric = PerformanceMetric(
            metric_type=metric_type,
            value=value,
            timestamp=timestamp,
            tags=tags
        )
        
        with self._lock:
            self.metrics[metric_type].append(metric)
    
    def record_custom_metric(self, name: str, value: float, timestamp: Optional[float] = None, tags: Optional[Dict[str, str]] = None) -> None:
        """
        记录自定义指标
        
        Args:
            name: 指标名称
            value: 指标值
            timestamp: 时间戳（可选）
            tags: 标签（可选）
        """
        if timestamp is None:
            timestamp = time.time()
        
        if tags is None:
            tags = {}
        
        with self._lock:
            if name not in self.custom_metrics:
                self.custom_metrics[name] = deque(maxlen=self.history_size)
            
            metric = PerformanceMetric(
                metric_type=MetricType.RESPONSE_TIME,  # 使用通用类型
                value=value,
                timestamp=timestamp,
                tags={**tags, 'custom_name': name}
            )
            
            self.custom_metrics[name].append(metric)
    
    def record_response_time(self, operation: str, response_time: float, timestamp: Optional[float] = None, tags: Optional[Dict[str, str]] = None) -> None:
        """
        记录响应时间
        
        Args:
            operation: 操作名称
            response_time: 响应时间（毫秒）
            timestamp: 时间戳（可选）
            tags: 标签（可选）
        """
        if tags is None:
            tags = {}
        
        tags['operation'] = operation
        self.record_metric(
            MetricType.RESPONSE_TIME,
            response_time,
            timestamp,
            tags
        )
    
    def record_throughput(self, operation: str, count: int, duration: float, timestamp: Optional[float] = None, tags: Optional[Dict[str, str]] = None) -> None:
        """
        记录吞吐量
        
        Args:
            operation: 操作名称
            count: 操作次数
            duration: 持续时间（秒）
            timestamp: 时间戳（可选）
            tags: 标签（可选）
        """
        if tags is None:
            tags = {}
        
        if duration > 0:
            throughput = count / duration  # 操作/秒
        else:
            throughput = 0
        
        tags['operation'] = operation
        self.record_metric(
            MetricType.THROUGHPUT,
            throughput,
            timestamp,
            tags
        )
    
    def record_error_rate(self, operation: str, error_count: int, total_count: int, timestamp: Optional[float] = None, tags: Optional[Dict[str, str]] = None) -> None:
        """
        记录错误率
        
        Args:
            operation: 操作名称
            error_count: 错误次数
            total_count: 总次数
            timestamp: 时间戳（可选）
            tags: 标签（可选）
        """
        if tags is None:
            tags = {}
        
        if total_count > 0:
            error_rate = (error_count / total_count) * 100  # 百分比
        else:
            error_rate = 0
        
        tags['operation'] = operation
        self.record_metric(
            MetricType.ERROR_RATE,
            error_rate,
            timestamp,
            tags
        )
    
    def _calculate_statistics(self) -> None:
        """计算统计信息"""
        timestamp = time.time()
        
        with self._lock:
            for metric_type, metrics in self.metrics.items():
                if metrics:
                    values = [metric.value for metric in metrics]
                    
                    stats = PerformanceStats(
                        metric_type=metric_type,
                        count=len(values),
                        average=statistics.mean(values),
                        min_value=min(values),
                        max_value=max(values),
                        median=statistics.median(values),
                        p95=self._calculate_percentile(values, 95),
                        p99=self._calculate_percentile(values, 99),
                        std_dev=statistics.stdev(values) if len(values) > 1 else 0,
                        timestamp=timestamp
                    )
                    
                    self.stats_history[metric_type].append(stats)
    
    def _calculate_percentile(self, values: List[float], percentile: float) -> float:
        """计算百分位数"""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = (percentile / 100) * (len(sorted_values) - 1)
        
        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower = sorted_values[int(index)]
            upper = sorted_values[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def _check_alerts(self) -> None:
        """检查告警"""
        with self._lock:
            for metric_type, threshold in self.alert_thresholds.items():
                if metric_type in self.metrics and self.metrics[metric_type]:
                    latest_metric = self.metrics[metric_type][-1]
                    
                    if latest_metric.value > threshold:
                        self._trigger_alert(metric_type, latest_metric.value, threshold)
    
    def _trigger_alert(self, metric_type: MetricType, value: float, threshold: float) -> None:
        """触发告警"""
        alert_message = f"性能告警: {metric_type.value} = {value:.2f} 超过阈值 {threshold:.2f}"
        self.logger.warning(alert_message)
        
        # 调用回调函数
        for callback in self._alert_callbacks:
            try:
                callback(metric_type, value, threshold, alert_message)
            except Exception as e:
                self.logger.error(f"告警回调执行失败: {e}")
    
    def add_alert_callback(self, callback: Callable) -> None:
        """
        添加告警回调函数
        
        Args:
            callback: 回调函数
        """
        self._alert_callbacks.append(callback)
    
    def set_alert_threshold(self, metric_type: MetricType, threshold: float) -> None:
        """
        设置告警阈值
        
        Args:
            metric_type: 指标类型
            threshold: 阈值
        """
        self.alert_thresholds[metric_type] = threshold
        self.logger.info(f"设置 {metric_type.value} 告警阈值为 {threshold}")
    
    def get_metrics(self, metric_type: MetricType, limit: Optional[int] = None) -> List[PerformanceMetric]:
        """
        获取指标数据
        
        Args:
            metric_type: 指标类型
            limit: 限制数量（可选）
            
        Returns:
            List[PerformanceMetric]: 指标列表
        """
        with self._lock:
            metrics = list(self.metrics[metric_type])
            if limit is not None:
                metrics = metrics[-limit:]
            return metrics
    
    def get_custom_metrics(self, name: str, limit: Optional[int] = None) -> List[PerformanceMetric]:
        """
        获取自定义指标数据
        
        Args:
            name: 指标名称
            limit: 限制数量（可选）
            
        Returns:
            List[PerformanceMetric]: 指标列表
        """
        with self._lock:
            if name in self.custom_metrics:
                metrics = list(self.custom_metrics[name])
                if limit is not None:
                    metrics = metrics[-limit:]
                return metrics
            else:
                return []
    
    def get_latest_metric(self, metric_type: MetricType) -> Optional[PerformanceMetric]:
        """
        获取最新指标
        
        Args:
            metric_type: 指标类型
            
        Returns:
            Optional[PerformanceMetric]: 最新指标
        """
        with self._lock:
            if self.metrics[metric_type]:
                return self.metrics[metric_type][-1]
            return None
    
    def get_statistics(self, metric_type: MetricType, limit: Optional[int] = None) -> List[PerformanceStats]:
        """
        获取统计信息
        
        Args:
            metric_type: 指标类型
            limit: 限制数量（可选）
            
        Returns:
            List[PerformanceStats]: 统计信息列表
        """
        with self._lock:
            stats = list(self.stats_history[metric_type])
            if limit is not None:
                stats = stats[-limit:]
            return stats
    
    def get_latest_statistics(self, metric_type: MetricType) -> Optional[PerformanceStats]:
        """
        获取最新统计信息
        
        Args:
            metric_type: 指标类型
            
        Returns:
            Optional[PerformanceStats]: 最新统计信息
        """
        with self._lock:
            if self.stats_history[metric_type]:
                return self.stats_history[metric_type][-1]
            return None
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        获取系统信息
        
        Returns:
            Dict[str, Any]: 系统信息
        """
        try:
            # CPU信息
            cpu_info = {
                'physical_cores': psutil.cpu_count(logical=False),
                'total_cores': psutil.cpu_count(logical=True),
                'max_frequency': psutil.cpu_freq().max if psutil.cpu_freq() else None,
                'current_frequency': psutil.cpu_freq().current if psutil.cpu_freq() else None,
            }
            
            # 内存信息
            memory = psutil.virtual_memory()
            memory_info = {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percent': memory.percent,
            }
            
            # 磁盘信息
            disk = psutil.disk_usage('.')
            disk_info = {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent,
            }
            
            # 网络信息
            net_io = psutil.net_io_counters()
            network_info = {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
            }
            
            return {
                'cpu': cpu_info,
                'memory': memory_info,
                'disk': disk_info,
                'network': network_info,
                'boot_time': psutil.boot_time(),
            }
        except Exception as e:
            self.logger.error(f"获取系统信息失败: {e}")
            return {}

    def get_performance_report(self) -> Dict[str, Any]:
        """
        生成性能报告
        
        Returns:
            Dict[str, Any]: 性能报告
        """
        report = {
            'timestamp': time.time(),
            'system_info': self.get_system_info(),
            'metrics_summary': {},
            'statistics_summary': {}
        }
        
        # 添加指标摘要
        with self._lock:
            for metric_type in MetricType:
                latest_metric = self.get_latest_metric(metric_type)
                if latest_metric:
                    report['metrics_summary'][metric_type.value] = {
                        'value': latest_metric.value,
                        'timestamp': latest_metric.timestamp,
                        'tags': latest_metric.tags
                    }
        
        # 添加统计摘要
        for metric_type in MetricType:
            latest_stats = self.get_latest_statistics(metric_type)
            if latest_stats:
                report['statistics_summary'][metric_type.value] = latest_stats.to_dict()
        
        return report


# 全局性能监控器实例
_global_performance_monitor = None


def get_global_performance_monitor() -> PerformanceMonitor:
    """
    获取全局性能监控器
    
    Returns:
        PerformanceMonitor: 全局性能监控器实例
    """
    global _global_performance_monitor
    if _global_performance_monitor is None:
        _global_performance_monitor = PerformanceMonitor()
    return _global_performance_monitor