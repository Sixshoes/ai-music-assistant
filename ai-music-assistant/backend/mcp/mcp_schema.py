"""MCP 模式定義

提供音樂創作處理模型的數據模型
"""

from enum import Enum
from typing import List, Optional, Union, Dict, Any, Tuple
import logging

# 嘗試導入pydantic，如果不可用則使用簡單替代模型
try:
    from pydantic import BaseModel, Field, validator
    USE_PYDANTIC = True
except ImportError:
    logging.warning("無法導入pydantic，使用基本類型替代。某些功能可能不可用。")
    USE_PYDANTIC = False
    
    # 創建簡單替代類
    class BaseModel:
        def __init__(self, **data):
            for key, value in data.items():
                setattr(self, key, value)
                
        @classmethod
        def model_validate(cls, data):
            return cls(**data)
            
        def model_dump(self):
            return {k: v for k, v in self.__dict__.items() 
                   if not k.startswith('_') and not callable(v)}
    
    # 簡單的Field替代函數
    def Field(*args, **kwargs):
        return None
        
    # 簡單的validator替代裝飾器
    def validator(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
from datetime import datetime

class MusicKey(str, Enum):
    """音樂調性枚舉"""
    C_MAJOR = "C"
    G_MAJOR = "G"
    D_MAJOR = "D"
    A_MAJOR = "A"
    E_MAJOR = "E"
    B_MAJOR = "B"
    F_SHARP_MAJOR = "F#"
    C_SHARP_MAJOR = "C#"
    F_MAJOR = "F"
    B_FLAT_MAJOR = "Bb"
    E_FLAT_MAJOR = "Eb"
    A_FLAT_MAJOR = "Ab"
    D_FLAT_MAJOR = "Db"
    G_FLAT_MAJOR = "Gb"
    A_MINOR = "Am"
    E_MINOR = "Em"
    B_MINOR = "Bm"
    F_SHARP_MINOR = "F#m"
    C_SHARP_MINOR = "C#m"
    G_SHARP_MINOR = "G#m"
    D_SHARP_MINOR = "D#m"
    A_SHARP_MINOR = "A#m"
    D_MINOR = "Dm"
    G_MINOR = "Gm"
    C_MINOR = "Cm"
    F_MINOR = "Fm"
    B_FLAT_MINOR = "Bbm"
    E_FLAT_MINOR = "Ebm"

class TimeSignature(str, Enum):
    """拍號枚舉"""
    TWO_FOUR = "2/4"
    THREE_FOUR = "3/4"
    FOUR_FOUR = "4/4"
    THREE_EIGHT = "3/8"
    SIX_EIGHT = "6/8"
    NINE_EIGHT = "9/8"
    TWELVE_EIGHT = "12/8"

class Genre(str, Enum):
    """音樂風格枚舉"""
    POP = "pop"
    ROCK = "rock"
    JAZZ = "jazz"
    CLASSICAL = "classical"
    ELECTRONIC = "electronic"
    FOLK = "folk"
    BLUES = "blues"
    COUNTRY = "country"
    HIPHOP = "hiphop"
    RNB = "rnb"
    LATIN = "latin"
    METAL = "metal"
    PUNK = "punk"
    REGGAE = "reggae"
    SOUL = "soul"
    FUNK = "funk"
    DISCO = "disco"
    AMBIENT = "ambient"
    WORLD = "world"

class InstrumentType(str, Enum):
    """樂器類型枚舉"""
    PIANO = "piano"
    GUITAR = "guitar"
    BASS = "bass"
    DRUMS = "drums"
    STRINGS = "strings"
    BRASS = "brass"
    WOODWINDS = "woodwinds"
    SYNTHESIZER = "synthesizer"
    PERCUSSION = "percussion"
    VOICE = "voice"
    ORGAN = "organ"
    HARP = "harp"
    ACCORDION = "accordion"
    HARMONICA = "harmonica"
    BANJO = "banjo"
    MANDOLIN = "mandolin"
    UKULELE = "ukulele"
    VIOLIN = "violin"
    VIOLA = "viola"
    CELLO = "cello"
    DOUBLE_BASS = "double_bass"
    FLUTE = "flute"
    CLARINET = "clarinet"
    SAXOPHONE = "saxophone"
    TRUMPET = "trumpet"
    TROMBONE = "trombone"
    FRENCH_HORN = "french_horn"
    TUBA = "tuba"

class CommandStatus(str, Enum):
    """命令狀態枚舉"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Note(BaseModel):
    """音符模型"""
    pitch: int = Field(..., description="MIDI音高 (0-127)", ge=0, le=127)
    start_time: float = Field(..., description="開始時間（秒）", ge=0)
    duration: float = Field(..., description="持續時間（秒）", gt=0)
    velocity: int = Field(64, description="力度 (1-127)", ge=1, le=127)

    @validator('duration')
    def check_positive_duration(cls, v):
        if v <= 0:
            raise ValueError("持續時間必須為正數")
        return v

class MelodyInput(BaseModel):
    """旋律輸入模型"""
    notes: List[Note] = Field(..., description="旋律音符序列")
    tempo: Optional[int] = Field(None, description="旋律速度", ge=40, le=240)

class MusicParameters(BaseModel):
    """音樂參數模型"""
    description: str = Field(
        default="自動生成的音樂",
        description="音樂描述"
    )
    tempo: int = Field(
        default=120,
        ge=40,
        le=240,
        description="速度（每分鐘拍數）"
    )
    key: MusicKey = Field(
        default=MusicKey.C_MAJOR,
        description="調性"
    )
    time_signature: TimeSignature = Field(
        default=TimeSignature.FOUR_FOUR,
        description="拍號"
    )
    genre: Genre = Field(
        default=Genre.POP,
        description="音樂風格"
    )
    instruments: List[InstrumentType] = Field(
        default=[InstrumentType.PIANO],
        description="樂器列表"
    )
    duration: int = Field(
        default=60,
        ge=10,
        le=300,
        description="時長（秒）"
    )
    complexity: int = Field(
        default=3,
        ge=1,
        le=5,
        description="複雜度（1-5）"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "description": "輕快的流行音樂",
                "tempo": 120,
                "key": "C",
                "time_signature": "4/4",
                "genre": "pop",
                "instruments": ["piano", "guitar"],
                "duration": 60,
                "complexity": 3
            }
        }
    }

class MCPCommand(BaseModel):
    """MCP命令模型"""
    command_id: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y%m%d%H%M%S"),
        description="命令ID"
    )
    type: str = Field(
        ...,
        description="命令類型"
    )
    text_input: Optional[str] = Field(
        None,
        description="文字輸入"
    )
    audio_input: Optional[str] = Field(
        None,
        description="音頻輸入（Base64編碼）"
    )
    parameters: Optional[MusicParameters] = Field(
        None,
        description="音樂參數"
    )
    status: CommandStatus = Field(
        default=CommandStatus.PENDING,
        description="命令狀態"
    )
    result: Optional[Dict[str, Any]] = Field(
        None,
        description="處理結果"
    )
    error: Optional[str] = Field(
        None,
        description="錯誤信息"
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="創建時間"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="更新時間"
    )
    completed_at: Optional[datetime] = Field(
        None,
        description="完成時間"
    )

class MCPResponse(BaseModel):
    """MCP響應模型"""
    command_id: str = Field(
        ...,
        description="命令ID"
    )
    status: CommandStatus = Field(
        ...,
        description="命令狀態"
    )
    result: Optional[Dict[str, Any]] = Field(
        None,
        description="處理結果"
    )
    error: Optional[str] = Field(
        None,
        description="錯誤信息"
    ) 