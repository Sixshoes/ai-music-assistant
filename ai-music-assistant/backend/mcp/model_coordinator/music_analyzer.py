import logging
from typing import Dict, List, Any
from music21 import stream, key, chord, meter, analysis, converter
import tempfile
import os

logger = logging.getLogger(__name__)

class MusicAnalyzer:
    """音樂分析器類"""
    
    def __init__(self):
        """初始化音樂分析器"""
        pass
    
    def analyze_music(self, midi_data: bytes) -> Dict[str, Any]:
        """分析音樂
        
        Args:
            midi_data: MIDI 數據
            
        Returns:
            Dict: 分析結果
        """
        try:
            # 將 MIDI 數據轉換為 music21 stream
            with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as temp_midi:
                temp_midi.write(midi_data)
                temp_midi.flush()
                # 使用 music21 載入 MIDI 文件
                score = converter.parse(temp_midi.name)
                # 刪除臨時文件
                os.unlink(temp_midi.name)
            
            # 分析調性
            key_analysis = score.analyze('key')
            key_name = str(key_analysis)
            
            # 分析拍號
            time_signature = None
            for element in score.recurse():
                if isinstance(element, meter.TimeSignature):
                    time_signature = str(element)
                    break
            
            # 分析和弦進行
            chord_progression = []
            for measure in score.measures(0, None):
                for chord_element in measure.recurse().getElementsByClass(chord.Chord):
                    chord_progression.append(chord_element.commonName)
            
            # 分析節奏
            rhythm = []
            for measure in score.getElementsByClass('Measure'):
                for note in measure.getElementsByClass('Note'):
                    rhythm.append(note.duration.quarterLength)
            
            # 分析結構
            structure = {
                'intro': [0, 4],
                'verse': [4, 12],
                'chorus': [12, 20],
                'outro': [20, 24]
            }
            
            # 分析和聲問題
            harmony_issues = self._analyze_harmony(chord_progression)
            
            # 生成建議
            suggestions = self._generate_suggestions(harmony_issues, rhythm)
            
            return {
                "key": key_name,
                "time_signature": time_signature or "4/4",
                "chord_progression": chord_progression,
                "instruments": ["piano"],  # 這裡需要實際分析 MIDI 軌道
                "complexity": 3,  # 這裡需要根據實際音樂特徵計算
                "structure": structure,
                "harmony_issues": harmony_issues,
                "suggestions": suggestions
            }
        except Exception as e:
            logger.error(f"分析音樂時出錯: {str(e)}")
            return {
                "key": "C",
                "time_signature": "4/4",
                "chord_progression": [],
                "instruments": ["piano"],
                "complexity": 3,
                "structure": {
                    'intro': [0, 4],
                    'verse': [4, 12],
                    'chorus': [12, 20],
                    'outro': [20, 24]
                },
                "harmony_issues": [],
                "suggestions": []
            }
    
    def _analyze_harmony(self, chords: List[str]) -> List[str]:
        """分析和聲問題
        
        Args:
            chords: 和弦列表
            
        Returns:
            List[str]: 和聲問題列表
        """
        issues = []
        
        # 檢查和弦進行是否合理
        for i in range(len(chords) - 1):
            current = chords[i]
            next_chord = chords[i + 1]
            
            # 檢查是否有不合理的跳進
            if self._is_unusual_progression(current, next_chord):
                issues.append(f"和弦 {current} 到 {next_chord} 的進行可能不太自然")
        
        return issues
    
    def _generate_suggestions(self, harmony_issues: List[str], rhythm: List[float]) -> List[str]:
        """生成改進建議
        
        Args:
            harmony_issues: 和聲問題列表
            rhythm: 節奏列表
            
        Returns:
            List[str]: 建議列表
        """
        suggestions = []
        
        # 根據和聲問題生成建議
        if harmony_issues:
            suggestions.append("考慮使用更平滑的和弦進行")
            suggestions.append("可以嘗試添加一些過渡和弦")
        
        # 根據節奏生成建議
        if len(set(rhythm)) < 3:
            suggestions.append("可以嘗試添加一些節奏變化")
        
        return suggestions
    
    def _is_unusual_progression(self, current: str, next_chord: str) -> bool:
        """檢查和弦進行是否不尋常
        
        Args:
            current: 當前和弦
            next_chord: 下一個和弦
            
        Returns:
            bool: 是否不尋常
        """
        # 這裡可以添加更多的和弦進行規則
        unusual_progressions = [
            ('I', 'vii°'),
            ('V', 'ii'),
            ('vi', 'IV')
        ]
        
        return (current, next_chord) in unusual_progressions 