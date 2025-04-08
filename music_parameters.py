#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
音樂參數模塊
定義音樂生成所需的參數類型、樂理規則和工作流程
確保音樂生成遵循"文本→參數→樂理校驗→作品"的流程
"""

import copy
import random
from typing import List

# 音樂風格預設
STYLE_PRESETS = {
    "古典": {
        "tempo_range": (70, 100),
        "harmonic_complexity": 0.7,     # 和聲複雜度
        "rhythmic_regularity": 0.8,     # 節奏規律性
        "melodic_contour": "arch",      # 旋律輪廓: arch, wave, ascend, descend
        "texture": "homophonic",        # 音樂織體: homophonic, polyphonic, monophonic
        "scale_preference": ["大調", "小調"],
        "chord_progression_types": ["authentic", "plagal", "deceptive"],  # 終止式類型
        "development_techniques": ["sequence", "inversion", "retrograde"],
        "phrase_structure": "period",   # 樂句結構: period, sentence, hybrid
        "instrument_roles": {
            "melody": {"function": "主旋律", "register": "middle", "articulation": "legato"},
            "harmony": {"function": "支持", "register": "middle", "articulation": "legato"}, 
            "bass": {"function": "基礎", "register": "low", "articulation": "detached"}
        },
        "orchestration": {
            "min_tracks": 4,
            "recommended_tracks": 8,
            "max_tracks": 16,
            "standard_instruments": [
                "violin",       # 第一小提琴 - 主旋律
                "violin",       # 第二小提琴 - 副旋律/和聲
                "viola",        # 中提琴 - 和聲
                "cello",        # 大提琴 - 低音/和聲
                "double_bass",  # 低音提琴 - 低音
                "flute",        # 長笛 - 裝飾/獨奏
                "oboe",         # 雙簧管 - 色彩/獨奏
                "clarinet",     # 單簧管 - 色彩/獨奏
                "bassoon",      # 巴松 - 低音/色彩
                "french_horn",  # 法國號 - 和聲/色彩
                "trumpet",      # 小號 - 強調/色彩
                "trombone",     # 長號 - 和聲/色彩
                "timpani",      # 定音鼓 - 節奏/強調
                "piano",        # 鋼琴 - 獨奏/伴奏
                "harp",         # 豎琴 - 琶音/色彩
                "percussion"    # 打擊樂器 - 節奏/色彩
            ],
            "grouping": {
                "strings": ["violin", "viola", "cello", "double_bass"],
                "woodwinds": ["flute", "oboe", "clarinet", "bassoon"],
                "brass": ["french_horn", "trumpet", "trombone"],
                "percussion": ["timpani", "percussion"],
                "others": ["piano", "harp"]
            },
            "voice_distribution": {
                "melody": ["violin", "flute", "oboe", "clarinet", "piano"],
                "counter_melody": ["violin", "viola", "clarinet", "french_horn"],
                "harmony": ["viola", "cello", "french_horn", "trombone", "bassoon"],
                "bass": ["cello", "double_bass", "bassoon", "trombone"],
                "rhythm": ["timpani", "percussion", "piano", "harp"]
            }
        },
        "form_structures": {
            "sonata": ["exposition", "development", "recapitulation", "coda"],
            "rondo": ["A", "B", "A", "C", "A", "D", "A"],
            "theme_variations": ["theme", "var1", "var2", "var3", "var4", "coda"],
            "minuet_trio": ["minuet", "trio", "minuet"],
            "concerto": ["tutti", "solo", "tutti", "solo", "cadenza", "tutti"]
        },
        "tonality_plan": {
            "primary_key": "tonic",
            "secondary_keys": ["dominant", "relative_minor", "subdominant"],
            "modulation_points": [0.25, 0.5, 0.75]  # 調性變化的相對位置
        }
    },
    "爵士": {
        "tempo_range": (100, 140),
        "harmonic_complexity": 0.9,     # 和聲複雜度
        "rhythmic_regularity": 0.5,     # 節奏規律性
        "melodic_contour": "wave",      # 旋律輪廓
        "texture": "homophonic",        # 音樂織體
        "scale_preference": ["藍調", "小調"],
        "chord_progression_types": ["2-5-1", "blues", "modal"],
        "development_techniques": ["improvisation", "call_response", "blue_notes"],
        "phrase_structure": "blues",    # 樂句結構
        "instrument_roles": {
            "melody": {"function": "即興", "register": "middle-high", "articulation": "swing"},
            "harmony": {"function": "聲部進行", "register": "middle", "articulation": "comping"}, 
            "bass": {"function": "行走低音", "register": "low", "articulation": "walking"}
        },
        "orchestration": {
            "min_tracks": 3,
            "recommended_tracks": 5,
            "max_tracks": 7,
            "standard_instruments": [
                "piano",       # 鋼琴 - 和聲/獨奏
                "double_bass", # C貝斯 - 行走低音
                "drums",       # 鼓組 - 節奏
                "saxophone",   # 薩克斯風 - 主奏
                "trumpet",     # 小號 - 主奏/和聲
                "trombone",    # 長號 - 和聲/主奏
                "guitar"       # 吉他 - 和聲/獨奏
            ],
            "grouping": {
                "rhythm_section": ["piano", "double_bass", "drums", "guitar"],
                "horn_section": ["saxophone", "trumpet", "trombone"]
            }
        },
        "form_structures": {
            "blues": ["I", "IV", "I", "I", "IV", "IV", "I", "I", "V", "IV", "I", "V"],
            "jazz_standard": ["head", "solos", "head"],
            "modal": ["intro", "theme", "solos", "theme", "outro"],
            "bebop": ["theme", "solos", "trading_fours", "theme"]
        }
    },
    "流行": {
        "tempo_range": (90, 130),
        "harmonic_complexity": 0.5,     # 和聲複雜度
        "rhythmic_regularity": 0.7,     # 節奏規律性
        "melodic_contour": "wave",      # 旋律輪廓
        "texture": "homophonic",        # 音樂織體
        "scale_preference": ["大調", "五聲"],
        "chord_progression_types": ["pop", "four_chords", "loop"],
        "development_techniques": ["repetition", "hook", "contrast"],
        "phrase_structure": "verse_chorus",   # 樂句結構
        "instrument_roles": {
            "melody": {"function": "主唱", "register": "middle-high", "articulation": "mix"},
            "harmony": {"function": "伴奏", "register": "middle", "articulation": "rhythm"}, 
            "bass": {"function": "節奏", "register": "low", "articulation": "emphatic"}
        }
    },
    "電子": {
        "tempo_range": (120, 160),
        "harmonic_complexity": 0.4,     # 和聲複雜度
        "rhythmic_regularity": 0.9,     # 節奏規律性
        "melodic_contour": "repetitive", # 旋律輪廓
        "texture": "layered",           # 音樂織體
        "scale_preference": ["五聲", "大調"],
        "chord_progression_types": ["minimal", "drone", "loop"],
        "development_techniques": ["layering", "filtering", "sampling"],
        "phrase_structure": "grid",     # 樂句結構
        "instrument_roles": {
            "melody": {"function": "主導", "register": "middle-high", "articulation": "staccato"},
            "harmony": {"function": "紋理", "register": "wide", "articulation": "sustained"}, 
            "bass": {"function": "基礎節奏", "register": "low", "articulation": "tight"}
        }
    }
}

# 情感參數映射
EMOTION_PARAMETERS = {
    "快樂": {
        "mode": "大調",
        "tempo_adjustment": 1.2,        # 速度調整倍數
        "register_preference": "高",     # 音域偏好
        "harmonic_brightness": 0.8,     # 和聲明亮度
        "rhythmic_energy": 0.7,         # 節奏活力
        "articulation": "staccato",     # 演奏方式
        "dynamics_range": (0.6, 0.9),   # 力度範圍
        "texture_density": 0.7,         # 織體密度
        "consonance_preference": 0.6    # 和諧偏好度
    },
    "悲傷": {
        "mode": "小調",
        "tempo_adjustment": 0.8,        # 速度調整倍數
        "register_preference": "低",     # 音域偏好
        "harmonic_brightness": 0.3,     # 和聲明亮度
        "rhythmic_energy": 0.3,         # 節奏活力
        "articulation": "legato",       # 演奏方式
        "dynamics_range": (0.3, 0.6),   # 力度範圍
        "texture_density": 0.5,         # 織體密度
        "consonance_preference": 0.8    # 和諧偏好度
    },
    "激動": {
        "mode": "大調",
        "tempo_adjustment": 1.3,        # 速度調整倍數
        "register_preference": "寬",     # 音域偏好
        "harmonic_brightness": 0.7,     # 和聲明亮度
        "rhythmic_energy": 0.9,         # 節奏活力
        "articulation": "marcato",      # 演奏方式
        "dynamics_range": (0.7, 1.0),   # 力度範圍
        "texture_density": 0.9,         # 織體密度
        "consonance_preference": 0.5    # 和諧偏好度
    },
    "平靜": {
        "mode": "大調",
        "tempo_adjustment": 0.7,        # 速度調整倍數
        "register_preference": "中",     # 音域偏好
        "harmonic_brightness": 0.6,     # 和聲明亮度
        "rhythmic_energy": 0.2,         # 節奏活力
        "articulation": "legato",       # 演奏方式
        "dynamics_range": (0.2, 0.5),   # 力度範圍
        "texture_density": 0.4,         # 織體密度
        "consonance_preference": 0.9    # 和諧偏好度
    }
}

# 音階定義
SCALES = {
    "大調": [0, 2, 4, 5, 7, 9, 11],     # C大調: C D E F G A B
    "小調": [0, 2, 3, 5, 7, 8, 10],     # c小調: C D Eb F G Ab Bb
    "五聲": [0, 2, 4, 7, 9],            # C五聲: C D E G A
    "藍調": [0, 3, 5, 6, 7, 10],        # C藍調: C Eb F F# G Bb
    "和聲小調": [0, 2, 3, 5, 7, 8, 11],  # 和聲小調: C D Eb F G Ab B
    "多利亞": [0, 2, 3, 5, 7, 9, 10],    # 多利亞調式: C D Eb F G A Bb
    "全音": [0, 2, 4, 6, 8, 10]          # 全音階: C D E F# G# A#
}

# 和弦功能定義 - 基於調內音級
CHORD_FUNCTIONS = {
    # 大調和弦功能
    "major": {
        0: {"name": "I", "type": "major", "function": "tonic"},
        1: {"name": "ii", "type": "minor", "function": "subdominant"},
        2: {"name": "iii", "type": "minor", "function": "tonic"},
        3: {"name": "IV", "type": "major", "function": "subdominant"},
        4: {"name": "V", "type": "major", "function": "dominant"},
        5: {"name": "vi", "type": "minor", "function": "tonic"},
        6: {"name": "vii°", "type": "diminished", "function": "dominant"}
    },
    # 小調和弦功能
    "minor": {
        0: {"name": "i", "type": "minor", "function": "tonic"},
        1: {"name": "ii°", "type": "diminished", "function": "subdominant"},
        2: {"name": "III", "type": "major", "function": "tonic"},
        3: {"name": "iv", "type": "minor", "function": "subdominant"},
        4: {"name": "v", "type": "minor", "function": "dominant"}, # 自然小調
        5: {"name": "VI", "type": "major", "function": "subdominant"},
        6: {"name": "VII", "type": "major", "function": "subtonic"}
    }
}

# 常見和弦進行
CHORD_PROGRESSIONS = {
    "authentic": [
        [0, 4, 0],          # I-V-I
        [0, 1, 4, 0],       # I-ii-V-I
        [0, 3, 4, 0]        # I-IV-V-I
    ],
    "plagal": [
        [0, 3, 0],          # I-IV-I
        [0, 5, 3, 0],       # I-vi-IV-I
        [0, 3, 1, 0]        # I-IV-ii-I
    ],
    "deceptive": [
        [0, 4, 5],          # I-V-vi
        [0, 3, 4, 5],       # I-IV-V-vi
        [0, 4, 5, 3, 0]     # I-V-vi-IV-I
    ],
    "2-5-1": [
        [1, 4, 0],          # ii-V-I (爵士經典)
        [1, 4, 0, 3],       # ii-V-I-IV
        [1, 4, 0, 5, 1, 4]  # ii-V-I-vi-ii-V
    ],
    "blues": [
        [0, 0, 0, 0, 3, 3, 0, 0, 4, 3, 0, 0],  # 12小節藍調
        [0, 3, 4, 3]                           # 簡化藍調
    ],
    "pop": [
        [0, 3, 5, 4],       # I-IV-vi-V (流行四和弦)
        [5, 3, 0, 4],       # vi-IV-I-V
        [0, 5, 3, 4]        # I-vi-IV-V
    ],
    "minimal": [
        [0, 5],             # I-vi (簡約循環)
        [0, 3],             # I-IV
        [0, 0, 3, 3]        # 重複兩個和弦
    ]
}

# 音符與和弦關係定義 - 用於樂理校驗
TONE_CHORD_RELATIONSHIPS = {
    "stable": {
        "description": "穩定音 - 最佳選擇，適合重要拍點",
        "intervals": [0, 4, 7]  # 和弦音（根音、三度、五度）
    },
    "color": {
        "description": "色彩音 - 豐富和聲，適合次要拍點",
        "intervals": [2, 9, 11, 14]  # 九度、六度、七度、九度
    },
    "tension": {
        "description": "張力音 - 創造張力，需要進行至穩定音",
        "intervals": [1, 3, 6, 8, 10]  # 二度、小三度、增四度/減五度、六度、小七度
    }
}

# 擴展和弦功能，添加更多和弦類型和進行
EXTENDED_CHORD_TYPES = {
    "M": [0, 4, 7],           # 大三和弦
    "m": [0, 3, 7],           # 小三和弦
    "dim": [0, 3, 6],         # 減三和弦
    "aug": [0, 4, 8],         # 增三和弦
    "sus4": [0, 5, 7],        # 掛四和弦
    "sus2": [0, 2, 7],        # 掛二和弦
    "7": [0, 4, 7, 10],       # 屬七和弦
    "M7": [0, 4, 7, 11],      # 大七和弦
    "m7": [0, 3, 7, 10],      # 小七和弦
    "dim7": [0, 3, 6, 9],     # 減七和弦
    "m7b5": [0, 3, 6, 10],    # 半減七和弦
    "aug7": [0, 4, 8, 10],    # 增七和弦
    "6": [0, 4, 7, 9],        # 大六和弦
    "m6": [0, 3, 7, 9],       # 小六和弦
    "9": [0, 4, 7, 10, 14],   # 屬九和弦
    "M9": [0, 4, 7, 11, 14],  # 大九和弦
    "m9": [0, 3, 7, 10, 14],  # 小九和弦
    "add9": [0, 4, 7, 14],    # 加九和弦
    "madd9": [0, 3, 7, 14]    # 小加九和弦
}

# 轉調相關功能
def calculate_circle_of_fifths_distance(key1: str, key2: str) -> int:
    """計算兩個調性在五度圈上的距離
    
    Args:
        key1: 第一個調性
        key2: 第二個調性
        
    Returns:
        int: 距離步數（正數表示順時針，負數表示逆時針）
    """
    # 調性順序（按五度圈順序排列）
    circle = [
        "C", "G", "D", "A", "E", "B", "F#", "C#", "G#", "D#", "A#", "F"
    ]
    
    # 提取調性根音（不考慮大小調）
    key1_root = key1.split()[0] if " " in key1 else key1
    key2_root = key2.split()[0] if " " in key2 else key2
    
    # 標準化表示（將降號調整為升號）
    if key1_root == "Db": key1_root = "C#"
    if key1_root == "Eb": key1_root = "D#"
    if key1_root == "Gb": key1_root = "F#"
    if key1_root == "Ab": key1_root = "G#"
    if key1_root == "Bb": key1_root = "A#"
    
    if key2_root == "Db": key2_root = "C#"
    if key2_root == "Eb": key2_root = "D#"
    if key2_root == "Gb": key2_root = "F#"
    if key2_root == "Ab": key2_root = "G#"
    if key2_root == "Bb": key2_root = "A#"
    
    # 計算在圓圈上的位置
    try:
        pos1 = circle.index(key1_root)
        pos2 = circle.index(key2_root)
    except ValueError:
        # 如果找不到調性，返回0（假設相同）
        return 0
    
    # 計算距離
    clockwise_distance = (pos2 - pos1) % 12
    counterclockwise_distance = (pos1 - pos2) % 12
    
    # 返回步數較少的方向
    if clockwise_distance <= counterclockwise_distance:
        return clockwise_distance
    else:
        return -counterclockwise_distance

def get_chord_symbol(chord_type: str, root_note: str) -> str:
    """根據和弦類型和根音生成和弦符號
    
    Args:
        chord_type: 和弦類型（如"M", "m", "7"等）
        root_note: 根音（如"C", "D#"等）
        
    Returns:
        str: 和弦符號（如"CM", "D#m", "G7"等）
    """
    # 特殊情況處理
    if chord_type == "M":
        return root_note
    else:
        return f"{root_note}{chord_type}"

def transpose_chord(chord: str, semitones: int) -> str:
    """將和弦轉調指定的半音數
    
    Args:
        chord: 和弦符號（如"C", "Dm", "G7"等）
        semitones: 轉調的半音數（正數表示上調，負數表示下調）
        
    Returns:
        str: 轉調後的和弦符號
    """
    # 音符列表
    notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    
    # 提取根音和和弦類型
    if not chord:
        return chord
    
    root = chord[0]
    chord_type = chord[1:] if len(chord) > 1 else "M"
    
    # 處理可能的升降號（#和b）
    if len(chord) > 1 and chord[1] in ["#", "b"]:
        root += chord[1]
        chord_type = chord[2:] if len(chord) > 2 else "M"
    
    # 標準化根音表示（將降號調整為升號）
    if root == "Db": root = "C#"
    if root == "Eb": root = "D#"
    if root == "Gb": root = "F#"
    if root == "Ab": root = "G#"
    if root == "Bb": root = "A#"
    
    # 查找根音在列表中的位置
    try:
        index = notes.index(root)
    except ValueError:
        # 如果找不到根音，返回原和弦
        return chord
    
    # 計算轉調後的索引
    new_index = (index + semitones) % 12
    
    # 獲取新根音
    new_root = notes[new_index]
    
    # 返回新和弦
    return get_chord_symbol(chord_type, new_root)

def create_modal_interchange_chord(key: str, scale_degree: int, target_mode: str) -> List[int]:
    """創建調式互換和弦
    
    從目標調式中借用和弦，豐富和聲色彩
    
    Args:
        key: 當前調性
        scale_degree: 級數（1-7）
        target_mode: 目標調式（如"大調", "小調", "多利亞"等）
        
    Returns:
        List[int]: 生成的和弦音符列表
    """
    # 提取根音
    key_root = key.split()[0] if " " in key else key
    
    # 標準化根音表示
    if key_root == "Db": key_root = "C#"
    if key_root == "Eb": key_root = "D#"
    if key_root == "Gb": key_root = "F#"
    if key_root == "Ab": key_root = "G#"
    if key_root == "Bb": key_root = "A#"
    
    # 獲取目標調式的音階
    target_scale = SCALES.get(target_mode, SCALES["大調"])
    
    # 計算根音的MIDI音高
    root_midi = NOTE_TO_MIDI.get(key_root, 60)
    
    # 計算目標和弦的根音
    degree_idx = scale_degree - 1  # 轉換為0-6的索引
    chord_root = (root_midi + target_scale[degree_idx % len(target_scale)]) % 12
    
    # 從目標調式構建和弦（簡單三和弦）
    chord = [chord_root]
    chord.append((chord_root + target_scale[(degree_idx + 2) % len(target_scale)]) % 12)
    chord.append((chord_root + target_scale[(degree_idx + 4) % len(target_scale)]) % 12)
    
    # 轉換為絕對MIDI音高（加上八度信息）
    return [note + 60 for note in chord]

# 全局音樂參數結構
class MusicParameters:
    """音樂參數類，用於存儲和計算音樂參數"""
    
    def __init__(self, style="古典", emotion=None):
        """初始化參數，根據風格和情感設置參數值"""
        self.params = {}
        self.set_style(style)
        if emotion:
            self.apply_emotion(emotion)
        
        # 填充默認參數
        self._fill_default_params()
    
    def set_style(self, style):
        """設置風格參數"""
        if style not in STYLE_PRESETS:
            print(f"未知風格: {style}，使用預設的'古典'風格")
            style = "古典"
        
        self.style = style
        self.params = copy.deepcopy(STYLE_PRESETS[style])
        
        # 選擇預設音階
        self.params["scale"] = self.params["scale_preference"][0]
        
        # 選擇和弦進行類型
        prog_type = random.choice(self.params["chord_progression_types"])
        self.params["chord_progression_type"] = prog_type
        if prog_type in CHORD_PROGRESSIONS:
            self.params["chord_progression"] = random.choice(CHORD_PROGRESSIONS[prog_type])
    
    def apply_emotion(self, emotion):
        """應用情感參數調整"""
        if emotion not in EMOTION_PARAMETERS:
            emotion_keys = list(EMOTION_PARAMETERS.keys())
            closest_match = None
            for key in emotion_keys:
                if key in emotion.lower():
                    closest_match = key
                    break
            
            if not closest_match:
                print(f"未知情感: {emotion}，不進行情感調整")
                return
            emotion = closest_match
        
        # 從情感參數字典中獲取參數
        emotion_params = EMOTION_PARAMETERS[emotion]
        
        # 整合情感參數到音樂參數中
        for key, value in emotion_params.items():
            if key == "mode":
                # 設定音階
                for scale_name in SCALES:
                    if value in scale_name:
                        self.params["scale"] = scale_name
                        break
            elif key == "tempo_adjustment":
                # 調整速度範圍
                min_tempo, max_tempo = self.params["tempo_range"]
                adjusted_min = int(min_tempo * value)
                adjusted_max = int(max_tempo * value)
                self.params["tempo_range"] = (adjusted_min, adjusted_max)
            else:
                # 直接設置其他參數
                self.params[key] = value
    
    def _fill_default_params(self):
        """填充默認參數值，確保所有必要參數都存在"""
        
        # 基本音樂參數默認值
        defaults = {
            "tempo": sum(self.params["tempo_range"]) // 2,  # 默認使用範圍中間值
            "octave": 4,
            "harmony_richness": 0.5,
            "note_density": 0.5,
            "rhythm_variety": 0.5
        }
        
        # 設置默認值 (僅當尚未設置時)
        for param, value in defaults.items():
            if param not in self.params:
                self.params[param] = value
    
    def get_param(self, param_name, default=None):
        """獲取參數值，如果不存在則返回默認值"""
        return self.params.get(param_name, default)
    
    def set_param(self, param_name, value):
        """設置參數值"""
        self.params[param_name] = value
    
    def validate_parameters(self):
        """校驗參數的有效性和一致性"""
        valid = True
        messages = []
        
        # 檢查必要參數是否存在
        required_params = ["tempo_range", "scale"]
        for param in required_params:
            if param not in self.params:
                valid = False
                messages.append(f"缺少必要參數: {param}")
        
        # 檢查和弦進行是否有效
        if "chord_progression" in self.params:
            # 確保和弦進行中的每一個和弦都是有效的
            scale_length = len(SCALES.get(self.params["scale"], []))
            if scale_length > 0:
                for chord_index in self.params["chord_progression"]:
                    if not (0 <= chord_index < scale_length):
                        valid = False
                        messages.append(f"和弦進行包含無效的和弦索引: {chord_index}")
        
        return valid, messages
    
    def get_scale_notes(self, root=60):
        """獲取當前音階的音符 (MIDI 數字)"""
        scale_type = self.params.get("scale", "大調")
        if scale_type in SCALES:
            return [root + interval for interval in SCALES[scale_type]]
        return [root + i for i in range(7)]  # 默認返回自然音階
    
    def get_chord_progression(self, root=60):
        """根據當前參數生成完整和弦進行"""
        scale_type = self.params.get("scale", "大調")
        scale = self.get_scale_notes(root)
        
        # 根據音階類型選擇和弦功能
        chord_function_set = "major"
        if "小調" in scale_type or scale_type == "藍調":
            chord_function_set = "minor"
        
        chord_functions = CHORD_FUNCTIONS[chord_function_set]
        
        # 獲取和弦進行索引
        progression_indices = self.params.get("chord_progression", [0, 4, 0])
        
        # 建立完整和弦
        chord_progression = []
        for idx in progression_indices:
            idx = idx % len(scale)  # 確保索引在有效範圍內
            
            # 根據和弦功能確定和弦類型
            chord_type = chord_functions[idx]["type"]
            root_note = scale[idx]
            
            # 根據和弦類型建立和弦
            chord = [root_note]  # 根音
            
            if chord_type == "major":
                chord.append(root_note + 4)  # 大三度
                chord.append(root_note + 7)  # 純五度
            elif chord_type == "minor":
                chord.append(root_note + 3)  # 小三度
                chord.append(root_note + 7)  # 純五度
            elif chord_type == "diminished":
                chord.append(root_note + 3)  # 小三度
                chord.append(root_note + 6)  # 減五度
            elif chord_type == "augmented":
                chord.append(root_note + 4)  # 大三度
                chord.append(root_note + 8)  # 增五度
            
            # 根據和聲豐富度添加七音
            harmony_richness = self.params.get("harmony_richness", 0.5)
            if random.random() < harmony_richness * 0.7:
                if chord_type == "major":
                    if chord_functions[idx]["function"] == "dominant":
                        chord.append(root_note + 10)  # 小七度 (屬七和弦)
                    else:
                        chord.append(root_note + 11)  # 大七度
                elif chord_type == "minor":
                    chord.append(root_note + 10)  # 小七度
                elif chord_type == "diminished":
                    chord.append(root_note + 9)  # 減七度
            
            chord_progression.append(chord)
        
        return chord_progression
    
    def validate_melody_with_chords(self, melody_notes, chord_progression):
        """驗證旋律與和弦的和諧關係，返回需要調整的音符索引"""
        adjustments_needed = []
        
        # 根據和弦分段
        chord_duration = 4.0  # 每個和弦4拍
        melody_time = 0
        
        for i, note in enumerate(melody_notes):
            # 計算當前時間點對應的和弦
            chord_idx = min(int(melody_time / chord_duration), len(chord_progression) - 1)
            current_chord = chord_progression[chord_idx]
            
            # 檢查音符與和弦的關係
            note_in_chord = False
            for chord_note in current_chord:
                # 考慮八度等效
                if (note - chord_note) % 12 == 0:
                    note_in_chord = True
                    break
            
            consonance_preference = self.params.get("consonance_preference", 0.7)
            
            # 決定是否需要調整
            if not note_in_chord and random.random() < consonance_preference:
                adjustments_needed.append(i)
            
            # 更新時間 (簡化，實際需要累加持續時間)
            melody_time += 1
        
        return adjustments_needed
    
    def suggest_better_note(self, note, chord):
        """根據當前和弦建議更合適的音符"""
        
        # 將音符標準化到一個八度內進行比較
        base_note = note % 12
        
        # 計算和弦根音
        root = chord[0] % 12
        
        # 將和弦音標準化
        chord_tones = [tone % 12 for tone in chord]
        
        # 如果音符已經是和弦音，不需要調整
        if base_note in chord_tones:
            return note
        
        # 找出距離當前音符最近的和弦音
        closest_dist = 12
        closest_tone = None
        
        for tone in chord_tones:
            dist = min((tone - base_note) % 12, (base_note - tone) % 12)
            if dist < closest_dist:
                closest_dist = dist
                closest_tone = tone
        
        # 把最近和弦音調整到與原音符相同的八度
        octave = note // 12
        adjusted_note = closest_tone + (octave * 12)
        
        # 确保音符在合理范围内
        if adjusted_note < 36:  # 低于C2
            adjusted_note += 12
        elif adjusted_note > 96:  # 高于C7
            adjusted_note -= 12
            
        return adjusted_note

    def apply_modulation(self, new_key: str, transition_point: float):
        """應用轉調效果
        
        在指定的位置轉換到新的調性
        
        Args:
            new_key: 新調性
            transition_point: 轉調點（相對位置，0.0-1.0）
        """
        # 記錄轉調信息
        if "modulations" not in self.params:
            self.params["modulations"] = []
        
        # 添加轉調點
        self.params["modulations"].append({
            "target_key": new_key,
            "position": transition_point
        })
        
        logger.info(f"添加轉調：從 {self.params.get('key', 'C')} 到 {new_key}，位置：{transition_point}")

    def get_modulation_chords(self, current_key: str, target_key: str) -> List[List[int]]:
        """獲取用於轉調的和弦進行
        
        生成一個自然過渡的和弦進行，從當前調性轉到目標調性
        
        Args:
            current_key: 當前調性
            target_key: 目標調性
            
        Returns:
            List[List[int]]: 和弦進行（包含轉調和弦）
        """
        # 計算在五度圈上的距離
        distance = calculate_circle_of_fifths_distance(current_key, target_key)
        
        # 生成轉調和弦進行
        modulation_chords = []
        
        # 根據距離選擇轉調策略
        if distance == 0:
            # 相同調性或無法確定距離，不需要轉調
            return [[60, 64, 67]]  # 返回C和弦作為占位符
        
        elif abs(distance) <= 2:
            # 近關係調性，可以使用共同和弦
            # 添加當前調的屬和弦
            modulation_chords.append(self.get_chord_by_degree(current_key, 5))  # V
            
            # 添加目標調的下屬和弦和屬和弦
            modulation_chords.append(self.get_chord_by_degree(target_key, 4))   # IV
            modulation_chords.append(self.get_chord_by_degree(target_key, 5))   # V
            modulation_chords.append(self.get_chord_by_degree(target_key, 1))   # I
        
        else:
            # 遠關係調性，使用多步轉調或轉門和弦
            # 添加當前調的減七和弦（常用作轉門和弦）
            modulation_chords.append(self.get_chord_by_degree(current_key, 7, "dim7"))
            
            # 添加目標調的屬七和弦和主和弦
            modulation_chords.append(self.get_chord_by_degree(target_key, 5, "7"))    # V7
            modulation_chords.append(self.get_chord_by_degree(target_key, 1))         # I
        
        return modulation_chords

    def get_chord_by_degree(self, key: str, degree: int, chord_type: str = None) -> List[int]:
        """根據級數和調性獲取和弦
        
        Args:
            key: 調性
            degree: 級數（1-7）
            chord_type: 和弦類型（可選），如果未指定則使用調內和弦
            
        Returns:
            List[int]: 和弦音符列表
        """
        # 確定調式（大調或小調）
        is_minor = "minor" in key.lower() or "小調" in key
        mode = "minor" if is_minor else "major"
        
        # 提取根音
        key_root = key.split()[0] if " " in key else key
        
        # 標準化根音表示
        if key_root == "Db": key_root = "C#"
        if key_root == "Eb": key_root = "D#"
        if key_root == "Gb": key_root = "F#"
        if key_root == "Ab": key_root = "G#"
        if key_root == "Bb": key_root = "A#"
        
        # 獲取調式的音階
        scale = SCALES["小調"] if is_minor else SCALES["大調"]
        
        # 計算根音的MIDI音高
        root_midi = NOTE_TO_MIDI.get(key_root, 60)
        
        # 計算和弦的根音
        degree_idx = degree - 1  # 轉換為0-6的索引
        chord_root = root_midi + scale[degree_idx % len(scale)]
        
        # 如果指定了和弦類型，使用擴展和弦類型
        if chord_type and chord_type in EXTENDED_CHORD_TYPES:
            # 構建指定類型的和弦
            intervals = EXTENDED_CHORD_TYPES[chord_type]
            return [chord_root + interval for interval in intervals]
        else:
            # 使用調內和弦
            chord_function = CHORD_FUNCTIONS[mode][degree_idx]
            chord_type = chord_function["type"]
            
            # 根據和弦類型構建和弦
            chord = [chord_root]  # 根音
            
            if chord_type == "major":
                chord.append(chord_root + 4)  # 大三度
                chord.append(chord_root + 7)  # 純五度
            elif chord_type == "minor":
                chord.append(chord_root + 3)  # 小三度
                chord.append(chord_root + 7)  # 純五度
            elif chord_type == "diminished":
                chord.append(chord_root + 3)  # 小三度
                chord.append(chord_root + 6)  # 減五度
            elif chord_type == "augmented":
                chord.append(chord_root + 4)  # 大三度
                chord.append(chord_root + 8)  # 增五度
            
            # 根據情況可能添加七音
            if chord_function["function"] == "dominant":
                chord.append(chord_root + 10)  # 小七度（屬七和弦）
            
            return chord

# 使用範例
if __name__ == "__main__":
    # 創建默認的古典風格參數
    params = MusicParameters("古典")
    print(f"默認參數: {params.params}")
    
    # 應用情感調整
    params.apply_emotion("快樂")
    print(f"應用情感後參數: {params.params}")
    
    # 獲取音階音符
    scale_notes = params.get_scale_notes()
    print(f"音階音符: {scale_notes}")
    
    # 獲取和弦進行
    chord_progression = params.get_chord_progression()
    print(f"和弦進行: {chord_progression}")
    
    # 驗證參數有效性
    valid, messages = params.validate_parameters()
    print(f"參數有效性: {valid}")
    if not valid:
        print(f"問題: {messages}") 