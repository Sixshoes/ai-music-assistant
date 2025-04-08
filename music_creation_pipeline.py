"""音樂創作流水線

整合三階段流程：需求分析、參數生成和音樂創作
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

from music_requirement_analyzer import MusicRequirementAnalyzer, MusicRequirement, LLMProviderType
from ai-music-assistant.backend.music_generation.llm_music_generator import LLMMusicGenerator

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MusicCreationPipeline:
    """音樂創作流水線
    
    整合三階段流程：需求分析、參數生成和音樂創作
    """
    
    def __init__(self, 
                llm_api_key: Optional[str] = None, 
                llm_api_url: Optional[str] = None,
                provider_type: LLMProviderType = LLMProviderType.OLLAMA):
        """初始化音樂創作流水線
        
        Args:
            llm_api_key: 大語言模型API密鑰
            llm_api_url: 大語言模型API端點
            provider_type: 提供商類型
        """
        self.llm_api_key = llm_api_key
        self.llm_api_url = llm_api_url
        self.provider_type = provider_type
        
        # 初始化需求分析器
        self.requirement_analyzer = MusicRequirementAnalyzer(
            llm_api_key=llm_api_key,
            llm_api_url=llm_api_url,
            provider_type=provider_type
        )
        
        # 初始化音樂生成器
        self.music_generator = LLMMusicGenerator(
            llm_api_key=llm_api_key,
            llm_api_url=llm_api_url,
            provider_type=provider_type
        )
        
        logger.info(f"初始化音樂創作流水線，提供商: {provider_type.value}")
    
    def create_music(self, description: str, output_path: str) -> Dict[str, Any]:
        """創建音樂
        
        三階段流程：
        1. 分析用戶的音樂需求
        2. 根據需求生成音樂參數
        3. 基於參數創作音樂
        
        Args:
            description: 用戶的音樂創作需求描述
            output_path: 輸出文件路徑
            
        Returns:
            Dict[str, Any]: 創建結果，包含所有階段的數據
        """
        result = {
            "original_description": description,
            "stages": {}
        }
        
        try:
            # 第一階段：分析音樂需求
            logger.info(f"第一階段：分析音樂需求 - {description}")
            music_req = self.requirement_analyzer.analyze_music_requirement(description)
            result["stages"]["requirement_analysis"] = music_req.to_dict()
            
            # 從需求中提取基本參數
            from ai-music-assistant.mcp.mcp_schema import MusicParameters
            
            music_params = MusicParameters(
                tempo=music_req.tempo,
                key=music_req.key,
                genre=music_req.genre
            )
            
            # 創建增強的描述，包含更多音樂細節
            enhanced_description = self._create_enhanced_description(music_req)
            result["stages"]["enhanced_description"] = enhanced_description
            
            # 第二階段和第三階段：生成音樂
            logger.info(f"第二和第三階段：生成音樂 - {enhanced_description}")
            
            # 生成旋律
            melody = self.music_generator.generate_melody(enhanced_description, music_params)
            
            # 生成和弦進行
            chords = self.music_generator.generate_chord_progression(enhanced_description, music_params, melody)
            
            # 保存結果
            melody_data = [
                {
                    "pitch": note.pitch,
                    "start_time": note.start_time,
                    "duration": note.duration,
                    "velocity": note.velocity
                }
                for note in melody
            ]
            
            result["stages"]["music_generation"] = {
                "melody": melody_data,
                "chords": chords
            }
            
            # 保存結果到文件
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            # 保存MIDI文件
            melody_path = output_path.replace('.json', '_melody.mid')
            chord_path = output_path.replace('.json', '_chord.mid')
            
            from midiutil import MIDIFile
            
            # 保存旋律
            self._save_notes_to_midi(melody, melody_path, music_req.tempo)
            
            # 保存和弦
            self._save_chord_progression_to_midi(chords, chord_path, music_req.tempo)
            
            # 更新結果
            result["output_files"] = {
                "json": output_path,
                "melody_midi": melody_path,
                "chord_midi": chord_path
            }
            
            logger.info(f"音樂創作完成，結果保存至 {output_path}")
            
            return result
            
        except Exception as e:
            logger.error(f"音樂創作過程中發生錯誤: {str(e)}", exc_info=True)
            result["error"] = str(e)
            return result
    
    def _create_enhanced_description(self, music_req: MusicRequirement) -> str:
        """創建增強的描述
        
        根據音樂需求參數創建更詳細的描述，以便更好地指導音樂生成
        
        Args:
            music_req: 音樂需求參數
            
        Returns:
            str: 增強的描述
        """
        # 基本描述
        description = music_req.description
        
        # 添加風格和情感
        enhance = f"這是一首{music_req.genre}風格的音樂，表達{music_req.mood}的情感。"
        
        # 添加文化元素
        if music_req.cultural_elements:
            elements = "、".join(music_req.cultural_elements)
            enhance += f"融合了{elements}的文化元素。"
        
        # 添加樂器信息
        if music_req.instruments:
            instruments = "、".join(music_req.instruments)
            enhance += f"主要使用{instruments}演奏。"
        
        # 添加結構信息
        enhance += f"曲目結構為{music_req.form}，分為{music_req.section_count}個段落。"
        
        # 添加旋律和和聲特性
        enhance += f"旋律以{music_req.melodic_character}的特性為主，和聲複雜度為{music_req.harmonic_complexity}，節奏特徵為{music_req.rhythmic_features}。"
        
        # 添加技巧信息
        if music_req.techniques:
            techniques = "、".join(music_req.techniques)
            enhance += f"使用了{techniques}等演奏技巧。"
        
        # 組合原始描述和增強的描述
        enhanced_description = f"{description}\n\n詳細音樂指導：{enhance}\n調性：{music_req.key}，速度：{music_req.tempo} BPM，拍號：{music_req.time_signature}。"
        
        return enhanced_description
    
    def _save_notes_to_midi(self, notes: List[Any], output_path: str, tempo: int = 120) -> None:
        """保存音符到MIDI文件
        
        Args:
            notes: 音符列表
            output_path: 輸出路徑
            tempo: 速度
        """
        # 創建MIDI文件，單軌道
        midi = MIDIFile(1)
        
        # 設置速度
        midi.addTempo(0, 0, tempo)
        
        # 添加音符
        for note in notes:
            midi.addNote(
                track=0, 
                channel=0, 
                pitch=note.pitch, 
                time=note.start_time, 
                duration=note.duration, 
                volume=note.velocity
            )
        
        # 寫入文件
        with open(output_path, "wb") as f:
            midi.writeFile(f)
        
        logger.info(f"旋律MIDI文件已保存至 {output_path}")
    
    def _save_chord_progression_to_midi(self, chords: List[Dict[str, Any]], output_path: str, tempo: int = 120) -> None:
        """保存和弦進行到MIDI文件
        
        Args:
            chords: 和弦進行
            output_path: 輸出路徑
            tempo: 速度
        """
        # 創建MIDI文件，單軌道
        midi = MIDIFile(1)
        
        # 設置速度
        midi.addTempo(0, 0, tempo)
        
        # 添加和弦
        for chord in chords:
            for note in chord.get("notes", []):
                midi.addNote(
                    track=0, 
                    channel=0, 
                    pitch=note, 
                    time=chord["start_time"], 
                    duration=chord["duration"], 
                    volume=70
                )
        
        # 寫入文件
        with open(output_path, "wb") as f:
            midi.writeFile(f)
        
        logger.info(f"和弦MIDI文件已保存至 {output_path}")


# 測試代碼
if __name__ == "__main__":
    import argparse
    
    # 解析命令行參數
    parser = argparse.ArgumentParser(description="音樂創作流水線")
    parser.add_argument("--description", "-d", type=str, required=True, help="音樂創作需求描述")
    parser.add_argument("--output", "-o", type=str, default="output/music_creation_result.json", help="輸出文件路徑")
    parser.add_argument("--llm-service", type=str, default="ollama", choices=["ollama", "openai", "huggingface", "lmstudio"], help="LLM服務類型")
    parser.add_argument("--api-key", type=str, help="API密鑰")
    parser.add_argument("--api-url", type=str, help="API端點")
    parser.add_argument("--debug", action="store_true", help="啟用調試模式")
    
    args = parser.parse_args()
    
    # 設置日誌級別
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    
    # 從環境變量獲取API密鑰和URL（如果未提供）
    api_key = args.api_key
    api_url = args.api_url
    
    if args.llm_service == "openai":
        api_key = api_key or os.environ.get("OPENAI_API_KEY")
        api_url = api_url or "https://api.openai.com/v1/chat/completions"
        provider = LLMProviderType.OPENAI
    elif args.llm_service == "huggingface":
        api_key = api_key or os.environ.get("HF_API_KEY")
        api_url = api_url or os.environ.get("HF_API_URL")
        provider = LLMProviderType.HUGGINGFACE
    elif args.llm_service == "lmstudio":
        api_url = api_url or "http://localhost:1234/v1/chat/completions"
        provider = LLMProviderType.LMSTUDIO
    else:  # 默認使用ollama
        api_url = api_url or "http://localhost:11434/api/generate"
        provider = LLMProviderType.OLLAMA
    
    # 創建音樂創作流水線
    pipeline = MusicCreationPipeline(
        llm_api_key=api_key,
        llm_api_url=api_url,
        provider_type=provider
    )
    
    # 創建音樂
    result = pipeline.create_music(args.description, args.output)
    
    # 打印結果
    print("\n音樂創作完成!")
    print(f"原始描述: {result['original_description']}")
    print(f"增強描述: {result['stages'].get('enhanced_description', '')}")
    print(f"旋律MIDI: {result.get('output_files', {}).get('melody_midi', '')}")
    print(f"和弦MIDI: {result.get('output_files', {}).get('chord_midi', '')}")
    print(f"JSON結果: {result.get('output_files', {}).get('json', '')}") 