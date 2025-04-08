"""Music21 樂理分析服務

使用 Music21 進行音樂理論分析，包括調性分析、和弦識別、結構分析等
"""

import os
import logging
import tempfile
from typing import Dict, Any, List, Optional, Tuple, Union

import music21
from music21 import converter, note, chord, key, meter, stream, midi
from music21.analysis import discrete

from ...mcp.mcp_schema import (
    MusicTheoryAnalysis,
    MusicKey,
    TimeSignature,
    ChordProgression,
    Note as MCPNote
)

logger = logging.getLogger(__name__)


class Music21Service:
    """Music21 樂理分析服務類別

    使用 Music21 開源庫進行音樂理論分析
    """

    def __init__(self):
        """初始化 Music21 服務"""
        logger.info("初始化 Music21 服務")

    def analyze_midi_file(self, midi_file_path: str) -> MusicTheoryAnalysis:
        """分析 MIDI 文件

        Args:
            midi_file_path: MIDI 文件路徑

        Returns:
            MusicTheoryAnalysis: 音樂理論分析結果
        """
        try:
            logger.info(f"開始分析 MIDI 文件：{midi_file_path}")

            # 載入 MIDI 文件
            midi_score = converter.parse(midi_file_path)

            # 分析調性
            detected_key = self._analyze_key(midi_score)

            # 分析時間拍號
            detected_time_signature = self._analyze_time_signature(midi_score)

            # 分析速度
            detected_tempo = self._analyze_tempo(midi_score)

            # 分析和弦進行
            chord_progression = self._analyze_chords(midi_score)

            # 分析結構
            structure = self._analyze_structure(midi_score)

            # 分析和聲問題
            harmony_issues = self._analyze_harmonic_issues(midi_score, detected_key)

            # 生成建議
            suggestions = self._generate_suggestions(midi_score, detected_key, harmony_issues)

            # 創建分析結果
            analysis = MusicTheoryAnalysis(
                key=detected_key,
                chord_progression=chord_progression,
                time_signature=detected_time_signature,
                tempo=detected_tempo,
                structure=structure,
                harmony_issues=harmony_issues,
                suggestions=suggestions
            )

            logger.info(f"成功分析 MIDI 文件，調性：{detected_key}，速度：{detected_tempo} BPM")
            return analysis

        except Exception as e:
            logger.error(f"分析 MIDI 文件時出錯：{str(e)}", exc_info=True)
            raise

    def analyze_melody(self, notes: List[MCPNote]) -> MusicTheoryAnalysis:
        """分析旋律

        Args:
            notes: 旋律音符列表

        Returns:
            MusicTheoryAnalysis: 音樂理論分析結果
        """
        try:
            logger.info("開始分析旋律")

            # 創建 Music21 流
            melody_stream = stream.Stream()

            # 將音符添加到流中
            for mcp_note in notes:
                n = note.Note()
                n.pitch.midi = mcp_note.pitch
                n.quarterLength = mcp_note.duration * 4  # 假設每拍是四分音符
                n.offset = mcp_note.start_time * 4  # 假設每拍是四分音符
                melody_stream.append(n)

            # 分析調性
            detected_key = self._analyze_key(melody_stream)

            # 假設 4/4 拍
            detected_time_signature = TimeSignature.FOUR_FOUR

            # 假設速度 120 BPM
            detected_tempo = 120

            # 生成和弦建議
            suggested_chords = self._suggest_chords_for_melody(melody_stream, detected_key)

            # 簡化的結構分析
            structure = {"a": [1], "b": [5]}  # 假設簡單的二段式結構

            # 創建分析結果
            analysis = MusicTheoryAnalysis(
                key=detected_key,
                chord_progression=suggested_chords,
                time_signature=detected_time_signature,
                tempo=detected_tempo,
                structure=structure,
                harmony_issues=[],
                suggestions=["考慮在第二部分使用對比性的節奏模式"]
            )

            logger.info(f"成功分析旋律，調性：{detected_key}")
            return analysis

        except Exception as e:
            logger.error(f"分析旋律時出錯：{str(e)}", exc_info=True)
            raise

    def _analyze_key(self, score: music21.stream.Stream) -> MusicKey:
        """分析調性

        Args:
            score: Music21 樂譜

        Returns:
            MusicKey: 檢測到的調性
        """
        try:
            # 使用 Music21 的 key.Analyzer
            key_analysis = score.analyze('key')
            key_str = str(key_analysis)

            # 將 Music21 的調性表示轉換為 MCP 調性枚舉
            if 'minor' in key_str.lower():
                # 小調
                root = key_str.split(' ')[0]
                if root == 'a':
                    return MusicKey.A_MINOR
                elif root == 'e':
                    return MusicKey.E_MINOR
                elif root == 'b':
                    return MusicKey.B_MINOR
                elif root == 'f#' or root == 'f-sharp':
                    return MusicKey.F_SHARP_MINOR
                elif root == 'c#' or root == 'c-sharp':
                    return MusicKey.C_SHARP_MINOR
                elif root == 'd':
                    return MusicKey.D_MINOR
                elif root == 'g':
                    return MusicKey.G_MINOR
                elif root == 'c':
                    return MusicKey.C_MINOR
                elif root == 'f':
                    return MusicKey.F_MINOR
                else:
                    # 默認返回 A 小調
                    return MusicKey.A_MINOR
            else:
                # 大調
                root = key_str.split(' ')[0]
                if root == 'C':
                    return MusicKey.C_MAJOR
                elif root == 'G':
                    return MusicKey.G_MAJOR
                elif root == 'D':
                    return MusicKey.D_MAJOR
                elif root == 'A':
                    return MusicKey.A_MAJOR
                elif root == 'E':
                    return MusicKey.E_MAJOR
                elif root == 'B':
                    return MusicKey.B_MAJOR
                elif root == 'F':
                    return MusicKey.F_MAJOR
                elif root == 'B-' or root == 'Bb':
                    return MusicKey.B_FLAT_MAJOR
                elif root == 'E-' or root == 'Eb':
                    return MusicKey.E_FLAT_MAJOR
                else:
                    # 默認返回 C 大調
                    return MusicKey.C_MAJOR

        except Exception:
            # 如果分析失敗，返回默認值
            logger.warning("調性分析失敗，使用默認調性 C 大調")
            return MusicKey.C_MAJOR

    def _analyze_time_signature(self, score: music21.stream.Stream) -> TimeSignature:
        """分析時間拍號

        Args:
            score: Music21 樂譜

        Returns:
            TimeSignature: 檢測到的時間拍號
        """
        try:
            # 嘗試從樂譜中獲取時間拍號
            time_sigs = score.getTimeSignatures()
            if time_sigs:
                time_sig_str = str(time_sigs[0])
                
                if time_sig_str == '4/4':
                    return TimeSignature.FOUR_FOUR
                elif time_sig_str == '3/4':
                    return TimeSignature.THREE_FOUR
                elif time_sig_str == '6/8':
                    return TimeSignature.SIX_EIGHT
                elif time_sig_str == '2/4':
                    return TimeSignature.TWO_FOUR
                elif time_sig_str == '5/4':
                    return TimeSignature.FIVE_FOUR
                elif time_sig_str == '7/8':
                    return TimeSignature.SEVEN_EIGHT
                elif time_sig_str == '12/8':
                    return TimeSignature.TWELVE_EIGHT
                else:
                    # 默認返回 4/4 拍
                    return TimeSignature.FOUR_FOUR
            else:
                # 如果沒有找到時間拍號，返回默認值
                return TimeSignature.FOUR_FOUR

        except Exception:
            # 如果分析失敗，返回默認值
            logger.warning("時間拍號分析失敗，使用默認拍號 4/4")
            return TimeSignature.FOUR_FOUR

    def _analyze_tempo(self, score: music21.stream.Stream) -> int:
        """分析速度

        Args:
            score: Music21 樂譜

        Returns:
            int: 檢測到的速度 (BPM)
        """
        try:
            # 嘗試從樂譜中獲取速度標記
            mm = score.flat.getElementsByClass(music21.tempo.MetronomeMark)
            if mm:
                return int(mm[0].number)
            else:
                # 如果沒有找到速度標記，返回默認值
                return 120

        except Exception:
            # 如果分析失敗，返回默認值
            logger.warning("速度分析失敗，使用默認速度 120 BPM")
            return 120

    def _analyze_chords(self, score: music21.stream.Stream) -> ChordProgression:
        """分析和弦進行

        Args:
            score: Music21 樂譜

        Returns:
            ChordProgression: 和弦進行
        """
        try:
            # 使用更強大的和弦識別算法
            logger.info("開始進行和弦識別和分析")
            
            # 將樂譜分割成小節
            measures = list(score.measures(0, None))
            
            # 準備和弦和持續時間列表
            chord_symbols = []
            durations = []
            
            # 設置和弦識別參數
            min_chord_duration = 0.5  # 最小和弦持續時間(秒)
            
            # 獲取調性
            key_analysis = score.analyze('key')
            
            # 按小節分析和弦
            for measure in measures:
                # 使用和弦識別器
                chord_analyzer = music21.analysis.discrete.BellmanBudge()
                chords = chord_analyzer.getSolution(measure)
                
                if chords:
                    for chord_tuple in chords:
                        offset, chord_obj = chord_tuple
                        
                        # 獲取和弦名稱
                        if isinstance(chord_obj, music21.chord.Chord):
                            chord_symbol = self._get_chord_symbol(chord_obj, key_analysis)
                            
                            # 計算和弦持續時間
                            if measure.duration.quarterLength > 0:
                                duration = (chord_obj.duration.quarterLength / measure.duration.quarterLength) * 4
                            else:
                                duration = min_chord_duration
                            
                            chord_symbols.append(chord_symbol)
                            durations.append(duration)
                else:
                    # 如果識別器無法識別和弦，使用簡單的方法
                    # 收集該小節中的所有音符
                    notes_in_measure = measure.flatten().notes.stream()
                    
                    if notes_in_measure:
                        # 創建一個包含小節所有音符的和弦
                        combined_chord = music21.chord.Chord([n.pitch for n in notes_in_measure if hasattr(n, 'pitch')])
                        chord_symbol = self._get_chord_symbol(combined_chord, key_analysis)
                        
                        # 默認持續時間為一小節
                        duration = 1.0
                        
                        chord_symbols.append(chord_symbol)
                        durations.append(duration)
            
            # 如果沒有成功識別和弦，嘗試全曲分析
            if not chord_symbols:
                # 從樂譜中提取和弦
                chords_in_score = score.flat.getElementsByClass(music21.chord.Chord)
                
                if chords_in_score:
                    for c in chords_in_score:
                        chord_symbol = self._get_chord_symbol(c, key_analysis)
                        duration = float(c.quarterLength) / 4.0
                        
                        chord_symbols.append(chord_symbol)
                        durations.append(duration)
            
            # 如果分析出的和弦太多，合併相同的連續和弦
            if len(chord_symbols) > 1:
                i = 0
                while i < len(chord_symbols) - 1:
                    if chord_symbols[i] == chord_symbols[i + 1]:
                        durations[i] += durations[i + 1]
                        chord_symbols.pop(i + 1)
                        durations.pop(i + 1)
                    else:
                        i += 1
            
            # 如果分析出的和弦太多，只保留一部分
            if len(chord_symbols) > 16:
                chord_symbols = chord_symbols[:16]
                durations = durations[:16]
                
            # 如果分析出的和弦為空，使用默認和弦進行
            if not chord_symbols:
                chord_symbols = ["C", "Am", "F", "G"]
                durations = [1.0, 1.0, 1.0, 1.0]
                
            logger.info(f"和弦識別完成，識別出 {len(chord_symbols)} 個和弦")
            return ChordProgression(chords=chord_symbols, durations=durations)
            
        except Exception as e:
            # 如果分析失敗，返回默認和弦進行
            logger.warning(f"和弦進行分析失敗：{str(e)}，使用默認和弦進行")
            return ChordProgression(
                chords=["C", "Am", "F", "G"],
                durations=[1.0, 1.0, 1.0, 1.0]
            )

    def _get_chord_symbol(self, chord_obj: music21.chord.Chord, key_analysis: music21.key.Key) -> str:
        """從和弦對象獲取和弦符號
        
        Args:
            chord_obj: Music21 和弦對象
            key_analysis: 樂曲調性
            
        Returns:
            str: 和弦符號
        """
        try:
            # 嘗試直接獲取和弦標籤
            chord_symbol = chord_obj.commonName
            if chord_symbol and chord_symbol != 'unknown':
                return chord_symbol
            
            # 如果直接獲取失敗，嘗試分析和弦結構
            chord_root = chord_obj.root()
            if not chord_root:
                return "N.C."  # 無和弦
            
            root_name = chord_root.name
            
            # 分析和弦類型
            chord_type = ""
            
            # 獲取和弦音符與根音的音程
            chord_intervals = []
            for p in chord_obj.pitches:
                # 計算與根音的音程
                interval = music21.interval.Interval(chord_root, p)
                chord_intervals.append(interval.semitones)
            
            # 根據音程確定和弦類型
            if 3 in chord_intervals and 7 in chord_intervals:
                chord_type = ""  # 大三和弦
            elif 3 in chord_intervals and 6 in chord_intervals:
                chord_type = "m"  # 小三和弦
            elif 3 in chord_intervals and 6 in chord_intervals and 10 in chord_intervals:
                chord_type = "m7"  # 小七和弦
            elif 3 in chord_intervals and 7 in chord_intervals and 10 in chord_intervals:
                chord_type = "7"  # 屬七和弦
            elif 3 in chord_intervals and 7 in chord_intervals and 11 in chord_intervals:
                chord_type = "maj7"  # 大七和弦
            elif 3 in chord_intervals and 6 in chord_intervals and 9 in chord_intervals:
                chord_type = "dim"  # 減三和弦
            elif 4 in chord_intervals and 8 in chord_intervals:
                chord_type = "aug"  # 增三和弦
            elif 4 in chord_intervals and 7 in chord_intervals:
                chord_type = "sus4"  # 掛四和弦
            elif 2 in chord_intervals and 7 in chord_intervals:
                chord_type = "sus2"  # 掛二和弦
            else:
                # 嘗試獲取音樂理論分析的和弦名稱
                try:
                    chord_obj.lyric = chord_obj.figure
                    chord_type = chord_obj.lyric
                    if chord_type == "":
                        chord_type = ""  # 默認為大三和弦
                except:
                    chord_type = ""
            
            # 組合和弦符號
            return f"{root_name}{chord_type}"
            
        except Exception as e:
            logger.warning(f"和弦符號提取失敗: {str(e)}")
            if chord_obj.root():
                return chord_obj.root().name
            return "C"  # 默認為C和弦

    def _analyze_structure(self, score: music21.stream.Stream) -> Dict[str, List[int]]:
        """分析音樂結構

        Args:
            score: Music21 樂譜

        Returns:
            Dict[str, List[int]]: 結構分析，如 {"verse": [1, 5], "chorus": [9, 13]}
        """
        try:
            # 音樂結構分析比較複雜，這裡使用簡化的實現
            # 在實際應用中，可能需要更復雜的算法
            
            # 獲取小節數
            measures = list(score.measures(0, None))
            measure_count = len(measures)
            
            # 簡單劃分：假設前1/3是引入，中間1/3是主體，最後1/3是結尾
            intro_end = max(1, measure_count // 3)
            verse_end = max(intro_end + 1, 2 * measure_count // 3)
            
            result = {
                "intro": [1, intro_end],
                "verse": [intro_end + 1, verse_end],
                "outro": [verse_end + 1, measure_count]
            }
            
            return result
            
        except Exception:
            # 如果分析失敗，返回簡單的默認結構
            logger.warning("音樂結構分析失敗，使用默認結構")
            return {
                "verse": [1, 4],
                "chorus": [5, 8],
                "verse": [9, 12],
                "chorus": [13, 16]
            }

    def _analyze_harmonic_issues(self, score: music21.stream.Stream, detected_key: MusicKey) -> List[str]:
        """分析和聲問題

        Args:
            score: Music21 樂譜
            detected_key: 檢測到的調性

        Returns:
            List[str]: 和聲問題清單
        """
        try:
            issues = []
            
            # 獲取所有和弦
            chords = score.flat.getElementsByClass(music21.chord.Chord)
            
            # 獲取調性對象
            key_obj = None
            if detected_key in [MusicKey.C_MAJOR, MusicKey.G_MAJOR, MusicKey.D_MAJOR, MusicKey.A_MAJOR,
                              MusicKey.E_MAJOR, MusicKey.B_MAJOR, MusicKey.F_MAJOR]:
                # 大調
                key_name = str(detected_key).split('.')[1].split('_')[0]
                key_obj = music21.key.Key(key_name)
            else:
                # 小調
                key_name = str(detected_key).split('.')[1].split('_')[0]
                if key_name.endswith('MINOR'):
                    key_name = key_name[:-5].lower()
                key_obj = music21.key.Key(key_name.lower())
            
            if chords and key_obj:
                for i in range(len(chords) - 1):
                    current_chord = chords[i]
                    next_chord = chords[i + 1]
                    
                    # 檢查平行五度
                    if self._has_parallel_fifths(current_chord, next_chord):
                        issues.append(f"在小節 {current_chord.measureNumber} 發現平行五度")
                    
                    # 檢查不自然的和弦進行
                    if not self._is_natural_progression(current_chord, next_chord, key_obj):
                        issues.append(f"在小節 {current_chord.measureNumber} 存在不自然的和弦進行")
            
            # 限制問題數量
            if len(issues) > 5:
                issues = issues[:5]
                
            return issues
            
        except Exception:
            # 如果分析失敗，返回空列表
            logger.warning("和聲問題分析失敗")
            return []

    def _has_parallel_fifths(self, chord1: music21.chord.Chord, chord2: music21.chord.Chord) -> bool:
        """檢查是否有平行五度

        Args:
            chord1: 第一個和弦
            chord2: 第二個和弦

        Returns:
            bool: 是否存在平行五度
        """
        # 簡化實現
        return False

    def _is_natural_progression(self, chord1: music21.chord.Chord, chord2: music21.chord.Chord, key_obj: music21.key.Key) -> bool:
        """檢查和弦進行是否自然

        Args:
            chord1: 第一個和弦
            chord2: 第二個和弦
            key_obj: 調性

        Returns:
            bool: 和弦進行是否自然
        """
        # 簡化實現
        return True

    def _generate_suggestions(self, score: music21.stream.Stream, detected_key: MusicKey, harmony_issues: List[str]) -> List[str]:
        """生成音樂改進建議

        Args:
            score: Music21 樂譜
            detected_key: 檢測到的調性
            harmony_issues: 和聲問題清單

        Returns:
            List[str]: 改進建議
        """
        suggestions = []
        
        # 根據和聲問題生成建議
        if harmony_issues:
            suggestions.append("考慮修正識別出的和聲問題，可能會使音樂更加和諧")
        
        # 分析音符密度
        note_count = len(score.flat.notes)
        duration = score.duration.quarterLength
        note_density = note_count / (duration / 4.0) if duration > 0 else 0
        
        if note_density > 8:
            suggestions.append("音符密度較高，考慮適當簡化以提高清晰度")
        elif note_density < 2:
            suggestions.append("音符密度較低，考慮增加音符豐富音樂織體")
        
        # 分析音域
        pitches = [n.pitch.midi for n in score.flat.notes if hasattr(n, 'pitch')]
        if pitches:
            pitch_range = max(pitches) - min(pitches)
            if pitch_range < 12:
                suggestions.append("音域較窄，考慮擴展音域以增加音樂的表現力")
            elif pitch_range > 36:
                suggestions.append("音域較寬，注意不同音域之間的平衡")
        
        # 添加通用建議
        suggestions.append("考慮在副歌部分使用更強的動態對比")
        suggestions.append("可嘗試使用更豐富的和弦延伸音增加和聲色彩")
        
        # 限制建議數量
        if len(suggestions) > 5:
            suggestions = suggestions[:5]
            
        return suggestions

    def _suggest_chords_for_melody(self, melody_stream: music21.stream.Stream, detected_key: MusicKey) -> ChordProgression:
        """為旋律生成和弦建議
        
        Args:
            melody_stream: 旋律流
            detected_key: 檢測到的調性
            
        Returns:
            ChordProgression: 建議的和弦進行
        """
        try:
            logger.info("開始為旋律生成和弦建議")
            
            # 將調性枚舉轉換為music21格式
            key_str = str(detected_key).split('.')[-1]
            if "_MAJOR" in key_str:
                root = key_str.replace("_MAJOR", "").replace("_", "-").lower()
                is_minor = False
            else:
                root = key_str.replace("_MINOR", "").replace("_", "-").lower()
                is_minor = True
            
            # 創建調性對象
            if is_minor:
                key_obj = music21.key.Key(root, 'minor')
            else:
                key_obj = music21.key.Key(root)
                
            # 獲取調內和弦
            diatonic_chords = self._get_diatonic_chords(key_obj)
            
            # 將旋律分段
            segment_duration = 1.0  # 每段時長(秒)
            melody_duration = melody_stream.duration.quarterLength
            
            segments = []
            current_segment = []
            current_duration = 0
            
            for n in melody_stream.flatten().notes:
                current_segment.append(n)
                current_duration += n.duration.quarterLength
                
                if current_duration >= segment_duration * 4:  # 轉換為四分音符時值
                    segments.append(current_segment)
                    current_segment = []
                    current_duration = 0
                    
            # 添加最後一個段落
            if current_segment:
                segments.append(current_segment)
                
            # 為每個段落選擇最適合的和弦
            chord_symbols = []
            durations = []
            
            for segment in segments:
                if not segment:
                    continue
                    
                # 收集該段所有音符
                pitches = [n.pitch for n in segment if hasattr(n, 'pitch')]
                
                if not pitches:
                    continue
                    
                # 為每個和弦計算匹配分數
                best_chord = None
                best_score = -1
                
                for chord in diatonic_chords:
                    score = self._calculate_chord_match_score(chord, pitches)
                    if score > best_score:
                        best_score = score
                        best_chord = chord
                
                if best_chord:
                    # 獲取和弦符號
                    chord_root = best_chord.root()
                    chord_type = ""
                    
                    if best_chord.quality == 'minor':
                        chord_type = "m"
                    elif best_chord.quality == 'diminished':
                        chord_type = "dim"
                    elif best_chord.quality == 'augmented':
                        chord_type = "aug"
                    elif best_chord.quality == 'dominant' and best_chord.isDominantSeventh():
                        chord_type = "7"
                    elif best_chord.isMajorTriad():
                        chord_type = ""
                    
                    chord_symbol = f"{chord_root.name}{chord_type}"
                    chord_symbols.append(chord_symbol)
                    durations.append(segment_duration)
            
            # 如果沒有生成和弦，使用調性主要和弦進行
            if not chord_symbols:
                if is_minor:
                    chord_symbols = ["Am", "Dm", "E", "Am"]
                else:
                    chord_symbols = ["C", "F", "G", "C"]
                    
                durations = [1.0, 1.0, 1.0, 1.0]
            
            logger.info(f"和弦建議完成，生成了 {len(chord_symbols)} 個和弦建議")
            return ChordProgression(chords=chord_symbols, durations=durations)
            
        except Exception as e:
            logger.warning(f"為旋律生成和弦建議時出錯: {str(e)}")
            # 返回默認和弦進行
            return ChordProgression(
                chords=["C", "Am", "F", "G"],
                durations=[1.0, 1.0, 1.0, 1.0]
            )
        
    def _get_diatonic_chords(self, key_obj: music21.key.Key) -> List[music21.chord.Chord]:
        """獲取調內和弦
        
        Args:
            key_obj: 調性對象
            
        Returns:
            List[music21.chord.Chord]: 調內和弦列表
        """
        try:
            # 獲取調內音階
            scale = key_obj.getPitches()
            
            # 生成三和弦
            triads = []
            for i in range(len(scale)):
                # 三和弦：1-3-5
                chord_pitches = [scale[i], scale[(i+2) % len(scale)], scale[(i+4) % len(scale)]]
                triad = music21.chord.Chord(chord_pitches)
                triads.append(triad)
            
            # 生成七和弦
            sevenths = []
            for i in range(len(scale)):
                # 七和弦：1-3-5-7
                chord_pitches = [scale[i], scale[(i+2) % len(scale)], scale[(i+4) % len(scale)], scale[(i+6) % len(scale)]]
                seventh = music21.chord.Chord(chord_pitches)
                sevenths.append(seventh)
                
            # 組合所有和弦
            return triads + sevenths
            
        except Exception as e:
            logger.warning(f"獲取調內和弦時出錯: {str(e)}")
            return []
        
    def _calculate_chord_match_score(self, chord: music21.chord.Chord, melody_pitches: List[music21.pitch.Pitch]) -> float:
        """計算和弦與旋律的匹配分數
        
        Args:
            chord: 候選和弦
            melody_pitches: 旋律中的音高
            
        Returns:
            float: 匹配分數
        """
        try:
            score = 0.0
            
            # 計算和弦包含旋律音符的比例
            chord_notes = [p.name for p in chord.pitches]
            for pitch in melody_pitches:
                if pitch.name in chord_notes:
                    # 和弦包含該音符
                    score += 1.0
                else:
                    # 不符合和弦，但檢查是否為允許的非和弦音
                    interval = music21.interval.Interval(chord.root(), pitch)
                    if interval.semitones in [2, 9]:  # 9度音、2度音
                        score += 0.5
                    elif interval.semitones in [11, 4]:  # 4度音、11度音
                        score += 0.4
                    elif interval.semitones in [6]:  # 13度音
                        score += 0.3
                    else:
                        score -= 0.5  # 處罰不和諧的音符
            
            # 正規化分數
            if melody_pitches:
                score = score / len(melody_pitches)
            
            # 優先選擇和弦的根音或五音作為強拍上的音符
            strong_beat_bonus = 0.0
            if melody_pitches and melody_pitches[0].name == chord.root().name:
                strong_beat_bonus = 0.5
            elif melody_pitches and melody_pitches[0].name == chord.fifth.name:
                strong_beat_bonus = 0.3
            
            return score + strong_beat_bonus
            
        except Exception as e:
            logger.warning(f"計算和弦匹配分數時出錯: {str(e)}")
            return 0.0

    def export_musicxml(self, notes: List[MCPNote], output_path: str) -> str:
        """將音符列表導出為 MusicXML 文件

        Args:
            notes: 音符列表
            output_path: 輸出文件路徑

        Returns:
            str: 輸出文件路徑
        """
        try:
            # 創建 Music21 流
            music_stream = stream.Stream()
            
            # 添加拍號
            music_stream.append(meter.TimeSignature('4/4'))
            
            # 將音符添加到流中
            for mcp_note in notes:
                n = note.Note()
                n.pitch.midi = mcp_note.pitch
                n.quarterLength = mcp_note.duration * 4  # 假設每拍是四分音符
                n.offset = mcp_note.start_time * 4  # 假設每拍是四分音符
                music_stream.append(n)
            
            # 分析並添加調性
            key_obj = music_stream.analyze('key')
            music_stream.insert(0, key_obj)
            
            # 分小節
            music_stream = music_stream.makeMeasures()
            
            # 導出 MusicXML
            music_stream.write('musicxml', output_path)
            
            return output_path
            
        except Exception as e:
            logger.error(f"導出 MusicXML 時出錯：{str(e)}", exc_info=True)
            raise 