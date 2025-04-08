"""音樂工具命令行界面

提供命令行介面使用整合的音樂工具功能
"""

import os
import sys
import argparse
import logging
from typing import Dict, Any, List, Optional

from .music_tools_integrator import MusicToolsIntegrator
from .mcp_schema import MusicParameters, Note, MusicKey, TimeSignature

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ai_music_assistant.log')
    ]
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """解析命令行參數"""
    parser = argparse.ArgumentParser(description='音樂工具命令行介面')
    
    # 頂層子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # Magenta 相關命令
    magenta_parser = subparsers.add_parser('magenta', help='Magenta 深度學習模型功能')
    magenta_subparsers = magenta_parser.add_subparsers(dest='subcommand', help='Magenta 子命令')
    
    # 旋律生成
    melody_parser = magenta_subparsers.add_parser('generate-melody', help='生成旋律')
    melody_parser.add_argument('--output', '-o', required=True, help='輸出 MIDI 文件路徑')
    melody_parser.add_argument('--tempo', '-t', type=int, default=120, help='速度 (BPM)')
    melody_parser.add_argument('--key', '-k', default='C', help='調性 (C, Am 等)')
    melody_parser.add_argument('--steps', '-s', type=int, default=128, help='生成步數')
    melody_parser.add_argument('--temperature', '-T', type=float, default=1.0, help='生成溫度參數')
    melody_parser.add_argument('--primer', '-p', help='引導旋律 MIDI 文件路徑')
    
    # 旋律變奏
    variation_parser = magenta_subparsers.add_parser('generate-variation', help='生成旋律變奏')
    variation_parser.add_argument('--input', '-i', required=True, help='輸入 MIDI 文件路徑')
    variation_parser.add_argument('--output', '-o', required=True, help='輸出 MIDI 文件路徑')
    variation_parser.add_argument('--degree', '-d', type=float, default=0.5, help='變奏程度 (0.0-1.0)')
    
    # 演奏風格
    performance_parser = magenta_subparsers.add_parser('apply-performance', help='應用演奏風格')
    performance_parser.add_argument('--input', '-i', required=True, help='輸入 MIDI 文件路徑')
    performance_parser.add_argument('--output', '-o', required=True, help='輸出 MIDI 文件路徑')
    performance_parser.add_argument('--style', '-s', default='default', help='演奏風格 (default, expressive, virtuosic, gentle)')
    
    # 完整音樂生成
    idea_parser = magenta_subparsers.add_parser('generate-idea', help='生成完整音樂想法')
    idea_parser.add_argument('--output', '-o', required=True, help='輸出 MIDI 文件路徑')
    idea_parser.add_argument('--tempo', '-t', type=int, default=120, help='速度 (BPM)')
    idea_parser.add_argument('--key', '-k', default='C', help='調性 (C, Am 等)')
    
    # Music21 相關命令
    music21_parser = subparsers.add_parser('music21', help='Music21 樂理分析功能')
    music21_subparsers = music21_parser.add_subparsers(dest='subcommand', help='Music21 子命令')
    
    # 分析 MIDI 文件
    analyze_parser = music21_subparsers.add_parser('analyze', help='分析 MIDI 文件')
    analyze_parser.add_argument('--input', '-i', required=True, help='輸入 MIDI 文件路徑')
    analyze_parser.add_argument('--output', '-o', help='輸出分析結果 JSON 文件路徑')
    
    # 生成樂譜
    score_parser = music21_subparsers.add_parser('generate-score', help='生成樂譜')
    score_parser.add_argument('--input', '-i', required=True, help='輸入 MIDI 文件路徑')
    score_parser.add_argument('--output', '-o', required=True, help='輸出樂譜文件路徑 (.xml 或 .musicxml)')
    
    # Basic Pitch 相關命令
    basic_pitch_parser = subparsers.add_parser('basic-pitch', help='Basic Pitch 音頻處理功能')
    basic_pitch_subparsers = basic_pitch_parser.add_subparsers(dest='subcommand', help='Basic Pitch 子命令')
    
    # 音頻轉 MIDI
    audio_to_midi_parser = basic_pitch_subparsers.add_parser('audio-to-midi', help='將音頻轉換為 MIDI')
    audio_to_midi_parser.add_argument('--input', '-i', required=True, help='輸入音頻文件路徑')
    audio_to_midi_parser.add_argument('--output', '-o', required=True, help='輸出 MIDI 文件路徑')
    
    # 音頻轉樂譜
    audio_to_score_parser = basic_pitch_subparsers.add_parser('audio-to-score', help='將音頻轉換為樂譜')
    audio_to_score_parser.add_argument('--input', '-i', required=True, help='輸入音頻文件路徑')
    audio_to_score_parser.add_argument('--output', '-o', required=True, help='輸出樂譜文件路徑 (.xml 或 .musicxml)')
    
    # 音頻校正
    correct_pitch_parser = basic_pitch_subparsers.add_parser('correct-pitch', help='對音頻進行音準校正')
    correct_pitch_parser.add_argument('--input', '-i', required=True, help='輸入音頻文件路徑')
    correct_pitch_parser.add_argument('--output', '-o', required=True, help='輸出音頻文件路徑')
    
    # 組合功能
    combo_parser = subparsers.add_parser('combo', help='組合功能')
    combo_subparsers = combo_parser.add_subparsers(dest='subcommand', help='組合功能子命令')
    
    # 音頻轉表現力演奏
    expressive_parser = combo_subparsers.add_parser('audio-to-expressive', help='將音頻轉換為富有表現力的 MIDI')
    expressive_parser.add_argument('--input', '-i', required=True, help='輸入音頻文件路徑')
    expressive_parser.add_argument('--output', '-o', required=True, help='輸出 MIDI 文件路徑')
    expressive_parser.add_argument('--style', '-s', default='expressive', help='演奏風格')
    
    return parser.parse_args()


