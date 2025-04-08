"""工作流程

實現音樂生成的工作流程
"""

import logging
import json
import base64
import os
import tempfile
import subprocess
import time
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from datetime import datetime
from ..mcp_schema import MCPCommand, MusicParameters, CommandStatus
from .music_generator import MusicGenerator
from .music_analyzer import MusicAnalyzer
from .score_generator import ScoreGenerator
from .exceptions import CommandProcessingError
from .utils import save_command
import numpy as np
import random

logger = logging.getLogger(__name__)

class Workflow(ABC):
    """工作流程抽象基類"""
    
    def __init__(self):
        """初始化工作流程"""
        self.logger = logging.getLogger(__name__)
    
    @abstractmethod
    def execute(self, command: MCPCommand) -> Dict[str, Any]:
        """執行工作流程
        
        Args:
            command: MCP指令對象
            
        Returns:
            Dict[str, Any]: 處理結果字典
        """
        pass

# 初始化音樂生成器
music_generator = MusicGenerator()

# 初始化音樂分析器
music_analyzer = MusicAnalyzer()

class SoundRenderer:
    """音頻渲染器"""
    
    def render_midi_to_audio(self, midi_data: bytes) -> bytes:
        """將 MIDI 數據渲染為音頻數據
        
        Args:
            midi_data: MIDI 數據
            
        Returns:
            bytes: 音頻數據
        """
        try:
            if not midi_data or len(midi_data) < 10:
                logger.error(f"MIDI數據無效或太短: {len(midi_data) if midi_data else 0} 字節")
                return self._generate_audio_from_midi(midi_data)
                
            # 顯示MIDI頭部以進行調試
            try:
                header = midi_data[:16]
                hex_header = ' '.join([f'{b:02x}' for b in header])
                ascii_header = ''.join([chr(b) if 32 <= b <= 126 else '.' for b in header])
                logger.info(f"MIDI頭部(16字節): {hex_header} | ASCII: {ascii_header}")
            except Exception as e:
                logger.warning(f"無法顯示MIDI頭部: {str(e)}")
            
            # 創建臨時目錄儲存文件
            tmp_dir = tempfile.mkdtemp()
            midi_path = os.path.join(tmp_dir, "temp.mid")
            wav_path = os.path.join(tmp_dir, "output.wav")
            
            # 保存MIDI文件
            with open(midi_path, 'wb') as f:
                f.write(midi_data)
            
            # 使用 midiutil 生成音頻
            return self._generate_audio_from_midi(midi_data)
                
        except Exception as e:
            logger.error(f"音頻渲染失敗: {str(e)}")
            return self._generate_audio_from_midi(midi_data)
            
        finally:
            # 清理臨時文件
            try:
                if os.path.exists(midi_path):
                    os.remove(midi_path)
                if os.path.exists(wav_path):
                    os.remove(wav_path)
                os.rmdir(tmp_dir)
            except Exception as e:
                logger.warning(f"清理臨時文件失敗: {str(e)}")
                
    def _generate_audio_from_midi(self, midi_data: bytes) -> bytes:
        """從 MIDI 數據生成音頻
        
        Args:
            midi_data: MIDI 數據
            
        Returns:
            bytes: WAV 格式的音頻數據
        """
        import struct
        import math
        import random
        from midiutil import MIDIFile
        from io import BytesIO
        
        # 音頻參數
        sample_rate = 44100  # 採樣率
        duration = 10.0  # 持續時間
        volume = 0.5  # 音量
        
        # 從 MIDI 數據中提取音符信息
        midi_notes = []
        if midi_data and len(midi_data) > 10:
            try:
                midi_file = BytesIO(midi_data)
                for i, track in enumerate(midi_file.readlines()):
                    if track.startswith(b'MTrk'):
                        for event in track[4:]:
                            if event & 0x90 == 0x90:  # Note On 事件
                                note = event & 0x7F
                                midi_notes.append(note)
            except Exception as e:
                logger.warning(f"無法解析MIDI數據: {str(e)}")
        
        # 如果沒有提取到音符，使用默認音符
        if not midi_notes:
            midi_notes = [60, 64, 67, 72]  # C大調和弦
        
        # 計算樣本數
        num_samples = int(sample_rate * duration)
        samples = []
        
        # 生成音頻
        for i in range(num_samples):
            t = i / sample_rate
            sample = 0.0
            
            # 為每個音符生成正弦波
            for note in midi_notes:
                freq = 440.0 * (2 ** ((note - 69) / 12.0))  # MIDI音符到頻率的轉換
                sample += 0.25 * math.sin(2 * math.pi * freq * t)
            
            # 添加一些隨機變化使聲音更自然
            sample += 0.05 * (random.random() * 2 - 1)
            
            # 應用音量並轉換為16位整數
            sample = int(volume * sample * 32767)
            samples.append(max(-32768, min(32767, sample)))
        
        # 生成WAV文件
        wav = bytearray()
        
        # RIFF頭部
        wav.extend(b'RIFF')
        wav.extend(struct.pack('<I', 36 + len(samples) * 2))
        wav.extend(b'WAVE')
        
        # fmt塊
        wav.extend(b'fmt ')
        wav.extend(struct.pack('<I', 16))
        wav.extend(struct.pack('<H', 1))
        wav.extend(struct.pack('<H', 1))
        wav.extend(struct.pack('<I', sample_rate))
        wav.extend(struct.pack('<I', sample_rate * 2))
        wav.extend(struct.pack('<H', 2))
        wav.extend(struct.pack('<H', 16))
        
        # data塊
        wav.extend(b'data')
        wav.extend(struct.pack('<I', len(samples) * 2))
        for sample in samples:
            wav.extend(struct.pack('<h', sample))
        
        logger.info(f"生成了音頻數據，時長: {duration}秒，大小: {len(wav)}字節")
        return bytes(wav)

