"""和聲優化模組

負責分析和優化音樂的和聲結構，確保音樂理論上的合理性和美感
"""

import logging
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Set
from enum import Enum
from dataclasses import dataclass
import random

from ...mcp.mcp_schema import MusicParameters, Note

logger = logging.getLogger(__name__)


class ChordType(Enum):
    """和弦類型"""
    MAJOR = "major"  # 大三和弦
    MINOR = "minor"  # 小三和弦
    DIMINISHED = "diminished"  # 減三和弦
    AUGMENTED = "augmented"  # 增三和弦
    DOMINANT7 = "dominant7"  # 屬七和弦
    MAJOR7 = "major7"  # 大七和弦
    MINOR7 = "minor7"  # 小七和弦
    HALF_DIMINISHED7 = "half_diminished7"  # 半減七和弦
    DIMINISHED7 = "diminished7"  # 減減七和弦
    SUSPENDED4 = "sus4"  # 掛四和弦
    SUSPENDED2 = "sus2"  # 掛二和弦


@dataclass
class Chord:
    """和弦資料結構"""
    root: int  # 根音 (MIDI pitch，C4=60)
    chord_type: ChordType  # 和弦類型
    inversion: int = 0  # 轉位 (0=原位, 1=第一轉位, 等)
    duration: float = 1.0  # 和弦持續時間
    start_time: float = 0.0  # 和弦開始時間
    
    @property
    def notes(self) -> List[int]:
        """獲取和弦中的音符
        
        Returns:
            List[int]: 和弦中的音符 (MIDI pitch)
        """
        intervals = []
        
        if self.chord_type == ChordType.MAJOR:
            intervals = [0, 4, 7]  # 根音, 大三度, 純五度
        elif self.chord_type == ChordType.MINOR:
            intervals = [0, 3, 7]  # 根音, 小三度, 純五度
        elif self.chord_type == ChordType.DIMINISHED:
            intervals = [0, 3, 6]  # 根音, 小三度, 減五度
        elif self.chord_type == ChordType.AUGMENTED:
            intervals = [0, 4, 8]  # 根音, 大三度, 增五度
        elif self.chord_type == ChordType.DOMINANT7:
            intervals = [0, 4, 7, 10]  # 根音, 大三度, 純五度, 小七度
        elif self.chord_type == ChordType.MAJOR7:
            intervals = [0, 4, 7, 11]  # 根音, 大三度, 純五度, 大七度
        elif self.chord_type == ChordType.MINOR7:
            intervals = [0, 3, 7, 10]  # 根音, 小三度, 純五度, 小七度
        elif self.chord_type == ChordType.HALF_DIMINISHED7:
            intervals = [0, 3, 6, 10]  # 根音, 小三度, 減五度, 小七度
        elif self.chord_type == ChordType.DIMINISHED7:
            intervals = [0, 3, 6, 9]  # 根音, 小三度, 減五度, 減七度
        elif self.chord_type == ChordType.SUSPENDED4:
            intervals = [0, 5, 7]  # 根音, 純四度, 純五度
        elif self.chord_type == ChordType.SUSPENDED2:
            intervals = [0, 2, 7]  # 根音, 大二度, 純五度
        
        # 應用轉位
        if self.inversion > 0 and self.inversion < len(intervals):
            intervals = intervals[self.inversion:] + [i + 12 for i in intervals[:self.inversion]]
        
        return [self.root + i for i in intervals]


class Scale(Enum):
    """音階類型"""
    MAJOR = "major"  # 大調
    MINOR = "minor"  # 小調
    HARMONIC_MINOR = "harmonic_minor"  # 和聲小調
    MELODIC_MINOR = "melodic_minor"  # 旋律小調
    DORIAN = "dorian"  # 多利安調式
    PHRYGIAN = "phrygian"  # 弗里幾亞調式
    LYDIAN = "lydian"  # 利底亞調式
    MIXOLYDIAN = "mixolydian"  # 混合利底亞調式
    LOCRIAN = "locrian"  # 洛克里安調式
    PENTATONIC_MAJOR = "pentatonic_major"  # 大調五聲音階
    PENTATONIC_MINOR = "pentatonic_minor"  # 小調五聲音階
    BLUES = "blues"  # 藍調音階


