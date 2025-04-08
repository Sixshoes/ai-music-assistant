"""Music VAE 服務模組

使用 Magenta 的 MusicVAE 模型進行旋律變奏和生成
"""

import os
import logging
import tempfile
from typing import Dict, Any, List, Optional, Tuple, Union

import numpy as np
import tensorflow as tf

# Magenta 相關依賴
from magenta.models.music_vae import configs
from magenta.models.music_vae.trained_model import TrainedModel
from magenta.music import midi_io
from magenta.music import constants
from magenta.music import sequences_lib
from magenta.music import note_sequence_utils
from magenta.music.protobuf import music_pb2

from ...mcp.mcp_schema import MusicParameters, Note

logger = logging.getLogger(__name__)


class MusicVAEService:
    """Music VAE 服務類別

    使用 Magenta 的 MusicVAE 模型進行旋律變奏和生成
    """

    def __init__(self, model_path_dict: Optional[Dict[str, str]] = None):
        """初始化 Music VAE 服務

        Args:
            model_path_dict: 模型路徑字典，如 {"cat_melody": "/path/to/model"}
        """
        self.model_path_dict = model_path_dict or {}
        self.models = {}
        self._initialize_models()

    def _initialize_models(self):
        """初始化 Music VAE 模型"""
        try:
            # 載入旋律變奏模型
            if "melody_16bar" in self.model_path_dict:
                melody_model_path = self.model_path_dict["melody_16bar"]
            else:
                # 使用默認模型
                melody_model_path = "https://storage.googleapis.com/magentadata/models/music_vae/checkpoints/mel_16bar_small.mag"
            
            config = configs.CONFIG_MAP["cat-mel_16bar"]
            self.models["melody_16bar"] = TrainedModel(
                config=config,
                batch_size=1,
                checkpoint_dir_or_path=melody_model_path
            )
            
            # 載入旋律插值模型
            if "melody_2bar" in self.model_path_dict:
                melody_2bar_model_path = self.model_path_dict["melody_2bar"]
            else:
                # 使用默認模型
                melody_2bar_model_path = "https://storage.googleapis.com/magentadata/models/music_vae/checkpoints/mel_2bar_small.mag"
            
            config_2bar = configs.CONFIG_MAP["cat-mel_2bar"]
            self.models["melody_2bar"] = TrainedModel(
                config=config_2bar,
                batch_size=1,
                checkpoint_dir_or_path=melody_2bar_model_path
            )
            
            # 載入鼓點變奏模型
            if "drums_2bar" in self.model_path_dict:
                drums_model_path = self.model_path_dict["drums_2bar"]
            else:
                # 使用默認模型
                drums_model_path = "https://storage.googleapis.com/magentadata/models/music_vae/checkpoints/drums_2bar_small.mag"
            
            config_drums = configs.CONFIG_MAP["cat-drums_2bar"]
            self.models["drums_2bar"] = TrainedModel(
                config=config_drums,
                batch_size=1,
                checkpoint_dir_or_path=drums_model_path
            )
            
            logger.info("成功初始化 Music VAE 模型")
        
        except Exception as e:
            logger.error(f"初始化 Music VAE 模型時出錯：{str(e)}", exc_info=True)
            raise

    def generate_variation(self, 
                          melody: List[Note], 
                          temperature: float = 0.5, 
                          variation_degree: float = 0.5) -> List[Note]:
        """生成旋律變奏

        Args:
            melody: 原始旋律音符列表
            temperature: 生成溫度，控制隨機性
            variation_degree: 變奏程度，0.0-1.0，越高變化越大

        Returns:
            List[Note]: 變奏後的旋律音符列表
        """
        try:
            logger.info(f"使用 Music VAE 生成旋律變奏，變奏程度: {variation_degree}")
            
            # 獲取 Music VAE 模型
            model = self.models.get("melody_16bar")
            if not model:
                raise ValueError("Music VAE 模型未初始化")
            
            # 將音符列表轉換為 NoteSequence
            sequence = self._notes_to_sequence(melody)
            
            # 確保序列長度合適
            if sequence.total_time > 16 * 4:  # 假設16小節，每小節4拍
                # 截斷序列
                sequence = sequences_lib.trim_note_sequence(sequence, 0, 16 * 4)
            elif sequence.total_time < 16 * 4:
                # 延長序列
                sequence = self._extend_sequence(sequence, 16 * 4)
            
            # 轉換為模型輸入格式
            try:
                z, _ = model.encode([sequence])
            except:
                logger.warning("無法直接編碼序列，可能需要預處理")
                sequence = sequences_lib.quantize_note_sequence(
                    sequence, steps_per_quarter=4
                )
                z, _ = model.encode([sequence])
            
            # 應用變奏程度
            if variation_degree > 0:
                z_noise = np.random.normal(0, 1, z.shape)
                z = z * (1 - variation_degree) + z_noise * variation_degree
            
            # 解碼生成新序列
            outputs = model.decode(
                z,
                length=256,  # 16小節，每小節16步
                temperature=temperature
            )
            
            # 轉換回音符列表
            varied_notes = self._sequence_to_notes(outputs[0])
            
            logger.info(f"成功生成旋律變奏，原始旋律 {len(melody)} 個音符，變奏後 {len(varied_notes)} 個音符")
            return varied_notes
            
        except Exception as e:
            logger.error(f"生成旋律變奏時出錯：{str(e)}", exc_info=True)
            # 如果生成失敗，返回原始旋律
            return melody

    def interpolate_melodies(self,
                           melody1: List[Note],
                           melody2: List[Note],
                           num_steps: int = 5) -> List[List[Note]]:
        """在兩個旋律之間插值生成過渡

        Args:
            melody1: 第一個旋律音符列表
            melody2: 第二個旋律音符列表
            num_steps: 生成的過渡步數

        Returns:
            List[List[Note]]: 插值生成的旋律列表，包含從 melody1 到 melody2 的平滑過渡
        """
        try:
            logger.info(f"在兩個旋律之間生成 {num_steps} 步插值過渡")
            
            # 獲取 Music VAE 模型
            model = self.models.get("melody_2bar")
            if not model:
                raise ValueError("Music VAE 2bar 模型未初始化")
            
            # 將音符列表轉換為 NoteSequence
            sequence1 = self._notes_to_sequence(melody1)
            sequence2 = self._notes_to_sequence(melody2)
            
            # 量化並調整序列長度
            sequence1 = sequences_lib.quantize_note_sequence(sequence1, steps_per_quarter=4)
            sequence2 = sequences_lib.quantize_note_sequence(sequence2, steps_per_quarter=4)
            
            # 確保長度合適（2小節）
            if sequence1.total_time > 2 * 4:
                sequence1 = sequences_lib.trim_note_sequence(sequence1, 0, 2 * 4)
            elif sequence1.total_time < 2 * 4:
                sequence1 = self._extend_sequence(sequence1, 2 * 4)
                
            if sequence2.total_time > 2 * 4:
                sequence2 = sequences_lib.trim_note_sequence(sequence2, 0, 2 * 4)
            elif sequence2.total_time < 2 * 4:
                sequence2 = self._extend_sequence(sequence2, 2 * 4)
            
            # 編碼兩個序列
            try:
                z1, _ = model.encode([sequence1])
                z2, _ = model.encode([sequence2])
            except:
                logger.warning("無法直接編碼序列，檢查序列長度和格式")
                return [melody1] + [melody1] * (num_steps - 2) + [melody2]
            
            # 在潛在空間中插值
            interpolated_z = []
            for i in range(num_steps):
                t = i / (num_steps - 1) if num_steps > 1 else 0
                zi = z1 * (1 - t) + z2 * t
                interpolated_z.append(zi)
            
            # 解碼生成插值序列
            interpolated_sequences = model.decode(
                np.vstack(interpolated_z),
                length=32,  # 2小節，每小節16步
                temperature=0.5
            )
            
            # 轉換為音符列表
            interpolated_melodies = [
                self._sequence_to_notes(seq) for seq in interpolated_sequences
            ]
            
            logger.info(f"成功生成 {len(interpolated_melodies)} 個插值旋律")
            return interpolated_melodies
            
        except Exception as e:
            logger.error(f"生成旋律插值時出錯：{str(e)}", exc_info=True)
            # 如果生成失敗，返回簡單的線性插值
            return [melody1] + [melody1] * (num_steps - 2) + [melody2]

    def generate_drums(self, 
                      num_measures: int = 4, 
                      temperature: float = 1.0) -> List[Note]:
        """生成鼓點模式

        Args:
            num_measures: 小節數
            temperature: 生成溫度，控制隨機性

        Returns:
            List[Note]: 生成的鼓點音符列表
        """
        try:
            logger.info(f"使用 Music VAE 生成 {num_measures} 小節鼓點模式")
            
            # 獲取鼓點模型
            model = self.models.get("drums_2bar")
            if not model:
                raise ValueError("鼓點模型未初始化")
            
            # 生成隨機潛在向量
            z = np.random.normal(0, 0.5, [num_measures // 2, model.z_size])
            
            # 生成鼓點序列
            outputs = model.decode(
                z,
                length=32,  # 2小節，每小節16步
                temperature=temperature
            )
            
            # 合併多個2小節的鼓點片段為完整序列
            complete_sequence = music_pb2.NoteSequence()
            complete_sequence.tempos.add().qpm = 120
            complete_sequence.ticks_per_quarter = constants.STANDARD_PPQ
            
            current_time = 0
            for i, seq in enumerate(outputs):
                for note in seq.notes:
                    new_note = complete_sequence.notes.add()
                    new_note.pitch = note.pitch
                    new_note.velocity = note.velocity
                    new_note.start_time = note.start_time + current_time
                    new_note.end_time = note.end_time + current_time
                    new_note.is_drum = True
                    
                # 更新當前時間
                current_time += 2 * 4  # 2小節 × 4拍/小節
            
            complete_sequence.total_time = current_time
            
            # 轉換為音符列表
            drum_notes = self._sequence_to_notes(complete_sequence)
            
            logger.info(f"成功生成 {len(drum_notes)} 個鼓點音符")
            return drum_notes
            
        except Exception as e:
            logger.error(f"生成鼓點模式時出錯：{str(e)}", exc_info=True)
            # 如果生成失敗，返回簡單的鼓點模式
            return self._generate_simple_drum_pattern(num_measures)

    def _notes_to_sequence(self, notes: List[Note]) -> music_pb2.NoteSequence:
        """將音符列表轉換為 NoteSequence

        Args:
            notes: 音符列表

        Returns:
            music_pb2.NoteSequence: 轉換後的 NoteSequence
        """
        sequence = music_pb2.NoteSequence()
        sequence.tempos.add().qpm = 120
        sequence.ticks_per_quarter = constants.STANDARD_PPQ
        
        end_time = 0
        for note in notes:
            sequence_note = sequence.notes.add()
            sequence_note.pitch = note.pitch
            sequence_note.start_time = note.start_time
            sequence_note.end_time = note.start_time + note.duration
            sequence_note.velocity = note.velocity
            sequence_note.instrument = 0
            sequence_note.program = 0
            
            end_time = max(end_time, sequence_note.end_time)
        
        sequence.total_time = end_time
        return sequence

    def _sequence_to_notes(self, sequence: music_pb2.NoteSequence) -> List[Note]:
        """將 NoteSequence 轉換為音符列表

        Args:
            sequence: NoteSequence

        Returns:
            List[Note]: 轉換後的音符列表
        """
        notes = []
        for seq_note in sequence.notes:
            note = Note(
                pitch=seq_note.pitch,
                start_time=seq_note.start_time,
                duration=seq_note.end_time - seq_note.start_time,
                velocity=seq_note.velocity
            )
            notes.append(note)
        
        # 按開始時間排序
        notes.sort(key=lambda x: x.start_time)
        return notes

    def _extend_sequence(self, sequence: music_pb2.NoteSequence, target_length: float) -> music_pb2.NoteSequence:
        """延長序列到目標長度

        Args:
            sequence: 原始 NoteSequence
            target_length: 目標長度（拍數）

        Returns:
            music_pb2.NoteSequence: 延長後的 NoteSequence
        """
        if sequence.total_time >= target_length:
            return sequence
        
        # 創建新序列
        extended_sequence = music_pb2.NoteSequence()
        extended_sequence.CopyFrom(sequence)
        
        # 計算需要重複的次數
        repetitions = int(target_length / sequence.total_time) + 1
        
        # 擴展序列
        original_notes = list(sequence.notes)
        original_end_time = sequence.total_time
        
        for rep in range(1, repetitions):
            for original_note in original_notes:
                new_note = extended_sequence.notes.add()
                new_note.CopyFrom(original_note)
                new_note.start_time += rep * original_end_time
                new_note.end_time += rep * original_end_time
                
        extended_sequence.total_time = repetitions * original_end_time
        
        # 如果超出目標長度，裁剪
        if extended_sequence.total_time > target_length:
            extended_sequence = sequences_lib.trim_note_sequence(
                extended_sequence, 0, target_length
            )
        
        return extended_sequence

    def _generate_simple_drum_pattern(self, num_measures: int) -> List[Note]:
        """生成簡單的鼓點模式

        當主要生成方法失敗時使用的後備方法

        Args:
            num_measures: 小節數

        Returns:
            List[Note]: 生成的鼓點音符列表
        """
        # 簡單的鼓點模式：每拍踢鼓，每個偶數拍軍鼓，每 1/8 拍打一次踩鈸
        drum_notes = []
        beats_per_measure = 4  # 假設 4/4 拍
        seconds_per_beat = 60.0 / 120  # 假設 120 BPM
        
        for measure in range(num_measures):
            for beat in range(beats_per_measure):
                beat_time = measure * beats_per_measure * seconds_per_beat + beat * seconds_per_beat
                
                # 踢鼓（bass drum）- MIDI 音符 36
                kick = Note(
                    pitch=36,
                    start_time=beat_time,
                    duration=0.1,
                    velocity=100 if beat == 0 else 80
                )
                drum_notes.append(kick)
                
                # 軍鼓（snare drum）- MIDI 音符 38，在每個偶數拍上
                if beat % 2 == 1:
                    snare = Note(
                        pitch=38,
                        start_time=beat_time,
                        duration=0.1,
                        velocity=90
                    )
                    drum_notes.append(snare)
                
                # 踩鈸（hi-hat）- MIDI 音符 42，每 1/8 拍
                for i in range(2):
                    hi_hat_time = beat_time + i * seconds_per_beat / 2
                    hi_hat = Note(
                        pitch=42,
                        start_time=hi_hat_time,
                        duration=0.1,
                        velocity=70 if i == 0 else 50
                    )
                    drum_notes.append(hi_hat)
        
        return drum_notes 