# 使用音頻渲染器
sound_renderer = SoundRenderer()

class TextToMusicWorkflow(Workflow):
    """文字到音樂工作流程"""
    
    def __init__(self):
        """初始化工作流程"""
        super().__init__()
        self.music_generator = MusicGenerator()
        self.score_generator = ScoreGenerator()
        
        # 風格關鍵詞映射
        self.style_keywords = {
            "classical": ["古典", "交響", "協奏", "奏鳴", "巴洛克", "浪漫", "室內樂", "莫札特", "貝多芬", "蕭邦", "弦樂"],
            "jazz": ["爵士", "藍調", "即興", "搖擺", "自由", "沙啞", "薩克斯風", "酒吧", "後現代", "Miles Davis"],
            "pop": ["流行", "通俗", "當代", "主流", "商業", "大眾", "熱門", "情歌", "偶像"],
            "rock": ["搖滾", "重金屬", "龐克", "硬核", "另類", "吉他", "激烈", "電吉他", "鼓手"],
            "electronic": ["電子", "舞曲", "節拍", "合成", "數字", "迷幻", "氛圍", "舞池", "夜店", "混音"],
            "folk": ["民謠", "傳統", "鄉村", "田園", "自然", "民族", "木吉他", "敘事"],
            "soundtrack": ["配樂", "電影", "影視", "背景", "遊戲", "壯麗", "史詩", "氣氛"]
        }
        
        # 情感關鍵詞映射
        self.emotion_keywords = {
            "happy": ["快樂", "歡快", "喜悅", "歡樂", "雀躍", "愉快", "開心", "正能量"],
            "sad": ["悲傷", "憂鬱", "憂愁", "哀愁", "傷感", "悲痛", "消沉", "低落"],
            "energetic": ["激動", "熱烈", "熱情", "活力", "振奮", "激昂", "興奮", "奔放"],
            "calm": ["平靜", "寧靜", "舒緩", "安寧", "平和", "緩慢", "安詳", "恬靜"],
            "mysterious": ["神秘", "詭異", "懸疑", "莫測", "奇異", "未知", "曖昧", "幽深"],
            "majestic": ["宏偉", "壯觀", "雄壯", "恢弘", "氣派", "莊嚴", "崇高", "壯麗"]
        }
        
        # 速度關鍵詞映射
        self.tempo_keywords = {
            "very_slow": ["極慢", "極緩", "非常慢", "十分緩慢", "極度舒緩"],
            "slow": ["慢", "緩慢", "舒緩", "悠閒", "從容"],
            "moderate": ["中速", "適中", "平穩", "均勻", "中庸"],
            "fast": ["快", "急促", "迅速", "活潑", "敏捷"],
            "very_fast": ["極快", "飛速", "疾速", "狂熱", "熱烈"]
        }
        
        # 樂器類型關鍵詞映射
        self.instrument_keywords = {
            "piano": ["鋼琴", "大鋼琴", "電鋼琴", "古鋼琴"],
            "strings": ["弦樂", "小提琴", "大提琴", "中提琴", "低音提琴", "弦樂四重奏", "弦樂合奏"],
            "guitar": ["吉他", "木吉他", "古典吉他", "電吉他", "民謠吉他", "原聲吉他"],
            "wind": ["管樂", "長笛", "單簧管", "雙簧管", "薩克斯風", "小號", "長號", "圓號"],
            "percussion": ["打擊樂", "鼓", "架子鼓", "定音鼓", "鐃鈸", "馬林巴", "鑼"],
            "synth": ["合成器", "電子", "合成音色", "人工", "數字音色", "虛擬音色"],
            "orchestral": ["管弦樂", "交響樂", "樂團", "合奏", "協奏", "大型樂隊"]
        }
    
    async def execute(self, command: MCPCommand, context: Dict[str, Any]) -> Dict[str, Any]:
        """執行文字到音樂工作流程
        
        Args:
            command: MCP指令對象
            context: 執行環境上下文
            
        Returns:
            Dict[str, Any]: 生成的音樂數據
        """
        try:
            logger.info(f"執行文字到音樂工作流程，輸入文字: {command.text}")
            
            # 提取音樂參數
            params = self._extract_music_parameters(command.text_input)
            
            # 生成 MIDI 數據
            midi_data = self.music_generator.generate(
                tempo=params.get('tempo'),
                key=params.get('key'),
                genre=params.get('genre'),
                instruments=params.get('instruments')
            )
            
            # 生成音頻數據
            audio_data = self.music_generator.midi_to_audio(midi_data)
            
            # 生成樂譜數據
            score_data = self.score_generator.generate_score_data(
                params.dict()
            )
            
            # 返回結果
            return {
                "midi": base64.b64encode(midi_data).decode(),
                "audio": base64.b64encode(audio_data).decode(),
                "score": score_data
            }
            
        except Exception as e:
            logger.error(f"執行工作流程時發生錯誤: {str(e)}")
            raise CommandProcessingError(command.command_id, str(e))
        
    def _extract_music_parameters(self, text_input: str, params: Any = None) -> Any:
        """從文本輸入中提取音樂參數
        
        Args:
            text_input: 文本輸入
            params: 現有參數 (可選)
            
        Returns:
            Any: 提取的音樂參數
        """
        # 確保 params 是有效的
        if params is None:
            # 初始化默認參數
            # 在實際實現中，這裡應使用 MusicParameters 類的實例
            params = {
                'tempo': None,
                'key': None,
                'genre': None,
                'instruments': None,
                'mood': None,
                'complexity': None,
                'time_signature': None,
                'structure': None,
                'duration': 60,
            }
        
        param_updates = {}
        
        # 提取風格
        if not params.get('genre'):
            detected_genres = []
            # 使用風格關鍵詞進行匹配
            for genre, keywords in self.style_keywords.items():
                for keyword in keywords:
                    if keyword in text_input:
                        detected_genres.append((genre, 1))
                        # 檢查是否有重複關鍵詞以增加權重
                        count = text_input.count(keyword)
                        if count > 1:
                            detected_genres[-1] = (genre, count)
            
            # 選擇出現次數最多的風格
            if detected_genres:
                detected_genres.sort(key=lambda x: x[1], reverse=True)
                param_updates["genre"] = detected_genres[0][0]
                logger.info(f"提取的風格: {param_updates['genre']} (權重: {detected_genres[0][1]})")
        
        # 提取情感/心情
        if not params.get('mood'):
            detected_emotions = []
            for emotion, keywords in self.emotion_keywords.items():
                for keyword in keywords:
                    if keyword in text_input:
                        detected_emotions.append((emotion, 1))
                        # 檢查是否有重複關鍵詞以增加權重
                        count = text_input.count(keyword)
                        if count > 1:
                            detected_emotions[-1] = (emotion, count)
            
            # 選擇出現次數最多的情感
            if detected_emotions:
                detected_emotions.sort(key=lambda x: x[1], reverse=True)
                param_updates["mood"] = detected_emotions[0][0]
                logger.info(f"提取的情感: {param_updates['mood']} (權重: {detected_emotions[0][1]})")
        
        # 提取速度
        if not params.get('tempo'):
            detected_tempos = []
            for tempo_cat, keywords in self.tempo_keywords.items():
                for keyword in keywords:
                    if keyword in text_input:
                        detected_tempos.append((tempo_cat, 1))
                        count = text_input.count(keyword)
                        if count > 1:
                            detected_tempos[-1] = (tempo_cat, count)
            
            # 將速度類別轉換為BPM值
            if detected_tempos:
                detected_tempos.sort(key=lambda x: x[1], reverse=True)
                tempo_category = detected_tempos[0][0]
                
                # 將類別映射到BPM範圍
                tempo_map = {
                    "very_slow": (40, 60),
                    "slow": (60, 85),
                    "moderate": (85, 110),
                    "fast": (110, 140),
                    "very_fast": (140, 200)
                }
                
                tempo_range = tempo_map.get(tempo_category, (90, 120))
                tempo_value = random.randint(*tempo_range)
                param_updates["tempo"] = tempo_value
                logger.info(f"提取的速度: {tempo_value} BPM (從類別: {tempo_category})")
        
        # 提取樂器
        if not params.get('instruments'):
            detected_instruments = []
            for inst_type, keywords in self.instrument_keywords.items():
                for keyword in keywords:
                    if keyword in text_input:
                        detected_instruments.append(inst_type)
                        break  # 找到一個關鍵詞就足以識別這類樂器
            
            if detected_instruments:
                param_updates["instruments"] = detected_instruments
                logger.info(f"提取的樂器: {', '.join(detected_instruments)}")
                
                # 為古典類型自動添加更多樂器，確保有足夠的音軌
                if 'classical' in param_updates.get('genre', '') and len(detected_instruments) < 3:
                    standard_classical = ["strings", "piano", "wind"]
                    for inst in standard_classical:
                        if inst not in detected_instruments:
                            detected_instruments.append(inst)
                    param_updates["instruments"] = detected_instruments
                    logger.info(f"為古典風格補充樂器: {', '.join(detected_instruments)}")
        
        # 提取複雜度 (基於文本描述推斷)
        if not params.get('complexity'):
            # 低複雜度關鍵詞
            low_complexity = ["簡單", "基本", "簡約", "清晰", "單一"]
            # 高複雜度關鍵詞
            high_complexity = ["複雜", "精細", "豐富", "複合", "華麗", "多層次", "交織"]
            
            complexity_value = 3  # 默認中等複雜度 (1-5)
            
            for keyword in low_complexity:
                if keyword in text_input:
                    complexity_value -= 1
                    break
            
            for keyword in high_complexity:
                if keyword in text_input:
                    complexity_value += 1
                    break
            
            # 限制在1-5範圍內
            complexity_value = max(1, min(5, complexity_value))
            param_updates["complexity"] = complexity_value
            logger.info(f"提取的複雜度: {complexity_value}/5")
        
        # 提取音樂結構 (例如 AABA, 回環曲, 奏鳴曲式等)
        if not params.get('structure'):
            structure_keywords = {
                "verse_chorus": ["主歌副歌", "verse-chorus", "常規歌曲"],
                "aaba": ["AABA", "32小節", "歌謠曲式"],
                "sonata": ["奏鳴曲", "sonata", "展開部"],
                "rondo": ["迴旋曲", "rondo"],
                "theme_variations": ["主題變奏", "變奏曲"],
                "through_composed": ["貫穿式", "自由發展"],
                "strophic": ["詩歌體", "重複段落"]
            }
            
            for structure, keywords in structure_keywords.items():
                for keyword in keywords:
                    if keyword in text_input:
                        param_updates["structure"] = structure
                        logger.info(f"提取的結構: {structure}")
                        break
                if "structure" in param_updates:
                    break
        
        # 提取曲目時長 (分析文本中的時間描述)
        if not params.get('duration') or params.get('duration') == 60:  # 默認長度的情況下才嘗試提取
            # 嘗試從數字提取
            import re
            time_patterns = [
                r'(\d+)[\s]*秒鐘',
                r'(\d+)[\s]*秒',
                r'(\d+)[\s]*分鐘'
            ]
            
            for pattern in time_patterns:
                matches = re.search(pattern, text_input)
                if matches:
                    value = int(matches.group(1))
                    if '分鐘' in pattern:
                        value *= 60  # 轉換為秒
                    param_updates["duration"] = value
                    logger.info(f"從數字提取的時長: {value}秒")
                    break
            
            # 如果沒有找到時間描述，使用較長的默認值
            if "duration" not in param_updates:
                param_updates["duration"] = 180  # 默認3分鐘
                logger.info(f"使用默認時長: 180秒")
        
        # 更新參數
        if param_updates:
            # 根據參數類型更新
            if isinstance(params, dict):
                for key, value in param_updates.items():
                    params[key] = value
            else:
                # 假設是某種對象型參數，使用setattr
                for key, value in param_updates.items():
                    if hasattr(params, key):
                        setattr(params, key, value)
        
        # 設置默認值
        if not params.get('tempo'):
            if isinstance(params, dict):
                params['tempo'] = 120
            else:
                params.tempo = 120
                
        if not params.get('key'):
            if isinstance(params, dict):
                params['key'] = "C"
            else:
                params.key = "C"
        
        return params

