#!/usr/bin/env python
"""
直接生成各種風格和調性的MIDI文件
確保能正確展示調性和風格的差異
"""

import os
from midiutil import MIDIFile

# 調性對應的音階和基礎音高
KEY_SCALES = {
    # 大調
    'C': {'scale': [0, 2, 4, 5, 7, 9, 11], 'base': 60},  # C大調: C D E F G A B
    'G': {'scale': [0, 2, 4, 5, 7, 9, 11], 'base': 55},  # G大調: G A B C D E F#
    'D': {'scale': [0, 2, 4, 5, 7, 9, 11], 'base': 50},  # D大調: D E F# G A B C#
    'F': {'scale': [0, 2, 4, 5, 7, 9, 11], 'base': 53},  # F大調: F G A Bb C D E
    
    # 小調
    'Am': {'scale': [0, 2, 3, 5, 7, 8, 10], 'base': 57},  # A小調: A B C D E F G
    'Em': {'scale': [0, 2, 3, 5, 7, 8, 10], 'base': 52},  # E小調: E F# G A B C D
    'Dm': {'scale': [0, 2, 3, 5, 7, 8, 10], 'base': 50},  # D小調: D E F G A Bb C
}

# 各種風格的節奏和力度特性
STYLE_PATTERNS = {
    'pop': {
        'name': '流行',
        'durations': [0.25, 0.5, 1.0],  # 四分音符、八分音符、十六分音符
        'duration_weights': [0.3, 0.5, 0.2],  # 偏好八分音符
        'velocity_range': (75, 90),  # 中等音量
    },
    'rock': {
        'name': '搖滾',
        'durations': [0.25, 0.5, 0.75],  # 更多短音符
        'duration_weights': [0.4, 0.4, 0.2],
        'velocity_range': (80, 100),  # 高音量
    },
    'jazz': {
        'name': '爵士',
        'durations': [0.33, 0.5, 0.67, 1.0],  # 更多變化的節奏
        'duration_weights': [0.3, 0.3, 0.2, 0.2],
        'velocity_range': (65, 90),  # 動態變化豐富
    },
    'classical': {
        'name': '古典',
        'durations': [0.5, 1.0, 2.0],  # 更多長音符
        'duration_weights': [0.3, 0.5, 0.2],
        'velocity_range': (60, 95),  # 更豐富的動態
    }
}

def create_scale_midi(key, filename="c_scale.mid"):
    """生成一個完整的音階MIDI文件"""
    print(f"生成{key}音階: {filename}")
    
    # 取得音階和基礎音高
    key_info = KEY_SCALES.get(key, KEY_SCALES['C'])
    scale = key_info['scale']
    base_pitch = key_info['base']
    
    # 創建MIDI文件
    midi = MIDIFile(1)
    track = 0
    time = 0
    tempo = 120
    midi.addTrackName(track, time, f"{key} Scale")
    midi.addTempo(track, time, tempo)
    
    # 添加上行音階 (一個八度)
    for i, interval in enumerate(scale):
        pitch = base_pitch + interval
        midi.addNote(track, 0, pitch, time + i * 0.5, 0.5, 80)
    
    # 添加最高音
    midi.addNote(track, 0, base_pitch + 12, time + len(scale) * 0.5, 0.5, 80)
    
    # 添加下行音階
    for i, interval in reversed(list(enumerate(scale))):
        pitch = base_pitch + interval
        position = time + (len(scale) + 1 + (len(scale) - i)) * 0.5
        midi.addNote(track, 0, pitch, position, 0.5, 80)
    
    # 寫入文件
    with open(filename, 'wb') as output_file:
        midi.writeFile(output_file)
    
    print(f"成功生成 {key} 音階 MIDI: {filename}")
    return filename