def str_to_music_key(key_str: str) -> MusicKey:
    """將字符串轉換為 MusicKey 枚舉

    Args:
        key_str: 調性字符串，如 "C", "Am"

    Returns:
        MusicKey: 對應的枚舉值
    """
    key_map = {
        # 大調
        "C": MusicKey.C_MAJOR,
        "G": MusicKey.G_MAJOR,
        "D": MusicKey.D_MAJOR,
        "A": MusicKey.A_MAJOR,
        "E": MusicKey.E_MAJOR,
        "B": MusicKey.B_MAJOR,
        "F": MusicKey.F_MAJOR,
        "Bb": MusicKey.B_FLAT_MAJOR,
        "Eb": MusicKey.E_FLAT_MAJOR,
        
        # 小調
        "Am": MusicKey.A_MINOR,
        "Em": MusicKey.E_MINOR,
        "Bm": MusicKey.B_MINOR,
        "F#m": MusicKey.F_SHARP_MINOR,
        "C#m": MusicKey.C_SHARP_MINOR,
        "Dm": MusicKey.D_MINOR,
        "Gm": MusicKey.G_MINOR,
        "Cm": MusicKey.C_MINOR,
        "Fm": MusicKey.F_MINOR,
    }
    
    if key_str in key_map:
        return key_map[key_str]
    else:
        # 默認為 C 大調
        logger.warning(f"未知的調性: {key_str}，使用 C 大調代替")
        return MusicKey.C_MAJOR


def main():
    """命令行主函數"""
    args = parse_arguments()
    
    # 如果沒有指定命令，顯示幫助
    if not args.command:
        print("請指定要使用的命令。使用 -h 查看幫助。")
        sys.exit(1)
    
    # 初始化音樂工具整合器
    integrator = MusicToolsIntegrator()
    
    try:
        # 處理 Magenta 相關命令
        if args.command == 'magenta':
            handle_magenta_command(args, integrator)
        
        # 處理 Music21 相關命令
        elif args.command == 'music21':
            handle_music21_command(args, integrator)
        
        # 處理 Basic Pitch 相關命令
        elif args.command == 'basic-pitch':
            handle_basic_pitch_command(args, integrator)
        
        # 處理組合功能
        elif args.command == 'combo':
            handle_combo_command(args, integrator)
        
    except Exception as e:
        logger.error(f"執行命令時發生錯誤: {str(e)}", exc_info=True)
        print(f"錯誤: {str(e)}")
        sys.exit(1)