def process_text_to_music(command: MCPCommand) -> Dict[str, Any]:
    """處理文本到音樂的轉換
    
    Args:
        command: MCP命令
        
    Returns:
        Dict: 生成的音樂數據
    """
    try:
        logger.info("="*50)
        logger.info("開始處理文本到音樂轉換")
        logger.info(f"輸入文本: {command.text_input}")
        logger.info(f"參數: {command.parameters}")
        logger.info("="*50)
        
        # 檢查命令參數
        if not hasattr(command, 'parameters') or command.parameters is None:
            logger.error("❌ 命令參數為空")
            logger.info("使用默認參數")
            command.parameters = {
                'tempo': 120,
                'key': 'C',
                'genre': 'pop',
                'instruments': ['piano']
            }
        
        # 確保參數是字典類型
        if not isinstance(command.parameters, dict):
            logger.error(f"❌ 參數格式錯誤: {type(command.parameters)}")
            logger.info("嘗試轉換參數為字典格式")
            try:
                if hasattr(command.parameters, '__dict__'):
                    command.parameters = command.parameters.__dict__
                else:
                    command.parameters = dict(command.parameters)
            except Exception as e:
                logger.error(f"❌ 無法轉換參數為字典格式: {str(e)}")
                command.parameters = {
                    'tempo': 120,
                    'key': 'C',
                    'genre': 'pop',
                    'instruments': ['piano']
                }
        
        # 檢查並設置默認值
        default_params = {
            'tempo': 120,
            'key': 'C',
            'genre': 'pop',
            'instruments': ['piano']
        }
        
        # 合併默認參數和用戶參數
        for key, default_value in default_params.items():
            if key not in command.parameters or command.parameters[key] is None:
                logger.info(f"使用默認參數 {key}: {default_value}")
                command.parameters[key] = default_value
        
        logger.info("✅ 參數檢查通過")
        logger.info(f"最終參數: {command.parameters}")
        
        # 生成音樂
        logger.info("開始生成音樂...")
        music_data = music_generator.generate_music(command.parameters)
        if not music_data or "midi_data" not in music_data:
            logger.error("❌ 音樂生成失敗，返回的數據無效")
            raise ValueError("音樂生成失敗")
        
        # 檢查 MIDI 數據
        if not music_data["midi_data"] or len(music_data["midi_data"]) < 10:
            logger.error(f"❌ MIDI 數據無效或太短: {len(music_data['midi_data'])}")
            raise ValueError("MIDI 數據無效")
        
        # 檢查 MIDI 文件頭部
        midi_header = music_data["midi_data"][:4]
        if midi_header != b'MThd':
            logger.error(f"❌ MIDI 文件頭部無效: {midi_header}")
            raise ValueError("MIDI 文件格式無效")
        
        logger.info(f"✅ 音樂生成成功，MIDI數據長度: {len(music_data['midi_data'])}")
        
        # 渲染音頻
        logger.info("開始渲染音頻...")
        audio_data = sound_renderer.render_midi_to_audio(music_data["midi_data"])
        if not audio_data:
            logger.error("❌ 音頻渲染失敗")
            raise ValueError("音頻渲染失敗")
        
        # 檢查音頻數據
        if len(audio_data) < 44:  # WAV 文件頭部至少 44 字節
            logger.error(f"❌ 音頻數據太短: {len(audio_data)}")
            raise ValueError("音頻數據無效")
        
        # 檢查 WAV 文件頭部
        if not audio_data.startswith(b'RIFF') or b'WAVE' not in audio_data[:12]:
            logger.error("❌ 音頻格式無效")
            raise ValueError("音頻格式無效")
        
        logger.info(f"✅ 音頻渲染成功，音頻數據長度: {len(audio_data)}")
        
        # 構建結果
        result = {
            "midi_data": base64.b64encode(music_data["midi_data"]).decode('utf-8'),
            "audio_data": base64.b64encode(audio_data).decode('utf-8'),
            "score_data": {
                "musicxml": base64.b64encode(b"<musicxml>dummy</musicxml>").decode('utf-8'),
                "pdf": base64.b64encode(b"%PDF-1.4 dummy").decode('utf-8')
            },
            "analysis": music_data.get("analysis", {})
        }
        
        logger.info("="*50)
        logger.info("✅ 文本到音樂轉換完成")
        logger.info("="*50)
        return result
        
    except Exception as e:
        logger.error("="*50)
        logger.error("❌ 處理文本到音樂轉換時發生錯誤")
        logger.error(f"錯誤類型: {type(e).__name__}")
        logger.error(f"錯誤信息: {str(e)}")
        logger.error("="*50, exc_info=True)
        raise

