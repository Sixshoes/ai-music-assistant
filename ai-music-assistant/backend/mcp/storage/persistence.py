"""持久化存儲模組

提供通用存儲接口和抽象基類
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, TypeVar, Generic
from datetime import datetime
from uuid import uuid4

T = TypeVar('T')


class StorageResult:
    """存儲操作結果"""
    
    def __init__(self, success: bool, message: str = "", data: Any = None, error: Exception = None):
        """初始化存儲結果
        
        Args:
            success: 操作是否成功
            message: 結果消息
            data: 返回的數據
            error: 錯誤對象（如果有）
        """
        self.success = success
        self.message = message
        self.data = data
        self.error = error
        self.timestamp = datetime.now()
    
    @classmethod
    def ok(cls, message: str = "操作成功", data: Any = None) -> 'StorageResult':
        """創建成功結果
        
        Args:
            message: 結果消息
            data: 返回的數據
            
        Returns:
            成功的存儲結果
        """
        return cls(True, message, data)
    
    @classmethod
    def error(cls, message: str = "操作失敗", error: Exception = None) -> 'StorageResult':
        """創建失敗結果
        
        Args:
            message: 結果消息
            error: 錯誤對象
            
        Returns:
            失敗的存儲結果
        """
        return cls(False, message, None, error)
    
    def __bool__(self) -> bool:
        """布爾轉換
        
        Returns:
            操作是否成功
        """
        return self.success


class PersistenceStorage(Generic[T], ABC):
    """持久化存儲抽象基類"""
    
    @abstractmethod
    async def save(self, key: str, data: T) -> StorageResult:
        """保存數據
        
        Args:
            key: 數據鍵
            data: 要保存的數據
            
        Returns:
            存儲操作結果
        """
        pass
    
    @abstractmethod
    async def get(self, key: str) -> StorageResult:
        """獲取數據
        
        Args:
            key: 數據鍵
            
        Returns:
            包含數據的存儲操作結果
        """
        pass
    
    @abstractmethod
    async def update(self, key: str, data: T) -> StorageResult:
        """更新數據
        
        Args:
            key: 數據鍵
            data: 新數據
            
        Returns:
            存儲操作結果
        """
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> StorageResult:
        """刪除數據
        
        Args:
            key: 數據鍵
            
        Returns:
            存儲操作結果
        """
        pass
    
    @abstractmethod
    async def list(self, pattern: str = "*") -> StorageResult:
        """列出滿足模式的所有鍵
        
        Args:
            pattern: 匹配模式
            
        Returns:
            包含鍵列表的存儲操作結果
        """
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """檢查鍵是否存在
        
        Args:
            key: 數據鍵
            
        Returns:
            鍵是否存在
        """
        pass


class StorageFactory:
    """存儲工廠類"""
    
    @staticmethod
    def create_storage(storage_type: str, **kwargs) -> PersistenceStorage:
        """創建存儲實例
        
        Args:
            storage_type: 存儲類型
            **kwargs: 初始化參數
            
        Returns:
            對應類型的存儲實例
            
        Raises:
            ValueError: 如果存儲類型不支持
        """
        from .json_storage import JSONStorage
        from .sqlite_storage import SQLiteStorage
        
        if storage_type.lower() == "json":
            return JSONStorage(**kwargs)
        elif storage_type.lower() == "sqlite":
            return SQLiteStorage(**kwargs)
        else:
            raise ValueError(f"不支持的存儲類型: {storage_type}")


def generate_id() -> str:
    """生成唯一ID
    
    Returns:
        唯一ID字符串
    """
    return str(uuid4()) 