def create_style_midi(key, style, filename=None):
    """生成一個特定風格和調性的旋律"""
    if filename is None:
        filename = f"{style}_{key.lower()}.mid"
    
    print(f"生成 {STYLE_PATTERNS[style]['name']} 風格 {key} 調旋律: {filename}")
    
    # 取得音階和基礎音高
    key_info = KEY_SCALES.get(key, KEY_SCALES['C'])
    scale = key_info['scale']
    base_pitch = key_info['base']
    
    # 取得風格特性
    style_info = STYLE_PATTERNS.get(style, STYLE_PATTERNS['pop'])
    durations = style_info['durations']
    duration_weights = style_info['duration_weights']
    velocity_range = style_info['velocity_range']
    
    # 創建MIDI文件
    midi = MIDIFile(1)
    track = 0
    time = 0
    tempo = 120
    midi.addTrackName(track, time, f"{style.capitalize()} {key} Melody")
    midi.addTempo(track, time, tempo)
    
    # 為風格和調性生成適當的旋律
    import random
    current_time = 0
    
    # 生成16個音符的旋律
    for _ in range(16):
        # 選擇音高 (從音階中)
        scale_step = random.randrange(len(scale))
        octave = random.choice([0, 1])  # 基本八度或高一個八度
        pitch = base_pitch + scale[scale_step] + octave * 12
        
        # 確保音高在合理範圍內
        while pitch < 36 or pitch > 96:
            scale_step = random.randrange(len(scale))
            octave = random.choice([0, 1])
            pitch = base_pitch + scale[scale_step] + octave * 12
        
        # 選擇持續時間
        duration_idx = random.choices(range(len(durations)), weights=duration_weights)[0]
        duration = durations[duration_idx]
        
        # 選擇力度
        velocity = random.randint(velocity_range[0], velocity_range[1])
        
        # 添加音符
        midi.addNote(track, 0, pitch, current_time, duration, velocity)
        
        # 更新時間
        current_time += duration
    
    # 寫入文件
    with open(filename, 'wb') as output_file:
        midi.writeFile(output_file)
    
    print(f"成功生成 {STYLE_PATTERNS[style]['name']} 風格 {key} 調旋律: {filename}")
    return filename


def create_chord_progression(key, filename="chord_progression.mid"):
    """創建一個和弦進行示例"""
    print(f"生成 {key} 調和弦進行: {filename}")
    
    # 不同調性的和弦進行
    progressions = {
        'C': [
            [60, 64, 67],  # C
            [65, 69, 72],  # F
            [67, 71, 74],  # G
            [60, 64, 67]   # C
        ],
        'G': [
            [55, 59, 62],  # G
            [60, 64, 67],  # C
            [62, 66, 69],  # D
            [55, 59, 62]   # G
        ],
        'Am': [
            [57, 60, 64],  # Am
            [55, 59, 62],  # G
            [53, 57, 60],  # F
            [52, 55, 59]   # E
        ],
        'F': [
            [53, 57, 60],  # F
            [55, 59, 62],  # G
            [60, 64, 67],  # C
            [53, 57, 60]   # F
        ],
    }
    
    # 創建MIDI文件
    midi = MIDIFile(1)
    track = 0
    time = 0
    tempo = 120
    midi.addTrackName(track, time, f"{key} Chord Progression")
    midi.addTempo(track, time, tempo)
    
    # 獲取對應調性的和弦進行
    chords = progressions.get(key, progressions['C'])
    
    # 添加和弦
    for i, chord in enumerate(chords):
        for note in chord:
            midi.addNote(track, 0, note, i, 1.0, 80)
    
    # 寫入文件
    with open(filename, 'wb') as output_file:
        midi.writeFile(output_file)
    
    print(f"成功生成 {key} 調和弦進行: {filename}")
    return filename


