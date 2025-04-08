"""和弦生成器模組

基於旋律生成合適的和弦進行
"""

import logging
import numpy as np
import os
import sys
from typing import List, Dict, Any, Optional, Tuple
from music21 import chord, note, stream, key, pitch

# 添加項目根目錄到 Python 路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
if project_root not in sys.path:
    sys.path.append(project_root)

from backend.mcp.mcp_schema import Note as MCPNote, MelodyInput

logger = logging.getLogger(__name__)

class ChordGenerator:
    """和弦生成器類別
    
    基於旋律自動生成和弦進行
    """
    
    def __init__(self):
        """初始化和弦生成器"""
        logger.info("初始化和弦生成器")
    
    def generate_chords(self, melody: MelodyInput, 
                        style: str = "pop",
                        complexity: int = 3) -> List[Dict[str, Any]]:
        """根據旋律生成和弦進行
        
        Args:
            melody: 輸入的旋律
            style: 音樂風格，影響和弦選擇
            complexity: 和弦複雜度，1-5
            
        Returns:
            和弦列表，每個和弦包含名稱、開始時間、持續時間等信息
        """
        try:
            # 檢測旋律的調性
            detected_key = self._detect_key(melody.notes)
            logger.info(f"檢測到的旋律調性: {detected_key}")
            
            # 分析旋律結構
            sections = self._analyze_melody_structure(melody.notes)
            
            # 根據調性和旋律分段生成和弦
            chord_progression = self._create_chord_progression(
                melody.notes, 
                detected_key,
                sections,
                style,
                complexity
            )
            
            logger.info(f"已為旋律生成和弦進行，共 {len(chord_progression)} 個和弦")
            return chord_progression
            
        except Exception as e:
            logger.error(f"和弦生成失敗: {str(e)}", exc_info=True)
            raise
    
    def _detect_key(self, melody_notes: List[MCPNote]) -> str:
        """從旋律檢測調性
        
        Args:
            melody_notes: 旋律中的音符列表
            
        Returns:
            檢測到的調性，例如 "C" 或 "Am"
        """
        try:
            # 轉換為 music21 音符
            notes_stream = stream.Stream()
            for note_obj in melody_notes:
                p = pitch.Pitch()
                p.midi = note_obj.pitch
                notes_stream.append(note.Note(p))
            
            # 檢測調性
            detected_key = notes_stream.analyze('key')
            
            # 格式化調性名稱
            key_name = detected_key.tonicPitchNameWithCase
            
            return key_name
        
        except Exception as e:
            logger.warning(f"調性檢測失敗，使用默認調性 C: {str(e)}")
            return "C"  # 默認返回 C 大調
    
    def _analyze_melody_structure(self, melody_notes: List[MCPNote]) -> List[Dict[str, Any]]:
        """分析旋律結構，識別不同段落
        
        Args:
            melody_notes: 旋律中的音符列表
            
        Returns:
            旋律段落列表，每個段落包含開始時間、結束時間、特徵等
        """
        # 簡單實現：按照固定時間間隔或休止符分段
        sections = []
        current_section_start = 0.0
        
        if not melody_notes:
            return sections
        
        # 排序音符，確保按時間順序
        sorted_notes = sorted(melody_notes, key=lambda n: n.start_time)
        
        # 分析音符間的間隔
        for i in range(1, len(sorted_notes)):
            prev_note = sorted_notes[i-1]
            curr_note = sorted_notes[i]
            
            # 檢測是否有明顯的間隔（可能是段落間的休止）
            gap = curr_note.start_time - (prev_note.start_time + prev_note.duration)
            
            if gap > 0.5:  # 如果間隔超過0.5秒，視為段落分界
                # 結束當前段落
                sections.append({
                    "start_time": current_section_start,
                    "end_time": prev_note.start_time + prev_note.duration,
                    "notes_count": i
                })
                
                # 開始新的段落
                current_section_start = curr_note.start_time
        
        # 添加最後一個段落
        last_note = sorted_notes[-1]
        sections.append({
            "start_time": current_section_start,
            "end_time": last_note.start_time + last_note.duration,
            "notes_count": len(sorted_notes) - len(sections)
        })
        
        return sections
    
    def _create_chord_progression(self, 
                                melody_notes: List[MCPNote],
                                detected_key: str,
                                sections: List[Dict[str, Any]],
                                style: str,
                                complexity: int) -> List[Dict[str, Any]]:
        """創建和弦進行
        
        Args:
            melody_notes: 旋律中的音符列表
            detected_key: 檢測到的調性
            sections: 旋律段落
            style: 音樂風格
            complexity: 和弦複雜度
            
        Returns:
            和弦進行，包含每個和弦的信息
        """
        # 常見和弦進行模式（按風格和調性）
        chord_patterns = {
            "pop": {
                "major": [
                    ["I", "V", "vi", "IV"],  # 經典流行進行
                    ["I", "IV", "V"],        # 簡單三和弦進行
                    ["I", "vi", "IV", "V"],  # 50年代進行
                    ["I", "V", "vi", "iii", "IV", "I", "IV", "V"]  # 擴展進行
                ],
                "minor": [
                    ["i", "VII", "VI", "V"],  # 自然小調進行
                    ["i", "iv", "VII", "III"],# 常見小調進行
                    ["i", "iv", "v"],         # 簡單小調三和弦進行
                    ["i", "VI", "III", "VII"] # 另一種常見小調進行
                ]
            },
            "jazz": {
                "major": [
                    ["I", "vi", "ii", "V"],       # 2-5-1進行
                    ["I", "vi", "ii7", "V7"],     # 帶7和弦的2-5-1
                    ["Imaj7", "vi7", "ii7", "V7"] # 更豐富的爵士進行
                ],
                "minor": [
                    ["i", "iv", "V"],            # 小調基本進行
                    ["i7", "iv7", "V7"],         # 帶7和弦
                    ["im7", "ivm7", "V7alt"]     # 更豐富的爵士小調進行
                ]
            }
        }
        
        # 如果找不到指定風格，使用流行樂
        if style not in chord_patterns:
            style = "pop"
        
        # 判斷是大調還是小調
        is_minor = detected_key.islower() or detected_key.endswith('m')
        mode = "minor" if is_minor else "major"
        
        # 根據複雜度選擇進行
        pattern_idx = min(complexity - 1, len(chord_patterns[style][mode]) - 1)
        chord_pattern = chord_patterns[style][mode][pattern_idx]
        
        # 將和弦級數轉換為實際和弦
        k = key.Key(detected_key)
        
        # 根據旋律段落生成和弦
        result_chords = []
        
        # 音符太少時使用簡單的和弦進行
        if len(melody_notes) < 4 or not sections:
            # 每2秒一個和弦，或使用旋律持續時間
            max_time = max([n.start_time + n.duration for n in melody_notes]) if melody_notes else 8.0
            chord_duration = 2.0
            
            for i in range(0, int(max_time / chord_duration) + 1):
                chord_idx = i % len(chord_pattern)
                chord_degree = chord_pattern[chord_idx]
                
                # 轉換為實際和弦
                chord_name = self._degree_to_chord(chord_degree, k)
                
                result_chords.append({
                    "chord": chord_name,
                    "start_time": i * chord_duration,
                    "duration": chord_duration
                })
        else:
            # 為每個段落生成和弦
            for section_idx, section in enumerate(sections):
                section_duration = section["end_time"] - section["start_time"]
                
                # 計算每個和弦的持續時間
                # 較短段落使用較少和弦，較長段落使用更多和弦
                chords_count = max(1, min(4, int(section_duration / 2)))
                chord_duration = section_duration / chords_count
                
                # 選擇這個段落使用的和弦進行模式部分
                # 為了變化，不同段落可以使用不同的和弦進行模式部分
                pattern_offset = section_idx % len(chord_pattern)
                
                for i in range(chords_count):
                    chord_idx = (i + pattern_offset) % len(chord_pattern)
                    chord_degree = chord_pattern[chord_idx]
                    
                    # 轉換為實際和弦
                    chord_name = self._degree_to_chord(chord_degree, k)
                    
                    result_chords.append({
                        "chord": chord_name,
                        "start_time": section["start_time"] + i * chord_duration,
                        "duration": chord_duration
                    })
        
        # 根據旋律音符進一步調整和弦
        self._refine_chords_with_melody(result_chords, melody_notes, k, complexity)
        
        return result_chords
    
    def _degree_to_chord(self, degree: str, k: key.Key) -> str:
        """將和弦級數轉換為實際和弦名稱
        
        Args:
            degree: 和弦級數（如"I", "vi", "V7"等）
            k: 調性對象
            
        Returns:
            實際和弦名稱（如"C", "Am", "G7"等）
        """
        # 解析級數
        is_minor = degree[0].islower()
        
        # 檢查是否有其他修飾符（如7, maj7等）
        base_degree = degree[0].upper()
        modifiers = degree[1:] if len(degree) > 1 else ""
        
        # 級數到羅馬數字的映射
        roman_to_int = {
            "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7
        }
        
        # 獲取級數代表的音階音
        scale_index = roman_to_int.get(base_degree, 1) - 1
        
        # 獲取調內的音階音
        if k.mode == 'minor':
            scale_degrees = k.getScale('minor').getPitches()
        else:
            scale_degrees = k.getScale('major').getPitches()
        
        # 獲取和弦根音
        root_note = scale_degrees[scale_index % len(scale_degrees)]
        root_name = root_note.name
        
        # 構建和弦名稱
        chord_name = root_name
        
        # 添加和弦類型
        if is_minor:
            chord_name += "m"
        
        # 添加修飾符
        chord_name += modifiers
        
        return chord_name
    
    def _refine_chords_with_melody(self, 
                                  chords: List[Dict[str, Any]], 
                                  melody_notes: List[MCPNote],
                                  k: key.Key,
                                  complexity: int):
        """根據旋律進一步調整和弦
        
        Args:
            chords: 和弦進行
            melody_notes: 旋律音符
            k: 調性對象
            complexity: 複雜度
            
        Returns:
            調整後的和弦進行（直接修改輸入的chords列表）
        """
        # 僅在複雜度較高時進行更復雜的調整
        if complexity < 3:
            return
        
        # 遍歷每個和弦
        for chord_data in chords:
            chord_start = chord_data["start_time"]
            chord_end = chord_start + chord_data["duration"]
            
            # 找出這個和弦區間內的所有旋律音符
            notes_in_chord = [
                n for n in melody_notes 
                if (n.start_time >= chord_start and n.start_time < chord_end) or
                   (n.start_time < chord_start and n.start_time + n.duration > chord_start)
            ]
            
            # 如果沒有音符在此和弦範圍內，跳過
            if not notes_in_chord:
                continue
                
            # 獲取這些音符的MIDI音高
            pitches = [n.pitch for n in notes_in_chord]
            
            # 如果有足夠的不同音高，可以考慮使用它們構成的和弦
            unique_pitches = set(pitches)
            if len(unique_pitches) >= 3 and complexity >= 4:
                # 將MIDI音高轉換為音符名稱
                pitch_objs = [pitch.Pitch(midi=p) for p in unique_pitches]
                pitch_names = [p.name for p in pitch_objs]
                
                # 嘗試從這些音符創建和弦
                try:
                    # 使用 music21 嘗試辨識和弦
                    c = chord.Chord(pitch_names)
                    common_name = c.commonName
                    
                    # 如果找到了有意義的和弦名稱，使用它
                    if common_name and common_name != 'Chord':
                        # 找到根音
                        root = c.root().name
                        
                        # 構建和弦名稱
                        if 'minor' in common_name.lower():
                            chord_data["chord"] = root + "m"
                        elif 'major' in common_name.lower():
                            chord_data["chord"] = root
                        elif 'seventh' in common_name.lower():
                            chord_data["chord"] = root + "7"
                        elif 'diminished' in common_name.lower():
                            chord_data["chord"] = root + "dim"
                        elif 'augmented' in common_name.lower():
                            chord_data["chord"] = root + "aug"
                        else:
                            # 保持原樣
                            pass
                except:
                    # 如果辨識失敗，保持原樣
                    pass 