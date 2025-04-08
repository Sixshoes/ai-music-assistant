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
            primer_melody: 引導旋律，如果提供則基於此旋律繼續生成
            num_steps: 生成的步數
            temperature: 生成的溫度參數，越高結果越隨機

        Returns:
            List[Note]: 生成的旋律音符列表
        """
        logger.info("生成旋律 (模擬)")
        
        # 創建模擬的旋律音符
        melody_notes = []
        
        # 如果有引導旋律，使用它作為起點
        if primer_melody:
            melody_notes.extend(primer_melody)
            last_note = primer_melody[-1]
            start_time = last_note.start_time + last_note.duration
        else:
            start_time = 0.0
        
        # 根據參數調整音符數量
        note_count = max(8, min(32, num_steps // 4))
        
        # 決定調性相關的音高範圍
        base_pitch = 60  # C4
        if hasattr(parameters, 'key') and parameters.key:
            key_name = parameters.key
            if key_name == 'C':  # C大調
                pitch_range = list(range(60, 72))  # C4 到 B4
            elif key_name == 'Am':  # A小調
                pitch_range = list(range(57, 69))  # A3 到 G#4
            else:
                pitch_range = list(range(57, 72))  # A3 到 B4
        else:
            pitch_range = list(range(57, 72))
            
        # 根據速度調整音符持續時間
        tempo = getattr(parameters, 'tempo', 120)
        beat_duration = 60 / tempo  # 一拍的持續時間(秒)
        
        # 基本持續時間選項
        durations = [0.25 * beat_duration, 0.5 * beat_duration, beat_duration]
        
        # 根據溫度參數調整隨機程度
        randomness = max(0.1, min(1.0, temperature))
        
        # 生成音符
        for i in range(note_count):
            # 變化音高，使用溫度參數調整隨機程度
            if randomness > 0.8:
                # 高隨機度
                pitch = random.choice(pitch_range)
            else:
                # 低隨機度，偏好音階上的音符
                scale = [0, 2, 4, 5, 7, 9, 11]  # C大調音階
                pitch_class = random.choice(scale)
                octave = random.choice([4, 5])  # C4-C6之間
                pitch = 60 + pitch_class + (octave - 4) * 12
            
            # 變化持續時間
            duration = random.choice(durations)
            
            # 力度
            velocity = random.randint(70, 90)
            
            # 創建音符
            note = Note(
                pitch=pitch,
                start_time=start_time,
                duration=duration,
                velocity=velocity
            )
            melody_notes.append(note)
            
            # 更新下一個音符的開始時間
            start_time += duration
        
        return melody_notes

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
            
        # 根據速度調整音符持續時間
        tempo = getattr(parameters, 'tempo', 120)
        beat_duration = 60 / tempo
            
        # 生成模擬的和弦音符
        chord_notes = []
        bass_notes = []
        
        # 簡單的和弦進行
        chord_progressions = [
            [60, 64, 67],  # C
            [57, 60, 64],  # Am
            [65, 69, 72],  # F
            [67, 71, 74]   # G
        ]
        
        # 生成和弦
        current_time = 0.0
        chord_duration = 4 * beat_duration  # 一個和弦持續4拍
        
        while current_time < total_duration:
            # 選擇和弦
            chord_index = int(current_time / chord_duration) % len(chord_progressions)
            chord = chord_progressions[chord_index]
            
            # 創建和弦音符
            for pitch in chord:
                chord_note = Note(
                    pitch=pitch,
                    start_time=current_time,
                    duration=chord_duration,
                    velocity=70
                )
                chord_notes.append(chord_note)
            
            # 創建低音音符
            bass_note = Note(
                pitch=chord[0] - 12,  # 低八度
                start_time=current_time,
                duration=chord_duration,
                velocity=80
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
            num_measures: 小節數

        Returns:
            List[Note]: 鼓點音符列表
        """
        logger.info("生成鼓點模式 (模擬)")
        
        # 根據速度調整音符持續時間
        tempo = getattr(parameters, 'tempo', 120)
        beat_duration = 60 / tempo
        
        # 標準鼓點音高
        kick = 36  # 大鼓
        snare = 38  # 小鼓
        hihat = 42  # 踩鈸
        
        drum_notes = []
        
        # 生成基本鼓點模式
        for measure in range(num_measures):
            for beat in range(4):  # 4/4拍
                time = (measure * 4 + beat) * beat_duration
                
                # 每拍大鼓
                if beat % 2 == 0:
                    drum_notes.append(Note(
                        pitch=kick,
                        start_time=time,
                        duration=0.1,
                        velocity=90
                    ))
                
                # 2、4拍小鼓
                if beat % 2 == 1:
                    drum_notes.append(Note(
                        pitch=snare,
                        start_time=time,
                        duration=0.1,
                        velocity=85
                    ))
                
                # 每1/8拍踩鈸
                for eighth in range(2):
                    drum_notes.append(Note(
                        pitch=hihat,
                        start_time=time + eighth * beat_duration/2,
                        duration=0.1,
                        velocity=70
                    ))
        
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
        logger.info("將旋律轉換為 MIDI (模擬)")
        
        # 創建臨時文件
        if not output_path:
            temp_dir = tempfile.gettempdir()
            output_path = os.path.join(temp_dir, f"melody_{int(random.random() * 1000)}.mid")
        
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
        
        # 如果沒有旋律，先生成一個
        if not melody:
            melody = self.generate_melody(params)
        
        # 生成伴奏
        accompaniment = self.generate_accompaniment(melody, params)
        
        # 生成鼓點
        drums = self.generate_drum_pattern(params)
        
        # 生成 MIDI 文件
        temp_dir = tempfile.gettempdir()
        midi_path = os.path.join(temp_dir, f"arrangement_{int(random.random() * 1000)}.mid")
        self.melody_to_midi(melody, midi_path, params.tempo or 120)
        
        # 返回結果
        return {
            "melody": melody,
            "chords": accompaniment["chords"],
            "bass": accompaniment["bass"],
            "drums": drums,
            "tempo": params.tempo or 120,
            "midi_path": midi_path,
            "models_used": suggested_models or ["mock_melody_generator", "mock_accompaniment_generator"]
        }

    def text_to_melody(self, text: str, parameters: MusicParameters) -> List[Note]:
        """根據文本描述生成旋律

        Args:
            text: 文本描述
            parameters: 音樂參數

        Returns:
            生成的旋律音符列表
        """
        logger.info(f"根據文本生成旋律 (模擬): {text}")
        
        # 從文本中提取關鍵情感特徵
        text_lower = text.lower()
        
        # 決定旋律特性
        is_energetic = any(word in text_lower for word in ["energetic", "exciting", "upbeat", "happy", "fast", "快樂", "興奮", "活力", "快速"])
        is_calm = any(word in text_lower for word in ["calm", "peaceful", "relaxing", "gentle", "quiet", "平靜", "和平", "放鬆", "溫柔", "安靜"])
        is_dark = any(word in text_lower for word in ["dark", "sad", "melancholy", "dramatic", "tense", "黑暗", "悲傷", "憂鬱", "戲劇性", "緊張"])
        
        # 根據情感特徵設置參數
        if is_energetic:
            # 快速、明亮的旋律
            if not hasattr(parameters, 'tempo') or not parameters.tempo:
                parameters.tempo = random.randint(120, 160)
            pitches = list(range(60, 84))  # 較高的音域
        elif is_calm:
            # 緩慢、柔和的旋律
            if not hasattr(parameters, 'tempo') or not parameters.tempo:
                parameters.tempo = random.randint(60, 90)
            pitches = list(range(55, 75))  # 中間音域
        elif is_dark:
            # 低沉、緩慢的旋律
            if not hasattr(parameters, 'tempo') or not parameters.tempo:
                parameters.tempo = random.randint(50, 80)
            pitches = list(range(48, 68))  # 較低的音域
        else:
            # 默認中等節奏
            if not hasattr(parameters, 'tempo') or not parameters.tempo:
                parameters.tempo = random.randint(90, 120)
            pitches = list(range(55, 79))  # 正常音域
        
        # 生成旋律
        beat_duration = 60 / parameters.tempo
        melody_notes = []
        
        # 決定音符數量
        note_count = random.randint(16, 32)
        
        # 調性和音階
        key_map = {
            'C': [0, 2, 4, 5, 7, 9, 11],    # C大調
            'Am': [0, 2, 3, 5, 7, 8, 10],   # A小調
            'G': [0, 2, 4, 6, 7, 9, 11],    # G大調
            'Em': [0, 2, 3, 5, 7, 8, 10],   # E小調
        }
        
        key = getattr(parameters, 'key', 'C')
        scale = key_map.get(key, key_map['C'])
        
        # 根據情感選擇模式
        if is_energetic:
            # 快節奏模式，較多短音符
            duration_choices = [0.25 * beat_duration, 0.5 * beat_duration]  
            pattern_type = "energetic"
        elif is_calm:
            # 平和模式，較多長音符
            duration_choices = [beat_duration, 2 * beat_duration]
            pattern_type = "calm"
        elif is_dark:
            # 低沉模式，較多中長音符
            duration_choices = [0.5 * beat_duration, beat_duration, 1.5 * beat_duration]
            pattern_type = "dark"
        else:
            # 平衡模式
            duration_choices = [0.25 * beat_duration, 0.5 * beat_duration, beat_duration]
            pattern_type = "balanced"
            
        start_time = 0.0
        for i in range(note_count):
            # 選擇符合調性的音高
            base_pitch = random.choice(pitches)
            pitch_class = base_pitch % 12
            while pitch_class not in scale:
                base_pitch += 1
                pitch_class = base_pitch % 12
            
            # 選擇持續時間
            duration = random.choice(duration_choices)
            
            # 根據模式決定力度
            if pattern_type == "energetic":
                velocity = random.randint(80, 100)
            elif pattern_type == "calm":
                velocity = random.randint(50, 70)
            elif pattern_type == "dark":
                velocity = random.randint(60, 85)
            else:
                velocity = random.randint(70, 90)
            
            # 創建音符
            note = Note(
                pitch=base_pitch,
                start_time=start_time,
                duration=duration,
                velocity=velocity
            )
            melody_notes.append(note)
            
            # 更新下一個音符的開始時間
            start_time += duration
            
        return melody_notes

    def create_audio_from_arrangement(self, 
                                     arrangement: Dict[str, List[Note]], 
                                     parameters: MusicParameters) -> str:
        """從編曲生成音頻

        Args:
            arrangement: 編曲，包含各個部分的音符
            parameters: 音樂參數

        Returns:
            Base64編碼的音頻數據
        """
        logger.info("從編曲生成音頻 (模擬)")
        
        # 對於模擬版本，返回一個空的音頻文件的Base64編碼
        # 真實實現應該創建並編碼一個實際的音頻文件
        mock_audio_data = base64.b64encode(b'MOCK_AUDIO_DATA').decode('utf-8')
        return mock_audio_data
    
    def generate_cover_image(self, 
                           melody: List[Note], 
                           parameters: MusicParameters) -> str:
        """生成音樂封面圖片

        Args:
            melody: 旋律音符列表
            parameters: 音樂參數

        Returns:
            Base64編碼的圖片數據
        """
        logger.info("生成音樂封面圖片 (模擬)")
        
        # 對於模擬版本，返回一個空的圖片文件的Base64編碼
        # 真實實現應該創建並編碼一個實際的圖片文件
        mock_image_data = base64.b64encode(b'MOCK_IMAGE_DATA').decode('utf-8')
        return mock_image_data 