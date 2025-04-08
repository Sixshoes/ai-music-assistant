#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
簡化版MCP服務

提供與MCP兼容的接口，但不依賴TensorFlow等重量級庫
"""

import os
import random
import logging
from typing import Dict, List, Any, Optional
from enum import Enum
from midiutil import MIDIFile

# 配置日誌
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Note:
    """音符類"""
    def __init__(self, pitch: int, start_time: float, duration: float, velocity: int = 100):
        self.pitch = pitch  # MIDI音高
        self.start_time = start_time  # 開始時間(拍)
        self.duration = duration  # 持續時間(拍)
        self.velocity = velocity  # 力度(0-127)

class RhythmPattern(Enum):
    """節奏型態枚舉"""
    STRAIGHT = "straight"  # 平直
    SWING = "swing"        # 搖擺
    SHUFFLE = "shuffle"    # 切分
    SYNCOPATED = "syncopated"  # 切分音
    WALTZ = "waltz"        # 華爾茲
    LATIN = "latin"        # 拉丁
    COMPLEX = "complex"    # 複雜

class SimplifiedMCP:
    """簡化版MCP服務"""
    
    def __init__(self):
        """初始化簡化版MCP服務"""
        logger.info("初始化簡化版MCP服務")
        self.scales = {
            "C": [0, 2, 4, 5, 7, 9, 11],  # C大調
            "G": [7, 9, 11, 0, 2, 4, 6],  # G大調
            "F": [5, 7, 9, 10, 0, 2, 4],  # F大調
            "Am": [9, 11, 0, 2, 4, 5, 7], # A小調
            "Em": [4, 6, 7, 9, 11, 0, 2], # E小調
            "Dm": [2, 4, 5, 7, 9, 10, 0]  # D小調
        }
        
        self.chord_progressions = {
            "pop": [
                ["C", "G", "Am", "F"],
                ["C", "Am", "F", "G"],
                ["G", "D", "Em", "C"],
                ["Am", "F", "C", "G"]
            ],
            "jazz": [
                ["Cmaj7", "Dm7", "G7", "Cmaj7"],
                ["Dm7", "G7", "Cmaj7", "Am7"],
                ["Cmaj7", "Am7", "Dm7", "G7"],
                ["Dm7", "G7", "Em7", "A7", "Dm7", "G7"]
            ],
            "classical": [
                ["C", "G", "Am", "Em", "F", "C", "F", "G"],
                ["C", "Dm", "G", "C"],
                ["Am", "Dm", "E", "Am"]
            ],
            "electronic": [
                ["Am", "F", "C", "G"],
                ["Cm", "G#", "D#", "G"],
                ["Fm", "C#", "G#", "D#"]
            ]
        }
        
        self.chord_to_notes = {
            # 大三和弦
            "C": [60, 64, 67],     # C E G
            "G": [55, 59, 62],     # G B D
            "D": [50, 54, 57],     # D F# A
            "A": [57, 61, 64],     # A C# E
            "E": [52, 56, 59],     # E G# B
            "F": [53, 57, 60],     # F A C
            
            # 小三和弦
            "Am": [57, 60, 64],    # A C E
            "Em": [52, 55, 59],    # E G B
            "Dm": [50, 53, 57],    # D F A
            "Bm": [59, 62, 66],    # B D F#
            
            # 七和弦
            "Cmaj7": [60, 64, 67, 71], # C E G B
            "Dm7": [50, 53, 57, 60],   # D F A C
            "G7": [55, 59, 62, 65],    # G B D F
            "Fmaj7": [53, 57, 60, 64], # F A C E
            "Am7": [57, 60, 64, 67],   # A C E G
            "Em7": [52, 55, 59, 62],   # E G B D
            
            # 屬七和弦
            "A7": [57, 61, 64, 67],    # A C# E G
            "E7": [52, 56, 59, 63],    # E G# B D
            
            # 增強和減弱和弦
            "Caug": [60, 64, 68],     # C E G#
            "Cdim": [60, 63, 66],     # C Eb Gb
            
            # 其他和弦
            "G#": [56, 60, 63],       # G# C D#
            "D#": [51, 55, 58],       # D# G A#
            "C#": [49, 53, 56],       # C# F G#
            "Fm": [53, 56, 60],       # F G# C
            "Cm": [48, 51, 55],       # C Eb G
        }
    
    def generate_melody_from_text(self, text_description: str, params: Optional[Dict[str, Any]] = None) -> List[Note]:
        """根據文字描述生成旋律
        
        Args:
            text_description: 文字描述
            params: 音樂參數
            
        Returns:
            List[Note]: 旋律音符列表
        """
        logger.info(f"根據文字描述生成旋律: {text_description}")
        
        # 從文字描述推斷音樂風格
        music_style = self._analyze_music_style(text_description)
        scale = self._get_scale(params)
        
        # 創建基本音樂結構
        notes = self._generate_melody(scale, music_style)
        
        # 創建標準Note對象列表
        result = []
        for i, note in enumerate(notes):
            result.append(Note(
                pitch=note,
                start_time=i * 0.25,  # 每個音符1/4拍
                duration=0.25,
                velocity=80 + random.randint(-10, 10)
            ))
        
        logger.info(f"生成了 {len(result)} 個旋律音符")
        return result
    
    def generate_musical_idea(self, parameters: Dict[str, Any], output_midi_path: str) -> Dict[str, Any]:
        """生成完整的音樂想法並保存為MIDI
        
        Args:
            parameters: 音樂參數
            output_midi_path: 輸出MIDI文件路徑
            
        Returns:
            Dict[str, Any]: 音樂生成結果
        """
        logger.info(f"生成完整的音樂想法: {parameters}")
        
        # 提取參數
        description = parameters.get("description", "")
        
        # 從文字描述推斷音樂風格
        music_style = self._analyze_music_style(description)
        
        # 生成旋律
        melody_notes = self._generate_melody(self._get_scale(parameters), music_style)
        
        # 轉換為標準Note對象
        melody = []
        for i, note in enumerate(melody_notes):
            melody.append(Note(
                pitch=note,
                start_time=i * 0.25,  # 每個音符1/4拍
                duration=0.25,
                velocity=80 + random.randint(-10, 10)
            ))
        
        # 生成和弦進行
        chord_progression = self._get_chord_progression(music_style)
        
        # 轉換和弦為音符
        chord_notes = []
        for i, chord in enumerate(chord_progression):
            # 每個和弦持續4拍
            chord_pitches = self.chord_to_notes.get(chord, [60, 64, 67])  # 默認為C和弦
            for pitch in chord_pitches:
                chord_notes.append(Note(
                    pitch=pitch,
                    start_time=i * 4.0,
                    duration=4.0,
                    velocity=60
                ))
        
        # 生成低音聲部
        bass_notes = []
        for i, chord in enumerate(chord_progression):
            # 使用和弦的根音作為低音
            root = self.chord_to_notes.get(chord, [60])[0]
            # 移到低八度
            root_bass = root - 12
            # 添加基本的低音模式
            for j in range(4):  # 每個和弦4拍
                if j == 0:  # 第一拍彈根音
                    bass_notes.append(Note(
                        pitch=root_bass,
                        start_time=i * 4.0 + j,
                        duration=1.0,
                        velocity=70
                    ))
                elif j == 2:  # 第三拍彈五度
                    bass_notes.append(Note(
                        pitch=root_bass + 7,
                        start_time=i * 4.0 + j,
                        duration=1.0,
                        velocity=65
                    ))
                else:  # 其他拍彈隨機音符
                    bass_notes.append(Note(
                        pitch=root_bass + random.choice([0, 7, 4]),
                        start_time=i * 4.0 + j,
                        duration=1.0,
                        velocity=65
                    ))
        
        # 生成鼓聲部
        drum_notes = []
        total_bars = len(chord_progression)
        for bar in range(total_bars):
            for beat in range(4):  # 每小節4拍
                # 低音鼓 (每拍的第1拍和第3拍)
                if beat == 0 or beat == 2:
                    drum_notes.append(Note(
                        pitch=36,  # 低音鼓
                        start_time=bar * 4 + beat,
                        duration=0.25,
                        velocity=80
                    ))
                
                # 小鼓 (每拍的第2和第4拍)
                if beat == 1 or beat == 3:
                    drum_notes.append(Note(
                        pitch=38,  # 小鼓
                        start_time=bar * 4 + beat,
                        duration=0.25,
                        velocity=70
                    ))
                
                # 閉合踩鑔 (每個八分音符)
                for i in range(2):
                    drum_notes.append(Note(
                        pitch=42,  # 閉合踩鑔
                        start_time=bar * 4 + beat + i * 0.5,
                        duration=0.25,
                        velocity=60
                    ))
        
        # 保存為MIDI
        self._save_to_midi(
            melody=melody,
            chords=chord_notes,
            bass=bass_notes,
            drums=drum_notes,
            tempo=self._get_tempo(parameters, music_style),
            output_path=output_midi_path
        )
        
        result = {
            "melody_length": len(melody),
            "chord_progression": chord_progression,
            "bass_notes": len(bass_notes),
            "drum_notes": len(drum_notes),
            "midi_path": output_midi_path,
            "style": music_style
        }
        
        logger.info(f"音樂想法已生成並保存到 {output_midi_path}")
        return result
    
    def _analyze_music_style(self, text: str) -> str:
        """從文字描述分析音樂風格
        
        Args:
            text: 文字描述
            
        Returns:
            str: 音樂風格
        """
        text = text.lower()
        
        if any(word in text for word in ["爵士", "jazz", "藍調", "blues", "搖擺"]):
            return "jazz"
        elif any(word in text for word in ["古典", "classical", "交響", "symphony", "協奏"]):
            return "classical"
        elif any(word in text for word in ["電子", "electronic", "edm", "舞曲", "dance"]):
            return "electronic"
        else:
            return "pop"  # 默認為流行風格
    
    def _get_scale(self, params: Optional[Dict[str, Any]] = None) -> List[int]:
        """獲取音階
        
        Args:
            params: 音樂參數
            
        Returns:
            List[int]: 音階音符
        """
        if params and "key" in params:
            key = params["key"]
            return self.scales.get(key, self.scales["C"])
        
        # 默認使用C大調
        return self.scales["C"]
    
    def _get_tempo(self, params: Optional[Dict[str, Any]] = None, style: str = "pop") -> int:
        """獲取速度
        
        Args:
            params: 音樂參數
            style: 音樂風格
            
        Returns:
            int: 速度 (BPM)
        """
        if params and "tempo" in params:
            return int(params["tempo"])
        
        # 根據風格設置默認速度
        default_tempos = {
            "jazz": 120,
            "classical": 90,
            "electronic": 130,
            "pop": 110
        }
        
        return default_tempos.get(style, 120)
    
    def _get_chord_progression(self, style: str) -> List[str]:
        """獲取和弦進行
        
        Args:
            style: 音樂風格
            
        Returns:
            List[str]: 和弦進行
        """
        # 從預設和弦進行中隨機選擇一個
        progressions = self.chord_progressions.get(style, self.chord_progressions["pop"])
        return random.choice(progressions)
    
    def _generate_melody(self, scale: List[int], style: str, length: int = 64) -> List[int]:
        """生成旋律
        
        Args:
            scale: 音階
            style: 音樂風格
            length: 旋律長度
            
        Returns:
            List[int]: 旋律音符
        """
        melody = []
        
        # 定義音樂動機（短小、有特色的旋律片段）
        motifs = {
            "jazz": [
                [0, 2, 4, 5, 7, 9, 11, 12],  # 上行音階
                [0, 2, 3, 5, 7, 9, 10, 12],  # 小調音階
                [0, 3, 5, 6, 7, 10, 12],     # 藍調音階
                [0, 4, 7, 11, 12],           # 大七和弦分解
                [0, 3, 7, 10, 12],           # 小七和弦分解
                [0, 4, 7, 10, 12],           # 屬七和弦分解
                [0, -1, 0, 2, 0, -1, -3]     # 爵士特色動機
            ],
            "classical": [
                [0, 2, 4, 0, 2, 4, 7],       # 三和弦分解
                [0, 1, 2, 3, 4, 5, 4, 3],    # 古典風格
                [0, 2, 4, 7, 4, 2, 0],       # 下行三和弦
                [0, -2, 0, 2, 0, -2, 0],     # 對稱動機
                [0, 4, 7, 12, 7, 4, 0],      # 大跨度動機
                [0, 2, 0, 2, 4, 2, 4, 7]     # 階梯式動機
            ],
            "pop": [
                [0, 2, 4, 5, 4, 2, 0],       # 流行風格
                [0, 0, 4, 4, 5, 5, 4],       # 重複音動機
                [0, 0, 7, 7, 9, 9, 7],       # 重音高跳躍
                [0, 2, 4, 0, 0, 2, 4, 0],    # 迴圈動機
                [0, 2, 4, 2, 0, -3, 0]       # 波浪型動機
            ],
            "electronic": [
                [0, 0, 7, 7, 9, 9, 7, 7],    # 重複電子風格
                [0, 12, 0, 12, 7, 19, 7],    # 極大跳躍 
                [0, 4, 7, 12, 0, 4, 7, 12],  # 和弦分解重複
                [0, 4, 7, 4, 0, 4, 7, 4],    # 分解和弦型
                [0, 7, 12, 7, 0, 7, 12, 7]   # 空五度動機
            ]
        }
        
        # 根據不同風格創建相應的強調節奏位置（1表示強調）
        rhythm_emphasis = {
            "jazz": [1, 0, 0.5, 0, 1, 0, 0.5, 0],  # 搖擺感，強調1和5拍，弱化3和7拍
            "classical": [1, 0, 0.8, 0, 0.9, 0, 0.8, 0],  # 較均衡的分佈
            "pop": [1, 0, 0, 0, 1, 0, 0, 0],  # 強調1和5拍，四四拍
            "electronic": [1, 0.3, 0.7, 0.3, 1, 0.3, 0.7, 0.3]  # 更頻繁的強調
        }
        
        # 起始音符 (音階的第一個音)
        current_note = scale[0] + 60  # 中央C (MIDI音高60) + 音階起始音
        melody.append(current_note)
        
        # 創建旋律輪廓
        if length < 16:
            contour = "linear"  # 短旋律使用簡單線性輪廓
        elif random.random() < 0.6:
            contour = "arch"    # 60%機率使用拱形輪廓（上升然後下降）
        else:
            contour = "wave"    # 40%機率使用波浪形輪廓
        
        # 生成輪廓指導方向
        directions = []
        if contour == "arch":
            mid_point = length // 2
            for i in range(length):
                if i < mid_point:
                    directions.append(1)  # 上升
                else:
                    directions.append(-1)  # 下降
        elif contour == "wave":
            wave_length = random.choice([4, 8, 12])  # 波長變化
            for i in range(length):
                period = (i % (wave_length * 2)) / wave_length
                if period < 1:
                    directions.append(1)  # 上升
                else:
                    directions.append(-1)  # 下降
        else:  # linear
            # 隨機選擇方向
            main_direction = random.choice([1, -1])
            directions = [main_direction] * length
        
        # 從風格特定動機中選擇1-3個
        style_motifs = motifs.get(style, motifs["pop"])
        selected_motifs = random.sample(style_motifs, min(3, len(style_motifs)))
        
        # 獲取風格特定的節奏強調
        emphasis = rhythm_emphasis.get(style, [1, 0, 0.5, 0, 1, 0, 0.5, 0])
        
        # 生成旋律
        i = 1
        while i < length:
            # 定期插入動機
            if random.random() < 0.3 and i + 8 <= length:  # 30%的機率插入動機
                # 選擇一個動機
                motif = random.choice(selected_motifs)
                
                # 轉換動機到當前音高
                current_scale_idx = scale.index(current_note % 12) if (current_note % 12) in scale else 0
                for j, interval in enumerate(motif):
                    if i + j >= length:
                        break
                        
                    # 計算音符
                    note_idx = (current_scale_idx + interval) % len(scale)
                    octave = (current_note // 12) + ((current_scale_idx + interval) // len(scale))
                    new_note = scale[note_idx] + (octave * 12)
                    
                    # 確保在合理範圍內
                    while new_note < 48:  # C3
                        new_note += 12
                    while new_note > 84:  # C6
                        new_note -= 12
                    
                    melody.append(new_note)
                    current_note = new_note
                    i += 1
            else:
                # 正常生成單個音符
                # 選擇一個隨機間隔，偏向於輪廓方向
                direction = directions[i % len(directions)]
                
                # 根據風格和節奏位置調整間隔選擇
                beat_position = i % 8  # 假設8分音符為基本節奏單位
                emphasis_value = emphasis[beat_position]
                
                if emphasis_value > 0.8:  # 強拍
                    if style == "jazz":
                        intervals = [direction * x for x in [1, 2, 3, 5, 7]] # 爵士強拍偏好更大間隔
                    else:
                        intervals = [direction * x for x in [1, 2, 3, 4]]  # 強拍偏好穩定和諧音程
                elif emphasis_value > 0.4:  # 次強拍
                    intervals = [direction * x for x in [1, 2, 3]]  # 中等間隔
                else:  # 弱拍
                    # 弱拍可以有更多變化
                    if style == "jazz":
                        intervals = [-3, -2, -1, 0, 1, 2, 3, 4, 5]  # 更多變化
                    elif style == "classical":
                        intervals = [-2, -1, 0, 1, 2]  # 經過音，級進
                    elif style == "electronic":
                        intervals = [-2, -1, 0, 0, 0, 1, 2, 3, 7]  # 更多重複和跳躍
                    else:  # pop
                        intervals = [-3, -2, -1, 0, 1, 2, 3, 4]
                
                # 選擇間隔
                interval = random.choice(intervals)
                
                # 計算音階內的新音符
                current_scale_idx = scale.index(current_note % 12) if (current_note % 12) in scale else 0
                
                # 根據間隔選擇新的音階位置
                new_scale_idx = (current_scale_idx + interval) % len(scale)
                
                # 計算八度偏移
                octave_shift = (current_scale_idx + interval) // len(scale)
                if interval < 0 and (current_scale_idx + interval) < 0:
                    octave_shift = -1 + (current_scale_idx + interval) // len(scale)
                
                # 計算新音符的實際MIDI音高
                new_note = scale[new_scale_idx] + ((current_note // 12) + octave_shift) * 12
                
                # 確保音符在合理範圍內 (MIDI 48-84，即C3-C6)
                while new_note < 48:
                    new_note += 12
                while new_note > 84:
                    new_note -= 12
                
                # 應用風格特定變化
                if style == "jazz":
                    # 爵士風格：添加藍調音和微分音
                    if random.random() < 0.15:
                        # 藍音：降三度或降七度
                        if random.random() < 0.5:
                            new_note -= 1
                        else:
                            # 有時使用#9（升九度，相當於升二度）
                            new_note = new_note + 3 if random.random() < 0.3 else new_note
                    
                    # 添加更多切分音
                    if beat_position % 2 == 0 and random.random() < 0.3:
                        # 在偶數拍上添加一些節奏變化
                        if random.random() < 0.5:
                            # 延長前一個音符（模擬切分）
                            if len(melody) > 0:
                                melody.append(melody[-1])  # 重複前一個音符
                                i += 1
                                continue
                
                elif style == "classical":
                    # 古典風格：添加裝飾音和華彩
                    if random.random() < 0.1:
                        if random.random() < 0.7:
                            # 添加上裝飾音
                            ornament = new_note + 1 if (new_note + 1) % 12 in scale else new_note + 2
                            melody.append(ornament)
                            i += 1
                        melody.append(new_note)  # 添加主音
                        i += 1
                        continue
                
                elif style == "pop":
                    # 流行風格：重複音符和簡單旋律型
                    if random.random() < 0.2:
                        # 20%的可能重複當前音符
                        melody.append(current_note)
                        i += 1
                        continue
                    
                    # 有時保持在同一音符上
                    if random.random() < 0.15:
                        new_note = current_note
                
                elif style == "electronic":
                    # 電子風格：大跳躍和重複模式
                    if random.random() < 0.15:
                        # 偶爾添加八度跳躍
                        new_note = current_note + (12 * direction)
                    elif random.random() < 0.2:
                        # 重複前一個音符
                        melody.append(current_note)
                        i += 1
                        continue
                
                # 將新音符添加到旋律
                melody.append(new_note)
                current_note = new_note
                i += 1
        
        # 後處理：確保結束音是音階中的穩定音
        # 優先選擇根音(1級)、屬音(5級)或中音(3級)結束
        final_note = melody[-1]
        root_note = scale[0]  # 根音
        dominant_note = scale[4] if len(scale) > 4 else scale[0]  # 屬音(5級)
        mediant_note = scale[2] if len(scale) > 2 else scale[0]  # 中音(3級)
        
        # 計算最後音符與根音的差異（以半音為單位）
        final_class = final_note % 12
        if final_class != root_note and final_class != dominant_note and final_class != mediant_note:
            # 如果最後一個音符不是1/3/5級，則修改為其中之一
            last_idx = len(melody) - 1
            
            # 優先選擇根音結束
            if random.random() < 0.6:  # 60%的機率使用根音結束
                final_octave = final_note // 12
                melody[last_idx] = root_note + (final_octave * 12)
            elif random.random() < 0.7:  # 28%的機率使用屬音結束(0.6 + 0.4*0.7 = 0.88)
                final_octave = final_note // 12
                melody[last_idx] = dominant_note + (final_octave * 12)
            else:  # 12%的機率使用中音結束
                final_octave = final_note // 12
                melody[last_idx] = mediant_note + (final_octave * 12)
                
        # 為旋律添加額外的音樂表現和變化
        melody = self._add_melodic_variations(melody, style)
        
        return melody
        
    def _add_melodic_variations(self, melody: List[int], style: str) -> List[int]:
        """為旋律添加音樂表現和變化
        
        Args:
            melody: 原始旋律
            style: 音樂風格
            
        Returns:
            List[int]: 處理後的旋律
        """
        if len(melody) < 4:
            return melody
            
        # 創建一個新的旋律列表
        result = melody.copy()
        
        # 應用風格特定處理
        if style == "jazz":
            # 爵士風格：添加藍調音和即興修飾
            for i in range(1, len(result) - 1):
                # 在強拍位置的連續音符間添加經過音
                if i % 4 == 0 and random.random() < 0.25:
                    # 在兩個音符之間添加一個經過音
                    current = result[i]
                    previous = result[i-1]
                    interval = current - previous
                    
                    if abs(interval) > 2:  # 只在大於全音的間隔中添加
                        # 在兩音符中間插入經過音
                        middle_note = previous + (interval // 2)
                        # 將經過音插入到適當位置
                        result.insert(i, middle_note)
                        
            # 應用爵士裝飾
            for i in range(len(result) - 3):
                # 添加爵士風格的滑音或裝飾音
                if random.random() < 0.1:
                    # 10%的機率在當前音符添加一個上滑音
                    upper_neighbor = result[i] + 1
                    # 插入滑音
                    result.insert(i + 1, upper_neighbor)
                    
        elif style == "classical":
            # 古典風格：添加更多裝飾音和華彩
            for i in range(2, len(result) - 2):
                if i % 8 == 0 and random.random() < 0.3:
                    # 添加簡單的華彩
                    current = result[i]
                    if random.random() < 0.5:
                        # 上方華彩
                        result.insert(i, current + 2)
                        result.insert(i, current + 1)
                    else:
                        # 下方華彩
                        result.insert(i, current - 2)
                        result.insert(i, current - 1)
                    
        elif style == "pop":
            # 流行風格：更多的音符重複和節奏穩定性
            i = 0
            while i < len(result) - 1:
                # 增加音符重複的機率
                if random.random() < 0.15:
                    # 重複當前音符
                    result.insert(i + 1, result[i])
                i += 1
                    
        elif style == "electronic":
            # 電子風格：增加極端的對比和重複序列
            for i in range(0, len(result) - 4, 4):
                if random.random() < 0.2:
                    # 創建一個4音符的重複序列
                    pattern = result[i:i+4]
                    # 在原序列之後添加重複
                    for note in pattern:
                        result.append(note)
        
        # 確保旋律不會太長
        max_length = 128  # 設置最大長度限制
        if len(result) > max_length:
            result = result[:max_length]
            
        return result
    
    def _save_to_midi(self, melody, chords, bass, drums, tempo, output_path):
        """保存音樂到MIDI文件
        
        Args:
            melody: 旋律音符列表
            chords: 和弦音符列表
            bass: 低音音符列表
            drums: 鼓聲部音符列表
            tempo: 速度
            output_path: 輸出路徑
        """
        # 創建MIDI文件，四個軌道：旋律、和弦、低音和鼓
        midi = MIDIFile(4)
        
        # 設置速度
        for i in range(4):
            midi.addTempo(i, 0, tempo)
        
        # 設置樂器音色
        midi.addProgramChange(0, 0, 0, 0)   # 旋律: 鋼琴
        midi.addProgramChange(1, 1, 0, 48)  # 和弦: 弦樂合奏
        midi.addProgramChange(2, 2, 0, 33)  # 低音: 電貝斯
        # 鼓不需要設置音色，直接使用MIDI打擊樂通道(10)
        
        # 添加旋律
        for note in melody:
            midi.addNote(
                track=0, 
                channel=0, 
                pitch=note.pitch, 
                time=note.start_time, 
                duration=note.duration, 
                volume=note.velocity
            )
        
        # 添加和弦
        for note in chords:
            midi.addNote(
                track=1, 
                channel=1, 
                pitch=note.pitch, 
                time=note.start_time, 
                duration=note.duration, 
                volume=note.velocity
            )
        
        # 添加低音
        for note in bass:
            midi.addNote(
                track=2, 
                channel=2, 
                pitch=note.pitch, 
                time=note.start_time, 
                duration=note.duration, 
                volume=note.velocity
            )
        
        # 添加鼓聲部
        for note in drums:
            midi.addNote(
                track=3, 
                channel=9,  # MIDI通道10(索引9)用於打擊樂器
                pitch=note.pitch, 
                time=note.start_time, 
                duration=note.duration, 
                volume=note.velocity
            )
        
        # 確保輸出目錄存在
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # 寫入文件
        with open(output_path, "wb") as f:
            midi.writeFile(f)
        
        logger.info(f"MIDI文件已保存至 {output_path}") 