"""緩存服務

用於儲存生成結果和重用計算資源
"""

import os
import json
import time
import hashlib
from typing import Dict, Any, List, Optional, Union, Callable, TypeVar
from datetime import datetime, timedelta
import asyncio

from .persistence import PersistenceStorage, StorageResult, StorageFactory

T = TypeVar('T')


class CacheService:
    """緩存服務類"""
    
    def __init__(
        self, 
        storage_type: str = "sqlite", 
        namespace: str = "cache",
        default_ttl: int = 3600,  # 默認過期時間（秒）
        **storage_kwargs
    ):
        """初始化緩存服務
        
        Args:
            storage_type: 存儲類型 ("sqlite" 或 "json")
            namespace: 緩存命名空間
            default_ttl: 默認過期時間（秒）
            **storage_kwargs: 存儲參數
        """
        # 設置默認參數
        if storage_type == "sqlite":
            default_kwargs = {"db_path": f"data/{namespace}.db", "table_name": namespace}
        else:  # json
            default_kwargs = {"base_dir": f"data/{namespace}"}
        
        # 合併默認參數和提供的參數
        storage_kwargs = {**default_kwargs, **storage_kwargs}
        
        # 創建存儲實例
        self.storage = StorageFactory.create_storage(storage_type, **storage_kwargs)
        self.namespace = namespace
        self.default_ttl = default_ttl
    
    def _generate_cache_key(self, key_components: Union[str, Dict[str, Any], List[Any]]) -> str:
        """生成緩存鍵
        
        Args:
            key_components: 鍵組件，可以是字符串、字典或列表
            
        Returns:
            緩存鍵
        """
        # 如果已經是字符串，直接使用
        if isinstance(key_components, str):
            return f"{self.namespace}:{key_components}"
        
        # 序列化並計算哈希
        key_str = json.dumps(key_components, sort_keys=True)
        hash_key = hashlib.md5(key_str.encode('utf-8')).hexdigest()
        
        return f"{self.namespace}:{hash_key}"
    
    async def get(self, key: Union[str, Dict[str, Any], List[Any]]) -> StorageResult:
        """獲取緩存數據
        
        Args:
            key: 緩存鍵或鍵組件
            
        Returns:
            包含緩存數據的存儲操作結果，如果過期或不存在則返回錯誤結果
        """
        cache_key = self._generate_cache_key(key)
        
        # 獲取數據
        result = await self.storage.get(cache_key)
        if not result.success:
            return result
        
        cache_data = result.data
        
        # 檢查是否過期
        if "expires_at" in cache_data:
            expires_at = cache_data["expires_at"]
            if isinstance(expires_at, str):
                expires_at = datetime.fromisoformat(expires_at)
            
            if expires_at < datetime.now():
                # 異步刪除過期數據
                asyncio.create_task(self.storage.delete(cache_key))
                return StorageResult.error("緩存已過期")
        
        # 返回實際數據
        return StorageResult.ok("緩存命中", cache_data["data"])
    
    async def set(
        self, 
        key: Union[str, Dict[str, Any], List[Any]], 
        data: Any, 
        ttl: Optional[int] = None
    ) -> StorageResult:
        """設置緩存數據
        
        Args:
            key: 緩存鍵或鍵組件
            data: 緩存數據
            ttl: 過期時間（秒），如果為None則使用默認值
            
        Returns:
            存儲操作結果
        """
        cache_key = self._generate_cache_key(key)
        
        # 計算過期時間
        ttl = ttl if ttl is not None else self.default_ttl
        expires_at = datetime.now() + timedelta(seconds=ttl)
        
        # 構建緩存數據
        cache_data = {
            "data": data,
            "created_at": datetime.now(),
            "expires_at": expires_at,
            "ttl": ttl
        }
        
        # 存儲數據
        return await self.storage.save(cache_key, cache_data)
    
    async def delete(self, key: Union[str, Dict[str, Any], List[Any]]) -> StorageResult:
        """刪除緩存數據
        
        Args:
            key: 緩存鍵或鍵組件
            
        Returns:
            存儲操作結果
        """
        cache_key = self._generate_cache_key(key)
        return await self.storage.delete(cache_key)
    
    async def exists(self, key: Union[str, Dict[str, Any], List[Any]]) -> bool:
        """檢查緩存是否存在且未過期
        
        Args:
            key: 緩存鍵或鍵組件
            
        Returns:
            緩存是否有效
        """
        result = await self.get(key)
        return result.success
    
    async def get_or_set(
        self, 
        key: Union[str, Dict[str, Any], List[Any]], 
        data_provider: Callable[[], Union[T, asyncio.Future[T]]], 
        ttl: Optional[int] = None
    ) -> T:
        """獲取緩存數據，如果不存在則設置
        
        Args:
            key: 緩存鍵或鍵組件
            data_provider: 數據提供函數，當緩存不存在時調用
            ttl: 過期時間（秒）
            
        Returns:
            緩存數據或新生成的數據
        """
        # 嘗試獲取緩存
        result = await self.get(key)
        
        # 如果緩存命中，直接返回
        if result.success:
            return result.data
        
        # 否則調用數據提供函數
        data = data_provider()
        
        # 如果返回值是協程或Future，等待其完成
        if asyncio.iscoroutine(data) or isinstance(data, asyncio.Future):
            data = await data
        
        # 設置緩存
        await self.set(key, data, ttl)
        
        return data
    
    async def clear_namespace(self) -> StorageResult:
        """清空當前命名空間的所有緩存
        
        Returns:
            存儲操作結果
        """
        # 獲取所有鍵
        list_result = await self.storage.list(f"{self.namespace}:*")
        if not list_result.success:
            return list_result
        
        # 刪除每個鍵
        deleted_count = 0
        for key in list_result.data:
            delete_result = await self.storage.delete(key)
            if delete_result.success:
                deleted_count += 1
        
        return StorageResult.ok(f"已清除 {deleted_count} 個緩存項")
    
    async def cleanup_expired(self) -> StorageResult:
        """清理過期緩存
        
        Returns:
            存儲操作結果
        """
        # 獲取所有鍵
        list_result = await self.storage.list(f"{self.namespace}:*")
        if not list_result.success:
            return list_result
        
        now = datetime.now()
        deleted_count = 0
        
        # 檢查每個緩存項
        for key in list_result.data:
            get_result = await self.storage.get(key)
            if not get_result.success:
                continue
            
            cache_data = get_result.data
            
            # 檢查是否過期
            if "expires_at" in cache_data:
                expires_at = cache_data["expires_at"]
                if isinstance(expires_at, str):
                    expires_at = datetime.fromisoformat(expires_at)
                
                if expires_at < now:
                    delete_result = await self.storage.delete(key)
                    if delete_result.success:
                        deleted_count += 1
        
        return StorageResult.ok(f"已清理 {deleted_count} 個過期緩存項") 