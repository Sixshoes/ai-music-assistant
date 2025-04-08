#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
音樂參數模塊
定義音樂生成所需的參數類型、樂理規則和工作流程
確保音樂生成遵循"文本→參數→樂理校驗→作品"的流程
"""

import copy
import random

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

# 全局音樂參數結構
class MusicParameters:
    """音樂參數類，用於存儲和計算音樂參數"""
    
    def __init__(self, style=None, emotion=None):
        """初始化參數，根據風格和情感設置參數值"""
        self.params = {}
        
        # 設置基本參數默認值
        self.params = {
            "tempo_range": (90, 140),
            "scale_preference": ["大調", "小調"],
            "harmonic_complexity": 0.5,
            "rhythmic_regularity": 0.7,
            "chord_progression_types": ["authentic", "plagal", "pop"]
        }
        
        # 選擇預設音階
        self.params["scale"] = self.params["scale_preference"][0]
        
        # 選擇和弦進行類型
        prog_type = random.choice(self.params["chord_progression_types"])
        self.params["chord_progression_type"] = prog_type
        if prog_type in CHORD_PROGRESSIONS:
            self.params["chord_progression"] = random.choice(CHORD_PROGRESSIONS[prog_type])
        
        # 填充默認參數
        self._fill_default_params()
        
        # 應用情感參數（如果提供）
        if emotion:
            self.apply_emotion(emotion)
    
    def apply_emotion(self, emotion):
        """應用情感參數調整（由語言模型動態生成）"""
        # 這裡保留空實現，由語言模型在運行時動態生成風格參數
        pass
    
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
            
            # 根據和聲複雜度可能添加七度音
            if self.params.get("harmonic_complexity", 0.5) > 0.7:
                if chord_type == "major":
                    chord.append(root_note + 11)  # 大七度
                elif chord_type == "minor":
                    chord.append(root_note + 10)  # 小七度
                elif chord_type == "diminished":
                    chord.append(root_note + 9)   # 減七度
            
            chord_progression.append(chord)
        
        return chord_progression
    
    def validate_melody_with_chords(self, melody_notes, chord_progression):
        """校驗旋律與和弦的關係"""
        issues = []
        suggestions = []
        
        current_chord_idx = 0
        chord_duration = 4  # 默認每個和弦持續4拍
        
        for i, note in enumerate(melody_notes):
            # 判斷當前音符對應哪個和弦
            chord_idx = min(int(i / chord_duration), len(chord_progression) - 1)
            if chord_idx != current_chord_idx:
                current_chord_idx = chord_idx
            
            current_chord = chord_progression[current_chord_idx]
            
            # 旋律音符與和弦的相對關係
            relative_pitch = note % 12  # 將所有音符轉換到一個八度內
            chord_pitches = [p % 12 for p in current_chord]  # 和弦音也轉換到一個八度
            
            # 判斷音符與和弦的關係類型
            relationship = "tension"  # 默認為張力音
            
            # 檢查是否為和弦音
            for interval in TONE_CHORD_RELATIONSHIPS["stable"]["intervals"]:
                for root in chord_pitches:
                    if (root + interval) % 12 == relative_pitch:
                        relationship = "stable"
                        break
            
            # 如果不是和弦音，檢查是否為色彩音
            if relationship == "tension":
                for interval in TONE_CHORD_RELATIONSHIPS["color"]["intervals"]:
                    for root in chord_pitches:
                        if (root + interval) % 12 == relative_pitch:
                            relationship = "color"
                            break
            
            # 對於重要拍點上的張力音（如小節的第一拍），提出建議
            if relationship == "tension" and i % 4 == 0:  # 假設每小節有4拍，第一拍為重拍
                issues.append(f"音符 {note} 在第 {i//4 + 1} 小節的重拍上是張力音")
                better_note = self.suggest_better_note(note, current_chord)
                suggestions.append(f"建議將音符 {note} 改為 {better_note}")
        
        return issues, suggestions
    
    def suggest_better_note(self, note, chord):
        """基於和弦建議更好的音符"""
        # 將音符轉換到一個八度內
        relative_pitch = note % 12
        octave = note // 12
        
        # 尋找最近的和弦音
        min_distance = 12
        best_note = note
        
        for chord_note in chord:
            chord_relative = chord_note % 12
            distance = min((chord_relative - relative_pitch) % 12, (relative_pitch - chord_relative) % 12)
            
            if distance < min_distance:
                min_distance = distance
                best_note = octave * 12 + chord_relative
        
        return best_note

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