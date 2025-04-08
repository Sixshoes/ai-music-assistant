"""風格管理器

管理不同音樂風格的配置和參數
"""

import logging
from enum import Enum
from typing import Dict, List, Tuple, Any, Optional
from ..mcp_schema import Genre, InstrumentType

logger = logging.getLogger(__name__)

class PlayingStyle(str, Enum):
    """演奏風格枚舉"""
    NORMAL = "normal"
    STACCATO = "staccato"  # 斷奏
    LEGATO = "legato"  # 連奏
    TREMOLO = "tremolo"  # 顫音
    ARPEGGIO = "arpeggio"  # 琶音

class RhythmPattern(Enum):
    """節奏型態枚舉"""
    STRAIGHT = "straight"  # 平直
    SWING = "swing"        # 搖擺
    SHUFFLE = "shuffle"    # 切分
    SYNCOPATED = "syncopated"  # 切分音
    WALTZ = "waltz"        # 華爾茲
    LATIN = "latin"        # 拉丁
    COMPLEX = "complex"    # 複雜

class StyleManager:
    """風格管理器"""
    
    def __init__(self):
        """初始化風格管理器"""
        # 動態風格配置 - 不再使用硬編碼預設
        self.style_configs = {}
        
        # 用於LLM風格生成的基本空模板
        self.style_template = {
            "chord_progressions": [],
            "tempo_range": (80, 140),
            "instruments": {
                "lead": [],
                "pad": [],
                "bass": [],
                "drums": []
            },
            "patterns": {}
        }
    
    def get_style_config(self, genre: Genre) -> Dict[str, Any]:
        """獲取風格配置
        
        Args:
            genre: 風格類型
            
        Returns:
            風格配置字典
        """
        # 風格配置由LLM動態生成，不再使用硬編碼預設
        # 返回一個空模板，具體內容將由LLM填充
        genre_str = str(genre).lower()
        return self.style_template.copy()
    
    def get_chord_progression(self, genre: Genre) -> List[str]:
        """獲取和弦進行
        
        Args:
            genre: 風格類型
            
        Returns:
            和弦進行列表
        """
        # 由LLM動態生成和弦進行
        # 這裡只返回一個簡單的默認值
        return ["C", "G", "Am", "F"]
    
    def get_tempo_range(self, genre: Genre) -> Tuple[int, int]:
        """獲取速度範圍
        
        Args:
            genre: 風格類型
            
        Returns:
            速度範圍元組
        """
        # 返回默認範圍，具體內容由LLM調整
        return (80, 140)
    
    def get_instruments(self, genre: Genre) -> Dict[str, List[InstrumentType]]:
        """獲取樂器配置
        
        Args:
            genre: 風格類型
            
        Returns:
            樂器配置字典
        """
        # 由LLM動態生成樂器配置
        # 返回簡單的默認值
        return {
            "lead": [InstrumentType.PIANO],
            "pad": [InstrumentType.SYNTH],
            "bass": [InstrumentType.BASS],
            "drums": [InstrumentType.DRUMS]
        }
    
    def get_default_instrument(self, genre: Genre, role: str) -> InstrumentType:
        """獲取指定角色的默認樂器
        
        Args:
            genre: 風格類型
            role: 樂器角色
            
        Returns:
            樂器類型
        """
        # 簡單的默認值映射
        default_map = {
            "lead": InstrumentType.PIANO,
            "pad": InstrumentType.SYNTH,
            "bass": InstrumentType.BASS,
            "drums": InstrumentType.DRUMS
        }
        return default_map.get(role, InstrumentType.PIANO) 