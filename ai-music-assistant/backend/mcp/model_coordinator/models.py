"""模型協調器定義

實現與不同AI模型交互的協調器組件
"""

import logging
from typing import Dict, List, Optional, Any, Callable, Union

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

class MusicParameters(BaseModel):
    description: str
    duration: int = Field(default=30, ge=10, le=300)
    tempo: int = Field(default=120, ge=40, le=200)
    key: str = Field(default="C", pattern="^[A-G][b#]?$")
    genre: str = Field(default="pop", pattern="^(pop|jazz|classical|rock|electronic|blues|folk)$")
    instruments: List[str] = Field(default=["piano"])
    complexity: float = Field(default=3.0, ge=0.0, le=5.0)
    mood: str = Field(default="happy", pattern="^(happy|sad|energetic|calm|mysterious)$")
    style: str = Field(default="normal", pattern="^(normal|staccato|legato|arpeggio)$") 