class KeySignature:
    """調號定義"""
    
    def __init__(self, root: int, scale: Scale):
        """初始化調號
        
        Args:
            root: 調號的根音 (MIDI pitch，C4=60)
            scale: 音階類型
        """
        self.root = root
        self.scale = scale
        
        # 計算調號中的音符
        self.scale_notes = self._calculate_scale_notes()
        
        # 計算調號中的和弦級數
        self.chords = self._calculate_chords()
    
    def _calculate_scale_notes(self) -> List[int]:
        """計算調號中的音符
        
        Returns:
            List[int]: 調號中的音符 (音程)
        """
        scale_intervals = {
            Scale.MAJOR: [0, 2, 4, 5, 7, 9, 11],  # 全全半全全全半
            Scale.MINOR: [0, 2, 3, 5, 7, 8, 10],  # 全半全全半全全
            Scale.HARMONIC_MINOR: [0, 2, 3, 5, 7, 8, 11],  # 全半全全半增半
            Scale.MELODIC_MINOR: [0, 2, 3, 5, 7, 9, 11],  # 全半全全全全半 (上行)
            Scale.DORIAN: [0, 2, 3, 5, 7, 9, 10],  # 全半全全全半全
            Scale.PHRYGIAN: [0, 1, 3, 5, 7, 8, 10],  # 半全全全半全全
            Scale.LYDIAN: [0, 2, 4, 6, 7, 9, 11],  # 全全全半全全半
            Scale.MIXOLYDIAN: [0, 2, 4, 5, 7, 9, 10],  # 全全半全全半全
            Scale.LOCRIAN: [0, 1, 3, 5, 6, 8, 10],  # 半全全半全全全
            Scale.PENTATONIC_MAJOR: [0, 2, 4, 7, 9],  # 大調五聲音階
            Scale.PENTATONIC_MINOR: [0, 3, 5, 7, 10],  # 小調五聲音階
            Scale.BLUES: [0, 3, 5, 6, 7, 10]  # 藍調音階
        }
        
        return [(self.root % 12) + interval for interval in scale_intervals[self.scale]]
    
    def _calculate_chords(self) -> Dict[int, Chord]:
        """計算調號中的和弦級數
        
        Returns:
            Dict[int, Chord]: 和弦級數 (1-7)
        """
        chords = {}
        
        if self.scale == Scale.MAJOR:
            # 大調的和弦級數: I(大), ii(小), iii(小), IV(大), V(大), vi(小), vii°(減)
            chord_types = [
                ChordType.MAJOR,  # I
                ChordType.MINOR,  # ii
                ChordType.MINOR,  # iii
                ChordType.MAJOR,  # IV
                ChordType.MAJOR,  # V
                ChordType.MINOR,  # vi
                ChordType.DIMINISHED  # vii°
            ]
        elif self.scale in [Scale.MINOR, Scale.HARMONIC_MINOR]:
            # 和聲小調的和弦級數: i(小), ii°(減), III+(增), iv(小), V(大), VI(大), vii°(減)
            chord_types = [
                ChordType.MINOR,  # i
                ChordType.DIMINISHED,  # ii°
                ChordType.MAJOR,  # III+
                ChordType.MINOR,  # iv
                ChordType.MAJOR,  # V (和聲小調)
                ChordType.MAJOR,  # VI
                ChordType.DIMINISHED  # vii°
            ]
        else:
            # 其他調式的和弦級數 (簡化)
            chord_types = [ChordType.MAJOR] * 7
        
        # 創建和弦
        for i, interval in enumerate(range(0, 12, 2)[:7]):
            root_note = self.root + interval
            chords[i + 1] = Chord(root=root_note, chord_type=chord_types[i])
        
        return chords
    
    def is_in_key(self, note: int) -> bool:
        """檢查音符是否在調內
        
        Args:
            note: 音符 (MIDI pitch)
            
        Returns:
            bool: 是否在調內
        """
        return (note % 12) in self.scale_notes
    
    def get_nearest_scale_note(self, note: int) -> int:
        """獲取最接近的調內音符
        
        Args:
            note: 音符 (MIDI pitch)
            
        Returns:
            int: 最接近的調內音符
        """
        note_class = note % 12
        octave = note // 12
        
        if note_class in self.scale_notes:
            return note
        
        # 尋找最接近的調內音
        distances = [(abs(note_class - sn), sn) for sn in self.scale_notes]
        distances.sort()
        
        return (octave * 12) + distances[0][1]


