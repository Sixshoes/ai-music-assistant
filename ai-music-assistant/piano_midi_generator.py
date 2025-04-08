#!/usr/bin/env python
"""
鋼琴 MIDI 文件生成器

這個腳本專門用於生成帶有鋼琴音色的 MIDI 文件，設置具體的控制參數。
"""

import os
from midiutil import MIDIFile

def generate_piano_melody(filename="piano_melody.mid"):
    """生成一個簡單的鋼琴旋律 MIDI 文件
    
    Args:
        filename: 輸出文件名
    """
    # 創建一個雙軌道的 MIDI 文件
    # 第一軌用於控制信息，第二軌用於音符
    my_midi = MIDIFile(2)
    
    # 初始化參數
    control_track = 0    # 控制軌道
    melody_track = 1     # 旋律軌道
    channel = 0          # 使用第一個通道
    tempo = 120          # 設置速度為 120 BPM
    
    # 設置軌道名稱和速度
    my_midi.addTrackName(control_track, 0, "Control Track")
    my_midi.addTrackName(melody_track, 0, "Piano Melody")
    my_midi.addTempo(control_track, 0, tempo)
    
    # 設置為鋼琴音色 (GM音色表中的0號是大鋼琴)
    my_midi.addProgramChange(melody_track, channel, 0, 0)
    
    # 添加一些控制參數
    # 控制變化 (CC) 91 是混響效果
    my_midi.addControllerEvent(control_track, channel, 0, 91, 50)
    # 控制變化 (CC) 93 是和聲效果
    my_midi.addControllerEvent(control_track, channel, 0, 93, 30)
    # 控制變化 (CC) 7 是主音量
    my_midi.addControllerEvent(control_track, channel, 0, 7, 100)
    
    # 定義簡單鋼琴旋律 - 莫札特小星星變奏曲開頭
    melody = [
        # (音高, 開始時間, 持續時間, 音量)
        (60, 0, 1, 100),   # C4
        (60, 1, 1, 100),   # C4
        (67, 2, 1, 100),   # G4
        (67, 3, 1, 100),   # G4
        (69, 4, 1, 100),   # A4
        (69, 5, 1, 100),   # A4
        (67, 6, 2, 100),   # G4 (持續兩拍)
        
        (65, 8, 1, 100),   # F4
        (65, 9, 1, 100),   # F4
        (64, 10, 1, 100),  # E4
        (64, 11, 1, 100),  # E4
        (62, 12, 1, 100),  # D4
        (62, 13, 1, 100),  # D4
        (60, 14, 2, 100),  # C4 (持續兩拍)
    ]
    
    # 添加旋律音符
    for pitch, time, duration, volume in melody:
        my_midi.addNote(melody_track, channel, pitch, time, duration, volume)
    
    # 保存 MIDI 文件
    with open(filename, "wb") as output_file:
        my_midi.writeFile(output_file)
    
    return os.path.abspath(filename)

def generate_piano_chord_arpeggios(filename="piano_arpeggios.mid"):
    """生成鋼琴和弦琶音 MIDI 文件
    
    Args:
        filename: 輸出文件名
    """
    # 創建一個雙軌道的 MIDI 文件
    my_midi = MIDIFile(2)
    
    # 初始化參數
    control_track = 0    # 控制軌道
    music_track = 1      # 音樂軌道
    channel = 0          # 使用第一個通道
    tempo = 90           # 設置速度為 90 BPM
    
    # 設置軌道名稱和速度
    my_midi.addTrackName(control_track, 0, "Control Track")
    my_midi.addTrackName(music_track, 0, "Piano Arpeggios")
    my_midi.addTempo(control_track, 0, tempo)
    
    # 設置為鋼琴音色 (GM音色表中的0號是大鋼琴)
    my_midi.addProgramChange(music_track, channel, 0, 0)
    
    # 添加控制參數
    my_midi.addControllerEvent(control_track, channel, 0, 91, 60)  # 混響
    my_midi.addControllerEvent(control_track, channel, 0, 10, 64)  # 聲像 (中)
    
    # 定義幾個和弦及其琶音
    chord_arpeggios = [
        # C 大三和弦 (C, E, G)
        [(60, 0, 2, 90), (64, 0.5, 2, 90), (67, 1, 2, 90), (72, 1.5, 2, 90)],
        
        # G 大三和弦 (G, B, D)
        [(55, 4, 2, 90), (59, 4.5, 2, 90), (62, 5, 2, 90), (67, 5.5, 2, 90)],
        
        # A 小三和弦 (A, C, E)
        [(57, 8, 2, 90), (60, 8.5, 2, 90), (64, 9, 2, 90), (69, 9.5, 2, 90)],
        
        # F 大三和弦 (F, A, C)
        [(53, 12, 2, 90), (57, 12.5, 2, 90), (60, 13, 2, 90), (65, 13.5, 2, 90)],
    ]
    
    # 添加琶音音符
    for chord in chord_arpeggios:
        for pitch, time, duration, volume in chord:
            my_midi.addNote(music_track, channel, pitch, time, duration, volume)
    
    # 保存 MIDI 文件
    with open(filename, "wb") as output_file:
        my_midi.writeFile(output_file)
    
    return os.path.abspath(filename)

if __name__ == "__main__":
    print("正在生成鋼琴旋律 (小星星變奏曲)...")
    melody_path = generate_piano_melody()
    print(f"已保存到：{melody_path}")
    
    print("\n正在生成鋼琴和弦琶音...")
    arpeggio_path = generate_piano_chord_arpeggios()
    print(f"已保存到：{arpeggio_path}")
    
    print("\n全部文件已生成。")
    
    # 提示用戶如何打開文件
    print("\n請使用以下方式打開這些 MIDI 文件：")
    print("- macOS: 使用 GarageBand 或 Logic Pro 打開以獲得更好的音色")
    print("- Windows: 使用 Windows Media Player 或 FL Studio 打開")
    print("- Linux: 使用 TiMidity++ 或 FluidSynth 打開") 