def handle_magenta_command(args, integrator: MusicToolsIntegrator):
    """處理 Magenta 相關命令

    Args:
        args: 命令行參數
        integrator: 音樂工具整合器
    """
    if not args.subcommand:
        print("請指定 Magenta 子命令。使用 magenta -h 查看幫助。")
        return
    
    # 處理生成旋律命令
    if args.subcommand == 'generate-melody':
        # 創建音樂參數
        params = MusicParameters(
            tempo=args.tempo,
            key=str_to_music_key(args.key)
        )
        
        # 讀取引導旋律（如果有）
        primer_melody = None
        if args.primer:
            try:
                # 這裡需要實現讀取 MIDI 並轉換為 Note 列表的功能
                # 此處為示例，實際需要定義 read_midi_notes 函數
                primer_melody = read_midi_notes(args.primer)
            except Exception as e:
                logger.warning(f"無法讀取引導旋律 {args.primer}: {str(e)}")
        
        # 生成旋律
        melody = integrator.generate_melody(
            parameters=params,
            primer_melody=primer_melody,
            num_steps=args.steps,
            temperature=args.temperature
        )
        
        # 將旋律寫入 MIDI 文件
        midi_path = integrator.magenta_service.melody_to_midi(
            melody=melody,
            output_path=args.output,
            tempo=args.tempo
        )
        
        print(f"已生成旋律並保存到: {midi_path}")
    
    # 處理旋律變奏命令
    elif args.subcommand == 'generate-variation':
        # 讀取輸入 MIDI
        input_notes = read_midi_notes(args.input)
        
        # 生成變奏
        varied_notes = integrator.generate_variation(
            melody=input_notes,
            parameters=MusicParameters(),
            variation_degree=args.degree
        )
        
        # 將變奏寫入 MIDI 文件
        midi_path = integrator.magenta_service.melody_to_midi(
            melody=varied_notes,
            output_path=args.output,
            tempo=120  # 可以從輸入 MIDI 中獲取，此處簡化為 120
        )
        
        print(f"已生成變奏並保存到: {midi_path}")
    
    # 處理應用演奏風格命令
    elif args.subcommand == 'apply-performance':
        # 讀取輸入 MIDI
        input_notes = read_midi_notes(args.input)
        
        # 應用演奏風格
        performance_notes = integrator.apply_performance_style(
            melody=input_notes,
            style=args.style,
            temperature=1.0
        )
        
        # 將演奏寫入 MIDI 文件
        midi_path = integrator.performance_rnn_service.performance_to_midi(
            notes=performance_notes,
            output_path=args.output,
            tempo=120  # 可以從輸入 MIDI 中獲取，此處簡化為 120
        )
        
        print(f"已應用 {args.style} 演奏風格並保存到: {midi_path}")
    
    # 處理生成完整音樂想法命令
    elif args.subcommand == 'generate-idea':
        # 創建音樂參數
        params = MusicParameters(
            tempo=args.tempo,
            key=str_to_music_key(args.key)
        )
        
        # 生成完整音樂想法
        result = integrator.generate_musical_idea(
            parameters=params,
            output_midi_path=args.output
        )
        
        print(f"已生成完整音樂想法並保存到: {args.output}")
        print(f"包含 {len(result['melody'])} 個旋律音符，{len(result['drums'])} 個鼓點音符")


def handle_music21_command(args, integrator: MusicToolsIntegrator):
    """處理 Music21 相關命令

    Args:
        args: 命令行參數
        integrator: 音樂工具整合器
    """
    if not args.subcommand:
        print("請指定 Music21 子命令。使用 music21 -h 查看幫助。")
        return
    
    # 處理分析 MIDI 命令
    if args.subcommand == 'analyze':
        # 分析 MIDI 文件
        analysis = integrator.analyze_midi(args.input)
        
        # 輸出分析結果
        if args.output:
            import json
            
            # 轉換為字典格式
            analysis_dict = analysis.dict()
            
            # 寫入 JSON 文件
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(analysis_dict, f, ensure_ascii=False, indent=2)
            
            print(f"分析結果已保存到: {args.output}")
        else:
            # 直接打印到控制台
            print(f"調性: {analysis.key.name}")
            print(f"速度: {analysis.tempo} BPM")
            print(f"時間拍號: {analysis.time_signature.name}")
            print("和弦進行:")
            for i, (chord, duration) in enumerate(zip(analysis.chord_progression.chords, analysis.chord_progression.durations)):
                print(f"  {i+1}: {chord} ({duration:.2f} 拍)")
    
    # 處理生成樂譜命令
    elif args.subcommand == 'generate-score':
        # 讀取 MIDI 文件
        input_notes = read_midi_notes(args.input)
        
        # 生成樂譜
        score_path = integrator.generate_sheet_music(
            notes=input_notes,
            output_path=args.output
        )
        
        print(f"已生成樂譜並保存到: {score_path}")


