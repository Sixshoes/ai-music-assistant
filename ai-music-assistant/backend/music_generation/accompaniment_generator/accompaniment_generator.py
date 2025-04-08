"""自動伴奏生成器

基於旋律和和弦生成多軌道編曲功能
"""

import logging
import random
import os
import sys
from typing import List, Dict, Any, Optional, Tuple

# 添加項目根目錄到 Python 路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
if project_root not in sys.path:
    sys.path.append(project_root)

from backend.mcp.mcp_schema import Note as MCPNote, MelodyInput
from .chord_generator import ChordGenerator

logger = logging.getLogger(__name__)

class AccompanimentGenerator:
    """自動伴奏生成器
    
    基於旋律和和弦生成多軌伴奏
    """
    
    def __init__(self):
        """初始化伴奏生成器"""
        self.chord_generator = ChordGenerator()
        logger.info("初始化伴奏生成器")
    
    def generate_accompaniment(self, 
                              melody: MelodyInput,
                              style: str = "pop",
                              complexity: int = 3,
                              instruments: List[str] = None) -> Dict[str, Any]:
        """生成多軌伴奏
        
        Args:
            melody: 輸入旋律
            style: 音樂風格
            complexity: 複雜度 (1-5)
            instruments: 樂器列表，如未指定則自動選擇
            
        Returns:
            多軌伴奏數據
        """
        try:
            logger.info(f"開始為旋律生成{style}風格伴奏，複雜度: {complexity}")
            
            # 如果未指定樂器，根據風格自動選擇
            if not instruments:
                instruments = self._select_instruments(style)
            
            # 生成和弦進行
            chord_progression = self.chord_generator.generate_chords(
                melody=melody,
                style=style,
                complexity=complexity
            )
            
            # 生成各軌道的音符
            tracks = {}
            
            # 1. 和弦軌道
            tracks["chords"] = self._generate_chord_track(
                chord_progression=chord_progression,
                style=style,
                complexity=complexity
            )
            
            # 2. 低音軌道
            tracks["bass"] = self._generate_bass_track(
                chord_progression=chord_progression,
                style=style,
                complexity=complexity
            )
            
            # 3. 節奏軌道
            if complexity >= 2:
                tracks["rhythm"] = self._generate_rhythm_track(
                    chord_progression=chord_progression,
                    style=style,
                    complexity=complexity
                )
            
            # 4. 裝飾音軌道
            if complexity >= 3:
                tracks["ornament"] = self._generate_ornament_track(
                    chord_progression=chord_progression,
                    melody=melody.notes,
                    style=style,
                    complexity=complexity
                )
            
            # 5. 打擊樂軌道
            if "drums" in instruments:
                tracks["drums"] = self._generate_drums_track(
                    melody=melody,
                    style=style,
                    complexity=complexity
                )
            
            return {
                "chord_progression": chord_progression,
                "tracks": tracks,
                "instruments": instruments,
                "style": style,
                "complexity": complexity
            }
            
        except Exception as e:
            logger.error(f"生成伴奏失敗: {str(e)}", exc_info=True)
            raise
    
    def _select_instruments(self, style: str) -> List[str]:
        """根據風格選擇適合的樂器
        
        Args:
            style: 音樂風格
            
        Returns:
            樂器列表
        """
        # 預設樂器配置
        style_instruments = {
            "pop": ["piano", "acoustic_guitar", "bass", "drums"],
            "rock": ["electric_guitar", "bass", "drums", "synth"],
            "jazz": ["piano", "double_bass", "drums", "saxophone"],
            "classical": ["piano", "violin", "cello", "flute"],
            "electronic": ["synth_lead", "synth_bass", "synth_pad", "drums"]
        }
        
        return style_instruments.get(style, ["piano", "bass", "drums"])
    
    def _generate_chord_track(self, 
                             chord_progression: List[Dict[str, Any]],
                             style: str,
                             complexity: int) -> List[Dict[str, Any]]:
        """生成和弦軌道
        
        Args:
            chord_progression: 和弦進行
            style: 音樂風格
            complexity: 複雜度
            
        Returns:
            和弦軌道的音符列表
        """
        chord_notes = []
        
        # 和弦音符的基準八度
        base_octave = 4
        
        # 和弦琶音模式
        arpeggio_patterns = {
            "pop": [
                [0, 1, 2],          # 基本三和弦
                [0, 2, 1, 2],       # 簡單琶音
                [0, 1, 2, 1, 0, 1]  # 更複雜的琶音
            ],
            "jazz": [
                [0, 1, 2, 3],       # 七和弦
                [0, 2, 1, 3, 2],    # 爵士風格
                [3, 2, 1, 0, 1, 2]  # 下行琶音
            ]
        }
        
        # 默認使用流行樂模式
        patterns = arpeggio_patterns.get(style, arpeggio_patterns["pop"])
        pattern_idx = min(complexity - 1, len(patterns) - 1)
        pattern = patterns[pattern_idx]
        
        for chord_data in chord_progression:
            chord_name = chord_data["chord"]
            start_time = chord_data["start_time"]
            duration = chord_data["duration"]
            
            # 解析和弦類型
            root, chord_type = self._parse_chord_name(chord_name)
            
            # 獲取和弦音符
            chord_tones = self._get_chord_tones(root, chord_type)
            
            # 使用不同的和弦音符排列，根據複雜度和風格
            if complexity <= 2 or style == "classical":
                # 簡單的塊狀和弦
                # 生成和弦的每個音符
                for i, interval in enumerate(chord_tones):
                    note_data = {
                        "pitch": self._note_name_to_midi(root, base_octave) + interval,
                        "start_time": start_time,
                        "duration": duration,
                        "velocity": 70 + (i == 0) * 10  # 根音稍微強調
                    }
                    chord_notes.append(note_data)
            else:
                # 較複雜的琶音或分解和弦
                note_count = max(4, int(duration * 2))  # 每2秒4個音符
                note_duration = duration / note_count
                
                for i in range(note_count):
                    # 使用模式選擇和弦音的索引
                    tone_idx = pattern[i % len(pattern)] % len(chord_tones)
                    interval = chord_tones[tone_idx]
                    
                    # 生成音符
                    note_data = {
                        "pitch": self._note_name_to_midi(root, base_octave) + interval,
                        "start_time": start_time + i * note_duration,
                        "duration": note_duration * 0.8,  # 略微縮短，使聲音不連貫
                        "velocity": 70 + (i % len(pattern) == 0) * 15  # 強調某些音符
                    }
                    chord_notes.append(note_data)
        
        return chord_notes
    
    def _generate_bass_track(self, 
                            chord_progression: List[Dict[str, Any]],
                            style: str,
                            complexity: int) -> List[Dict[str, Any]]:
        """生成低音軌道
        
        Args:
            chord_progression: 和弦進行
            style: 音樂風格
            complexity: 複雜度
            
        Returns:
            低音軌道的音符列表
        """
        bass_notes = []
        
        # 低音音符的八度
        bass_octave = 2
        
        # 低音模式
        bass_patterns = {
            "pop": [
                [0],                # 只有根音
                [0, 0, 4, 0],       # 根音和屬音交替
                [0, 4, 5, 4, 0, 2]  # 更複雜的走音
            ],
            "jazz": [
                [0, 7],             # 根音和屬音
                [0, 2, 4, 5],       # 爵士風格走音
                [0, 7, 5, 4, 2, 0]  # 下行走音
            ]
        }
        
        # 默認使用流行樂模式
        patterns = bass_patterns.get(style, bass_patterns["pop"])
        pattern_idx = min(complexity - 1, len(patterns) - 1)
        pattern = patterns[pattern_idx]
        
        for chord_data in chord_progression:
            chord_name = chord_data["chord"]
            start_time = chord_data["start_time"]
            duration = chord_data["duration"]
            
            # 解析和弦根音
            root, _ = self._parse_chord_name(chord_name)
            root_midi = self._note_name_to_midi(root, bass_octave)
            
            if complexity <= 1:
                # 簡單的持續低音
                bass_notes.append({
                    "pitch": root_midi,
                    "start_time": start_time,
                    "duration": duration * 0.9,  # 留一點空隙
                    "velocity": 90
                })
            else:
                # 更複雜的低音走向
                notes_count = max(1, int(duration * 2))  # 大約每0.5秒一個音符
                note_duration = duration / notes_count
                
                for i in range(notes_count):
                    # 使用模式選擇音程
                    interval = pattern[i % len(pattern)]
                    
                    # 生成音符
                    note_data = {
                        "pitch": root_midi + interval,
                        "start_time": start_time + i * note_duration,
                        "duration": note_duration * 0.8,  # 稍微縮短
                        "velocity": 85 + (i % len(pattern) == 0) * 10  # 強調某些音符
                    }
                    bass_notes.append(note_data)
        
        return bass_notes
    
    def _generate_rhythm_track(self, 
                              chord_progression: List[Dict[str, Any]],
                              style: str,
                              complexity: int) -> List[Dict[str, Any]]:
        """生成節奏軌道
        
        Args:
            chord_progression: 和弦進行
            style: 音樂風格
            complexity: 複雜度
            
        Returns:
            節奏軌道的音符列表
        """
        rhythm_notes = []
        
        # 節奏吉他/鋼琴的八度
        rhythm_octave = 3
        
        # 節奏模式 (1代表彈，0代表不彈)
        rhythm_patterns = {
            "pop": [
                [1, 0, 1, 0],           # 簡單的節奏
                [1, 0, 0, 1, 0, 1, 0, 0],# 稍微複雜的節奏
                [1, 0, 1, 1, 0, 1, 0, 1] # 更豐富的節奏
            ],
            "rock": [
                [1, 0, 1, 0],
                [1, 1, 0, 1, 0, 0, 1, 0],
                [1, 0, 1, 0, 1, 0, 1, 1]
            ],
            "jazz": [
                [0, 1, 0, 1],           # 反拍
                [0, 1, 1, 0, 1, 0, 1, 1],
                [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0]
            ]
        }
        
        # 默認使用流行樂模式
        patterns = rhythm_patterns.get(style, rhythm_patterns["pop"])
        pattern_idx = min(complexity - 2, len(patterns) - 1)  # 考慮到需要至少2的複雜度
        pattern = patterns[pattern_idx]
        
        for chord_data in chord_progression:
            chord_name = chord_data["chord"]
            start_time = chord_data["start_time"]
            duration = chord_data["duration"]
            
            # 解析和弦
            root, chord_type = self._parse_chord_name(chord_name)
            
            # 獲取和弦音符
            chord_tones = self._get_chord_tones(root, chord_type)
            
            # 計算這個和弦需要多少個節奏單位
            # 通常是每拍一個節奏單位
            beat_duration = 60 / 120  # 假設120 BPM，每拍0.5秒
            units_count = max(1, int(duration / beat_duration))
            
            # 設定每個節奏單位的持續時間
            unit_duration = duration / units_count
            
            for i in range(units_count):
                # 檢查這個單位是否需要彈奏
                should_play = pattern[i % len(pattern)] == 1
                
                if should_play:
                    # 為每個和弦音符添加一個節奏音符
                    for j, interval in enumerate(chord_tones):
                        note_data = {
                            "pitch": self._note_name_to_midi(root, rhythm_octave) + interval,
                            "start_time": start_time + i * unit_duration,
                            "duration": unit_duration * 0.7,  # 使聲音不連貫
                            "velocity": 70 if j > 0 else 80  # 根音稍強
                        }
                        rhythm_notes.append(note_data)
        
        return rhythm_notes
    
    def _generate_ornament_track(self, 
                                chord_progression: List[Dict[str, Any]],
                                melody: List[MCPNote],
                                style: str,
                                complexity: int) -> List[Dict[str, Any]]:
        """生成裝飾音軌道
        
        Args:
            chord_progression: 和弦進行
            melody: 主旋律音符
            style: 音樂風格
            complexity: 複雜度
            
        Returns:
            裝飾音軌道的音符列表
        """
        ornament_notes = []
        
        # 裝飾音的八度
        ornament_octave = 5
        
        # 裝飾音間隔
        ornament_intervals = {
            "pop": [0, 7, 12],  # 根音、五度、高八度
            "jazz": [0, 4, 7, 11],  # 七和弦音
            "classical": [0, 7, 12, 16]  # 更廣泛的音程
        }
        
        used_intervals = ornament_intervals.get(style, ornament_intervals["pop"])
        
        # 生成裝飾音
        for i, chord_data in enumerate(chord_progression):
            chord_name = chord_data["chord"]
            start_time = chord_data["start_time"]
            duration = chord_data["duration"]
            
            # 解析和弦
            root, chord_type = self._parse_chord_name(chord_name)
            
            # 獲取和弦音符
            chord_tones = self._get_chord_tones(root, chord_type)
            
            # 為了變化，每個和弦使用不同的裝飾音模式
            if complexity >= 4 and i % 2 == 1:  # 隔一個和弦使用不同的裝飾方式
                # 創建一個簡單的對旋律
                notes_count = max(2, int(duration * 2))
                note_duration = duration / notes_count
                
                # 使用和弦音加上一些過渡音
                for j in range(notes_count):
                    # 選擇一個和弦音
                    chord_idx = j % len(chord_tones)
                    interval = chord_tones[chord_idx]
                    
                    # 添加一些隨機性
                    if j > 0 and random.random() < 0.3:
                        # 偶爾添加非和弦音作為過渡
                        interval = interval + random.choice([-1, 1])
                    
                    note_data = {
                        "pitch": self._note_name_to_midi(root, ornament_octave) + interval,
                        "start_time": start_time + j * note_duration,
                        "duration": note_duration * 0.8,
                        "velocity": 65 + (j == 0) * 10  # 強調第一個音符
                    }
                    ornament_notes.append(note_data)
            else:
                # 使用簡單的裝飾音
                # 避免與主旋律衝突
                melody_at_this_time = [n for n in melody 
                                     if (n.start_time >= start_time and 
                                         n.start_time < start_time + duration)]
                
                # 如果這段時間有主旋律，使用較少的裝飾音
                if melody_at_this_time:
                    # 只在和弦開始時添加一個強調音
                    for interval in used_intervals[:1]:  # 只使用第一個間隔
                        note_data = {
                            "pitch": self._note_name_to_midi(root, ornament_octave) + interval,
                            "start_time": start_time + duration * 0.5,  # 在中間位置
                            "duration": duration * 0.4,
                            "velocity": 60  # 較輕的力度
                        }
                        ornament_notes.append(note_data)
                else:
                    # 沒有主旋律時，添加更多裝飾音
                    for interval in used_intervals:
                        note_data = {
                            "pitch": self._note_name_to_midi(root, ornament_octave) + interval,
                            "start_time": start_time,
                            "duration": duration * 0.9,
                            "velocity": 70
                        }
                        ornament_notes.append(note_data)
        
        return ornament_notes
    
    def _generate_drums_track(self, 
                             melody: MelodyInput,
                             style: str,
                             complexity: int) -> List[Dict[str, Any]]:
        """生成打擊樂軌道
        
        Args:
            melody: 輸入旋律
            style: 音樂風格
            complexity: 複雜度
            
        Returns:
            打擊樂軌道的音符列表
        """
        drums_notes = []
        
        # 鼓的MIDI音符對應
        drum_map = {
            "kick": 36,      # 低音鼓
            "snare": 38,     # 小鼓
            "hihat": 42,     # 閉合高音鈸
            "open_hh": 46,   # 開放高音鈸
            "crash": 49,     # 碰撞鈸
            "ride": 51       # 叮叮鈸
        }
        
        # 不同風格的鼓點模式
        drum_patterns = {
            "pop": {
                "kick":  [1, 0, 0, 0, 1, 0, 0, 0],
                "snare": [0, 0, 1, 0, 0, 0, 1, 0],
                "hihat": [1, 1, 1, 1, 1, 1, 1, 1]
            },
            "rock": {
                "kick":  [1, 0, 0, 1, 1, 0, 0, 0],
                "snare": [0, 0, 1, 0, 0, 0, 1, 0],
                "hihat": [1, 1, 1, 1, 1, 1, 1, 1]
            },
            "jazz": {
                "ride":  [1, 0, 1, 0, 1, 0, 1, 0],
                "hihat": [0, 0, 1, 0, 0, 0, 1, 0],
                "kick":  [1, 0, 0, 0, 1, 0, 0, 0]
            }
        }
        
        # 默認使用流行鼓模式
        pattern = drum_patterns.get(style, drum_patterns["pop"])
        
        # 預計的速度，這裡假設120 BPM
        tempo = melody.tempo or 120
        beat_duration = 60 / tempo
        
        # 獲取旋律的總長度
        max_time = 0
        if melody.notes:
            max_time = max([n.start_time + n.duration for n in melody.notes])
        else:
            max_time = 60  # 默認1分鐘
        
        # 生成鼓點
        current_time = 0
        measure_length = beat_duration * 4  # 4/4拍
        
        while current_time < max_time:
            for i in range(8):  # 8個8分音符，相當於一個2/4小節
                time_point = current_time + i * beat_duration / 2
                
                # 添加打擊樂器音符
                for drum_name, hits in pattern.items():
                    if hits[i % len(hits)]:
                        velocity = 100 if drum_name == "kick" or (drum_name == "snare" and i in [2, 6]) else 80
                        
                        # 根據複雜度調整
                        if complexity >= 4 and random.random() < 0.2:
                            # 偶爾添加變化
                            continue
                        
                        note_data = {
                            "pitch": drum_map[drum_name],
                            "start_time": time_point,
                            "duration": beat_duration / 4,  # 鼓聲較短
                            "velocity": velocity
                        }
                        drums_notes.append(note_data)
                        
                        # 添加填充
                        if complexity >= 3 and i == 7 and random.random() < 0.3:
                            # 在小節末尾偶爾添加鼓點填充
                            fill_velocity = 70
                            fill_duration = beat_duration / 4
                            
                            for j in range(4):
                                fill_note = {
                                    "pitch": random.choice([drum_map["snare"], drum_map["hihat"]]),
                                    "start_time": time_point + j * fill_duration / 4,
                                    "duration": fill_duration / 4,
                                    "velocity": fill_velocity + j * 5
                                }
                                drums_notes.append(fill_note)
            
            current_time += measure_length
        
        return drums_notes
    
    def _parse_chord_name(self, chord_name: str) -> Tuple[str, str]:
        """解析和弦名稱
        
        Args:
            chord_name: 和弦名稱，例如"C"、"Am"、"G7"
            
        Returns:
            根音和和弦類型
        """
        # 基本解析
        if chord_name[1:2] in ['#', 'b']:
            root = chord_name[:2]
            chord_type = chord_name[2:]
        else:
            root = chord_name[:1]
            chord_type = chord_name[1:]
        
        # 如果沒有明確的和弦類型，假設是大調
        if not chord_type:
            chord_type = "maj"
        
        return root, chord_type
    
    def _get_chord_tones(self, root: str, chord_type: str) -> List[int]:
        """獲取和弦的音程列表
        
        Args:
            root: 根音
            chord_type: 和弦類型
            
        Returns:
            相對於根音的音程列表（半音單位）
        """
        # 常見和弦類型的音程
        chord_intervals = {
            "": [0, 4, 7],           # 大三和弦
            "maj": [0, 4, 7],        # 大三和弦
            "m": [0, 3, 7],          # 小三和弦
            "7": [0, 4, 7, 10],      # 屬七和弦
            "maj7": [0, 4, 7, 11],   # 大七和弦
            "m7": [0, 3, 7, 10],     # 小七和弦
            "dim": [0, 3, 6],        # 減三和弦
            "aug": [0, 4, 8],        # 增三和弦
            "sus4": [0, 5, 7],       # 掛四和弦
            "sus2": [0, 2, 7],       # 掛二和弦
            "6": [0, 4, 7, 9],       # 大六和弦
            "m6": [0, 3, 7, 9],      # 小六和弦
            "9": [0, 4, 7, 10, 14],  # 九和弦
            "maj9": [0, 4, 7, 11, 14], # 大九和弦
            "m9": [0, 3, 7, 10, 14], # 小九和弦
        }
        
        # 返回和弦的音程，如果沒有找到，返回大三和弦
        return chord_intervals.get(chord_type, chord_intervals[""])
    
    def _note_name_to_midi(self, note_name: str, octave: int) -> int:
        """將音符名稱轉換為MIDI音符值
        
        Args:
            note_name: 音符名稱，例如"C"、"Eb"
            octave: 八度
            
        Returns:
            MIDI音符值
        """
        # 音符到相對值的映射
        note_values = {
            "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
            "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
            "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11
        }
        
        # 獲取音符的相對值
        note_value = note_values.get(note_name, 0)
        
        # 計算MIDI值
        midi_value = 12 + (octave * 12) + note_value
        
        return midi_value 