def process_audio_to_music(command: MCPCommand) -> Dict[str, Any]:
    """處理音頻到音樂的轉換
    
    Args:
        command: MCP命令
        
    Returns:
        Dict: 生成的音樂數據
    """
    try:
        logger.info(f"執行音頻到音樂工作流程，輸入文字: {command.text}")
        
        # 使用音樂生成器生成音樂
        music_data = music_generator.generate_music(command.parameters)
        
        # 渲染音頻
        audio_data = sound_renderer.render_midi_to_audio(music_data["midi_data"])
        
        # 構建完整結果
        result = {
            "music_data": {
                "midi_data": base64.b64encode(music_data["midi_data"]).decode(),
                "audio_data": "data:audio/wav;base64," + base64.b64encode(audio_data).decode(),
                "score_data": {
                    "musicxml": base64.b64encode(b"dummy_musicxml").decode(),  # 待實現樂譜生成
                    "pdf": base64.b64encode(b"dummy_pdf").decode()  # 待實現PDF生成
                }
            }
        }
        
        return result
    
    except Exception as e:
        logger.error(f"處理音頻到音樂轉換時發生錯誤: {str(e)}")
        raise 

def generate_enhanced_test_audio(midi_data: bytes = None) -> bytes:
    """生成增強的測試音頻數據，根據MIDI數據特性
    
    Args:
        midi_data: MIDI數據，用於提取音樂特性
        
    Returns:
        bytes: WAV格式的音頻數據
    """
    import struct
    import math
    import random
    
    # 默認音頻參數
    sample_rate = 44100  # 採樣率
    duration = 10.0  # 持續時間
    base_frequency = 440.0  # A4音調(Hz)
    volume = 0.5  # 音量
    
    # 從MIDI數據中提取一些基本特性（如果可能）
    has_rhythm = False
    has_melody = True
    tempo_factor = 1.0
    
    if midi_data and len(midi_data) > 30:
        # 非常簡單的MIDI分析，只是為了生成略有區別的音頻
        has_rhythm = midi_data[20] > 100  # 隨機條件
        has_melody = midi_data[25] > 50   # 隨機條件
        tempo_factor = max(0.7, min(1.5, midi_data[15] / 100.0))  # 限制在合理範圍
    
    # 調整音頻參數
    tempo = 120 * tempo_factor  # BPM
    beats_per_second = tempo / 60
    
    # 計算樣本數
    num_samples = int(sample_rate * duration)
    samples = []
    
    # 音階頻率
    scale = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88]  # C4到B4
    
    # 生成更複雜的音頻
    for i in range(num_samples):
        t = i / sample_rate  # 時間(秒)
        sample = 0.0
        
        # 添加一個基本旋律
        if has_melody:
            melody_note = int((t * beats_per_second * 2) % len(scale))
            melody_freq = scale[melody_note] 
            sample += 0.3 * math.sin(2 * math.pi * melody_freq * t)
            
            # 添加一些和聲
            sample += 0.15 * math.sin(2 * math.pi * melody_freq * 1.5 * t)
        else:
            sample += 0.3 * math.sin(2 * math.pi * base_frequency * t)
        
        # 添加節奏元素
        if has_rhythm:
            # 簡單的節奏模式
            beat_position = (t * beats_per_second) % 1.0
            if beat_position < 0.1 or (beat_position > 0.5 and beat_position < 0.6):
                sample += 0.2 * math.sin(2 * math.pi * 100 * t)  # 低頻"鼓"聲
        
        # 稍微添加一些隨機噪聲，使聲音更豐富
        sample += 0.05 * (random.random() * 2 - 1)
        
        # 應用音量並轉換為16位整數
        sample = int(volume * sample * 32767)
        samples.append(max(-32768, min(32767, sample)))  # 確保在有效範圍內
    
    # 組裝WAV文件
    wav = bytearray()
    
    # RIFF頭部
    wav.extend(b'RIFF')
    wav.extend(struct.pack('<I', 36 + len(samples) * 2))  # 文件大小
    wav.extend(b'WAVE')
    
    # fmt塊
    wav.extend(b'fmt ')
    wav.extend(struct.pack('<I', 16))  # 塊大小
    wav.extend(struct.pack('<H', 1))  # 格式類型(PCM)
    wav.extend(struct.pack('<H', 1))  # 聲道數
    wav.extend(struct.pack('<I', sample_rate))  # 採樣率
    wav.extend(struct.pack('<I', sample_rate * 2))  # 每秒位元組數
    wav.extend(struct.pack('<H', 2))  # 塊對齊
    wav.extend(struct.pack('<H', 16))  # 每個樣本位元數
    
    # data塊
    wav.extend(b'data')
    wav.extend(struct.pack('<I', len(samples) * 2))  # 數據大小
    for sample in samples:
        wav.extend(struct.pack('<h', sample))  # 樣本數據
    
    logger.info(f"生成了增強的測試音頻，時長: {duration}秒，大小: {len(wav)}字節")
    return bytes(wav)

