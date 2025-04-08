"""配置模組

提供系統配置功能
"""

import os
import logging
from pathlib import Path

# 嘗試導入pydantic，如果不可用則使用簡單替代模型
try:
    from pydantic import BaseModel, Field
    USE_PYDANTIC = True
except ImportError:
    logging.warning("無法導入pydantic，使用基本類型替代。某些功能可能不可用。")
    USE_PYDANTIC = False
    
    # 創建簡單替代類
    class BaseModel:
        def __init__(self, **data):
            for key, value in data.items():
                setattr(self, key, value)
                
    # 簡單的Field替代函數
    def Field(*args, **kwargs):
        return None

class Config(BaseModel):
    """配置類"""
    # 基本路徑
    base_dir: str = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    # 臨時文件目錄
    temp_dir: str = os.path.join(base_dir, "temp")
    
    # 日誌目錄
    log_dir: str = os.path.join(base_dir, "logs")
    
    # 字體目錄
    font_dir: str = os.path.join(base_dir, "fonts")
    
    # 音色庫目錄
    soundfont_dir: str = os.path.join(base_dir, "soundfonts")
    
    # 默認音色庫
    default_soundfont: str = os.path.join(soundfont_dir, "default.sf2")
    
    def __init__(self, **data):
        if USE_PYDANTIC:
            super().__init__(**data)
        else:
            for key, value in data.items():
                setattr(self, key, value)
        self._create_directories()
    
    def _create_directories(self):
        """創建必要的目錄"""
        for dir_path in [self.temp_dir, self.log_dir, self.font_dir, self.soundfont_dir]:
            os.makedirs(dir_path, exist_ok=True)

__all__ = ['Config'] 