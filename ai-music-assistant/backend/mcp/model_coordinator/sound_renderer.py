import tempfile
import os
import subprocess
import logging

logger = logging.getLogger(__name__)

class SoundRenderer:
    def render_midi_to_audio(self, midi_data: bytes) -> bytes:
        """將 MIDI 數據渲染為音頻
        
        Args:
            midi_data: MIDI 數據
            
        Returns:
            bytes: WAV 格式的音頻數據
        """
        try:
            logger.info("開始渲染 MIDI 到音頻")
            
            # 檢查 MIDI 數據
            if not midi_data or len(midi_data) < 10:
                logger.error(f"MIDI 數據無效或太短: {len(midi_data)}")
                raise ValueError("MIDI 數據無效")
            
            # 檢查 MIDI 文件頭部
            midi_header = midi_data[:4]
            if midi_header != b'MThd':
                logger.error(f"MIDI 文件頭部無效: {midi_header}")
                raise ValueError("MIDI 文件格式無效")
            
            # 檢查 fluidsynth 是否安裝
            try:
                result = subprocess.run(['fluidsynth', '--version'], 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE, 
                                      check=True)
                logger.info(f"fluidsynth 版本: {result.stdout.decode().strip()}")
            except subprocess.CalledProcessError as e:
                logger.error(f"fluidsynth 未安裝或不可用: {e.stderr.decode()}")
                raise RuntimeError("fluidsynth 未安裝或不可用")
            
            # 創建臨時 MIDI 文件
            with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as midi_file:
                midi_file.write(midi_data)
                midi_path = midi_file.name
                logger.info(f"創建臨時 MIDI 文件: {midi_path}")
            
            try:
                # 創建臨時 WAV 文件
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as wav_file:
                    wav_path = wav_file.name
                    logger.info(f"創建臨時 WAV 文件: {wav_path}")
                
                # 使用 fluidsynth 渲染 MIDI
                soundfont_path = os.path.join(os.path.dirname(__file__), 'soundfonts', 'GeneralUser.sf2')
                if not os.path.exists(soundfont_path):
                    logger.error(f"找不到音色文件: {soundfont_path}")
                    raise FileNotFoundError(f"找不到音色文件: {soundfont_path}")
                
                # 構建 fluidsynth 命令
                cmd = [
                    'fluidsynth', '-F', wav_path,
                    '-ni', soundfont_path,
                    midi_path
                ]
                
                # 執行渲染
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                stdout, stderr = process.communicate()
                
                if process.returncode != 0:
                    logger.error(f"fluidsynth 渲染失敗: {stderr.decode()}")
                    raise RuntimeError(f"音頻渲染失敗: {stderr.decode()}")
                
                # 讀取生成的 WAV 文件
                with open(wav_path, 'rb') as f:
                    audio_data = f.read()
                
                if not audio_data:
                    logger.error("生成的音頻數據為空")
                    raise ValueError("音頻數據為空")
                
                # 檢查 WAV 文件頭部
                if not audio_data.startswith(b'RIFF') or b'WAVE' not in audio_data[:12]:
                    logger.error("生成的音頻不是有效的 WAV 格式")
                    raise ValueError("音頻格式無效")
                
                logger.info(f"音頻渲染成功，數據長度: {len(audio_data)}")
                return audio_data
                
            finally:
                # 清理臨時文件
                try:
                    os.unlink(midi_path)
                    os.unlink(wav_path)
                except Exception as e:
                    logger.warning(f"清理臨時文件時發生錯誤: {str(e)}")
        
        except Exception as e:
            logger.error(f"渲染 MIDI 到音頻時發生錯誤: {str(e)}", exc_info=True)
            raise 