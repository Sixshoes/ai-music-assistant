#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
音樂理論驗證模組

此模組提供音樂理論規則驗證功能，用於檢查和分析音樂作品中的和聲、節奏和結構是否符合音樂理論規則。
"""

import json
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
import numpy as np
from enum import Enum

# 設置日誌記錄
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('theory_validator')

# 定義常量
MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]  # 大調音階的半音間隔
MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]  # 小調音階的半音間隔

# 定義和弦類型
class ChordType(Enum):
    MAJOR = "major"
    MINOR = "minor"
    DIMINISHED = "diminished"
    AUGMENTED = "augmented"
    DOMINANT_SEVENTH = "dominant_seventh"
    MAJOR_SEVENTH = "major_seventh"
    MINOR_SEVENTH = "minor_seventh"
    HALF_DIMINISHED = "half_diminished"
    DIMINISHED_SEVENTH = "diminished_seventh"
    SUSPENDED_FOURTH = "suspended_fourth"
    SUSPENDED_SECOND = "suspended_second"

# 定義調性類型
class KeyType(Enum):
    MAJOR = "major"
    MINOR = "minor"

# 定義音符類
class Note:
    def __init__(self, pitch: int, duration: float, velocity: int = 64):
        """
        初始化音符
        
        Args:
            pitch: MIDI 音高（0-127）
            duration: 音符持續時間（以拍為單位）
            velocity: MIDI 力度（0-127）
        """
        self.pitch = pitch
        self.duration = duration
        self.velocity = velocity
    
    @property
    def pitch_class(self) -> int:
        """返回音符的音高類別（0-11）"""
        return self.pitch % 12
    
    def transpose(self, semitones: int) -> 'Note':
        """移調音符"""
        return Note(self.pitch + semitones, self.duration, self.velocity)
    
    def __repr__(self) -> str:
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = self.pitch // 12 - 1
        note_name = note_names[self.pitch_class]
        return f"{note_name}{octave}({self.duration})"

# 定義和弦類
class Chord:
    def __init__(self, root: int, chord_type: ChordType, notes: Optional[List[Note]] = None):
        """
        初始化和弦
        
        Args:
            root: 根音的音高類別（0-11，其中0代表C）
            chord_type: 和弦類型
            notes: 和弦中包含的音符
        """
        self.root = root
        self.chord_type = chord_type
        self.notes = notes or []
    
    @property
    def pitches(self) -> List[int]:
        """返回和弦中所有音符的音高類別"""
        return [note.pitch_class for note in self.notes]
    
    def is_valid(self) -> bool:
        """檢查和弦是否有效（包含至少三個音符）"""
        return len(set(self.pitches)) >= 3
    
    def __repr__(self) -> str:
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        root_name = note_names[self.root]
        
        chord_symbols = {
            ChordType.MAJOR: "",
            ChordType.MINOR: "m",
            ChordType.DIMINISHED: "dim",
            ChordType.AUGMENTED: "aug",
            ChordType.DOMINANT_SEVENTH: "7",
            ChordType.MAJOR_SEVENTH: "maj7",
            ChordType.MINOR_SEVENTH: "m7",
            ChordType.HALF_DIMINISHED: "ø",
            ChordType.DIMINISHED_SEVENTH: "°7",
            ChordType.SUSPENDED_FOURTH: "sus4",
            ChordType.SUSPENDED_SECOND: "sus2",
        }
        
        return f"{root_name}{chord_symbols[self.chord_type]}"

# 理論驗證器類
class TheoryValidator:
    def __init__(self):
        """初始化理論驗證器"""
        logger.info("初始化音樂理論驗證器")
    
    def analyze_key(self, notes: List[Note]) -> Tuple[int, KeyType]:
        """
        分析一系列音符的調性
        
        Args:
            notes: 要分析的音符列表
            
        Returns:
            調性根音和調性類型
        """
        # 統計每個音高類別的出現次數
        pitch_counts = np.zeros(12)
        for note in notes:
            pitch_counts[note.pitch_class] += note.duration
        
        # 嘗試每個可能的調性，看哪個最匹配
        best_correlation = -1
        best_key = (0, KeyType.MAJOR)
        
        # 檢查所有可能的大調和小調
        for root in range(12):
            # 建立調性模板
            major_template = np.zeros(12)
            for interval in MAJOR_SCALE:
                major_template[(root + interval) % 12] = 1
            
            minor_template = np.zeros(12)
            for interval in MINOR_SCALE:
                minor_template[(root + interval) % 12] = 1
            
            # 計算相關性
            major_correlation = np.corrcoef(pitch_counts, major_template)[0, 1]
            minor_correlation = np.corrcoef(pitch_counts, minor_template)[0, 1]
            
            # 更新最佳匹配
            if major_correlation > best_correlation:
                best_correlation = major_correlation
                best_key = (root, KeyType.MAJOR)
            
            if minor_correlation > best_correlation:
                best_correlation = minor_correlation
                best_key = (root, KeyType.MINOR)
        
        return best_key
    
    def identify_chords(self, notes: List[Note], segment_size: float = 1.0) -> List[Chord]:
        """
        識別樂曲中的和弦
        
        Args:
            notes: 要分析的音符列表
            segment_size: 分段大小（以拍為單位）
            
        Returns:
            識別出的和弦列表
        """
        # 按時間分段
        max_time = max(note.duration for note in notes)
        segments = []
        
        for i in range(int(max_time / segment_size) + 1):
            start_time = i * segment_size
            end_time = (i + 1) * segment_size
            segment_notes = [note for note in notes if start_time <= note.duration < end_time]
            segments.append(segment_notes)
        
        chords = []
        
        # 分析每個段落中的和弦
        for segment in segments:
            if not segment:
                continue
            
            # 統計音高類別
            pitch_classes = [note.pitch_class for note in segment]
            pitch_counts = {}
            
            for pc in pitch_classes:
                if pc in pitch_counts:
                    pitch_counts[pc] += 1
                else:
                    pitch_counts[pc] = 1
            
            # 找出最可能的根音
            root = max(pitch_counts, key=pitch_counts.get)
            
            # 檢查和弦類型
            chord_type = self._determine_chord_type(pitch_classes, root)
            
            chords.append(Chord(root, chord_type, segment))
        
        return chords
    
    def _determine_chord_type(self, pitches: List[int], root: int) -> ChordType:
        """
        根據音符和根音確定和弦類型
        
        Args:
            pitches: 音高類別列表
            root: 根音的音高類別
            
        Returns:
            和弦類型
        """
        # 標準化音高，相對於根音
        normalized_pitches = [(p - root) % 12 for p in pitches]
        unique_pitches = set(normalized_pitches)
        
        # 判斷和弦類型
        if 4 in unique_pitches and 7 in unique_pitches:
            if 10 in unique_pitches:
                return ChordType.DOMINANT_SEVENTH
            elif 11 in unique_pitches:
                return ChordType.MAJOR_SEVENTH
            else:
                return ChordType.MAJOR
        elif 3 in unique_pitches and 7 in unique_pitches:
            if 10 in unique_pitches:
                return ChordType.MINOR_SEVENTH
            else:
                return ChordType.MINOR
        elif 3 in unique_pitches and 6 in unique_pitches:
            if 9 in unique_pitches:
                return ChordType.HALF_DIMINISHED
            elif 9 in unique_pitches:
                return ChordType.DIMINISHED_SEVENTH
            else:
                return ChordType.DIMINISHED
        elif 4 in unique_pitches and 8 in unique_pitches:
            return ChordType.AUGMENTED
        elif 5 in unique_pitches and 7 in unique_pitches:
            return ChordType.SUSPENDED_FOURTH
        elif 2 in unique_pitches and 7 in unique_pitches:
            return ChordType.SUSPENDED_SECOND
        
        # 默認為大三和弦
        return ChordType.MAJOR
    
    def check_parallel_fifths(self, chords: List[Chord]) -> List[Tuple[int, int]]:
        """
        檢查平行五度
        
        Args:
            chords: 要檢查的和弦列表
            
        Returns:
            找到的平行五度位置列表（以和弦索引對表示）
        """
        parallel_fifths = []
        
        for i in range(len(chords) - 1):
            chord1 = chords[i]
            chord2 = chords[i + 1]
            
            # 對每個音符檢查是否有平行五度
            for note1 in chord1.notes:
                for note2 in chord1.notes:
                    if (note2.pitch - note1.pitch) % 12 == 7:  # 五度關係
                        # 在下一個和弦中查找這兩個音是否仍然保持五度關係且都移動了
                        for next_note1 in chord2.notes:
                            for next_note2 in chord2.notes:
                                if (next_note2.pitch - next_note1.pitch) % 12 == 7:
                                    if note1.pitch != next_note1.pitch and note2.pitch != next_note2.pitch:
                                        parallel_fifths.append((i, i + 1))
                                        break
        
        return parallel_fifths
    
    def analyze_melody(self, notes: List[Note]) -> Dict[str, Any]:
        """
        分析旋律特徵
        
        Args:
            notes: 要分析的音符列表
            
        Returns:
            旋律分析結果
        """
        if not notes:
            return {"error": "無音符可分析"}
        
        pitches = [note.pitch for note in notes]
        intervals = [pitches[i] - pitches[i-1] for i in range(1, len(pitches))]
        
        return {
            "note_count": len(notes),
            "pitch_range": max(pitches) - min(pitches),
            "average_pitch": sum(pitches) / len(pitches),
            "largest_interval": max(intervals, key=abs) if intervals else 0,
            "most_common_interval": max(set(intervals), key=intervals.count) if intervals else 0,
            "intervals": intervals
        }
    
    def validate(self, notes: List[Note]) -> Dict[str, Any]:
        """
        對音樂作品進行全面的理論驗證
        
        Args:
            notes: 作品中的音符列表
            
        Returns:
            包含分析結果和建議的字典
        """
        if not notes:
            return {"error": "無音符可分析"}
        
        # 執行各種分析
        key_root, key_type = self.analyze_key(notes)
        chords = self.identify_chords(notes)
        melody_analysis = self.analyze_melody(notes)
        parallel_fifths = self.check_parallel_fifths(chords)
        
        # 生成和弦進行
        chord_progression = [str(chord) for chord in chords]
        
        # 準備音樂理論反饋
        feedback = {
            "key": self._get_key_name(key_root, key_type),
            "chords": chord_progression,
            "chord_count": len(chords),
            "melody_analysis": melody_analysis,
            "issues": [],
            "suggestions": []
        }
        
        # 檢查平行五度
        if parallel_fifths:
            feedback["issues"].append({
                "type": "parallel_fifths",
                "message": f"在 {len(parallel_fifths)} 處發現平行五度",
                "locations": parallel_fifths
            })
            feedback["suggestions"].append("避免平行五度，可以使用反向運動")
        
        # 檢查旋律特徵
        if melody_analysis["pitch_range"] > 24:  # 超過兩個八度
            feedback["issues"].append({
                "type": "large_pitch_range",
                "message": "旋律的音高範圍過大",
                "details": f"音高範圍: {melody_analysis['pitch_range']} 半音"
            })
            feedback["suggestions"].append("考慮縮小旋律的音高範圍，使其更容易演奏")
        
        # 檢查和弦多樣性
        unique_chords = set(chord_progression)
        if len(unique_chords) < 4 and len(chords) > 8:
            feedback["issues"].append({
                "type": "limited_chord_variety",
                "message": "和弦變化有限",
                "details": f"僅使用了 {len(unique_chords)} 種不同的和弦"
            })
            feedback["suggestions"].append("嘗試引入更多種類的和弦以增加和聲變化")
        
        # 檢查和弦進行
        if len(chords) >= 2:
            feedback["suggestions"].append(self._suggest_chord_progression(chords, key_root, key_type))
        
        # 計算整體分數
        score = self._calculate_score(feedback)
        feedback["score"] = score
        
        return feedback
    
    def _get_key_name(self, root: int, key_type: KeyType) -> str:
        """返回調性的名稱"""
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        suffix = " Major" if key_type == KeyType.MAJOR else " Minor"
        return note_names[root] + suffix
    
    def _suggest_chord_progression(self, chords: List[Chord], key_root: int, key_type: KeyType) -> str:
        """基於當前和弦進行提出建議"""
        # 這裡可以實現更複雜的和弦進行建議算法
        # 簡單示例：建議使用常見的終止式
        if key_type == KeyType.MAJOR:
            return "考慮在樂曲結尾使用 V7-I 終止式以增強結束感"
        else:
            return "考慮在樂曲結尾使用 V7-i 或 V7-I 終止式以增強結束感"
    
    def _calculate_score(self, feedback: Dict[str, Any]) -> int:
        """根據分析結果計算整體分數"""
        # 基礎分數
        score = 80
        
        # 根據問題扣分
        score -= len(feedback["issues"]) * 5
        
        # 根據和弦多樣性加分
        unique_chords = set(feedback["chords"])
        if len(unique_chords) >= 7:
            score += 10
        elif len(unique_chords) >= 5:
            score += 5
        
        # 確保分數在0-100範圍內
        return max(0, min(100, score))

# 從 JSON 加載音符數據的輔助函數
def load_notes_from_json(json_data: str) -> List[Note]:
    """
    從 JSON 字符串加載音符數據
    
    Args:
        json_data: JSON 格式的音符數據
        
    Returns:
        音符列表
    """
    try:
        data = json.loads(json_data)
        notes = []
        
        for note_data in data.get("notes", []):
            pitch = note_data.get("pitch", 60)
            duration = note_data.get("duration", 1.0)
            velocity = note_data.get("velocity", 64)
            notes.append(Note(pitch, duration, velocity))
        
        return notes
    except Exception as e:
        logger.error(f"加載音符數據時出錯: {e}")
        return []

# 主函數用於測試
def main():
    """測試理論驗證器的功能"""
    # 創建一些測試音符
    notes = [
        Note(60, 1.0),  # C4
        Note(64, 1.0),  # E4
        Note(67, 1.0),  # G4
        Note(62, 1.0),  # D4
        Note(65, 1.0),  # F4
        Note(69, 1.0),  # A4
        Note(64, 1.0),  # E4
        Note(67, 1.0),  # G4
        Note(71, 1.0),  # B4
        Note(60, 1.0),  # C4
        Note(64, 1.0),  # E4
        Note(67, 1.0),  # G4
    ]
    
    # 創建理論驗證器實例
    validator = TheoryValidator()
    
    # 執行驗證
    results = validator.validate(notes)
    
    # 輸出結果
    print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main() 