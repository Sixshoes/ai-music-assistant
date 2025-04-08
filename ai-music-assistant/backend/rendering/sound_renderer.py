"""音色渲染模組

提供音色渲染和音頻合成功能
"""

import os
import logging
from typing import Dict, List, Optional, Union
import numpy as np
from pathlib import Path
import fluidsynth as fs
import mido
from mido import MidiFile, MidiTrack, Message
import asyncio
import queue
import threading
import tempfile
import soundfile as sf
import subprocess
import shutil
import json

logger = logging.getLogger(__name__)

class SoundRenderer:
    """音色渲染器"""
    
    def __init__(self):
        """初始化音色渲染器"""
        self.fluidsynth = None
        self.soundfont_path = None
        self.realtime_queue = queue.Queue()
        self.is_realtime_running = False
        self.dexed_enabled = self._check_dexed_available()
        self.octasine_enabled = self._check_octasine_available()
        self.musescore_path = self._find_musescore_path()
        self._initialize_fluidsynth()
    
    def _check_dexed_available(self) -> bool:
        """檢查Dexed是否可用"""
        try:
            # 檢查Dexed相關文件是否存在
            current_dir = os.path.dirname(os.path.abspath(__file__))
            dexed_path = os.path.join(current_dir, "synths", "dexed")
            
            if os.path.exists(dexed_path):
                logger.info("Dexed 合成器可用")
                return True
            else:
                logger.info("Dexed 合成器不可用")
                return False
        except Exception as e:
            logger.warning(f"檢查Dexed可用性時出錯: {str(e)}")
            return False
    
    def _check_octasine_available(self) -> bool:
        """檢查OctaSine是否可用"""
        try:
            # 檢查OctaSine是否已安裝
            try:
                import octasine
                logger.info("OctaSine 合成器可用")
                return True
            except ImportError:
                # 嘗試檢查獨立安裝
                current_dir = os.path.dirname(os.path.abspath(__file__))
                octasine_path = os.path.join(current_dir, "synths", "octasine")
                
                if os.path.exists(octasine_path):
                    logger.info("OctaSine 合成器可用")
                    return True
                else:
                    logger.info("OctaSine 合成器不可用")
                    return False
        except Exception as e:
            logger.warning(f"檢查OctaSine可用性時出錯: {str(e)}")
            return False
    
    def _find_musescore_path(self) -> Optional[str]:
        """尋找MuseScore路徑"""
        try:
            # 常見的MuseScore安裝路徑
            common_paths = [
                # macOS
                "/Applications/MuseScore 4.app/Contents/MacOS/mscore",
                "/Applications/MuseScore 3.app/Contents/MacOS/mscore",
                # Windows
                "C:/Program Files/MuseScore 4/bin/MuseScore4.exe",
                "C:/Program Files/MuseScore 3/bin/MuseScore3.exe",
                # Linux
                "/usr/bin/musescore",
                "/usr/bin/mscore",
                "/usr/local/bin/musescore"
            ]
            
            # 檢查路徑是否存在
            for path in common_paths:
                if os.path.exists(path):
                    logger.info(f"找到MuseScore路徑: {path}")
                    return path
            
            # 嘗試通過which命令找到路徑
            try:
                result = subprocess.run(["which", "musescore"], 
                                       stdout=subprocess.PIPE, 
                                       stderr=subprocess.PIPE, 
                                       text=True, 
                                       check=False)
                if result.returncode == 0 and result.stdout.strip():
                    path = result.stdout.strip()
                    logger.info(f"找到MuseScore路徑: {path}")
                    return path
            except:
                pass
                
            logger.info("未找到MuseScore安裝")
            return None
            
        except Exception as e:
            logger.warning(f"尋找MuseScore路徑時出錯: {str(e)}")
            return None
    
    def _initialize_fluidsynth(self):
        """初始化FluidSynth"""
        try:
            # 嘗試使用系統默認音色庫
            default_soundfonts = [
                "/usr/share/sounds/sf2/FluidR3_GM.sf2",  # Linux
                "/Library/Audio/Sounds/Banks/FluidR3_GM.sf2",  # macOS
                os.path.expanduser("~/Library/Audio/Sounds/Banks/FluidR3_GM.sf2"),  # macOS user
                "/usr/local/share/fluidsynth/FluidR3_GM.sf2",  # Homebrew
            ]
            
            for sf_path in default_soundfonts:
                if os.path.exists(sf_path):
                    self.soundfont_path = sf_path
                    break
            
            # 如果找不到系統音色庫，使用本地音色庫
            if not self.soundfont_path:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                self.soundfont_path = os.path.join(current_dir, "soundfonts", "GeneralUser.sf2")
            
            if not os.path.exists(self.soundfont_path):
                raise FileNotFoundError(f"找不到音色庫文件: {self.soundfont_path}")
            
            # 初始化FluidSynth
            self.fluidsynth = fs.Synth(gain=0.5, samplerate=44100)
            self.fluidsynth.start()
            
            # 加載音色庫
            sfid = self.fluidsynth.sfload(self.soundfont_path)
            if sfid == -1:
                raise RuntimeError("無法加載音色庫文件")
                
            if self.fluidsynth.sfpreset_select(sfid, 0, 0) == -1:
                raise RuntimeError("無法選擇音色預設")
                
            logger.info(f"FluidSynth初始化成功，使用音色庫: {self.soundfont_path}")
        
        except Exception as e:
            logger.error(f"FluidSynth初始化失敗: {str(e)}")
            raise
    
    def start_realtime_rendering(self):
        """開始實時渲染"""
        if not self.is_realtime_running:
            self.is_realtime_running = True
            self.realtime_thread = threading.Thread(target=self._realtime_loop)
            self.realtime_thread.start()
    
    def stop_realtime_rendering(self):
        """停止實時渲染"""
        self.is_realtime_running = False
        if hasattr(self, 'realtime_thread'):
            self.realtime_thread.join()
    
    def _realtime_loop(self):
        """實時渲染循環"""
        while self.is_realtime_running:
            try:
                # 從隊列中獲取MIDI消息
                msg = self.realtime_queue.get(timeout=0.1)
                if msg.type == 'note_on':
                    self.fluidsynth.noteon(0, msg.note, msg.velocity)
                elif msg.type == 'note_off':
                    self.fluidsynth.noteoff(0, msg.note)
                elif msg.type == 'program_change':
                    self.fluidsynth.program_change(0, msg.program)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"實時渲染錯誤: {str(e)}")
    
    def send_realtime_message(self, msg: Message):
        """發送實時MIDI消息
        
        Args:
            msg: MIDI消息
        """
        self.realtime_queue.put(msg)
    
    def render_midi(self, midi_data: Dict, output_path: str, synth_type: str = "fluidsynth") -> str:
        """渲染MIDI數據為音頻
        
        Args:
            midi_data: MIDI數據
            output_path: 輸出文件路徑
            synth_type: 合成器類型，可選值: "fluidsynth", "dexed", "octasine"
            
        Returns:
            str: 生成的音頻文件路徑
        """
        try:
            # 創建MIDI文件
            midi_file = self._create_midi_file(midi_data)
            temp_midi_path = "temp_render.mid"
            midi_file.save(temp_midi_path)
            
            # 根據選擇的合成器渲染音頻
            if synth_type == "dexed" and self.dexed_enabled:
                audio_data = self._render_with_dexed(temp_midi_path)
            elif synth_type == "octasine" and self.octasine_enabled:
                audio_data = self._render_with_octasine(temp_midi_path)
            else:
                # 默認使用FluidSynth
                audio_data = self._render_with_fluidsynth(temp_midi_path)
            
            # 保存音頻文件
            self._save_audio(audio_data, output_path)
            
            # 清除臨時文件
            if os.path.exists(temp_midi_path):
                os.remove(temp_midi_path)
            
            return output_path
        
        except Exception as e:
            logger.error(f"MIDI渲染失敗: {str(e)}")
            raise
    
    def _create_midi_file(self, midi_data: Dict) -> MidiFile:
        """創建MIDI文件
        
        Args:
            midi_data: MIDI數據
            
        Returns:
            MidiFile: MIDI文件對象
        """
        try:
            # 創建MIDI文件
            midi = MidiFile()
            track = MidiTrack()
            midi.tracks.append(track)
            
            # 設置速度
            tempo = mido.bpm2tempo(midi_data.get("tempo", 120))
            track.append(mido.MetaMessage('set_tempo', tempo=tempo))
            
            # 設置拍號
            time_signature = midi_data.get("time_signature", "4/4")
            numerator, denominator = map(int, time_signature.split("/"))
            track.append(mido.MetaMessage(
                'time_signature',
                numerator=numerator,
                denominator=denominator
            ))
            
            # 添加音符
            for instrument, notes in midi_data.get("instruments", {}).items():
                # 設置樂器
                program = self._get_instrument_program(instrument)
                track.append(Message('program_change', program=program))
                
                # 添加音符
                for note in notes.get("notes", []):
                    track.append(Message(
                        'note_on',
                        note=self._note_to_midi(note),
                        velocity=64
                    ))
                    track.append(Message(
                        'note_off',
                        note=self._note_to_midi(note),
                        velocity=64,
                        time=notes.get("duration", 480)
                    ))
            
            return midi
        
        except Exception as e:
            logger.error(f"創建MIDI文件失敗: {str(e)}")
            raise
    
    def _render_with_fluidsynth(self, midi_path: str) -> np.ndarray:
        """使用FluidSynth渲染MIDI文件
        
        Args:
            midi_path: MIDI文件路徑
            
        Returns:
            np.ndarray: 音頻數據
        """
        try:
            # 使用FluidSynth渲染
            synth = fs.Synth(gain=0.5, samplerate=44100)
            synth.start()
            sfid = synth.sfload(self.soundfont_path)
            synth.program_select(0, sfid, 0, 0)
            
            # 創建臨時WAV文件
            temp_wav_path = midi_path.replace('.mid', '.wav')
            
            # 渲染MIDI到WAV
            synth.midi_to_audio(midi_path, temp_wav_path)
            
            # 讀取音頻數據
            audio_data, _ = sf.read(temp_wav_path)
            
            # 清理
            synth.delete()
            if os.path.exists(temp_wav_path):
                os.remove(temp_wav_path)
            
            return audio_data
            
        except Exception as e:
            logger.error(f"FluidSynth渲染失敗: {str(e)}")
            raise
    
    def _render_with_dexed(self, midi_path: str) -> np.ndarray:
        """使用Dexed渲染MIDI文件
        
        Args:
            midi_path: MIDI文件路徑
            
        Returns:
            np.ndarray: 音頻數據
        """
        try:
            # 檢查Dexed可執行文件
            current_dir = os.path.dirname(os.path.abspath(__file__))
            dexed_cli = os.path.join(current_dir, "synths", "dexed", "dexed_cli")
            
            if not os.path.exists(dexed_cli):
                raise FileNotFoundError(f"找不到Dexed CLI: {dexed_cli}")
            
            # 設置Dexed預設音色
            preset_path = os.path.join(current_dir, "synths", "dexed", "presets", "epiano.syx")
            
            # 創建臨時WAV文件
            temp_wav_path = midi_path.replace('.mid', '_dexed.wav')
            
            # 執行Dexed命令行工具渲染MIDI
            cmd = [
                dexed_cli,
                "--preset", preset_path,
                "--midi", midi_path,
                "--output", temp_wav_path
            ]
            
            process = subprocess.run(cmd, 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE, 
                                   check=True)
            
            # 讀取音頻數據
            if os.path.exists(temp_wav_path):
                audio_data, _ = sf.read(temp_wav_path)
                
                # 清理
                os.remove(temp_wav_path)
                
                return audio_data
            else:
                raise FileNotFoundError(f"Dexed未能生成音頻文件: {temp_wav_path}")
            
        except Exception as e:
            logger.error(f"Dexed渲染失敗，回退到FluidSynth: {str(e)}")
            return self._render_with_fluidsynth(midi_path)
    
    def _render_with_octasine(self, midi_path: str) -> np.ndarray:
        """使用OctaSine渲染MIDI文件
        
        Args:
            midi_path: MIDI文件路徑
            
        Returns:
            np.ndarray: 音頻數據
        """
        try:
            # 檢查OctaSine可執行文件
            current_dir = os.path.dirname(os.path.abspath(__file__))
            octasine_path = os.path.join(current_dir, "synths", "octasine", "octasine_cli")
            
            # 如果無法找到獨立可執行文件，嘗試使用Python庫
            if not os.path.exists(octasine_path):
                try:
                    import octasine
                    from octasine import OctaSine
                    import mido
                    import numpy as np
                    
                    # 加載MIDI文件
                    midi_file = mido.MidiFile(midi_path)
                    
                    # 初始化OctaSine
                    synth = OctaSine(samplerate=44100)
                    
                    # 渲染MIDI
                    buffer = np.zeros((int(midi_file.length * 44100), 2), dtype=np.float32)
                    synth.render_midi(midi_file, buffer)
                    
                    return buffer
                except ImportError:
                    raise RuntimeError("未找到OctaSine Python庫或獨立可執行文件")
            
            # 創建臨時WAV文件
            temp_wav_path = midi_path.replace('.mid', '_octasine.wav')
            
            # 執行OctaSine命令行工具渲染MIDI
            cmd = [
                octasine_path,
                "--midi", midi_path,
                "--output", temp_wav_path
            ]
            
            process = subprocess.run(cmd, 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE, 
                                   check=True)
            
            # 讀取音頻數據
            if os.path.exists(temp_wav_path):
                audio_data, _ = sf.read(temp_wav_path)
                
                # 清理
                os.remove(temp_wav_path)
                
                return audio_data
            else:
                raise FileNotFoundError(f"OctaSine未能生成音頻文件: {temp_wav_path}")
            
        except Exception as e:
            logger.error(f"OctaSine渲染失敗，回退到FluidSynth: {str(e)}")
            return self._render_with_fluidsynth(midi_path)
    
    def _save_audio(self, audio_data: np.ndarray, output_path: str):
        """保存音頻數據
        
        Args:
            audio_data: 音頻數據
            output_path: 輸出文件路徑
        """
        try:
            # 確保輸出目錄存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 保存為WAV文件
            sf.write(output_path, audio_data, 44100)
            
            logger.info(f"音頻文件已保存: {output_path}")
        
        except Exception as e:
            logger.error(f"保存音頻文件失敗: {str(e)}")
            raise
    
    def _get_instrument_program(self, instrument: str) -> int:
        """獲取樂器對應的MIDI程序號
        
        Args:
            instrument: 樂器名稱
            
        Returns:
            int: MIDI程序號
        """
        instrument_map = {
            # 鋼琴類
            "piano": 0,
            "electric_piano": 4,
            "honky_tonk": 3,
            "harpsichord": 6,
            
            # 弦樂器
            "violin": 40,
            "viola": 41,
            "cello": 42,
            "contrabass": 43,
            "harp": 46,
            
            # 吉他類
            "acoustic_guitar": 24,
            "electric_guitar": 27,
            "distortion_guitar": 30,
            "acoustic_bass": 32,
            "electric_bass": 33,
            
            # 管樂器
            "trumpet": 56,
            "trombone": 57,
            "french_horn": 60,
            "saxophone": 64,
            "oboe": 68,
            "bassoon": 70,
            "clarinet": 71,
            "piccolo": 72,
            "flute": 73,
            "recorder": 74,
            
            # 打擊樂器
            "drums": 128,
            "timpani": 47,
            "marimba": 12,
            "xylophone": 13,
            "vibraphone": 11,
            
            # 合成器
            "synth_bass": 38,
            "synth_lead": 80,
            "synth_pad": 88,
            
            # 其他
            "choir": 52,
            "organ": 19,
            "accordion": 21
        }
        return instrument_map.get(instrument.lower(), 0)
    
    def _note_to_midi(self, note: str) -> int:
        """將音符轉換為MIDI音符號
        
        Args:
            note: 音符名稱（如"C4"）
            
        Returns:
            int: MIDI音符號
        """
        note_map = {
            'C': 0, 'C#': 1, 'D': 2, 'D#': 3,
            'E': 4, 'F': 5, 'F#': 6, 'G': 7,
            'G#': 8, 'A': 9, 'A#': 10, 'B': 11
        }
        
        note_name = note[:-1]
        octave = int(note[-1])
        return note_map[note_name] + (octave + 1) * 12 

    def render_midi_to_audio(self, midi_data: bytes) -> bytes:
        """將MIDI數據渲染為音頻數據
        
        Args:
            midi_data: MIDI文件數據
            
        Returns:
            bytes: 音頻文件數據
        """
        try:
            # 創建臨時MIDI文件
            with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as midi_file:
                midi_file.write(midi_data)
                midi_path = midi_file.name
            
            # 創建臨時WAV文件
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as wav_file:
                wav_path = wav_file.name
            
            # 使用FluidSynth渲染音頻
            fs = fs.Synth()
            fs.start()
            
            # 加載音色庫
            soundfont_path = os.path.join(os.path.dirname(__file__), 'soundfonts', 'FluidR3_GM.sf2')
            sfid = fs.sfload(soundfont_path)
            fs.program_select(0, sfid, 0, 0)
            
            # 渲染MIDI到WAV
            fs.midi_to_audio(midi_path, wav_path)
            fs.delete()
            
            # 讀取WAV文件
            with open(wav_path, 'rb') as wav_file:
                audio_data = wav_file.read()
            
            # 清理臨時文件
            os.unlink(midi_path)
            os.unlink(wav_path)
            
            return audio_data
            
        except Exception as e:
            logger.error(f"渲染音頻時發生錯誤: {str(e)}")
            raise
            
    def __del__(self):
        """清理資源"""
        self.fluidsynth.delete()

    def export_to_musescore(self, midi_path: str, output_path: Optional[str] = None) -> str:
        """將MIDI文件轉換為MuseScore格式並導出
        
        Args:
            midi_path: MIDI文件路徑
            output_path: 輸出文件路徑，如果為None則自動生成
            
        Returns:
            str: 導出的文件路徑，可能是MSCZ或PDF格式
        """
        try:
            if not self.musescore_path or not os.path.exists(self.musescore_path):
                raise RuntimeError("未找到MuseScore安裝，無法導出")
            
            # 決定輸出路徑和格式
            if not output_path:
                output_path = midi_path.replace('.mid', '.mscz')
            
            # 獲取輸出格式
            output_format = output_path.split('.')[-1].lower()
            
            # 支持的格式: mscz, pdf, png, svg, mp3, wav, flac
            supported_formats = ['mscz', 'pdf', 'png', 'svg', 'mp3', 'wav', 'flac']
            if output_format not in supported_formats:
                output_format = 'mscz'
                output_path = f"{os.path.splitext(output_path)[0]}.{output_format}"
            
            # 構建MuseScore命令
            cmd = [
                self.musescore_path,
                "-o", output_path,   # 輸出路徑
                midi_path            # 輸入MIDI文件
            ]
            
            logger.info(f"執行MuseScore命令: {' '.join(cmd)}")
            
            # 執行MuseScore命令
            process = subprocess.run(cmd, 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE, 
                                   text=True, 
                                   check=False)
            
            if process.returncode != 0:
                logger.warning(f"MuseScore導出可能有問題: {process.stderr}")
            
            # 檢查文件是否創建
            if os.path.exists(output_path):
                logger.info(f"成功導出到MuseScore格式: {output_path}")
                return output_path
            else:
                raise FileNotFoundError(f"MuseScore未能生成文件: {output_path}")
            
        except Exception as e:
            logger.error(f"導出到MuseScore時出錯: {str(e)}")
            raise 