class HarmonyOptimizer:
    """和聲優化器
    
    負責分析和優化音樂的和聲結構
    """
    
    def __init__(self):
        """初始化和聲優化器"""
        self.key_signature = None
        
        logger.info("和聲優化器初始化完成")
    
    def set_key_signature(self, root: int, scale: Scale):
        """設置調號
        
        Args:
            root: 調號的根音 (MIDI pitch)
            scale: 音階類型
        """
        self.key_signature = KeySignature(root, scale)
        logger.info(f"設置調號: 根音={root}, 音階={scale.value}")
    
    def analyze_melody(self, notes: List[Note]) -> Dict[str, Any]:
        """分析旋律
        
        Args:
            notes: 旋律音符
            
        Returns:
            Dict[str, Any]: 分析結果
        """
        if not notes:
            return {"error": "空旋律"}
        
        logger.info(f"分析旋律，音符數量: {len(notes)}")
        
        # 如果尚未設置調號，嘗試檢測調號
        if self.key_signature is None:
            detected_key = self._detect_key(notes)
            self.set_key_signature(detected_key["root"], detected_key["scale"])
        
        # 分析音符分佈
        pitches = [note.pitch for note in notes]
        
        # 計算調內和調外音符
        in_key_notes = [p for p in pitches if self.key_signature.is_in_key(p)]
        out_of_key_notes = [p for p in pitches if not self.key_signature.is_in_key(p)]
        
        # 計算音域
        range_min = min(pitches) if pitches else 0
        range_max = max(pitches) if pitches else 0
        
        # 節奏分析
        durations = [note.duration for note in notes]
        mean_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            "total_notes": len(notes),
            "in_key_notes": len(in_key_notes),
            "out_of_key_notes": len(out_of_key_notes),
            "key_adherence": len(in_key_notes) / len(notes) if notes else 0,
            "pitch_range": (range_min, range_max),
            "pitch_range_span": range_max - range_min,
            "mean_duration": mean_duration,
            "key_signature": {
                "root": self.key_signature.root,
                "scale": self.key_signature.scale.value
            }
        }
    
    def _detect_key(self, notes: List[Note]) -> Dict[str, Any]:
        """檢測旋律的可能調號
        
        Args:
            notes: 旋律音符
            
        Returns:
            Dict[str, Any]: 檢測到的調號
        """
        logger.info("檢測旋律的調號")
        
        # 簡單的檢測方法：統計音符出現頻率，匹配大調或小調模式
        pitch_classes = [note.pitch % 12 for note in notes]
        pitch_counts = {i: pitch_classes.count(i) for i in range(12)}
        
        # 檢查與各個大調和小調的匹配度
        best_score = -1
        best_key = {"root": 0, "scale": Scale.MAJOR}
        
        for root in range(12):
            # 檢查大調
            major_key = KeySignature(root, Scale.MAJOR)
            major_score = sum(pitch_counts.get(pc, 0) for pc in major_key.scale_notes)
            
            # 檢查小調
            minor_key = KeySignature(root, Scale.MINOR)
            minor_score = sum(pitch_counts.get(pc, 0) for pc in minor_key.scale_notes)
            
            if major_score > best_score:
                best_score = major_score
                best_key = {"root": root, "scale": Scale.MAJOR}
            
            if minor_score > best_score:
                best_score = minor_score
                best_key = {"root": root, "scale": Scale.MINOR}
        
        logger.info(f"檢測到的調號: 根音={best_key['root']}, 音階={best_key['scale'].value}")
        return best_key
    
    def generate_chord_progression(self, 
                                 length: int = 4, 
                                 style: str = "basic") -> List[Chord]:
        """生成和弦進行
        
        Args:
            length: 和弦數量
            style: 和弦風格 ('basic', 'jazz', 'pop', 等)
            
        Returns:
            List[Chord]: 和弦列表
        """
        if self.key_signature is None:
            self.set_key_signature(60, Scale.MAJOR)  # 默認 C 大調
        
        logger.info(f"生成和弦進行，長度: {length}, 風格: {style}")
        
        if style == "basic":
            # 基本的和弦進行: I-IV-V-I
            progression = [1, 4, 5, 1]
        elif style == "pop":
            # 流行音樂常用進行: I-V-vi-IV
            progression = [1, 5, 6, 4]
        elif style == "jazz":
            # 爵士風格: ii-V-I-VI
            progression = [2, 5, 1, 6]
        else:
            # 隨機進行
            available_degrees = list(self.key_signature.chords.keys())
            progression = [random.choice(available_degrees) for _ in range(length)]
        
        # 重複到指定長度
        while len(progression) < length:
            progression.extend(progression)
        progression = progression[:length]
        
        # 創建和弦列表
        chords = []
        for i, degree in enumerate(progression):
            chord = self.key_signature.chords.get(degree)
            if chord:
                # 複製和弦並設置時間
                new_chord = Chord(
                    root=chord.root,
                    chord_type=chord.chord_type,
                    inversion=0,
                    duration=1.0,
                    start_time=float(i)
                )
                chords.append(new_chord)
        
        return chords
    
    def harmonize_melody(self, 
                        notes: List[Note], 
                        style: str = "basic") -> List[Chord]:
        """為旋律創建和聲
        
        Args:
            notes: 旋律音符
            style: 和聲風格
            
        Returns:
            List[Chord]: 和弦列表
        """
        if not notes:
            return []
        
        logger.info(f"為旋律創建和聲，音符數量: {len(notes)}, 風格: {style}")
        
        # 分析旋律
        analysis = self.analyze_melody(notes)
        
        # 確定和弦變化點 (簡單策略：每小節一個和弦)
        max_time = max([n.start_time + n.duration for n in notes])
        measures = int(max_time / 4) + 1  # 假設4/4拍
        
        # 生成和弦進行
        chords = self.generate_chord_progression(measures, style)
        
        # 將和弦與旋律對齊
        aligned_chords = []
        for i, chord in enumerate(chords):
            chord.start_time = i * 4.0  # 每小節一個和弦
            chord.duration = 4.0
            aligned_chords.append(chord)
        
        return aligned_chords
    
    def optimize_melody(self, 
                      notes: List[Note], 
                      strictness: float = 0.5) -> List[Note]:
        """優化旋律以更好地符合和聲
        
        Args:
            notes: 旋律音符
            strictness: 嚴格程度 (0.0-1.0)，越高越嚴格遵循調內音
            
        Returns:
            List[Note]: 優化後的旋律
        """
        if not notes or self.key_signature is None:
            return notes
        
        logger.info(f"優化旋律，音符數量: {len(notes)}, 嚴格度: {strictness}")
        
        optimized_notes = []
        
        for note in notes:
            # 檢查是否需要修正
            if not self.key_signature.is_in_key(note.pitch):
                # 計算修正的機率
                if random.random() < strictness:
                    # 獲取最近的調內音
                    new_pitch = self.key_signature.get_nearest_scale_note(note.pitch)
                    
                    # 創建新音符
                    new_note = Note(
                        pitch=new_pitch,
                        start_time=note.start_time,
                        duration=note.duration,
                        velocity=note.velocity
                    )
                    optimized_notes.append(new_note)
                else:
                    # 保持原樣
                    optimized_notes.append(note)
            else:
                # 在調內，保持原樣
                optimized_notes.append(note)
        
        return optimized_notes
    
    def optimize_chords(self, 
                       chords: List[Chord], 
                       complexity: float = 0.5,
                       melody_notes: Optional[List[Note]] = None) -> List[Chord]:
        """優化和弦進行
        
        Args:
            chords: 和弦列表
            complexity: 複雜度 (0.0-1.0)
            melody_notes: 可選的旋律音符，用於確保和弦與旋律協調
            
        Returns:
            List[Chord]: 優化後的和弦
        """
        if not chords:
            return chords
        
        logger.info(f"優化和弦進行，和弦數量: {len(chords)}, 複雜度: {complexity}")
        
        optimized_chords = []
        
        for i, chord in enumerate(chords):
            # 基於複雜度決定是否增加七和弦
            if random.random() < complexity:
                # 轉換為七和弦
                new_type = chord.chord_type
                
                if chord.chord_type == ChordType.MAJOR:
                    new_type = ChordType.MAJOR7
                elif chord.chord_type == ChordType.MINOR:
                    new_type = ChordType.MINOR7
                
                # 創建新和弦
                new_chord = Chord(
                    root=chord.root,
                    chord_type=new_type,
                    inversion=chord.inversion,
                    duration=chord.duration,
                    start_time=chord.start_time
                )
                optimized_chords.append(new_chord)
            else:
                # 保持原樣
                optimized_chords.append(chord)
        
        return optimized_chords
    
    def chords_to_notes(self, 
                       chords: List[Chord], 
                       style: str = "basic") -> List[Note]:
        """將和弦轉換為音符序列
        
        Args:
            chords: 和弦列表
            style: 伴奏風格
            
        Returns:
            List[Note]: 音符列表
        """
        if not chords:
            return []
        
        logger.info(f"將和弦轉換為音符，和弦數量: {len(chords)}, 風格: {style}")
        
        notes = []
        
        for chord in chords:
            chord_notes = chord.notes
            
            if style == "basic":
                # 基本的塊狀和弦
                for pitch in chord_notes:
                    note = Note(
                        pitch=pitch,
                        start_time=chord.start_time,
                        duration=chord.duration,
                        velocity=70
                    )
                    notes.append(note)
            
            elif style == "arpeggio":
                # 琶音
                division = chord.duration / len(chord_notes)
                for i, pitch in enumerate(chord_notes):
                    note = Note(
                        pitch=pitch,
                        start_time=chord.start_time + i * division,
                        duration=division * 0.9,
                        velocity=70
                    )
                    notes.append(note)
            
            elif style == "waltz":
                # 華爾滋風格 (3/4)
                bass_note = chord_notes[0] - 12  # 低八度的根音
                
                # 低音
                notes.append(Note(
                    pitch=bass_note,
                    start_time=chord.start_time,
                    duration=chord.duration / 3,
                    velocity=80
                ))
                
                # 和弦其餘音符
                for i in range(2):
                    for pitch in chord_notes[1:]:
                        notes.append(Note(
                            pitch=pitch,
                            start_time=chord.start_time + (i + 1) * chord.duration / 3,
                            duration=chord.duration / 3 * 0.8,
                            velocity=70
                        ))
            
            else:
                # 默認簡單的和弦
                for pitch in chord_notes:
                    note = Note(
                        pitch=pitch,
                        start_time=chord.start_time,
                        duration=chord.duration,
                        velocity=70
                    )
                    notes.append(note)
        
        return notes


