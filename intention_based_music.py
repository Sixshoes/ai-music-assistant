#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
意圖驅動的音樂創作
基於用戶意圖理解生成音樂的三階段流程實現
"""

import os
import sys
import json
import time
import logging
import argparse
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import random

# 配置日誌
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 嘗試導入MIDI工具
try:
    from midiutil import MIDIFile
except ImportError:
    logger.error("缺少midiutil套件，請執行: pip install midiutil")
    sys.exit(1)
    
try:
    import pygame
except ImportError:
    logger.warning("缺少pygame套件，無法播放MIDI。若要播放，請執行: pip install pygame")

# 導入現有的參數和和聲處理模組
try:
    from music_parameters import MusicParameters
    from music_harmony import HarmonyAnalyzer, BassLineGenerator
except ImportError:
    logger.error("找不到音樂參數模組，請確保music_parameters.py和music_harmony.py在當前目錄")
    sys.exit(1)

class Note:
    """音符類"""
    def __init__(self, pitch: int, start_time: float, duration: float, velocity: int = 100):
        self.pitch = pitch  # MIDI音高
        self.start_time = start_time  # 開始時間(拍)
        self.duration = duration  # 持續時間(拍)
        self.velocity = velocity  # 力度(0-127)

class MusicRequirement:
    """音樂需求參數"""
    def __init__(self, description: str, genre: str = "古典", mood: str = "平靜", 
                 tempo: int = 100, key: str = "C", instruments=None):
        self.description = description
        self.genre = genre
        self.mood = mood
        self.tempo = tempo
        self.key = key
        self.time_signature = "4/4"
        self.form = "binary"
        self.duration = 60
        self.section_count = 2
        self.cultural_elements = []
        self.instruments = instruments or ["piano"]
        self.techniques = []
        self.melodic_character = "flowing"
        self.harmonic_complexity = "moderate"
        self.rhythmic_features = "regular"
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "description": self.description,
            "genre": self.genre,
            "mood": self.mood,
            "tempo": self.tempo,
            "key": self.key,
            "time_signature": self.time_signature,
            "form": self.form,
            "duration": self.duration,
            "section_count": self.section_count,
            "cultural_elements": self.cultural_elements,
            "instruments": self.instruments,
            "techniques": self.techniques,
            "melodic_character": self.melodic_character,
            "harmonic_complexity": self.harmonic_complexity,
            "rhythmic_features": self.rhythmic_features
        }

class MusicIntentionAnalyzer:
    """音樂意圖分析器 - 簡化版，不依賴外部API"""
    
    def analyze_intention(self, description: str) -> MusicRequirement:
        """分析用戶意圖並返回音樂需求
        
        由於沒有外部API，這裡提供一個簡單的文本分析實現
        
        Args:
            description: 用戶描述
            
        Returns:
            MusicRequirement: 音樂需求
        """
        # 創建基本需求
        req = MusicRequirement(description)
        
        # 分析文本意圖 - 風格判斷
        description = description.lower()
        
        # 識別風格
        if "古典" in description or "交響" in description or "室內樂" in description:
            req.genre = "古典"
        elif "爵士" in description or "藍調" in description or "搖擺" in description:
            req.genre = "爵士"
        elif "流行" in description or "現代" in description or "通俗" in description:
            req.genre = "流行"
        elif "電子" in description or "舞曲" in description or "節拍" in description:
            req.genre = "電子"
        elif "搖滾" in description or "rock" in description:
            req.genre = "搖滾"
        elif "民謠" in description or "民歌" in description or "傳統" in description:
            req.genre = "民謠"
        
        # 識別情感
        if any(word in description for word in ["快樂", "歡快", "歡樂", "輕快", "喜悅"]):
            req.mood = "快樂"
        elif any(word in description for word in ["悲傷", "憂鬱", "傷感", "憂愁", "哀愁"]):
            req.mood = "悲傷"
        elif any(word in description for word in ["激動", "激昂", "熱烈", "熱情", "活潑"]):
            req.mood = "激動"
        elif any(word in description for word in ["平靜", "安詳", "寧靜", "沉思", "冥想", "放鬆"]):
            req.mood = "平靜"
        
        # 識別速度
        if any(word in description for word in ["快速", "快節奏", "急促", "活躍"]):
            req.tempo = random.randint(120, 160)
        elif any(word in description for word in ["中速", "適中", "中等"]):
            req.tempo = random.randint(90, 120)
        elif any(word in description for word in ["慢速", "緩慢", "從容", "悠閒"]):
            req.tempo = random.randint(60, 90)
        
        # 識別樂器
        instruments = []
        instrument_keywords = {
            "鋼琴": "piano", "吉他": "guitar", "小提琴": "violin", 
            "大提琴": "cello", "長笛": "flute", "單簧管": "clarinet",
            "雙簧管": "oboe", "薩克斯": "saxophone", "小號": "trumpet",
            "法國號": "french_horn", "長號": "trombone", "鼓": "drums",
            "電貝斯": "bass", "古箏": "guzheng", "琵琶": "pipa",
            "笛子": "dizi", "二胡": "erhu"
        }
        
        for zh_name, en_name in instrument_keywords.items():
            if zh_name in description:
                instruments.append(en_name)
        
        if instruments:
            req.instruments = instruments
        
        # 識別文化元素
        cultural_elements = []
        if any(word in description for word in ["中國", "東方", "古箏", "笛子", "琵琶", "二胡"]):
            cultural_elements.append("Chinese")
        elif any(word in description for word in ["日本", "和風", "三味線", "尺八"]):
            cultural_elements.append("Japanese")
        elif any(word in description for word in ["西班牙", "佛朗明哥", "弗拉門戈"]):
            cultural_elements.append("Spanish")
        
        if cultural_elements:
            req.cultural_elements = cultural_elements
        
        # 調整其他參數
        if "複雜" in description or "豐富" in description:
            req.harmonic_complexity = "complex"
        
        if "簡單" in description or "簡約" in description:
            req.harmonic_complexity = "simple"
        
        if "不規則" in description or "變化" in description:
            req.rhythmic_features = "irregular"
        
        return req

class MusicCreator:
    """音樂創作器"""
    
    def __init__(self):
        """初始化音樂創作器"""
        pass
    
    def create_music_from_intention(self, description: str, output_path: str, play: bool = False) -> Dict[str, Any]:
        """基於意圖創作音樂
        
        三階段流程：
        1. 分析意圖
        2. 生成參數
        3. 創作音樂
        
        Args:
            description: 用戶描述
            output_path: 輸出路徑
            play: 是否播放生成的音樂
            
        Returns:
            Dict: 包含創作過程和結果的字典
        """
        # 記錄整個過程
        result = {
            "original_description": description,
            "stages": {}
        }
        
        # 第一階段：分析意圖
        logger.info(f"第一階段：分析音樂意圖 - {description}")
        analyzer = MusicIntentionAnalyzer()
        music_req = analyzer.analyze_intention(description)
        result["stages"]["intention_analysis"] = music_req.to_dict()
        
        logger.info(f"意圖分析結果: ")
        logger.info(f"  風格: {music_req.genre}")
        logger.info(f"  情感: {music_req.mood}")
        logger.info(f"  速度: {music_req.tempo}")
        logger.info(f"  樂器: {', '.join(music_req.instruments)}")
        if music_req.cultural_elements:
            logger.info(f"  文化元素: {', '.join(music_req.cultural_elements)}")
        
        # 第二階段：生成參數
        logger.info(f"第二階段：生成音樂參數")
        
        # 從意圖創建音樂參數
        style_mapping = {
            "古典": "古典",
            "爵士": "爵士",
            "流行": "流行",
            "電子": "電子",
            "搖滾": "流行",  # 映射到流行
            "民謠": "流行"   # 映射到流行
        }
        
        # 創建音樂參數
        music_style = style_mapping.get(music_req.genre, "古典")
        music_params = MusicParameters(music_style)
        music_params.apply_emotion(music_req.mood)
        
        # 設置速度
        tempo_range = (music_req.tempo - 10, music_req.tempo + 10)
        music_params.set_param("tempo_range", tempo_range)
        music_params.set_param("tempo", music_req.tempo)
        
        # 輸出生成的參數
        logger.info(f"生成的音樂參數:")
        logger.info(f"  風格: {music_style}")
        logger.info(f"  情感: {music_req.mood}")
        logger.info(f"  速度: {music_params.get_param('tempo')}")
        logger.info(f"  音階: {music_params.get_param('scale')}")
        
        result["stages"]["parameter_generation"] = {
            "style": music_style,
            "emotion": music_req.mood,
            "tempo": music_params.get_param("tempo"),
            "scale": music_params.get_param("scale"),
            "harmonic_complexity": music_params.get_param("harmonic_complexity", 0.5),
            "rhythmic_regularity": music_params.get_param("rhythmic_regularity", 0.7)
        }
        
        # 第三階段：創作音樂
        logger.info(f"第三階段：創作音樂")
        
        # 生成和弦進行
        chord_progression = music_params.get_chord_progression()
        logger.info(f"生成和弦進行: {len(chord_progression)}個和弦")
        
        # 確保和弦中的所有音符都是整數
        chord_progression = [[int(note) for note in chord] for chord in chord_progression]
        
        # 生成旋律
        melody_notes = self.generate_melody(music_params, chord_progression)
        logger.info(f"生成旋律: {len(melody_notes)}個音符")
        
        # 確保所有旋律音符都是整數
        melody_notes = [int(note) if isinstance(note, (int, float)) else note for note in melody_notes]
        
        # 生成低音聲部
        # bass_generator = BassLineGenerator(music_params)
        # bass_notes = bass_generator.create_bass_line(chord_progression)
        # logger.info(f"生成低音聲部: {len(bass_notes)}個音符")
        
        # 自行生成低音聲部 - 簡單使用和弦根音
        bass_notes = []
        for chord in chord_progression:
            # 獲取和弦根音並降低一個八度
            root = chord[0] - 12
            bass_notes.append(root)
        
        # 擴展低音聲部以匹配旋律長度
        while len(bass_notes) < len(melody_notes):
            bass_notes.extend(bass_notes)
        bass_notes = bass_notes[:len(melody_notes)]
        
        logger.info(f"生成低音聲部: {len(bass_notes)}個音符")
        
        # 轉換為標準格式
        melody = []
        for i, note in enumerate(melody_notes):
            melody.append(Note(
                pitch=note,
                start_time=i,
                duration=1.0,
                velocity=80 + random.randint(-10, 10)
            ))
        
        chords = []
        for i, chord in enumerate(chord_progression):
            chords.append({
                "start_time": i * 4.0,  # 每四拍一個和弦
                "duration": 4.0,
                "notes": chord
            })
        
        bass = []
        for i, note in enumerate(bass_notes):
            bass.append(Note(
                pitch=note,
                start_time=i,
                duration=1.0,
                velocity=70 + random.randint(-5, 5)
            ))
        
        # 保存結果
        result["stages"]["music_creation"] = {
            "melody": [{"pitch": n.pitch, "start_time": n.start_time, "duration": n.duration, "velocity": n.velocity} for n in melody],
            "chords": chords,
            "bass": [{"pitch": n.pitch, "start_time": n.start_time, "duration": n.duration, "velocity": n.velocity} for n in bass]
        }
        
        # 保存為MIDI
        midi_path = self.save_to_midi(melody, chords, bass, music_params.get_param("tempo"), output_path)
        result["output_file"] = midi_path
        
        # 播放音樂
        if play:
            self.play_midi(midi_path)
        
        return result
    
    def generate_melody(self, music_params, chord_progression, length=32) -> List[int]:
        """基於參數生成旋律
        
        Args:
            music_params: 音樂參數
            chord_progression: 和弦進行
            length: 旋律長度
            
        Returns:
            List[int]: 旋律音符
        """
        melody = []
        
        # 獲取音階和調式
        scale = music_params.get_param("scale", "大調")
        scale_notes = music_params.get_scale_notes()
        
        # 旋律輪廓類型
        contour = music_params.get_param("melodic_contour", "arch")
        
        # 根據輪廓生成方向趨勢
        directions = []
        if contour == "arch":
            # 拱形：上升然後下降
            mid_point = length // 2
            for i in range(length):
                if i < mid_point:
                    directions.append(1)  # 上升
                else:
                    directions.append(-1)  # 下降
        elif contour == "wave":
            # 波浪形：上下交替
            section_length = 4
            for i in range(length):
                section = (i // section_length) % 2
                if section == 0:
                    directions.append(1)  # 上升
                else:
                    directions.append(-1)  # 下降
        else:
            # 默認為隨機方向
            directions = [random.choice([-1, 0, 1]) for _ in range(length)]
        
        # 從首個和弦的音符開始
        if chord_progression and len(chord_progression) > 0:
            # 選擇和弦的根音或三音作為開始
            start_options = [chord_progression[0][0] % 12]
            if len(chord_progression[0]) >= 3:
                start_options.append(chord_progression[0][2] % 12)
            
            # 選擇一個八度
            octave = 5
            start_note = random.choice(start_options) + (octave * 12)
        else:
            # 無和弦時使用音階的調性音開始
            start_note = scale_notes[0]
        
        melody.append(start_note)
        
        # 和聲複雜度影響和弦外音的使用
        harmonic_complexity = music_params.get_param("harmonic_complexity", 0.5)
        chord_tone_preference = 1.0 - harmonic_complexity  # 越複雜越少使用和弦音
        
        # 節奏的規律性
        rhythmic_regularity = music_params.get_param("rhythmic_regularity", 0.7)
        
        # 生成剩餘的旋律
        current_note = start_note
        chord_idx = 0
        
        for i in range(1, length):
            # 每4拍更換和弦
            chord_idx = min(i // 4, len(chord_progression) - 1)
            current_chord = chord_progression[chord_idx]
            
            # 當前音符的音階位置
            current_scale_pos = current_note % 12
            
            # 可能的下一個音符
            possible_notes = []
            
            # 傾向於使用和弦音
            if random.random() < chord_tone_preference:
                # 選擇和弦音
                for chord_note in current_chord:
                    note_val = chord_note % 12
                    # 找到接近當前音符八度的和弦音
                    octave_shift = (current_note // 12) * 12
                    possible_notes.append(note_val + octave_shift)
                    # 也考慮相鄰八度
                    possible_notes.append(note_val + octave_shift + 12)
                    possible_notes.append(note_val + octave_shift - 12)
            
            # 也使用音階上的音
            for scale_note in scale_notes:
                note_val = scale_note % 12
                octave_shift = (current_note // 12) * 12
                possible_notes.append(note_val + octave_shift)
                possible_notes.append(note_val + octave_shift + 12)
                possible_notes.append(note_val + octave_shift - 12)
            
            # 過濾掉範圍外的音符
            possible_notes = [n for n in possible_notes if 48 <= n <= 84]
            
            # 按照方向偏好過濾
            direction = directions[i]
            if direction > 0:
                # 上升
                possible_notes = [n for n in possible_notes if n >= current_note]
            elif direction < 0:
                # 下降
                possible_notes = [n for n in possible_notes if n <= current_note]
            
            # 如果沒有符合條件的音符，使用所有可能音符
            if not possible_notes:
                possible_notes = [n for n in range(current_note - 12, current_note + 13) if 48 <= n <= 84]
            
            # 選擇下一個音符
            if possible_notes:
                # 對可能的音符按照與當前音符的距離排序
                possible_notes.sort(key=lambda n: abs(n - current_note))
                
                # 偏好小間距移動 (級進)
                weights = [1.0 / (1 + abs(n - current_note)) for n in possible_notes]
                
                # 標準化權重
                total_weight = sum(weights)
                if total_weight > 0:
                    weights = [w / total_weight for w in weights]
                
                # 加權隨機選擇
                next_note_idx = random.choices(range(len(possible_notes)), weights=weights, k=1)[0]
                next_note = possible_notes[next_note_idx]
            else:
                # 沒有符合條件的音符，維持當前音符
                next_note = current_note
            
            # 避免連續相同音符
            if next_note == current_note and i < length - 1:
                # 嘗試選擇一個不同的音符
                alternatives = [n for n in possible_notes if n != current_note]
                if alternatives:
                    next_note = random.choice(alternatives)
            
            # 添加到旋律
            melody.append(next_note)
            current_note = next_note
        
        return melody
    
    def save_to_midi(self, melody: List[Note], chords: List[Dict], bass: List[Note], 
                     tempo: int, output_path: str) -> str:
        """保存為MIDI文件
        
        Args:
            melody: 旋律音符
            chords: 和弦
            bass: 低音聲部
            tempo: 速度
            output_path: 輸出路徑
            
        Returns:
            str: MIDI文件路徑
        """
        # 確保目錄存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 創建MIDI文件，3軌道：旋律、和弦、低音
        midi = MIDIFile(3)
        
        # 設置軌道名稱
        midi.addTrackName(0, 0, "Melody")
        midi.addTrackName(1, 0, "Chords")
        midi.addTrackName(2, 0, "Bass")
        
        # 設置速度
        midi.addTempo(0, 0, tempo)
        midi.addTempo(1, 0, tempo)
        midi.addTempo(2, 0, tempo)
        
        # 添加旋律音符
        for note in melody:
            midi.addNote(0, 0, note.pitch, note.start_time, note.duration, note.velocity)
        
        # 添加和弦音符
        for chord in chords:
            for pitch in chord["notes"]:
                midi.addNote(1, 0, pitch, chord["start_time"], chord["duration"], 70)
        
        # 添加低音聲部
        for note in bass:
            midi.addNote(2, 0, note.pitch, note.start_time, note.duration, note.velocity)
        
        # 寫入MIDI文件
        with open(output_path, "wb") as f:
            midi.writeFile(f)
        
        logger.info(f"MIDI文件已保存至: {output_path}")
        return output_path
    
    def play_midi(self, midi_path: str) -> None:
        """播放MIDI文件
        
        Args:
            midi_path: MIDI文件路徑
        """
        if 'pygame' not in sys.modules:
            logger.warning("缺少pygame套件，無法播放MIDI")
            return
        
        try:
            # 初始化pygame
            pygame.init()
            pygame.mixer.init()
            
            # 顯示播放信息
            logger.info(f"正在播放 {midi_path}...")
            logger.info("按Ctrl+C停止播放")
            
            # 播放MIDI
            pygame.mixer.music.load(midi_path)
            pygame.mixer.music.play()
            
            # 等待播放完成
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
        except KeyboardInterrupt:
            logger.info("\n播放已停止")
        except Exception as e:
            logger.error(f"播放時發生錯誤: {str(e)}")
        finally:
            # 清理pygame資源
            pygame.mixer.quit()
            pygame.quit()

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="基於用戶意圖理解的音樂創作")
    parser.add_argument("--description", "-d", type=str, required=True, help="音樂創作意圖描述")
    parser.add_argument("--output", "-o", type=str, default="output/intention_music.mid", help="輸出MIDI文件路徑")
    parser.add_argument("--play", "-p", action="store_true", help="生成後播放MIDI文件")
    parser.add_argument("--debug", action="store_true", help="啟用調試模式")
    
    args = parser.parse_args()
    
    # 設置日誌級別
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    
    # 創建音樂創作器
    creator = MusicCreator()
    
    # 基於意圖創作音樂
    logger.info(f"基於意圖創作音樂: {args.description}")
    result = creator.create_music_from_intention(args.description, args.output, args.play)
    
    # 保存結果
    json_path = args.output.replace(".mid", ".json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    logger.info(f"創作結果已保存至: {json_path}")
    logger.info(f"MIDI文件已保存至: {args.output}")

if __name__ == "__main__":
    main() 