"""Performance RNN 服務模組

使用 Magenta 的 Performance RNN 模型生成富有表現力的音樂演奏
"""

import os
import logging
import tempfile
from typing import Dict, Any, List, Optional, Tuple, Union

import numpy as np
import tensorflow as tf

# Magenta 相關依賴
from magenta.models.performance_rnn import performance_sequence_generator
from magenta.models.performance_rnn import performance_model
from magenta.models.shared import sequence_generator_bundle
from magenta.music import constants
from magenta.music import midi_io
from magenta.music import sequences_lib
from magenta.music.protobuf import generator_pb2
from magenta.music.protobuf import music_pb2
from magenta.music import performance_lib

from ...mcp.mcp_schema import MusicParameters, Note

logger = logging.getLogger(__name__)


class PerformanceRNNService:
    """Performance RNN 服務類別

    使用 Magenta 的 Performance RNN 模型生成富有表現力的音樂演奏
    """

    def __init__(self, model_path_dict: Optional[Dict[str, str]] = None):
        """初始化 Performance RNN 服務

        Args:
            model_path_dict: 模型路徑字典，如 {"performance_with_dynamics": "/path/to/model"}
        """
        self.model_path_dict = model_path_dict or {}
        self.models = {}
        self._initialize_models()

    def _initialize_models(self):
        """初始化 Performance RNN 模型"""
        try:
            # 載入標準演奏模型
            if "performance" in self.model_path_dict:
                performance_model_path = self.model_path_dict["performance"]
            else:
                # 使用默認模型
                performance_model_path = "https://storage.googleapis.com/magentadata/models/performance_rnn/tfjs/mono_rnn"
            
            bundle = sequence_generator_bundle.read_bundle_file(performance_model_path)
            generator_map = performance_sequence_generator.get_generator_map()
            performance_model = performance_sequence_generator.PerformanceRnnSequenceGenerator(
                model=generator_map['performance'](checkpoint=None, bundle=bundle),
                details=performance_sequence_generator.DETAILS,
                steps_per_second=performance_lib.DEFAULT_STEPS_PER_SECOND,
                num_velocity_bins=0,
                min_note=constants.MIN_MIDI_PITCH,
                max_note=constants.MAX_MIDI_PITCH
            )
            
            self.models["performance"] = performance_model
            
            # 載入帶有表情的演奏模型
            if "performance_with_dynamics" in self.model_path_dict:
                performance_dynamics_model_path = self.model_path_dict["performance_with_dynamics"]
            else:
                # 使用默認模型
                performance_dynamics_model_path = "https://storage.googleapis.com/magentadata/models/performance_rnn/tfjs/dynamics_rnn"
            
            bundle = sequence_generator_bundle.read_bundle_file(performance_dynamics_model_path)
            performance_dynamics_model = performance_sequence_generator.PerformanceRnnSequenceGenerator(
                model=generator_map['performance_with_dynamics'](checkpoint=None, bundle=bundle),
                details=performance_sequence_generator.DETAILS,
                steps_per_second=performance_lib.DEFAULT_STEPS_PER_SECOND,
                num_velocity_bins=32,
                min_note=constants.MIN_MIDI_PITCH,
                max_note=constants.MAX_MIDI_PITCH
            )
            
            self.models["performance_with_dynamics"] = performance_dynamics_model
            
            logger.info("成功初始化 Performance RNN 模型")
        
        except Exception as e:
            logger.error(f"初始化 Performance RNN 模型時出錯：{str(e)}", exc_info=True)
            raise

    def generate_performance(self, 
                           primer_melody: Optional[List[Note]] = None,
                           parameters: Optional[MusicParameters] = None,
                           style: str = "default",
                           duration: float = 30.0,
                           temperature: float = 1.0) -> List[Note]:
        """生成富有表現力的演奏

        Args:
            primer_melody: 引導旋律，如未提供則自動生成
            parameters: 音樂參數
            style: 演奏風格，如 "default", "expressive", "virtuosic"
            duration: 生成演奏的長度（秒）
            temperature: 生成溫度參數，控制隨機性

        Returns:
            List[Note]: 生成的演奏音符列表
        """
        try:
            logger.info(f"使用 Performance RNN 生成 {style} 風格的演奏")
            
            # 根據風格選擇模型
            model_key = "performance"
            if style.lower() in ["expressive", "dynamic", "dynamics"]:
                model_key = "performance_with_dynamics"
            
            # 獲取模型
            model = self.models.get(model_key)
            if not model:
                raise ValueError(f"未找到 {model_key} 模型")
            
            # 創建或使用引導序列
            if primer_melody and len(primer_melody) > 0:
                # 如果提供了引導旋律，使用它
                primer_sequence = self._notes_to_sequence(primer_melody)
            else:
                # 創建簡單的引導序列
                primer_sequence = music_pb2.NoteSequence()
                primer_sequence.tempos.add().qpm = parameters.tempo if parameters and parameters.tempo else 120
                primer_sequence.ticks_per_quarter = constants.STANDARD_PPQ
                
                # 添加簡單的 C 大調音階作為引導
                for i in range(4):
                    seq_note = primer_sequence.notes.add()
                    seq_note.pitch = 60 + i  # C4, D4, E4, F4
                    seq_note.start_time = i * 0.5
                    seq_note.end_time = (i + 1) * 0.5
                    seq_note.velocity = 80
                    seq_note.instrument = 0
                    seq_note.program = 0
                
                primer_sequence.total_time = 2.0
            
            # 設置生成參數
            qpm = parameters.tempo if parameters and parameters.tempo else 120
            seconds_per_step = 1.0 / performance_lib.DEFAULT_STEPS_PER_SECOND
            
            # 設置生成選項
            generator_options = generator_pb2.GeneratorOptions()
            generator_options.args['temperature'].float_value = temperature
            generator_options.args['beam_size'].int_value = 1
            generator_options.args['branch_factor'].int_value = 1
            generator_options.args['steps_per_iteration'].int_value = 1
            
            # 確保引導序列有有效的 tempo
            if not primer_sequence.tempos:
                primer_sequence.tempos.add().qpm = qpm
                
            # 設置演奏的總長度
            performance_seconds = duration
            generator_options.generate_sections.add(
                start_time=primer_sequence.total_time,
                end_time=performance_seconds
            )
            
            # 調整風格相關參數
            if style.lower() == "virtuosic":
                # 使用更高的溫度，產生更複雜的演奏
                generator_options.args['temperature'].float_value = max(0.8, temperature * 1.3)
            elif style.lower() == "gentle":
                # 使用較低的溫度，產生更平穩的演奏
                generator_options.args['temperature'].float_value = min(1.0, temperature * 0.7)
            
            # 生成演奏序列
            generated_sequence = model.generate(primer_sequence, generator_options)
            
            # 轉換為音符列表
            performance_notes = self._sequence_to_notes(generated_sequence)
            
            logger.info(f"成功生成演奏，共 {len(performance_notes)} 個音符")
            return performance_notes
            
        except Exception as e:
            logger.error(f"生成演奏時出錯：{str(e)}", exc_info=True)
            # 如果生成失敗，返回原始引導旋律或簡單音符
            if primer_melody:
                return primer_melody
            else:
                return self._generate_simple_melody()

    def apply_performance_style(self, 
                              melody: List[Note], 
                              style: str = "default", 
                              temperature: float = 1.0) -> List[Note]:
        """將演奏風格應用到現有旋律

        Args:
            melody: 原始旋律音符列表
            style: 演奏風格，如 "default", "expressive", "virtuosic"
            temperature: 生成溫度參數，控制隨機性

        Returns:
            List[Note]: 應用演奏風格後的音符列表
        """
        try:
            logger.info(f"將 {style} 演奏風格應用到旋律")
            
            # 將原始旋律轉換為序列作為引導
            primer_sequence = self._notes_to_sequence(melody)
            
            # 獲取原始旋律的持續時間
            melody_duration = max([note.start_time + note.duration for note in melody])
            
            # 將演奏風格應用到旋律
            return self.generate_performance(
                primer_melody=melody,
                style=style,
                duration=melody_duration * 1.1,  # 稍微延長一點
                temperature=temperature
            )
            
        except Exception as e:
            logger.error(f"應用演奏風格時出錯：{str(e)}", exc_info=True)
            # 如果應用失敗，返回原始旋律
            return melody

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

    def _generate_simple_melody(self) -> List[Note]:
        """生成簡單的旋律

        當主要生成方法失敗時使用的後備方法

        Returns:
            List[Note]: 生成的簡單旋律
        """
        # C 大調音階
        notes = []
        pitches = [60, 62, 64, 65, 67, 69, 71, 72]  # C4 to C5
        
        for i, pitch in enumerate(pitches):
            note = Note(
                pitch=pitch,
                start_time=i * 0.5,
                duration=0.4,
                velocity=80
            )
            notes.append(note)
        
        return notes

    def performance_to_midi(self, notes: List[Note], output_path: str, tempo: int = 120) -> str:
        """將演奏音符轉換為 MIDI 文件

        Args:
            notes: 演奏音符列表
            output_path: 輸出 MIDI 文件路徑
            tempo: 速度 (BPM)

        Returns:
            str: 輸出 MIDI 文件路徑
        """
        try:
            # 創建 NoteSequence
            sequence = music_pb2.NoteSequence()
            sequence.tempos.add().qpm = tempo
            sequence.ticks_per_quarter = constants.STANDARD_PPQ
            
            for note in notes:
                sequence_note = sequence.notes.add()
                sequence_note.pitch = note.pitch
                sequence_note.start_time = note.start_time
                sequence_note.end_time = note.start_time + note.duration
                sequence_note.velocity = note.velocity
                sequence_note.instrument = 0
                sequence_note.program = 0
            
            if notes:
                sequence.total_time = max(note.start_time + note.duration for note in notes)
            else:
                sequence.total_time = 0
            
            # 量化序列以確保正確的 MIDI 時序
            quantized_sequence = sequences_lib.quantize_note_sequence(
                sequence, steps_per_quarter=4
            )
            
            # 將 NoteSequence 轉換為 MIDI 文件
            midi_io.sequence_proto_to_midi_file(quantized_sequence, output_path)
            
            return output_path
        
        except Exception as e:
            logger.error(f"將演奏轉換為 MIDI 時出錯：{str(e)}", exc_info=True)
            raise 