def create_piano_melody(key="C", style="classical", filename="piano_melody.mid"):
    """創建一個鋼琴旋律，使用音色0(鋼琴)"""
    print(f"生成 {key} 調鋼琴旋律: {filename}")
    
    # 取得音階和基礎音高
    key_info = KEY_SCALES.get(key, KEY_SCALES['C'])
    scale = key_info['scale']
    base_pitch = key_info['base']
    
    # 創建MIDI文件
    midi = MIDIFile(1)
    track = 0
    time = 0
    tempo = 100
    midi.addTrackName(track, time, f"Piano Melody in {key}")
    midi.addTempo(track, time, tempo)
    
    # 設置鋼琴音色 (0 = Acoustic Grand Piano)
    midi.addProgramChange(track, 0, 0, 0)
    
    # 創建旋律模式
    melody_pattern = []
    
    if style == "classical":
        # 巴赫風格的旋律片段
        melody_pattern = [0, 2, 4, 7, 4, 2, 0, 2, 4, 7, 9, 7, 4, 2, 0]
    else:
        # 簡單的彈跳旋律
        melody_pattern = [0, 4, 7, 4, 0, 4, 7, 9, 7, 4, 0, 2, 4, 2, 0]
    
    # 添加旋律
    for i, step in enumerate(melody_pattern):
        # 轉換音階級數為實際音高
        pitch = base_pitch + scale[step % len(scale)] + (step // len(scale)) * 12
        
        # 持續時間和力度
        duration = 0.5 if i % 2 == 0 else 0.25
        velocity = 90 if i % 4 == 0 else 75
        
        # 添加音符
        midi.addNote(track, 0, pitch, time, duration, velocity)
        time += duration
    
    # 寫入文件
    with open(filename, 'wb') as output_file:
        midi.writeFile(output_file)
    
    print(f"成功生成 {key} 調鋼琴旋律: {filename}")
    return filename


def create_piano_arpeggios(key="C", filename="piano_arpeggios.mid"):
    """創建鋼琴琶音練習"""
    print(f"生成 {key} 調鋼琴琶音: {filename}")
    
    # 取得音階和基礎音高
    key_info = KEY_SCALES.get(key, KEY_SCALES['C'])
    scale = key_info['scale']
    base_pitch = key_info['base']
    
    # 創建MIDI文件
    midi = MIDIFile(1)
    track = 0
    time = 0
    tempo = 120
    midi.addTrackName(track, time, f"Piano Arpeggios in {key}")
    midi.addTempo(track, time, tempo)
    
    # 設置鋼琴音色
    midi.addProgramChange(track, 0, 0, 0)
    
    # 創建主要三和弦琶音
    if 'Am' in key or 'Em' in key or 'Dm' in key:  # 小調
        arpeggios = [
            [0, 3, 7],  # 小三和弦
            [5, 8, 12],  # 小調屬和弦
            [7, 10, 14],  # 小調下屬和弦
            [0, 3, 7]   # 小三和弦
        ]
    else:  # 大調
        arpeggios = [
            [0, 4, 7],  # 大三和弦
            [5, 9, 12],  # 屬和弦
            [7, 11, 14],  # 下屬和弦
            [0, 4, 7]   # 大三和弦
        ]
    
    # 添加琶音
    current_time = 0
    for arpeggio in arpeggios:
        # 上行琶音
        for note in arpeggio:
            pitch = base_pitch + note
            midi.addNote(track, 0, pitch, current_time, 0.25, 80)
            current_time += 0.25
        
        # 下行琶音
        for note in reversed(arpeggio):
            pitch = base_pitch + note
            midi.addNote(track, 0, pitch, current_time, 0.25, 80)
            current_time += 0.25
    
    # 寫入文件
    with open(filename, 'wb') as output_file:
        midi.writeFile(output_file)
    
    print(f"成功生成 {key} 調鋼琴琶音: {filename}")
    return filename


def main():
    """主函數：生成各種MIDI示例"""
    # 生成C大調音階
    c_scale_midi = create_scale_midi('C', 'c_scale.mid')
    
    # 生成簡單和弦進行
    chord_midi = create_chord_progression('C', 'chord_progression.mid')
    
    # 生成一個簡單的旋律
    simple_midi = create_style_midi('C', 'pop', 'simple_melody.mid')
    
    # 生成鋼琴旋律
    piano_midi = create_piano_melody('C', 'classical', 'piano_melody.mid')
    
    # 生成鋼琴琶音
    arpeggios_midi = create_piano_arpeggios('C', 'piano_arpeggios.mid')
    
    # 生成不同風格的旋律示例
    styles = ['pop', 'rock', 'jazz', 'classical']
    keys = ['C', 'G', 'F', 'Am']
    
    for style in styles:
        for key in keys[:1]:  # 為簡化，每種風格只生成一個調性的示例
            create_style_midi(key, style)
    
    # 在macOS上嘗試播放
    if os.uname().sysname == "Darwin":
        print("嘗試播放MIDI文件...")
        os.system(f'open "{c_scale_midi}"')
    
    print("所有MIDI文件生成完成！")


if __name__ == "__main__":
    main() 