def handle_basic_pitch_command(args, integrator: MusicToolsIntegrator):
    """處理 Basic Pitch 相關命令

    Args:
        args: 命令行參數
        integrator: 音樂工具整合器
    """
    if not args.subcommand:
        print("請指定 Basic Pitch 子命令。使用 basic-pitch -h 查看幫助。")
        return
    
    # 處理音頻轉 MIDI 命令
    if args.subcommand == 'audio-to-midi':
        midi_path = integrator.audio_to_midi(
            audio_file_path=args.input,
            output_path=args.output
        )
        
        print(f"已將音頻轉換為 MIDI 並保存到: {midi_path}")
    
    # 處理音頻轉樂譜命令
    elif args.subcommand == 'audio-to-score':
        score_path = integrator.audio_to_sheet_music(
            audio_file_path=args.input,
            output_path=args.output
        )
        
        print(f"已將音頻轉換為樂譜並保存到: {score_path}")
    
    # 處理音頻校正命令
    elif args.subcommand == 'correct-pitch':
        corrected_path = integrator.correct_pitch(
            audio_file_path=args.input,
            output_path=args.output
        )
        
        print(f"已對音頻進行音準校正並保存到: {corrected_path}")


def handle_combo_command(args, integrator: MusicToolsIntegrator):
    """處理組合功能命令

    Args:
        args: 命令行參數
        integrator: 音樂工具整合器
    """
    if not args.subcommand:
        print("請指定組合功能子命令。使用 combo -h 查看幫助。")
        return
    
    # 處理音頻轉表現力演奏命令
    if args.subcommand == 'audio-to-expressive':
        midi_path = integrator.audio_to_expressive_performance(
            audio_file_path=args.input,
            output_midi_path=args.output,
            style=args.style
        )
        
        print(f"已將音頻轉換為富有表現力的 MIDI 演奏並保存到: {midi_path}")


def read_midi_notes(midi_path: str) -> List[Note]:
    """從 MIDI 文件讀取音符列表

    Args:
        midi_path: MIDI 文件路徑

    Returns:
        List[Note]: 音符列表
    """
    # 檢查文件是否存在
    if not os.path.exists(midi_path):
        raise FileNotFoundError(f"找不到 MIDI 文件: {midi_path}")
    
    try:
        # 使用 music21 讀取 MIDI
        import music21
        midi_stream = music21.converter.parse(midi_path)
        
        # 提取音符
        notes = []
        for note_obj in midi_stream.flat.notes:
            if isinstance(note_obj, music21.note.Note):
                note = Note(
                    pitch=note_obj.pitch.midi,
                    start_time=note_obj.offset / 4.0,  # 轉換拍數到秒數，假設4拍/秒
                    duration=note_obj.quarterLength / 4.0,
                    velocity=80  # music21 可能沒有直接提供 velocity
                )
                notes.append(note)
            elif isinstance(note_obj, music21.chord.Chord):
                # 處理和弦，取最高音作為旋律音符
                highest_pitch = max([n.pitch.midi for n in note_obj.notes])
                note = Note(
                    pitch=highest_pitch,
                    start_time=note_obj.offset / 4.0,
                    duration=note_obj.quarterLength / 4.0,
                    velocity=80
                )
                notes.append(note)
        
        # 按開始時間排序
        notes.sort(key=lambda x: x.start_time)
        return notes
    
    except Exception as e:
        logger.error(f"讀取 MIDI 文件時出錯: {str(e)}", exc_info=True)
        raise


if __name__ == '__main__':
    main() 