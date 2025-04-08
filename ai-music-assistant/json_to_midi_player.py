"""
將JSON音樂數據轉換為MIDI並播放

用法:
python json_to_midi_player.py <json_file_path>
"""

import json
import sys
import os
import platform
import subprocess
from midiutil import MIDIFile
import pygame
import time

def json_to_midi(json_path, output_path=None):
    """將JSON音樂數據轉換為MIDI文件
    
    Args:
        json_path: JSON文件路徑
        output_path: 輸出MIDI文件路徑，如果未指定則使用相同的文件名
        
    Returns:
        生成的MIDI文件路徑
    """
    # 如果未指定輸出路徑，使用相同的文件名但擴展名為.mid
    if output_path is None:
        output_path = os.path.splitext(json_path)[0] + '.mid'
    
    # 讀取JSON數據
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 創建MIDI文件對象
    # 1個軌道用於旋律，1個軌道用於和弦
    midi = MIDIFile(2)
    
    # 設置軌道名稱
    midi.addTrackName(0, 0, "Melody")
    midi.addTrackName(1, 0, "Chords")
    
    # 設置速度
    tempo = data.get('parameters', {}).get('tempo', 120)
    midi.addTempo(0, 0, tempo)
    midi.addTempo(1, 0, tempo)
    
    # 添加旋律音符
    for note in data.get('melody', []):
        pitch = note.get('pitch')
        start_time = note.get('start_time')
        duration = note.get('duration')
        velocity = note.get('velocity', 100)
        
        midi.addNote(0, 0, pitch, start_time, duration, velocity)
    
    # 添加和弦音符
    for chord in data.get('chords', []):
        start_time = chord.get('start_time')
        duration = chord.get('duration')
        
        # 為每個和弦音符添加音符
        for pitch in chord.get('notes', []):
            midi.addNote(1, 0, pitch, start_time, duration, 70)  # 和弦音量略小
    
    # 寫入MIDI文件
    with open(output_path, 'wb') as f:
        midi.writeFile(f)
    
    print(f"MIDI文件已保存至: {output_path}")
    return output_path

def play_midi_with_system(midi_path):
    """使用系統命令播放MIDI文件
    
    Args:
        midi_path: MIDI文件路徑
        
    Returns:
        bool: 是否成功播放
    """
    system = platform.system()
    
    try:
        if system == "Darwin":  # macOS
            print(f"在macOS上嘗試用系統播放器播放 {midi_path}...")
            # 使用open命令，這將用系統默認應用打開MIDI文件
            subprocess.run(["open", midi_path], check=True)
            return True
        elif system == "Windows":
            print(f"在Windows上嘗試用系統播放器播放 {midi_path}...")
            # Windows中使用默認關聯的程序打開MIDI文件
            os.startfile(os.path.abspath(midi_path))
            return True
        elif system == "Linux":
            print(f"在Linux上嘗試用timidity播放 {midi_path}...")
            # Linux中嘗試使用timidity播放
            subprocess.run(["timidity", midi_path], check=True)
            return True
        else:
            print(f"未知系統 {system}，無法使用系統命令播放MIDI")
            return False
    except Exception as e:
        print(f"使用系統命令播放MIDI時出錯: {e}")
        return False

def play_midi(midi_path):
    """播放MIDI文件
    
    Args:
        midi_path: MIDI文件路徑
    """
    try:
        # 直接使用系統命令播放MIDI
        success = play_midi_with_system(midi_path)
        
        if not success:
            # 如果系統命令失敗，嘗試使用pygame
            print("系統命令播放失敗，嘗試使用pygame...")
            
            # 初始化pygame
            pygame.init()
            pygame.mixer.init()
            
            # 在控制台顯示播放信息
            print(f"正在用pygame播放 {midi_path}...")
            print("按Ctrl+C停止播放")
            
            try:
                pygame.mixer.music.load(midi_path)
                pygame.mixer.music.play()
                
                # 等待播放完成
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                    
            except pygame.error as e:
                print(f"使用pygame無法播放MIDI文件: {e}")
                print(f"MIDI文件已保存在: {os.path.abspath(midi_path)}")
                print("請使用您系統上的MIDI播放器手動打開它")
            finally:
                # 清理pygame資源
                pygame.mixer.quit()
                pygame.quit()
            
    except KeyboardInterrupt:
        print("\n播放已停止")

def main():
    # 檢查命令行參數
    if len(sys.argv) < 2:
        print(f"用法: {sys.argv[0]} <json_file_path>")
        return
    
    json_path = sys.argv[1]
    
    # 檢查文件是否存在
    if not os.path.exists(json_path):
        print(f"錯誤: 文件 '{json_path}' 不存在")
        return
    
    # 轉換為MIDI
    midi_path = json_to_midi(json_path)
    
    # 播放MIDI
    play_midi(midi_path)

if __name__ == "__main__":
    main() 