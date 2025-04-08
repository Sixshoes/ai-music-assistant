"""JSON文件存儲實現

基於JSON文件的持久化存儲
"""

import os
import json
import glob
import asyncio
from typing import Any, Dict, List, Optional, Union, TypeVar
from datetime import datetime
import aiofiles
from aiofiles.os import makedirs

from .persistence import PersistenceStorage, StorageResult


class JSONStorage(PersistenceStorage):
    """JSON文件存儲類"""
    
    def __init__(self, base_dir: str = "data", indent: int = 2):
        """初始化JSON存儲
        
        Args:
            base_dir: 基礎目錄
            indent: JSON縮進
        """
        self.base_dir = base_dir
        self.indent = indent
        
        # 確保目錄存在
        os.makedirs(self.base_dir, exist_ok=True)
    
    def _get_file_path(self, key: str) -> str:
        """獲取文件路徑
        
        Args:
            key: 數據鍵
            
        Returns:
            完整文件路徑
        """
        # 確保文件名合法
        safe_key = key.replace('/', '_').replace('\\', '_')
        
        return os.path.join(self.base_dir, f"{safe_key}.json")
    
    async def save(self, key: str, data: Any) -> StorageResult:
        """保存數據到JSON文件
        
        Args:
            key: 數據鍵
            data: 要保存的數據
            
        Returns:
            存儲操作結果
        """
        try:
            # 確保目錄存在
            await makedirs(self.base_dir, exist_ok=True)
            
            file_path = self._get_file_path(key)
            
            # 轉換日期時間對象為ISO格式字符串
            serializable_data = self._prepare_data_for_serialization(data)
            
            async with aiofiles.open(file_path, mode='w', encoding='utf-8') as f:
                json_str = json.dumps(serializable_data, ensure_ascii=False, indent=self.indent)
                await f.write(json_str)
            
            return StorageResult.ok(f"數據已保存到 {file_path}", key)
        except Exception as e:
            return StorageResult.error(f"保存數據失敗: {str(e)}", e)
    
    async def get(self, key: str) -> StorageResult:
        """從JSON文件獲取數據
        
        Args:
            key: 數據鍵
            
        Returns:
            包含數據的存儲操作結果
        """
        try:
            file_path = self._get_file_path(key)
            
            if not os.path.exists(file_path):
                return StorageResult.error(f"找不到數據: {key}")
            
            async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
                content = await f.read()
                data = json.loads(content)
                
                # 將ISO格式字符串轉換回日期時間對象
                parsed_data = self._parse_date_strings(data)
                
                return StorageResult.ok(f"數據已加載", parsed_data)
        except Exception as e:
            return StorageResult.error(f"讀取數據失敗: {str(e)}", e)
    
    async def update(self, key: str, data: Any) -> StorageResult:
        """更新JSON文件
        
        Args:
            key: 數據鍵
            data: 新數據
            
        Returns:
            存儲操作結果
        """
        if not await self.exists(key):
            return StorageResult.error(f"找不到要更新的數據: {key}")
        
        # 更新就是覆蓋保存
        return await self.save(key, data)
    
    async def delete(self, key: str) -> StorageResult:
        """刪除JSON文件
        
        Args:
            key: 數據鍵
            
        Returns:
            存儲操作結果
        """
        try:
            file_path = self._get_file_path(key)
            
            if not os.path.exists(file_path):
                return StorageResult.error(f"找不到要刪除的數據: {key}")
            
            os.remove(file_path)
            return StorageResult.ok(f"數據已刪除: {key}")
        except Exception as e:
            return StorageResult.error(f"刪除數據失敗: {str(e)}", e)
    
    async def list(self, pattern: str = "*") -> StorageResult:
        """列出所有JSON文件
        
        Args:
            pattern: 匹配模式
            
        Returns:
            包含鍵列表的存儲操作結果
        """
        try:
            # 將模式轉換為文件模式
            file_pattern = os.path.join(self.base_dir, f"{pattern}.json")
            
            # 獲取所有匹配的文件
            file_paths = glob.glob(file_pattern)
            
            # 提取鍵名
            keys = [os.path.splitext(os.path.basename(path))[0] for path in file_paths]
            
            return StorageResult.ok(f"找到 {len(keys)} 個匹配鍵", keys)
        except Exception as e:
            return StorageResult.error(f"列出鍵失敗: {str(e)}", e)
    
    async def exists(self, key: str) -> bool:
        """檢查JSON文件是否存在
        
        Args:
            key: 數據鍵
            
        Returns:
            文件是否存在
        """
        file_path = self._get_file_path(key)
        return os.path.exists(file_path)
    
    def _prepare_data_for_serialization(self, data: Any) -> Any:
        """準備數據以進行序列化
        
        Args:
            data: 原始數據
            
        Returns:
            可序列化的數據
        """
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                result[key] = self._prepare_data_for_serialization(value)
            return result
        elif isinstance(data, list):
            return [self._prepare_data_for_serialization(item) for item in data]
        elif isinstance(data, datetime):
            return {"__datetime__": data.isoformat()}
        elif hasattr(data, "to_dict") and callable(getattr(data, "to_dict")):
            return data.to_dict()
        elif hasattr(data, "__dict__"):
            return self._prepare_data_for_serialization(data.__dict__)
        else:
            return data
    
    def _parse_date_strings(self, data: Any) -> Any:
        """解析日期字符串
        
        Args:
            data: 序列化數據
            
        Returns:
            解析後的數據
        """
        if isinstance(data, dict):
            if len(data) == 1 and "__datetime__" in data:
                return datetime.fromisoformat(data["__datetime__"])
            
            result = {}
            for key, value in data.items():
                result[key] = self._parse_date_strings(value)
            return result
        elif isinstance(data, list):
            return [self._parse_date_strings(item) for item in data]
        else:
            return data 