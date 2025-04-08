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


class CommandType(str, Enum):
    """MCP 指令類型枚舉"""
    TEXT_TO_MUSIC = "text_to_music"
    MELODY_TO_ARRANGEMENT = "melody_to_arrangement"
    MUSIC_ANALYSIS = "music_analysis"
    PITCH_CORRECTION = "pitch_correction"
    STYLE_TRANSFER = "style_transfer"
    IMPROVISATION = "improvisation"


class ModelType(str, Enum):
    """AI模型類型枚舉"""
    MAGENTA = "magenta"
    MUSIC21 = "music21"
    BASIC_PITCH = "basic_pitch"
    DDSP = "ddsp"
    MUSENET = "musenet"
    RNN_COMPOSER = "rnn_composer"


class ProcessingStatus(str, Enum):
    """處理狀態枚舉"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# 為了向後兼容，CommandStatus 是 ProcessingStatus 的別名
CommandStatus = ProcessingStatus


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
    C_FLAT_MAJOR = "Cb"
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
    A_FLAT_MINOR = "Abm"


class TimeSignature(str, Enum):
    """拍號枚舉"""
    FOUR_FOUR = "4/4"
    THREE_FOUR = "3/4"
    SIX_EIGHT = "6/8"
    TWO_FOUR = "2/4"
    FIVE_FOUR = "5/4"
    SEVEN_EIGHT = "7/8"
    TWELVE_EIGHT = "12/8"
    NINE_EIGHT = "9/8"
    THREE_EIGHT = "3/8"


class Genre(str, Enum):
    """音樂風格枚舉"""
    POP = "pop"
    ROCK = "rock"
    JAZZ = "jazz"
    CLASSICAL = "classical"
    ELECTRONIC = "electronic"
    FOLK = "folk"
    HIP_HOP = "hip_hop"
    RNB = "rnb"
    COUNTRY = "country"
    BLUES = "blues"
    AMBIENT = "ambient"
    FUNK = "funk"
    LATIN = "latin"
    WORLD = "world"


class Emotion(str, Enum):
    """情感描述枚舉"""
    HAPPY = "happy"
    SAD = "sad"
    ENERGETIC = "energetic"
    CALM = "calm"
    ROMANTIC = "romantic"
    DARK = "dark"
    NOSTALGIC = "nostalgic"
    EPIC = "epic"
    PLAYFUL = "playful"
    MYSTERIOUS = "mysterious"
    ANXIOUS = "anxious"
    HOPEFUL = "hopeful"
    DREAMY = "dreamy"
    ANGRY = "angry"


class InstrumentType(str, Enum):
    """樂器類型枚舉"""
    PIANO = "piano"
    GUITAR = "guitar"
    DRUMS = "drums"
    BASS = "bass"
    STRINGS = "strings"
    BRASS = "brass"
    WOODWINDS = "woodwinds"
    SYNTH = "synth"
    VOCAL = "vocal"
    ORGAN = "organ"
    PERCUSSION = "percussion"
    HARP = "harp"
    MARIMBA = "marimba"
    ACCORDION = "accordion"


class MusicalForm(str, Enum):
    """音樂形式枚舉"""
    VERSE_CHORUS = "verse_chorus"
    ABA = "aba"
    RONDO = "rondo"
    THROUGH_COMPOSED = "through_composed"
    THEME_VARIATIONS = "theme_variations"
    SONATA = "sonata"
    BINARY = "binary"
    TERNARY = "ternary"


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


class AudioInput(BaseModel):
    """音訊輸入模型"""
    audio_data_url: str = Field(..., description="Base64 編碼的錄音數據")
    format: str = Field("wav", description="音訊格式")
    sample_rate: Optional[int] = Field(44100, description="採樣率 (Hz)")


class ChordProgression(BaseModel):
    """和弦進行模型"""
    chords: List[str] = Field(..., description="和弦標記列表")
    durations: List[float] = Field(..., description="每個和弦的持續時間")

    @validator('durations')
    def check_durations_length(cls, v, values):
        if 'chords' in values and len(values['chords']) != len(v):
            raise ValueError("和弦數量必須與持續時間數量相同")
        return v


class MusicParameters(BaseModel):
    """音樂參數模型"""
    key: Optional[MusicKey] = Field(None, description="音樂調性")
    tempo: Optional[int] = Field(None, description="每分鐘拍數 (BPM)", ge=40, le=240)
    time_signature: Optional[TimeSignature] = Field(None, description="拍號")
    genre: Optional[Genre] = Field(None, description="音樂風格")
    emotion: Optional[Emotion] = Field(None, description="情感描述")
    instruments: Optional[List[InstrumentType]] = Field(None, description="樂器清單")
    duration: Optional[int] = Field(None, description="音樂長度（秒）", ge=5, le=600)
    form: Optional[MusicalForm] = Field(None, description="音樂形式")
    complexity: Optional[int] = Field(None, description="複雜度 (1-10)", ge=1, le=10)

    def update(self, parameters: Dict[str, Any]) -> None:
        """更新參數
        
        Args:
            parameters: 新的參數字典
        """
        # 處理特殊類型
        if "key" in parameters and isinstance(parameters["key"], str):
            parameters["key"] = MusicKey(parameters["key"])
        if "genre" in parameters and isinstance(parameters["genre"], str):
            parameters["genre"] = Genre(parameters["genre"])
        if "emotion" in parameters and isinstance(parameters["emotion"], str):
            parameters["emotion"] = Emotion(parameters["emotion"])
        if "time_signature" in parameters and isinstance(parameters["time_signature"], str):
            parameters["time_signature"] = TimeSignature(parameters["time_signature"])
        if "form" in parameters and isinstance(parameters["form"], str):
            parameters["form"] = MusicalForm(parameters["form"])
        if "instruments" in parameters and isinstance(parameters["instruments"], list):
            parameters["instruments"] = [InstrumentType(i) if isinstance(i, str) else i for i in parameters["instruments"]]
        
        # 合併當前參數和新參數
        current_data = self.model_dump()
        current_data.update(parameters)
        
        # 使用model_validate更新參數
        updated = self.model_validate(current_data)
        for field in self.model_fields:
            setattr(self, field, getattr(updated, field))


class ScoreData(BaseModel):
    """樂譜數據模型"""
    musicxml: Optional[str] = Field(None, description="MusicXML數據 (Base64)")
    pdf: Optional[str] = Field(None, description="PDF樂譜 (Base64)")
    svg: Optional[str] = Field(None, description="SVG樂譜 (Base64)")


class MusicData(BaseModel):
    """音樂數據模型"""
    audio_data: Optional[str] = Field(None, description="音頻數據 (Base64)")
    midi_data: Optional[str] = Field(None, description="MIDI數據 (Base64)")
    score_data: Optional[ScoreData] = Field(None, description="樂譜數據")
    tracks: Optional[Dict[str, List[Note]]] = Field(None, description="多軌道音符數據")


class MusicTheoryAnalysis(BaseModel):
    """音樂理論分析結果模型"""
    key: MusicKey = Field(..., description="偵測到的調性")
    chord_progression: ChordProgression = Field(..., description="和弦進行")
    time_signature: TimeSignature = Field(..., description="偵測到的拍號")
    tempo: int = Field(..., description="偵測到的速度 (BPM)")
    structure: Dict[str, List[int]] = Field(..., description="結構分析 (段落標記和小節數)")
    harmony_issues: Optional[List[str]] = Field(None, description="和聲問題清單")
    suggestions: Optional[List[str]] = Field(None, description="改進建議")
    complexity_analysis: Optional[Dict[str, Any]] = Field(None, description="複雜度分析")
    melody_patterns: Optional[List[List[int]]] = Field(None, description="旋律模式分析")


class MCPCommand(BaseModel):
    """MCP 指令模型"""
    command_type: CommandType = Field(..., description="指令類型")
    text_input: Optional[str] = Field(None, description="文字描述輸入")
    melody_input: Optional[MelodyInput] = Field(None, description="旋律輸入")
    audio_input: Optional[AudioInput] = Field(None, description="音訊輸入")
    parameters: Optional[MusicParameters] = Field(None, description="音樂參數")
    model_preferences: Optional[List[ModelType]] = Field(None, description="偏好使用的模型")
    created_at: datetime = Field(default_factory=datetime.now, description="創建時間")

    @validator('text_input', 'melody_input', 'audio_input')
    def check_required_input(cls, v, values, **kwargs):
        field_name = kwargs['field'].name
        if 'command_type' in values:
            command_type = values['command_type']
            
            if command_type == CommandType.TEXT_TO_MUSIC and field_name == 'text_input' and not v:
                raise ValueError("文字描述輸入為必填")
            elif command_type == CommandType.MELODY_TO_ARRANGEMENT and field_name == 'melody_input' and not v:
                raise ValueError("旋律輸入為必填")
            elif command_type == CommandType.PITCH_CORRECTION and field_name == 'audio_input' and not v:
                raise ValueError("音訊輸入為必填")
        
        return v


class MCPResponse(BaseModel):
    """MCP 回應模型"""
    command_id: str = Field(..., description="指令ID")
    status: ProcessingStatus = Field(..., description="處理狀態")
    music_data: Optional[MusicData] = Field(None, description="生成的音樂數據")
    analysis: Optional[MusicTheoryAnalysis] = Field(None, description="音樂分析結果")
    error: Optional[str] = Field(None, description="錯誤訊息")
    suggestions: Optional[List[str]] = Field(None, description="建議")
    models_used: Optional[List[ModelType]] = Field(None, description="使用的模型")
    processing_time: Optional[float] = Field(None, description="處理時間（秒）")
    created_at: datetime = Field(default_factory=datetime.now, description="創建時間")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新時間") 