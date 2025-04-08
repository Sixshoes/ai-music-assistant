#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
音樂結構生成器

根據音樂需求生成具有完整性的歌曲結構，包括前奏、主歌、副歌、橋段和尾聲等
"""

import logging
import random
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SongSection:
    """歌曲段落"""
    name: str                # 段落名稱（如"verse"、"chorus"等）
    start_bar: int           # 開始小節
    length_bars: int         # 長度（小節數）
    chord_progression: List[List[int]] = None  # 和弦進行
    melody_variation: float = 1.0      # 旋律變化程度（相對於主題）
    dynamic_level: float = 0.7         # 力度水平 (0.0-1.0)
    instrumentation: List[str] = None  # 編配樂器
    
    def __post_init__(self):
        """初始化後處理"""
        if self.chord_progression is None:
            self.chord_progression = []
        if self.instrumentation is None:
            self.instrumentation = ["piano"]
    
    @property
    def end_bar(self) -> int:
        """結束小節"""
        return self.start_bar + self.length_bars - 1

class SongStructureGenerator:
    """歌曲結構生成器
    
    用於生成具有完整性的歌曲結構，包括前奏、主歌、副歌、橋段和尾聲等
    """
    
    def __init__(self):
        """初始化歌曲結構生成器"""
        # 各種歌曲結構模板
        self.structure_templates = {
            "simple": ["intro", "verse", "chorus", "verse", "chorus", "outro"],
            "verse_chorus": ["intro", "verse", "chorus", "verse", "chorus", "bridge", "chorus", "outro"],
            "aaba": ["intro", "A", "A", "B", "A", "outro"],
            "binary": ["intro", "A", "B", "outro"],
            "ternary": ["intro", "A", "B", "A", "outro"],
            "strophic": ["intro", "verse", "verse", "verse", "outro"],
            "through_composed": ["intro", "A", "B", "C", "D", "outro"],
            "extended": ["intro", "verse", "pre_chorus", "chorus", "verse", "pre_chorus", "chorus", "bridge", "chorus", "outro"]
        }
        
        # 段落標準長度（小節數）
        self.section_lengths = {
            "intro": (4, 8),      # 前奏：4-8小節
            "verse": (8, 16),     # 主歌：8-16小節
            "pre_chorus": (4, 8), # 導歌：4-8小節
            "chorus": (8, 16),    # 副歌：8-16小節
            "bridge": (4, 8),     # 橋段：4-8小節
            "outro": (4, 8),      # 尾聲：4-8小節
            "A": (8, 16),         # A段：8-16小節
            "B": (8, 16),         # B段：8-16小節
            "C": (8, 16),         # C段：8-16小節
            "D": (8, 16)          # D段：8-16小節
        }
        
        # 段落力度水平
        self.section_dynamics = {
            "intro": 0.5,      # 前奏：中等力度
            "verse": 0.6,      # 主歌：中高力度
            "pre_chorus": 0.7, # 導歌：較高力度
            "chorus": 0.9,     # 副歌：最高力度
            "bridge": 0.8,     # 橋段：高力度
            "outro": 0.5,      # 尾聲：中等力度
            "A": 0.6,          # A段：中高力度
            "B": 0.7,          # B段：較高力度
            "C": 0.8,          # C段：高力度
            "D": 0.7           # D段：較高力度
        }
        
        # 段落編配模板（簡化版）
        self.instrumentation_templates = {
            "basic": {
                "intro": ["piano", "strings"],
                "verse": ["piano", "bass", "drums"],
                "chorus": ["piano", "strings", "bass", "drums"],
                "bridge": ["piano", "strings", "bass"],
                "outro": ["piano", "strings"]
            },
            "band": {
                "intro": ["guitar", "bass"],
                "verse": ["guitar", "bass", "drums", "vocals"],
                "chorus": ["guitar", "bass", "drums", "vocals", "synth"],
                "bridge": ["guitar", "bass", "drums", "vocals", "synth"],
                "outro": ["guitar", "bass", "drums", "synth"]
            },
            "electronic": {
                "intro": ["synth", "drums"],
                "verse": ["synth", "bass", "drums"],
                "chorus": ["synth", "bass", "drums", "lead_synth"],
                "bridge": ["synth", "bass", "lead_synth"],
                "outro": ["synth", "drums"]
            },
            "orchestral": {
                "intro": ["strings", "woodwinds"],
                "verse": ["strings", "woodwinds", "brass"],
                "chorus": ["strings", "woodwinds", "brass", "percussion"],
                "bridge": ["strings", "woodwinds", "harp"],
                "outro": ["strings", "woodwinds"]
            }
        }
    
    def generate_song_structure(self, music_req: Dict[str, Any]) -> List[SongSection]:
        """生成歌曲結構
        
        Args:
            music_req: 音樂需求參數
            
        Returns:
            List[SongSection]: 歌曲段落列表
        """
        # 從需求中提取參數
        form = music_req.get("form", "verse_chorus")
        has_intro = music_req.get("has_intro", True)
        has_outro = music_req.get("has_outro", True)
        has_bridge = music_req.get("has_bridge", form == "verse_chorus")
        song_structure = music_req.get("song_structure", None)
        genre = music_req.get("genre", "classical")
        
        # 選擇合適的結構模板
        template_key = "verse_chorus"  # 默認模板
        
        if form in self.structure_templates:
            template_key = form
        elif form == "sonata":
            template_key = "extended"
        elif form == "rondo":
            template_key = "through_composed"
        
        # 如果用戶提供了自定義結構，則使用它
        if song_structure and isinstance(song_structure, list):
            structure = song_structure.copy()
        else:
            structure = self.structure_templates[template_key].copy()
        
        # 根據需求調整結構
        if not has_intro and "intro" in structure:
            structure.remove("intro")
        
        if not has_outro and "outro" in structure:
            structure.remove("outro")
        
        if not has_bridge:
            structure = [s for s in structure if s != "bridge"]
        
        # 選擇編配模板
        instrumentation_template = "basic"
        if "rock" in genre.lower() or "pop" in genre.lower():
            instrumentation_template = "band"
        elif "electronic" in genre.lower() or "edm" in genre.lower():
            instrumentation_template = "electronic"
        elif "classical" in genre.lower() or "orchestral" in genre.lower():
            instrumentation_template = "orchestral"
        
        # 生成具體的段落
        sections = []
        current_bar = 0
        
        for section_name in structure:
            # 確定段落長度
            min_length, max_length = self.section_lengths.get(section_name, (8, 16))
            length = random.randint(min_length, max_length)
            
            # 如果是重複段落（如第二個verse），稍微縮短或保持一致
            if sections and any(s.name == section_name for s in sections):
                prev_same_section = next(s for s in reversed(sections) if s.name == section_name)
                if random.random() < 0.7:  # 70%的機率保持長度一致
                    length = prev_same_section.length_bars
                else:
                    # 稍微變化，但不要差距太大
                    length = max(min_length, min(max_length, prev_same_section.length_bars + random.randint(-2, 2)))
            
            # 設置力度水平
            dynamic_level = self.section_dynamics.get(section_name, 0.7)
            
            # 設置旋律變化程度
            melody_variation = 1.0
            if sections:
                if section_name == "chorus" and any(s.name == "chorus" for s in sections):
                    # 副歌通常保持相似
                    melody_variation = 0.3
                elif section_name in ["verse", "A"] and any(s.name == section_name for s in sections):
                    # 主歌可能有較多變化
                    melody_variation = 0.7
            
            # 獲取編配
            instrumentation = self.instrumentation_templates.get(instrumentation_template, {}).get(section_name, ["piano"])
            
            # 創建段落
            section = SongSection(
                name=section_name,
                start_bar=current_bar,
                length_bars=length,
                melody_variation=melody_variation,
                dynamic_level=dynamic_level,
                instrumentation=instrumentation
            )
            
            sections.append(section)
            current_bar += length
        
        logger.info(f"生成歌曲結構：{[s.name for s in sections]}，總小節數：{current_bar}")
        return sections
    
    def design_harmony_for_structure(self, sections: List[SongSection], music_req: Dict[str, Any]) -> List[SongSection]:
        """為歌曲結構設計和聲
        
        Args:
            sections: 歌曲段落列表
            music_req: 音樂需求參數
            
        Returns:
            List[SongSection]: 更新後的段落列表
        """
        # 從需求中提取參數
        key = music_req.get("key", "C")
        harmonic_complexity = music_req.get("harmonic_complexity", "moderate")
        
        # 轉換複雜度為數值
        complexity_value = 0.5  # 默認中等複雜度
        if isinstance(harmonic_complexity, (int, float)):
            complexity_value = float(harmonic_complexity)
        else:
            if harmonic_complexity == "simple":
                complexity_value = 0.3
            elif harmonic_complexity == "complex":
                complexity_value = 0.8
        
        # 生成主題和弦進行（用於主歌/副歌）
        verse_progression = self._generate_chord_progression(key, complexity_value, 8)
        chorus_progression = self._generate_chord_progression(key, complexity_value, 8, more_stable=True)
        
        # 為每個段落分配和弦進行
        for section in sections:
            # 根據段落長度計算所需和弦進行次數
            repetitions = max(1, section.length_bars // 8)
            remaining_bars = section.length_bars % 8
            
            if section.name in ["chorus", "C"]:
                base_progression = chorus_progression
            elif section.name in ["bridge", "B"]:
                # 橋段使用更有變化的和弦進行
                base_progression = self._generate_chord_progression(key, complexity_value + 0.2, 8, dominant_focus=True)
            elif section.name in ["intro", "outro"]:
                # 前奏/尾奏可能更簡單
                base_progression = self._generate_chord_progression(key, max(0.2, complexity_value - 0.2), 4)
            else:
                base_progression = verse_progression
            
            # 根據段落長度複製和擴展和弦進行
            progression = []
            for _ in range(repetitions):
                progression.extend(base_progression)
            
            # 處理剩餘小節
            if remaining_bars > 0:
                progression.extend(base_progression[:remaining_bars])
            
            # 分配和弦進行
            section.chord_progression = progression
        
        return sections
    
    def _generate_chord_progression(self, key: str, complexity: float, length: int, 
                                  more_stable: bool = False, dominant_focus: bool = False) -> List[List[int]]:
        """生成和弦進行
        
        簡化版實現，實際應用中可能需要更複雜的和弦生成邏輯
        
        Args:
            key: 調性
            complexity: 複雜度
            length: 進行長度
            more_stable: 是否更穩定（適合副歌）
            dominant_focus: 是否強調屬和弦（適合橋段）
            
        Returns:
            List[List[int]]: 和弦進行（格式為MIDI音符列表）
        """
        # 簡化實現，實際應用需要完整的和弦生成邏輯
        # 這裡返回一個示例和弦進行
        # 實際開發中需要根據調性、複雜度等生成合適的和弦
        
        # 示例中使用的MIDI音符列表表示和弦
        # 以C調為例，可以建立一個基本的和弦映射
        base_midi = self._key_to_midi(key)
        
        chord_map = {
            "I": [base_midi, base_midi + 4, base_midi + 7],                  # I (C)
            "ii": [base_midi + 2, base_midi + 5, base_midi + 9],             # ii (Dm)
            "iii": [base_midi + 4, base_midi + 7, base_midi + 11],           # iii (Em)
            "IV": [base_midi + 5, base_midi + 9, base_midi + 12],            # IV (F)
            "V": [base_midi + 7, base_midi + 11, base_midi + 14],            # V (G)
            "vi": [base_midi + 9, base_midi + 12, base_midi + 16],           # vi (Am)
            "vii°": [base_midi + 11, base_midi + 14, base_midi + 17],        # vii° (Bdim)
            "I7": [base_midi, base_midi + 4, base_midi + 7, base_midi + 11], # Imaj7 (Cmaj7)
            "V7": [base_midi + 7, base_midi + 11, base_midi + 14, base_midi + 17]  # V7 (G7)
        }
        
        # 設置可能的和弦進行模式
        if more_stable:
            # 更穩定的進行（常用於副歌）
            patterns = [
                ["I", "IV", "V", "I"],
                ["I", "vi", "IV", "V"],
                ["I", "IV", "I", "V"]
            ]
        elif dominant_focus:
            # 強調屬和弦（常用於橋段）
            patterns = [
                ["vi", "V", "IV", "V7"],
                ["ii", "V7", "I", "IV"],
                ["IV", "V7", "iii", "vi"]
            ]
        else:
            # 一般進行
            patterns = [
                ["I", "vi", "IV", "V"],
                ["I", "IV", "vi", "V"],
                ["ii", "V", "I", "IV"],
                ["I", "V", "vi", "IV"]
            ]
        
        # 根據複雜度可能添加七和弦
        if complexity > 0.6:
            for i, pattern in enumerate(patterns):
                for j, chord in enumerate(pattern):
                    if chord == "V" and random.random() < complexity:
                        patterns[i][j] = "V7"
                    elif chord == "I" and random.random() < complexity - 0.2:
                        patterns[i][j] = "I7"
        
        # 選擇一個模式
        pattern = random.choice(patterns)
        
        # 重複模式直到達到所需長度
        extended_pattern = []
        while len(extended_pattern) < length:
            extended_pattern.extend(pattern)
        
        # 裁剪到所需長度
        pattern = extended_pattern[:length]
        
        # 轉換為MIDI音符列表
        progression = [chord_map[chord] for chord in pattern]
        
        return progression
    
    def _key_to_midi(self, key: str) -> int:
        """將調性轉換為MIDI基準音高
        
        Args:
            key: 調性名稱
            
        Returns:
            int: MIDI基準音高
        """
        # 基本音高映射
        base_notes = {
            "C": 60, "C#": 61, "Db": 61, "D": 62, "D#": 63, "Eb": 63,
            "E": 64, "F": 65, "F#": 66, "Gb": 66, "G": 67, "G#": 68,
            "Ab": 68, "A": 69, "A#": 70, "Bb": 70, "B": 71
        }
        
        # 提取調性名稱（不含大小調標識）
        key_parts = key.split()
        key_name = key_parts[0]
        
        # 根據大小調調整八度
        if len(key_parts) > 1 and "minor" in key_parts[1].lower():
            octave = 3  # 小調使用較低八度
        else:
            octave = 4  # 大調使用中央C所在八度
        
        # 獲取MIDI基準音高
        base_midi = base_notes.get(key_name, 60)  # 默認為C
        
        # 調整到正確的八度
        return base_midi + (octave - 4) * 12


# 測試代碼
if __name__ == "__main__":
    # 創建歌曲結構生成器
    generator = SongStructureGenerator()
    
    # 測試不同的音樂需求
    test_reqs = [
        {
            "form": "verse_chorus",
            "has_intro": True,
            "has_outro": True,
            "has_bridge": True,
            "genre": "pop",
            "key": "C",
            "harmonic_complexity": "moderate"
        },
        {
            "form": "binary",
            "has_intro": True,
            "has_outro": False,
            "has_bridge": False,
            "genre": "classical",
            "key": "G",
            "harmonic_complexity": "complex"
        },
        {
            "form": "verse_chorus",
            "has_intro": True,
            "has_outro": True,
            "has_bridge": True,
            "song_structure": ["intro", "verse", "chorus", "verse", "chorus", "bridge", "chorus", "outro"],
            "genre": "rock",
            "key": "E minor",
            "harmonic_complexity": "complex"
        }
    ]
    
    for i, req in enumerate(test_reqs):
        print(f"\n測試 {i+1}: {req['form']} ({req['genre']})")
        
        # 生成結構
        sections = generator.generate_song_structure(req)
        
        # 設計和聲
        sections = generator.design_harmony_for_structure(sections, req)
        
        # 輸出結果
        print(f"歌曲結構:")
        for section in sections:
            print(f"  {section.name}: 小節 {section.start_bar+1}-{section.end_bar+1} ({section.length_bars}小節)")
            print(f"    力度: {section.dynamic_level:.1f}, 旋律變化: {section.melody_variation:.1f}")
            print(f"    樂器: {', '.join(section.instrumentation)}")
            if section.chord_progression:
                print(f"    和弦數量: {len(section.chord_progression)}") 