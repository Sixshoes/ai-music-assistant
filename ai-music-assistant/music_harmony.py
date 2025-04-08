#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
音樂和聲模塊
處理和聲關係、音軌之間的協調和樂理規則
確保生成的音樂具有和聲統一感
"""

import random
import math

# 音程定義（半音數）
INTERVALS = {
    "unison": 0,
    "minor_second": 1, 
    "major_second": 2,
    "minor_third": 3,
    "major_third": 4,
    "perfect_fourth": 5,
    "tritone": 6,
    "perfect_fifth": 7,
    "minor_sixth": 8,
    "major_sixth": 9,
    "minor_seventh": 10,
    "major_seventh": 11,
    "octave": 12
}

# 和弦類型定義
CHORD_TYPES = {
    "major": [0, 4, 7],              # 大三和弦 (根音、大三度、純五度)
    "minor": [0, 3, 7],              # 小三和弦 (根音、小三度、純五度)
    "diminished": [0, 3, 6],         # 減三和弦 (根音、小三度、減五度)
    "augmented": [0, 4, 8],          # 增三和弦 (根音、大三度、增五度)
    "dominant7": [0, 4, 7, 10],      # 屬七和弦 (大三和弦+小七度)
    "major7": [0, 4, 7, 11],         # 大七和弦 (大三和弦+大七度)
    "minor7": [0, 3, 7, 10],         # 小七和弦 (小三和弦+小七度)
    "half_diminished7": [0, 3, 6, 10], # 半減七和弦 (減三和弦+小七度)
    "diminished7": [0, 3, 6, 9],     # 減七和弦 (減三和弦+減七度)
    "sus4": [0, 5, 7],               # 掛四和弦 (根音、純四度、純五度)
    "sus2": [0, 2, 7]                # 掛二和弦 (根音、大二度、純五度)
}

# 協和度定義 - 數值越低表示越協和
CONSONANCE_RATINGS = {
    0: 0,    # 同度/八度 - 最協和
    7: 1,    # 純五度 - 非常協和
    4: 2,    # 大三度 - 協和
    5: 2,    # 純四度 - 協和
    3: 3,    # 小三度 - 協和
    9: 3,    # 大六度 - 協和
    8: 4,    # 小六度 - 相對協和
    2: 5,    # 大二度 - 較不協和
    10: 5,   # 小七度 - 較不協和
    11: 6,   # 大七度 - 不協和
    1: 6,    # 小二度 - 不協和
    6: 7     # 增四度/減五度 - 最不協和
}

# 音符與和弦關係分類
NOTE_CHORD_CLASSIFICATION = {
    "chord_tone": [0, 4, 7],              # 和弦音
    "added_tone": [2, 9, 11, 14],         # 添加音
    "passing_tone": [1, 3, 5, 6, 8, 10],  # 經過音
    "tension_tone": [1, 6, 10, 11]        # 張力音
}

class HarmonyAnalyzer:
    """和聲分析器，用於音樂的和聲分析與生成"""

    def __init__(self, scale_type="大調"):
        """初始化和聲分析器"""
        # 設置音階類型
        self.scale_type = scale_type
        
        # 定義基本的音階音
        self.c_major_scale = [60, 62, 64, 65, 67, 69, 71]  # C大調音階
        self.a_minor_scale = [57, 59, 60, 62, 64, 65, 67]  # A小調音階
        
        # 定義基本和弦
        self.triads = {
            'major': [0, 4, 7],     # 大三和弦
            'minor': [0, 3, 7],     # 小三和弦
            'dim': [0, 3, 6],       # 減三和弦
            'aug': [0, 4, 8],       # 增三和弦
            'sus4': [0, 5, 7],      # 掛四和弦
            'sus2': [0, 2, 7]       # 掛二和弦
        }
        
        # 添加七和弦
        self.seventh_chords = {
            'maj7': [0, 4, 7, 11],   # 大七和弦
            'min7': [0, 3, 7, 10],   # 小七和弦
            '7': [0, 4, 7, 10],      # 屬七和弦
            'dim7': [0, 3, 6, 9],    # 減七和弦
            'hdim7': [0, 3, 6, 10],  # 半減七和弦
            'minmaj7': [0, 3, 7, 11] # 小大七和弦
        }
        
        # 添加九和弦
        self.ninth_chords = {
            'maj9': [0, 4, 7, 11, 14],  # 大九和弦
            'min9': [0, 3, 7, 10, 14],  # 小九和弦
            '9': [0, 4, 7, 10, 14],     # 屬九和弦
            'maj7b9': [0, 4, 7, 11, 13], # 大七降九和弦
            '7b9': [0, 4, 7, 10, 13],   # 屬七降九和弦
            '7#9': [0, 4, 7, 10, 15]    # 屬七升九和弦
        }
        
        # 添加十一和弦和十三和弦（常用於爵士樂）
        self.extended_chords = {
            '11': [0, 4, 7, 10, 14, 17],      # 11和弦
            'maj11': [0, 4, 7, 11, 14, 17],   # 大11和弦
            'min11': [0, 3, 7, 10, 14, 17],   # 小11和弦
            '13': [0, 4, 7, 10, 14, 17, 21],  # 13和弦
            'maj13': [0, 4, 7, 11, 14, 17, 21], # 大13和弦
            'min13': [0, 3, 7, 10, 14, 17, 21]  # 小13和弦
        }
        
        # 定義特殊的爵士和弦進行
        self.jazz_progressions = {
            'ii-V-I': [[2, 'min7'], [5, '7'], [1, 'maj7']],
            'ii-V-I-VI': [[2, 'min7'], [5, '7'], [1, 'maj7'], [6, 'min7']],
            'I-VI-ii-V': [[1, 'maj7'], [6, 'min7'], [2, 'min7'], [5, '7']]
        }
    
    def calculate_consonance(self, note1, note2):
        """計算兩個音符之間的協和度（數值越低表示越協和）"""
        # 標準化到一個八度內
        interval = abs(note1 - note2) % 12
        return CONSONANCE_RATINGS.get(interval, 7)  # 默認為最不協和
    
    def check_note_chord_relationship(self, note, chord):
        """檢查音符與和弦的關係，返回關係類型和協和度評分"""
        # 標準化音符和和弦到一個八度內
        note_class = note % 12
        chord_classes = [c % 12 for c in chord]
        root = chord_classes[0]
        
        # 計算相對於根音的間隔
        relative_interval = (note_class - root) % 12
        
        # 確定關係類型
        relationship = "non_chord"
        for rel_type, intervals in NOTE_CHORD_CLASSIFICATION.items():
            if relative_interval in intervals:
                relationship = rel_type
                break
        
        # 計算與和弦各音符的協和度
        consonance_scores = [self.calculate_consonance(note_class, c) for c in chord_classes]
        avg_consonance = sum(consonance_scores) / len(consonance_scores)
        
        return relationship, avg_consonance
    
    def find_compatible_note(self, note, chord, stability_preference=0.7):
        """找到與當前和弦兼容的音符（可能是原音符或調整後的音符）"""
        
        relationship, consonance = self.check_note_chord_relationship(note, chord)
        
        # 如果已經是和弦音或協和度高，則不需要調整
        if relationship == "chord_tone" or consonance <= 2:
            return note
        
        # 如果是經過音且隨機值超過穩定性偏好，則保留原音符
        if relationship == "passing_tone" and random.random() > stability_preference:
            return note
        
        # 需要調整 - 找到最近的和弦音
        note_class = note % 12
        root = chord[0] % 12
        octave = note // 12
        
        # 計算和弦音
        chord_tones = [(root + interval) % 12 for interval in CHORD_TYPES["major"]]
        
        # 找到最近的和弦音
        min_distance = 12
        nearest_tone = note_class
        
        for tone in chord_tones:
            # 計算音符間距離（向上或向下）
            up_distance = (tone - note_class) % 12
            down_distance = (note_class - tone) % 12
            distance = min(up_distance, down_distance)
            
            if distance < min_distance:
                min_distance = distance
                nearest_tone = tone
        
        # 調整到正確的八度
        adjusted_note = nearest_tone + (octave * 12)
        
        # 確保在合理的MIDI音符範圍內
        while adjusted_note < 36:  # C2
            adjusted_note += 12
        while adjusted_note > 96:  # C7
            adjusted_note -= 12
        
        return adjusted_note
    
    def validate_melody_with_chords(self, melody, durations, chord_progression):
        """檢查旋律與和弦進行的和諧性，必要時調整旋律"""
        if not melody or not chord_progression:
            return melody, durations
        
        validated_melody = melody.copy()
        melody_time = 0
        chord_duration = 4.0  # 假設每個和弦持續4拍
        
        for i, (note, duration) in enumerate(zip(melody, durations)):
            # 確定當前時間對應的和弦
            chord_idx = min(int(melody_time / chord_duration), len(chord_progression) - 1)
            current_chord = chord_progression[chord_idx]
            
            # 檢查音符與和弦的關係
            relationship, consonance = self.check_note_chord_relationship(note, current_chord)
            
            # 重要拍點上的音符需要更高的和諧度
            is_strong_beat = melody_time % 1.0 < 0.1  # 接近整數拍的視為強拍
            
            # 根據關係和協和度決定是否需要調整
            if is_strong_beat and relationship != "chord_tone" and consonance > 3:
                # 在強拍上找到更和諧的音符
                validated_melody[i] = self.find_compatible_note(note, current_chord, 0.9)
            elif not is_strong_beat and consonance > 5:
                # 在弱拍上只調整極不協和的音符
                validated_melody[i] = self.find_compatible_note(note, current_chord, 0.6)
            
            melody_time += duration
        
        return validated_melody, durations
    
    def enhance_vertical_harmony(self, tracks):
        """增強多音軌之間的垂直和聲關係"""
        if not tracks or len(tracks) < 2:
            return tracks
        
        enhanced_tracks = [track.copy() for track in tracks]
        
        # 處理每個時間點的所有音軌
        for time_point in range(min(len(track) for track in tracks)):
            # 收集此時間點所有音軌的音符
            current_notes = [track[time_point] for track in tracks]
            
            # 檢查所有音符的和諧度
            dissonance_detected = False
            for i in range(len(current_notes)):
                for j in range(i+1, len(current_notes)):
                    consonance = self.calculate_consonance(current_notes[i], current_notes[j])
                    if consonance > 5:  # 高不協和度
                        dissonance_detected = True
                        break
                if dissonance_detected:
                    break
            
            # 如果檢測到不協和，進行調整
            if dissonance_detected:
                # 從低音到高音排序音符
                sorted_indices = sorted(range(len(current_notes)), key=lambda i: current_notes[i])
                
                # 保持低音不變，調整其他音使其與低音協和
                bass_note = current_notes[sorted_indices[0]]
                for idx in sorted_indices[1:]:
                    if self.calculate_consonance(current_notes[idx], bass_note) > 5:
                        # 調整為更協和的音符
                        adjusted_note = self.find_compatible_note(current_notes[idx], [bass_note, bass_note+7], 0.8)
                        enhanced_tracks[idx][time_point] = adjusted_note
        
        return enhanced_tracks
    
    def apply_voice_leading(self, chord_sequence):
        """應用聲部進行原則生成更流暢的和弦連接"""
        if not chord_sequence or len(chord_sequence) < 2:
            return chord_sequence
        
        smooth_sequence = [chord_sequence[0]]  # 第一個和弦保持不變
        
        for i in range(1, len(chord_sequence)):
            prev_chord = chord_sequence[i-1]
            current_chord = chord_sequence[i]
            
            # 如果和弦相同，則直接添加
            if prev_chord == current_chord:
                smooth_sequence.append(current_chord)
                continue
            
            # 嘗試找到最小運動的聲部進行
            smoothed_chord = self._find_smooth_voice_leading(prev_chord, current_chord)
            smooth_sequence.append(smoothed_chord)
        
        return smooth_sequence
    
    def _find_smooth_voice_leading(self, prev_chord, current_chord):
        """找到兩個和弦間最流暢的聲部進行方式"""
        # 保持和弦類型不變，只調整音符的八度位置
        root = current_chord[0]
        chord_type = [note - root for note in current_chord]
        
        # 嘗試不同的八度組合
        best_movement = float('inf')
        best_chord = current_chord
        
        # 對每個音符嘗試不同的八度
        for octave_shift in [-12, 0, 12]:
            candidate_chord = [root + octave_shift]
            # 添加和弦其他音符
            for interval in chord_type[1:]:
                candidate_chord.append(root + interval + octave_shift)
            
            # 計算總的聲部移動距離
            total_movement = 0
            for prev_note in prev_chord:
                # 找到最近的新和弦音符
                min_move = min(abs(new_note - prev_note) for new_note in candidate_chord)
                total_movement += min_move
            
            # 更新最佳選擇
            if total_movement < best_movement:
                best_movement = total_movement
                best_chord = candidate_chord
        
        return best_chord

class BassLineGenerator:
    """低音聲部生成器，基於和弦進行創建和諧的低音線"""
    
    def __init__(self, style="classical"):
        """初始化低音生成器"""
        self.style = style
    
    def create_bass_line(self, chord_progression, style="classical", rhythmic_pattern=None):
        """基於和弦進行創建低音線"""
        if not chord_progression:
            return [], []
        
        bass_notes = []
        bass_durations = []
        
        # 設置默認節奏模式
        if not rhythmic_pattern:
            if style == "classical":
                rhythmic_pattern = [4.0]  # 整小節低音
            elif style == "jazz":
                rhythmic_pattern = [1.0, 1.0, 1.0, 1.0]  # 行進低音
            elif style == "pop":
                rhythmic_pattern = [1.0, 1.0, 1.0, 1.0]  # 節拍低音
            else:  # electronic
                rhythmic_pattern = [2.0, 2.0]  # 強調低音
        
        for chord in chord_progression:
            root = chord[0]
            bass_note = root - 12  # 降低一個八度
            
            # 根據風格生成不同的低音型態
            if style == "classical":
                # 主要使用根音
                for duration in rhythmic_pattern:
                    bass_notes.append(bass_note)
                    bass_durations.append(duration)
            
            elif style == "jazz":
                # 行進低音，使用根音、五度和經過音
                notes_in_pattern = []
                for i, duration in enumerate(rhythmic_pattern):
                    if i == 0:  # 第一拍用根音
                        notes_in_pattern.append(bass_note)
                    elif i == 2:  # 第三拍用五度
                        notes_in_pattern.append(bass_note + 7)
                    else:  # 其他拍使用經過音
                        possible_notes = [bass_note + 2, bass_note + 4, bass_note + 9]
                        notes_in_pattern.append(random.choice(possible_notes))
                
                bass_notes.extend(notes_in_pattern)
                bass_durations.extend(rhythmic_pattern)
            
            elif style == "pop":
                # 流行風格節奏低音，強調根音和八度
                for i, duration in enumerate(rhythmic_pattern):
                    if i % 4 == 0:  # 每小節第一拍
                        bass_notes.append(bass_note)
                    elif i % 4 == 2:  # 每小節第三拍
                        bass_notes.append(bass_note)
                    elif i % 2 == 0:  # 其他偶數拍
                        bass_notes.append(bass_note + 7)  # 五度
                    else:  # 其他拍
                        bass_notes.append(bass_note)
                    
                    bass_durations.append(duration)
            
            else:  # electronic
                # 電子風格，簡單但強調的低音
                for i, duration in enumerate(rhythmic_pattern):
                    if i == 0:
                        # 第一拍加重
                        bass_notes.append(bass_note)
                    else:
                        # 其他拍可能使用八度或原音
                        if random.random() > 0.7:
                            bass_notes.append(bass_note + 12)  # 高八度
                        else:
                            bass_notes.append(bass_note)
                    
                    bass_durations.append(duration)
        
        return bass_notes, bass_durations

class ChordVoicingGenerator:
    """和弦聲部編配生成器，創建適合不同風格的和弦聲部安排"""
    
    def __init__(self, style="classical"):
        """初始化和弦聲部生成器"""
        self.style = style
    
    def create_chord_voicings(self, chord_progression, style="classical"):
        """為和弦進行創建適合特定風格的聲部編配"""
        if not chord_progression:
            return [], []
        
        chord_notes = []
        chord_durations = []
        
        for chord in chord_progression:
            root = chord[0]
            
            # 獲取和弦轉位和聲部排列
            voicing = self._get_style_voicing(chord, style)
            rhythm_pattern = self._get_style_rhythm(style)
            
            # 根據節奏模式添加和弦
            for duration in rhythm_pattern:
                if style == "classical":
                    # 古典風格可能使用分解和弦
                    if random.random() > 0.5:
                        # 塊狀和弦
                        chord_notes.append(voicing)
                        chord_durations.append(duration)
                    else:
                        # 分解和弦
                        for note in voicing:
                            chord_notes.append([note])
                            chord_durations.append(duration / len(voicing))
                else:
                    # 其他風格主要使用塊狀和弦
                    chord_notes.append(voicing)
                    chord_durations.append(duration)
        
        return chord_notes, chord_durations
    
    def _get_style_voicing(self, chord, style):
        """根據風格獲取和弦聲部編配"""
        root = chord[0]
        
        if style == "classical":
            # 古典風格：緊密排列和弦，避免低音區的不協和
            voicing = chord.copy()
            # 調整八度使和弦在中音區並聲部緊密
            while voicing[0] < 48:  # C3
                voicing[0] += 12
            # 確保和弦間距合適
            for i in range(1, len(voicing)):
                while voicing[i] < voicing[i-1]:
                    voicing[i] += 12
                while voicing[i] > voicing[i-1] + 12:
                    voicing[i] -= 12
        
        elif style == "jazz":
            # 爵士風格：使用擴展和弦、四和弦結構和開放聲部
            voicing = chord.copy()
            
            # 添加色彩音
            if len(voicing) <= 4 and random.random() > 0.5:
                if random.random() > 0.5:
                    voicing.append(root + 9)  # 添加六度
                else:
                    voicing.append(root + 14)  # 添加九度
            
            # 調整八度和聲部排列
            voicing.sort()  # 先排序
            # 調到中低音區
            while voicing[0] < 48:  # C3
                for i in range(len(voicing)):
                    voicing[i] += 12
            
            # 爵士風格常省略五度
            if len(voicing) > 3 and random.random() > 0.6:
                fifth_idx = None
                for i, note in enumerate(voicing):
                    if (note - root) % 12 == 7:  # 找到五度音
                        fifth_idx = i
                        break
                if fifth_idx is not None:
                    voicing.pop(fifth_idx)
        
        elif style == "pop":
            # 流行風格：簡單開放和弦，強調低音和高音
            voicing = chord.copy()
            # 確保根音在低音區
            while voicing[0] > 48:
                voicing[0] -= 12
            # 其他聲部可能在高一些的音區
            for i in range(1, len(voicing)):
                while voicing[i] < 60:  # C4以上
                    voicing[i] += 12
        
        else:  # electronic
            # 電子風格：可以使用更寬的聲部間距
            voicing = chord.copy()
            # 根音放在低音區
            while voicing[0] > 36:  # C2以下
                voicing[0] -= 12
            # 其他聲部可能分散在更寬的音域
            for i in range(1, len(voicing)):
                # 隨機決定八度
                octave_shift = random.choice([0, 1, 2]) * 12
                voicing[i] = (voicing[i] % 12) + 60 + octave_shift  # 從C4開始
        
        return voicing
    
    def _get_style_rhythm(self, style):
        """根據風格獲取和弦節奏模式"""
        if style == "classical":
            # 古典風格：較長的和弦持續時間
            return [4.0]  # 一個和弦持續一小節
        
        elif style == "jazz":
            # 爵士風格：復雜節奏，經常使用切分
            patterns = [
                [1.0, 1.0, 1.0, 1.0],  # 標準四拍
                [1.5, 0.5, 1.5, 0.5],  # 切分節奏
                [0.5, 1.0, 0.5, 2.0]   # 不規則節奏
            ]
            return random.choice(patterns)
        
        elif style == "pop":
            # 流行風格：重複節奏模式
            patterns = [
                [1.0, 1.0, 1.0, 1.0],  # 標準四拍
                [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]  # 八分音符節奏
            ]
            return random.choice(patterns)
        
        else:  # electronic
            # 電子風格：強調特定拍點
            patterns = [
                [1.0, 1.0, 1.0, 1.0],  # 標準四拍
                [2.0, 2.0],            # 強調第一和第三拍
                [0.5] * 8              # 快速重複節奏
            ]
            return random.choice(patterns)

# 使用範例
if __name__ == "__main__":
    # 創建和聲分析器
    harmony_analyzer = HarmonyAnalyzer()
    
    # 測試和弦間關係檢查
    c_major = [60, 64, 67]  # C大三和弦
    test_note = 62  # D
    relationship, consonance = harmony_analyzer.check_note_chord_relationship(test_note, c_major)
    print(f"音符 {test_note} 與和弦 {c_major} 的關係: {relationship}, 協和度: {consonance}")
    
    # 測試音符調整
    adjusted_note = harmony_analyzer.find_compatible_note(test_note, c_major)
    print(f"調整後的音符: {adjusted_note}")
    
    # 測試低音生成
    bass_generator = BassLineGenerator()
    chord_progression = [[60, 64, 67], [67, 71, 74], [65, 69, 72], [60, 64, 67]]  # C-G-F-C
    bass_notes, bass_durations = bass_generator.create_bass_line(chord_progression, "jazz")
    print(f"生成的爵士低音線: {bass_notes}")
    print(f"低音持續時間: {bass_durations}")
    
    # 測試和弦聲部生成
    chord_voicing = ChordVoicingGenerator()
    voicings, voicing_durations = chord_voicing.create_chord_voicings(chord_progression, "jazz")
    print(f"生成的爵士和弦聲部: {voicings}")
    print(f"和弦持續時間: {voicing_durations}") 