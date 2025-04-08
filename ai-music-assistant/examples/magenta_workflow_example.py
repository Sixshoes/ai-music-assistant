#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Magenta 工作流示例

展示如何整合 Magenta 模型管理器、音色引擎和和聲優化器來創建完整的音樂生成流程。
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional

# 確保可以導入項目模塊
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ai_music_assistant.backend.music_generation.magenta_model_manager import (
    MagentaModelManager, ModelType, ModelConfiguration
)
from ai_music_assistant.backend.music_generation.timbre_engine import (
    TimbreEngine, TimbreInstrument
)
from ai_music_assistant.backend.music_generation.harmony_optimizer import (
    HarmonyOptimizer, Scale, ChordType, Chord
)
from ai_music_assistant.mcp.mcp_schema import MusicParameters, Note

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_output_directories():
    """創建輸出目錄"""
    os.makedirs("output", exist_ok=True)
    os.makedirs("output/midi", exist_ok=True)
    os.makedirs("output/audio", exist_ok=True)
    os.makedirs("output/score", exist_ok=True)
    os.makedirs("models", exist_ok=True)


def setup_magenta_models(manager: MagentaModelManager):
    """設置 Magenta 模型
    
    Args:
        manager: Magenta 模型管理器
    """
    # 註冊常用的 Magenta 模型
    manager.register_model(
        "melody_rnn_basic",
        ModelConfiguration(
            model_type=ModelType.MELODY_RNN,
            checkpoint_path="models/melody_rnn/basic_rnn.mag",
            config_name="basic_rnn"
        )
    )
    
    manager.register_model(
        "melody_rnn_attention",
        ModelConfiguration(
            model_type=ModelType.MELODY_RNN,
            checkpoint_path="models/melody_rnn/attention_rnn.mag",
            config_name="attention_rnn"
        )
    )
    
    manager.register_model(
        "performance_rnn_base",
        ModelConfiguration(
            model_type=ModelType.PERFORMANCE_RNN,
            checkpoint_path="models/performance_rnn/performance.mag",
            config_name="performance"
        )
    )
    
    manager.register_model(
        "music_vae_mel16",
        ModelConfiguration(
            model_type=ModelType.MUSIC_VAE,
            checkpoint_path="models/music_vae/mel_16bar_small.mag",
            config_name="mel_16bar_small"
        )
    )
    
    manager.register_model(
        "improv_rnn_basic",
        ModelConfiguration(
            model_type=ModelType.IMPROV_RNN,
            checkpoint_path="models/improv_rnn/basic_improv.mag",
            config_name="basic_improv"
        )
    )
    
    logger.info("Magenta 模型註冊完成")


def setup_timbre_engine(engine: TimbreEngine):
    """設置音色引擎
    
    Args:
        engine: 音色引擎
    """
    # 註冊樂器
    violin = TimbreInstrument("violin", "models/violin.bin", "string")
    piano = TimbreInstrument("piano", "models/piano.bin", "percussion")
    flute = TimbreInstrument("flute", "models/flute.bin", "wind")
    guitar = TimbreInstrument("guitar", "models/guitar.bin", "string")
    bass = TimbreInstrument("bass", "models/bass.bin", "string")
    drums = TimbreInstrument("drums", "models/drums.bin", "percussion")
    
    engine.register_instrument(violin)
    engine.register_instrument(piano)
    engine.register_instrument(flute)
    engine.register_instrument(guitar)
    engine.register_instrument(bass)
    engine.register_instrument(drums)
    
    # 創建預設
    engine.create_preset("warm_violin", "violin", {
        "brightness": 0.7,
        "vibrato": 0.5
    })
    
    engine.create_preset("bright_piano", "piano", {
        "brightness": 0.8,
        "hardness": 0.6
    })
    
    engine.create_preset("soft_flute", "flute", {
        "breathiness": 0.6,
        "brightness": 0.4
    })
    
    engine.create_preset("acoustic_guitar", "guitar", {
        "brightness": 0.6,
        "attack": 0.3
    })
    
    engine.create_preset("deep_bass", "bass", {
        "brightness": 0.3,
        "resonance": 0.7
    })
    
    engine.create_preset("jazz_drums", "drums", {
        "tightness": 0.6,
        "room": 0.4
    })
    
    logger.info("音色引擎初始化完成")


