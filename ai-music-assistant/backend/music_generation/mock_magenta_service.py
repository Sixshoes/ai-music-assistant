"""Magenta 音樂生成服務 (模擬版)

提供基於 Magenta 的音樂生成功能的模擬實現
"""

import os
import logging
import random
import tempfile
import base64
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

# 配置日誌
logger = logging.getLogger(__name__)

# 嘗試導入 MCP 相關模組
try:
    from mcp.mcp_schema import MusicParameters, Note, MelodyInput, Genre
except ImportError:
    try:
        from mcp.mcp_schema_simple import MusicParameters, Note, MelodyInput, Genre
        logger.info("使用簡化版 mcp_schema_simple")
    except ImportError:
        try:
            from backend.mcp.mcp_schema import MusicParameters, Note, MelodyInput, Genre
        except ImportError:
            try:
                from backend.mcp.mcp_schema_simple import MusicParameters, Note, MelodyInput, Genre
                logger.info("使用絕對路徑簡化版 mcp_schema_simple")
            except ImportError:
                # 如果導入失敗，創建簡單的替代類
                logger.warning("無法導入任何MCP模塊，使用內置替代類")
                
                class Genre:
                    POP = "pop"
                    ROCK = "rock"
                    JAZZ = "jazz"
                    CLASSICAL = "classical"
                    ELECTRONIC = "electronic"
                    BLUES = "blues"
                    COUNTRY = "country"
                
                class Note:
                    def __init__(self, pitch=0, start_time=0, duration=0, velocity=0):
                        self.pitch = pitch
                        self.start_time = start_time
                        self.duration = duration
                        self.velocity = velocity
                        
                class MelodyInput:
                    def __init__(self, notes=None):
                        self.notes = notes or []
                        
                class MusicParameters:
                    def __init__(self, **kwargs):
                        for key, value in kwargs.items():
                            setattr(self, key, value)

