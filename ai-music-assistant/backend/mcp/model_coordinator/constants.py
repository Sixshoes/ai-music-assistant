"""常量定義模組

定義系統中使用的常量和枚舉類型
"""

from enum import Enum

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

class InstrumentType(str, Enum):
    """樂器類型枚舉"""
    PIANO = "piano"
    GUITAR = "guitar"
    BASS = "bass"
    DRUMS = "drums"
    STRINGS = "strings"
    BRASS = "brass"
    WOODWINDS = "woodwinds"
    SYNTH = "synth"
    PAD = "pad"
    LEAD = "lead"

class CommandStatus(str, Enum):
    """命令狀態枚舉"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# 命令超時時間（秒）
COMMAND_TIMEOUT = 300

# 音頻相關常量
SAMPLE_RATE = 44100
CHANNELS = 2
BIT_DEPTH = 16

# 音樂生成相關常量
DEFAULT_TEMPO = 120
DEFAULT_KEY = "C"
DEFAULT_TIME_SIGNATURE = "4/4"
DEFAULT_DURATION = 180  # 秒
DEFAULT_COMPLEXITY = 3  # 1-5
DEFAULT_INSTRUMENTS = ["piano"]

# 檔案路徑
SOUNDFONT_PATH = "mcp/model_coordinator/soundfonts/FluidR3_GM.sf2"
TEMP_DIR = "temp"

# 默認音頻參數
DEFAULT_SAMPLE_RATE = 44100
DEFAULT_CHANNELS = 2
DEFAULT_BIT_DEPTH = 16

# MIDI 相關常量
MIDI_TICKS_PER_BEAT = 480
MIDI_TEMPO = 500000  # 微秒/拍，相當於 120 BPM

# 音頻生成相關常量
MIN_DURATION = 10  # 最小音頻時長（秒）
MAX_DURATION = 600  # 最大音頻時長（秒）

# 樂器相關常量
DEFAULT_VELOCITY = 100  # 默認音符力度
DEFAULT_PROGRAM = 0  # 默認 MIDI 程序（大鋼琴）

# 音樂理論相關常量
NOTES_IN_OCTAVE = 12
MIN_OCTAVE = 0
MAX_OCTAVE = 8
DEFAULT_OCTAVE = 4

# 文件路徑相關常量
OUTPUT_DIR = "output"

# 錯誤重試相關常量
MAX_RETRIES = 3
RETRY_DELAY = 1  # 重試延遲（秒） 