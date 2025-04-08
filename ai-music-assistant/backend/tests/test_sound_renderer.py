"""測試音色渲染器"""

import unittest
import os
import numpy as np
from rendering.sound_renderer import SoundRenderer
import mido
from mido import Message

class TestSoundRenderer(unittest.TestCase):
    """測試音色渲染器"""
    
    def setUp(self):
        """設置測試環境"""
        self.renderer = SoundRenderer()
        self.test_output_dir = "test_output"
        os.makedirs(self.test_output_dir, exist_ok=True)
    
    def test_render_midi(self):
        """測試MIDI渲染"""
        # 創建測試MIDI數據
        midi_data = {
            "tempo": 120,
            "time_signature": "4/4",
            "instruments": {
                "piano": {
                    "notes": ["C4", "E4", "G4"],
                    "duration": 480
                }
            }
        }
        
        # 渲染MIDI
        output_path = os.path.join(self.test_output_dir, "test_piano.wav")
        result_path = self.renderer.render_midi(midi_data, output_path)
        
        # 驗證結果
        self.assertTrue(os.path.exists(result_path))
        self.assertTrue(result_path.endswith(".wav"))
    
    def test_realtime_rendering(self):
        """測試實時渲染"""
        # 啟動實時渲染
        self.renderer.start_realtime_rendering()
        
        # 播放一些音符
        self.renderer.send_realtime_message(
            Message('program_change', program=0)  # 鋼琴
        )
        
        # 播放C大調音階
        notes = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]
        for note in notes:
            note_number = self.renderer._note_to_midi(note)
            self.renderer.send_realtime_message(
                Message('note_on', note=note_number, velocity=64)
            )
            self.renderer.send_realtime_message(
                Message('note_off', note=note_number)
            )
        
        # 停止實時渲染
        self.renderer.stop_realtime_rendering()
    
    def test_instrument_mapping(self):
        """測試樂器映射"""
        # 測試一些樂器
        instruments = [
            "piano", "violin", "guitar", "trumpet", "flute",
            "electric_piano", "synth_bass", "choir"
        ]
        
        for instrument in instruments:
            program = self.renderer._get_instrument_program(instrument)
            self.assertIsInstance(program, int)
            self.assertTrue(0 <= program <= 128)
    
    def test_note_conversion(self):
        """測試音符轉換"""
        # 測試一些音符
        notes = ["C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4"]
        
        for note in notes:
            midi_number = self.renderer._note_to_midi(note)
            self.assertIsInstance(midi_number, int)
            self.assertTrue(0 <= midi_number <= 127)
    
    def tearDown(self):
        """清理測試環境"""
        # 停止實時渲染（如果正在運行）
        if hasattr(self.renderer, 'is_realtime_running') and self.renderer.is_realtime_running:
            self.renderer.stop_realtime_rendering()
        
        # 刪除測試輸出文件
        if os.path.exists(self.test_output_dir):
            for file in os.listdir(self.test_output_dir):
                os.remove(os.path.join(self.test_output_dir, file))
            os.rmdir(self.test_output_dir)

if __name__ == "__main__":
    unittest.main() 