class MagentaService:
    """Magenta 音樂生成服務(模擬版)

    提供與 Magenta 相容的音樂生成功能接口
    """

    def __init__(self, model_path_dict: Optional[Dict[str, str]] = None):
        """初始化 Magenta 服務

        Args:
            model_path_dict: 模型路徑字典，如 {"melody_rnn": "/path/to/model"}
        """
        self.model_path_dict = model_path_dict or {}
        logger.info("初始化 Magenta 模擬服務")
    
    def generate_melody(self, 
                       parameters: MusicParameters, 
                       primer_melody: Optional[List[Note]] = None,
                       num_steps: int = 128,
                       temperature: float = 1.0) -> List[Note]:
        """生成旋律

        Args:
            parameters: 音樂參數
            primer_melody: 起始旋律（如果提供）
            num_steps: 生成的步數
            temperature: 溫度參數（控制隨機性）

        Returns:
            List[Note]: 生成的旋律
        """
        logger.info(f"生成旋律 (模擬), 溫度={temperature}, 步數={num_steps}")
        
        # 獲取參數
        tempo = getattr(parameters, 'tempo', 120)
        key = getattr(parameters, 'key', 'C')
        genre = getattr(parameters, 'genre', 'pop').lower()  # 確保風格名稱小寫
        
        # 定義不同風格的音樂特徵
        style_traits = {
            'pop': {
                'note_density': 0.8,          # 音符密度 (0-1)
                'rhythmic_variety': 0.6,      # 節奏變化程度 (0-1)
                'pitch_range': (60, 84),      # 音高範圍 (MIDI音符)
                'syncopation': 0.3,           # 切分音使用程度 (0-1)
                'velocity_range': (70, 90),   # 力度範圍
                'durations': [0.25, 0.5, 1.0] # 音符持續時間 (拍)
            },
            'rock': {
                'note_density': 0.7,
                'rhythmic_variety': 0.7,
                'pitch_range': (48, 78),      # 搖滾樂旋律通常較低
                'syncopation': 0.5,           # 更多切分音
                'velocity_range': (80, 110),  # 更大的力度
                'durations': [0.25, 0.5, 0.75, 1.0]
            },
            'jazz': {
                'note_density': 0.9,
                'rhythmic_variety': 0.9,      # 爵士樂有更多節奏變化
                'pitch_range': (55, 85),
                'syncopation': 0.8,           # 大量切分音
                'velocity_range': (60, 100),
                'durations': [0.125, 0.25, 0.33, 0.5, 0.75]  # 更複雜的節奏
            },
            'classical': {
                'note_density': 0.7,
                'rhythmic_variety': 0.6,
                'pitch_range': (60, 96),      # 古典樂更寬的音域
                'syncopation': 0.2,           # 較少切分音
                'velocity_range': (50, 100),  # 更大的力度變化
                'durations': [0.25, 0.5, 1.0, 2.0]  # 更多長音符
            }
        }
        
        # 如果不支援的風格，使用流行樂風格特徵
        if genre not in style_traits:
            logger.warning(f"不支援的風格 '{genre}'，使用 'pop' 風格特徵")
            genre = 'pop'
        
        # 獲取當前風格特徵
        traits = style_traits[genre]
        
        # 根據調性定義音階
        scales = {
            'C': [0, 2, 4, 5, 7, 9, 11],    # C大調: C D E F G A B
            'G': [7, 9, 11, 0, 2, 4, 6],    # G大調: G A B C D E F#
            'D': [2, 4, 6, 7, 9, 11, 1],    # D大調: D E F# G A B C#
            'A': [9, 11, 1, 2, 4, 6, 8],    # A大調: A B C# D E F# G#
            'E': [4, 6, 8, 9, 11, 1, 3],    # E大調: E F# G# A B C# D#
            'F': [5, 7, 9, 10, 0, 2, 4],    # F大調: F G A Bb C D E
            'Bb': [10, 0, 2, 3, 5, 7, 9],   # Bb大調: Bb C D Eb F G A
            'Am': [9, 11, 0, 2, 4, 5, 7],   # A小調: A B C D E F G
            'Em': [4, 6, 7, 9, 11, 0, 2],   # E小調: E F# G A B C D
            'Bm': [11, 1, 2, 4, 6, 7, 9],   # B小調: B C# D E F# G A
            'F#m': [6, 8, 9, 11, 1, 2, 4],  # F#小調: F# G# A B C# D E
            'Cm': [0, 2, 3, 5, 7, 8, 10],   # C小調: C D Eb F G Ab Bb
            'Gm': [7, 9, 10, 0, 2, 3, 5]    # G小調: G A Bb C D Eb F
        }
        
        # 默認使用C大調
        base_scale = scales.get(key, scales['C'])
        
        # 根據風格選擇起始八度
        if genre == 'rock':
            base_octave = 4  # 較低
        elif genre == 'classical':
            base_octave = 5  # 較高
        else:
            base_octave = 5  # 中等
        
        # 生成旋律
        notes = []
        current_time = 0.0
        beat_duration = 60 / tempo  # 一拍的持續時間 (秒)
        
        # 決定旋律長度 (音符數量)
        if genre == 'jazz':
            num_notes = random.randint(24, 32)  # 爵士樂通常音符更多
        elif genre == 'classical':
            num_notes = random.randint(16, 32)  # 古典樂變化較大
        else:
            num_notes = random.randint(16, 24)  # 其他風格適中
        
        # 在風格指定的音高範圍內生成起始音符
        min_pitch, max_pitch = traits['pitch_range']
        
        # 生成音符
        for i in range(num_notes):
            # 選擇音階中的音符
            scale_degree = random.choice(range(len(base_scale)))
            
            # 根據風格特徵，決定音高的分佈
            if genre == 'jazz' and random.random() < 0.3:
                # 爵士樂更喜歡使用藍調音階中的特殊音符
                pitch_options = [base_scale[scale_degree], base_scale[scale_degree] - 1]
                pitch = random.choice(pitch_options)
            else:
                pitch = base_scale[scale_degree]
            
            # 確定八度
            if random.random() < 0.2:  # 20% 機率使用相鄰八度
                if random.random() < 0.5:
                    octave = base_octave + 1
                else:
                    octave = base_octave - 1
            else:
                octave = base_octave
            
            # 計算MIDI音高
            midi_pitch = 12 * octave + pitch
            
            # 確保音高在風格允許的範圍內
            midi_pitch = max(min_pitch, min(max_pitch, midi_pitch))
            
            # 根據風格特徵選擇持續時間
            duration_weights = None
            if genre == 'jazz':
                # 爵士樂傾向於更短和更不規則的音符
                duration_weights = [0.4, 0.3, 0.2, 0.05, 0.05]
            elif genre == 'classical':
                # 古典樂有更多變化，包括更長的音符
                duration_weights = [0.2, 0.3, 0.3, 0.2]
            elif genre == 'rock':
                # 搖滾樂節奏強勁但簡單
                duration_weights = [0.3, 0.5, 0.15, 0.05]
            else:  # pop
                duration_weights = [0.3, 0.5, 0.2]
            
            duration_value = random.choices(traits['durations'], weights=duration_weights)[0]
            duration = duration_value * beat_duration
            
            # 根據風格添加切分音
            if random.random() < traits['syncopation']:
                # 添加輕微的時間偏移
                time_offset = beat_duration * 0.125 * random.choice([-1, 1])
                current_time = max(0, current_time + time_offset)
            
            # 根據風格選擇力度 (音量)
            min_vel, max_vel = traits['velocity_range']
            velocity = random.randint(min_vel, max_vel)
            
            # 根據音樂的位置調整力度 (對所有風格都適用)
            if i % 4 == 0:  # 每4個音符的第一個是強拍
                velocity = min(127, velocity + 15)
            
            # 創建音符
            note = Note(
                pitch=midi_pitch,
                start_time=current_time,
                duration=duration,
                velocity=velocity
            )
            notes.append(note)
            
            # 更新時間
            current_time += duration
            
            # 根據風格的音符密度有機率添加休止符
            if random.random() > traits['note_density']:
                # 添加短暫休止
                current_time += beat_duration * random.choice([0.25, 0.5])
        
        # 如果有起始旋律，將其添加到生成的旋律之前
        if primer_melody:
            combined_notes = []
            for note in primer_melody:
                combined_notes.append(note)
            
            # 調整生成旋律的起始時間
            last_end_time = max([n.start_time + n.duration for n in primer_melody])
            for note in notes:
                note.start_time += last_end_time
                combined_notes.append(note)
            
            notes = combined_notes
        
        logger.info(f"已生成 {len(notes)} 個音符的 {genre} 風格旋律")
        return notes

    def generate_accompaniment(self, 
                              melody: List[Note], 
                              parameters: MusicParameters) -> Dict[str, List[Note]]:
        """為旋律生成伴奏

        Args:
            melody: 主旋律音符列表
            parameters: 音樂參數

        Returns:
            Dict[str, List[Note]]: 各聲部伴奏音符，如 {"chords": [...], "bass": [...]}
        """
        logger.info("生成伴奏 (模擬)")
        
        # 計算總時長
        if melody:
            last_note = max(melody, key=lambda n: n.start_time + n.duration)
            total_duration = last_note.start_time + last_note.duration
        else:
            total_duration = 8.0  # 默認8秒
            
        # 獲取並處理風格參數
        genre = "pop"
        if hasattr(parameters, 'genre') and parameters.genre:
            genre = str(parameters.genre).lower()
            logger.info(f"伴奏使用風格: {genre}")
        
        # 獲取並確保正確處理調性
        key = "C"  # 默認C大調
        if hasattr(parameters, 'key') and parameters.key:
            key = str(parameters.key)
            logger.info(f"伴奏使用調性: {key}")
            
        # 根據速度調整音符持續時間
        tempo = getattr(parameters, 'tempo', 120)
        # 確保速度是有效的數值
        try:
            tempo = float(tempo)
            if tempo < 40:
                tempo = 40
            elif tempo > 240:
                tempo = 240
        except (ValueError, TypeError):
            tempo = 120
            logger.warning(f"無效的速度值，使用默認值120: {parameters.tempo}")
            
        beat_duration = 60 / tempo
        logger.info(f"伴奏使用速度: {tempo} BPM")
            
        # 生成模擬的和弦音符
        chord_notes = []
        bass_notes = []
        
        # 不同調性的和弦進行
        chord_progressions = {
            # 大調和弦進行
            'C': [
                [60, 64, 67],  # C
                [65, 69, 72],  # F
                [67, 71, 74],  # G
                [60, 64, 67]   # C
            ],
            'G': [
                [55, 59, 62],  # G
                [60, 64, 67],  # C
                [62, 66, 69],  # D
                [55, 59, 62]   # G
            ],
            'D': [
                [50, 54, 57],  # D
                [55, 59, 62],  # G
                [57, 61, 64],  # A
                [50, 54, 57]   # D
            ],
            'F': [
                [53, 57, 60],  # F
                [58, 62, 65],  # Bb
                [60, 64, 67],  # C
                [53, 57, 60]   # F
            ],
            
            # 小調和弦進行
            'Am': [
                [57, 60, 64],  # Am
                [55, 59, 62],  # G
                [53, 57, 60],  # F
                [52, 55, 59]   # E
            ],
            'Em': [
                [52, 55, 59],  # Em
                [50, 54, 57],  # D
                [48, 52, 55],  # C
                [47, 50, 54]   # B
            ],
            'Dm': [
                [50, 53, 57],  # Dm
                [48, 52, 55],  # C
                [53, 57, 60],  # F
                [55, 59, 62]   # G
            ]
        }
        
        # 獲取對應調性的和弦進行，如果沒有對應的則使用C大調
        selected_progression = chord_progressions.get(key, chord_progressions['C'])
        
        # 根據風格調整和弦節奏
        if genre == "pop":
            # 流行: 標準4拍和弦
            chord_duration = 4 * beat_duration
            velocity_chords = (65, 80)
            velocity_bass = (75, 90)
            
        elif genre == "rock":
            # 搖滾: 強勁的和弦
            chord_duration = 2 * beat_duration  # 更快的和弦變化
            velocity_chords = (75, 90)
            velocity_bass = (80, 95)
            
        elif genre == "jazz":
            # 爵士: 複雜的和弦和節奏
            chord_duration = 4 * beat_duration
            velocity_chords = (60, 75)
            velocity_bass = (70, 85)
            
            # 爵士和弦加入9度音
            for i in range(len(selected_progression)):
                if random.random() > 0.5:  # 50%概率添加9度音
                    ninth = (selected_progression[i][0] + 14) % 12 + 60
                    selected_progression[i].append(ninth)
            
        elif genre == "classical":
            # 古典: 優雅的分解和弦
            chord_duration = 4 * beat_duration
            velocity_chords = (55, 75)
            velocity_bass = (65, 80)
            
        elif genre == "electronic":
            # 電子: 重複的單一和弦或音符
            chord_duration = 2 * beat_duration
            velocity_chords = (70, 80)
            velocity_bass = (75, 85)
            
        else:
            # 默認
            chord_duration = 4 * beat_duration
            velocity_chords = (65, 80)
            velocity_bass = (75, 90)
            
        # 生成和弦
        current_time = 0.0
        
        while current_time < total_duration:
            # 選擇和弦
            chord_index = int(current_time / chord_duration) % len(selected_progression)
            chord = selected_progression[chord_index]
            
            # 創建和弦音符
            for pitch in chord:
                # 控制和弦音符的力度
                velocity_chord = random.randint(velocity_chords[0], velocity_chords[1])
                
                chord_note = Note(
                    pitch=pitch,
                    start_time=current_time,
                    duration=chord_duration,
                    velocity=velocity_chord
                )
                chord_notes.append(chord_note)
            
            # 創建低音音符
            velocity_bass_note = random.randint(velocity_bass[0], velocity_bass[1])
            
            bass_note = Note(
                pitch=chord[0] - 12,  # 低八度
                start_time=current_time,
                duration=chord_duration,
                velocity=velocity_bass_note
            )
            bass_notes.append(bass_note)
            
            current_time += chord_duration
        
        return {
            "chords": chord_notes,
            "bass": bass_notes
        }

    def generate_drum_pattern(self, 
                             parameters: MusicParameters, 
                             num_measures: int = 4) -> List[Note]:
        """生成鼓點模式

        Args:
            parameters: 音樂參數
            num_measures: 生成的小節數

        Returns:
            List[Note]: 鼓點音符列表
        """
        logger.info(f"生成鼓點模式 (模擬), 小節數={num_measures}")
        
        # 獲取參數
        tempo = getattr(parameters, 'tempo', 120)
        genre = getattr(parameters, 'genre', 'pop').lower()  # 確保風格名稱小寫
        
        # 鼓點映射（MIDI音符編號）
        drum_map = {
            'kick': 36,        # 低音鼓
            'snare': 38,       # 小鼓
            'clap': 39,        # 拍手
            'closed_hh': 42,   # 閉合高音踩鑔
            'open_hh': 46,     # 開放高音踩鑔
            'ride': 51,        # 叉鑔
            'crash': 49,       # 碰鑔
            'tom_h': 48,       # 高音嗵鼓
            'tom_m': 47,       # 中音嗵鼓
            'tom_l': 45,       # 低音嗵鼓
            'cowbell': 56,     # 牛鈴
            'tambourine': 54   # 鈴鼓
        }
        
        # 不同風格的鼓點模式 (1表示擊打，0表示不擊打)
        # 每個小節4拍，每拍分為4個16分音符
        style_patterns = {
            'pop': {
                'kick':      [1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0],
                'snare':     [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                'closed_hh': [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
                'crash':     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            },
            'rock': {
                'kick':      [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
                'snare':     [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                'closed_hh': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                'crash':     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                'tom_h':     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
            },
            'jazz': {
                'ride':      [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
                'closed_hh': [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
                'kick':      [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                'snare':     [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0]
            },
            'classical': {
                # 古典樂通常沒有鼓點，但可以用定音鼓和其他打擊樂器代替
                'kick':      [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                'tom_l':     [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                'tambourine':[0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0]
            },
            'electronic': {
                'kick':      [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
                'snare':     [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
                'closed_hh': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                'open_hh':   [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
                'clap':      [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
            },
            'funk': {
                'kick':      [1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0],
                'snare':     [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
                'closed_hh': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                'open_hh':   [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1]
            },
            'hip hop': {
                'kick':      [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                'snare':     [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                'closed_hh': [1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1],
                'open_hh':   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
            }
        }
        
        # 如果不支援的風格，使用流行樂風格特徵
        if genre not in style_patterns:
            logger.warning(f"不支援的鼓點風格 '{genre}'，使用 'pop' 風格")
            genre = 'pop'
        
        # 獲取當前風格的鼓點模式
        pattern = style_patterns[genre]
        
        # 計算時間參數
        beat_duration = 60 / tempo  # 一拍的持續時間 (秒)
        sixteenth_duration = beat_duration / 4  # 16分音符的持續時間
        
        # 根據力度和變化調整參數
        velocity_variation = {
            'pop': 10,
            'rock': 15,
            'jazz': 20,
            'classical': 25,
            'electronic': 5,
            'funk': 15,
            'hip hop': 10
        }
        
        # 獲取當前風格的力度變化範圍
        var_range = velocity_variation.get(genre, 10)
        
        # 根據風格設定基本力度
        base_velocity = {
            'kick': {'pop': 100, 'rock': 110, 'jazz': 90, 'classical': 95, 'electronic': 115, 'funk': 105, 'hip hop': 110},
            'snare': {'pop': 95, 'rock': 100, 'jazz': 85, 'classical': 90, 'electronic': 100, 'funk': 95, 'hip hop': 105},
            'closed_hh': {'pop': 80, 'rock': 90, 'jazz': 70, 'classical': 75, 'electronic': 95, 'funk': 85, 'hip hop': 90},
            'open_hh': {'pop': 85, 'rock': 95, 'jazz': 75, 'classical': 80, 'electronic': 100, 'funk': 90, 'hip hop': 95},
            'ride': {'pop': 80, 'rock': 85, 'jazz': 90, 'classical': 85, 'electronic': 90, 'funk': 85, 'hip hop': 85},
            'crash': {'pop': 100, 'rock': 110, 'jazz': 95, 'classical': 100, 'electronic': 105, 'funk': 100, 'hip hop': 100},
            'tom_h': {'pop': 90, 'rock': 95, 'jazz': 85, 'classical': 90, 'electronic': 95, 'funk': 90, 'hip hop': 90},
            'tom_m': {'pop': 90, 'rock': 95, 'jazz': 85, 'classical': 90, 'electronic': 95, 'funk': 90, 'hip hop': 90},
            'tom_l': {'pop': 90, 'rock': 95, 'jazz': 85, 'classical': 90, 'electronic': 95, 'funk': 90, 'hip hop': 90}
        }
        
        # 生成鼓點
        drum_notes = []
        
        # 為每個小節生成鼓點
        for measure in range(num_measures):
            # 計算當前小節的起始時間
            measure_start = measure * 16 * sixteenth_duration
            
            # 為每種鼓點添加音符
            for drum_type, hits in pattern.items():
                if drum_type not in drum_map:
                    continue
                    
                # 獲取鼓點的MIDI音符編號
                pitch = drum_map[drum_type]
                
                # 獲取基本力度
                base_vel = base_velocity.get(drum_type, {}).get(genre, 90)
                
                # 對每個16分音符位置檢查是否需要添加鼓點
                for i, hit in enumerate(hits):
                    if hit == 1:
                        # 添加一些隨機變化，使鼓點聽起來更自然
                        # 時間偏移 (微小的時間提前或延後)
                        time_offset = 0
                        if genre == 'jazz':  # 爵士樂有更多擺動感
                            # 爵士鼓的擺動感
                            if i % 2 == 1:  # 偶數位置（弱拍）
                                time_offset = sixteenth_duration * random.uniform(0.05, 0.2)
                        elif genre == 'funk':  # 放克有獨特的律動
                            time_offset = sixteenth_duration * random.uniform(-0.05, 0.1)
                            
                        # 力度變化 (使鼓點聽起來更有活力)
                        velocity_offset = random.randint(-var_range, var_range)
                        
                        # 強拍通常力度更強
                        if i % 4 == 0:  # 每一拍的第一個16分音符
                            velocity_offset += 10
                        
                        # 起始時間、持續時間和力度
                        start_time = measure_start + (i * sixteenth_duration) + time_offset
                        # 低音鼓和小鼓通常持續時間較長
                        if drum_type in ['kick', 'snare', 'tom_l', 'tom_m', 'tom_h']:
                            duration = sixteenth_duration * 1.5
                        else:
                            duration = sixteenth_duration
                            
                        velocity = min(127, max(1, base_vel + velocity_offset))
                        
                        # 創建音符
                        note = Note(
                            pitch=pitch,
                            start_time=start_time,
                            duration=duration,
                            velocity=velocity
                        )
                        drum_notes.append(note)
                        
                        # 為某些風格添加鬼音符 (ghost notes)
                        if drum_type == 'snare' and genre in ['funk', 'jazz'] and random.random() < 0.3:
                            # 在下一個16分音符位置添加較輕的鬼音符
                            ghost_time = start_time + sixteenth_duration
                            ghost_velocity = max(1, min(127, int(velocity * 0.6)))
                            ghost_note = Note(
                                pitch=pitch,
                                start_time=ghost_time,
                                duration=sixteenth_duration * 0.7,
                                velocity=ghost_velocity
                            )
                            drum_notes.append(ghost_note)
                            
        # 添加每小節開始的強調
        if genre in ['rock', 'pop', 'electronic']:
            for measure in range(num_measures):
                # 在每小節開始添加一個強調的碰鑔 (除了第一小節，那已經有了)
                if measure > 0 and measure % 4 == 0:  # 每4小節
                    crash_note = Note(
                        pitch=drum_map['crash'],
                        start_time=measure * 16 * sixteenth_duration,
                        duration=beat_duration * 2,  # 通常碰鑔會持續較長時間
                        velocity=100
                    )
                    drum_notes.append(crash_note)
                    
        logger.info(f"已生成 {len(drum_notes)} 個 {genre} 風格的鼓點音符")
        return drum_notes

    def melody_to_midi(self, melody: List[Note], output_path: str, tempo: int = 120) -> str:
        """將旋律轉換為 MIDI 文件

        Args:
            melody: 旋律音符列表
            output_path: 輸出 MIDI 文件路徑
            tempo: 速度 (BPM)

        Returns:
            str: MIDI 文件路徑
        """
        logger.info(f"將旋律轉換為 MIDI (保存至 {output_path})")
        
        # 創建臨時文件
        if not output_path:
            temp_dir = tempfile.gettempdir()
            output_path = os.path.join(temp_dir, f"melody_{int(random.random() * 1000)}.mid")
        
        try:
            # 嘗試使用midiutil創建MIDI文件
            from midiutil import MIDIFile
            
            # 創建一個單軌道的MIDI文件
            midi = MIDIFile(1)
            
            # 添加軌道名稱和tempo
            track = 0
            time = 0
            midi.addTrackName(track, time, "AI Generated Melody")
            midi.addTempo(track, time, tempo)
            
            # 將音符添加到MIDI文件
            for note in melody:
                pitch = int(note.pitch)
                # 確保音高在MIDI範圍內 (0-127)
                if pitch < 0:
                    pitch = 0
                elif pitch > 127:
                    pitch = 127
                    
                # 計算音符的開始時間(以拍為單位)
                start_beat = note.start_time * (tempo / 60)
                
                # 計算音符的持續時間(以拍為單位)
                duration_beat = note.duration * (tempo / 60)
                
                # 確保力度在合理範圍內
                velocity = max(1, min(127, note.velocity))
                
                # 添加音符
                midi.addNote(
                    track=track,
                    channel=0,  # 使用MIDI通道0
                    pitch=pitch,
                    time=start_beat,
                    duration=duration_beat,
                    volume=velocity
                )
            
            # 寫入MIDI文件
            with open(output_path, 'wb') as output_file:
                midi.writeFile(output_file)
                
            logger.info(f"已成功創建MIDI文件: {output_path}，包含 {len(melody)} 個音符")
            return output_path
            
        except ImportError:
            logger.warning("無法使用midiutil庫，將創建基本MIDI文件")
            # 寫入一個基本的MIDI文件頭部
            with open(output_path, 'wb') as f:
                # 標準MIDI文件頭部
                f.write(b'MThd' + b'\x00\x00\x00\x06' + b'\x00\x01' + b'\x00\x01' + b'\x01\x80')
                
                # 寫入軌道頭
                f.write(b'MTrk')
                
                # 占位 - 實際應用中應該計算軌道長度並填寫
                f.write(b'\x00\x00\x00\x00')
            
            logger.warning(f"創建的是空MIDI文件: {output_path}，請安裝midiutil庫以生成有音符的文件")
            return output_path
        except Exception as e:
            logger.error(f"創建MIDI文件時發生錯誤: {str(e)}")
            # 寫入一個空的文件
            with open(output_path, 'wb') as f:
                f.write(b'MThd' + b'\x00\x00\x00\x06' + b'\x00\x01' + b'\x00\x01' + b'\x01\x80')
            return output_path

    def generate_full_arrangement(self,
                                 melody: Optional[List[Note]] = None,
                                 parameters: Optional[MusicParameters] = None,
                                 suggested_models: Optional[List[str]] = None) -> Dict[str, Any]:
        """生成完整編曲

        Args:
            melody: 主旋律，如未提供則自動生成
            parameters: 音樂參數
            suggested_models: 推薦使用的模型列表

        Returns:
            Dict[str, Any]: 包含各聲部的完整編曲
        """
        logger.info("生成完整編曲 (模擬)")
        
        params = parameters or MusicParameters(tempo=120)
        
        # 設定音樂風格相關參數
        style = getattr(params, 'genre', 'pop').lower()  # 確保風格名稱是小寫
        key = getattr(params, 'key', 'C')
        tempo = getattr(params, 'tempo', 120)
        
        # 定義不同風格的特徵
        style_traits = {
            'pop': {
                'chord_pattern': ['I', 'V', 'vi', 'IV'],  # 常見的流行樂和弦進行
                'bass_pattern': 'simple',                 # 簡單的貝斯線
                'drum_pattern': 'straight',               # 標準的鼓點型態
                'melody_octave': 5,                       # 旋律的八度範圍
                'instrument_map': {                       # 樂器映射
                    'melody': 0,     # 鋼琴
                    'chords': 4,     # 電鋼琴
                    'bass': 33,      # 原聲貝斯
                    'drums': 118     # 合成鼓
                }
            },
            'rock': {
                'chord_pattern': ['I', 'IV', 'V', 'IV'],  # 岩石樂和弦進行
                'bass_pattern': 'driving',                # 強勁的貝斯線
                'drum_pattern': 'heavy',                  # 較重的鼓點
                'melody_octave': 5,
                'instrument_map': {
                    'melody': 30,    # 電吉他
                    'chords': 29,    # 悶音電吉他 
                    'bass': 34,      # 電貝斯
                    'drums': 118     # 合成鼓
                }
            },
            'jazz': {
                'chord_pattern': ['ii', 'V', 'I', 'vi'],  # 爵士樂和弦進行
                'bass_pattern': 'walking',                # 行走低音
                'drum_pattern': 'swing',                  # 擺動節奏
                'melody_octave': 5,
                'instrument_map': {
                    'melody': 66,    # 薩克斯風
                    'chords': 0,     # 鋼琴
                    'bass': 33,      # 原聲貝斯
                    'drums': 118     # 合成鼓
                }
            },
            'classical': {
                'chord_pattern': ['I', 'IV', 'V', 'I'],   # 古典樂和弦進行
                'bass_pattern': 'baroque',                # 巴洛克風格低音
                'drum_pattern': 'none',                   # 無鼓點
                'melody_octave': 6,
                'instrument_map': {
                    'melody': 48,    # 弦樂合奏
                    'chords': 0,     # 鋼琴
                    'bass': 43,      # 大提琴
                    'drums': 47      # 定音鼓
                }
            }
        }
        
        # 如果指定了不支援的風格，使用流行樂作為默認風格
        if style not in style_traits:
            logger.warning(f"不支援的風格 '{style}'，使用 'pop' 風格代替")
            style = 'pop'
        
        # 獲取當前風格的特徵
        current_style = style_traits[style]
        
        # 如果沒有旋律，根據指定風格生成一個
        if not melody:
            # 調整旋律生成參數以符合風格
            melody_params = MusicParameters(
                tempo=params.tempo,
                key=params.key,
                genre=style  # 確保使用正確的風格
            )
            melody = self.generate_melody(melody_params)
            logger.info(f"已根據 '{style}' 風格生成旋律")
        
        # 生成符合風格的伴奏
        accompaniment = self.generate_accompaniment(melody, params)
        logger.info(f"已根據 '{style}' 風格生成伴奏")
        
        # 為當前風格生成適合的鼓點
        drums_params = MusicParameters(
            tempo=params.tempo,
            genre=style  # 確保使用正確的風格
        )
        drums = self.generate_drum_pattern(drums_params)
        logger.info(f"已根據 '{style}' 風格生成鼓點")
        
        # 生成 MIDI 文件
        temp_dir = tempfile.gettempdir()
        midi_path = os.path.join(temp_dir, f"{style}_arrangement_{int(random.random() * 1000)}.mid")
        
        try:
            # 嘗試使用midiutil創建多軌MIDI文件
            from midiutil import MIDIFile
            
            # 創建一個四軌道的MIDI文件 (旋律、和弦、低音、鼓)
            midi = MIDIFile(4)
            
            # 添加速度
            for track in range(4):
                midi.addTempo(track, 0, tempo)
            
            # 添加軌道名稱
            midi.addTrackName(0, 0, "Melody")
            midi.addTrackName(1, 0, "Chords")
            midi.addTrackName(2, 0, "Bass")
            midi.addTrackName(3, 0, "Drums")
            
            # 根據風格設置樂器音色
            instruments = current_style['instrument_map']
            for track, (role, program) in enumerate([
                ('melody', instruments['melody']), 
                ('chords', instruments['chords']), 
                ('bass', instruments['bass']), 
                ('drums', instruments['drums'])
            ]):
                midi.addProgramChange(track, 0, 0, program)
            
            # 添加旋律軌道的音符
            for note in melody:
                # 轉換時間單位從秒到拍
                start_beat = note.start_time * (tempo / 60)
                duration_beat = note.duration * (tempo / 60)
                
                # 根據風格調整旋律的力度
                velocity_mod = 1.0
                if style == 'rock':
                    velocity_mod = 1.2  # 搖滾樂旋律更強
                elif style == 'classical':
                    velocity_mod = 0.9  # 古典樂旋律更柔和
                    
                midi.addNote(
                    track=0,
                    channel=0,
                    pitch=max(0, min(127, note.pitch)),
                    time=start_beat,
                    duration=duration_beat,
                    volume=max(1, min(127, int(note.velocity * velocity_mod)))
                )
            
            # 添加和弦軌道的音符
            for note in accompaniment["chords"]:
                start_beat = note.start_time * (tempo / 60)
                duration_beat = note.duration * (tempo / 60)
                
                # 根據風格調整和弦的力度
                velocity_mod = 1.0
                if style == 'jazz':
                    velocity_mod = 0.8  # 爵士樂和弦更輕柔
                elif style == 'rock':
                    velocity_mod = 1.1  # 搖滾樂和弦更強勁
                    
                midi.addNote(
                    track=1,
                    channel=0,
                    pitch=max(0, min(127, note.pitch)),
                    time=start_beat,
                    duration=duration_beat,
                    volume=max(1, min(127, int(note.velocity * velocity_mod)))
                )
            
            # 添加低音軌道的音符
            for note in accompaniment["bass"]:
                start_beat = note.start_time * (tempo / 60)
                duration_beat = note.duration * (tempo / 60)
                
                # 根據風格調整貝斯的力度和音高
                velocity_mod = 1.0
                pitch_mod = 0
                
                if style == 'rock':
                    velocity_mod = 1.2  # 搖滾樂貝斯更強勁
                elif style == 'jazz':
                    # 爵士樂通常有更活躍的貝斯線
                    if random.random() < 0.3:  # 30% 機率添加走音
                        pitch_mod = random.choice([-2, 2])
                    
                midi.addNote(
                    track=2,
                    channel=0,
                    pitch=max(0, min(127, note.pitch + pitch_mod)),
                    time=start_beat,
                    duration_beat=duration_beat,
                    volume=max(1, min(127, int(note.velocity * velocity_mod)))
                )
            
            # 添加鼓點軌道的音符
            for note in drums:
                start_beat = note.start_time * (tempo / 60)
                duration_beat = note.duration * (tempo / 60)
                
                # 古典樂通常沒有鼓點
                if style == 'classical' and random.random() < 0.7:
                    continue
                    
                # 搖滾樂的鼓點更強
                velocity_mod = 1.1 if style == 'rock' else 1.0
                    
                midi.addNote(
                    track=3,
                    channel=9,  # MIDI通道10（索引9）是標準鼓點通道
                    pitch=max(0, min(127, note.pitch)),
                    time=start_beat,
                    duration=duration_beat,
                    volume=max(1, min(127, int(note.velocity * velocity_mod)))
                )
            
            # 寫入MIDI文件
            with open(midi_path, 'wb') as output_file:
                midi.writeFile(output_file)
                
            logger.info(f"已成功創建 {style} 風格的完整編曲MIDI文件: {midi_path}")
        
        except ImportError:
            logger.warning("無法使用midiutil庫，將創建簡化版MIDI文件")
            # 僅生成旋律部分的MIDI
            self.melody_to_midi(melody, midi_path, tempo)
        except Exception as e:
            logger.error(f"創建MIDI文件時發生錯誤: {str(e)}")
            # 僅生成旋律部分的MIDI作為備選
            self.melody_to_midi(melody, midi_path, tempo)
        
        # 返回結果
        return {
            "melody": melody,
            "chords": accompaniment["chords"],
            "bass": accompaniment["bass"],
            "drums": drums,
            "tempo": tempo,
            "style": style,
            "midi_path": midi_path,
            "models_used": suggested_models or ["mock_melody_generator", "mock_accompaniment_generator"]
        } 