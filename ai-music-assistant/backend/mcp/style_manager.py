"""風格管理器

處理不同音樂風格的特性，包括樂器配置、演奏方式、節奏型態和和聲進行
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
from .mcp_schema import Genre, InstrumentType

class PlayingStyle(Enum):
    """演奏風格"""
    LEGATO = "legato"  # 連奏
    STACCATO = "staccato"  # 斷奏
    TREMOLO = "tremolo"  # 顫音
    PIZZICATO = "pizzicato"  # 撥奏
    NORMAL = "normal"  # 普通演奏
    
class RhythmPattern(Enum):
    """節奏型態"""
    STRAIGHT = "straight"  # 直拍
    SWING = "swing"  # 搖擺
    SHUFFLE = "shuffle"  # 切分
    SYNCOPATED = "syncopated"  # 切分音
    WALTZ = "waltz"  # 華爾滋
    LATIN = "latin"  # 拉丁
    
class StyleManager:
    """風格管理器類"""
    
    def __init__(self):
        """初始化風格管理器"""
        # 定義各種風格的基本配置
        self.style_configs = {
            Genre.POP: {
                "instruments": {
                    "main": [InstrumentType.PIANO, InstrumentType.GUITAR],
                    "rhythm": [InstrumentType.DRUMS, InstrumentType.BASS],
                    "pad": [InstrumentType.SYNTH],
                    "optional": [InstrumentType.STRINGS]
                },
                "playing_styles": {
                    InstrumentType.PIANO: PlayingStyle.NORMAL,
                    InstrumentType.GUITAR: PlayingStyle.NORMAL,
                    InstrumentType.DRUMS: PlayingStyle.NORMAL,
                    InstrumentType.BASS: PlayingStyle.NORMAL
                },
                "rhythm_patterns": [RhythmPattern.STRAIGHT, RhythmPattern.SYNCOPATED],
                "chord_progressions": [
                    ["I", "V", "vi", "IV"],
                    ["I", "vi", "IV", "V"],
                    ["vi", "IV", "I", "V"]
                ],
                "tempo_range": (90, 130),
                "complexity_weights": {
                    "melody": 0.8,
                    "harmony": 0.6,
                    "rhythm": 0.7
                }
            },
            Genre.ROCK: {
                "instruments": {
                    "main": [InstrumentType.ELECTRIC_GUITAR, InstrumentType.ELECTRIC_GUITAR],
                    "rhythm": [InstrumentType.DRUMS, InstrumentType.BASS],
                    "pad": [InstrumentType.SYNTH],
                    "optional": [InstrumentType.PIANO]
                },
                "playing_styles": {
                    InstrumentType.ELECTRIC_GUITAR: PlayingStyle.NORMAL,
                    InstrumentType.DRUMS: PlayingStyle.NORMAL,
                    InstrumentType.BASS: PlayingStyle.NORMAL
                },
                "rhythm_patterns": [RhythmPattern.STRAIGHT, RhythmPattern.SHUFFLE],
                "chord_progressions": [
                    ["I", "IV", "V", "IV"],
                    ["I", "V", "IV", "I"],
                    ["I", "bVII", "IV", "I"]
                ],
                "tempo_range": (100, 160),
                "complexity_weights": {
                    "melody": 0.7,
                    "harmony": 0.5,
                    "rhythm": 0.9
                }
            },
            Genre.JAZZ: {
                "instruments": {
                    "main": [InstrumentType.PIANO, InstrumentType.SAXOPHONE],
                    "rhythm": [InstrumentType.DRUMS, InstrumentType.BASS],
                    "pad": [],
                    "optional": [InstrumentType.TRUMPET, InstrumentType.GUITAR]
                },
                "playing_styles": {
                    InstrumentType.PIANO: PlayingStyle.NORMAL,
                    InstrumentType.SAXOPHONE: PlayingStyle.LEGATO,
                    InstrumentType.DRUMS: PlayingStyle.NORMAL,
                    InstrumentType.BASS: PlayingStyle.NORMAL
                },
                "rhythm_patterns": [RhythmPattern.SWING],
                "chord_progressions": [
                    ["ii", "V", "I", "vi"],
                    ["I", "vi", "ii", "V"],
                    ["iii", "vi", "ii", "V"]
                ],
                "tempo_range": (80, 140),
                "complexity_weights": {
                    "melody": 0.9,
                    "harmony": 0.9,
                    "rhythm": 0.8
                }
            },
            Genre.CLASSICAL: {
                "instruments": {
                    "main": [InstrumentType.PIANO, InstrumentType.STRINGS],
                    "rhythm": [],
                    "pad": [InstrumentType.STRINGS],
                    "optional": [InstrumentType.WOODWINDS, InstrumentType.BRASS]
                },
                "playing_styles": {
                    InstrumentType.PIANO: PlayingStyle.LEGATO,
                    InstrumentType.STRINGS: PlayingStyle.LEGATO,
                    InstrumentType.WOODWINDS: PlayingStyle.LEGATO,
                    InstrumentType.BRASS: PlayingStyle.NORMAL
                },
                "rhythm_patterns": [RhythmPattern.STRAIGHT],
                "chord_progressions": [
                    ["I", "IV", "V", "I"],
                    ["I", "vi", "IV", "V"],
                    ["I", "V", "vi", "iii"]
                ],
                "tempo_range": (60, 120),
                "complexity_weights": {
                    "melody": 1.0,
                    "harmony": 0.8,
                    "rhythm": 0.6
                }
            }
        }
        
    def get_style_config(self, genre: Genre) -> Dict:
        """獲取指定風格的配置
        
        Args:
            genre: 音樂風格
            
        Returns:
            Dict: 風格配置
        """
        return self.style_configs.get(genre, self.style_configs[Genre.POP])
    
    def get_instruments(self, genre: Genre, complexity: float) -> List[InstrumentType]:
        """根據風格和複雜度獲取樂器列表
        
        Args:
            genre: 音樂風格
            complexity: 複雜度（0-1）
            
        Returns:
            List[InstrumentType]: 樂器列表
        """
        config = self.get_style_config(genre)
        instruments = []
        
        # 添加主要樂器
        instruments.extend(config["instruments"]["main"])
        
        # 添加節奏樂器
        instruments.extend(config["instruments"]["rhythm"])
        
        # 根據複雜度添加襯底樂器
        if complexity > 0.5:
            instruments.extend(config["instruments"]["pad"])
        
        # 根據複雜度添加可選樂器
        if complexity > 0.8:
            instruments.extend(config["instruments"]["optional"])
        
        return list(set(instruments))  # 去重
    
    def get_playing_style(self, genre: Genre, instrument: InstrumentType) -> PlayingStyle:
        """獲取指定風格和樂器的演奏方式
        
        Args:
            genre: 音樂風格
            instrument: 樂器類型
            
        Returns:
            PlayingStyle: 演奏方式
        """
        config = self.get_style_config(genre)
        return config["playing_styles"].get(instrument, PlayingStyle.NORMAL)
    
    def get_rhythm_pattern(self, genre: Genre) -> RhythmPattern:
        """獲取指定風格的節奏型態
        
        Args:
            genre: 音樂風格
            
        Returns:
            RhythmPattern: 節奏型態
        """
        config = self.get_style_config(genre)
        return config["rhythm_patterns"][0]  # 暫時只返回第一個節奏型態
    
    def get_chord_progression(self, genre: Genre) -> List[str]:
        """獲取指定風格的和弦進行
        
        Args:
            genre: 音樂風格
            
        Returns:
            List[str]: 和弦進行
        """
        config = self.get_style_config(genre)
        return config["chord_progressions"][0]  # 暫時只返回第一個和弦進行
    
    def get_tempo_range(self, genre: Genre) -> Tuple[int, int]:
        """獲取指定風格的速度範圍
        
        Args:
            genre: 音樂風格
            
        Returns:
            Tuple[int, int]: (最小速度, 最大速度)
        """
        config = self.get_style_config(genre)
        return config["tempo_range"]
    
    def get_complexity_weights(self, genre: Genre) -> Dict[str, float]:
        """獲取指定風格的複雜度權重
        
        Args:
            genre: 音樂風格
            
        Returns:
            Dict[str, float]: 複雜度權重
        """
        config = self.get_style_config(genre)
        return config["complexity_weights"] 