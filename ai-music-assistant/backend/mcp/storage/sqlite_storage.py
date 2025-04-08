"""SQLite存儲實現

基於SQLite的持久化存儲
"""

import os
import json
import sqlite3
import asyncio
from typing import Any, Dict, List, Optional, Union, TypeVar
from datetime import datetime
import aiosqlite

from .persistence import PersistenceStorage, StorageResult


class SQLiteStorage(PersistenceStorage):
    """SQLite存儲類"""
    
    def __init__(self, db_path: str = "data/storage.db", table_name: str = "data"):
        """初始化SQLite存儲
        
        Args:
            db_path: 數據庫文件路徑
            table_name: 表名
        """
        self.db_path = db_path
        self.table_name = table_name
        
        # 確保目錄存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # 初始化數據庫
        self._init_db()
    
    def _init_db(self):
        """初始化數據庫"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 創建表
        cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            key TEXT PRIMARY KEY,
            data TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        ''')
        
        # 創建索引
        cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_{self.table_name}_key ON {self.table_name} (key)')
        
        conn.commit()
        conn.close()
    
    async def save(self, key: str, data: Any) -> StorageResult:
        """保存數據到SQLite
        
        Args:
            key: 數據鍵
            data: 要保存的數據
            
        Returns:
            存儲操作結果
        """
        try:
            # 序列化數據
            serialized_data = json.dumps(self._prepare_data_for_serialization(data), ensure_ascii=False)
            now = datetime.now().isoformat()
            
            async with aiosqlite.connect(self.db_path) as db:
                # 檢查是否已存在
                cursor = await db.execute(f"SELECT key FROM {self.table_name} WHERE key = ?", (key,))
                exists = await cursor.fetchone()
                
                if exists:
                    # 更新現有記錄
                    await db.execute(
                        f"UPDATE {self.table_name} SET data = ?, updated_at = ? WHERE key = ?",
                        (serialized_data, now, key)
                    )
                else:
                    # 插入新記錄
                    await db.execute(
                        f"INSERT INTO {self.table_name} (key, data, created_at, updated_at) VALUES (?, ?, ?, ?)",
                        (key, serialized_data, now, now)
                    )
                
                await db.commit()
            
            return StorageResult.ok(f"數據已保存: {key}", key)
        except Exception as e:
            return StorageResult.error(f"保存數據失敗: {str(e)}", e)
    
    async def get(self, key: str) -> StorageResult:
        """從SQLite獲取數據
        
        Args:
            key: 數據鍵
            
        Returns:
            包含數據的存儲操作結果
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(f"SELECT data FROM {self.table_name} WHERE key = ?", (key,))
                row = await cursor.fetchone()
            
            if not row:
                return StorageResult.error(f"找不到數據: {key}")
            
            # 反序列化數據
            data = json.loads(row[0])
            parsed_data = self._parse_date_strings(data)
            
            return StorageResult.ok(f"數據已加載: {key}", parsed_data)
        except Exception as e:
            return StorageResult.error(f"讀取數據失敗: {str(e)}", e)
    
    async def update(self, key: str, data: Any) -> StorageResult:
        """更新SQLite數據
        
        Args:
            key: 數據鍵
            data: 新數據
            
        Returns:
            存儲操作結果
        """
        try:
            # 檢查記錄是否存在
            if not await self.exists(key):
                return StorageResult.error(f"找不到要更新的數據: {key}")
            
            # 序列化數據
            serialized_data = json.dumps(self._prepare_data_for_serialization(data), ensure_ascii=False)
            now = datetime.now().isoformat()
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    f"UPDATE {self.table_name} SET data = ?, updated_at = ? WHERE key = ?",
                    (serialized_data, now, key)
                )
                await db.commit()
            
            return StorageResult.ok(f"數據已更新: {key}", key)
        except Exception as e:
            return StorageResult.error(f"更新數據失敗: {str(e)}", e)
    
    async def delete(self, key: str) -> StorageResult:
        """刪除SQLite數據
        
        Args:
            key: 數據鍵
            
        Returns:
            存儲操作結果
        """
        try:
            # 檢查記錄是否存在
            if not await self.exists(key):
                return StorageResult.error(f"找不到要刪除的數據: {key}")
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(f"DELETE FROM {self.table_name} WHERE key = ?", (key,))
                await db.commit()
            
            return StorageResult.ok(f"數據已刪除: {key}")
        except Exception as e:
            return StorageResult.error(f"刪除數據失敗: {str(e)}", e)
    
    async def list(self, pattern: str = "*") -> StorageResult:
        """列出SQLite數據
        
        Args:
            pattern: 匹配模式 (使用SQL LIKE語法)
            
        Returns:
            包含鍵列表的存儲操作結果
        """
        try:
            # 將*轉換為SQL LIKE模式
            sql_pattern = pattern.replace("*", "%")
            
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    f"SELECT key FROM {self.table_name} WHERE key LIKE ?",
                    (sql_pattern,)
                )
                rows = await cursor.fetchall()
            
            # 提取鍵
            keys = [row[0] for row in rows]
            
            return StorageResult.ok(f"找到 {len(keys)} 個匹配鍵", keys)
        except Exception as e:
            return StorageResult.error(f"列出鍵失敗: {str(e)}", e)
    
    async def exists(self, key: str) -> bool:
        """檢查SQLite數據是否存在
        
        Args:
            key: 數據鍵
            
        Returns:
            數據是否存在
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(f"SELECT 1 FROM {self.table_name} WHERE key = ?", (key,))
                row = await cursor.fetchone()
            
            return row is not None
        except Exception:
            return False
    
    async def query(self, sql: str, params: tuple = ()) -> StorageResult:
        """執行自定義SQL查詢
        
        Args:
            sql: SQL語句
            params: 查詢參數
            
        Returns:
            查詢結果
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(sql, params)
                rows = await cursor.fetchall()
            
            return StorageResult.ok(f"查詢成功，返回 {len(rows)} 條記錄", rows)
        except Exception as e:
            return StorageResult.error(f"執行查詢失敗: {str(e)}", e)
    
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