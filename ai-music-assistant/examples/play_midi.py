#!/usr/bin/env python3
"""MIDI播放器

用於播放MIDI文件的簡單腳本
"""

import os
import sys
import time
import argparse
import pygame
import pygame.midi

def play_midi_file(midi_file_path, duration=None):
    """播放MIDI文件
    
    Args:
        midi_file_path: MIDI文件路徑
        duration: 播放持續時間（秒）
    """
    # 初始化pygame和MIDI
    pygame.init()
    pygame.mixer.init()
    
    print(f"正在播放: {midi_file_path}")
    
    try:
        # 加載MIDI文件
        pygame.mixer.music.load(midi_file_path)
        
        # 播放MIDI
        pygame.mixer.music.play()
        
        # 如果指定了持續時間，等待指定時間
        if duration:
            time.sleep(duration)
        else:
            # 否則等待播放完成
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
                
        print("播放完成")
        
    except Exception as e:
        print(f"播放MIDI文件時出錯: {str(e)}")
    finally:
        # 清理
        pygame.mixer.quit()
        pygame.quit()

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="播放MIDI文件")
    parser.add_argument("midi_file", help="MIDI文件路徑")
    parser.add_argument("--duration", "-d", type=float, help="播放持續時間（秒）")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.midi_file):
        print(f"錯誤: 找不到MIDI文件 '{args.midi_file}'")
        sys.exit(1)
    
    play_midi_file(args.midi_file, args.duration)

if __name__ == "__main__":
    main() 