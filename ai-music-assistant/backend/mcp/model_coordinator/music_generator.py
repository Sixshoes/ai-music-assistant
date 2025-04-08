"""音樂生成器

實現音樂生成的核心邏輯
"""

import logging
import json
from typing import Dict, Any, List, Optional, Union
from ..mcp_schema import MusicParameters
from midiutil import MIDIFile
import io
from .style_manager import StyleManager, PlayingStyle, RhythmPattern
import random
from io import BytesIO
import math
import time

logger = logging.getLogger(__name__)

class MusicGenerator:
    """音樂生成器類"""
    
    def __init__(self):
        """初始化音樂生成器"""
        # 音符到MIDI音高的映射
        self.note_to_midi = {
            'C': 60, 'C#': 61, 'Db': 61, 'D': 62, 'D#': 63, 'Eb': 63,
            'E': 64, 'F': 65, 'F#': 66, 'Gb': 66, 'G': 67, 'G#': 68,
            'Ab': 68, 'A': 69, 'A#': 70, 'Bb': 70, 'B': 71
        }
        
        # 初始化風格管理器
        self.style_manager = StyleManager()
        
        # 風格和情緒對應表
        self.mood_map = {
            "happy": {
                "tempo_mod": 1.2,
                "scale": "major",
                "note_density": 0.8
            },
            "sad": {
                "tempo_mod": 0.8,
                "scale": "minor",
                "note_density": 0.6
            },
            "energetic": {
                "tempo_mod": 1.4,
                "scale": "major",
                "note_density": 1.0
            },
            "calm": {
                "tempo_mod": 0.9,
                "scale": "major",
                "note_density": 0.5
            },
            "mysterious": {
                "tempo_mod": 1.0,
                "scale": "minor",
                "note_density": 0.7
            }
        }
        
        # 調性到音階的映射
        self.key_to_scale = {
            "C": ["C", "D", "E", "F", "G", "A", "B"],
            "G": ["G", "A", "B", "C", "D", "E", "F#"],
            "D": ["D", "E", "F#", "G", "A", "B", "C#"],
            "A": ["A", "B", "C#", "D", "E", "F#", "G#"],
            "Am": ["A", "B", "C", "D", "E", "F", "G"],
            "Em": ["E", "F#", "G", "A", "B", "C", "D"],
        }
    
    def note_to_midi_number(self, note: str) -> int:
        """將音符名稱轉換為MIDI音高數字
        
        Args:
            note: 音符名稱（如 'C4'）
            
        Returns:
            int: MIDI音高數字
        """
        note_name = ''.join(filter(str.isalpha, note))
        octave = int(''.join(filter(str.isdigit, note)))
        base_note = self.note_to_midi[note_name]
        return base_note + (octave - 4) * 12
    
    def generate_music(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """根據參數生成音樂
        
        Args:
            parameters: 音樂參數
            
        Returns:
            Dict: 包含MIDI數據的字典
        """
        try:
            logger.info(f"開始生成音樂，參數: {parameters}")
            start_time = time.time()
            
            # 確保提供了必要參數
            if not parameters:
                logger.warning("未提供參數，使用默認參數")
                parameters = {
                    "tempo": DEFAULT_TEMPO,
                    "key": DEFAULT_KEY,
                    "genre": "jazz",  # 默認為爵士樂風格
                    "instruments": DEFAULT_INSTRUMENTS,
                    "duration": 180  # 至少3分鐘
                }
            
            # 設置預設值（如果缺少）
            tempo = parameters.get("tempo", DEFAULT_TEMPO)
            key = parameters.get("key", DEFAULT_KEY)
            genre = parameters.get("genre", "jazz").lower()
            complexity = float(parameters.get("complexity", DEFAULT_COMPLEXITY)) / 5.0  # 轉換為0-1範圍
            mood = parameters.get("mood", "neutral").lower()
            style = parameters.get("style", "normal").lower()
            time_signature = parameters.get("time_signature", DEFAULT_TIME_SIGNATURE)
            
            # 確保持續時間至少3分鐘
            duration = max(180, parameters.get("duration", 180))
            logger.info(f"設置音樂時長為 {duration} 秒")
            
            # 計算總拍數和小節數
            beats_per_minute = tempo
            total_seconds = duration
            beats_per_second = beats_per_minute / 60
            total_beats = total_seconds * beats_per_second
            beats_per_bar = int(time_signature.split('/')[0])
            total_bars = int(total_beats / beats_per_bar)
            
            # 確保至少有足夠的小節來創建一首完整的曲子
            total_bars = max(total_bars, 32)  # 至少32小節
            
            logger.info(f"總拍數: {total_beats}, 總小節數: {total_bars}")
            
            # 處理枚舉類型
            if hasattr(key, 'value'):
                key = key.value
            if hasattr(genre, 'value'):
                genre = genre.value
            
            # 處理列表中的枚舉類型
            if instruments and isinstance(instruments, list):
                instruments = [i.value if hasattr(i, 'value') else i for i in instruments]
            
            logger.info(f"開始生成音樂，參數: tempo={tempo}, key={key}, genre={genre}, instruments={instruments}")
            
            # 決定音軌數量 - 根據樂器列表、風格和複雜度
            track_count = len(instruments)
            if genre == 'classical':
                # 古典音樂通常需要更多音軌
                base_tracks = max(4, track_count)  # 至少4個音軌
                # 複雜度影響音軌數量
                complexity_factor = 1 + (complexity * 0.5)  # 複雜度為5時增加2.5倍
                target_tracks = min(12, int(base_tracks * complexity_factor))  # 最多12個音軌
                
                # 如果需要擴展現有樂器列表
                if track_count < target_tracks:
                    # 擴充傳統古典樂器組合
                    standard_classical_instruments = [
                        'violin', 'viola', 'cello', 'double_bass',  # 弦樂四重奏
                        'flute', 'oboe', 'clarinet', 'bassoon',     # 木管樂
                        'french_horn', 'trumpet', 'trombone', 'tuba', # 銅管樂
                        'timpani', 'percussion',                      # 打擊樂
                        'harp', 'piano'                               # 其他
                    ]
                    
                    # 添加未包含的樂器
                    for instrument in standard_classical_instruments:
                        if instrument not in instruments and len(instruments) < target_tracks:
                            instruments.append(instrument)
                            
                logger.info(f"古典樂器組合擴展至 {len(instruments)} 個音軌")
                
            elif genre == 'jazz':
                # 爵士樂標準組合
                if track_count < 3:  # 確保至少有節奏組
                    jazz_basics = ['piano', 'bass', 'drums', 'saxophone']
                    for inst in jazz_basics:
                        if inst not in instruments and len(instruments) < 5:
                            instruments.append(inst)
                            
            elif genre == 'electronic':
                # 電子音樂通常有更多層次
                if track_count < 4:
                    electronic_basics = ['synth_lead', 'synth_bass', 'drums', 'pad', 'arpeggio']
                    for inst in electronic_basics:
                        if inst not in instruments and len(instruments) < 6:
                            instruments.append(inst)
                            
            # 更新音軌數量
            track_count = len(instruments)
            
            # 創建MIDI文件
            midi = MIDIFile(track_count)
            
            # 設置速度
            for i in range(track_count):
                midi.addTempo(i, 0, tempo)
            
            # 計算小節數（假設4/4拍）
            beats_per_bar = 4
            beats_per_minute = tempo
            total_beats = (duration * beats_per_minute) / 60
            total_bars = int(total_beats / beats_per_bar)
            
            # 設置樂器
            for i, instrument in enumerate(instruments):
                # 將文字樂器名轉換為General MIDI程序號
                program = self._instrument_name_to_program(instrument)
                midi.addProgramChange(i, 0, 0, program)
                
                # 生成音樂
                # 根據樂器和風格選擇適合的生成方法
                if instrument in ['drums', 'percussion']:
                    self._generate_percussion(midi, i, total_bars, key, genre, complexity, mood, style)
                elif instrument in ['bass', 'double_bass', 'synth_bass']:
                    self._generate_bass_line(midi, i, total_bars, key, genre, complexity, mood, style)
                elif instrument in ['piano', 'keyboard', 'synth']:
                    # 決定鋼琴是旋律還是和弦功能
                    if i == 0 or (genre == 'classical' and i == 1):  # 第一軌通常是主旋律
                        self._generate_melody(midi, i, total_bars, key, genre, complexity, mood, style)
                    else:
                        self._generate_chord_accompaniment(midi, i, total_bars, key, genre, complexity, mood, style)
                elif instrument in ['violin', 'flute', 'trumpet', 'saxophone', 'synth_lead']:
                    # 首席樂器通常負責旋律
                    if i <= 2:  # 前兩軌可以是不同旋律
                        self._generate_melody(midi, i, total_bars, key, genre, complexity, mood, style, 
                                              is_counter_melody=(i > 0))  # 第二個旋律是對位
                    else:
                        # 其他樂器提供和聲支持
                        self._generate_harmony_support(midi, i, total_bars, key, genre, complexity, mood, style)
                elif instrument in ['viola', 'cello', 'french_horn', 'trombone']:
                    # 中音域樂器通常提供和聲或對位
                    self._generate_harmony_support(midi, i, total_bars, key, genre, complexity, mood, style)
                elif instrument in ['harp', 'pad', 'strings', 'synth_pad']:
                    # 這些樂器常用於提供和弦背景
                    self._generate_chord_accompaniment(midi, i, total_bars, key, genre, complexity, mood, style)
                elif instrument in ['arpeggio', 'synth_arp']:
                    # 分解和弦
                    self._generate_arpeggios(midi, i, total_bars, key, genre, complexity, mood, style)
                else:
                    # 默認生成方法
                    self._generate_music_by_style(midi, i, total_bars, key, genre, complexity, mood, style)
            
            # 轉換為MIDI數據
            midi_data = self._midi_to_bytes(midi)
            
            # 分析生成的音樂
            analysis = {
                "key": key,
                "tempo": tempo,
                "genre": genre,
                "duration": duration,
                "track_count": track_count,
                "instruments": instruments,
                "complexity": complexity,
                "mood": mood
            }
            
            return {
                "midi_data": midi_data,
                "analysis": analysis
            }
        
        except Exception as e:
            logger.error(f"生成音樂時發生錯誤: {str(e)}", exc_info=True)
            raise

    def _instrument_name_to_program(self, instrument_name: str) -> int:
        """將樂器名稱轉換為General MIDI程序號
        
        Args:
            instrument_name: 樂器名稱
            
        Returns:
            int: General MIDI程序號
        """
        instrument_map = {
            # 鋼琴家族
            'piano': 0,
            'grand_piano': 0,
            'bright_piano': 1,
            'electric_piano': 4,
            'honky_tonk_piano': 3,
            'electric_grand': 2,
            'harpsichord': 6,
            'clavinet': 7,
            
            # 色彩打擊樂器
            'celesta': 8,
            'glockenspiel': 9,
            'music_box': 10,
            'vibraphone': 11,
            'marimba': 12,
            'xylophone': 13,
            'tubular_bells': 14,
            'dulcimer': 15,
            
            # 風琴
            'organ': 19,
            'church_organ': 19,
            'reed_organ': 20,
            'accordion': 21,
            'harmonica': 22,
            'tango_accordion': 23,
            
            # 吉他
            'guitar': 24,
            'acoustic_guitar': 24,
            'nylon_guitar': 24,
            'steel_guitar': 25,
            'jazz_guitar': 26,
            'electric_guitar': 27,
            'clean_guitar': 27,
            'muted_guitar': 28,
            'overdrive_guitar': 29,
            'distortion_guitar': 30,
            'rock_guitar': 29,
            
            # 貝斯
            'bass': 32,
            'acoustic_bass': 32,
            'electric_bass': 33,
            'fingered_bass': 33,
            'picked_bass': 34,
            'fretless_bass': 35,
            'slap_bass': 36,
            'synth_bass': 38,
            'pop_bass': 39,
            'double_bass': 43,  # 弦樂組的低音提琴
            
            # 弦樂
            'violin': 40,
            'viola': 41,
            'cello': 42,
            'double_bass': 43,
            'tremolo_strings': 44,
            'pizzicato_strings': 45,
            'harp': 46,
            'timpani': 47,
            'strings': 48,
            'string_ensemble': 48,
            'slow_strings': 49,
            'synth_strings': 50,
            
            # 合唱/人聲
            'voice': 52,
            'choir': 52,
            'vocal': 53,
            
            # 銅管樂器
            'trumpet': 56,
            'trombone': 57,
            'tuba': 58,
            'muted_trumpet': 59,
            'french_horn': 60,
            'brass': 61,
            'brass_section': 61,
            'synth_brass': 62,
            
            # 簧樂器
            'saxophone': 66,
            'soprano_sax': 64,
            'alto_sax': 65,
            'tenor_sax': 66,
            'baritone_sax': 67,
            'oboe': 68,
            'english_horn': 69,
            'bassoon': 70,
            'clarinet': 71,
            
            # 笛類
            'flute': 73,
            'piccolo': 72,
            'recorder': 74,
            'pan_flute': 75,
            'bottle_blow': 76,
            'shakuhachi': 77,
            'whistle': 78,
            'ocarina': 79,
            
            # 合成音
            'synth_lead': 80,
            'square_lead': 80,
            'saw_lead': 81,
            'calliope_lead': 82,
            'fm_lead': 84,
            'synth_pad': 89,
            'pad': 89,
            'warm_pad': 89,
            'synth_pad_warm': 89,
            'synth_pad_polysynth': 90,
            'space_pad': 91,
            'arp_synth': 96,
            'arpeggio': 96,
            
            # 民族樂器
            'sitar': 104,
            'banjo': 105,
            'shamisen': 106,
            'koto': 107,
            'kalimba': 108,
            'bagpipe': 109,
            'fiddle': 110,
            'shanai': 111,
            
            # 打擊樂器
            'drums': 118,  # 這不是真正的GM程序，需要特別處理
            'percussion': 119  # 這不是真正的GM程序，需要特別處理
        }
        
        # 返回默認值 (大鋼琴) 如果未找到匹配
        return instrument_map.get(instrument_name.lower(), 0)

    def _generate_harmony_support(self, midi: MIDIFile, track: int, total_bars: int, key: str, 
                                 genre: str, complexity: float, mood: str, style: str):
        """生成和聲支持音軌
        
        這個功能用於生成中音域樂器的襯托和聲部分，如中提琴、大提琴等
        
        Args:
            midi: MIDI文件對象
            track: 軌道號
            total_bars: 總小節數
            key: 調性
            genre: 風格
            complexity: 複雜度
            mood: 情緒
            style: 演奏風格
        """
        # 根據情緒調整參數
        mood_params = self.mood_map.get(mood, self.mood_map["happy"])
        tempo_mod = mood_params["tempo_mod"]
        scale = mood_params["scale"]
        note_density = mood_params["note_density"]
        
        # 獲取調性對應的音階
        key_scale = self.key_to_scale.get(key, self.key_to_scale["C"])
        
        # 創建基礎和弦進行
        chord_prog = self._get_harmony_progression(key, genre)
        
        # 記錄已使用的音高以避免與其他軌道重複
        bar_length = 4  # 假設4/4拍
        current_time = 0
        
        for bar in range(total_bars):
            # 決定當前和弦
            chord_idx = bar % len(chord_prog)
            current_chord = chord_prog[chord_idx]
            
            # 確定和弦音
            chord_notes = self._get_chord_notes(current_chord, key_scale)
            
            # 在中間音域選擇和弦音
            middle_chord_notes = [note for note in chord_notes if 48 <= note <= 72]
            
            # 根據複雜度決定每小節音符數量
            notes_per_bar = 1 + int(complexity * 3)  # 1-4個音符
            
            # 每個音符的時長 (平均)
            duration_per_note = bar_length / notes_per_bar
            
            # 生成和聲音符
            for i in range(notes_per_bar):
                # 選擇和弦音
                if middle_chord_notes:
                    note = random.choice(middle_chord_notes)
                    
                    # 稍微變化音高以增加多樣性，但仍保持在和弦內
                    if random.random() < complexity * 0.3:
                        note_options = [n for n in middle_chord_notes if abs(n - note) <= 7]
                        if note_options:
                            note = random.choice(note_options)
                    
                    # 隨機調整音符時長
                    note_duration = duration_per_note
                    if random.random() < complexity * 0.4:
                        note_duration *= random.choice([0.5, 0.75, 1.0, 1.5])
                    
                    # 限制在一個小節內
                    note_duration = min(note_duration, bar_length - (i * (bar_length / notes_per_bar)))
                    
                    # 添加力度變化
                    velocity = random.randint(60, 90)
                    if genre == "classical":
                        # 古典音樂通常有更多的力度變化
                        velocity = self._dynamic_curve(bar, total_bars, base=70, amplitude=20)
                    
                    # 添加音符
                    start_time = current_time + (i * (bar_length / notes_per_bar))
                    midi.addNote(track, 0, note, start_time, note_duration, velocity)
            
            # 更新當前時間
            current_time += bar_length

    def _generate_arpeggios(self, midi: MIDIFile, track: int, total_bars: int, key: str, 
                           genre: str, complexity: float, mood: str, style: str):
        """生成分解和弦
        
        用於豎琴、琶音合成器等擅長分解和弦的樂器
        
        Args:
            midi: MIDI文件對象
            track: 軌道號
            total_bars: 總小節數
            key: 調性
            genre: 風格
            complexity: 複雜度
            mood: 情緒
            style: 演奏風格
        """
        # 根據情緒調整參數
        mood_params = self.mood_map.get(mood, self.mood_map["happy"])
        tempo_mod = mood_params["tempo_mod"]
        scale = mood_params["scale"]
        note_density = mood_params["note_density"]
        
        # 獲取調性對應的音階
        key_scale = self.key_to_scale.get(key, self.key_to_scale["C"])
        
        # 創建基礎和弦進行
        chord_prog = self._get_harmony_progression(key, genre)
        
        # 記錄已使用的音高以避免與其他軌道重複
        bar_length = 4  # 假設4/4拍
        current_time = 0
        
        # 琶音模式
        arpeggio_patterns = [
            [0, 1, 2, 3],      # 上升
            [3, 2, 1, 0],      # 下降
            [0, 2, 1, 3],      # 交替1
            [0, 3, 1, 2],      # 交替2
            [0, 1, 2, 3, 2, 1] # 上下
        ]
        
        # 根據複雜度選擇琶音模式 - 複雜度越高，模式越複雜
        pattern_idx = min(int(complexity * len(arpeggio_patterns)), len(arpeggio_patterns) - 1)
        arp_pattern = arpeggio_patterns[pattern_idx]
        
        for bar in range(total_bars):
            # 決定當前和弦
            chord_idx = bar % len(chord_prog)
            current_chord = chord_prog[chord_idx]
            
            # 確定和弦音
            chord_notes = self._get_chord_notes(current_chord, key_scale)
            
            # 確保有足夠的音符用於琶音
            while len(chord_notes) < 4:
                chord_notes.append(chord_notes[0] + 12)  # 添加八度高音
            
            # 根據音樂風格調整每小節的音符數量
            notes_per_bar = 8  # 默認值
            if genre == "classical":
                notes_per_bar = 8 + int(complexity * 8)  # 8-16個音符
            elif genre == "electronic":
                notes_per_bar = 8 + int(complexity * 16)  # 8-24個音符
            elif genre == "jazz":
                notes_per_bar = 4 + int(complexity * 4)  # 4-8個音符
            
            # 每個音符的時長
            duration_per_note = bar_length / notes_per_bar
            
            # 生成琶音
            for i in range(notes_per_bar):
                # 選擇琶音模式中的位置
                pattern_pos = i % len(arp_pattern)
                chord_idx = arp_pattern[pattern_pos] % len(chord_notes)
                
                # 獲取音符
                note = chord_notes[chord_idx]
                
                # 加入八度變化以增加豐富性
                if random.random() < complexity * 0.2:
                    octave_shift = random.choice([-12, 0, 12])
                    note += octave_shift
                
                # 限制音符在合理範圍內
                note = max(36, min(96, note))
                
                # 添加力度變化
                velocity = random.randint(70, 100)
                
                # 添加音符
                start_time = current_time + (i * duration_per_note)
                midi.addNote(track, 0, note, start_time, duration_per_note * 0.9, velocity)
            
            # 更新當前時間
            current_time += bar_length

    def _dynamic_curve(self, bar: int, total_bars: int, base: int = 64, amplitude: int = 16) -> int:
        """生成自然的力度曲線
        
        Args:
            bar: 當前小節
            total_bars: 總小節數
            base: 基礎力度值
            amplitude: 力度變化幅度
            
        Returns:
            int: 計算出的力度值
        """
        # 使用正弦曲線產生自然的起伏
        if total_bars <= 1:
            return base
        
        # 正弦曲線，產生波浪形的力度變化
        position = bar / total_bars
        
        # 多個正弦曲線疊加，產生更自然的變化
        curve1 = math.sin(position * 2 * math.pi)  # 一個完整週期
        curve2 = 0.5 * math.sin(position * 4 * math.pi)  # 兩個週期，幅度減半
        curve3 = 0.25 * math.sin(position * 6 * math.pi)  # 三個週期，幅度再減半
        
        # 組合曲線並放大到力度範圍
        dynamic = base + int(amplitude * (curve1 + curve2 + curve3) / 1.75)
        
        # 確保在合理範圍內
        return max(30, min(dynamic, 127))

    def _get_harmony_progression(self, key: str, genre: str) -> List[str]:
        """獲取和弦進行
        
        Args:
            key: 調性
            genre: 風格
            
        Returns:
            List[str]: 和弦進行列表
        """
        # 基本的和弦進行模板
        progressions = {
            "classical": [
                ["I", "IV", "V", "I"],  # 最基本的正格終止式
                ["I", "vi", "IV", "V", "I"],  # 擴展的正格終止式
                ["I", "IV", "I", "V", "vi", "IV", "V", "I"],  # 古典風格8小節進行
                ["I", "V", "vi", "iii", "IV", "I", "IV", "V"]  # 另一種古典進行
            ],
            "jazz": [
                ["ii7", "V7", "Imaj7", "VI7"],  # 基本的爵士進行
                ["Imaj7", "vi7", "ii7", "V7"],  # 爵士標準進行
                ["iii7", "VI7", "ii7", "V7"]  # 常見轉位
            ],
            "pop": [
                ["I", "V", "vi", "IV"],  # 流行音樂常見進行
                ["vi", "IV", "I", "V"],  # 另一個流行進行
                ["I", "IV", "V", "IV"]  # 簡單的流行進行
            ],
            "rock": [
                ["I", "IV", "V", "IV"],  # 基本搖滾進行
                ["I", "V", "IV", "IV"],  # 另一個搖滾進行
                ["I", "bVII", "IV", "I"]  # 硬搖滾進行
            ],
            "electronic": [
                ["I", "V", "vi", "IV"],  # 電子音樂進行
                ["vi", "V", "IV", "III"],  # 另一個電子進行
                ["I", "I", "I", "V", "V", "vi", "vi", "IV", "IV", "IV", "IV", "V"]  # EDM風格長進行
            ]
        }
        
        # 獲取風格的和弦進行列表，如果沒有則使用流行風格
        style_progressions = progressions.get(genre, progressions["pop"])
        
        # 隨機選擇一個進行
        selected_progression = random.choice(style_progressions)
        
        # 根據調性和和弦進行生成完整和弦
        key_root = key.split("_")[0] if "_" in key else key  # 從類似"C_MAJOR"提取"C"
        
        # 主要調性的和弦映射 (簡化版，僅考慮基本和弦)
        chord_mapping = {
            # 大調和弦
            "I": key_root,
            "ii": self._transpose_note(key_root, 2) + "m",
            "iii": self._transpose_note(key_root, 4) + "m",
            "IV": self._transpose_note(key_root, 5),
            "V": self._transpose_note(key_root, 7),
            "vi": self._transpose_note(key_root, 9) + "m",
            "vii": self._transpose_note(key_root, 11) + "dim",
            
            # 大調七和弦
            "Imaj7": key_root + "maj7",
            "ii7": self._transpose_note(key_root, 2) + "7",
            "iii7": self._transpose_note(key_root, 4) + "7",
            "IVmaj7": self._transpose_note(key_root, 5) + "maj7",
            "V7": self._transpose_note(key_root, 7) + "7",
            "vi7": self._transpose_note(key_root, 9) + "7",
            
            # 其他常用和弦
            "bVII": self._transpose_note(key_root, 10),
            "VI7": self._transpose_note(key_root, 8) + "7",
            "III": self._transpose_note(key_root, 4)
        }
        
        # 將和弦符號轉換為實際和弦
        actual_progression = []
        for chord in selected_progression:
            if chord in chord_mapping:
                actual_progression.append(chord_mapping[chord])
            else:
                logger.warning(f"未知和弦符號: {chord}，使用主和弦替代")
                actual_progression.append(key_root)
        
        return actual_progression

    def _transpose_note(self, note: str, semitones: int) -> str:
        """將音符升高指定的半音數
        
        Args:
            note: 音符名稱
            semitones: 升高的半音數
            
        Returns:
            str: 轉置後的音符名稱
        """
        notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        
        # 找到音符在音階中的位置
        try:
            note_idx = notes.index(note)
            new_idx = (note_idx + semitones) % 12
            return notes[new_idx]
        except ValueError:
            logger.warning(f"無法識別的音符: {note}，使用C代替")
            return "C"

    def _get_chord_notes(self, chord: str, scale: List[int]) -> List[int]:
        """獲取和弦的音符
        
        Args:
            chord: 和弦名稱
            scale: 音階列表
            
        Returns:
            List[int]: 和弦音符的MIDI數字列表
        """
        # 提取和弦根音
        root = chord[0]
        if len(chord) > 1 and chord[1] in ["#", "b"]:
            root = chord[:2]
            chord_type = chord[2:]
        else:
            chord_type = chord[1:]
        
        # 將根音轉換為MIDI數字
        try:
            root_midi = self.note_to_midi_number(root + "4")
        except:
            root_midi = 60  # 如果轉換失敗，使用中央C
        
        # 根據和弦類型選擇音符偏移
        if "maj7" in chord_type:
            return [root_midi, root_midi + 4, root_midi + 7, root_midi + 11]
        elif "7" in chord_type:
            return [root_midi, root_midi + 4, root_midi + 7, root_midi + 10]
        elif "dim" in chord_type:
            return [root_midi, root_midi + 3, root_midi + 6]
        elif "m" in chord_type:
            return [root_midi, root_midi + 3, root_midi + 7]
        else:  # 大三和弦
            return [root_midi, root_midi + 4, root_midi + 7]

    def _get_chord_root(self, chord: str) -> Union[str, int]:
        """獲取和弦的根音
        
        Args:
            chord: 和弦名稱
            
        Returns:
            Union[str, int]: 和弦根音的名稱或MIDI數字
        """
        # 提取和弦根音
        root = chord[0]
        if len(chord) > 1 and chord[1] in ["#", "b"]:
            root = chord[:2]
        
        return root

    def _generate_music_by_style(
        self, 
        midi: MIDIFile, 
        track: int, 
        total_bars: int, 
        key: str, 
        genre: str,
        complexity: float,
        mood: str,
        style: str
    ) -> None:
        """根據風格生成音樂
        
        Args:
            midi: MIDI文件對象
            track: 軌道號
            total_bars: 總小節數
            key: 調性
            genre: 風格
            complexity: 複雜度
            mood: 情緒
            style: 演奏風格
        """
        # 根據情緒調整參數
        mood_params = self.mood_map.get(mood, self.mood_map["happy"])
        tempo_mod = mood_params["tempo_mod"]
        scale = mood_params["scale"]
        note_density = mood_params["note_density"]
        
        # 根據風格選擇模式
        style_patterns = {
            'pop': {
                'chords': ['C', 'G', 'Am', 'F'],
                'rhythm': [1, 1, 1, 1],
                'velocity': 80
            },
            'jazz': {
                'chords': ['Dm7', 'G7', 'Cmaj7', 'Am7'],
                'rhythm': [0.5, 0.5, 1, 1],
                'velocity': 70
            },
            'classical': {
                'chords': ['C', 'F', 'G', 'C'],
                'rhythm': [1, 1, 1, 1],
                'velocity': 90
            },
            'rock': {
                'chords': ['C', 'F', 'G', 'F'],
                'rhythm': [0.5, 0.5, 0.5, 0.5],
                'velocity': 100
            },
            'blues': {
                'chords': ['C', 'F', 'C', 'G'],
                'rhythm': [1, 1, 1, 1],
                'velocity': 85
            },
            'folk': {
                'chords': ['C', 'G', 'Am', 'F'],
                'rhythm': [1, 1, 1, 1],
                'velocity': 75
            }
        }
        
        pattern = style_patterns.get(genre.lower(), style_patterns['pop'])
        chords = pattern['chords']
        rhythm = pattern['rhythm']
        base_velocity = pattern['velocity']
        
        # 根據複雜度調整節奏和力度
        rhythm = [r * (1 + complexity * 0.5) for r in rhythm]
        velocity = int(base_velocity * (1 + complexity * 0.2))
        
        # 根據演奏風格調整音符持續時間
        if style == 'staccato':
            duration_multiplier = 0.5
        elif style == 'legato':
            duration_multiplier = 1.2
        elif style == 'arpeggio':
            duration_multiplier = 0.8
        else:  # normal
            duration_multiplier = 1.0
        
        # 生成和弦進行
        for bar in range(total_bars):
            chord = chords[bar % len(chords)]
            duration = rhythm[bar % len(rhythm)] * duration_multiplier
            time = bar * 4.0  # 假設每小節4拍
            
            # 獲取和弦音符
            chord_notes = self._get_chord_notes(chord, self.key_to_scale[key])
            
            # 添加和弦音符
            for note in chord_notes:
                if note >= 0 and note <= 127:  # MIDI 音符範圍檢查
                    midi.addNote(track, 0, note, time, duration, velocity)
                    
            # 根據複雜度添加額外的音符變化
            if complexity > 0.7:
                # 添加一些裝飾音
                for note in chord_notes:
                    if random.random() < 0.3:  # 30% 的機率添加裝飾音
                        decoration_time = time + random.random() * duration
                        decoration_duration = duration * 0.25
                        if note + 2 <= 127:  # 確保音符在有效範圍內
                            midi.addNote(track, 0, note + 2, decoration_time, 
                                       decoration_duration, int(velocity * 0.8))

    def _generate_piano(self, midi: MIDIFile, track: int, total_bars: int, key: str):
        """生成鋼琴部分
        
        Args:
            midi: MIDI文件對象
            track: 軌道號
            total_bars: 小節數
            key: 調性
        """
        try:
            logger.info(f"開始生成鋼琴部分，軌道: {track}, 小節數: {total_bars}, 調性: {key}")
            
            # 設置鋼琴音色
            midi.addProgramChange(track, 0, 0, 0)  # 0 = 鋼琴
            
            # 生成和弦進行
            chord_progression = self._generate_chord_progression(key)
            logger.info(f"生成的和弦進行: {chord_progression}")
            
            # 計算每個和弦的持續時間（以拍為單位）
            beats_per_chord = 4  # 每個和弦4拍
            
            # 重複和弦進行直到達到所需的小節數
            for bar in range(total_bars):
                chord_index = bar % len(chord_progression)
                chord = chord_progression[chord_index]
                
                # 獲取和弦音符
                chord_notes = self._get_chord_notes(chord, self.key_to_scale[key])
                logger.debug(f"小節 {bar} 的和弦 {chord} 音符: {chord_notes}")
                
                # 添加和弦
                for note in chord_notes:
                    # 添加主和弦音符（較低八度）
                    midi.addNote(track, 0, note - 12, bar * 4, beats_per_chord, 80)
                    # 添加高八度和弦音符
                    midi.addNote(track, 0, note, bar * 4, beats_per_chord, 70)
                
                # 添加一些旋律音符
                if bar % 2 == 0:  # 每隔一小節添加旋律
                    melody_note = chord_notes[0] + 12  # 使用和弦根音的高八度
                    midi.addNote(track, 0, melody_note, bar * 4 + 2, 2, 90)
            
            logger.info(f"鋼琴部分生成完成，共 {total_bars} 小節")
            
        except Exception as e:
            logger.error(f"生成鋼琴部分時發生錯誤: {str(e)}", exc_info=True)
            raise

    def _generate_strings(self, midi: MIDIFile, track: int, total_bars: int, key: str):
        """生成弦樂部分
        
        Args:
            midi: MIDI文件對象
            track: 軌道號
            total_bars: 小節數
            key: 調性
        """
        # 生成和弦進行
        chord_progression = self._generate_chord_progression(key)
        
        # 計算每個和弦的持續時間
        beats_per_chord = 4
        
        # 重複和弦進行
        for bar in range(total_bars):
            chord_index = bar % len(chord_progression)
            chord = chord_progression[chord_index]
            
            # 獲取和弦音符
            chord_notes = self._get_chord_notes(chord, self.key_to_scale[key])
            
            # 添加持續音符
            for note in chord_notes:
                midi.addNote(track, 0, note, bar * 4, beats_per_chord, 48)

    def _generate_guitar(self, midi: MIDIFile, track: int, total_bars: int, key: str):
        """生成吉他部分
        
        Args:
            midi: MIDI文件對象
            track: 軌道號
            total_bars: 小節數
            key: 調性
        """
        # 生成和弦進行
        chord_progression = self._generate_chord_progression(key)
        
        # 計算每個和弦的持續時間
        beats_per_chord = 4
        
        # 重複和弦進行
        for bar in range(total_bars):
            chord_index = bar % len(chord_progression)
            chord = chord_progression[chord_index]
            
            # 獲取和弦音符
            chord_notes = self._get_chord_notes(chord, self.key_to_scale[key])
            
            # 添加分解和弦
            for i, note in enumerate(chord_notes):
                midi.addNote(track, 0, note, bar * 4 + i, 1, 64)

    def _generate_bass(self, midi: MIDIFile, track: int, total_bars: int, key: str):
        """生成貝斯部分
        
        Args:
            midi: MIDI文件對象
            track: 軌道號
            total_bars: 小節數
            key: 調性
        """
        # 生成和弦進行
        chord_progression = self._generate_chord_progression(key)
        
        # 計算每個和弦的持續時間
        beats_per_chord = 4
        
        # 重複和弦進行
        for bar in range(total_bars):
            chord_index = bar % len(chord_progression)
            chord = chord_progression[chord_index]
            
            # 獲取和弦根音
            root_note = self._get_chord_root(chord)
            
            # 添加根音
            midi.addNote(track, 0, root_note - 24, bar * 4, beats_per_chord, 80)

    def _generate_drums(self, midi: MIDIFile, track: int, total_bars: int):
        """生成鼓組部分
        
        Args:
            midi: MIDI文件對象
            track: 軌道號
            total_bars: 小節數
        """
        # 基本鼓點模式（4/4拍）
        kick = 36    # 低音鼓
        snare = 38   # 小鼓
        hihat = 42   # 閉合踩鑔
        
        # 重複鼓點模式
        for bar in range(total_bars):
            # 低音鼓（1、3拍）
            midi.addNote(track, 9, kick, bar * 4 + 0, 1, 100)
            midi.addNote(track, 9, kick, bar * 4 + 2, 1, 100)
            
            # 小鼓（2、4拍）
            midi.addNote(track, 9, snare, bar * 4 + 1, 1, 80)
            midi.addNote(track, 9, snare, bar * 4 + 3, 1, 80)
            
            # 踩鑔（每拍）
            for beat in range(4):
                midi.addNote(track, 9, hihat, bar * 4 + beat, 1, 60)

    def _generate_melody(self, midi: MIDIFile, track: int, total_bars: int, key: str, 
                        genre: str, complexity: float, mood: str, style: str, is_counter_melody: bool = False):
        """生成旋律
        
        Args:
            midi: MIDIFile對象
            track: 軌道編號
            total_bars: 總小節數
            key: 調性
            genre: 風格
            complexity: 複雜度 (0-1)
            mood: 情緒
            style: 演奏風格
            is_counter_melody: 是否為對位旋律
        """
        logger.info(f"生成{'對位' if is_counter_melody else '主'}旋律，風格: {genre}, 複雜度: {complexity:.2f}")
        
        # 獲取調式的音階
        key_scale = self._get_scale_for_key(key)
        
        # 確保音階是整數列表
        key_scale = [int(note) if not isinstance(note, int) else note for note in key_scale]
        
        # 計算小節長度（以拍為單位）
        bar_length = float(self.beats_per_bar)
        
        # 初始化當前時間
        current_time = 0.0
        
        # 設置旋律基本參數
        register_offset = 0
        if is_counter_melody:
            register_offset = -12 if random.random() < 0.7 else 12  # 對位旋律通常在不同音域
        
        # 根據情緒調整音符力度
        velocity_base = 70  # 默認基礎力度
        if mood == "happy" or mood == "energetic":
            velocity_base = 85
        elif mood == "sad" or mood == "calm":
            velocity_base = 60
        
        # 根據複雜度調整音符密度
        note_density = 4 + int(complexity * 8)  # 從4到12個音符/小節
        
        # 生成所有小節的旋律
        for bar in range(total_bars):
            # 獲取當前小節的和弦
            chord_idx = bar % len(self.chord_progression)
            current_chord = self.chord_progression[chord_idx]
            
            # 從和弦音符中提取可用音符
            chord_tones = [note % 12 for note in current_chord]  # 轉到一個八度內
            
            # 為每個小節計算音符數量
            # 偶爾變化音符密度以創造更自然的旋律
            if random.random() < 0.3:
                note_count = max(2, note_density + random.randint(-2, 2))
            else:
                note_count = note_density
            
            # 計算每個音符的平均持續時間
            avg_note_duration = bar_length / note_count
            
            # 每個音符的開始音高
            if bar == 0:
                # 第一小節從和弦的根音或中音開始
                current_pitch = current_chord[0] % 12
                current_pitch += 60  # 中音區域
            else:
                # 其他小節保持前一旋律的連續性
                current_pitch = last_pitch if 'last_pitch' in locals() else 60
            
            # 生成本小節的音符
            for i in range(note_count):
                # 根據旋律連續性和和弦結構選擇下一個音符
                # 70%的機率使用和弦音，30%使用音階上的其他音
                if random.random() < 0.7:
                    # 選擇和弦音
                    pitch_class = random.choice(chord_tones)
                else:
                    # 選擇音階上的音符
                    scale_degree = random.randint(0, len(key_scale) - 1)
                    pitch_class = key_scale[scale_degree] % 12
                
                # 決定最終音高(考慮八度)
                # 從當前音高開始，限制音符移動幅度
                current_octave = current_pitch // 12
                
                # 計算同音階類的不同八度選項
                options = [
                    (current_octave - 1) * 12 + pitch_class,
                    current_octave * 12 + pitch_class,
                    (current_octave + 1) * 12 + pitch_class
                ]
                
                # 選擇距離當前音符最近的音高
                note_pitch = min(options, key=lambda x: abs(x - current_pitch))
                
                # 應用對位旋律的音域偏移
                note_pitch += register_offset
                
                # 限制音符在合理範圍內(中音區)
                note_pitch = max(48, min(84, note_pitch))
                
                # 更新當前音高，用於下一個音符
                current_pitch = note_pitch
                last_pitch = note_pitch
                
                # 設置音符持續時間
                # 根據演奏風格調整
                duration_factor = 1.0
                if style == "staccato":
                    duration_factor = 0.5
                elif style == "legato":
                    duration_factor = 0.95
                
                # 根據音符在小節中的位置調整力度
                # 強拍通常力度更大
                position_in_bar = i / note_count
                beat_emphasis = 1.0
                if position_in_bar < 0.1 or abs(position_in_bar - 0.5) < 0.1:  # 第一拍和第三拍
                    beat_emphasis = 1.2
                
                velocity = min(100, int(velocity_base * beat_emphasis))
                
                # 添加音符到MIDI
                midi.addNote(
                    track, 
                    0, 
                    note_pitch, 
                    current_time + (i * avg_note_duration), 
                    avg_note_duration * duration_factor, 
                    velocity
                )
            
            # 更新當前時間到下一小節
            current_time += bar_length
        
        logger.info(f"旋律生成完成，共 {total_bars} 小節，音符數: ~{note_density * total_bars}")
    
    def _generate_rhythm(self, midi: MIDIFile, track: int, rhythm_pattern: RhythmPattern,
                        playing_style: PlayingStyle, complexity: float):
        """生成節奏
        
        Args:
            midi: MIDI文件對象
            track: 軌道號
            rhythm_pattern: 節奏型態
            playing_style: 演奏風格
            complexity: 複雜度
        """
        logger.info(f"生成節奏部分，節奏型態: {rhythm_pattern}, 複雜度: {complexity}")
        
        # 節奏樂器音符映射
        drum_notes = {
            "kick": 36,      # 低音鼓
            "snare": 38,     # 小鼓
            "closed_hat": 42, # 閉合踩鑔
            "open_hat": 46,  # 開放踩鑔
            "crash": 49,     # 擊鑔
            "ride": 51       # 叉鑔
        }
        
        # 不同節奏型態的模板
        patterns = {
            RhythmPattern.STRAIGHT: [
                {"beat": 0.0, "drum": "kick", "velocity": 100},
                {"beat": 0.5, "drum": "closed_hat", "velocity": 80},
                {"beat": 1.0, "drum": "snare", "velocity": 90},
                {"beat": 1.5, "drum": "closed_hat", "velocity": 80},
                {"beat": 2.0, "drum": "kick", "velocity": 100},
                {"beat": 2.5, "drum": "closed_hat", "velocity": 80},
                {"beat": 3.0, "drum": "snare", "velocity": 90},
                {"beat": 3.5, "drum": "closed_hat", "velocity": 80}
            ],
            RhythmPattern.SWING: [
                {"beat": 0.0, "drum": "kick", "velocity": 100},
                {"beat": 0.66, "drum": "closed_hat", "velocity": 70},
                {"beat": 1.0, "drum": "snare", "velocity": 90},
                {"beat": 1.66, "drum": "closed_hat", "velocity": 70},
                {"beat": 2.0, "drum": "kick", "velocity": 100},
                {"beat": 2.66, "drum": "closed_hat", "velocity": 70},
                {"beat": 3.0, "drum": "snare", "velocity": 90},
                {"beat": 3.66, "drum": "closed_hat", "velocity": 70}
            ]
        }
        
        # 獲取對應節奏型態的模板，如果沒有則使用直拍
        pattern = patterns.get(rhythm_pattern, patterns[RhythmPattern.STRAIGHT])
        
        # 計算總體節奏時長
        num_bars = 4  # 生成4小節
        
        # 添加額外的打擊樂變化，根據複雜度調整
        extra_hits = []
        if complexity > 0.5:
            # 添加簡單的變化
            extra_hits.append({"beat": 0.25, "drum": "closed_hat", "velocity": 60})
            extra_hits.append({"beat": 1.25, "drum": "closed_hat", "velocity": 60})
        
        if complexity > 0.7:
            # 添加更多變化
            extra_hits.append({"beat": 2.25, "drum": "closed_hat", "velocity": 60})
            extra_hits.append({"beat": 3.25, "drum": "closed_hat", "velocity": 60})
        
        if complexity > 0.9:
            # 添加高複雜度變化
            extra_hits.append({"beat": 1.75, "drum": "kick", "velocity": 80})
            extra_hits.append({"beat": 3.75, "drum": "snare", "velocity": 70})
        
        # 合併基本模板和額外打擊
        full_pattern = pattern + extra_hits
        
        # 生成所有小節的節奏
        for bar in range(num_bars):
            for hit in full_pattern:
                # 計算實際時間點
                time_point = bar * 4 + hit["beat"]  # 每小節4拍
                
                # 添加打擊音符
                midi.addNote(
                    track, 0, 
                    drum_notes[hit["drum"]], 
                    time_point, 
                    0.1,  # 打擊樂持續時間短
                    hit["velocity"]
                )
                
                # 每8小節添加一些變奏
                if bar % 2 == 1 and complexity > 0.6:
                    # 添加一些隨機變奏
                    if random.random() < 0.3:
                        # 隨機添加額外的鼓點
                        rand_drum = random.choice(list(drum_notes.keys()))
                        rand_time = time_point + random.choice([0.125, 0.25, 0.375])
                        midi.addNote(
                            track, 0, 
                            drum_notes[rand_drum], 
                            rand_time, 
                            0.1, 
                            70 + random.randint(-10, 10)
                        )
        
        logger.info(f"節奏部分生成完成，節奏型態: {rhythm_pattern}，小節數: {num_bars}")
    
    def _generate_pad(self, midi: MIDIFile, track: int, chord_progression: List[str],
                     playing_style: PlayingStyle, complexity: float, scale: List[str], key: str):
        """生成襯底聲部
        
        Args:
            midi: MIDI文件對象
            track: 軌道號
            chord_progression: 和弦進行
            playing_style: 演奏風格
            complexity: 複雜度
            scale: 音階
            key: 調性
        """
        logger.info(f"生成襯底聲部，調性: {key}, 複雜度: {complexity}")
        
        # 和弦到音符的簡單映射
        chord_notes = {
            "C": ["C3", "E3", "G3"],
            "Cmaj7": ["C3", "E3", "G3", "B3"],
            "G": ["G2", "B2", "D3"],
            "G7": ["G2", "B2", "D3", "F3"],
            "Am": ["A2", "C3", "E3"],
            "Dm7": ["D2", "F2", "A2", "C3"],
            "F": ["F2", "A2", "C3"],
            "F7": ["F2", "A2", "C3", "Eb3"],
            "E": ["E2", "G#2", "B2"],
            "D": ["D2", "F#2", "A2"],
            "A": ["A2", "C#3", "E3"],
            "Em": ["E2", "G2", "B2"]
        }
        
        # 設置和弦進行的時長
        chord_duration = 4.0  # 每個和弦4拍
        
        for i, chord in enumerate(chord_progression):
            # 獲取和弦對應的音符
            if chord in chord_notes:
                notes = chord_notes[chord]
            else:
                # 如果找不到和弦，使用調性的基本和弦
                notes = chord_notes.get(key, ["C3", "E3", "G3"])
            
            # 根據複雜度可能添加更多音符
            if complexity > 0.7 and len(notes) < 4:
                # 在高複雜度時添加第7音或第9音
                octave = "3"
                seventh_note = scale[(scale.index(notes[0][0]) + 6) % len(scale)] + octave
                notes.append(seventh_note)
            
            # 根據演奏風格調整持續時間和力度
            if playing_style == PlayingStyle.STACCATO:
                duration = 0.5
                velocity = 70
            elif playing_style == PlayingStyle.LEGATO:
                duration = chord_duration * 0.95
                velocity = 60
            elif playing_style == PlayingStyle.ARPEGGIO:
                # 琶音演奏
                for j, note in enumerate(notes):
                    pitch = self.note_to_midi_number(note)
                    start_time = i * chord_duration + j * (chord_duration / len(notes))
                    note_duration = chord_duration / len(notes) * 0.8
                    midi.addNote(track, 0, pitch, start_time, note_duration, 70)
                continue
            else:  # NORMAL
                duration = chord_duration * 0.8
                velocity = 60
            
            # 添加和弦音符
            for note in notes:
                pitch = self.note_to_midi_number(note)
                midi.addNote(track, 0, pitch, i * chord_duration, duration, velocity)
                
            # 根據複雜度，可能在每個和弦之間添加過渡音符
            if complexity > 0.8 and i < len(chord_progression) - 1:
                # 添加一些過渡音符
                next_chord = chord_progression[i + 1]
                if next_chord in chord_notes:
                    next_notes = chord_notes[next_chord]
                    
                    # 選擇一個過渡音符
                    transition_note = random.choice(next_notes)
                    pitch = self.note_to_midi_number(transition_note)
                    
                    # 在和弦結束前稍早添加過渡音符
                    transition_start = (i + 1) * chord_duration - 0.5
                    midi.addNote(track, 0, pitch, transition_start, 0.3, 50)
        
        logger.info(f"襯底聲部生成完成，和弦進行: {chord_progression}")
    
    def _get_instrument_program(self, instrument: str) -> int:
        """獲取樂器的 MIDI 程序號
        
        Args:
            instrument: 樂器名稱
            
        Returns:
            int: MIDI 程序號
        """
        instrument_map = {
            'piano': 0,      # 鋼琴
            'strings': 48,   # 弦樂合奏
            'guitar': 24,    # 尼龍弦吉他
            'bass': 32,      # 貝斯
            'drums': 128,    # 鼓組
            'violin': 40,    # 小提琴
            'cello': 42,     # 大提琴
            'flute': 73,     # 長笛
            'trumpet': 56,   # 小號
            'saxophone': 66, # 薩克斯
            'organ': 16,     # 管風琴
            'choir': 52,     # 合唱
            'synth': 80,     # 合成器
            'harp': 46,      # 豎琴
            'clarinet': 71,  # 單簧管
        }
        return instrument_map.get(instrument.lower(), 0)

    def _generate_chord_progression(self, key: str) -> List[str]:
        """生成和弦進行
        
        Args:
            key: 調性
            
        Returns:
            List[str]: 和弦進行
        """
        # 常見的和弦進行
        progressions = {
            'C': ['C', 'G', 'Am', 'F'],
            'G': ['G', 'D', 'Em', 'C'],
            'D': ['D', 'A', 'Bm', 'G'],
            'A': ['A', 'E', 'F#m', 'D'],
            'F': ['F', 'C', 'Dm', 'Bb'],
            'Am': ['Am', 'Em', 'F', 'G'],
            'Em': ['Em', 'Bm', 'C', 'D']
        }
        return progressions.get(key, ['C', 'G', 'Am', 'F'])

    def _get_chord_root(self, chord: str) -> int:
        """獲取和弦的根音
        
        Args:
            chord: 和弦名稱
            
        Returns:
            int: MIDI音符號
        """
        # 基本音符映射（C3 = 48）
        base_notes = {
            'C': 48, 'C#': 49, 'D': 50, 'D#': 51,
            'E': 52, 'F': 53, 'F#': 54, 'G': 55,
            'G#': 56, 'A': 57, 'A#': 58, 'B': 59
        }
        
        # 獲取根音
        root = chord[0]
        if len(chord) > 1 and chord[1] in ['#', 'b']:
            root = chord[:2]
        
        return base_notes.get(root, 48)

    def _add_chord(self, midi: MIDIFile, track: int, bar: int, key: str, chord: str, duration: float, velocity: int):
        """添加和弦到 MIDI 文件
        
        Args:
            midi: MIDI 文件對象
            track: 軌道號
            bar: 小節號
            key: 調性
            chord: 和弦名稱
            duration: 持續時間
            velocity: 音量
        """
        # 和弦音符偏移量映射
        chord_offsets = {
            'maj': [0, 4, 7],      # 大三和弦
            'min': [0, 3, 7],      # 小三和弦
            'dim': [0, 3, 6],      # 減三和弦
            'aug': [0, 4, 8],      # 增三和弦
            '7': [0, 4, 7, 10],    # 屬七和弦
            'maj7': [0, 4, 7, 11], # 大七和弦
            'min7': [0, 3, 7, 10], # 小七和弦
        }
        
        # 獲取和弦根音
        root = self._get_chord_root(chord)
        if root is None:
            # 如果無法識別和弦，使用調性的主音
            root = self.note_to_midi_number(key)
        
        # 確定和弦類型
        chord_type = 'maj'  # 默認為大三和弦
        if 'm' in chord or 'min' in chord:
            chord_type = 'min'
        elif 'dim' in chord:
            chord_type = 'dim'
        elif 'aug' in chord:
            chord_type = 'aug'
        elif 'maj7' in chord:
            chord_type = 'maj7'
        elif '7' in chord:
            chord_type = '7'
        elif 'min7' in chord:
            chord_type = 'min7'
        
        # 計算時間
        time = bar * 4.0  # 假設每小節4拍
        
        # 添加和弦音符
        for offset in chord_offsets[chord_type]:
            note = root + offset
            if note >= 0 and note <= 127:  # MIDI 音符範圍檢查
                midi.addNote(track, 0, note, time, duration, velocity) 

    def _generate_chord_accompaniment(self, midi: MIDIFile, track: int, total_bars: int, key: str, 
                               genre: str, complexity: float, mood: str, style: str):
        """生成和弦伴奏
        
        Args:
            midi: MIDI文件對象
            track: 軌道號
            total_bars: 總小節數
            key: 調性
            genre: 風格
            complexity: 複雜度
            mood: 情緒
            style: 演奏風格
        """
        # 獲取和弦進行
        chord_progression = self._get_harmony_progression(key, genre)
        
        # 當前時間
        current_time = 0.0
        
        # 設置基本參數
        bar_length = 4.0  # 每小節4拍
        
        # 獲取調性對應的音階
        key_scale = self.key_to_scale.get(key, self.key_to_scale["C"])
        
        # 生成和弦
        for bar in range(total_bars):
            # 決定當前和弦
            chord_idx = bar % len(chord_progression)
            current_chord = chord_progression[chord_idx]
            
            # 獲取和弦音符
            chord_notes = self._get_chord_notes(current_chord, key_scale)
            
            # 根據風格和複雜度決定每小節的和弦變化數量
            if genre == "classical":
                if complexity < 0.3:
                    changes_per_bar = 1  # 每小節一個和弦
                elif complexity < 0.7:
                    changes_per_bar = 2  # 每小節兩個和弦
                else:
                    changes_per_bar = 4  # 每小節四個和弦
            elif genre == "jazz":
                changes_per_bar = min(4, 1 + int(complexity * 4))  # 爵士樂和弦變化更頻繁
            else:
                changes_per_bar = 1  # 默認每小節一個和弦
            
            # 計算每個和弦的持續時間
            chord_duration = bar_length / changes_per_bar
            
            # 對於當前小節應用和弦變化
            for change in range(changes_per_bar):
                # 計算和弦時間點
                chord_time = current_time + (change * chord_duration)
                
                # 計算和弦力度
                velocity = 60 + int(complexity * 20)  # 複雜度越高，和弦越響亮
                
                # 根據風格選擇和弦播放方式
                if style == "arpeggio":
                    # 分解和弦方式
                    for i, note in enumerate(chord_notes):
                        note_time = chord_time + (i * (chord_duration / len(chord_notes) * 0.8))
                        note_duration = min(chord_duration / len(chord_notes), chord_duration * 0.8)
                        midi.addNote(track, 0, note, note_time, note_duration, velocity)
                else:
                    # 整體和弦方式
                    for note in chord_notes:
                        if style == "staccato":
                            note_duration = chord_duration * 0.5
                        else:  # legato或正常
                            note_duration = chord_duration * 0.95
                        
                        # 添加和弦音符
                        midi.addNote(track, 0, note, chord_time, note_duration, velocity)
            
            # 更新當前時間到下一小節
            current_time += bar_length
        
        logger.info(f"和弦伴奏生成完成，共 {total_bars} 小節")

    def _generate_bass_line(self, midi: MIDIFile, track: int, total_bars: int, key: str, 
                      genre: str, complexity: float, mood: str, style: str):
        """生成低音聲部
        
        Args:
            midi: MIDIFile對象
            track: 軌道編號
            total_bars: 總小節數
            key: 調性
            genre: 風格
            complexity: 複雜度
            mood: 情緒
            style: 演奏風格
        """
        logger.info(f"生成低音聲部，風格: {genre}, 複雜度: {complexity:.2f}, 小節數: {total_bars}")
        
        # 獲取調式的音階
        key_scale = self._get_scale_for_key(key)
        
        # 確保音階是整數列表
        key_scale = [int(note) if not isinstance(note, int) else note for note in key_scale]
        
        # 計算小節長度（以拍為單位）
        bar_length = float(self.beats_per_bar)
        
        # 初始化當前時間
        current_time = 0.0
        
        # 為每個小節生成低音
        for bar in range(total_bars):
            # 獲取當前小節的和弦（簡化，實際需要考慮和弦進行）
            chord_idx = bar % len(self.chord_progression)
            chord = self.chord_progression[chord_idx]
            
            # 獲取和弦的根音作為低音音符
            bass_note = chord[0]
            
            # 確保低音音符在合適的音域（低八度）
            while bass_note >= 48:  # C3
                bass_note -= 12
            while bass_note < 24:  # C1
                bass_note += 12
            
            # 基於複雜度和風格選擇低音型態
            notes_per_bar = int(2 + complexity * 6)  # 從2到8個音符/小節
            note_duration = bar_length / notes_per_bar
            
            # 生成基於和弦的低音音符
            for i in range(notes_per_bar):
                # 根據位置選擇音符
                if i == 0:  # 每小節第一拍強調根音
                    note = bass_note
                    velocity = 80 + int(10 * complexity)  # 力度稍強
                else:
                    # 隨機選擇和弦內音符或經過音
                    if random.random() < 0.7:  # 70%機率使用和弦音
                        chord_tone_idx = random.randint(0, len(chord) - 1)
                        note = chord[chord_tone_idx]
                        # 確保在低音區域
                        while note >= 48:
                            note -= 12
                    else:  # 30%機率使用經過音
                        note = bass_note + random.choice([1, 2, 3, 5, 7, 8, 10])
                    velocity = 60 + random.randint(-10, 10)
                
                # 根據情緒調整力度
                if mood == "sad" or mood == "calm":
                    velocity = int(velocity * 0.8)
                elif mood == "happy" or mood == "energetic":
                    velocity = min(127, int(velocity * 1.2))
                
                # 添加低音音符
                start_time = current_time + (i * note_duration)
                midi.addNote(track, 0, note, start_time, note_duration * 0.9, velocity)
            
            # 更新當前時間到下一小節
            current_time += bar_length
        
        logger.info(f"低音聲部生成完成，共 {total_bars} 小節")

    def _generate_harmony_support(self, midi: MIDIFile, track: int, total_bars: int, key: str, 
                           genre: str, complexity: float, mood: str, style: str):
        """生成和聲支持聲部
        
        Args:
            midi: MIDI文件對象
            track: 軌道號
            total_bars: 總小節數
            key: 調性
            genre: 風格
            complexity: 複雜度
            mood: 情緒
            style: 演奏風格
        """
        # 根據情緒調整參數
        mood_params = self.mood_map.get(mood, self.mood_map["happy"])
        tempo_mod = mood_params["tempo_mod"]
        scale = mood_params["scale"]
        note_density = mood_params["note_density"]
        
        # 獲取調性對應的音階
        key_scale = self.key_to_scale.get(key, self.key_to_scale["C"])
        
        # 創建基礎和弦進行
        chord_prog = self._get_harmony_progression(key, genre)
        
        # 記錄已使用的音高以避免與其他軌道重複
        bar_length = 4  # 假設4/4拍
        current_time = 0
        
        for bar in range(total_bars):
            # 決定當前和弦
            chord_idx = bar % len(chord_prog)
            current_chord = chord_prog[chord_idx]
            
            # 確定和弦音
            chord_notes = self._get_chord_notes(current_chord, key_scale)
            
            # 在中間音域選擇和弦音
            middle_chord_notes = [note for note in chord_notes if 48 <= note <= 72]
            
            # 根據複雜度決定每小節音符數量
            notes_per_bar = 1 + int(complexity * 3)  # 1-4個音符
            
            # 每個音符的時長 (平均)
            duration_per_note = bar_length / notes_per_bar
            
            # 生成和聲音符
            for i in range(notes_per_bar):
                # 選擇和弦音
                if middle_chord_notes:
                    note = random.choice(middle_chord_notes)
                    
                    # 稍微變化音高以增加多樣性，但仍保持在和弦內
                    if random.random() < complexity * 0.3:
                        note_options = [n for n in middle_chord_notes if abs(n - note) <= 7]
                        if note_options:
                            note = random.choice(note_options)
                    
                    # 隨機調整音符時長
                    note_duration = duration_per_note
                    if random.random() < complexity * 0.4:
                        note_duration *= random.choice([0.5, 0.75, 1.0, 1.5])
                    
                    # 限制在一個小節內
                    note_duration = min(note_duration, bar_length - (i * (bar_length / notes_per_bar)))
                    
                    # 添加力度變化
                    velocity = random.randint(60, 90)
                    if genre == "classical":
                        # 古典音樂通常有更多的力度變化
                        velocity = self._dynamic_curve(bar, total_bars, base=70, amplitude=20)
                    
                    # 添加音符
                    start_time = current_time + (i * (bar_length / notes_per_bar))
                    midi.addNote(track, 0, note, start_time, note_duration, velocity)
            
            # 更新當前時間
            current_time += bar_length
        
        logger.info(f"和聲支持聲部生成完成，共 {total_bars} 小節")

    def _generate_percussion(self, midi: MIDIFile, track: int, total_bars: int, key: str, 
                       genre: str, complexity: float, mood: str, style: str):
        """生成打擊樂聲部
        
        Args:
            midi: MIDIFile對象
            track: 軌道編號
            total_bars: 總小節數
            key: 調性 (對打擊樂不太重要)
            genre: 風格
            complexity: 複雜度 (0-1)
            mood: 情緒
            style: 演奏風格
        """
        logger.info(f"生成打擊樂聲部，風格: {genre}, 複雜度: {complexity:.2f}")
        
        # 標準打擊樂器MIDI音符
        KICK = 36    # 大鼓
        SNARE = 38   # 小鼓
        CLOSED_HH = 42  # 閉合高帽
        OPEN_HH = 46    # 開放高帽
        RIDE = 51    # 騎鈸
        CRASH = 49   # 強鈸
        TOM_H = 48   # 高音嗵鼓
        TOM_M = 45   # 中音嗵鼓
        TOM_L = 41   # 低音嗵鼓
        
        # 計算小節長度
        bar_length = float(self.beats_per_bar)
        beats_per_bar = self.beats_per_bar
        current_time = 0.0
        
        # 根據情緒調整力度基準
        base_velocity = 80
        if mood == "sad" or mood == "calm":
            base_velocity = 60
        elif mood == "happy" or mood == "energetic":
            base_velocity = 90
        
        # 創建基本節奏模式 (基於複雜度和風格)
        # 節拍密度隨複雜度增加
        beat_density = 2 + int(complexity * 6)  # 從2到8個節拍點/小節
        
        # 生成所有小節的打擊樂
        for bar in range(total_bars):
            # 添加強拍的大鼓
            if random.random() < 0.8:  # 80%機率
                midi.addNote(track, 9, KICK, current_time, 0.2, base_velocity + random.randint(-10, 10))
            
            # 添加弱拍的小鼓 (通常在2、4拍)
            for beat in range(1, int(beats_per_bar), 2):  # 2、4拍...
                if random.random() < 0.7:  # 70%機率
                    midi.addNote(track, 9, SNARE, current_time + beat, 0.2, base_velocity + random.randint(-10, 10))
            
            # 添加高帽 (更密集)
            for i in range(beat_density):
                time = current_time + (bar_length * i / beat_density)
                # 隨機選擇閉合或開放高帽
                hat_type = CLOSED_HH if random.random() < 0.8 else OPEN_HH
                # 隨機調整力度
                velocity = base_velocity - 20 + random.randint(-10, 10)
                midi.addNote(track, 9, hat_type, time, 0.1, velocity)
            
            # 根據複雜度添加額外的打擊樂元素
            if complexity > 0.5:
                # 偶爾添加強鈸
                if bar % 8 == 0 or random.random() < 0.1:  # 每8小節或10%機率
                    midi.addNote(track, 9, CRASH, current_time, 0.3, base_velocity + 10)
                
                # 偶爾添加嗵鼓
                if random.random() < 0.2 * complexity:  # 最高20%*complexity機率
                    tom = random.choice([TOM_H, TOM_M, TOM_L])
                    time = current_time + random.random() * bar_length
                    midi.addNote(track, 9, tom, time, 0.2, base_velocity)
            
            # 更新當前時間到下一小節
            current_time += bar_length
        
        logger.info(f"打擊樂聲部生成完成，共 {total_bars} 小節")

    def _midi_to_bytes(self, midi: MIDIFile) -> bytes:
        """將MIDI對象轉換為字節數據
        
        Args:
            midi: MIDI文件對象
            
        Returns:
            bytes: MIDI文件的字節數據
        """
        import io
        
        # 創建一個內存文件對象
        midi_file = io.BytesIO()
        
        # 將MIDI數據寫入內存文件
        midi.writeFile(midi_file)
        
        # 重置文件指針到開頭
        midi_file.seek(0)
        
        # 讀取字節數據
        midi_bytes = midi_file.read()
        
        # 關閉內存文件
        midi_file.close()
        
        return midi_bytes