# 保留原始的測試音頻生成函數作為備用
def generate_test_audio() -> bytes:
    """生成簡單的測試音頻數據
    
    Returns:
        bytes: WAV格式的音頻數據
    """
    import struct
    import math
    import random
    
    # 音頻參數
    sample_rate = 44100  # 採樣率
    duration = 10.0  # 持續時間增加到10秒
    volume = 0.5  # 音量
    
    # 計算樣本數
    num_samples = int(sample_rate * duration)
    
    # 生成更豐富的音頻
    samples = []
    for i in range(num_samples):
        t = i / sample_rate  # 時間(秒)
        sample = 0.0
        
        # 添加主旋律（C大調音階）
        melody_freq = 440.0 * (2 ** (random.randint(-2, 2) / 12.0))  # 隨機選擇音高
        sample += 0.3 * math.sin(2 * math.pi * melody_freq * t)
        
        # 添加和聲
        harmony_freq = melody_freq * 1.5  # 五度音程
        sample += 0.2 * math.sin(2 * math.pi * harmony_freq * t)
        
        # 添加低音
        bass_freq = melody_freq * 0.5  # 低八度
        sample += 0.15 * math.sin(2 * math.pi * bass_freq * t)
        
        # 添加一些隨機變化
        sample += 0.05 * (random.random() * 2 - 1)
        
        # 應用音量並轉換為16位整數
        sample = int(volume * sample * 32767)
        samples.append(max(-32768, min(32767, sample)))  # 確保在有效範圍內
    
    # 組裝WAV文件
    wav = bytearray()
    
    # RIFF頭部
    wav.extend(b'RIFF')
    wav.extend(struct.pack('<I', 36 + len(samples) * 2))  # 文件大小
    wav.extend(b'WAVE')
    
    # fmt塊
    wav.extend(b'fmt ')
    wav.extend(struct.pack('<I', 16))  # 塊大小
    wav.extend(struct.pack('<H', 1))  # 格式類型(PCM)
    wav.extend(struct.pack('<H', 1))  # 聲道數
    wav.extend(struct.pack('<I', sample_rate))  # 採樣率
    wav.extend(struct.pack('<I', sample_rate * 2))  # 每秒位元組數
    wav.extend(struct.pack('<H', 2))  # 塊對齊
    wav.extend(struct.pack('<H', 16))  # 每個樣本位元數
    
    # data塊
    wav.extend(b'data')
    wav.extend(struct.pack('<I', len(samples) * 2))  # 數據大小
    for sample in samples:
        wav.extend(struct.pack('<h', sample))  # 樣本數據
    
    logger.info(f"生成了測試音頻，時長: {duration}秒，大小: {len(wav)}字節")
    return bytes(wav)