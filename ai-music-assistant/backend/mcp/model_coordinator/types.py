"""類型定義模組

定義系統中使用的自定義類型
"""

import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

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

class CommandResult(BaseModel):
    """命令執行結果"""
    music_data: Dict[str, Any]
    analysis: Dict[str, Any]
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "music_data": {
                    "midi_data": "base64_encoded_midi_data",
                    "audio_data": "base64_encoded_audio_data",
                    "score_data": {
                        "musicxml": "base64_encoded_musicxml",
                        "pdf": "base64_encoded_pdf"
                    }
                },
                "analysis": {
                    "key": "C",
                    "tempo": 120,
                    "time_signature": "4/4",
                    "genre": "pop",
                    "chord_progression": ["C", "G", "Am", "F"],
                    "mood": "happy",
                    "complexity": 3
                },
                "created_at": "2024-04-06T12:00:00",
                "completed_at": "2024-04-06T12:01:00"
            }
        }
    }

    def __init__(self, **data):
        super().__init__(**data)
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def complete(self, music_data: Dict[str, Any], analysis: Dict[str, Any]):
        """完成命令執行
        
        Args:
            music_data: 音樂數據
            analysis: 分析結果
        """
        self.music_data = music_data
        self.analysis = analysis
        self.completed_at = datetime.now()
    
    @property
    def duration(self) -> float:
        """獲取執行時長（秒）"""
        if self.completed_at and self.created_at:
            return (self.completed_at - self.created_at).total_seconds()
        return 0.0 