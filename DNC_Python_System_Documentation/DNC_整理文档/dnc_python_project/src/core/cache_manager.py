"""
缓存管理器
提供数据缓存功能，提升系统性能
"""

import time
import threading
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
import hashlib
import json

from src.utils.logger import get_logger


class CachePolicy(Enum):
    """缓存策略枚举"""
    LRU = "lru"  # 最近最少使用
    LFU = "lfu"  # 最不经常使用
    FIFO = "fifo"  # 先进先出
    TTL = "ttl"  # 生存时间


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    timestamp: float
    access_count: int
    ttl: int  # 生存时间（秒）
    size: int  # 估算大小（字节）
    
    @property
    def is_expired(self) -> bool:
        """检查缓存是否过期"""
        return time.time() - self.timestamp > self.ttl
    
    @property
    def access_frequency(self) -> float:
        """计算访问频率"""
        age = time.time() - self.timestamp
        if age == 0:
            return float('inf')
        return self.access_count / age


class CacheManager:
    """
    缓存管理器
    提供高效的数据缓存功能，支持多种缓存策略
    """
    
    def __init__(self, max_size: int = 1000, policy: CachePolicy = CachePolicy.LRU):
        """
        初始化缓存管理器
        
        Args:
            max_size: 最大缓存条目数
            policy: 缓存策略
        """
        self.max_size = max_size
        self.policy = policy
        self.logger = get_logger("CacheManager")
        
        # 缓存存储
        self.cache: Dict[str, CacheEntry] = {}
        
        # 统计信息
        self.hit_count = 0
        self.miss_count = 0
        self.eviction_count = 0
        
        # 线程安全
        self._lock = threading.RLock()
        
        # 清理线程
        self._cleanup_thread = None
        self._cleanup_interval = 60  # 清理间隔（秒）
        self._running = False
        
        self.logger.info(f"初始化缓存管理器，最大大小: {max_size}, 策略: {policy.value}")
    
    def start_cleanup_thread(self) -> None:
        """启动清理线程"""
        if self._cleanup_thread is None or not self._cleanup_thread.is_alive():
            self._running = True
            self._cleanup_thread = threading.Thread(
                target=self._cleanup_worker,
                daemon=True,
                name="CacheCleanup"
            )
            self._cleanup_thread.start()
            self.logger.info("缓存清理线程已启动")
    
    def stop_cleanup_thread(self) -> None:
        """停止清理线程"""
        self._running = False
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=5)
            self.logger.info("缓存清理线程已停止")
    
    def _cleanup_worker(self) -> None:
        """清理工作线程"""
        while self._running:
            try:
                time.sleep(self._cleanup_interval)
                self._clean_expired_entries()
            except Exception as e:
                self.logger.error(f"缓存清理线程异常: {e}")
    
    def _clean_expired_entries(self) -> None:
        """清理过期条目"""
        with self._lock:
            expired_keys = [
                key for key, entry in self.cache.items()
                if entry.is_expired
            ]
            
            for key in expired_keys:
                del self.cache[key]
                self.eviction_count += 1
            
            if expired_keys:
                self.logger.debug(f"清理了 {len(expired_keys)} 个过期缓存条目")
    
    def get(self, key: str, default: Any = None) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            default: 默认值
            
        Returns:
            Optional[Any]: 缓存值，如果不存在返回默认值
        """
        with self._lock:
            if key in self.cache:
                entry = self.cache[key]
                
                # 检查是否过期
                if entry.is_expired:
                    del self.cache[key]
                    self.miss_count += 1
                    self.logger.debug(f"缓存过期: {key}")
                    return default
                
                # 更新访问统计
                entry.access_count += 1
                self.hit_count += 1
                self.logger.debug(f"缓存命中: {key}")
                return entry.value
            else:
                self.miss_count += 1
                self.logger.debug(f"缓存未命中: {key}")
                return default
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 生存时间（秒）
        """
        with self._lock:
            # 估算值大小
            size = self._estimate_size(value)
            
            # 创建缓存条目
            entry = CacheEntry(
                key=key,
                value=value,
                timestamp=time.time(),
                access_count=0,
                ttl=ttl,
                size=size
            )
            
            # 检查是否需要淘汰
            if len(self.cache) >= self.max_size and key not in self.cache:
                self._evict_entries()
            
            # 设置缓存
            self.cache[key] = entry
            self.logger.debug(f"设置缓存: {key}, TTL: {ttl}s, 大小: {size} bytes")
    
    def _estimate_size(self, value: Any) -> int:
        """
        估算值的大小
        
        Args:
            value: 要估算的值
            
        Returns:
            int: 估算大小（字节）
        """
        try:
            if isinstance(value, (str, bytes)):
                return len(value)
            elif isinstance(value, (int, float, bool)):
                return 8  # 基本类型固定大小
            elif isinstance(value, (list, tuple, dict)):
                # 序列化为JSON字符串来估算大小
                json_str = json.dumps(value, default=str)
                return len(json_str.encode('utf-8'))
            else:
                # 对于其他类型，使用字符串表示
                return len(str(value).encode('utf-8'))
        except Exception:
            return 1024  # 默认大小
    
    def _evict_entries(self) -> None:
        """根据策略淘汰缓存条目"""
        if not self.cache:
            return
        
        # 计算需要淘汰的数量
        evict_count = max(1, len(self.cache) // 10)  # 淘汰10%的条目
        
        if self.policy == CachePolicy.LRU:
            self._evict_lru(evict_count)
        elif self.policy == CachePolicy.LFU:
            self._evict_lfu(evict_count)
        elif self.policy == CachePolicy.FIFO:
            self._evict_fifo(evict_count)
        elif self.policy == CachePolicy.TTL:
            self._evict_ttl(evict_count)
        
        self.logger.debug(f"淘汰了 {evict_count} 个缓存条目")
    
    def _evict_lru(self, count: int) -> None:
        """淘汰最近最少使用的条目"""
        entries = sorted(
            self.cache.values(),
            key=lambda e: e.access_count / (time.time() - e.timestamp + 1)
        )
        
        for entry in entries[:count]:
            del self.cache[entry.key]
            self.eviction_count += 1
    
    def _evict_lfu(self, count: int) -> None:
        """淘汰最不经常使用的条目"""
        entries = sorted(self.cache.values(), key=lambda e: e.access_count)
        
        for entry in entries[:count]:
            del self.cache[entry.key]
            self.eviction_count += 1
    
    def _evict_fifo(self, count: int) -> None:
        """淘汰最早进入的条目"""
        entries = sorted(self.cache.values(), key=lambda e: e.timestamp)
        
        for entry in entries[:count]:
            del self.cache[entry.key]
            self.eviction_count += 1
    
    def _evict_ttl(self, count: int) -> None:
        """淘汰即将过期的条目"""
        entries = sorted(
            self.cache.values(),
            key=lambda e: e.timestamp + e.ttl - time.time()
        )
        
        for entry in entries[:count]:
            del self.cache[entry.key]
            self.eviction_count += 1
    
    def delete(self, key: str) -> bool:
        """
        删除缓存条目
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 是否成功删除
        """
        with self._lock:
            if key in self.cache:
                del self.cache[key]
                self.logger.debug(f"删除缓存: {key}")
                return True
            return False
    
    def clear(self) -> None:
        """清空所有缓存"""
        with self._lock:
            count = len(self.cache)
            self.cache.clear()
            self.logger.info(f"清空了 {count} 个缓存条目")
    
    def exists(self, key: str) -> bool:
        """
        检查缓存是否存在
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 是否存在
        """
        with self._lock:
            if key in self.cache:
                entry = self.cache[key]
                if not entry.is_expired:
                    return True
                else:
                    del self.cache[key]
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        with self._lock:
            total_requests = self.hit_count + self.miss_count
            hit_rate = self.hit_count / total_requests if total_requests > 0 else 0
            
            # 计算缓存大小
            total_size = sum(entry.size for entry in self.cache.values())
            
            # 计算平均TTL
            avg_ttl = sum(entry.ttl for entry in self.cache.values()) / len(self.cache) if self.cache else 0
            
            return {
                'total_entries': len(self.cache),
                'max_size': self.max_size,
                'hit_count': self.hit_count,
                'miss_count': self.miss_count,
                'eviction_count': self.eviction_count,
                'hit_rate': hit_rate,
                'total_size_bytes': total_size,
                'average_ttl': avg_ttl,
                'policy': self.policy.value
            }
    
    def get_keys(self, pattern: Optional[str] = None) -> List[str]:
        """
        获取所有缓存键
        
        Args:
            pattern: 键模式（可选）
            
        Returns:
            List[str]: 缓存键列表
        """
        with self._lock:
            keys = list(self.cache.keys())
            
            if pattern:
                import fnmatch
                keys = [key for key in keys if fnmatch.fnmatch(key, pattern)]
            
            return keys
    
    def get_entries_info(self) -> List[Dict[str, Any]]:
        """
        获取所有缓存条目的详细信息
        
        Returns:
            List[Dict[str, Any]]: 条目信息列表
        """
        with self._lock:
            entries_info = []
            current_time = time.time()
            
            for key, entry in self.cache.items():
                entries_info.append({
                    'key': key,
                    'size_bytes': entry.size,
                    'access_count': entry.access_count,
                    'age_seconds': current_time - entry.timestamp,
                    'ttl_seconds': entry.ttl,
                    'expires_in': max(0, entry.timestamp + entry.ttl - current_time),
                    'is_expired': entry.is_expired
                })
            
            return entries_info
    
    def set_policy(self, policy: CachePolicy) -> None:
        """
        设置缓存策略
        
        Args:
            policy: 新的缓存策略
        """
        with self._lock:
            if self.policy != policy:
                self.policy = policy
                self.logger.info(f"缓存策略已更改为: {policy.value}")
    
    def set_max_size(self, max_size: int) -> None:
        """
        设置最大缓存大小
        
        Args:
            max_size: 新的最大大小
        """
        with self._lock:
            if self.max_size != max_size:
                old_size = self.max_size
                self.max_size = max_size
                
                # 如果新大小小于当前缓存数量，需要淘汰一些条目
                if len(self.cache) > max_size:
                    evict_count = len(self.cache) - max_size
                    self._evict_entries()
                
                self.logger.info(f"缓存最大大小已从 {old_size} 更改为 {max_size}")
    
    def generate_key(self, *args, **kwargs) -> str:
        """
        生成缓存键
        
        Args:
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            str: 生成的缓存键
        """
        # 将参数序列化为字符串
        key_parts = []
        
        # 添加位置参数
        for arg in args:
            key_parts.append(str(arg))
        
        # 添加关键字参数（排序以确保一致性）
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")
        
        # 生成哈希
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode('utf-8')).hexdigest()


