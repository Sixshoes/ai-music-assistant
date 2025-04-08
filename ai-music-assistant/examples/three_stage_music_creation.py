#!/usr/bin/env python3
"""三階段音樂創作示例

展示三階段音樂創作流程：需求分析、參數生成和音樂創作
"""

import os
import sys
import json
import logging
import argparse
from typing import Dict, Any, List, Optional
from pathlib import Path

# 添加項目根目錄到模塊搜索路徑
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.music_generation.music_requirement_analyzer import MusicRequirementAnalyzer, MusicRequirement, LLMProviderType
from backend.music_generation.llm_music_generator import LLMMusicGenerator
from mcp.mcp_schema import MusicParameters, Note

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def save_notes_to_midi(notes: List[Note], output_path: str, tempo: int = 120) -> None:
    """保存音符到MIDI文件
    
    Args:
        notes: 音符列表
        output_path: 輸出路徑
        tempo: 速度
    """
    from midiutil import MIDIFile
    
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

def save_chord_progression_to_midi(chords: List[Dict[str, Any]], output_path: str, tempo: int = 120) -> None:
    """保存和弦進行到MIDI文件
    
    Args:
        chords: 和弦進行
        output_path: 輸出路徑
        tempo: 速度
    """
    from midiutil import MIDIFile
    
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

def create_enhanced_description(music_req: MusicRequirement) -> str:
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

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="三階段音樂創作示例")
    parser.add_argument("--description", "-d", type=str, required=True, help="音樂創作需求描述")
    parser.add_argument("--output-dir", "-o", type=str, default="output", help="輸出目錄")
    parser.add_argument("--llm-service", "-s", type=str, default="huggingface", 
                        choices=["ollama", "openai", "huggingface", "lmstudio"], 
                        help="LLM服務類型")
    parser.add_argument("--api-key", "-k", type=str, help="API密鑰")
    parser.add_argument("--api-url", "-u", type=str, help="API端點")
    parser.add_argument("--debug", action="store_true", help="啟用調試模式")
    
    args = parser.parse_args()
    
    # 設置日誌級別
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    
    # 創建輸出目錄
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 從環境變量獲取API密鑰和URL（如果未提供）
    api_key = args.api_key
    api_url = args.api_url
    
    if args.llm_service == "openai":
        api_key = api_key or os.environ.get("OPENAI_API_KEY")
        api_url = api_url or "https://api.openai.com/v1/chat/completions"
        provider = LLMProviderType.OPENAI
    elif args.llm_service == "huggingface":
        api_key = api_key or os.environ.get("HF_API_KEY")
        api_url = api_url or os.environ.get("HF_API_URL", "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2")
        provider = LLMProviderType.HUGGINGFACE
    elif args.llm_service == "lmstudio":
        api_url = api_url or "http://localhost:1234/v1/chat/completions"
        provider = LLMProviderType.LMSTUDIO
    else:  # 默認使用ollama
        api_url = api_url or "http://localhost:11434/api/generate"
        provider = LLMProviderType.OLLAMA
    
    # 保存結果字典
    result = {
        "original_description": args.description,
        "stages": {}
    }
    
    try:
        # 第一階段：分析音樂需求
        logger.info("==================== 第一階段：分析音樂需求 ====================")
        logger.info(f"分析音樂需求: {args.description}")
        
        # 初始化需求分析器
        analyzer = MusicRequirementAnalyzer(
            llm_api_key=api_key,
            llm_api_url=api_url,
            provider_type=provider
        )
        
        # 分析音樂需求
        music_req = analyzer.analyze_music_requirement(args.description)
        result["stages"]["requirement_analysis"] = music_req.to_dict()
        
        # 打印分析結果
        logger.info("音樂需求分析結果:")
        logger.info(json.dumps(music_req.to_dict(), indent=2, ensure_ascii=False))
        
        # 第二階段：創建增強的描述，包含更多音樂細節
        logger.info("\n==================== 第二階段：創建增強的描述 ====================")
        enhanced_description = create_enhanced_description(music_req)
        result["stages"]["enhanced_description"] = enhanced_description
        
        logger.info(f"增強後的描述:\n{enhanced_description}")
        
        # 從需求中提取基本參數
        music_params = MusicParameters(
            tempo=music_req.tempo,
            key=music_req.key,
            genre=music_req.genre
        )
        
        # 第三階段：生成音樂
        logger.info("\n==================== 第三階段：生成音樂 ====================")
        
        # 初始化音樂生成器
        generator = LLMMusicGenerator(
            llm_api_key=api_key,
            llm_api_url=api_url,
            provider_type=provider
        )
        
        # 生成旋律
        logger.info(f"生成旋律...")
        melody = generator.generate_melody(enhanced_description, music_params)
        logger.info(f"成功生成旋律，共 {len(melody)} 個音符")
        
        # 生成和弦進行
        logger.info(f"生成和弦進行...")
        chords = generator.generate_chord_progression(enhanced_description, music_params, melody)
        logger.info(f"成功生成和弦進行，共 {len(chords)} 個和弦")
        
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
        
        # 保存JSON文件
        json_path = os.path.join(args.output_dir, "three_stage_result.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        # 保存MIDI文件
        melody_path = os.path.join(args.output_dir, "three_stage_melody.mid")
        chord_path = os.path.join(args.output_dir, "three_stage_chords.mid")
        
        # 保存旋律
        save_notes_to_midi(melody, melody_path, music_req.tempo)
        
        # 保存和弦
        save_chord_progression_to_midi(chords, chord_path, music_req.tempo)
        
        # 合併音樂數據為標準格式
        combined_data = {
            "description": args.description,
            "parameters": {
                "tempo": music_req.tempo,
                "key": music_req.key,
                "genre": music_req.genre
            },
            "melody": melody_data,
            "chords": chords
        }
        
        # 保存合併後的音樂數據
        combined_path = os.path.join(args.output_dir, "music_data.json")
        with open(combined_path, "w", encoding="utf-8") as f:
            json.dump(combined_data, f, indent=2, ensure_ascii=False)
        
        logger.info("\n==================== 音樂創作完成 ====================")
        logger.info(f"原始描述: {args.description}")
        logger.info(f"增強描述: {enhanced_description[:100]}...")
        logger.info(f"旋律MIDI: {melody_path}")
        logger.info(f"和弦MIDI: {chord_path}")
        logger.info(f"JSON結果: {json_path}")
        logger.info(f"標準音樂數據: {combined_path}")
        
        # 提示用戶如何播放
        logger.info("\n要播放生成的音樂，請運行:")
        logger.info(f"python json_to_midi_player.py {combined_path}")
        
    except Exception as e:
        logger.error(f"音樂創作過程中發生錯誤: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main() 