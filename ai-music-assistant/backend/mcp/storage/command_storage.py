"""指令存儲服務

專門用於保存和管理指令歷史
"""

import os
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import asyncio

from ..mcp_schema import MCPCommand, MCPResponse, CommandStatus
from .persistence import PersistenceStorage, StorageResult, StorageFactory


class CommandStorage:
    """指令存儲服務類"""
    
    def __init__(self, storage_type: str = "sqlite", **storage_kwargs):
        """初始化指令存儲服務
        
        Args:
            storage_type: 存儲類型 ("sqlite" 或 "json")
            **storage_kwargs: 存儲參數
        """
        # 設置默認參數
        if storage_type == "sqlite":
            default_kwargs = {"db_path": "data/commands.db", "table_name": "commands"}
        else:  # json
            default_kwargs = {"base_dir": "data/commands"}
        
        # 合併默認參數和提供的參數
        storage_kwargs = {**default_kwargs, **storage_kwargs}
        
        # 創建存儲實例
        self.storage = StorageFactory.create_storage(storage_type, **storage_kwargs)
    
    async def save_command(self, command: Union[MCPCommand, Dict[str, Any]]) -> StorageResult:
        """保存指令
        
        Args:
            command: 指令對象或字典
            
        Returns:
            存儲操作結果
        """
        # 確保command_id存在
        if isinstance(command, MCPCommand):
            command_id = command.command_id
            command_data = command.model_dump()
        else:
            command_id = command.get("command_id")
            if not command_id:
                return StorageResult.error("指令缺少command_id")
            command_data = command
        
        # 保存指令
        return await self.storage.save(command_id, command_data)
    
    async def get_command(self, command_id: str) -> StorageResult:
        """獲取指令
        
        Args:
            command_id: 指令ID
            
        Returns:
            包含指令的存儲操作結果
        """
        return await self.storage.get(command_id)
    
    async def update_command(self, command_id: str, updates: Dict[str, Any]) -> StorageResult:
        """更新指令
        
        Args:
            command_id: 指令ID
            updates: 更新數據
            
        Returns:
            存儲操作結果
        """
        # 先獲取現有指令
        result = await self.storage.get(command_id)
        if not result.success:
            return result
        
        # 合併更新
        command_data = result.data
        command_data.update(updates)
        
        # 更新時間戳
        command_data["updated_at"] = datetime.now()
        
        # 保存更新後的指令
        return await self.storage.update(command_id, command_data)
    
    async def update_command_status(
        self, 
        command_id: str, 
        status: CommandStatus,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> StorageResult:
        """更新指令狀態
        
        Args:
            command_id: 指令ID
            status: 新狀態
            result: 結果數據
            error: 錯誤消息
            
        Returns:
            存儲操作結果
        """
        updates = {"status": status.value if isinstance(status, CommandStatus) else status}
        
        # 添加可選字段
        if result is not None:
            updates["result"] = result
        
        if error is not None:
            updates["error"] = error
        
        # 根據狀態設置時間戳
        if status == CommandStatus.COMPLETED:
            updates["completed_at"] = datetime.now()
        elif status == CommandStatus.FAILED:
            updates["failed_at"] = datetime.now()
        elif status == CommandStatus.CANCELLED:
            updates["cancelled_at"] = datetime.now()
        
        return await self.update_command(command_id, updates)
    
    async def delete_command(self, command_id: str) -> StorageResult:
        """刪除指令
        
        Args:
            command_id: 指令ID
            
        Returns:
            存儲操作結果
        """
        return await self.storage.delete(command_id)
    
    async def get_command_history(
        self, 
        limit: int = 100, 
        offset: int = 0,
        status: Optional[Union[CommandStatus, List[CommandStatus]]] = None
    ) -> StorageResult:
        """獲取指令歷史
        
        Args:
            limit: 返回數量限制
            offset: 起始偏移
            status: 過濾狀態
            
        Returns:
            包含指令列表的存儲操作結果
        """
        # 對於SQLite存儲，可以使用自定義查詢
        if hasattr(self.storage, "query"):
            # 構建SQL查詢
            sql = "SELECT key, data FROM commands"
            params = []
            
            # 添加狀態過濾
            if status:
                if isinstance(status, list):
                    placeholders = ", ".join(["?" for _ in status])
                    status_values = [s.value if isinstance(s, CommandStatus) else s for s in status]
                    sql += f" WHERE json_extract(data, '$.status') IN ({placeholders})"
                    params.extend(status_values)
                else:
                    status_value = status.value if isinstance(status, CommandStatus) else status
                    sql += " WHERE json_extract(data, '$.status') = ?"
                    params.append(status_value)
            
            # 添加分頁
            sql += " ORDER BY json_extract(data, '$.created_at') DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            # 執行查詢
            result = await self.storage.query(sql, tuple(params))
            if not result.success:
                return result
            
            # 解析數據
            commands = []
            for _, data_json in result.data:
                try:
                    command_data = json.loads(data_json)
                    commands.append(command_data)
                except json.JSONDecodeError:
                    continue
            
            return StorageResult.ok(f"已獲取 {len(commands)} 條指令記錄", commands)
        
        # 對於其他類型的存儲，獲取所有鍵然後過濾
        else:
            # 獲取所有鍵
            list_result = await self.storage.list()
            if not list_result.success:
                return list_result
            
            keys = list_result.data
            commands = []
            
            # 獲取每個指令的數據
            for key in keys:
                get_result = await self.storage.get(key)
                if get_result.success:
                    command_data = get_result.data
                    
                    # 狀態過濾
                    if status:
                        command_status = command_data.get("status")
                        if isinstance(status, list):
                            status_values = [s.value if isinstance(s, CommandStatus) else s for s in status]
                            if command_status not in status_values:
                                continue
                        elif command_status != (status.value if isinstance(status, CommandStatus) else status):
                            continue
                    
                    commands.append(command_data)
            
            # 排序和分頁
            commands.sort(key=lambda x: x.get("created_at", datetime.min), reverse=True)
            paginated_commands = commands[offset:offset+limit]
            
            return StorageResult.ok(f"已獲取 {len(paginated_commands)} 條指令記錄", paginated_commands)
    
    async def count_commands(self, status: Optional[Union[CommandStatus, List[CommandStatus]]] = None) -> int:
        """計算指令數量
        
        Args:
            status: 過濾狀態
            
        Returns:
            指令數量
        """
        # 對於SQLite存儲，使用自定義查詢
        if hasattr(self.storage, "query"):
            # 構建SQL查詢
            sql = "SELECT COUNT(*) FROM commands"
            params = []
            
            # 添加狀態過濾
            if status:
                if isinstance(status, list):
                    placeholders = ", ".join(["?" for _ in status])
                    status_values = [s.value if isinstance(s, CommandStatus) else s for s in status]
                    sql += f" WHERE json_extract(data, '$.status') IN ({placeholders})"
                    params.extend(status_values)
                else:
                    status_value = status.value if isinstance(status, CommandStatus) else status
                    sql += " WHERE json_extract(data, '$.status') = ?"
                    params.append(status_value)
            
            # 執行查詢
            result = await self.storage.query(sql, tuple(params))
            if result.success and result.data:
                return result.data[0][0]
            return 0
        
        # 對於其他類型的存儲，獲取所有鍵然後計算
        else:
            # 獲取指令歷史，不限制數量
            result = await self.get_command_history(limit=100000, status=status)
            if result.success:
                return len(result.data)
            return 0
    
    async def cleanup_old_commands(self, days: int = 30) -> StorageResult:
        """清理舊指令
        
        Args:
            days: 保留天數
            
        Returns:
            存儲操作結果
        """
        # 計算截止日期
        cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
        
        # 對於SQLite存儲，使用自定義查詢
        if hasattr(self.storage, "query"):
            # 獲取要刪除的指令ID
            sql = "SELECT key FROM commands WHERE json_extract(data, '$.created_at') < ?"
            result = await self.storage.query(sql, (cutoff_date.isoformat(),))
            
            if not result.success:
                return result
            
            # 刪除每個指令
            deleted_count = 0
            for (key,) in result.data:
                delete_result = await self.storage.delete(key)
                if delete_result.success:
                    deleted_count += 1
            
            return StorageResult.ok(f"已清理 {deleted_count} 條舊指令")
        
        # 對於其他類型的存儲，獲取所有指令然後過濾刪除
        else:
            # 獲取所有指令
            result = await self.get_command_history(limit=100000)
            if not result.success:
                return result
            
            # 過濾出舊指令
            deleted_count = 0
            for command in result.data:
                created_at = command.get("created_at")
                if isinstance(created_at, str):
                    try:
                        created_at = datetime.fromisoformat(created_at)
                    except ValueError:
                        continue
                
                if created_at < cutoff_date:
                    delete_result = await self.storage.delete(command.get("command_id"))
                    if delete_result.success:
                        deleted_count += 1
            
            return StorageResult.ok(f"已清理 {deleted_count} 條舊指令") 