# 使用示例
if __name__ == "__main__":
    # 配置日誌
    logging.basicConfig(level=logging.INFO)
    
    # 創建和聲優化器
    optimizer = HarmonyOptimizer()
    
    # 設置調號 (C 大調)
    optimizer.set_key_signature(60, Scale.MAJOR)
    
    # 創建一些測試音符
    test_notes = [
        Note(pitch=60, start_time=0.0, duration=1.0, velocity=80),  # C4
        Note(pitch=62, start_time=1.0, duration=1.0, velocity=80),  # D4
        Note(pitch=64, start_time=2.0, duration=1.0, velocity=80),  # E4
        Note(pitch=65, start_time=3.0, duration=1.0, velocity=80),  # F4
        Note(pitch=67, start_time=4.0, duration=1.0, velocity=80),  # G4
        Note(pitch=69, start_time=5.0, duration=1.0, velocity=80),  # A4
        Note(pitch=71, start_time=6.0, duration=1.0, velocity=80),  # B4
        Note(pitch=72, start_time=7.0, duration=1.0, velocity=80),  # C5
    ]
    
    # 分析旋律
    analysis = optimizer.analyze_melody(test_notes)
    print(f"旋律分析結果: {analysis}")
    
    # 生成和弦進行
    chords = optimizer.generate_chord_progression(4, "pop")
    print(f"生成的和弦進行: {[(c.root, c.chord_type.value) for c in chords]}")
    
    # 為旋律創建和聲
    harmony_chords = optimizer.harmonize_melody(test_notes, "basic")
    print(f"創建的和聲: {[(c.root, c.chord_type.value) for c in harmony_chords]}")
    
    # 將和弦轉換為音符
    chord_notes = optimizer.chords_to_notes(harmony_chords, "arpeggio")
    print(f"生成的伴奏音符數量: {len(chord_notes)}") 