def generate_complete_piece(
    model_manager: MagentaModelManager,
    timbre_engine: TimbreEngine,
    harmony_optimizer: HarmonyOptimizer,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """生成完整的音樂作品
    
    Args:
        model_manager: Magenta 模型管理器
        timbre_engine: 音色引擎
        harmony_optimizer: 和聲優化器
        parameters: 生成參數
        
    Returns:
        Dict[str, Any]: 生成結果，包含各軌道音符、MIDI 和音頻資訊
    """
    logger.info(f"開始生成完整作品，風格: {parameters.get('genre', 'general')}")
    
    # 1. 確定最佳模型組合
    task_requirements = {
        'task_type': 'melody_generation',
        'genre': parameters.get('genre', 'general'),
        'complexity': parameters.get('complexity', 'medium')
    }
    
    optimal_models = model_manager.find_optimal_combinations(task_requirements)
    best_model_id = optimal_models[0]['model_id'] if optimal_models else "melody_rnn_attention"
    
    logger.info(f"選擇模型: {best_model_id}")
    
    # 2. 創建音樂參數
    music_params = MusicParameters(
        tempo=parameters.get('tempo', 120),
        key=parameters.get('key', 'C'),
        genre=parameters.get('genre', 'general')
    )
    
    # 3. 設置調號
    key_name = parameters.get('key', 'C')
    key_root = 60  # C4
    if key_name == 'A':
        key_root = 57  # A3
    elif key_name == 'D':
        key_root = 62  # D4
    # ... 可擴展更多調號
    
    harmony_optimizer.set_key_signature(
        key_root, 
        Scale.MAJOR if parameters.get('mode', 'major') == 'major' else Scale.MINOR
    )
    
    # 4. 生成旋律（模擬）
    # 在實際應用中，這裡應該調用 Magenta 模型
    melody_notes = [
        Note(pitch=60, start_time=0.0, duration=1.0, velocity=80),
        Note(pitch=62, start_time=1.0, duration=1.0, velocity=75),
        Note(pitch=64, start_time=2.0, duration=1.0, velocity=70),
        Note(pitch=65, start_time=3.0, duration=1.0, velocity=75),
        Note(pitch=67, start_time=4.0, duration=2.0, velocity=80),
        Note(pitch=64, start_time=6.0, duration=1.0, velocity=70),
        Note(pitch=62, start_time=7.0, duration=1.0, velocity=75),
        Note(pitch=60, start_time=8.0, duration=2.0, velocity=80),
    ]
    
    # 5. 優化旋律
    optimized_melody = harmony_optimizer.optimize_melody(
        melody_notes, 
        strictness=parameters.get('key_strictness', 0.8)
    )
    
    # 6. 生成和弦進行
    chord_style = "pop" if parameters.get('genre', 'general') == 'pop' else "basic"
    if parameters.get('genre', 'general') == 'jazz':
        chord_style = "jazz"
    
    chords = harmony_optimizer.harmonize_melody(optimized_melody, chord_style)
    
    # 7. 優化和弦
    optimized_chords = harmony_optimizer.optimize_chords(
        chords, 
        complexity=parameters.get('chord_complexity', 0.5)
    )
    
    # 8. 生成伴奏音符
    accompaniment_style = parameters.get('accompaniment_style', 'basic')
    accompaniment_notes = harmony_optimizer.chords_to_notes(optimized_chords, accompaniment_style)
    
    # 9. 生成貝斯線
    bass_notes = []
    for chord in optimized_chords:
        # 簡單的貝斯線，使用和弦根音
        bass_note = Note(
            pitch=chord.root - 24,  # 低兩個八度
            start_time=chord.start_time,
            duration=chord.duration,
            velocity=85
        )
        bass_notes.append(bass_note)
    
    # 10. 應用音色
    # 在實際應用中，這裡應該調用音色引擎合成聲音
    melody_audio = timbre_engine.synthesize_notes(
        optimized_melody, 
        "soft_flute", 
        "output/audio/melody.wav"
    )
    
    accompaniment_audio = timbre_engine.synthesize_notes(
        accompaniment_notes, 
        "bright_piano", 
        "output/audio/accompaniment.wav"
    )
    
    bass_audio = timbre_engine.synthesize_notes(
        bass_notes, 
        "deep_bass", 
        "output/audio/bass.wav"
    )
    
    # 11. 返回結果
    result = {
        "melody": optimized_melody,
        "chords": optimized_chords,
        "accompaniment": accompaniment_notes,
        "bass": bass_notes,
        "audio_files": {
            "melody": "output/audio/melody.wav",
            "accompaniment": "output/audio/accompaniment.wav",
            "bass": "output/audio/bass.wav"
        },
        "parameters": parameters
    }
    
    logger.info("音樂生成完成")
    return result


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="Magenta 音樂生成工作流示例")
    parser.add_argument("--genre", type=str, default="pop", help="音樂風格")
    parser.add_argument("--tempo", type=int, default=120, help="曲速")
    parser.add_argument("--key", type=str, default="C", help="調號")
    parser.add_argument("--mode", type=str, default="major", help="調式 (major/minor)")
    parser.add_argument("--complexity", type=str, default="medium", help="複雜度 (low/medium/high)")
    args = parser.parse_args()
    
    # 創建輸出目錄
    create_output_directories()
    
    # 初始化所有組件
    model_manager = MagentaModelManager()
    timbre_engine = TimbreEngine()
    harmony_optimizer = HarmonyOptimizer()
    
    # 設置各組件
    setup_magenta_models(model_manager)
    setup_timbre_engine(timbre_engine)
    
    # 準備生成參數
    parameters = {
        "genre": args.genre,
        "tempo": args.tempo,
        "key": args.key,
        "mode": args.mode,
        "complexity": args.complexity,
        "key_strictness": 0.8,
        "chord_complexity": 0.6,
        "accompaniment_style": "arpeggio" if args.genre == "pop" else "basic"
    }
    
    # 生成音樂
    result = generate_complete_piece(
        model_manager,
        timbre_engine,
        harmony_optimizer,
        parameters
    )
    
    # 顯示結果摘要
    print("\n===== 生成結果摘要 =====")
    print(f"音樂風格: {parameters['genre']}")
    print(f"調號: {parameters['key']} {parameters['mode']}")
    print(f"曲速: {parameters['tempo']} BPM")
    print(f"旋律音符數量: {len(result['melody'])}")
    print(f"和弦數量: {len(result['chords'])}")
    print(f"伴奏音符數量: {len(result['accompaniment'])}")
    print(f"貝斯音符數量: {len(result['bass'])}")
    print(f"音頻文件位置:")
    for track_name, file_path in result['audio_files'].items():
        print(f"  - {track_name}: {file_path}")


if __name__ == "__main__":
    main() 