# 全局缓存管理器实例
_global_cache_manager: Optional[CacheManager] = None


def get_global_cache_manager(max_size: int = 1000, policy: CachePolicy = CachePolicy.LRU) -> CacheManager:
    """
    获取全局缓存管理器实例
    
    Args:
        max_size: 最大缓存条目数
        policy: 缓存策略
        
    Returns:
        CacheManager: 全局缓存管理器实例
    """
    global _global_cache_manager
    if _global_cache_manager is None:
        _global_cache_manager = CacheManager(max_size, policy)
        _global_cache_manager.start_cleanup_thread()
    return _global_cache_manager


def set_global_cache_policy(policy: CachePolicy) -> None:
    """
    设置全局缓存策略
    
    Args:
        policy: 缓存策略
    """
    global _global_cache_manager
    if _global_cache_manager:
        _global_cache_manager.set_policy(policy)
    else:
        raise RuntimeError("全局缓存管理器未初始化")


def set_global_cache_size(max_size: int) -> None:
    """
    设置全局缓存大小
    
    Args:
        max_size: 最大缓存条目数
    """
    global _global_cache_manager
    if _global_cache_manager:
        _global_cache_manager.set_max_size(max_size)
    else:
        raise RuntimeError("全局缓存管理器未初始化")


def cleanup_global_cache() -> None:
    """清理全局缓存"""
    global _global_cache_manager
    if _global_cache_manager:
        _global_cache_manager.clear()


def get_global_cache_stats() -> Dict[str, Any]:
    """
    获取全局缓存统计
    
    Returns:
        Dict[str, Any]: 统计信息
    """
    global _global_cache_manager
    if _global_cache_manager:
        return _global_cache_manager.get_stats()
    else:
        return {'error': '全局缓存管理器未初始化'}
