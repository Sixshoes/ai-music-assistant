"""MIDI 數據轉換器

處理 MIDI 與其他格式之間的轉換
"""

import base64
import os
import tempfile
from typing import Dict, Any, List, Optional, BinaryIO, Union

from ..mcp_schema import Note, MelodyInput


class MIDIConverter:
    """MIDI 數據轉換器類別"""
    
    @staticmethod
    def note_to_midi_message(note: Note, channel: int = 0) -> List[Dict[str, Any]]:
        """將 Note 對象轉換為 MIDI 消息格式
        
        Args:
            note: Note 對象
            channel: MIDI 通道（0-15）
            
        Returns:
            List[Dict[str, Any]]: MIDI 消息列表，包含 note_on 和 note_off 事件
        """
        # 將秒轉換為 MIDI 時鐘刻度（假設 PPQ=480）
        ppq = 480
        ticks_per_second = ppq * 2  # 假設默認 tempo 為 120 BPM (2 beats/second)
        
        start_tick = int(note.start_time * ticks_per_second)
        end_tick = int((note.start_time + note.duration) * ticks_per_second)
        
        return [
            {
                "type": "note_on",
                "tick": start_tick,
                "channel": channel,
                "note": note.pitch,
                "velocity": note.velocity
            },
            {
                "type": "note_off",
                "tick": end_tick,
                "channel": channel,
                "note": note.pitch,
                "velocity": 0
            }
        ]
    
    @staticmethod
    def notes_to_midi_messages(notes: List[Note], channel: int = 0) -> List[Dict[str, Any]]:
        """將多個 Note 對象轉換為 MIDI 消息
        
        Args:
            notes: Note 對象列表
            channel: MIDI 通道（0-15）
            
        Returns:
            List[Dict[str, Any]]: MIDI 消息列表
        """
        messages = []
        for note in notes:
            messages.extend(MIDIConverter.note_to_midi_message(note, channel))
        
        # 按時間排序
        return sorted(messages, key=lambda m: m["tick"])
    
    @staticmethod
    def melody_to_midi_data(melody: MelodyInput) -> bytes:
        """將旋律轉換為 MIDI 二進制數據
        
        Args:
            melody: 旋律輸入
            
        Returns:
            bytes: MIDI 文件數據
        """
        # 實際實現需要使用 mido 或類似庫
        # 此處為模擬實現
        
        # 轉換為 MIDI 消息
        messages = MIDIConverter.notes_to_midi_messages(melody.notes)
        
        # 在實際實現中，會使用 mido 創建 MIDI 文件並寫入消息
        # 為模擬目的，返回虛構的 MIDI 數據
        return b'MThd\x00\x00\x00\x06\x00\x01\x00\x01\x01\xE0MTrk\x00\x00\x00\x0C\x00\x90\x40\x64\x83\x60\x80\x40\x00\x00\xFF\x2F\x00'
    
    @staticmethod
    def midi_data_to_base64(midi_data: bytes) -> str:
        """將 MIDI 數據轉換為 base64 編碼
        
        Args:
            midi_data: MIDI 二進制數據
            
        Returns:
            str: base64 編碼的 MIDI 數據
        """
        return base64.b64encode(midi_data).decode('utf-8')
    
    @staticmethod
    def base64_to_midi_data(base64_str: str) -> bytes:
        """將 base64 編碼的 MIDI 數據轉換為二進制
        
        Args:
            base64_str: base64 編碼的 MIDI 數據
            
        Returns:
            bytes: MIDI 二進制數據
        """
        return base64.b64decode(base64_str)
    
    @staticmethod
    def save_midi_to_temp_file(midi_data: bytes) -> str:
        """將 MIDI 數據保存為臨時文件
        
        Args:
            midi_data: MIDI 二進制數據
            
        Returns:
            str: 臨時文件路徑
        """
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, f"midi_file_{hash(midi_data)}.mid")
        
        with open(temp_file, "wb") as f:
            f.write(midi_data)
        
        return temp_file
    
    @staticmethod
    def extract_melody_from_midi(midi_data: bytes, track: int = 0) -> MelodyInput:
        """從 MIDI 數據中提取旋律
        
        Args:
            midi_data: MIDI 二進制數據
            track: 要提取的音軌索引
            
        Returns:
            MelodyInput: 提取的旋律
        """
        # 實際實現需要使用 mido 或類似庫解析 MIDI 文件
        # 此處為模擬實現
        
        # 為模擬目的，返回虛構的旋律
        notes = [
            Note(pitch=60, start_time=0.0, duration=0.5, velocity=80),
            Note(pitch=62, start_time=0.5, duration=0.5, velocity=80),
            Note(pitch=64, start_time=1.0, duration=1.0, velocity=80),
            Note(pitch=65, start_time=2.0, duration=0.5, velocity=80),
            Note(pitch=67, start_time=2.5, duration=1.5, velocity=80)
        ]
        
        return MelodyInput(notes=notes, tempo=120)
    
    @staticmethod
    def merge_midi_tracks(tracks: List[bytes]) -> bytes:
        """合併多個 MIDI 音軌
        
        Args:
            tracks: MIDI 數據列表，每個代表一個音軌
            
        Returns:
            bytes: 合併後的 MIDI 數據
        """
        # 實際實現需要使用 mido 或類似庫合併音軌
        # 此處為模擬實現
        return b'MThd\x00\x00\x00\x06\x00\x01\x00\x03\x01\xE0MTrk\x00\x00\x00\x0C\x00\x90\x40\x64\x83\x60\x80\x40\x00\x00\xFF\x2F\x00' 