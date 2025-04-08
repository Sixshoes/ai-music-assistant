"""工具模組

提供各種工具函數
"""

import os
import json
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from .config import Config

async def save_command(command: Dict[str, Any], command_dir: str = "commands") -> None:
    """保存命令到文件
    
    Args:
        command: 命令數據
        command_dir: 命令文件目錄
    """
    # 創建命令目錄
    command_dir = Path(command_dir)
    command_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成文件名
    filename = f"{command['command_id']}.json"
    filepath = command_dir / filename
    
    # 轉換日期時間為字符串
    command_data = command.copy()
    for key in ['created_at', 'updated_at', 'completed_at']:
        if key in command_data and isinstance(command_data[key], datetime):
            command_data[key] = command_data[key].isoformat()
    
    # 保存到文件
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(command_data, f, ensure_ascii=False, indent=2)

async def get_command(command_id: str, command_dir: str = "commands") -> Optional[Dict[str, Any]]:
    """從文件獲取命令
    
    Args:
        command_id: 命令ID
        command_dir: 命令文件目錄
        
    Returns:
        命令數據，如果不存在則返回 None
    """
    # 構建文件路徑
    filepath = Path(command_dir) / f"{command_id}.json"
    
    # 檢查文件是否存在
    if not filepath.exists():
        return None
    
    # 讀取文件
    with open(filepath, 'r', encoding='utf-8') as f:
        command_data = json.load(f)
    
    # 轉換日期時間字符串為對象
    for key in ['created_at', 'updated_at', 'completed_at']:
        if key in command_data and isinstance(command_data[key], str):
            command_data[key] = datetime.fromisoformat(command_data[key])
    
    return command_data 