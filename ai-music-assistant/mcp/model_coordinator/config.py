"""配置模組

提供系統配置功能
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

class Config:
    """配置類"""
    def __init__(self, **data):
        """初始化配置
        
        Args:
            **data: 配置參數
        """
        # 基本路徑
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        # 臨時文件目錄
        self.temp_dir = os.path.join(self.base_dir, "temp")
        
        # 日誌目錄
        self.log_dir = os.path.join(self.base_dir, "logs")
        
        # 字體目錄
        self.font_dir = os.path.join(self.base_dir, "fonts")
        
        # 音色庫目錄
        self.soundfont_dir = os.path.join(self.base_dir, "soundfonts")
        
        # 默認音色庫
        self.default_soundfont = os.path.join(self.soundfont_dir, "default.sf2")
        
        # 更新自定義配置
        for key, value in data.items():
            setattr(self, key, value)
        
        self._create_directories()
    
    def _create_directories(self):
        """創建必要的目錄"""
        for dir_path in [self.temp_dir, self.log_dir, self.font_dir, self.soundfont_dir]:
            os.makedirs(dir_path, exist_ok=True)
    
    def get(self, key: str, default: Any = None) -> Any:
        """獲取配置值
        
        Args:
            key: 配置鍵，可以使用點號分隔的路徑，如 "storage.db_path"
            default: 默認值，如果配置不存在則返回
            
        Returns:
            配置值
        """
        if "." in key:
            parts = key.split(".")
            value = self
            for part in parts:
                if hasattr(value, part):
                    value = getattr(value, part)
                else:
                    return default
            return value
        else:
            return getattr(self, key, default) 