"""和聲理論模塊

處理和弦進行和調式相關的邏輯
"""

from typing import Dict, List, Tuple
from ...core.parameters import MusicParameters

class Scale:
    """音階類"""
    
    MAJOR_INTERVALS = [0, 2, 4, 5, 7, 9, 11]  # 大調音階音程
    MINOR_INTERVALS = [0, 2, 3, 5, 7, 8, 10]  # 小調音階音程
    
    def __init__(self, root: int, is_major: bool = True):
        """初始化音階
        
        Args:
            root: 根音的MIDI音高
            is_major: 是否為大調
        """
        self.root = root
        self.is_major = is_major
        self.intervals = self.MAJOR_INTERVALS if is_major else self.MINOR_INTERVALS
        
    def get_scale_notes(self) -> List[int]:
        """獲取音階的所有音符
        
        Returns:
            音符列表（MIDI音高）
        """
        return [self.root + interval for interval in self.intervals]
    
    def get_chord(self, degree: int, seventh: bool = False) -> List[int]:
        """獲取指定級數的和弦
        
        Args:
            degree: 級數（1-7）
            seventh: 是否為七和弦
            
        Returns:
            和弦音符列表
        """
        if not 1 <= degree <= 7:
            raise ValueError("級數必須在1-7之間")
            
        # 獲取和弦的基本音
        scale_notes = self.get_scale_notes()
        root_idx = degree - 1
        third_idx = (root_idx + 2) % 7
        fifth_idx = (root_idx + 4) % 7
        
        chord = [
            scale_notes[root_idx],
            scale_notes[third_idx],
            scale_notes[fifth_idx]
        ]
        
        # 如果是七和弦，添加七音
        if seventh:
            seventh_idx = (root_idx + 6) % 7
            chord.append(scale_notes[seventh_idx])
            
        return chord

class HarmonyManager:
    """和聲管理器"""
    
    # 常用和弦進行
    COMMON_PROGRESSIONS = {
        "pop": [
            ["I", "V", "vi", "IV"],
            ["I", "vi", "IV", "V"],
            ["vi", "IV", "I", "V"]
        ],
        "jazz": [
            ["ii", "V", "I"],
            ["iii", "vi", "ii", "V"],
            ["I", "vi", "ii", "V"]
        ],
        "classical": [
            ["I", "IV", "V", "I"],
            ["I", "vi", "IV", "V"],
            ["I", "V", "vi", "iii"]
        ]
    }
    
    def __init__(self):
        """初始化和聲管理器"""
        self.scales = {}  # 緩存已創建的音階
        
    def get_progression(self, parameters: MusicParameters) -> List[str]:
        """根據參數獲取和弦進行
        
        Args:
            parameters: 音樂參數
            
        Returns:
            和弦進行列表
        """
        genre = parameters.genre.value if parameters.genre else "pop"
        progressions = self.COMMON_PROGRESSIONS.get(genre, self.COMMON_PROGRESSIONS["pop"])
        
        # 根據複雜度選擇和弦進行
        complexity = parameters.complexity if parameters.complexity is not None else 0.5
        progression_idx = int(complexity * (len(progressions) - 1))
        return progressions[progression_idx]
    
    def get_chord_notes(self, chord: str, key: int, is_major: bool = True) -> List[int]:
        """獲取和弦的具體音符
        
        Args:
            chord: 和弦符號（如 "I"、"vi" 等）
            key: 調式的根音
            is_major: 是否為大調
            
        Returns:
            和弦音符列表（MIDI音高）
        """
        # 獲取或創建音階
        scale_key = (key, is_major)
        if scale_key not in self.scales:
            self.scales[scale_key] = Scale(key, is_major)
        scale = self.scales[scale_key]
        
        # 解析和弦符號
        is_minor = chord.islower()
        degree = self._roman_to_int(chord.upper())
        
        # 獲取和弦音符
        return scale.get_chord(degree, seventh=False)  # 暫時不使用七和弦
    
    @staticmethod
    def _roman_to_int(roman: str) -> int:
        """將羅馬數字轉換為整數
        
        Args:
            roman: 羅馬數字字符串
            
        Returns:
            整數值
        """
        values = {
            'I': 1,
            'II': 2,
            'III': 3,
            'IV': 4,
            'V': 5,
            'VI': 6,
            'VII': 7
        }
        return values.get(roman, 1) 