#!/usr/bin/env python
"""
AI 音樂助手 - 交互式命令行版本

這個腳本提供一個簡單的命令行界面，讓用戶能夠生成和聆聽音樂。
"""

import os
import sys
import time
import random
import logging
import base64
import webbrowser
import subprocess
from pathlib import Path

# 嘗試導入 midiutil，用於創建真實的 MIDI 文件
try:
    from midiutil import MIDIFile
    HAVE_MIDIUTIL = True
except ImportError:
    HAVE_MIDIUTIL = False
    print("警告: 未安裝 midiutil 庫，無法生成真實 MIDI 文件")
    print("建議執行: pip install midiutil")

# 設置日誌記錄
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 設置環境變量以使用模擬服務
os.environ["USE_MOCK_MAGENTA"] = "true"

# 將當前目錄添加到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent))

# 檢查操作系統
IS_MAC = sys.platform == 'darwin'
IS_WINDOWS = sys.platform == 'win32'
IS_LINUX = sys.platform.startswith('linux')

# 設置 MIDI 文件播放命令
if IS_MAC:
    PLAY_COMMAND = 'open "{}"'
elif IS_WINDOWS:
    PLAY_COMMAND = 'start "" "{}"'
elif IS_LINUX:
    PLAY_COMMAND = 'xdg-open "{}"'
else:
    PLAY_COMMAND = None
    print("警告: 無法確定如何在您的操作系統上播放 MIDI 文件。")


def clear_screen():
    """清除屏幕"""
    os.system('cls' if IS_WINDOWS else 'clear')


def print_title():
    """打印標題"""
    print("\n" + "=" * 50)
    print("       AI 音樂助手 - 交互式命令行版本       ")
    print("=" * 50 + "\n")


def play_midi(midi_path):
    """播放 MIDI 文件"""
    if PLAY_COMMAND:
        try:
            subprocess.run(PLAY_COMMAND.format(midi_path), shell=True)
            return True
        except Exception as e:
            print(f"播放 MIDI 文件時出錯: {e}")
            return False
    else:
        print(f"無法播放 MIDI 文件，但您可以手動打開: {midi_path}")
        return False


def create_real_midi(notes, filename, tempo=120):
    """創建真實的 MIDI 文件，而不依賴 Magenta 的模擬服務
    
    Args:
        notes: 音符列表，每個音符應該有 pitch, start_time, duration, velocity 屬性
        filename: 輸出文件名
        tempo: 音樂速度 (BPM)
        
    Returns:
        midi_path: MIDI 文件路徑
    """
    if not HAVE_MIDIUTIL:
        print("無法創建真實 MIDI 文件，缺少 midiutil 庫")
        return None
        
    try:
        # 創建 MIDI 文件，1 個軌道
        midi = MIDIFile(1)

        # 設置軌道名稱和速度
        track = 0
        time = 0
        midi.addTrackName(track, time, "AI Generated Track")
        midi.addTempo(track, time, tempo)

        # 添加音符
        for note in notes:
            midi.addNote(
                track=track, 
                channel=0, 
                pitch=note.pitch, 
                time=note.start_time, 
                duration=note.duration, 
                volume=note.velocity
            )

        # 寫入文件
        with open(filename, "wb") as output_file:
            midi.writeFile(output_file)
            
        return os.path.abspath(filename)
    except Exception as e:
        print(f"創建 MIDI 文件時出錯: {e}")
        return None


