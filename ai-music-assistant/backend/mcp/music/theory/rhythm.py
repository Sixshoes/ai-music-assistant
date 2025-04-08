"""節奏理論模塊

處理節奏型態和生成邏輯
"""

from typing import List, Dict, Optional
from enum import Enum
from ...core.parameters import MusicParameters

class NoteLength(Enum):
    """音符長度"""
    WHOLE = 4.0  # 全音符
    HALF = 2.0  # 二分音符
    QUARTER = 1.0  # 四分音符
    EIGHTH = 0.5  # 八分音符
    SIXTEENTH = 0.25  # 十六分音符
    
class RhythmPattern:
    """節奏型態"""
    def __init__(self, beats: List[Dict], time_signature: str = "4/4"):
        """初始化節奏型態
        
        Args:
            beats: 節拍列表，每個節拍包含開始時間、持續時間和強度
            time_signature: 拍號
        """
        self.beats = beats
        self.time_signature = time_signature
        
    @property
    def duration(self) -> float:
        """獲取總時長"""
        return sum(beat["duration"] for beat in self.beats)
    
    def get_beats(self) -> List[Dict]:
        """獲取節拍列表"""
        return self.beats.copy()

class RhythmGenerator:
    """節奏生成器"""
    
    # 基本節奏型態模板
    PATTERNS = {
        "straight": [
            {"start": 0.0, "duration": 1.0, "velocity": 100},
            {"start": 1.0, "duration": 1.0, "velocity": 80},
            {"start": 2.0, "duration": 1.0, "velocity": 90},
            {"start": 3.0, "duration": 1.0, "velocity": 80}
        ],
        "swing": [
            {"start": 0.0, "duration": 1.0, "velocity": 100},
            {"start": 1.0, "duration": 0.66, "velocity": 80},
            {"start": 2.0, "duration": 1.0, "velocity": 90},
            {"start": 3.0, "duration": 0.66, "velocity": 80}
        ],
        "waltz": [
            {"start": 0.0, "duration": 1.0, "velocity": 100},
            {"start": 1.0, "duration": 1.0, "velocity": 70},
            {"start": 2.0, "duration": 1.0, "velocity": 70}
        ]
    }
    
    def __init__(self):
        """初始化節奏生成器"""
        self.patterns = {
            name: RhythmPattern(pattern) 
            for name, pattern in self.PATTERNS.items()
        }
        
    def generate_pattern(self, parameters: MusicParameters) -> RhythmPattern:
        """生成節奏型態
        
        Args:
            parameters: 音樂參數
            
        Returns:
            節奏型態
        """
        # 根據風格選擇基本節奏型態
        if parameters.genre:
            if parameters.genre.value == "jazz":
                base_pattern = self.patterns["swing"]
            elif parameters.genre.value == "classical" and parameters.time_signature == "3/4":
                base_pattern = self.patterns["waltz"]
            else:
                base_pattern = self.patterns["straight"]
        else:
            base_pattern = self.patterns["straight"]
            
        # 根據複雜度調整節奏
        pattern = self._adjust_complexity(
            base_pattern,
            parameters.complexity if parameters.complexity is not None else 0.5
        )
        
        return pattern
    
    def _adjust_complexity(self, pattern: RhythmPattern, complexity: float) -> RhythmPattern:
        """調整節奏複雜度
        
        Args:
            pattern: 基本節奏型態
            complexity: 複雜度（0-1）
            
        Returns:
            調整後的節奏型態
        """
        beats = pattern.get_beats()
        
        if complexity > 0.7:
            # 添加切分音
            new_beats = []
            for beat in beats:
                if beat["velocity"] > 80:  # 只在強拍上添加切分
                    # 將一個節拍分成兩個
                    new_beats.extend([
                        {
                            "start": beat["start"],
                            "duration": beat["duration"] * 0.6,
                            "velocity": beat["velocity"]
                        },
                        {
                            "start": beat["start"] + beat["duration"] * 0.6,
                            "duration": beat["duration"] * 0.4,
                            "velocity": beat["velocity"] - 20
                        }
                    ])
                else:
                    new_beats.append(beat)
            beats = new_beats
            
        elif complexity < 0.3:
            # 簡化節奏
            beats = [beat for beat in beats if beat["velocity"] > 70]
            
        return RhythmPattern(beats, pattern.time_signature)
    
    def get_drum_pattern(self, pattern: RhythmPattern) -> Dict[str, List[Dict]]:
        """獲取鼓組節奏型態
        
        Args:
            pattern: 基本節奏型態
            
        Returns:
            鼓組各部分的節奏型態
        """
        drum_pattern = {
            "kick": [],    # 低音鼓
            "snare": [],   # 小鼓
            "hihat": []    # 踩鑔
        }
        
        for beat in pattern.get_beats():
            # 低音鼓在強拍上
            if beat["velocity"] > 90:
                drum_pattern["kick"].append(beat.copy())
                
            # 小鼓在弱拍上
            if beat["velocity"] <= 90:
                drum_pattern["snare"].append(beat.copy())
                
            # 踩鑔保持穩定的八分音符節奏
            drum_pattern["hihat"].extend([
                {
                    "start": beat["start"],
                    "duration": 0.5,
                    "velocity": 70
                },
                {
                    "start": beat["start"] + 0.5,
                    "duration": 0.5,
                    "velocity": 60
                }
            ])
            
        return drum_pattern 