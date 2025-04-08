#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
獨立音樂應用程序
這是一個更簡單的音樂創建應用程序，專注於基本功能及風格模型微調。
整合高品質開源合成器與智能音色選擇系統。
新增高級參數調節、音樂張力曲線編輯和用戶風格記憶庫功能。
"""

from midiutil import MIDIFile
import os
import random
import json
import numpy as np
import time
import pickle
from datetime import datetime
try:
    import pretty_midi
except ImportError:
    print("請安裝必要的庫: pip install pretty_midi python-rtmidi")

# 添加風格模型參數定義
STYLE_PRESETS = {
    "古典": {
        "tempo_range": (70, 100),
        "scale": [60, 62, 64, 65, 67, 69, 71, 72],  # C大調自然音階
        "octave_range": (4, 6),
        "duration_options": [0.25, 0.5, 1, 2],  # 四分之一拍、八分之一拍等
        "velocity_range": (60, 90),
        "arpeggios": True,
        "chord_progression": [[60, 64, 67], [67, 71, 74], [65, 69, 72], [60, 64, 67]],  # I-V-IV-I和弦進行
        "temperature": 0.3,  # 較低的創新性，高度結構化
        "recommended_timbres": ["grand_piano", "string_ensemble", "flute", "clarinet"],
        "rhythm_complexity": 0.3,  # 節奏複雜度 (0-1)
        "harmony_richness": 0.7,  # 和聲豐富度 (0-1)
        "note_density": 0.5,  # 音符密度 (0-1)
        "velocity_dynamics": 0.4  # 力度變化 (0-1)
    },
    "爵士": {
        "tempo_range": (100, 140),
        "scale": [60, 62, 63, 65, 67, 68, 70, 72],  # C多利亞調式 (藍調音階)
        "octave_range": (3, 6),
        "duration_options": [0.125, 0.25, 0.33, 0.5, 0.75],  # 更多不規則節奏
        "velocity_range": (50, 110),
        "swing": True,
        "chord_progression": [[60, 63, 67, 70], [65, 68, 72, 75], [67, 70, 74, 77], [58, 62, 65, 68]],  # 7和弦進行
        "temperature": 0.7,  # 高創新性，較低結構性
        "recommended_timbres": ["saxophone", "electric_piano", "double_bass", "jazz_guitar"],
        "rhythm_complexity": 0.8,  # 節奏複雜度 (0-1)
        "harmony_richness": 0.9,  # 和聲豐富度 (0-1)
        "note_density": 0.7,  # 音符密度 (0-1)
        "velocity_dynamics": 0.8  # 力度變化 (0-1)
    },
    "流行": {
        "tempo_range": (90, 130),
        "scale": [60, 62, 64, 65, 67, 69, 71, 72],  # C大調
        "octave_range": (4, 5),
        "duration_options": [0.25, 0.5, 1],
        "velocity_range": (70, 100),
        "repetitive": True,
        "chord_progression": [[60, 64, 67], [65, 69, 72], [57, 60, 64], [67, 71, 74]],  # I-IV-vi-V和弦進行
        "temperature": 0.5,  # 平衡創新與結構
        "recommended_timbres": ["synth_pad", "electric_guitar", "synth_lead", "pop_bass"],
        "rhythm_complexity": 0.5,  # 節奏複雜度 (0-1)
        "harmony_richness": 0.6,  # 和聲豐富度 (0-1)
        "note_density": 0.6,  # 音符密度 (0-1)
        "velocity_dynamics": 0.5  # 力度變化 (0-1)
    },
    "電子": {
        "tempo_range": (120, 160),
        "scale": [60, 62, 64, 67, 69, 72],  # C 五聲音階
        "octave_range": (3, 7),
        "duration_options": [0.125, 0.25, 0.5],
        "velocity_range": (80, 127),
        "repetitive": True,
        "chord_progression": [[60, 64, 67], [60, 65, 67], [60, 67, 71], [60, 65, 69]],
        "temperature": 0.6,
        "recommended_timbres": ["synth_bass", "fm_lead", "arp_synth", "dance_pad"],
        "rhythm_complexity": 0.7,  # 節奏複雜度 (0-1)
        "harmony_richness": 0.5,  # 和聲豐富度 (0-1)
        "note_density": 0.8,  # 音符密度 (0-1)
        "velocity_dynamics": 0.6  # 力度變化 (0-1)
    }
}

# 高級參數定義 - 用於精細控制
ADVANCED_PARAMETERS = {
    "rhythm_complexity": {
        "description": "控制節奏的複雜程度，較高值會產生更多變化和不規則的節奏",
        "min": 0.0,
        "max": 1.0,
        "default": 0.5,
        "step": 0.1
    },
    "harmony_richness": {
        "description": "控制和聲的豐富度，較高值會使用更多的和弦類型和轉位",
        "min": 0.0,
        "max": 1.0,
        "default": 0.5,
        "step": 0.1
    },
    "note_density": {
        "description": "控制音符的密度，較高值會產生更多的音符",
        "min": 0.0,
        "max": 1.0,
        "default": 0.5,
        "step": 0.1
    },
    "velocity_dynamics": {
        "description": "控制音量變化的範圍，較高值會產生更豐富的力度動態",
        "min": 0.0,
        "max": 1.0,
        "default": 0.5,
        "step": 0.1
    }
}

# 張力曲線預設
TENSION_CURVES = {
    "標準起伏": [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.7, 0.6, 0.5, 0.6, 0.7, 0.8, 0.9, 0.7, 0.5, 0.3],
    "漸強": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.0, 1.0, 0.9, 0.8, 0.7, 0.6],
    "起伏波動": [0.5, 0.3, 0.7, 0.4, 0.8, 0.5, 0.9, 0.6, 0.4, 0.7, 0.3, 0.8, 0.5, 0.9, 0.4, 0.2],
    "平穩": [0.5, 0.5, 0.6, 0.6, 0.5, 0.5, 0.6, 0.6, 0.5, 0.5, 0.6, 0.6, 0.5, 0.5, 0.4, 0.4],
    "高潮式": [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.3]
}

# 合成器定義
SYNTHESIZER_PRESETS = {
    # Dexed (DX7 模擬器) 音色
    "dexed": {
        "grand_piano": {
            "algorithm": 5,
            "feedback": 3,
            "operators": [
                {"frequency": 1.0, "level": 90, "attack": 0, "decay": 30, "sustain": 70, "release": 15},
                {"frequency": 2.0, "level": 75, "attack": 0, "decay": 35, "sustain": 60, "release": 20},
                {"frequency": 3.0, "level": 60, "attack": 5, "decay": 40, "sustain": 50, "release": 25},
                {"frequency": 4.0, "level": 40, "attack": 10, "decay": 45, "sustain": 40, "release": 30},
            ]
        },
        "electric_piano": {
            "algorithm": 6,
            "feedback": 5,
            "operators": [
                {"frequency": 1.0, "level": 85, "attack": 0, "decay": 40, "sustain": 65, "release": 30},
                {"frequency": 2.1, "level": 70, "attack": 5, "decay": 45, "sustain": 55, "release": 25},
                {"frequency": 14.0, "level": 30, "attack": 0, "decay": 10, "sustain": 10, "release": 10},
                {"frequency": 1.0, "level": 20, "attack": 20, "decay": 30, "sustain": 0, "release": 30}
            ]
        },
        "fm_lead": {
            "algorithm": 3,
            "feedback": 7,
            "operators": [
                {"frequency": 1.0, "level": 99, "attack": 0, "decay": 20, "sustain": 80, "release": 20},
                {"frequency": 2.0, "level": 80, "attack": 10, "decay": 30, "sustain": 60, "release": 25},
                {"frequency": 4.0, "level": 60, "attack": 0, "decay": 40, "sustain": 40, "release": 30},
                {"frequency": 8.0, "level": 40, "attack": 5, "decay": 20, "sustain": 20, "release": 20}
            ]
        }
    },
    
    # OctaSine FM 合成器參數
    "octasine": {
        "synth_bass": {
            "operators": [
                {"ratio": 1.0, "level": 0.9, "attack": 0.01, "decay": 0.2, "sustain": 0.5, "release": 0.3},
                {"ratio": 2.0, "level": 0.6, "attack": 0.0, "decay": 0.3, "sustain": 0.0, "release": 0.2},
            ],
            "modulation_matrix": [[0, 0], [0.8, 0]]
        },
        "synth_pad": {
            "operators": [
                {"ratio": 1.0, "level": 0.7, "attack": 0.5, "decay": 1.0, "sustain": 0.8, "release": 2.0},
                {"ratio": 1.01, "level": 0.5, "attack": 0.7, "decay": 0.8, "sustain": 0.7, "release": 1.5},
                {"ratio": 2.0, "level": 0.3, "attack": 1.0, "decay": 0.5, "sustain": 0.4, "release": 1.8},
            ],
            "modulation_matrix": [[0, 0, 0], [0.3, 0, 0], [0.2, 0.1, 0]]
        }
    },
    
    # Helm 合成器參數
    "helm": {
        "arp_synth": {
            "oscillator": {"type": "saw", "unison": 4, "unison_detune": 10},
            "filter": {"type": "ladder", "cutoff": 80, "resonance": 0.3},
            "envelope": {"attack": 0.01, "decay": 0.2, "sustain": 0.5, "release": 0.3},
            "effects": {"reverb": 0.2, "delay": 0.3, "delay_sync": True}
        },
        "synth_lead": {
            "oscillator": {"type": "square", "unison": 2, "unison_detune": 5},
            "filter": {"type": "ladder", "cutoff": 100, "resonance": 0.1},
            "envelope": {"attack": 0.05, "decay": 0.1, "sustain": 0.7, "release": 0.2},
            "effects": {"distortion": 0.2, "reverb": 0.15}
        }
    },
    
    # Surge 合成器參數
    "surge": {
        "string_ensemble": {
            "oscillator": {"type": "wavetable", "table": "string", "unison": 8},
            "filter": {"type": "bandpass", "cutoff": 2000, "resonance": 0.2, "keytrack": 0.5},
            "envelope": {"attack": 0.3, "decay": 0.5, "sustain": 0.8, "release": 1.0},
            "effects": {"chorus": 0.5, "reverb": 0.4}
        },
        "dance_pad": {
            "oscillator": {"type": "wavetable", "table": "modern", "unison": 3},
            "filter": {"type": "comb", "cutoff": 4000, "resonance": 0.4, "keytrack": 0.3},
            "envelope": {"attack": 0.2, "decay": 0.7, "sustain": 0.6, "release": 1.5},
            "effects": {"phaser": 0.3, "reverb": 0.35, "delay": 0.2}
        }
    }
}

# 音色情感關鍵詞映射
EMOTION_TIMBRE_MAP = {
    "明亮": ["synth_lead", "electric_piano", "grand_piano"],
    "溫暖": ["synth_pad", "string_ensemble", "jazz_guitar"],
    "柔和": ["flute", "synth_pad", "string_ensemble"],
    "強勁": ["electric_guitar", "synth_bass", "fm_lead"],
    "夢幻": ["synth_pad", "dance_pad", "arp_synth"],
    "悠揚": ["saxophone", "clarinet", "flute"],
    "深沉": ["double_bass", "synth_bass", "pop_bass"],
    "活潑": ["arp_synth", "electric_piano", "synth_lead"]
}

# 用戶風格記憶庫路徑
USER_STYLE_DB_PATH = os.path.join(os.path.expanduser("~"), ".music_style_db")
USER_STYLE_FILE = os.path.join(USER_STYLE_DB_PATH, "user_styles.pickle")

# 確保用戶風格目錄存在
if not os.path.exists(USER_STYLE_DB_PATH):
    os.makedirs(USER_STYLE_DB_PATH)

class UserStyleManager:
    """管理用戶風格記憶庫的類"""
    
    def __init__(self):
        self.style_db = self._load_style_db()
        self.current_style = None
    
    def _load_style_db(self):
        """從文件加載用戶風格數據庫"""
        if os.path.exists(USER_STYLE_FILE):
            try:
                with open(USER_STYLE_FILE, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"載入用戶風格數據庫時出錯: {e}")
                return {"styles": {}, "history": []}
        return {"styles": {}, "history": []}
    
    def save_style_db(self):
        """保存用戶風格數據庫到文件"""
        try:
            with open(USER_STYLE_FILE, 'wb') as f:
                pickle.dump(self.style_db, f)
            print("用戶風格數據庫已保存")
        except Exception as e:
            print(f"保存用戶風格數據庫時出錯: {e}")
    
    def add_style(self, name, params):
        """添加或更新用戶風格"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.style_db["styles"][name] = {
            "params": params,
            "created": timestamp,
            "updated": timestamp,
            "used_count": 0
        }
        self.save_style_db()
    
    def get_style(self, name):
        """獲取指定名稱的用戶風格"""
        if name in self.style_db["styles"]:
            style = self.style_db["styles"][name]
            # 更新使用次數
            style["used_count"] += 1
            style["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.save_style_db()
            return style["params"]
        return None
    
    def list_styles(self):
        """列出所有用戶風格"""
        return list(self.style_db["styles"].keys())
    
    def add_to_history(self, params):
        """添加風格參數到歷史記錄"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history_entry = {
            "params": params,
            "timestamp": timestamp
        }
        self.style_db["history"].append(history_entry)
        # 限制歷史記錄數量為最近的50個
        if len(self.style_db["history"]) > 50:
            self.style_db["history"] = self.style_db["history"][-50:]
        self.save_style_db()
    
    def get_style_evolution(self, base_style_name, evolution_degree=0.3):
        """獲取風格的演變版本"""
        base_style = self.get_style(base_style_name)
        if not base_style:
            return None
        
        # 創建風格的演變版本，保持一些原始特性但引入新的變化
        evolved_style = base_style.copy()
        
        # 對每個參數進行演變
        for param in ["rhythm_complexity", "harmony_richness", "note_density", "velocity_dynamics"]:
            if param in evolved_style:
                # 在原始值基礎上增加一些隨機變化
                variation = (random.random() * 2 - 1) * evolution_degree
                new_value = evolved_style[param] + variation
                # 確保值在有效範圍內
                evolved_style[param] = max(0, min(1, new_value))
        
        return evolved_style
    
    def analyze_preferences(self):
        """分析用戶偏好並返回推薦的參數值"""
        if not self.style_db["history"]:
            return None
        
        # 計算每個參數的平均值
        param_totals = {}
        param_counts = {}
        
        for entry in self.style_db["history"]:
            params = entry["params"]
            for param, value in params.items():
                if isinstance(value, (int, float)):  # 只分析數值參數
                    param_totals[param] = param_totals.get(param, 0) + value
                    param_counts[param] = param_counts.get(param, 0) + 1
        
        # 計算平均值
        preferences = {}
        for param, total in param_totals.items():
            if param_counts[param] > 0:
                preferences[param] = total / param_counts[param]
        
        return preferences

class TensionCurveEditor:
    """音樂張力曲線編輯器"""
    
    def __init__(self, preset_name=None, num_points=16):
        self.num_points = num_points
        self.curve = self._load_preset(preset_name) if preset_name else [0.5] * num_points
    
    def _load_preset(self, preset_name):
        """載入預設張力曲線"""
        if preset_name in TENSION_CURVES:
            return TENSION_CURVES[preset_name].copy()
        return [0.5] * self.num_points
    
    def set_point(self, index, value):
        """設置特定點的張力值"""
        if 0 <= index < self.num_points:
            self.curve[index] = max(0, min(1, value))  # 確保值在0-1範圍內
    
    def get_point(self, index):
        """獲取特定點的張力值"""
        if 0 <= index < self.num_points:
            return self.curve[index]
        return None
    
    def get_curve(self):
        """獲取完整張力曲線"""
        return self.curve.copy()
    
    def save_as_preset(self, name):
        """將當前曲線保存為預設"""
        TENSION_CURVES[name] = self.curve.copy()
    
    def apply_to_generation(self, notes, durations, velocities):
        """將張力曲線應用於生成的音符"""
        if not notes or len(notes) == 0:
            return notes, durations, velocities
        
        modified_velocities = velocities.copy()
        
        # 根據曲線長度將音符分段
        segment_size = max(1, len(notes) // len(self.curve))
        
        for i, tension in enumerate(self.curve):
            start_idx = i * segment_size
            end_idx = min(start_idx + segment_size, len(notes))
            
            if start_idx >= len(notes):
                break
            
            # 根據張力值調整該段音符的力度
            for j in range(start_idx, end_idx):
                # 張力越高，力度越大，但保持原始力度的一些特性
                base_velocity = modified_velocities[j]
                tension_factor = 0.5 + tension * 0.5  # 張力對力度的影響範圍為50%-100%
                modified_velocities[j] = int(base_velocity * tension_factor)
                # 確保在MIDI範圍內(0-127)
                modified_velocities[j] = max(30, min(127, modified_velocities[j]))
        
        return notes, durations, modified_velocities

def apply_advanced_parameters(notes, durations, velocities, params):
    """應用高級參數到生成的音符序列"""
    modified_notes = notes.copy()
    modified_durations = durations.copy()
    modified_velocities = velocities.copy()
    
    # 1. 應用節奏複雜度
    if "rhythm_complexity" in params:
        complexity = params["rhythm_complexity"]
        for i in range(len(modified_durations)):
            if random.random() < complexity * 0.5:  # 複雜度越高，越可能修改節奏
                # 添加附點或切分
                if random.random() < 0.5:
                    modified_durations[i] *= 1.5  # 附點節奏
                else:
                    modified_durations[i] *= 0.75  # 切分節奏
    
    # 2. 應用和聲豐富度
    if "harmony_richness" in params:
        richness = params["harmony_richness"]
        new_notes = []
        new_durations = []
        new_velocities = []
        
        for i in range(len(modified_notes)):
            new_notes.append(modified_notes[i])
            new_durations.append(modified_durations[i])
            new_velocities.append(modified_velocities[i])
            
            # 根據和聲豐富度添加和弦音
            if random.random() < richness * 0.4:  # 豐富度越高，越可能添加和弦音
                # 添加三度和五度和弦音
                chord_notes = [modified_notes[i], modified_notes[i] + 4, modified_notes[i] + 7]
                for chord_note in chord_notes[1:]:  # 跳過根音，已經添加過
                    new_notes.append(chord_note)
                    new_durations.append(modified_durations[i])
                    # 和弦音的力度略低於主音
                    new_velocities.append(int(modified_velocities[i] * 0.8))
        
        modified_notes = new_notes
        modified_durations = new_durations
        modified_velocities = new_velocities
    
    # 3. 應用音符密度
    if "note_density" in params:
        density = params["note_density"]
        # 根據密度參數調整音符數量
        target_count = int(len(notes) * (0.5 + density * 1.0))  # 密度越高，音符數量越多
        
        if target_count > len(modified_notes):
            # 需要增加音符
            additional_count = target_count - len(modified_notes)
            
            for _ in range(additional_count):
                if not modified_notes:  # 確保列表不為空
                    break
                
                # 隨機選擇一個位置插入新音符
                insert_idx = random.randint(0, len(modified_notes) - 1)
                
                # 基於現有音符創建變化
                base_note = modified_notes[insert_idx]
                new_note = base_note + random.choice([-2, -1, 1, 2])  # 小的音高變化
                
                modified_notes.insert(insert_idx, new_note)
                modified_durations.insert(insert_idx, modified_durations[insert_idx] * 0.5)  # 新音符持續時間減半
                modified_velocities.insert(insert_idx, modified_velocities[insert_idx])
                
                # 原音符持續時間也減半
                modified_durations[insert_idx+1] *= 0.5
                
        elif target_count < len(modified_notes) and len(modified_notes) > 4:  # 確保至少保留一些音符
            # 需要減少音符
            while len(modified_notes) > target_count:
                # 隨機選擇一個音符移除
                remove_idx = random.randint(0, len(modified_notes) - 1)
                
                if remove_idx + 1 < len(modified_notes):
                    # 將下一個音符的持續時間增加
                    modified_durations[remove_idx + 1] += modified_durations[remove_idx]
                
                modified_notes.pop(remove_idx)
                modified_durations.pop(remove_idx)
                modified_velocities.pop(remove_idx)
    
    # 4. 應用力度變化
    if "velocity_dynamics" in params:
        dynamics = params["velocity_dynamics"]
        
        # 創建力度輪廓
        base_velocity = sum(modified_velocities) / len(modified_velocities) if modified_velocities else 80
        velocity_range = 40 * dynamics  # 動態範圍基於參數值
        
        # 應用漸強漸弱模式或其他模式
        pattern_type = random.choice(["crescendo", "wave", "random"])
        
        if pattern_type == "crescendo":
            # 漸強然後漸弱
            mid_point = len(modified_velocities) // 2
            for i in range(len(modified_velocities)):
                if i < mid_point:
                    # 漸強部分
                    factor = i / mid_point
                    modified_velocities[i] = int(base_velocity + velocity_range * factor * dynamics)
                else:
                    # 漸弱部分
                    factor = (len(modified_velocities) - i) / (len(modified_velocities) - mid_point)
                    modified_velocities[i] = int(base_velocity + velocity_range * factor * dynamics)
        
        elif pattern_type == "wave":
            # 波浪形力度變化
            for i in range(len(modified_velocities)):
                wave_pos = (i / len(modified_velocities)) * 2 * np.pi
                wave_factor = 0.5 + 0.5 * np.sin(wave_pos * 2)  # 2週期的正弦波
                modified_velocities[i] = int(base_velocity + velocity_range * wave_factor * dynamics)
        
        else:  # random
            # 隨機力度變化，但保持一定的連續性
            current_velocity = base_velocity
            for i in range(len(modified_velocities)):
                # 添加一些隨機變化
                change = random.uniform(-10, 10) * dynamics
                current_velocity += change
                # 確保力度在合理範圍內並緩慢回歸到基準值
                current_velocity = current_velocity * 0.9 + base_velocity * 0.1
                modified_velocities[i] = int(current_velocity)
        
        # 確保所有力度值在MIDI範圍內(0-127)
        for i in range(len(modified_velocities)):
            modified_velocities[i] = max(30, min(127, modified_velocities[i]))
    
    return modified_notes, modified_durations, modified_velocities

def apply_temperature(value, base_value, temperature):
    """基於溫度參數對值進行變化，溫度越高變化越大"""
    max_deviation = base_value * 0.5  # 最大偏差為基礎值的50%
    deviation = max_deviation * temperature * (random.random() * 2 - 1)
    return int(base_value + deviation)

def analyze_timbre_requirements(description):
    """分析輸入描述，提取可能的音色需求"""
    description = description.lower()
    matched_emotions = []
    
    for emotion, timbres in EMOTION_TIMBRE_MAP.items():
        if emotion in description:
            matched_emotions.append(emotion)
    
    # 如果沒有匹配情感，使用默認音色
    if not matched_emotions:
        return None
    
    # 從匹配的情感中選擇推薦音色
    recommended_timbres = []
    for emotion in matched_emotions:
        recommended_timbres.extend(EMOTION_TIMBRE_MAP[emotion])
    
    # 去除重複並返回前三個
    unique_timbres = list(dict.fromkeys(recommended_timbres))
    return unique_timbres[:3]

def get_synthesizer_preset(timbre_name):
    """根據音色名稱獲取適當的合成器預設"""
    # 檢查每個合成器是否有指定音色
    for synth_name, presets in SYNTHESIZER_PRESETS.items():
        if timbre_name in presets:
            return synth_name, presets[timbre_name]
    
    # 沒有找到匹配的預設，返回默認值
    return None, None

def export_midi_with_timbre(midi_filename, output_filename, timbre_name=None):
    """將MIDI轉換為包含音色信息的格式"""
    # 如果沒有提供音色名稱，使用隨機音色
    if timbre_name is None:
        all_timbres = []
        for presets in SYNTHESIZER_PRESETS.values():
            all_timbres.extend(list(presets.keys()))
        timbre_name = random.choice(all_timbres)
    
    # 獲取對應的合成器預設
    synth_name, preset = get_synthesizer_preset(timbre_name)
    
    if synth_name is None:
        print(f"未找到音色 '{timbre_name}' 的合成器預設，使用默認音色")
        synth_name = list(SYNTHESIZER_PRESETS.keys())[0]
        preset = list(SYNTHESIZER_PRESETS[synth_name].values())[0]
    
    # 載入MIDI文件
    try:
        midi_data = pretty_midi.PrettyMIDI(midi_filename)
        
        # 添加音色元數據
        metadata = {
            "synthesizer": synth_name,
            "timbre": timbre_name,
            "preset": preset
        }
        
        # 在MIDI文件中添加元數據作為文本事件
        for instrument in midi_data.instruments:
            # 將元數據轉換為JSON字符串
            meta_json = json.dumps(metadata)
            # 創建文本元數據事件
            text_event = pretty_midi.TextMetaEvent(
                text=f"TIMBRE_DATA:{meta_json}", 
                time=0.0
            )
            instrument.text_events.append(text_event)
        
        # 保存帶有音色信息的MIDI文件
        midi_data.write(output_filename)
        print(f"已將 MIDI 文件導出為 {output_filename}，包含 {synth_name}/{timbre_name} 音色信息")
        return output_filename
        
    except Exception as e:
        print(f"處理 MIDI 文件時出錯: {e}")
        return None

def create_midi_with_style(style="古典", filename=None, custom_temperature=None, timbre_description=None, 
                       advanced_params=None, tension_curve=None, user_style_manager=None):
    """創建特定風格的MIDI文件，具有風格模型微調和音色選擇，並支持高級參數控制、張力曲線和多音軌"""
    
    if style not in STYLE_PRESETS:
        print(f"未知風格: {style}，使用預設的'古典'風格")
        style = "古典"
    
    # 獲取風格預設參數
    preset = STYLE_PRESETS[style].copy()
    
    # 整合高級參數 - 確保所有高級參數都被正確合併到預設中
    if advanced_params:
        for key, value in advanced_params.items():
            preset[key] = value  # 接受所有參數
    
    # 如果提供自定義溫度，則覆蓋預設值
    temperature = custom_temperature if custom_temperature is not None else preset.get("temperature", 0.5)
    
    # 檔案名稱
    if filename is None:
        filename = f"{style}_music_output.mid"
    
    # 從預設或高級參數中提取所有需要的參數，設置默認值
    rhythm_complexity = preset.get("rhythm_complexity", 0.5)
    harmony_richness = preset.get("harmony_richness", 0.5)
    note_density = preset.get("note_density", 0.5)
    velocity_dynamics = preset.get("velocity_dynamics", 0.5)
    
    # 設置曲速參數
    tempo_range = preset.get("tempo_range", (80, 120))
    tempo_min, tempo_max = tempo_range
    tempo_span = tempo_max - tempo_min
    
    # 根據節奏複雜度調整曲速
    if rhythm_complexity > 0.7:
        tempo_min = int(tempo_min * 1.1)
        tempo_max = int(tempo_max * 1.1)
    elif rhythm_complexity < 0.3:
        tempo_min = int(tempo_min * 0.9)
        tempo_max = int(tempo_max * 0.9)
    
    # 根據參數計算最終曲速，但保留一定隨機性
    random_factor = random.random() * temperature
    tempo = int(tempo_min + (tempo_span * ((rhythm_complexity * 0.7) + (random_factor * 0.3))))
    tempo = max(60, min(200, tempo))
    
    # 音階和和弦進行
    scale = preset.get("scale", [60, 62, 64, 65, 67, 69, 71, 72])  # 預設 C大調
    octave_range = preset.get("octave_range", (4, 5))
    octave_min, octave_max = octave_range
    chord_progression = preset.get("chord_progression", [[60, 64, 67], [65, 69, 72], [67, 71, 74], [60, 64, 67]])
    
    # 使用持續時間選項，根據節奏複雜度調整
    duration_options = preset.get("duration_options", [0.25, 0.5, 1.0])
    if rhythm_complexity > 0.7:
        duration_options = sorted(set(duration_options + [0.125, 0.33, 0.75]))
    elif rhythm_complexity < 0.3:
        duration_options = sorted([d for d in duration_options if d in [0.25, 0.5, 1.0, 2.0]])
    
    # 獲取張力曲線
    tension_editor = TensionCurveEditor()
    if tension_curve:
        if isinstance(tension_curve, str) and tension_curve in TENSION_CURVES:
            tension_editor = TensionCurveEditor(preset_name=tension_curve)
        elif isinstance(tension_curve, list):
            tension_editor.curve = tension_curve.copy()
    else:
        tension_editor = TensionCurveEditor(preset_name="標準起伏")
    tension_values = tension_editor.get_curve()
    
    # 創建多軌MIDI對象 - 4軌：旋律、和弦、低音和節奏
    num_tracks = 4
    midi = MIDIFile(num_tracks)
    
    # 設置每個音軌的名稱和音量
    track_names = ["旋律", "和弦", "低音", "節奏"]
    track_volumes = [100, 90, 95, 85]  # 默認音量
    
    # 根據風格調整音軌音量
    if style == "爵士":
        track_volumes = [95, 85, 100, 90]  # 爵士低音更突出
    elif style == "電子":
        track_volumes = [90, 85, 100, 110]  # 電子風格節奏更強
    
    # 設置曲速和音軌信息
    for i in range(num_tracks):
        midi.addTempo(i, 0, tempo)
        try:
            midi.addTrackName(i, 0, track_names[i])
        except AttributeError:
            # 如果MIDIFile不支持addTrackName方法，則忽略
            pass
    
    # 計算總小節數 - 根據音符密度和風格調整
    base_bars = 8
    if note_density > 0.7:
        base_bars = 12
    elif note_density < 0.3:
        base_bars = 6
    
    # 根據張力曲線調整總長度
    tension_factor = sum(tension_values) / len(tension_values)  # 平均張力
    total_bars = max(4, int(base_bars * (0.8 + tension_factor * 0.4)))
    
    # 生成每個音軌
    melody_track = 0
    chord_track = 1
    bass_track = 2
    rhythm_track = 3
    
    # 1. 生成和弦進行 - 作為基礎
    chord_sequence = []
    # 根據總小節數擴展和弦進行
    for _ in range(total_bars // len(chord_progression) + 1):
        chord_sequence.extend(chord_progression)
    chord_sequence = chord_sequence[:total_bars]
    
    # 2. 生成低音聲部 - 主要使用和弦的根音
    bass_notes = []
    bass_durations = []
    bass_velocities = []
    bass_time = 0
    
    for bar_idx, chord in enumerate(chord_sequence):
        # 根據和聲豐富度決定低音音符複雜性
        if harmony_richness > 0.7:
            # 複雜的低音走向，可能使用和弦中的其他音
            notes_per_bar = 4
            if random.random() < 0.3:
                notes_per_bar = 2 if random.random() < 0.5 else 8
        elif harmony_richness < 0.3:
            # 簡單的低音走向，主要是根音
            notes_per_bar = 1
            if random.random() < 0.3:
                notes_per_bar = 2
            else:
                # 中等複雜度
                notes_per_bar = 2
                if random.random() < 0.4:
                    notes_per_bar = 4
        
        # 為每個小節生成低音音符
        bar_duration = 4.0 / notes_per_bar  # 4拍一小節
        root_note = chord[0] - 24  # 低音區域
        
        for note_idx in range(notes_per_bar):
            # 有時使用五度音或和弦的其他音
            if random.random() < harmony_richness * 0.3 and len(chord) > 1:
                if random.random() < 0.7:
                    # 使用和弦的第五音
                    bass_note = root_note + 7
                else:
                    # 使用和弦的其他音
                    chord_tone_idx = random.randint(1, len(chord) - 1)
                    bass_note = chord[chord_tone_idx] - 24
            else:
                bass_note = root_note
            
            # 根據張力添加一些變化
            current_tension = tension_values[min(bar_idx % len(tension_values), len(tension_values) - 1)]
            bass_velocity = int(70 + current_tension * 30)
            
            # 有時添加切分音或稍微變化節奏
            actual_duration = bar_duration
            if rhythm_complexity > 0.6 and random.random() < 0.3:
                actual_duration *= 0.75 if random.random() < 0.5 else 1.5
            
            bass_notes.append(bass_note)
            bass_durations.append(actual_duration)
            bass_velocities.append(bass_velocity)
    
    # 3. 生成和弦聲部
    chord_notes = []
    chord_durations = []
    chord_velocities = []
    chord_time = 0
    
    for bar_idx, chord in enumerate(chord_sequence):
        # 根據和聲豐富度決定和弦複雜性
        chord_density = 1  # 每小節的和弦數
        
        if harmony_richness > 0.7:
            # 更多的和弦變化
            if random.random() < 0.6:
                chord_density = 2
            if random.random() < 0.3:
                chord_density = 4
        elif harmony_richness < 0.3:
            # 簡單的和弦，每小節一個
            chord_density = 1
        else:
            # 中等複雜度
            if random.random() < 0.4:
                chord_density = 2
        
        # 當前張力值
        current_tension = tension_values[min(bar_idx % len(tension_values), len(tension_values) - 1)]
        
        # 為每個小節生成和弦
        bar_duration = 4.0 / chord_density  # 4拍一小節
        
        for _ in range(chord_density):
            # 根據和弦豐富度決定是否添加額外音
            if harmony_richness > 0.6 and random.random() < 0.4:
                # 添加七度或九度
                extended_chord = chord.copy()
                if random.random() < 0.7:
                    # 添加七度
                    extended_chord.append(chord[0] + 10)
                else:
                    # 添加九度
                    extended_chord.append(chord[0] + 14)
                current_chord = extended_chord
            else:
                current_chord = chord
            
            # 根據風格調整和弦型態
            if style == "爵士" and random.random() < 0.5:
                # 爵士風格常用的和弦轉位或張力和弦
                if random.random() < 0.5:
                    # 使用和弦轉位
                    current_chord = current_chord[1:] + [current_chord[0] + 12]
                else:
                    # 添加不協和音
                    tension_note = current_chord[0] + random.choice([1, 6, 10, 13])
                    current_chord.append(tension_note)
            
            # 和弦力度受張力影響
            chord_velocity = int(60 + current_tension * 30)
            
            # 創建和弦音
            for chord_note in current_chord:
                chord_notes.append(chord_note)
                chord_durations.append(bar_duration)
                chord_velocities.append(chord_velocity)
    
    # 4. 生成旋律聲部
    melody_notes = []
    melody_durations = []
    melody_velocities = []
    melody_time = 0
    
    # 預先計算每個小節的張力值
    bar_tensions = []
    for bar_idx in range(total_bars):
        tension_idx = min(bar_idx % len(tension_values), len(tension_values) - 1)
        bar_tensions.append(tension_values[tension_idx])
    
    # 計算旋律總音符數
    base_notes_per_bar = 4
    melody_notes_count = 0
    
    for bar_idx in range(total_bars):
        # 根據音符密度和張力調整每個小節的音符數
        current_tension = bar_tensions[bar_idx]
        
        if note_density > 0.7:
            # 高密度
            notes_in_bar = random.randint(4, 8)
            if current_tension > 0.7:
                notes_in_bar = random.randint(6, 10)
        elif note_density < 0.3:
            # 低密度
            notes_in_bar = random.randint(2, 4)
            if current_tension < 0.3:
                notes_in_bar = random.randint(1, 3)
        else:
            # 中等密度
            notes_in_bar = random.randint(3, 6)
            if current_tension > 0.7:
                notes_in_bar += 2
            elif current_tension < 0.3:
                notes_in_bar -= 1
        
        notes_in_bar = max(1, notes_in_bar)
        melody_notes_count += notes_in_bar
        
        # 當前小節的和弦
        current_chord = chord_sequence[bar_idx]
        
        # 為這個小節生成旋律音符
        bar_duration = 4.0  # 4拍一小節
        note_duration = bar_duration / notes_in_bar
        
        for note_idx in range(notes_in_bar):
            # 根據和聲豐富度和張力決定音符選擇
            use_chord_tone = random.random() < (0.4 + harmony_richness * 0.4 + current_tension * 0.2)
            
            if use_chord_tone:
                # 使用和弦音
                chord_tone_idx = random.randint(0, len(current_chord) - 1)
                base_note = current_chord[chord_tone_idx]
                
                # 根據八度範圍調整
                octave_offset = random.randint(-1, 1) * 12
                note = base_note + octave_offset
            else:
                # 使用音階音
                scale_idx = random.randint(0, len(scale) - 1)
                octave = random.randint(octave_min, octave_max)
                note = scale[scale_idx] + (octave - 4) * 12
            
            # 確保音符在合理範圍內
            while note < 48 or note > 84:
                if note < 48:
                    note += 12
                else:
                    note -= 12
            
            # 調整持續時間
            actual_duration = note_duration
            
            # 根據節奏複雜度添加變化
            if rhythm_complexity > 0.5 and random.random() < rhythm_complexity * 0.6:
                if random.random() < 0.5:
                    actual_duration *= 0.5  # 更短
                else:
                    actual_duration *= 1.5  # 更長，可能與下一個音符重疊
                    
                # 確保持續時間合理
                actual_duration = max(0.125, min(bar_duration - (note_idx * note_duration), actual_duration))
            
            # 力度基於張力和位置
            position_in_bar = note_idx / notes_in_bar
            velocity_base = 70 + int(current_tension * 30)
            
            # 第一拍通常更強
            if note_idx == 0:
                velocity_base += 10
            
            # 添加一些表現性變化
            velocity_variation = int((random.random() * 2 - 1) * 10 * velocity_dynamics)
            velocity = max(40, min(127, velocity_base + velocity_variation))
            
            melody_notes.append(note)
            melody_durations.append(actual_duration)
            melody_velocities.append(velocity)

def provide_playback_tips(filename):
    """提供關於如何播放MIDI文件的提示"""
    print("要播放此文件，請使用支持MIDI的媒體播放器")
    
    # 提供一些關於如何播放的提示
    if os.name == 'posix':  # macOS, Linux等
        print("在終端中使用以下命令嘗試播放:")
        print(f"  timidity {filename}")
        print("或")
        print(f"  fluidsynth -i {filename}")
    elif os.name == 'nt':  # Windows
        print("在Windows中，您可以雙擊MIDI文件來播放它")
        print("或者使用命令:")
        print(f"  start {filename}")

def create_simple_midi(filename="simple_output.mid", tempo=120, timbre_name=None):
    """創建一個簡單的MIDI文件，可選音色"""
    
    # 創建 MIDI 對象
    midi = MIDIFile(1)  # 只使用一個音軌
    
    track = 0
    time_pos = 0
    
    # 設置曲速
    midi.addTempo(track, time_pos, tempo)
    
    # 定義簡單的旋律
    notes = [60, 62, 64, 65, 67, 69, 71, 72, 71, 69, 67, 65, 64, 62, 60]  # C 大調上下音階
    durations = [0.5] * len(notes)  # 所有音符持續相同時間
    
    # 添加音符
    channel = 0
    volume = 100
    
    for i, pitch in enumerate(notes):
        midi.addNote(track, channel, pitch, time_pos, durations[i], volume)
        time_pos += durations[i]
    
    # 寫入MIDI文件
    with open(filename, "wb") as output_file:
        midi.writeFile(output_file)
    
    print(f"MIDI 文件已保存為 {filename}")
    
    # 如果指定了音色，導出帶有音色的文件
    if timbre_name:
        timbre_filename = f"{os.path.splitext(filename)[0]}_with_{timbre_name}.mid"
        exported_file = export_midi_with_timbre(filename, timbre_filename, timbre_name)
        if exported_file:
            return exported_file
    
    return filename

def list_available_timbres():
    """列出所有可用的音色"""
    print("可用音色列表:")
    print("=============")
    
    for synth_name, presets in SYNTHESIZER_PRESETS.items():
        print(f"\n{synth_name.upper()} 合成器音色:")
        for i, timbre_name in enumerate(presets.keys()):
            print(f"  {i+1}. {timbre_name}")
    
    print("\n情感關鍵詞映射:")
    for emotion, timbres in EMOTION_TIMBRE_MAP.items():
        print(f"  {emotion}: {', '.join(timbres)}")

def main():
    """程序主入口點"""
    print("音樂風格創作工具 (3.0版)")
    print("======================")
    print("可用風格: 古典, 爵士, 流行, 電子")
    
    # 初始化用戶風格管理器
    user_style_manager = UserStyleManager()
    
    while True:
        print("\n請選擇操作:")
        print("1. 創建風格化音樂")
        print("2. 創建簡單音樂")
        print("3. 查看可用音色列表")
        print("4. 高級參數調節")
        print("5. 音樂張力曲線編輯")
        print("6. 用戶風格管理")
        print("7. 退出")
        
        choice = input("請輸入選項 (1-7): ").strip()
        
        if choice == "1":
            style_choice = input("請選擇一種風格 (預設: 古典): ").strip()
            if not style_choice:
                style_choice = "古典"
            elif style_choice not in STYLE_PRESETS:
                print(f"未找到風格 '{style_choice}'，使用 '古典' 風格")
                style_choice = "古典"
            
            temperature_input = input("請輸入創新性參數 (0.1-1.0，預設使用風格預設值): ").strip()
            custom_temperature = None
            
            if temperature_input:
                try:
                    custom_temperature = float(temperature_input)
                    if custom_temperature < 0.1:
                        custom_temperature = 0.1
                    elif custom_temperature > 1.0:
                        custom_temperature = 1.0
                except ValueError:
                    print("無效的溫度值，使用風格預設值")
            
            timbre_description = input("請描述您想要的音色(例如：明亮、溫暖、強勁等，留空使用風格預設): ").strip()
            
            # 詢問是否使用高級參數
            use_advanced = input("是否使用高級參數? (y/n，預設: n): ").strip().lower() == 'y'
            advanced_params = {}
            
            if use_advanced:
                print("\n高級參數設置:")
                for param, info in ADVANCED_PARAMETERS.items():
                    print(f"{param}: {info['description']}")
                    print(f"  範圍: {info['min']}-{info['max']}, 預設: {info['default']}")
                    
                    # 顯示當前風格的預設值
                    style_default = STYLE_PRESETS[style_choice].get(param, info['default'])
                    print(f"  '{style_choice}'風格預設值: {style_default}")
                    
                    value_input = input(f"  請輸入值 (留空使用'{style_choice}'風格預設值 {style_default}): ").strip()
                    
                    if value_input:
                        try:
                            value = float(value_input)
                            value = max(info['min'], min(info['max'], value))
                            advanced_params[param] = value
                            print(f"  已設置 {param} = {value}")
                        except ValueError:
                            print(f"  無效的值，使用預設值 {style_default}")
                            advanced_params[param] = style_default
                    else:
                        # 使用風格預設值
                        advanced_params[param] = style_default
                        print(f"  使用預設值 {param} = {style_default}")
            
            # 詢問是否使用張力曲線
            use_tension = input("是否使用張力曲線? (y/n，預設: n): ").strip().lower() == 'y'
            tension_curve = None
            
            if use_tension:
                print("可用張力曲線預設:")
                for i, curve_name in enumerate(TENSION_CURVES.keys()):
                    print(f"{i+1}. {curve_name}")
                
                curve_choice = input("請選擇張力曲線預設 (輸入數字或名稱，留空使用標準起伏): ").strip()
                
                if curve_choice:
                    try:
                        # 嘗試按索引選擇
                        idx = int(curve_choice) - 1
                        if 0 <= idx < len(TENSION_CURVES):
                            tension_curve = list(TENSION_CURVES.keys())[idx]
                    except ValueError:
                        # 嘗試按名稱選擇
                        if curve_choice in TENSION_CURVES:
                            tension_curve = curve_choice
                
                if not tension_curve:
                    tension_curve = "標準起伏"
                
                print(f"使用張力曲線: {tension_curve}")
            
            print(f"正在創建 {style_choice} 風格的MIDI文件...")
            filename = create_midi_with_style(
                style_choice, 
                custom_temperature=custom_temperature,
                timbre_description=timbre_description,
                advanced_params=advanced_params if use_advanced else None,
                tension_curve=tension_curve,
                user_style_manager=user_style_manager
            )
            
            print(f"完成! 文件保存為 {filename}")
            provide_playback_tips(filename)
            
            # 詢問是否保存為用戶風格
            save_as_style = input("是否將此次設置保存為用戶風格? (y/n，預設: n): ").strip().lower() == 'y'
            if save_as_style:
                style_name = input("請為此風格命名: ").strip()
                if style_name:
                    # 整合所有使用的參數
                    style_params = STYLE_PRESETS[style_choice].copy()
                    # 記錄基礎風格供後續使用
                    style_params["style_base"] = style_choice
                    if use_advanced:
                        style_params.update(advanced_params)
                    if custom_temperature is not None:
                        style_params["temperature"] = custom_temperature
                    user_style_manager.add_style(style_name, style_params)
                    print(f"已保存風格 '{style_name}'")
            
        elif choice == "2":
            tempo_input = input("請輸入曲速 (BPM, 預設: 120): ").strip()
            tempo = 120
            
            if tempo_input:
                try:
                    tempo = int(tempo_input)
                    if tempo < 40:
                        tempo = 40
                    elif tempo > 240:
                        tempo = 240
                except ValueError:
                    print("無效的曲速值，使用預設值 120")
            
            timbre_name = input("請輸入想要使用的音色名稱 (留空使用默認): ").strip()
            
            filename = create_simple_midi(tempo=tempo, timbre_name=timbre_name if timbre_name else None)
            print(f"完成! 文件保存為 {filename}")
            provide_playback_tips(filename)
            
        elif choice == "3":
            list_available_timbres()
            
        elif choice == "4":
            print("高級參數調節")
            print("=============")
            
            for param, info in ADVANCED_PARAMETERS.items():
                print(f"{param}: {info['description']}")
                print(f"  範圍: {info['min']} - {info['max']}, 預設: {info['default']}, 步進: {info['step']}")
                print("")
            
            # 顯示不同風格的預設參數值以供參考
            print("風格參數參考:")
            for style_name, preset in STYLE_PRESETS.items():
                print(f"\n{style_name}風格預設參數:")
                for param in ADVANCED_PARAMETERS.keys():
                    if param in preset:
                        print(f"  {param}: {preset[param]}")
            
            input("\n按Enter返回主菜單...")
            
        elif choice == "5":
            print("音樂張力曲線編輯")
            print("===============")
            
            print("可用張力曲線預設:")
            for i, curve_name in enumerate(TENSION_CURVES.keys()):
                print(f"{i+1}. {curve_name}: {TENSION_CURVES[curve_name]}")
            
            subchoice = input("\n請選擇操作 (1: 編輯現有曲線, 2: 創建新曲線, 其他: 返回): ").strip()
            
            if subchoice == "1":
                curve_name = input("請輸入要編輯的曲線名稱: ").strip()
                if curve_name in TENSION_CURVES:
                    editor = TensionCurveEditor(preset_name=curve_name)
                    print(f"當前曲線值: {editor.get_curve()}")
                    
                    edit_points = input("請輸入要修改的點索引和值，格式為 '索引:值 索引:值...' (例如: '0:0.2 4:0.8'): ").strip()
                    point_edits = edit_points.split()
                    
                    for edit in point_edits:
                        try:
                            idx, val = edit.split(':')
                            idx = int(idx)
                            val = float(val)
                            if 0 <= idx < editor.num_points and 0 <= val <= 1:
                                editor.set_point(idx, val)
                                print(f"已設置點 {idx} 的值為 {val}")
                            else:
                                print(f"無效的索引或值: {edit}")
                        except (ValueError, IndexError):
                            print(f"格式錯誤: {edit}")
                    
                    print(f"修改後的曲線: {editor.get_curve()}")
                    save_changes = input("是否保存更改? (y/n): ").strip().lower() == 'y'
                    
                    if save_changes:
                        editor.save_as_preset(curve_name)
                        print(f"已更新張力曲線 '{curve_name}'")
                else:
                    print(f"找不到曲線 '{curve_name}'")
            
            elif subchoice == "2":
                new_curve_name = input("請為新曲線命名: ").strip()
                if new_curve_name and new_curve_name not in TENSION_CURVES:
                    curve_values = input("請輸入16個張力值(0-1之間，空格分隔): ").strip()
                    try:
                        values = [float(v) for v in curve_values.split()]
                        if len(values) != 16:
                            print("必須提供16個值，已自動調整")
                            # 調整到16個值
                            if len(values) < 16:
                                values.extend([0.5] * (16 - len(values)))
                            else:
                                values = values[:16]
                        
                        # 確保所有值在0-1範圍內
                        values = [max(0, min(1, v)) for v in values]
                        
                        editor = TensionCurveEditor()
                        editor.curve = values
                        editor.save_as_preset(new_curve_name)
                        print(f"已創建新張力曲線 '{new_curve_name}': {values}")
                    except ValueError:
                        print("輸入格式錯誤，請輸入有效的數字值")
                else:
                    print("無效的曲線名稱或名稱已存在")
            
        elif choice == "6":
            print("用戶風格管理")
            print("=============")
            
            subchoice = input("請選擇操作 (1: 查看所有風格, 2: 使用已保存風格, 3: 刪除風格, 4: 風格演變, 5: 分析偏好, 其他: 返回): ").strip()
            
            if subchoice == "1":
                styles = user_style_manager.list_styles()
                if styles:
                    print("用戶保存的風格:")
                    for i, style_name in enumerate(styles):
                        print(f"{i+1}. {style_name}")
                else:
                    print("您還沒有保存任何風格")
            
            elif subchoice == "2":
                styles = user_style_manager.list_styles()
                if styles:
                    print("可用的用戶風格:")
                    for i, style_name in enumerate(styles):
                        print(f"{i+1}. {style_name}")
                    
                    style_choice = input("請選擇風格 (輸入名稱): ").strip()
                    if style_choice in styles:
                        user_params = user_style_manager.get_style(style_choice)
                        
                        # 基礎風格預設
                        base_style = "古典"  # 默認
                        if "style_base" in user_params and user_params["style_base"] in STYLE_PRESETS:
                            base_style = user_params["style_base"]
                        
                        timbre_description = input("請描述您想要的音色(例如：明亮、溫暖、強勁等，留空使用默認): ").strip()
                        
                        print(f"正在使用用戶風格 '{style_choice}' 創建MIDI文件...")
                        filename = create_midi_with_style(
                            base_style, 
                            advanced_params=user_params,
                            timbre_description=timbre_description,
                            user_style_manager=user_style_manager
                        )
                        
                        print(f"完成! 文件保存為 {filename}")
                        provide_playback_tips(filename)
                    else:
                        print(f"找不到風格 '{style_choice}'")
                else:
                    print("您還沒有保存任何風格")
            
            elif subchoice == "3":
                styles = user_style_manager.list_styles()
                if styles:
                    print("可刪除的用戶風格:")
                    for i, style_name in enumerate(styles):
                        print(f"{i+1}. {style_name}")
                    
                    style_to_delete = input("請輸入要刪除的風格名稱: ").strip()
                    if style_to_delete in styles:
                        confirmation = input(f"確定要刪除風格 '{style_to_delete}'? (y/n): ").strip().lower() == 'y'
                        if confirmation:
                            user_style_manager.style_db["styles"].pop(style_to_delete)
                            user_style_manager.save_style_db()
                            print(f"已刪除風格 '{style_to_delete}'")
                    else:
                        print(f"找不到風格 '{style_to_delete}'")
                else:
                    print("您還沒有保存任何風格")
            
            elif subchoice == "4":
                styles = user_style_manager.list_styles()
                if styles:
                    print("可用於演變的用戶風格:")
                    for i, style_name in enumerate(styles):
                        print(f"{i+1}. {style_name}")
                    
                    base_style_name = input("請選擇基礎風格: ").strip()
                    if base_style_name in styles:
                        evolution_degree = input("請輸入演變程度 (0.1-0.5，預設: 0.3): ").strip()
                        try:
                            degree = float(evolution_degree) if evolution_degree else 0.3
                            degree = max(0.1, min(0.5, degree))
                        except ValueError:
                            degree = 0.3
                            print("無效的演變程度，使用預設值 0.3")
                        
                        evolved_params = user_style_manager.get_style_evolution(base_style_name, degree)
                        if evolved_params:
                            # 基礎風格預設
                            base_style = "古典"  # 默認
                            if "style_base" in evolved_params and evolved_params["style_base"] in STYLE_PRESETS:
                                base_style = evolved_params["style_base"]
                            
                            timbre_description = input("請描述您想要的音色(例如：明亮、溫暖、強勁等，留空使用默認): ").strip()
                            
                            print(f"正在使用風格 '{base_style_name}' 的演變版本創建MIDI文件...")
                            filename = create_midi_with_style(
                                base_style, 
                                advanced_params=evolved_params,
                                timbre_description=timbre_description,
                                user_style_manager=user_style_manager
                            )
                            
                            # 詢問是否保存演變風格
                            save_evolved = input("是否保存這個演變風格? (y/n): ").strip().lower() == 'y'
                            if save_evolved:
                                evolved_name = input(f"請為演變風格命名 (預設: {base_style_name}_evolved): ").strip()
                                if not evolved_name:
                                    evolved_name = f"{base_style_name}_evolved"
                                
                                user_style_manager.add_style(evolved_name, evolved_params)
                                print(f"已保存演變風格 '{evolved_name}'")
                            
                            print(f"完成! 文件保存為 {filename}")
                            provide_playback_tips(filename)
                    else:
                        print(f"找不到風格 '{base_style_name}'")
                else:
                    print("您還沒有保存任何風格，無法進行風格演變")
            
            elif subchoice == "5":
                preferences = user_style_manager.analyze_preferences()
                if preferences:
                    print("根據您的使用歷史分析出的偏好參數:")
                    for param, value in preferences.items():
                        if param in ADVANCED_PARAMETERS:
                            print(f"{param}: {value:.2f}")
                    
                    use_preferences = input("是否使用這些偏好參數創建音樂? (y/n): ").strip().lower() == 'y'
                    if use_preferences:
                        base_style = input("請選擇基礎風格 (預設: 古典): ").strip()
                        if not base_style or base_style not in STYLE_PRESETS:
                            base_style = "古典"
                        
                        timbre_description = input("請描述您想要的音色(例如：明亮、溫暖、強勁等，留空使用默認): ").strip()
                        
                        print(f"正在使用您的偏好參數創建MIDI文件...")
                        filename = create_midi_with_style(
                            base_style, 
                            advanced_params=preferences,
                            timbre_description=timbre_description,
                            user_style_manager=user_style_manager
                        )
                        
                        print(f"完成! 文件保存為 {filename}")
                        provide_playback_tips(filename)
                else:
                    print("歷史記錄不足，無法分析偏好")
            
        elif choice == "7":
            print("感謝使用音樂風格創作工具!")
            break
        
        else:
            print("無效選項，請重新選擇")

if __name__ == "__main__":
    main() 