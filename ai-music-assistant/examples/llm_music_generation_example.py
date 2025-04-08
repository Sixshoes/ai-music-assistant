#!/usr/bin/env python3
"""大語言模型音樂生成示例

展示如何使用大語言模型直接生成音樂內容，而不僅是生成參數
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
import tempfile
import base64
from midiutil import MIDIFile

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

try:
    from backend.music_generation import (
        LLMMusicGenerator, 
        LLMProviderType, 
        LLMGenerationConfig
    )
    from backend.mcp.mcp_schema import MusicParameters
except ImportError:
    try:
        from music_generation import (
            LLMMusicGenerator, 
            LLMProviderType, 
            LLMGenerationConfig
        )
        from mcp.mcp_schema import MusicParameters
    except ImportError:
        print("無法導入必要模組，請確保您在正確的目錄中運行此腳本")
        sys.exit(1)

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def notes_to_midi(notes, output_path, tempo=120):
    """將音符列表轉換為MIDI文件
    
    Args:
        notes: 音符列表
        output_path: 輸出路徑
        tempo: 速度 (BPM)
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
    
    logger.info(f"MIDI文件已保存至 {output_path}")

def save_chord_progression(chords, output_path, tempo=120):
    """將和弦進行保存為MIDI文件
    
    Args:
        chords: 和弦進行列表
        output_path: 輸出路徑
        tempo: 速度 (BPM)
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

def save_arrangement_plan(arrangement, output_path):
    """將編曲計劃保存為JSON文件
    
    Args:
        arrangement: 編曲計劃
        output_path: 輸出路徑
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(arrangement, f, indent=2, ensure_ascii=False)
    
    logger.info(f"編曲計劃已保存至 {output_path}")

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="大語言模型音樂生成示例")
    parser.add_argument("--description", "-d", type=str, default="一段輕快愉悅的旋律，適合春天的心情", 
                        help="音樂描述")
    parser.add_argument("--tempo", "-t", type=int, default=120, 
                        help="速度 (BPM)")
    parser.add_argument("--key", "-k", type=str, default="C", 
                        help="調性")
    parser.add_argument("--genre", "-g", type=str, default="pop", 
                        help="風格")
    parser.add_argument("--provider", "-p", type=str, default="ollama", 
                        choices=["ollama", "openai", "lmstudio", "huggingface"],
                        help="LLM提供商")
    parser.add_argument("--output-dir", "-o", type=str, default="output", 
                        help="輸出目錄")
    
    args = parser.parse_args()
    
    # 創建輸出目錄
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 獲取API密鑰和URL
    llm_api_key = None
    llm_api_url = None
    provider_type = None
    
    if args.provider == "openai":
        llm_api_key = os.environ.get("OPENAI_API_KEY")
        if not llm_api_key:
            logger.error("使用OpenAI需要設置OPENAI_API_KEY環境變量")
            sys.exit(1)
        llm_api_url = "https://api.openai.com/v1/chat/completions"
        provider_type = LLMProviderType.OPENAI
    elif args.provider == "huggingface":
        llm_api_key = os.environ.get("HF_API_KEY")
        if not llm_api_key:
            logger.error("使用Hugging Face需要設置HF_API_KEY環境變量")
            sys.exit(1)
        llm_api_url = os.environ.get("HF_API_URL")
        if not llm_api_url:
            logger.error("使用Hugging Face需要設置HF_API_URL環境變量")
            sys.exit(1)
        provider_type = LLMProviderType.HUGGINGFACE
    elif args.provider == "lmstudio":
        llm_api_url = "http://localhost:1234/v1/chat/completions"
        provider_type = LLMProviderType.LMSTUDIO
    else:  # ollama
        llm_api_url = "http://localhost:11434/api/generate"
        provider_type = LLMProviderType.OLLAMA
    
    # 創建LLM配置
    config = LLMGenerationConfig(
        temperature=0.7,
        max_tokens=2048,
        system_message="你是一位專業的音樂作曲家助手，能根據文字描述創作出優質的旋律和和聲。"
    )
    
    # 創建LLM音樂生成器
    generator = LLMMusicGenerator(
        llm_api_key=llm_api_key,
        llm_api_url=llm_api_url,
        provider_type=provider_type,
        config=config
    )
    
    # 設置音樂參數
    parameters = MusicParameters(
        tempo=args.tempo,
        key=args.key,
        genre=args.genre
    )
    
    try:
        logger.info(f"開始生成音樂，描述: {args.description}")
        
        # 生成旋律
        logger.info("生成旋律...")
        melody_data = generator.generate_melody_representation(args.description, parameters)
        melody = generator.generate_melody(args.description, parameters)
        
        # 保存旋律JSON
        melody_json_path = os.path.join(args.output_dir, "melody.json")
        with open(melody_json_path, 'w', encoding='utf-8') as f:
            json.dump(melody_data, f, indent=2, ensure_ascii=False)
        
        # 保存旋律MIDI
        melody_midi_path = os.path.join(args.output_dir, "melody.mid")
        notes_to_midi(melody, melody_midi_path, args.tempo)
        
        # 生成和弦進行
        logger.info("生成和弦進行...")
        chord_data = generator.generate_chord_progression(args.description, parameters, melody)
        
        # 保存和弦JSON
        chord_json_path = os.path.join(args.output_dir, "chords.json")
        with open(chord_json_path, 'w', encoding='utf-8') as f:
            json.dump(chord_data, f, indent=2, ensure_ascii=False)
        
        # 保存和弦MIDI
        chord_midi_path = os.path.join(args.output_dir, "chords.mid")
        save_chord_progression(chord_data, chord_midi_path, args.tempo)
        
        # 生成編曲計劃
        logger.info("生成編曲計劃...")
        arrangement = generator.generate_arrangement_plan(args.description, parameters)
        
        # 保存編曲計劃
        arrangement_path = os.path.join(args.output_dir, "arrangement_plan.json")
        save_arrangement_plan(arrangement, arrangement_path)
        
        logger.info("音樂生成完成!")
        logger.info(f"旋律MIDI: {melody_midi_path}")
        logger.info(f"和弦MIDI: {chord_midi_path}")
        logger.info(f"編曲計劃: {arrangement_path}")
        
    except Exception as e:
        logger.error(f"生成過程中發生錯誤: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 