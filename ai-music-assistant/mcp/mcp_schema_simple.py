"""簡化版MCP Schema

這個模塊是mcp_schema.py的簡化版，不依賴pydantic，
僅用於提供基本類型定義和導入支持，不包含驗證邏輯。
"""

from enum import Enum
from typing import List, Optional, Dict, Any


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


class ProcessingStatus(str, Enum):
    """處理狀態枚舉"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# 為了向後兼容，CommandStatus 是 ProcessingStatus 的別名
CommandStatus = ProcessingStatus


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


class Note:
    """音符模型"""
    def __init__(self, pitch, start_time, duration, velocity=64):
        self.pitch = pitch
        self.start_time = start_time
        self.duration = duration
        self.velocity = velocity


class MelodyInput:
    """旋律輸入模型"""
    def __init__(self, notes, tempo=None):
        self.notes = notes
        self.tempo = tempo


class AudioInput:
    """音訊輸入模型"""
    def __init__(self, audio_data_url, format="wav", sample_rate=44100):
        self.audio_data_url = audio_data_url
        self.format = format
        self.sample_rate = sample_rate


class ChordProgression:
    """和弦進行模型"""
    def __init__(self, chords, durations):
        self.chords = chords
        self.durations = durations


class ScoreData:
    """樂譜數據模型"""
    def __init__(self, musicxml=None, pdf=None, svg=None):
        self.musicxml = musicxml
        self.pdf = pdf
        self.svg = svg


class MusicData:
    """音樂數據模型"""
    def __init__(self, audio_data=None, midi_data=None, score_data=None, tracks=None, cover_image=None):
        self.audio_data = audio_data
        self.midi_data = midi_data
        self.score_data = score_data
        self.tracks = tracks
        self.cover_image = cover_image


class MusicParameters:
    """音樂參數模型"""
    def __init__(self, key=None, tempo=None, time_signature=None, genre=None, emotion=None, 
                 instruments=None, duration=None, form=None, complexity=None, description=None,
                 mood=None, style=None):
        self.key = key
        self.tempo = tempo
        self.time_signature = time_signature
        self.genre = genre
        self.emotion = emotion
        self.instruments = instruments or []
        self.duration = duration
        self.form = form
        self.complexity = complexity
        self.description = description
        self.mood = mood
        self.style = style
        
    def update(self, parameters: Dict[str, Any]) -> None:
        """更新參數"""
        for key, value in parameters.items():
            setattr(self, key, value)


class MusicTheoryAnalysis:
    """音樂理論分析結果模型"""
    def __init__(self, key, chord_progression, time_signature, tempo, structure,
                 harmony_issues=None, suggestions=None, complexity_analysis=None, melody_patterns=None):
        self.key = key
        self.chord_progression = chord_progression
        self.time_signature = time_signature
        self.tempo = tempo
        self.structure = structure
        self.harmony_issues = harmony_issues
        self.suggestions = suggestions
        self.complexity_analysis = complexity_analysis
        self.melody_patterns = melody_patterns


class MCPCommand:
    """MCP 指令模型"""
    def __init__(self, command_type, text_input=None, melody_input=None, audio_input=None,
                 parameters=None, model_preferences=None):
        self.command_type = command_type
        self.text_input = text_input
        self.melody_input = melody_input
        self.audio_input = audio_input
        self.parameters = parameters
        self.model_preferences = model_preferences


class MCPResponse:
    """MCP 回應模型"""
    def __init__(self, command_id, status, music_data=None, analysis=None, error=None,
                 suggestions=None, models_used=None, processing_time=None):
        self.command_id = command_id
        self.status = status
        self.music_data = music_data
        self.analysis = analysis
        self.error = error
        self.suggestions = suggestions
        self.models_used = models_used
        self.processing_time = processing_time 