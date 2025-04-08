"""音樂工具整合器模組

封裝和整合 Magenta, Music21 和 Basic Pitch 等開源音樂工具的功能
"""

import os
import logging
import tempfile
import json
from typing import Dict, Any, List, Optional, Tuple, Union
import random

# 導入核心服務
from ..music_generation.magenta_service import MagentaService
from ..music_generation.music_vae_service import MusicVAEService
from ..music_generation.performance_rnn_service import PerformanceRNNService
from ..music_theory.music21_service import Music21Service
from ..audio_processing.basic_pitch_service import BasicPitchService

# 導入相關型別
from .mcp_schema import (
    MusicParameters,
    Note,
    MelodyInput,
    MusicTheoryAnalysis,
    ChordProgression
)

from ..music_generation import (
    HarmonyOptimizer,
    TimbreEngine,
    LLMMusicGenerator,
    LLMProviderType,
    LLMGenerationConfig
)

logger = logging.getLogger(__name__)


class MusicToolsIntegrator:
    """音樂工具整合器

    整合多種開源音樂工具，提供統一的接口，包括:
    - Magenta 深度學習模型
    - Music21 樂理分析
    - Basic Pitch 音頻處理
    """

    def __init__(self, model_paths: Optional[Dict[str, str]] = None):
        """初始化音樂工具整合器

        Args:
            model_paths: 模型路徑字典，例如 {"melody_rnn": "/path/to/model"}
        """
        logger.info("初始化音樂工具整合器")
        
        # 初始化各個服務
        self.magenta_service = MagentaService(model_paths)
        self.music_vae_service = MusicVAEService(model_paths)
        self.performance_rnn_service = PerformanceRNNService(model_paths)
        self.music21_service = Music21Service()
        self.basic_pitch_service = BasicPitchService()
        
        # 初始化LLM音樂生成器
        self._init_llm_music_generator()
        
    def _init_llm_music_generator(self):
        """初始化LLM音樂生成器"""
        # 從環境變量獲取設置
        llm_service = os.environ.get("LLM_SERVICE", "ollama").lower()
        
        # 根據所選服務設置參數
        if llm_service == "openai":
            llm_api_key = os.environ.get("OPENAI_API_KEY")
            llm_api_url = "https://api.openai.com/v1/chat/completions"
            provider = LLMProviderType.OPENAI
        elif llm_service == "huggingface" or llm_service == "hf":
            llm_api_key = os.environ.get("HF_API_KEY")
            llm_api_url = os.environ.get("HF_API_URL")
            provider = LLMProviderType.HUGGINGFACE
        elif llm_service == "lmstudio":
            llm_api_key = None
            llm_api_url = "http://localhost:1234/v1/chat/completions"
            provider = LLMProviderType.LMSTUDIO
        else:  # 默認使用ollama
            llm_api_key = None
            llm_api_url = "http://localhost:11434/api/generate"
            provider = LLMProviderType.OLLAMA
        
        # 創建配置
        config = LLMGenerationConfig(
            temperature=0.7,
            max_tokens=2048,
            system_message="你是一位專業的音樂作曲家助手，能根據文字描述創作出優質的旋律和和聲。"
        )
        
        # 創建生成器
        self.llm_music_generator = LLMMusicGenerator(
            llm_api_key=llm_api_key,
            llm_api_url=llm_api_url,
            provider_type=provider,
            config=config
        )
        
        logger.info(f"LLM音樂生成器初始化完成，使用提供商: {provider.value}")
        
    # ===== Magenta 相關功能 =====
    
    def generate_melody(self, 
                       parameters: MusicParameters,
                       primer_melody: Optional[List[Note]] = None,
                       num_steps: int = 128,
                       temperature: float = 1.0) -> List[Note]:
        """使用 Magenta 生成旋律

        Args:
            parameters: 音樂參數
            primer_melody: 引導旋律，如果提供則基於此旋律繼續生成
            num_steps: 生成的步數
            temperature: 生成的溫度參數，越高結果越隨機

        Returns:
            List[Note]: 生成的旋律音符列表
        """
        logger.info("使用 Magenta 生成旋律")
        return self.magenta_service.generate_melody(
            parameters=parameters,
            primer_melody=primer_melody,
            num_steps=num_steps,
            temperature=temperature
        )
    
    def generate_accompaniment(self, 
                              melody: List[Note], 
                              parameters: MusicParameters) -> Dict[str, List[Note]]:
        """使用 Magenta 為旋律生成伴奏

        Args:
            melody: 主旋律音符列表
            parameters: 音樂參數

        Returns:
            Dict[str, List[Note]]: 各聲部伴奏音符，如 {"chords": [...], "bass": [...]}
        """
        logger.info("使用 Magenta 生成伴奏")
        return self.magenta_service.generate_accompaniment(
            melody=melody,
            parameters=parameters
        )
    
    def generate_performance(self,
                           melody: List[Note],
                           parameters: MusicParameters,
                           style: Optional[str] = None) -> List[Note]:
        """使用 Performance RNN 生成富有表現力的演奏

        Args:
            melody: 主旋律音符列表
            parameters: 音樂參數
            style: 演奏風格，如 "classical", "jazz", "rock" 等

        Returns:
            List[Note]: 包含表現力的演奏音符列表
        """
        logger.info(f"使用 Performance RNN 生成 {style} 風格的演奏")
        
        # 使用 Performance RNN 服務生成演奏
        return self.performance_rnn_service.generate_performance(
            primer_melody=melody,
            parameters=parameters,
            style=style or "default",
            temperature=1.0
        )
    
    def apply_performance_style(self,
                               melody: List[Note],
                               style: str = "default",
                               temperature: float = 1.0) -> List[Note]:
        """使用 Performance RNN 將演奏風格應用到旋律

        Args:
            melody: 原始旋律音符列表
            style: 演奏風格，如 "default", "expressive", "virtuosic"
            temperature: 生成溫度參數，控制隨機性

        Returns:
            List[Note]: 應用演奏風格後的音符列表
        """
        logger.info(f"將 {style} 演奏風格應用到旋律")
        return self.performance_rnn_service.apply_performance_style(
            melody=melody,
            style=style,
            temperature=temperature
        )
    
    def generate_variation(self,
                         melody: List[Note],
                         parameters: MusicParameters,
                         variation_degree: float = 0.5) -> List[Note]:
        """使用 Music VAE 生成旋律變奏

        Args:
            melody: 原始旋律音符列表
            parameters: 音樂參數
            variation_degree: 變奏程度，0.0-1.0，越高變化越大

        Returns:
            List[Note]: 變奏後的旋律音符列表
        """
        logger.info(f"使用 Music VAE 生成旋律變奏，變奏程度: {variation_degree}")
        
        # 使用 Music VAE 服務生成變奏
        return self.music_vae_service.generate_variation(
            melody=melody,
            temperature=1.0,
            variation_degree=variation_degree
        )
    
    def interpolate_melodies(self,
                           melody1: List[Note],
                           melody2: List[Note],
                           num_steps: int = 5) -> List[List[Note]]:
        """使用 Music VAE 在兩個旋律之間生成平滑過渡

        Args:
            melody1: 第一個旋律音符列表
            melody2: 第二個旋律音符列表
            num_steps: 生成的過渡步數

        Returns:
            List[List[Note]]: 插值生成的旋律列表
        """
        logger.info(f"在兩個旋律之間生成 {num_steps} 步插值過渡")
        return self.music_vae_service.interpolate_melodies(
            melody1=melody1,
            melody2=melody2,
            num_steps=num_steps
        )
    
    def generate_drums(self,
                      num_measures: int = 4,
                      temperature: float = 1.0) -> List[Note]:
        """使用 Music VAE 生成鼓點模式

        Args:
            num_measures: 小節數
            temperature: 生成溫度，控制隨機性

        Returns:
            List[Note]: 生成的鼓點音符列表
        """
        logger.info(f"使用 Music VAE 生成 {num_measures} 小節鼓點模式")
        return self.music_vae_service.generate_drums(
            num_measures=num_measures,
            temperature=temperature
        )
    
    def midi_to_audio(self, notes: List[Note], output_path: str, tempo: int = 120) -> str:
        """將 MIDI 音符轉換為音頻

        Args:
            notes: MIDI 音符列表
            output_path: 輸出音頻路徑
            tempo: 速度 (BPM)

        Returns:
            str: 輸出音頻文件路徑
        """
        # 先將 MIDI 音符轉換為 MIDI 文件
        temp_dir = tempfile.gettempdir()
        midi_path = os.path.join(temp_dir, "temp_midi.mid")
        
        self.magenta_service.melody_to_midi(
            melody=notes, 
            output_path=midi_path, 
            tempo=tempo
        )
        
        # TODO: 將 MIDI 文件轉換為音頻文件
        # 這部分功能可能需要擴展到 rendering 服務
        
        return midi_path  # 暫時返回 MIDI 路徑，後續可替換為音頻路徑
        
    # ===== Music21 相關功能 =====
    
    def analyze_midi(self, midi_file_path: str) -> MusicTheoryAnalysis:
        """使用 Music21 分析 MIDI 文件

        Args:
            midi_file_path: MIDI 文件路徑

        Returns:
            MusicTheoryAnalysis: 音樂理論分析結果
        """
        logger.info(f"使用 Music21 分析 MIDI 文件: {midi_file_path}")
        return self.music21_service.analyze_midi_file(midi_file_path)
    
    def analyze_melody(self, notes: List[Note]) -> MusicTheoryAnalysis:
        """使用 Music21 分析旋律

        Args:
            notes: 旋律音符列表

        Returns:
            MusicTheoryAnalysis: 音樂理論分析結果
        """
        logger.info("使用 Music21 分析旋律")
        return self.music21_service.analyze_melody(notes)
    
    def validate_harmony(self, melody: List[Note], chords: List[str]) -> List[str]:
        """驗證旋律和和弦的和聲關係

        Args:
            melody: 旋律音符列表
            chords: 和弦標記列表

        Returns:
            List[str]: 和聲問題列表
        """
        # 這個功能需要擴展現有的 music21_service
        # 可以基於 analyze_melody 和 analyze_midi_file 中的邏輯實現
        logger.info("驗證旋律和和弦的和聲關係")
        
        # 簡單實現：分析旋律並提取和聲問題
        analysis = self.music21_service.analyze_melody(notes=melody)
        return analysis.harmony_issues
    
    def generate_sheet_music(self, notes: List[Note], output_path: str) -> str:
        """生成樂譜

        Args:
            notes: 音符列表
            output_path: 輸出樂譜文件路徑

        Returns:
            str: 輸出樂譜文件路徑
        """
        logger.info(f"生成樂譜: {output_path}")
        return self.music21_service.export_musicxml(notes, output_path)
    
    # ===== Basic Pitch 相關功能 =====
    
    def audio_to_midi(self, audio_file_path: str, output_path: Optional[str] = None) -> str:
        """使用 Basic Pitch 將音頻轉換為 MIDI

        Args:
            audio_file_path: 輸入音頻文件路徑
            output_path: 輸出 MIDI 文件路徑，如未指定則創建臨時文件

        Returns:
            str: 輸出 MIDI 文件路徑
        """
        logger.info(f"使用 Basic Pitch 將音頻轉換為 MIDI: {audio_file_path}")
        return self.basic_pitch_service.audio_to_midi(audio_file_path, output_path)
    
    def audio_to_melody(self, audio_file_path: str) -> MelodyInput:
        """使用 Basic Pitch 從音頻提取旋律

        Args:
            audio_file_path: 輸入音頻文件路徑

        Returns:
            MelodyInput: 包含旋律信息的對象
        """
        logger.info(f"使用 Basic Pitch 從音頻提取旋律: {audio_file_path}")
        return self.basic_pitch_service.audio_to_melody(audio_file_path)
    
    def correct_pitch(self, audio_file_path: str, output_path: Optional[str] = None) -> str:
        """使用 Basic Pitch 對音頻進行音準校正

        Args:
            audio_file_path: 輸入音頻文件路徑
            output_path: 輸出音頻文件路徑，如未指定則創建臨時文件

        Returns:
            str: 校正後的音頻文件路徑
        """
        logger.info(f"使用 Basic Pitch 進行音準校正: {audio_file_path}")
        return self.basic_pitch_service.correct_pitch(audio_file_path, output_path)
    
    # ===== 組合功能示例 =====
    
    def audio_to_sheet_music(self, audio_file_path: str, output_path: str) -> str:
        """將音頻轉換為樂譜

        綜合使用 Basic Pitch 和 Music21 的功能

        Args:
            audio_file_path: 輸入音頻文件路徑
            output_path: 輸出樂譜文件路徑

        Returns:
            str: 輸出樂譜文件路徑
        """
        logger.info(f"將音頻轉換為樂譜: {audio_file_path} -> {output_path}")
        
        # 使用 Basic Pitch 從音頻提取旋律
        melody_input = self.audio_to_melody(audio_file_path)
        
        # 使用 Music21 生成樂譜
        return self.music21_service.export_musicxml(melody_input.notes, output_path)
    
    def harmonize_melody(self, melody: List[Note], parameters: MusicParameters) -> Dict[str, Any]:
        """為旋律配和聲

        綜合使用 Magenta 和 Music21 的功能

        Args:
            melody: 旋律音符列表
            parameters: 音樂參數

        Returns:
            Dict[str, Any]: 配和聲結果，包含旋律和和聲
        """
        logger.info("為旋律配和聲")
        
        # 使用 Music21 分析旋律
        analysis = self.analyze_melody(melody)
        
        # 使用 Magenta 生成伴奏
        accompaniment = self.generate_accompaniment(melody, parameters)
        
        # 組合結果
        return {
            "melody": melody,
            "accompaniment": accompaniment,
            "analysis": analysis
        }
    
    def audio_to_expressive_performance(self, 
                                      audio_file_path: str, 
                                      output_midi_path: str,
                                      style: str = "default") -> str:
        """將錄音音頻轉換為富有表現力的 MIDI 演奏

        綜合使用 Basic Pitch 和 Performance RNN 的功能

        Args:
            audio_file_path: 輸入音頻文件路徑
            output_midi_path: 輸出 MIDI 文件路徑
            style: 演奏風格

        Returns:
            str: 輸出 MIDI 文件路徑
        """
        logger.info(f"將錄音轉換為富有表現力的 MIDI 演奏: {audio_file_path} -> {output_midi_path}")
        
        # 使用 Basic Pitch 從音頻提取旋律
        melody_input = self.audio_to_melody(audio_file_path)
        
        # 使用 Performance RNN 應用演奏風格
        performance_notes = self.apply_performance_style(
            melody=melody_input.notes,
            style=style
        )
        
        # 將演奏轉換為 MIDI 文件
        return self.performance_rnn_service.performance_to_midi(
            notes=performance_notes,
            output_path=output_midi_path,
            tempo=melody_input.tempo
        )
    
    def generate_musical_idea(self,
                            parameters: MusicParameters,
                            output_midi_path: str) -> Dict[str, Any]:
        """生成完整的音樂想法

        綜合使用多個生成模型創建完整的音樂片段

        Args:
            parameters: 音樂參數
            output_midi_path: 輸出 MIDI 文件路徑

        Returns:
            Dict[str, Any]: 生成結果，包含旋律、伴奏等元素
        """
        logger.info("生成完整的音樂想法")
        
        # 生成主旋律
        melody = self.generate_melody(
            parameters=parameters,
            num_steps=128,
            temperature=1.0
        )
        
        # 生成伴奏
        accompaniment = self.generate_accompaniment(melody, parameters)
        
        # 生成鼓點
        drums = self.generate_drums(num_measures=8)
        
        # 將旋律應用表現風格
        expressive_melody = self.apply_performance_style(
            melody=melody,
            style="expressive"
        )
        
        # 組合所有部分
        all_notes = expressive_melody + accompaniment.get("chords", []) + accompaniment.get("bass", []) + drums
        
        # 輸出到 MIDI 文件
        self.performance_rnn_service.performance_to_midi(
            notes=all_notes,
            output_path=output_midi_path,
            tempo=parameters.tempo or 120
        )
        
        # 返回結果
        return {
            "melody": melody,
            "expressive_melody": expressive_melody,
            "accompaniment": accompaniment,
            "drums": drums,
            "midi_path": output_midi_path
        }

    def generate_melody_from_text(self,
                               text_description: str,
                               parameters: MusicParameters) -> List[Note]:
        """使用文本描述生成旋律
        
        Args:
            text_description: 文本描述
            parameters: 音樂參數
            
        Returns:
            List[Note]: 生成的旋律
        """
        logger.info(f"根據文本描述生成旋律: {text_description}")
        
        # 決定使用哪種生成方法
        use_llm = os.environ.get("USE_LLM_FOR_MELODY", "false").lower() in ["true", "1", "yes", "y"]
        
        if use_llm and hasattr(self, 'llm_music_generator'):
            try:
                # 使用LLM生成旋律
                logger.info("使用LLM直接生成旋律")
                melody = self.llm_music_generator.generate_melody(text_description, parameters)
                logger.info(f"LLM生成了 {len(melody)} 個音符的旋律")
                return melody
            except Exception as e:
                logger.error(f"使用LLM生成旋律時出錯: {str(e)}，將使用傳統方法")
                # 如果LLM生成失敗，降級到傳統方法
        
        # 使用傳統Magenta方法
        return self.magenta_service.text_to_melody(text_description, parameters)

    def generate_chord_progression(self, 
                                melody: List[Note], 
                                parameters: MusicParameters) -> Dict[str, Any]:
        """為旋律生成和弦進行
        
        Args:
            melody: 旋律音符
            parameters: 音樂參數
            
        Returns:
            Dict[str, Any]: 和弦進行
        """
        logger.info("為旋律生成和弦進行")
        
        # 決定使用哪種生成方法
        use_llm = os.environ.get("USE_LLM_FOR_CHORDS", "false").lower() in ["true", "1", "yes", "y"]
        
        if use_llm and hasattr(self, 'llm_music_generator'):
            try:
                # 使用LLM生成和弦進行
                text_description = f"為{parameters.genre or '流行'}風格的{parameters.key or 'C'}調旋律生成和弦進行"
                logger.info(f"使用LLM直接生成和弦進行: {text_description}")
                
                chord_data = self.llm_music_generator.generate_chord_progression(
                    text_description, 
                    parameters, 
                    melody
                )
                
                logger.info(f"LLM生成了 {len(chord_data)} 個和弦")
                
                # 轉換為內部格式
                chords = []
                bass = []
                
                for chord in chord_data:
                    # 處理和弦音符
                    for pitch in chord.get("notes", []):
                        note = Note(
                            pitch=pitch,
                            start_time=chord["start_time"],
                            duration=chord["duration"],
                            velocity=70
                        )
                        chords.append(note)
                    
                    # 為每個和弦添加低音音符
                    # 通常和弦的根音是音符列表的第一個
                    if chord.get("notes") and len(chord["notes"]) > 0:
                        bass_pitch = chord["notes"][0] - 12  # 低八度
                        bass_note = Note(
                            pitch=bass_pitch,
                            start_time=chord["start_time"],
                            duration=chord["duration"],
                            velocity=80
                        )
                        bass.append(bass_note)
                
                return {
                    "chords": chords,
                    "bass": bass,
                    "original_data": chord_data  # 保留原始數據供參考
                }
                
            except Exception as e:
                logger.error(f"使用LLM生成和弦進行時出錯: {str(e)}，將使用傳統方法")
                # 如果LLM生成失敗，降級到傳統方法
        
        # 使用傳統Magenta方法或和聲優化器
        return self.magenta_service.generate_accompaniment(melody, parameters)

    def generate_arrangement_plan(self,
                              text_description: str,
                              parameters: MusicParameters) -> Dict[str, Any]:
        """生成編曲計劃
        
        Args:
            text_description: 文本描述
            parameters: 音樂參數
            
        Returns:
            Dict[str, Any]: 編曲計劃
        """
        logger.info(f"生成編曲計劃: {text_description}")
        
        # 確保參數中包含樂器列表
        genre = getattr(parameters, 'genre', 'pop')
        if not hasattr(parameters, 'instruments') or not parameters.instruments:
            # 嘗試使用LLM生成樂器推薦
            if hasattr(self, 'llm_music_generator'):
                try:
                    instruments = self.llm_music_generator.recommend_instruments_for_genre(genre)
                    setattr(parameters, 'instruments', instruments)
                    logger.info(f"根據風格'{genre}'自動推薦的樂器: {instruments}")
                except Exception as e:
                    logger.error(f"推薦樂器時出錯: {str(e)}")
        
        # 嘗試使用LLM生成編曲計劃
        if hasattr(self, 'llm_music_generator'):
            try:
                logger.info("使用LLM生成編曲計劃")
                arrangement_plan = self.llm_music_generator.generate_arrangement_plan(
                    text_description, 
                    parameters
                )
                
                logger.info("LLM成功生成編曲計劃")
                return arrangement_plan
                
            except Exception as e:
                logger.error(f"使用LLM生成編曲計劃時出錯: {str(e)}")
                # 繼續使用預設方法
        
        # 預設編曲計劃
        tempo = getattr(parameters, 'tempo', 120)
        
        # 獲取樂器 - 如果之前已經設置過，則使用已有的值
        instruments = getattr(parameters, 'instruments', None)
        
        # 如果沒有樂器，則使用默認樂器
        if not instruments:
            # 基於風格選擇樂器
            if genre == 'rock':
                instruments = ["electric_guitar", "bass", "drums", "keyboard"]
            elif genre == 'jazz':
                instruments = ["piano", "bass", "drums", "saxophone", "trumpet"]
            elif genre == 'classical':
                instruments = ["strings", "piano", "woodwinds", "brass"]
            elif genre == 'electronic':
                instruments = ["synth", "drums", "bass", "pad"]
            else:  # pop 和其他
                instruments = ["piano", "guitar", "bass", "drums"]
        
        # 創建簡單的編曲計劃
        arrangement_plan = {
            "arrangement_name": f"{genre.capitalize()} Arrangement at {tempo} BPM",
            "sections": [
                {
                    "name": "Intro",
                    "duration_bars": 4,
                    "instruments": [{"name": instr, "role": "intro"} for instr in instruments[:2]]
                },
                {
                    "name": "Verse",
                    "duration_bars": 8,
                    "instruments": [{"name": instr, "role": "verse"} for instr in instruments]
                },
                {
                    "name": "Chorus",
                    "duration_bars": 8,
                    "instruments": [{"name": instr, "role": "chorus"} for instr in instruments]
                },
                {
                    "name": "Outro",
                    "duration_bars": 4,
                    "instruments": [{"name": instr, "role": "outro"} for instr in instruments[:3]]
                }
            ],
            "instruments": [
                {"name": instr, "midi_program": self._get_instrument_program(instr)} 
                for instr in instruments
            ],
            "tempo": tempo,
            "key": getattr(parameters, 'key', 'C'),
            "genre": genre
        }
        
        return arrangement_plan
    
    def _get_instrument_program(self, instrument: str) -> int:
        """獲取樂器的MIDI程序號
        
        Args:
            instrument: 樂器名稱
            
        Returns:
            int: MIDI程序號
        """
        # 簡單的樂器映射表
        instrument_map = {
            'piano': 0,
            'electric_piano': 4,
            'guitar': 24,
            'electric_guitar': 27,
            'bass': 33,
            'strings': 48,
            'choir': 52,
            'trumpet': 56,
            'saxophone': 66,
            'flute': 73,
            'synth': 80,
            'pad': 88,
            'fx': 96,
            'drums': 118,  # 通常為打擊樂使用通道10
        }
        
        return instrument_map.get(instrument.lower(), 0) 