def generate_simple_melody(key="C", tempo=120, num_notes=16):
    """生成一個簡單的旋律，不依賴 Magenta
    
    Args:
        key: 調性 (C, G, D, A, F, Am, Em, Dm)
        tempo: 速度 (BPM)
        num_notes: 音符數量
        
    Returns:
        notes: 音符列表
    """
    # 定義不同調性的音階
    scales = {
        "C":  [60, 62, 64, 65, 67, 69, 71, 72],  # C 大調
        "G":  [55, 57, 59, 60, 62, 64, 66, 67],  # G 大調
        "D":  [62, 64, 66, 67, 69, 71, 73, 74],  # D 大調
        "A":  [57, 59, 61, 62, 64, 66, 68, 69],  # A 大調
        "F":  [53, 55, 57, 58, 60, 62, 64, 65],  # F 大調
        "Am": [57, 59, 60, 62, 64, 65, 67, 69],  # A 小調
        "Em": [52, 54, 55, 57, 59, 60, 62, 64],  # E 小調
        "Dm": [50, 52, 53, 55, 57, 58, 60, 62],  # D 小調
    }
    
    # 默認使用 C 大調
    selected_scale = scales.get(key, scales["C"])
    
    # 創建一個類來模擬 Magenta 的 Note 對象
    class Note:
        def __init__(self, pitch, start_time, duration, velocity):
            self.pitch = pitch
            self.start_time = start_time
            self.duration = duration
            self.velocity = velocity
    
    # 生成音符
    notes = []
    current_time = 0.0
    beat_duration = 60 / tempo  # 一拍的持續時間 (秒)
    
    for i in range(num_notes):
        # 選擇音高
        pitch = random.choice(selected_scale)
        
        # 選擇持續時間
        durations = [0.25, 0.5, 1.0]  # 四分音符、二分音符、全音符（以拍為單位）
        weights = [0.6, 0.3, 0.1]     # 權重，更傾向於短音符
        duration = random.choices(durations, weights=weights)[0] * beat_duration
        
        # 選擇力度 (音量)
        velocity = random.randint(60, 100)
        
        # 創建音符
        note = Note(
            pitch=pitch,
            start_time=current_time,
            duration=duration,
            velocity=velocity
        )
        notes.append(note)
        
        # 更新時間
        current_time += duration
    
    return notes


