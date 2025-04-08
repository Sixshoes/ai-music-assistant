#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文本到音樂轉換程序

將用戶文本描述轉換為MIDI音樂的綜合應用程序。
整合了需求分析、參數生成、音樂創建和播放功能。
"""

import os
import sys
import json
import logging
import argparse
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from pathlib import Path
import random
import time

# 配置日誌
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 嘗試導入必要的MIDI工具
try:
    from midiutil import MIDIFile
except ImportError:
    logger.error("缺少midiutil套件，請執行: pip install midiutil")
    sys.exit(1)
    
try:
    import pygame
except ImportError:
    logger.warning("缺少pygame套件，無法播放MIDI。若要播放，請執行: pip install pygame")

# 導入現有的參數和和聲處理模組
LLM_MODULE_AVAILABLE = False
try:
    from music_requirement_analyzer import MusicRequirementAnalyzer, MusicRequirement, LLMProviderType
    LLM_MODULE_AVAILABLE = True
except ImportError:
    logger.warning("找不到LLM音樂需求分析模組，將使用簡化版分析器")

# 嘗試導入MCP相關模塊
MCP_MODULE_AVAILABLE = False
SIMPLIFIED_MCP_AVAILABLE = False

try:
    # 添加ai-music-assistant目錄到路徑
    sys.path.append(os.path.join(os.path.dirname(__file__), 'ai-music-assistant'))
    
    # 嘗試導入原始MCP服務
    try:
        from backend.mcp.music_tools_integrator import MusicToolsIntegrator
        MCP_MODULE_AVAILABLE = True
        logger.info("已成功導入MCP相關模組")
    except ImportError as e:
        logger.warning(f"無法導入原始MCP相關模組: {e}，將嘗試使用簡化版MCP")
        
        # 嘗試導入簡化版MCP服務
        try:
            from simplified_mcp import SimplifiedMCP
            SIMPLIFIED_MCP_AVAILABLE = True
            logger.info("已成功導入簡化版MCP模組")
        except ImportError as e:
            logger.warning(f"無法導入簡化版MCP模組: {e}，將使用本地實現")
except ImportError as e:
    logger.warning(f"無法導入任何MCP相關模組: {e}，將使用本地實現")

# 音樂參數模組路徑處理
try:
    # 嘗試從當前目錄導入
    from music_parameters import MusicParameters
    import sys, os
    sys.path.append('ai-music-assistant')
    from music_harmony import HarmonyAnalyzer, BassLineGenerator
except ImportError:
    try:
        # 嘗試從ai-music-assistant子目錄導入
        sys.path.append(os.path.join(os.path.dirname(__file__), 'ai-music-assistant'))
        from music_parameters import MusicParameters
        from music_harmony import HarmonyAnalyzer, BassLineGenerator
    except ImportError:
        logger.error("找不到音樂參數模組，請確保music_parameters.py和music_harmony.py在當前目錄或ai-music-assistant子目錄")
        sys.exit(1)

class Note:
    """音符類"""
    def __init__(self, pitch: int, start_time: float, duration: float, velocity: int = 100):
        self.pitch = pitch  # MIDI音高
        self.start_time = start_time  # 開始時間(拍)
        self.duration = duration  # 持續時間(拍)
        self.velocity = velocity  # 力度(0-127)

class TextToMusicConverter:
    """文本到音樂轉換器"""
    
    def __init__(self, use_llm: bool = False, llm_provider: str = "huggingface", llm_api_key: Optional[str] = None, llm_api_url: Optional[str] = None):
        """初始化文本到音樂轉換器
        
        Args:
            use_llm: 是否使用大語言模型進行分析
            llm_provider: 大語言模型提供商
            llm_api_key: API密鑰
            llm_api_url: API端點
        """
        self.use_llm = use_llm and LLM_MODULE_AVAILABLE
        
        if self.use_llm:
            # 設置LLM提供商類型
            provider_type = LLMProviderType.HUGGINGFACE
            if llm_provider.lower() == "openai":
                provider_type = LLMProviderType.OPENAI
            elif llm_provider.lower() == "lmstudio":
                provider_type = LLMProviderType.LMSTUDIO
            
            # 初始化需求分析器
            self.requirement_analyzer = MusicRequirementAnalyzer(
                llm_api_key=llm_api_key,
                llm_api_url=llm_api_url,
                provider_type=provider_type
            )
        
        # 嘗試初始化MCP工具整合器
        self.mcp_available = MCP_MODULE_AVAILABLE
        self.simplified_mcp_available = SIMPLIFIED_MCP_AVAILABLE
        
        if self.mcp_available:
            try:
                self.music_tools = MusicToolsIntegrator()
                logger.info("已初始化MCP音樂工具整合器")
            except Exception as e:
                logger.error(f"初始化MCP音樂工具整合器失敗: {e}")
                self.mcp_available = False
                
                # 如果原始MCP失敗，嘗試簡化版MCP
                if self.simplified_mcp_available:
                    try:
                        self.simplified_mcp = SimplifiedMCP()
                        logger.info("已初始化簡化版MCP服務")
                    except Exception as e:
                        logger.error(f"初始化簡化版MCP服務失敗: {e}")
                        self.simplified_mcp_available = False
        elif self.simplified_mcp_available:
            try:
                self.simplified_mcp = SimplifiedMCP()
                logger.info("已初始化簡化版MCP服務")
            except Exception as e:
                logger.error(f"初始化簡化版MCP服務失敗: {e}")
                self.simplified_mcp_available = False
        
        logger.info(f"初始化文本到音樂轉換器 (使用LLM: {self.use_llm}, 使用MCP: {self.mcp_available}, 使用簡化版MCP: {self.simplified_mcp_available})")
    
    def analyze_text(self, description: str) -> Dict[str, Any]:
        """分析文本描述，提取音樂參數
        
        Args:
            description: 用戶描述
            
        Returns:
            Dict: 音樂參數
        """
        logger.info(f"分析文本描述: {description}")
        
        if self.use_llm:
            # 使用LLM進行分析
            music_req = self.requirement_analyzer.analyze_music_requirement(description)
            return music_req.to_dict()
        else:
            # 使用簡化的文本分析
            return self._simple_text_analysis(description)
    
    def _simple_text_analysis(self, description: str) -> Dict[str, Any]:
        """簡化版文本分析（不依賴LLM）
        
        Args:
            description: 用戶描述
            
        Returns:
            Dict: 音樂參數
        """
        # 創建基本需求
        music_req = {
            "description": description,
            "genre": "古典",
            "mood": "平靜",
            "tempo": 100,
            "key": "C",
            "time_signature": "4/4",
            "form": "binary",
            "duration": 60,
            "section_count": 2,
            "cultural_elements": [],
            "instruments": ["piano"],
            "techniques": [],
            "melodic_character": "flowing",
            "harmonic_complexity": "moderate",
            "rhythmic_features": "regular"
        }
        
        # 分析文本意圖 - 風格判斷
        description = description.lower()
        
        # 識別風格
        if any(word in description for word in ["古典", "交響", "室內樂"]):
            music_req["genre"] = "古典"
        elif any(word in description for word in ["爵士", "藍調", "搖擺"]):
            music_req["genre"] = "爵士"
        elif any(word in description for word in ["流行", "現代", "通俗"]):
            music_req["genre"] = "流行"
        elif any(word in description for word in ["電子", "舞曲", "節拍"]):
            music_req["genre"] = "電子"
        elif any(word in description for word in ["搖滾", "rock"]):
            music_req["genre"] = "搖滾"
        elif any(word in description for word in ["民謠", "民歌", "傳統"]):
            music_req["genre"] = "民謠"
        
        # 識別情感
        if any(word in description for word in ["快樂", "歡快", "歡樂", "輕快", "喜悅"]):
            music_req["mood"] = "快樂"
        elif any(word in description for word in ["悲傷", "憂鬱", "傷感", "憂愁", "哀愁"]):
            music_req["mood"] = "悲傷"
        elif any(word in description for word in ["激動", "激昂", "熱烈", "熱情", "活潑"]):
            music_req["mood"] = "激動"
        elif any(word in description for word in ["平靜", "安詳", "寧靜", "沉思", "冥想", "放鬆"]):
            music_req["mood"] = "平靜"
        
        # 識別速度
        if any(word in description for word in ["快速", "快節奏", "急促", "活躍"]):
            music_req["tempo"] = random.randint(120, 160)
        elif any(word in description for word in ["中速", "適中", "中等"]):
            music_req["tempo"] = random.randint(90, 120)
        elif any(word in description for word in ["慢速", "緩慢", "從容", "悠閒"]):
            music_req["tempo"] = random.randint(60, 90)
        
        # 識別樂器
        instruments = []
        instrument_keywords = {
            "鋼琴": "piano", "吉他": "guitar", "小提琴": "violin", 
            "大提琴": "cello", "長笛": "flute", "單簧管": "clarinet",
            "雙簧管": "oboe", "薩克斯": "saxophone", "小號": "trumpet",
            "法國號": "french_horn", "長號": "trombone", "鼓": "drums",
            "電貝斯": "bass", "古箏": "guzheng", "琵琶": "pipa",
            "笛子": "dizi", "二胡": "erhu"
        }
        
        for zh_name, en_name in instrument_keywords.items():
            if zh_name in description:
                instruments.append(en_name)
        
        if instruments:
            music_req["instruments"] = instruments
        
        # 識別文化元素
        cultural_elements = []
        if any(word in description for word in ["中國", "東方", "古箏", "笛子", "琵琶", "二胡"]):
            cultural_elements.append("Chinese")
        elif any(word in description for word in ["日本", "和風", "三味線", "尺八"]):
            cultural_elements.append("Japanese")
        elif any(word in description for word in ["西班牙", "佛朗明哥", "弗拉門戈"]):
            cultural_elements.append("Spanish")
        
        if cultural_elements:
            music_req["cultural_elements"] = cultural_elements
        
        # 調整其他參數
        if "複雜" in description or "豐富" in description:
            music_req["harmonic_complexity"] = "complex"
        
        if "簡單" in description or "簡約" in description:
            music_req["harmonic_complexity"] = "simple"
        
        if "不規則" in description or "變化" in description:
            music_req["rhythmic_features"] = "irregular"
        
        return music_req
    
    def create_music(self, description: str, output_path: str, play: bool = False) -> Dict[str, Any]:
        """基於文本描述創建音樂
        
        Args:
            description: 用戶描述
            output_path: 輸出路徑
            play: 是否播放生成的音樂
            
        Returns:
            Dict: 包含創作過程和結果的字典
        """
        # 首先嘗試使用原始MCP服務
        if self.mcp_available:
            try:
                logger.info("嘗試使用MCP服務創建音樂")
                
                # 嘗試使用MCP生成音樂
                midi_path = os.path.splitext(output_path)[0] + "_mcp.mid"
                
                # 創建基本參數
                params = {
                    "description": description,
                    "output_path": midi_path
                }
                
                # 使用generate_musical_idea生成完整音樂
                try:
                    music_result = self.music_tools.generate_musical_idea(
                        parameters=params,
                        output_midi_path=midi_path
                    )
                    
                    logger.info(f"MCP已成功生成音樂: {midi_path}")
                    
                    # 如果生成成功，播放音樂
                    if play and os.path.exists(midi_path):
                        self._play_midi(midi_path)
                    
                    # 返回結果
                    return {
                        "original_description": description,
                        "output_file": midi_path,
                        "using_mcp": True,
                        "stages": {
                            "music_creation": music_result
                        }
                    }
                    
                except Exception as e:
                    logger.error(f"MCP生成musical_idea失敗: {e}")
                    # 繼續嘗試其他MCP方法
                
                # 嘗試使用更基本的旋律生成方法
                try:
                    # 生成旋律
                    melody = self.music_tools.generate_melody_from_text(description, params)
                    
                    if melody:
                        logger.info(f"MCP已生成旋律，長度: {len(melody)}")
                        
                        # 使用本地方法將旋律轉換為MIDI
                        melody_notes = [Note(
                            pitch=note.pitch,
                            start_time=note.start_time,
                            duration=note.duration,
                            velocity=note.velocity
                        ) for note in melody]
                        
                        # 使用本地方法處理後續步驟
                        # 創建基本音樂需求
                        music_req = {
                            "description": description,
                            "genre": "jazz",  # 基於描述猜測風格
                            "mood": "energetic",  # 基於描述猜測情感
                            "tempo": 120,
                            "instruments": ["piano"]
                        }
                        
                        # 使用本地方法處理後續步驟 (但使用MCP生成的旋律)
                        return self._create_music_with_local_method(melody_notes, music_req, output_path, play)
                except Exception as e:
                    logger.error(f"MCP生成旋律失敗: {e}")
                
            except Exception as e:
                logger.error(f"使用MCP服務失敗: {e}")
        
        # 如果原始MCP不可用或失敗，嘗試使用簡化版MCP
        if self.simplified_mcp_available:
            try:
                logger.info("嘗試使用簡化版MCP服務創建音樂")
                
                # 創建MIDI輸出路徑
                midi_path = os.path.splitext(output_path)[0] + "_simplified_mcp.mid"
                
                # 創建基本參數
                params = {
                    "description": description,
                    "key": "C",  # 默認C調
                    "tempo": 120  # 默認速度
                }
                
                # 使用簡化版MCP生成音樂
                music_result = self.simplified_mcp.generate_musical_idea(params, midi_path)
                
                logger.info(f"簡化版MCP已成功生成音樂: {midi_path}")
                
                # 如果生成成功，播放音樂
                if play and os.path.exists(midi_path):
                    self._play_midi(midi_path)
                
                # 返回結果
                return {
                    "original_description": description,
                    "output_file": midi_path,
                    "using_simplified_mcp": True,
                    "stages": {
                        "music_creation": music_result
                    }
                }
                
            except Exception as e:
                logger.error(f"使用簡化版MCP服務失敗: {e}")
        
        # 如果原始MCP和簡化版MCP都不可用或失敗，使用本地方法
        logger.info("使用本地方法創建音樂")
        return self._create_local_music(description, output_path, play)

    def _create_local_music(self, description: str, output_path: str, play: bool = False) -> Dict[str, Any]:
        """使用本地方法創建音樂
        
        Args:
            description: 用戶描述
            output_path: 輸出路徑
            play: 是否播放生成的音樂
            
        Returns:
            Dict: 包含創作過程和結果的字典
        """
        # 記錄整個過程
        result = {
            "original_description": description,
            "stages": {},
            "using_mcp": False
        }
        
        # 第一階段：分析意圖
        logger.info(f"第一階段：分析音樂意圖 - {description}")
        music_req = self.analyze_text(description)
        result["stages"]["intention_analysis"] = music_req
        
        logger.info(f"意圖分析結果: ")
        logger.info(f"  風格: {music_req['genre']}")
        logger.info(f"  情感: {music_req['mood']}")
        logger.info(f"  速度: {music_req['tempo']}")
        logger.info(f"  樂器: {', '.join(music_req['instruments'])}")
        
        # 輸出敘事分析結果
        if 'narrative_setting' in music_req:
            logger.info(f"  敘事場景: {music_req['narrative_setting']}")
        if 'occasion' in music_req:
            logger.info(f"  適用場合: {music_req['occasion']}")
        if 'cultural_background' in music_req:
            logger.info(f"  文化背景: {music_req['cultural_background']}")
            
        # 輸出樂器角色分配
        if 'instrument_roles' in music_req and music_req['instrument_roles']:
            logger.info(f"  樂器角色分配:")
            for instr, role in music_req['instrument_roles'].items():
                logger.info(f"    {instr}: {role}")
                
        # 輸出表現技巧建議
        if 'harmony_suggestions' in music_req and music_req['harmony_suggestions']:
            logger.info(f"  和聲語言建議: {', '.join(music_req['harmony_suggestions'][:3])}...")
        if 'arrangement_techniques' in music_req and music_req['arrangement_techniques']:
            logger.info(f"  配器技巧建議: {', '.join(music_req['arrangement_techniques'][:3])}...")
            
        if music_req.get('cultural_elements'):
            logger.info(f"  文化元素: {', '.join(music_req['cultural_elements'])}")
        
        # 第二階段：生成參數
        logger.info(f"第二階段：生成音樂參數")
        
        # 從意圖創建音樂參數
        style_mapping = {
            "古典": "古典",
            "爵士": "爵士",
            "流行": "流行",
            "電子": "電子",
            "搖滾": "流行",  # 映射到流行
            "民謠": "流行"   # 映射到流行
        }
        
        # 創建音樂參數
        music_style = style_mapping.get(music_req["genre"], "古典")
        music_params = MusicParameters(music_style)
        music_params.apply_emotion(music_req["mood"])
        
        # 設置速度
        tempo_range = (music_req["tempo"] - 10, music_req["tempo"] + 10)
        music_params.set_param("tempo_range", tempo_range)
        music_params.set_param("tempo", music_req["tempo"])
        
        # 根據和聲建議調整和聲複雜度
        if 'harmonic_complexity' in music_req:
            harmonic_complexity = 0.5  # 默認中等複雜度
            if music_req['harmonic_complexity'] == 'simple':
                harmonic_complexity = 0.3
            elif music_req['harmonic_complexity'] == 'complex':
                harmonic_complexity = 0.7
            music_params.set_param("harmonic_complexity", harmonic_complexity)
        
        # 根據節奏特徵調整節奏規律性
        if 'rhythmic_features' in music_req:
            rhythmic_regularity = 0.7  # 默認較規律
            if music_req['rhythmic_features'] == 'syncopated':
                rhythmic_regularity = 0.5
            elif music_req['rhythmic_features'] == 'complex':
                rhythmic_regularity = 0.3
            music_params.set_param("rhythmic_regularity", rhythmic_regularity)
            
        # 根據音色特徵調整音色
        if 'timbre_character' in music_req and music_req['timbre_character']:
            # 這裡可以添加對音色特徵的處理邏輯
            pass
        
        # 輸出生成的參數
        logger.info(f"生成的音樂參數:")
        logger.info(f"  風格: {music_style}")
        logger.info(f"  情感: {music_req['mood']}")
        logger.info(f"  速度: {music_params.get_param('tempo')}")
        logger.info(f"  音階: {music_params.get_param('scale')}")
        
        result["stages"]["parameter_generation"] = {
            "style": music_style,
            "emotion": music_req["mood"],
            "tempo": music_params.get_param("tempo"),
            "scale": music_params.get_param("scale"),
            "harmonic_complexity": music_params.get_param("harmonic_complexity", 0.5),
            "rhythmic_regularity": music_params.get_param("rhythmic_regularity", 0.7)
        }
        
        # 第二階段增強：生成歌曲結構
        logger.info(f"第二階段增強：生成歌曲結構")
        try:
            # 導入歌曲結構生成器
            from music_structure_generator import SongStructureGenerator
            structure_generator = SongStructureGenerator()
            
            # 使用music_req生成歌曲結構
            sections = structure_generator.generate_song_structure(music_req)
            
            # 為歌曲結構設計和聲
            sections = structure_generator.design_harmony_for_structure(sections, music_req)
            
            # 記錄歌曲結構
            result["stages"]["song_structure"] = {
                "sections": [
                    {
                        "name": section.name,
                        "start_bar": section.start_bar,
                        "length_bars": section.length_bars,
                        "dynamic_level": section.dynamic_level,
                        "instrumentation": section.instrumentation
                    } for section in sections
                ],
                "total_bars": sum(section.length_bars for section in sections)
            }
            
            logger.info(f"歌曲結構生成完成：{[section.name for section in sections]}")
            logger.info(f"總小節數：{sum(section.length_bars for section in sections)}")
            
            # 使用歌曲結構來生成完整的音樂
            has_structure = True
        except ImportError:
            logger.warning("無法導入歌曲結構生成器，將使用簡單結構")
            has_structure = False
        
        # 第三階段：創作音樂
        logger.info(f"第三階段：創作音樂")
        
        if has_structure:
            # 使用結構化生成
            return self._create_structured_music(music_params, sections, music_req, output_path, play, result)
        else:
            # 使用原始的簡單生成方法
            return self._create_simple_music(music_params, music_req, output_path, play, result)

    def _create_music_with_local_method(self, melody_notes, music_req, output_path, play):
        """使用本地方法完成音樂創作過程，但使用外部提供的旋律
        
        Args:
            melody_notes: 旋律音符列表
            music_req: 音樂需求字典
            output_path: 輸出路徑
            play: 是否播放
            
        Returns:
            Dict: 結果字典
        """
        # 記錄過程
        result = {
            "original_description": music_req.get("description", "生成的音樂"),
            "stages": {},
            "using_mcp": True,  # 部分使用MCP
            "mcp_contribution": "melody"  # MCP貢獻了旋律部分
        }
        
        # 創建音樂參數
        style = music_req.get("genre", "jazz").lower()
        music_style = style if style in ["古典", "爵士", "流行", "電子"] else "爵士"
        music_params = MusicParameters(music_style)
        
        # 應用情感
        music_params.apply_emotion(music_req.get("mood", "neutral"))
        
        # 設置速度
        tempo = music_req.get("tempo", 120)
        music_params.set_param("tempo", tempo)
        
        # 生成和弦進行
        chord_progression = music_params.get_chord_progression()
        
        # 記錄音樂創建階段
        result["stages"]["music_creation"] = {
            "melody_length": len(melody_notes),
            "chord_count": len(chord_progression)
        }
        
        # 生成低音聲部
        bass_generator = BassLineGenerator(music_style.lower())
        bass_notes, bass_durations = bass_generator.create_bass_line(chord_progression, music_style.lower())
        
        # 轉換為標準格式
        melody = []
        for note in melody_notes:
            melody.append(Note(
                pitch=note.pitch,
                start_time=note.start_time,
                duration=note.duration,
                velocity=note.velocity
            ))
        
        chords = []
        for i, chord in enumerate(chord_progression):
            chords.append({
                "start_time": i * 4.0,  # 每四拍一個和弦
                "duration": 4.0,
                "notes": chord
            })
        
        bass = []
        for i, note in enumerate(bass_notes):
            bass.append(Note(
                pitch=note,
                start_time=i,
                duration=1.0,
                velocity=70 + random.randint(-5, 5)
            ))
        
        # 保存為MIDI
        midi_path = self._save_to_midi(melody, chords, bass, music_params.get_param("tempo"), output_path)
        result["output_file"] = midi_path
        
        # 播放音樂
        if play:
            self._play_midi(midi_path)
        
        return result
    
    def _create_structured_music(self, music_params, sections, music_req, output_path, play, result):
        """使用結構化方法創建音樂
        
        Args:
            music_params: 音樂參數
            sections: 歌曲段落
            music_req: 音樂需求
            output_path: 輸出路徑
            play: 是否播放
            result: 結果字典
            
        Returns:
            Dict: 包含創作過程和結果的字典
        """
        # 獲取音樂風格
        music_style = music_req.get("genre", "classical").lower()
        
        # 獲取樂器列表
        instruments = music_req.get("instruments", ["piano"])
        instrument_roles = music_req.get("instrument_roles", {})
        
        # 如果沒有指定角色，根據樂器類型分配默認角色
        default_roles = {
            "piano": "melody",
            "guitar": "melody",
            "violin": "melody",
            "flute": "melody",
            "saxophone": "melody",
            "trumpet": "melody",
            "bass": "bass",
            "double_bass": "bass",
            "cello": "bass",
            "drums": "percussion",
            "percussion": "percussion",
            "synth": "harmony",
            "strings": "harmony",
            "organ": "harmony",
            "choir": "harmony"
        }
        
        # 確保每個樂器都有角色
        for instrument in instruments:
            if instrument not in instrument_roles:
                instrument_roles[instrument] = default_roles.get(instrument.lower(), "harmony")
        
        # 創建MIDI文件，每個樂器一個軌道
        track_count = len(instruments) + 1  # 加1是為了給總譜留一個軌道
        midi = MIDIFile(track_count)
        
        # 設置速度
        tempo = music_params.get_param("tempo")
        for i in range(track_count):
            midi.addTempo(i, 0, tempo)
        
        # 樂器到MIDI程序號的映射
        instrument_program_map = {
            "piano": 0,         # Acoustic Grand Piano
            "electric_piano": 4, # Electric Piano 1
            "organ": 19,        # Church Organ
            "guitar": 24,       # Acoustic Guitar (nylon)
            "electric_guitar": 27, # Electric Guitar (clean)
            "bass": 33,         # Electric Bass (finger)
            "violin": 40,       # Violin
            "viola": 41,        # Viola
            "cello": 42,        # Cello
            "double_bass": 43,  # Contrabass
            "strings": 48,      # String Ensemble 1
            "choir": 52,        # Choir Aahs
            "trumpet": 56,      # Trumpet
            "trombone": 57,     # Trombone
            "tuba": 58,         # Tuba
            "french_horn": 60,  # French Horn
            "saxophone": 66,    # Tenor Sax
            "clarinet": 71,     # Clarinet
            "flute": 73,        # Flute
            "recorder": 74,     # Recorder
            "pan_flute": 75,    # Pan Flute
            "sitar": 104,       # Sitar
            "banjo": 105,       # Banjo
            "shamisen": 106,    # Shamisen
            "koto": 107,        # Koto
            "kalimba": 108,     # Kalimba
            "bagpipe": 109,     # Bagpipe
            "fiddle": 110,      # Fiddle
            "shanai": 111,      # Shanai
            "bell": 112,        # Tinkle Bell
            "steel_drums": 114, # Steel Drums
            "wood_block": 115,  # Woodblock
            "taiko": 116,       # Taiko Drum
            "synth_pad": 88,    # Pad 1 (new age)
            "synth_lead": 80,   # Lead 1 (square)
            "synth_bass": 38,   # Synth Bass 1
            "drums": 118        # 鼓組使用General MIDI percussion channel
        }
        
        # 設置樂器音色
        for i, instrument in enumerate(instruments):
            # 獲取MIDI程序號
            program = instrument_program_map.get(instrument.lower(), 0)  # 默認為鋼琴
            # 鼓組特殊處理，使用第10通道(索引9)
            if instrument.lower() == "drums" or instrument.lower() == "percussion":
                channel = 9
            else:
                channel = i % 16
                if channel == 9:  # 避開第10通道(索引9)，它保留給打擊樂器
                    channel = 15
            
            # 設置樂器音色
            midi.addProgramChange(i, channel, 0, program)
        
        # 所有音符列表 (按樂器分類)
        all_notes_by_instrument = {instr: [] for instr in instruments}
        
        # 為每個段落生成音樂
        current_time = 0.0
        for section in sections:
            logger.info(f"生成段落 {section.name}，小節 {section.start_bar+1}-{section.end_bar+1}")
            
            # 獲取段落和弦進行
            chord_progression = section.chord_progression
            
            # 確保和弦中的所有音符都是整數
            if chord_progression:
                chord_progression = [[int(note) for note in chord] for chord in chord_progression]
            else:
                # 如果沒有具體的和弦進行，使用默認的
                chord_progression = music_params.get_chord_progression()
                chord_progression = [[int(note) for note in chord] for chord in chord_progression]
            
            # 按樂器角色分別生成音樂
            for i, instrument in enumerate(instruments):
                role = instrument_roles.get(instrument, "harmony")
                
                # 根據樂器角色生成相應的音樂
                if role == "melody":
                    # 生成旋律，長度為段落小節數 * 每小節4拍
                    melody_length = section.length_bars * 4
                    melody_notes = self._generate_melody(music_params, chord_progression, melody_length)
                    
                    # 根據段落特性調整旋律
                    if section.name in ["chorus", "C"]:
                        # 提高音域
                        melody_notes = [note + 3 if random.random() < 0.7 else note for note in melody_notes]
                        # 增加力度
                        velocity_base = 90
                    elif section.name in ["bridge", "B"]:
                        # 橋段可能有更多變化
                        melody_notes = [note + random.randint(-2, 4) if random.random() < 0.4 else note for note in melody_notes]
                        velocity_base = 85
                    elif section.name in ["intro", "outro"]:
                        # 前奏/尾聲可能更簡單
                        velocity_base = 75
                    else:
                        velocity_base = 80
                    
                    # 確保所有旋律音符都是整數
                    melody_notes = [int(note) if isinstance(note, (int, float)) else note for note in melody_notes]
                    
                    # 轉換為Note對象，並設置正確的時間
                    for j, note in enumerate(melody_notes):
                        all_notes_by_instrument[instrument].append({
                            "pitch": note,
                            "start_time": current_time + j * 0.25,  # 四分音符為1拍，每拍分為4個十六分音符
                            "duration": 0.25,
                            "velocity": velocity_base + random.randint(-10, 10)
                        })
                
                elif role == "bass":
                    # 生成低音聲部
                    bass_generator = BassLineGenerator(music_style)
                    bass_notes, _ = bass_generator.create_bass_line(chord_progression, music_style)
                    
                    # 確保所有低音音符都是整數
                    bass_notes = [int(note) if isinstance(note, (int, float)) else note for note in bass_notes]
                    
                    # 轉換為Note對象，並設置正確的時間
                    for j, note in enumerate(bass_notes):
                        all_notes_by_instrument[instrument].append({
                            "pitch": note,
                            "start_time": current_time + j * 0.5,  # 低音通常使用八分音符
                            "duration": 0.5,
                            "velocity": 70 + random.randint(-5, 5)
                        })
                
                elif role == "harmony":
                    # 和聲聲部使用和弦
                    for j, chord in enumerate(chord_progression):
                        # 根據和弦音符生成和聲
                        for note in chord:
                            all_notes_by_instrument[instrument].append({
                                "pitch": note,
                                "start_time": current_time + j * 4.0,  # 每四拍一個和弦
                                "duration": 4.0,
                                "velocity": 60 + random.randint(-5, 5)
                            })
                
                elif role == "percussion":
                    # 打擊樂聲部
                    if instrument.lower() == "drums":
                        # 鼓組使用固定的節奏型
                        for j in range(section.length_bars * 4):  # 每小節4拍
                            # 低音鼓 (每拍的第1拍)
                            if j % 4 == 0:
                                all_notes_by_instrument[instrument].append({
                                    "pitch": 36,  # 低音鼓
                                    "start_time": current_time + j * 0.25,
                                    "duration": 0.25,
                                    "velocity": 100
                                })
                            
                            # 小鼓 (每拍的第2和第4拍)
                            if j % 2 == 1:
                                all_notes_by_instrument[instrument].append({
                                    "pitch": 38,  # 小鼓
                                    "start_time": current_time + j * 0.25,
                                    "duration": 0.25,
                                    "velocity": 80
                                })
                            
                            # 閉合踩鑔 (每個八分音符)
                            all_notes_by_instrument[instrument].append({
                                "pitch": 42,  # 閉合踩鑔
                                "start_time": current_time + j * 0.25,
                                "duration": 0.25,
                                "velocity": 70
                            })
                    else:
                        # 其他打擊樂器
                        for j in range(section.length_bars * 8):  # 每小節8個八分音符
                            if random.random() < 0.3:  # 30%的概率有音符
                                all_notes_by_instrument[instrument].append({
                                    "pitch": random.choice([47, 49, 51, 52, 55]),  # 不同的打擊樂音高
                                    "start_time": current_time + j * 0.5,
                                    "duration": 0.25,
                                    "velocity": 60 + random.randint(-10, 10)
                                })
            
            # 更新當前時間
            current_time += section.length_bars * 4.0
        
        # 寫入MIDI文件
        for i, instrument in enumerate(instruments):
            # 鼓組特殊處理，使用第10通道(索引9)
            if instrument.lower() == "drums" or instrument.lower() == "percussion":
                channel = 9
            else:
                channel = i % 16
                if channel == 9:  # 避開第10通道(索引9)，它保留給打擊樂器
                    channel = 15
                    
            # 寫入該樂器的所有音符
            for note in all_notes_by_instrument[instrument]:
                midi.addNote(
                    track=i, 
                    channel=channel, 
                    pitch=note["pitch"], 
                    time=note["start_time"], 
                    duration=note["duration"], 
                    volume=note["velocity"]
                )
        
        # 確保輸出目錄存在
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # 寫入文件
        with open(output_path, "wb") as f:
            midi.writeFile(f)
        
        logger.info(f"結構化MIDI文件已保存至 {output_path}，包含 {len(instruments)} 個樂器軌道")
        
        # 保存音樂生成結果
        result["stages"]["music_creation"] = {
            "instruments": instruments,
            "instrument_roles": instrument_roles,
            "total_bars": sum(section.length_bars for section in sections),
            "track_count": len(instruments)
        }
        result["output_file"] = output_path
        
        # 播放音樂
        if play:
            self._play_midi(output_path)
        
        return result
    
    def _create_simple_music(self, music_params, music_req, output_path, play, result):
        """使用簡單方法創建音樂（原始方法）
        
        Args:
            music_params: 音樂參數
            music_req: 音樂需求
            output_path: 輸出路徑
            play: 是否播放
            result: 結果字典
            
        Returns:
            Dict: 包含創作過程和結果的字典
        """
        # 生成和弦進行
        chord_progression = music_params.get_chord_progression()
        logger.info(f"生成和弦進行: {len(chord_progression)}個和弦")
        
        # 確保和弦中的所有音符都是整數
        chord_progression = [[int(note) for note in chord] for chord in chord_progression]
        
        # 生成旋律
        melody_notes = self._generate_melody(music_params, chord_progression)
        logger.info(f"生成旋律: {len(melody_notes)}個音符")
        
        # 確保所有旋律音符都是整數
        melody_notes = [int(note) if isinstance(note, (int, float)) else note for note in melody_notes]
        
        # 生成低音聲部
        bass_generator = BassLineGenerator(music_style.lower())
        bass_notes, _ = bass_generator.create_bass_line(chord_progression, music_style.lower())
        logger.info(f"生成低音聲部: {len(bass_notes)}個音符")
        
        # 轉換為標準格式
        melody = []
        for i, note in enumerate(melody_notes):
            melody.append(Note(
                pitch=note,
                start_time=i,
                duration=1.0,
                velocity=80 + random.randint(-10, 10)
            ))
        
        chords = []
        for i, chord in enumerate(chord_progression):
            chords.append({
                "start_time": i * 4.0,  # 每四拍一個和弦
                "duration": 4.0,
                "notes": chord
            })
        
        bass = []
        for i, note in enumerate(bass_notes):
            bass.append(Note(
                pitch=note,
                start_time=i,
                duration=1.0,
                velocity=70 + random.randint(-5, 5)
            ))
        
        # 保存結果
        result["stages"]["music_creation"] = {
            "melody": [{"pitch": n.pitch, "start_time": n.start_time, "duration": n.duration, "velocity": n.velocity} for n in melody],
            "chords": chords,
            "bass": [{"pitch": n.pitch, "start_time": n.start_time, "duration": n.duration, "velocity": n.velocity} for n in bass]
        }
        
        # 保存為MIDI
        midi_path = self._save_to_midi(melody, chords, bass, music_params.get_param("tempo"), output_path)
        result["output_file"] = midi_path
        
        # 播放音樂
        if play:
            self._play_midi(midi_path)
        
        return result
    
    def _generate_melody(self, music_params, chord_progression, length=32) -> List[int]:
        """基於參數生成旋律
        
        Args:
            music_params: 音樂參數
            chord_progression: 和弦進行
            length: 旋律長度
            
        Returns:
            List[int]: 旋律音符
        """
        melody = []
        
        # 獲取音階和調式
        scale = music_params.get_param("scale", "大調")
        scale_notes = music_params.get_scale_notes()
        
        # 旋律輪廓類型
        contour = music_params.get_param("melodic_contour", "arch")
        
        # 根據輪廓生成方向趨勢
        directions = []
        if contour == "arch":
            # 拱形：上升然後下降
            mid_point = length // 2
            for i in range(length):
                if i < mid_point:
                    directions.append(1)  # 上升
                else:
                    directions.append(-1)  # 下降
        elif contour == "wave":
            # 波浪形：上下交替
            section_length = 4
            for i in range(length):
                section = (i // section_length) % 2
                if section == 0:
                    directions.append(1)  # 上升
                else:
                    directions.append(-1)  # 下降
        else:
            # 默認為隨機方向
            directions = [random.choice([-1, 0, 1]) for _ in range(length)]
        
        # 從首個和弦的音符開始
        if chord_progression and len(chord_progression) > 0:
            # 選擇和弦的根音或三音作為開始
            start_options = [chord_progression[0][0] % 12]
            if len(chord_progression[0]) >= 3:
                start_options.append(chord_progression[0][2] % 12)
            
            # 選擇一個八度
            octave = 5
            start_note = random.choice(start_options) + (octave * 12)
            current_note = start_note
            melody.append(current_note)
            
            # 根據音階和方向創建旋律
            for i in range(1, length):
                # 當前音高級別
                current_scale_idx = scale_notes.index(current_note % 12) if (current_note % 12) in scale_notes else 0
                
                # 根據方向決定下一個音符
                direction = directions[i]
                
                if direction > 0:  # 上升
                    scale_idx = (current_scale_idx + 1) % len(scale_notes)
                    next_note = scale_notes[scale_idx]
                    
                    # 確保實際上升
                    if next_note < (current_note % 12):
                        next_note += 12
                elif direction < 0:  # 下降
                    scale_idx = (current_scale_idx - 1) % len(scale_notes)
                    next_note = scale_notes[scale_idx]
                    
                    # 確保實際下降
                    if next_note > (current_note % 12):
                        next_note -= 12
                else:  # 保持
                    next_note = current_note % 12
                
                # 計算完整音符（包括八度）
                octave_shift = 0
                if next_note >= 12:
                    octave_shift = 1
                    next_note %= 12
                elif next_note < 0:
                    octave_shift = -1
                    next_note += 12
                
                octave = (current_note // 12) + octave_shift
                
                # 新音符
                new_note = next_note + (octave * 12)
                
                # 偶爾添加更大的跳躍
                if random.random() < 0.15:  # 15%的機會
                    if random.random() < 0.5:  # 上下跳的機會均等
                        new_note += 12  # 上跳八度
                    else:
                        new_note -= 12  # 下跳八度
                
                # 確保在合理範圍內
                while new_note < 48:  # C3
                    new_note += 12
                while new_note > 84:  # C6
                    new_note -= 12
                
                melody.append(new_note)
                current_note = new_note
        
        # 和聲分析器和旋律調整
        harmony_analyzer = HarmonyAnalyzer()
        melody, _ = harmony_analyzer.validate_melody_with_chords(melody, [1.0] * len(melody), chord_progression)
        
        return melody
    
    def _save_to_midi(self, melody, chords, bass, tempo, output_path):
        """保存音樂到MIDI文件
        
        Args:
            melody: 旋律音符列表
            chords: 和弦列表
            bass: 低音音符列表
            tempo: 速度
            output_path: 輸出路徑
            
        Returns:
            str: MIDI文件路徑
        """
        # 創建MIDI文件，三個軌道：旋律、和弦和低音
        midi = MIDIFile(3)
        
        # 設置速度
        midi.addTempo(0, 0, tempo)
        midi.addTempo(1, 0, tempo)
        midi.addTempo(2, 0, tempo)
        
        # 添加旋律
        for note in melody:
            midi.addNote(
                track=0, 
                channel=0, 
                pitch=note.pitch, 
                time=note.start_time, 
                duration=note.duration, 
                volume=note.velocity
            )
        
        # 添加和弦
        for chord in chords:
            for note in chord["notes"]:
                midi.addNote(
                    track=1, 
                    channel=1, 
                    pitch=note, 
                    time=chord["start_time"], 
                    duration=chord["duration"], 
                    volume=70
                )
        
        # 添加低音
        for note in bass:
            midi.addNote(
                track=2, 
                channel=2, 
                pitch=note.pitch, 
                time=note.start_time, 
                duration=note.duration, 
                volume=note.velocity
            )
        
        # 確保輸出目錄存在
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # 寫入文件
        with open(output_path, "wb") as f:
            midi.writeFile(f)
        
        logger.info(f"MIDI文件已保存至 {output_path}")
        
        return output_path
    
    def _play_midi(self, midi_path):
        """播放MIDI文件
        
        Args:
            midi_path: MIDI文件路徑
        """
        try:
            # 初始化pygame
            if 'pygame' not in sys.modules:
                logger.error("無法播放MIDI：pygame庫未安裝")
                return
            
            pygame.mixer.init()
            pygame.init()
            
            try:
                # 載入MIDI文件
                pygame.mixer.music.load(midi_path)
                
                # 播放音樂
                logger.info(f"正在播放: {midi_path}")
                pygame.mixer.music.play()
                
                # 顯示進度
                song_length = 30  # 假設歌曲長度為30秒
                print("\n播放進度：", end="")
                
                for i in range(song_length):
                    if not pygame.mixer.music.get_busy():
                        break
                    print(".", end="", flush=True)
                    time.sleep(1)
                
                print("\n播放結束")
                
            except Exception as e:
                logger.error(f"載入MIDI文件時出錯: {str(e)}")
                
        except Exception as e:
            logger.error(f"播放時發生錯誤: {str(e)}")
        finally:
            # 清理pygame資源
            pygame.mixer.quit()
            pygame.quit()

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="文本到音樂轉換程序")
    parser.add_argument("--description", "-d", type=str, help="音樂創作意圖描述")
    parser.add_argument("--output", "-o", type=str, default="output/music_output.mid", help="輸出MIDI文件路徑")
    parser.add_argument("--play", "-p", action="store_true", help="生成後播放MIDI文件")
    parser.add_argument("--use-llm", action="store_true", help="使用大語言模型進行分析")
    parser.add_argument("--llm-provider", type=str, default="huggingface", choices=["openai", "huggingface", "lmstudio"], help="LLM提供商")
    parser.add_argument("--api-key", type=str, help="API密鑰")
    parser.add_argument("--api-url", type=str, help="API端點")
    parser.add_argument("--interactive", "-i", action="store_true", help="互動模式")
    parser.add_argument("--debug", action="store_true", help="啟用調試模式")
    
    args = parser.parse_args()
    
    # 設置日誌級別
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    
    # 創建轉換器
    converter = TextToMusicConverter(
        use_llm=args.use_llm,
        llm_provider=args.llm_provider,
        llm_api_key=args.api_key,
        llm_api_url=args.api_url
    )
    
    if args.interactive:
        # 互動模式
        print("\n=== 文本到音樂轉換器 ===\n")
        print("請輸入您的音樂創作需求描述 (輸入 'exit' 退出):")
        
        while True:
            description = input("\n> ")
            
            if description.lower() in ['exit', 'quit', '退出']:
                break
            
            if not description.strip():
                continue
            
            try:
                # 設置默認輸出文件名
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                output_path = f"output/music_{timestamp}.mid"
                
                # 創建音樂
                result = converter.create_music(description, output_path, args.play)
                
                # 打印結果
                print(f"\n音樂已生成: {result['output_file']}")
                
            except Exception as e:
                logger.error(f"創建音樂時發生錯誤: {str(e)}")
                print(f"錯誤: {str(e)}")
    else:
        # 命令行模式
        if not args.description:
            parser.print_help()
            print("\n錯誤: 在非互動模式下，必須提供 --description 參數")
            sys.exit(1)
        
        # 創建音樂
        result = converter.create_music(args.description, args.output, args.play)
        
        # 打印結果
        print(f"音樂已生成: {result['output_file']}")

if __name__ == "__main__":
    main() 