def main():
    """主函數"""
    try:
        # 導入服務
        from backend.music_generation import MagentaService
        
        # 創建服務實例
        service = MagentaService()
        print("Magenta 服務初始化成功！\n")
        USE_MAGENTA = True
        
    except ImportError as e:
        logger.error(f"導入 Magenta 服務失敗: {e}")
        print("\n無法導入 Magenta 服務，將使用內置的簡單音樂生成功能。")
        USE_MAGENTA = False
    
    # 存儲生成的音樂
    generated_music = []
    
    while True:
        clear_screen()
        print_title()
        
        # 顯示主菜單
        print("請選擇操作:")
        print("1. 隨機生成旋律")
        print("2. 根據文本生成旋律")
        print("3. 生成完整編曲")
        print("4. 顯示生成的音樂列表")
        print("5. 關於 AI 音樂助手")
        
        if not USE_MAGENTA and HAVE_MIDIUTIL:
            print("6. 生成簡單可播放 MIDI (不使用 Magenta)")
            
        print("0. 退出")
        
        # 獲取用戶選擇
        choice = input("\n請輸入選項 (0-6): ")
        
        if choice == '0':
            print("\n感謝使用 AI 音樂助手！")
            break
            
        elif choice == '1' and USE_MAGENTA:
            # 隨機生成旋律
            clear_screen()
            print_title()
            print("【隨機生成旋律】\n")
            
            # 獲取參數
            tempo = int(input("請輸入速度 (BPM, 60-180): ") or "120")
            key = input("請輸入調性 (C, G, D, A, F, Am, Em, Dm): ") or "C"
            genre = input("請輸入風格 (pop, rock, jazz, classical): ") or "pop"
            
            # 創建參數對象
            class MusicParameters:
                def __init__(self):
                    self.tempo = tempo
                    self.key = key
                    self.genre = genre
                    self.description = f"{key} {genre} 音樂"
            
            params = MusicParameters()
            
            # 生成旋律
            print("\n正在生成旋律...")
            melody = service.generate_melody(params)
            print(f"生成了 {len(melody)} 個音符的旋律")
            
            # 將旋律保存為 MIDI
            timestamp = int(time.time())
            midi_filename = f"random_melody_{timestamp}.mid"
            
            # 使用 midiutil 創建真實的 MIDI 文件
            if HAVE_MIDIUTIL:
                midi_path = create_real_midi(melody, midi_filename, tempo)
                if midi_path:
                    print(f"真實 MIDI 旋律已保存到 {midi_path}")
                else:
                    # 使用模擬服務的 MIDI 生成
                    midi_path = os.path.abspath(midi_filename)
                    service.melody_to_midi(melody, midi_path, params.tempo)
                    print(f"旋律已保存到 {midi_path}")
            else:
                # 使用模擬服務的 MIDI 生成
                midi_path = os.path.abspath(midi_filename)
                service.melody_to_midi(melody, midi_path, params.tempo)
                print(f"旋律已保存到 {midi_path}")
            
            # 存儲音樂信息
            music_info = {
                "type": "旋律",
                "source": "隨機生成",
                "tempo": tempo,
                "key": key,
                "genre": genre,
                "notes_count": len(melody),
                "file_path": midi_path,
                "timestamp": timestamp
            }
            generated_music.append(music_info)
            
            # 詢問是否播放
            if input("\n是否立即播放? (y/n): ").lower().startswith('y'):
                play_midi(midi_path)
            
            input("\n按回車鍵繼續...")
            
        elif choice == '2' and USE_MAGENTA:
            # 根據文本生成旋律
            clear_screen()
            print_title()
            print("【根據文本生成旋律】\n")
            
            # 獲取參數
            text = input("請輸入音樂描述: ")
            if not text:
                print("錯誤: 必須提供文本描述！")
                input("\n按回車鍵繼續...")
                continue
                
            tempo = int(input("請輸入速度 (BPM, 60-180): ") or "120")
            key = input("請輸入調性 (C, G, D, A, F, Am, Em, Dm): ") or "C"
            
            # 創建參數對象
            class MusicParameters:
                def __init__(self):
                    self.tempo = tempo
                    self.key = key
                    self.genre = "pop"
                    self.description = text
            
            params = MusicParameters()
            
            # 生成旋律
            print("\n正在根據文本生成旋律...")
            melody = service.text_to_melody(text, params)
            print(f"生成了 {len(melody)} 個音符的旋律")
            
            # 將旋律保存為 MIDI
            timestamp = int(time.time())
            midi_filename = f"text_melody_{timestamp}.mid"
            
            # 使用 midiutil 創建真實的 MIDI 文件
            if HAVE_MIDIUTIL:
                midi_path = create_real_midi(melody, midi_filename, tempo)
                if midi_path:
                    print(f"真實 MIDI 旋律已保存到 {midi_path}")
                else:
                    # 使用模擬服務的 MIDI 生成
                    midi_path = os.path.abspath(midi_filename)
                    service.melody_to_midi(melody, midi_path, params.tempo)
                    print(f"旋律已保存到 {midi_path}")
            else:
                # 使用模擬服務的 MIDI 生成
                midi_path = os.path.abspath(midi_filename)
                service.melody_to_midi(melody, midi_path, params.tempo)
                print(f"旋律已保存到 {midi_path}")
            
            # 存儲音樂信息
            music_info = {
                "type": "旋律",
                "source": f"文本生成: {text}",
                "tempo": tempo,
                "key": key,
                "notes_count": len(melody),
                "file_path": midi_path,
                "timestamp": timestamp
            }
            generated_music.append(music_info)
            
            # 詢問是否播放
            if input("\n是否立即播放? (y/n): ").lower().startswith('y'):
                play_midi(midi_path)
            
            input("\n按回車鍵繼續...")
            
        elif choice == '3' and USE_MAGENTA:
            # 生成完整編曲
            clear_screen()
            print_title()
            print("【生成完整編曲】\n")
            
            # 獲取參數
            tempo = int(input("請輸入速度 (BPM, 60-180): ") or "120")
            key = input("請輸入調性 (C, G, D, A, F, Am, Em, Dm): ") or "C"
            genre = input("請輸入風格 (pop, rock, jazz, classical): ") or "pop"
            
            # 創建參數對象
            class MusicParameters:
                def __init__(self):
                    self.tempo = tempo
                    self.key = key
                    self.genre = genre
                    self.description = f"{key} {genre} 完整編曲"
            
            params = MusicParameters()
            
            # 生成編曲
            print("\n正在生成完整編曲...")
            arrangement = service.generate_full_arrangement(None, params)
            print(f"編曲已生成!")
            print(f"MIDI 文件位置: {arrangement.get('midi_path', 'unknown')}")
            
            # 獲取 MIDI 路徑
            midi_path = arrangement.get('midi_path', '')
            if not midi_path:
                print("錯誤: 無法獲取生成的 MIDI 文件路徑")
                input("\n按回車鍵繼續...")
                continue
            
            # 存儲音樂信息
            timestamp = int(time.time())
            music_info = {
                "type": "完整編曲",
                "source": "AI 生成",
                "tempo": tempo,
                "key": key,
                "genre": genre,
                "file_path": midi_path,
                "timestamp": timestamp
            }
            generated_music.append(music_info)
            
            # 詢問是否播放
            if input("\n是否立即播放? (y/n): ").lower().startswith('y'):
                play_midi(midi_path)
            
            input("\n按回車鍵繼續...")
            
        elif choice == '4':
            # 顯示生成的音樂列表
            clear_screen()
            print_title()
            print("【生成的音樂列表】\n")
            
            if not generated_music:
                print("尚未生成任何音樂！")
            else:
                for i, music in enumerate(generated_music, 1):
                    print(f"{i}. {music['type']} - {music['source']}")
                    print(f"   調性: {music['key']}, 速度: {music['tempo']} BPM")
                    if 'notes_count' in music:
                        print(f"   音符數量: {music['notes_count']}")
                    print(f"   文件: {music['file_path']}")
                    print()
                
                # 詢問是否播放
                play_choice = input("\n輸入編號播放音樂 (或按回車返回): ")
                if play_choice.isdigit() and 1 <= int(play_choice) <= len(generated_music):
                    idx = int(play_choice) - 1
                    play_midi(generated_music[idx]['file_path'])
            
            input("\n按回車鍵繼續...")
            
        elif choice == '5':
            # 關於
            clear_screen()
            print_title()
            print("【關於 AI 音樂助手】\n")
            print("AI 音樂助手是一個使用人工智能技術生成音樂的應用程序。")
            print("當前版本使用的是模擬模式，生成的音樂是通過簡單算法創建的示例。")
            print("\n使用說明:")
            print("- 生成的 MIDI 文件可以在音樂軟件中打開和編輯")
            print("- 在 Mac 上，可使用 GarageBand 或 QuickTime Player")
            print("- 在 Windows 上，可使用 Windows Media Player 或其他 MIDI 播放器")
            print("- 在 Linux 上，可使用 TiMidity++ 或其他 MIDI 播放器")
            
            input("\n按回車鍵繼續...")
        
        elif choice == '6' and not USE_MAGENTA and HAVE_MIDIUTIL:
            # 使用內置功能生成簡單 MIDI
            clear_screen()
            print_title()
            print("【生成簡單可播放 MIDI】\n")
            
            # 獲取參數
            tempo = int(input("請輸入速度 (BPM, 60-180): ") or "120")
            key = input("請輸入調性 (C, G, D, A, F, Am, Em, Dm): ") or "C"
            num_notes = int(input("請輸入音符數量 (8-32): ") or "16")
            
            if num_notes < 8:
                num_notes = 8
            elif num_notes > 32:
                num_notes = 32
            
            # 生成旋律
            print("\n正在生成簡單旋律...")
            melody = generate_simple_melody(key, tempo, num_notes)
            print(f"生成了 {len(melody)} 個音符的旋律")
            
            # 保存為 MIDI
            timestamp = int(time.time())
            midi_filename = f"simple_melody_{timestamp}.mid"
            midi_path = create_real_midi(melody, midi_filename, tempo)
            
            if midi_path:
                print(f"真實 MIDI 旋律已保存到 {midi_path}")
                
                # 存儲音樂信息
                music_info = {
                    "type": "簡單旋律",
                    "source": "內置生成器",
                    "tempo": tempo,
                    "key": key,
                    "notes_count": len(melody),
                    "file_path": midi_path,
                    "timestamp": timestamp
                }
                generated_music.append(music_info)
                
                # 詢問是否播放
                if input("\n是否立即播放? (y/n): ").lower().startswith('y'):
                    play_midi(midi_path)
            else:
                print("生成 MIDI 文件失敗")
            
            input("\n按回車鍵繼續...")
            
        else:
            print("\n無效的選項，請重新選擇！")
            input("\n按回車鍵繼續...")


if __name__ == "__main__":
    main() 