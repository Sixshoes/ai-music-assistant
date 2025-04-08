"""樂器管理器模塊

處理樂器配置和演奏邏輯
"""

from typing import Dict, List, Tuple, Optional
from enum import Enum
from ...mcp_schema import InstrumentType, Genre
from ..theory.harmony import Scale

class PlayingTechnique(Enum):
    """演奏技巧"""
    # 基本技巧
    NORMAL = "normal"  # 普通演奏
    LEGATO = "legato"  # 連奏
    STACCATO = "staccato"  # 斷奏
    TENUTO = "tenuto"  # 保持音
    MARCATO = "marcato"  # 重音
    
    # 弦樂技巧
    PIZZICATO = "pizzicato"  # 撥奏
    ARCO = "arco"  # 拉奏
    TREMOLO = "tremolo"  # 顫音
    VIBRATO = "vibrato"  # 揉音
    GLISSANDO = "glissando"  # 滑音
    TRILL = "trill"  # 顫音
    HARMONICS = "harmonics"  # 泛音
    SUL_PONTICELLO = "sul_ponticello"  # 近琴馬演奏
    SUL_TASTO = "sul_tasto"  # 近指板演奏
    COL_LEGNO = "col_legno"  # 弓桿擊弦
    SPICCATO = "spiccato"  # 跳弓
    SAUTILLE = "sautille"  # 彈跳弓
    RICOCHET = "ricochet"  # 拋弓
    MARTELE = "martele"  # 頓弓
    PORTATO = "portato"  # 連頓弓
    
    # 管樂技巧
    FLUTTER_TONGUE = "flutter_tongue"  # 花舌
    DOUBLE_TONGUE = "double_tongue"  # 雙吐
    TRIPLE_TONGUE = "triple_tongue"  # 三吐
    CIRCULAR_BREATHING = "circular_breathing"  # 循環呼吸
    MULTIPHONICS = "multiphonics"  # 複音
    KEY_CLICKS = "key_clicks"  # 按鍵聲
    SLAP_TONGUE = "slap_tongue"  # 拍舌
    
    # 打擊樂技巧
    ROLL = "roll"  # 滾奏
    FLAM = "flam"  # 裝飾音
    DRAG = "drag"  # 拖曳
    PARADIDDLE = "paradiddle"  # 複合擊
    RIM_SHOT = "rim_shot"  # 邊擊
    GHOST_NOTE = "ghost_note"  # 弱音
    MUTED = "muted"  # 悶音
    
    # 鍵盤樂器技巧
    PEDAL = "pedal"  # 踏板
    NON_LEGATO = "non_legato"  # 非連奏
    PORTAMENTO = "portamento"  # 滑奏
    ARPEGGIO = "arpeggio"  # 琶音
    TREMOLANDO = "tremolando"  # 震音
    GLISSANDO_KEYS = "glissando_keys"  # 鍵盤滑奏
    
    # 國樂特殊技巧
    HUAYIN = "huayin"  # 滑音（國樂）
    FANYIN = "fanyin"  # 泛音（國樂）
    ZHENYIN = "zhenyin"  # 震音（國樂）
    TUOYIN = "tuoyin"  # 拖音（國樂）
    DANYIN = "danyin"  # 單音（國樂）
    SHUANGYIN = "shuangyin"  # 雙音（國樂）
    SANYIN = "sanyin"  # 散音（國樂）
    LUANYIN = "luanyin"  # 亂音（國樂）
    FANYIN = "fanyin"  # 泛音（國樂）
    ZHENYIN = "zhenyin"  # 震音（國樂）
    TUOYIN = "tuoyin"  # 拖音（國樂）
    DANYIN = "danyin"  # 單音（國樂）
    SHUANGYIN = "shuangyin"  # 雙音（國樂）
    SANYIN = "sanyin"  # 散音（國樂）
    LUANYIN = "luanyin"  # 亂音（國樂）
    
    # 特殊效果
    SUL_PONTICELLO = "sul_ponticello"  # 近琴馬演奏
    SUL_TASTO = "sul_tasto"  # 近指板演奏
    COL_LEGNO = "col_legno"  # 弓桿擊弦
    SPICCATO = "spiccato"  # 跳弓
    SAUTILLE = "sautille"  # 彈跳弓
    RICOCHET = "ricochet"  # 拋弓
    MARTELE = "martele"  # 頓弓
    PORTATO = "portato"  # 連頓弓
    
    # 現代技巧
    PREPARED = "prepared"  # 預置
    EXTENDED = "extended"  # 擴展技巧
    MICROTONAL = "microtonal"  # 微分音
    NOISE = "noise"  # 噪音
    IMPROVISATION = "improvisation"  # 即興
    EXTENDED_TECHNIQUE = "extended_technique"  # 擴展技巧
    
    # 電子音樂技巧
    GRANULAR = "granular"  # 顆粒合成
    WAVETABLE = "wavetable"  # 波表合成
    FM = "fm"  # 頻率調製
    AM = "am"  # 振幅調製
    RING_MOD = "ring_mod"  # 環形調製
    FILTER = "filter"  # 濾波
    DELAY = "delay"  # 延遲
    REVERB = "reverb"  # 混響
    DISTORTION = "distortion"  # 失真
    BIT_CRUSH = "bit_crush"  # 位元壓縮
    GLITCH = "glitch"  # 故障效果
    GRANULAR = "granular"  # 顆粒合成
    WAVETABLE = "wavetable"  # 波表合成
    FM = "fm"  # 頻率調製
    AM = "am"  # 振幅調製
    RING_MOD = "ring_mod"  # 環形調製
    FILTER = "filter"  # 濾波
    DELAY = "delay"  # 延遲
    REVERB = "reverb"  # 混響
    DISTORTION = "distortion"  # 失真
    BIT_CRUSH = "bit_crush"  # 位元壓縮
    GLITCH = "glitch"  # 故障效果
    
class InstrumentRole(Enum):
    """樂器角色"""
    MELODY = "melody"  # 旋律
    HARMONY = "harmony"  # 和聲
    RHYTHM = "rhythm"  # 節奏
    BASS = "bass"  # 低音
    PAD = "pad"  # 襯底音色
    
class InstrumentConfig:
    """樂器配置類"""
    
    def __init__(
        self,
        instrument_type: InstrumentType,
        midi_program: int,
        range_low: int,
        range_high: int,
        default_velocity: int = 100,
        supported_techniques: List[PlayingTechnique] = None,
        preferred_roles: List[InstrumentRole] = None
    ):
        """初始化樂器配置
        
        Args:
            instrument_type: 樂器類型
            midi_program: MIDI程序號
            range_low: 最低MIDI音高
            range_high: 最高MIDI音高
            default_velocity: 預設力度
            supported_techniques: 支持的演奏技巧
            preferred_roles: 偏好的樂器角色
        """
        self.instrument_type = instrument_type
        self.midi_program = midi_program
        self.range_low = range_low
        self.range_high = range_high
        self.default_velocity = default_velocity
        self.supported_techniques = supported_techniques or [PlayingTechnique.NORMAL]
        self.preferred_roles = preferred_roles or [InstrumentRole.MELODY]
        
    def supports_technique(self, technique: PlayingTechnique) -> bool:
        """檢查是否支持指定的演奏技巧"""
        return technique in self.supported_techniques
    
    def is_note_in_range(self, note: int) -> bool:
        """檢查音符是否在音域範圍內"""
        return self.range_low <= note <= self.range_high
    
    def get_safe_note(self, note: int) -> int:
        """獲取安全的音符（在音域範圍內）"""
        while note < self.range_low:
            note += 12
        while note > self.range_high:
            note -= 12
        return note

class InstrumentManager:
    """樂器管理器類"""
    
    # 樂器配置字典
    INSTRUMENTS = {
        # 西樂配置
        InstrumentType.PIANO: InstrumentConfig(
            InstrumentType.PIANO,
            midi_program=0,
            range_low=21,  # A0
            range_high=108,  # C8
            supported_techniques=[
                PlayingTechnique.NORMAL,
                PlayingTechnique.LEGATO,
                PlayingTechnique.STACCATO,
                PlayingTechnique.TENUTO,
                PlayingTechnique.MARCATO,
                PlayingTechnique.PEDAL,
                PlayingTechnique.NON_LEGATO,
                PlayingTechnique.PORTAMENTO,
                PlayingTechnique.ARPEGGIO,
                PlayingTechnique.TREMOLANDO,
                PlayingTechnique.GLISSANDO_KEYS
            ],
            preferred_roles=[
                InstrumentRole.MELODY,
                InstrumentRole.HARMONY
            ]
        ),
        InstrumentType.GUITAR: InstrumentConfig(
            InstrumentType.GUITAR,
            midi_program=24,
            range_low=40,  # E2
            range_high=84,  # C6
            supported_techniques=[
                PlayingTechnique.NORMAL,
                PlayingTechnique.PIZZICATO,
                PlayingTechnique.TREMOLO
            ],
            preferred_roles=[
                InstrumentRole.MELODY,
                InstrumentRole.HARMONY
            ]
        ),
        InstrumentType.BASS: InstrumentConfig(
            InstrumentType.BASS,
            midi_program=32,
            range_low=28,  # E1
            range_high=60,  # C4
            supported_techniques=[
                PlayingTechnique.NORMAL,
                PlayingTechnique.PIZZICATO
            ],
            preferred_roles=[
                InstrumentRole.BASS
            ]
        ),
        InstrumentType.VIOLIN: InstrumentConfig(
            InstrumentType.VIOLIN,
            midi_program=40,
            range_low=55,  # G3
            range_high=103,  # G7
            supported_techniques=[
                PlayingTechnique.NORMAL,
                PlayingTechnique.LEGATO,
                PlayingTechnique.STACCATO,
                PlayingTechnique.PIZZICATO,
                PlayingTechnique.ARCO,
                PlayingTechnique.TREMOLO,
                PlayingTechnique.VIBRATO,
                PlayingTechnique.GLISSANDO,
                PlayingTechnique.TRILL,
                PlayingTechnique.HARMONICS,
                PlayingTechnique.SUL_PONTICELLO,
                PlayingTechnique.SUL_TASTO,
                PlayingTechnique.COL_LEGNO,
                PlayingTechnique.SPICCATO,
                PlayingTechnique.SAUTILLE,
                PlayingTechnique.RICOCHET,
                PlayingTechnique.MARTELE,
                PlayingTechnique.PORTATO
            ],
            preferred_roles=[
                InstrumentRole.MELODY,
                InstrumentRole.HARMONY
            ]
        ),
        InstrumentType.TRUMPET: InstrumentConfig(
            InstrumentType.TRUMPET,
            midi_program=56,
            range_low=55,  # G3
            range_high=82,  # Bb5
            supported_techniques=[
                PlayingTechnique.NORMAL,
                PlayingTechnique.LEGATO,
                PlayingTechnique.STACCATO,
                PlayingTechnique.FLUTTER_TONGUE,
                PlayingTechnique.DOUBLE_TONGUE,
                PlayingTechnique.TRIPLE_TONGUE,
                PlayingTechnique.MULTIPHONICS
            ],
            preferred_roles=[
                InstrumentRole.MELODY
            ]
        ),
        InstrumentType.SAXOPHONE: InstrumentConfig(
            InstrumentType.SAXOPHONE,
            midi_program=65,
            range_low=49,  # Db3
            range_high=80,  # Ab5
            supported_techniques=[
                PlayingTechnique.NORMAL,
                PlayingTechnique.LEGATO,
                PlayingTechnique.VIBRATO
            ],
            preferred_roles=[
                InstrumentRole.MELODY
            ]
        ),
        InstrumentType.DRUMS: InstrumentConfig(
            InstrumentType.DRUMS,
            midi_program=0,  # 在通道10上
            range_low=35,  # Acoustic Bass Drum
            range_high=81,  # Open Triangle
            supported_techniques=[
                PlayingTechnique.NORMAL,
                PlayingTechnique.ROLL,
                PlayingTechnique.FLAM,
                PlayingTechnique.DRAG,
                PlayingTechnique.PARADIDDLE,
                PlayingTechnique.RIM_SHOT,
                PlayingTechnique.GHOST_NOTE,
                PlayingTechnique.MUTED
            ],
            preferred_roles=[
                InstrumentRole.RHYTHM
            ]
        ),
        InstrumentType.SYNTH: InstrumentConfig(
            InstrumentType.SYNTH,
            midi_program=80,
            range_low=0,
            range_high=127,
            supported_techniques=[
                PlayingTechnique.NORMAL,
                PlayingTechnique.LEGATO
            ],
            preferred_roles=[
                InstrumentRole.PAD,
                InstrumentRole.MELODY
            ]
        ),
        InstrumentType.ERHU: InstrumentConfig(
            InstrumentType.ERHU,
            midi_program=110,  # 使用特殊音色
            range_low=55,  # G3
            range_high=103,  # G7
            supported_techniques=[
                PlayingTechnique.NORMAL,
                PlayingTechnique.LEGATO,
                PlayingTechnique.VIBRATO,
                PlayingTechnique.GLISSANDO,
                PlayingTechnique.HUAYIN,
                PlayingTechnique.FANYIN,
                PlayingTechnique.ZHENYIN,
                PlayingTechnique.TUOYIN,
                PlayingTechnique.DANYIN,
                PlayingTechnique.SHUANGYIN,
                PlayingTechnique.SANYIN,
                PlayingTechnique.LUANYIN
            ],
            preferred_roles=[
                InstrumentRole.MELODY
            ]
        ),
        InstrumentType.PIPA: InstrumentConfig(
            InstrumentType.PIPA,
            midi_program=105,  # 使用特殊音色
            range_low=48,  # C3
            range_high=96,  # C7
            supported_techniques=[
                PlayingTechnique.NORMAL,
                PlayingTechnique.PIZZICATO,
                PlayingTechnique.TREMOLO,
                PlayingTechnique.GLISSANDO,
                PlayingTechnique.HUAYIN,
                PlayingTechnique.FANYIN,
                PlayingTechnique.ZHENYIN,
                PlayingTechnique.TUOYIN,
                PlayingTechnique.DANYIN,
                PlayingTechnique.SHUANGYIN,
                PlayingTechnique.SANYIN,
                PlayingTechnique.LUANYIN
            ],
            preferred_roles=[
                InstrumentRole.MELODY,
                InstrumentRole.HARMONY
            ]
        ),
        InstrumentType.GUZHENG: InstrumentConfig(
            InstrumentType.GUZHENG,
            midi_program=107,  # 使用特殊音色
            range_low=36,  # C2
            range_high=84,  # C6
            supported_techniques=[
                PlayingTechnique.NORMAL,
                PlayingTechnique.PIZZICATO,
                PlayingTechnique.TREMOLO,
                PlayingTechnique.GLISSANDO,
                PlayingTechnique.HUAYIN,
                PlayingTechnique.FANYIN,
                PlayingTechnique.ZHENYIN,
                PlayingTechnique.TUOYIN,
                PlayingTechnique.DANYIN,
                PlayingTechnique.SHUANGYIN,
                PlayingTechnique.SANYIN,
                PlayingTechnique.LUANYIN
            ],
            preferred_roles=[
                InstrumentRole.MELODY,
                InstrumentRole.HARMONY
            ]
        ),
        InstrumentType.DIZI: InstrumentConfig(
            InstrumentType.DIZI,
            midi_program=75,  # 使用特殊音色
            range_low=60,  # C4
            range_high=96,  # C7
            supported_techniques=[
                PlayingTechnique.NORMAL,
                PlayingTechnique.LEGATO,
                PlayingTechnique.TREMOLO,
                PlayingTechnique.GLISSANDO,
                PlayingTechnique.FLUTTER_TONGUE,
                PlayingTechnique.DOUBLE_TONGUE,
                PlayingTechnique.TRIPLE_TONGUE,
                PlayingTechnique.CIRCULAR_BREATHING,
                PlayingTechnique.HUAYIN,
                PlayingTechnique.FANYIN,
                PlayingTechnique.ZHENYIN,
                PlayingTechnique.TUOYIN
            ],
            preferred_roles=[
                InstrumentRole.MELODY
            ]
        ),
        InstrumentType.SUONA: InstrumentConfig(
            InstrumentType.SUONA,
            midi_program=111,  # 使用特殊音色
            range_low=55,  # G3
            range_high=88,  # E6
            supported_techniques=[
                PlayingTechnique.NORMAL,
                PlayingTechnique.LEGATO,
                PlayingTechnique.STACCATO,
                PlayingTechnique.FLUTTER_TONGUE,
                PlayingTechnique.DOUBLE_TONGUE,
                PlayingTechnique.TRIPLE_TONGUE,
                PlayingTechnique.CIRCULAR_BREATHING,
                PlayingTechnique.HUAYIN,
                PlayingTechnique.FANYIN,
                PlayingTechnique.ZHENYIN,
                PlayingTechnique.TUOYIN
            ],
            preferred_roles=[
                InstrumentRole.MELODY
            ]
        ),
        InstrumentType.CHINESE_PERCUSSION: InstrumentConfig(
            InstrumentType.CHINESE_PERCUSSION,
            midi_program=112,  # 使用特殊音色
            range_low=35,  # 低音鼓
            range_high=81,  # 高音鑼
            supported_techniques=[
                PlayingTechnique.NORMAL,
                PlayingTechnique.ROLL,
                PlayingTechnique.FLAM,
                PlayingTechnique.DRAG,
                PlayingTechnique.RIM_SHOT,
                PlayingTechnique.GHOST_NOTE,
                PlayingTechnique.MUTED
            ],
            preferred_roles=[
                InstrumentRole.RHYTHM
            ]
        )
    }
    
    # 風格樂器配置
    STYLE_INSTRUMENTS = {
        Genre.POP: {
            InstrumentRole.MELODY: [InstrumentType.PIANO, InstrumentType.GUITAR],
            InstrumentRole.HARMONY: [InstrumentType.GUITAR, InstrumentType.SYNTH],
            InstrumentRole.RHYTHM: [InstrumentType.DRUMS],
            InstrumentRole.BASS: [InstrumentType.BASS],
            InstrumentRole.PAD: [InstrumentType.SYNTH]
        },
        Genre.ROCK: {
            InstrumentRole.MELODY: [InstrumentType.GUITAR],
            InstrumentRole.HARMONY: [InstrumentType.GUITAR],
            InstrumentRole.RHYTHM: [InstrumentType.DRUMS],
            InstrumentRole.BASS: [InstrumentType.BASS],
            InstrumentRole.PAD: [InstrumentType.SYNTH]
        },
        Genre.JAZZ: {
            InstrumentRole.MELODY: [InstrumentType.PIANO, InstrumentType.SAXOPHONE],
            InstrumentRole.HARMONY: [InstrumentType.PIANO, InstrumentType.GUITAR],
            InstrumentRole.RHYTHM: [InstrumentType.DRUMS],
            InstrumentRole.BASS: [InstrumentType.BASS],
            InstrumentRole.PAD: []
        },
        Genre.CLASSICAL: {
            InstrumentRole.MELODY: [InstrumentType.VIOLIN, InstrumentType.PIANO],
            InstrumentRole.HARMONY: [InstrumentType.VIOLIN, InstrumentType.PIANO],
            InstrumentRole.RHYTHM: [],
            InstrumentRole.BASS: [InstrumentType.BASS],
            InstrumentRole.PAD: [InstrumentType.STRINGS]
        },
        "CHINESE_TRADITIONAL": {
            InstrumentRole.MELODY: [InstrumentType.ERHU, InstrumentType.PIPA, InstrumentType.DIZI],
            InstrumentRole.HARMONY: [InstrumentType.GUZHENG, InstrumentType.YANGQIN],
            InstrumentRole.RHYTHM: [InstrumentType.CHINESE_PERCUSSION],
            InstrumentRole.BASS: [InstrumentType.ZHONGHU],
            InstrumentRole.PAD: [InstrumentType.CHINESE_STRINGS]
        },
        "CHINESE_MODERN": {
            InstrumentRole.MELODY: [InstrumentType.ERHU, InstrumentType.PIPA, InstrumentType.GUZHENG],
            InstrumentRole.HARMONY: [InstrumentType.YANGQIN, InstrumentType.SYNTH],
            InstrumentRole.RHYTHM: [InstrumentType.DRUMS, InstrumentType.CHINESE_PERCUSSION],
            InstrumentRole.BASS: [InstrumentType.BASS],
            InstrumentRole.PAD: [InstrumentType.CHINESE_STRINGS]
        }
    }
    
    def __init__(self):
        """初始化樂器管理器"""
        pass
        
    def get_instrument_config(self, instrument_type: InstrumentType) -> InstrumentConfig:
        """獲取樂器配置
        
        Args:
            instrument_type: 樂器類型
            
        Returns:
            樂器配置對象
        """
        return self.INSTRUMENTS.get(instrument_type)
    
    def get_style_instruments(
        self,
        genre: Genre,
        complexity: float
    ) -> Dict[InstrumentRole, List[InstrumentType]]:
        """根據風格和複雜度獲取樂器配置
        
        Args:
            genre: 音樂風格
            complexity: 複雜度（0-1）
            
        Returns:
            按角色分類的樂器列表
        """
        style_config = self.STYLE_INSTRUMENTS.get(genre, self.STYLE_INSTRUMENTS[Genre.POP])
        result = {}
        
        # 根據複雜度選擇樂器
        for role, instruments in style_config.items():
            if role == InstrumentRole.PAD and complexity < 0.5:
                # 複雜度低時不使用襯底音色
                result[role] = []
            elif role == InstrumentRole.HARMONY and complexity < 0.3:
                # 複雜度很低時減少和聲樂器
                result[role] = instruments[:1]
            else:
                result[role] = instruments
                
        return result
    
    def adjust_note_for_instrument(
        self,
        note: int,
        instrument_type: InstrumentType,
        preferred_octave: Optional[int] = None
    ) -> int:
        """調整音符以適應樂器音域
        
        Args:
            note: MIDI音符號
            instrument_type: 樂器類型
            preferred_octave: 偏好的八度區域
            
        Returns:
            調整後的MIDI音符號
        """
        config = self.get_instrument_config(instrument_type)
        if not config:
            return note
            
        # 如果指定了偏好的八度區域，先嘗試移動到該區域
        if preferred_octave is not None:
            target_note = note + (preferred_octave - note // 12) * 12
            if config.is_note_in_range(target_note):
                return target_note
                
        return config.get_safe_note(note)
    
    def get_playing_techniques(
        self,
        instrument_type: InstrumentType,
        role: InstrumentRole
    ) -> List[PlayingTechnique]:
        """獲取適合的演奏技巧
        
        Args:
            instrument_type: 樂器類型
            role: 樂器角色
            
        Returns:
            適合的演奏技巧列表
        """
        config = self.get_instrument_config(instrument_type)
        if not config:
            return [PlayingTechnique.NORMAL]
            
        # 根據角色篩選合適的技巧
        if role == InstrumentRole.MELODY:
            return [t for t in config.supported_techniques if t in [
                PlayingTechnique.NORMAL,
                PlayingTechnique.LEGATO,
                PlayingTechnique.VIBRATO
            ]]
        elif role == InstrumentRole.HARMONY:
            return [t for t in config.supported_techniques if t in [
                PlayingTechnique.NORMAL,
                PlayingTechnique.PIZZICATO,
                PlayingTechnique.TREMOLO
            ]]
        elif role == InstrumentRole.RHYTHM:
            return [t for t in config.supported_techniques if t in [
                PlayingTechnique.NORMAL,
                PlayingTechnique.STACCATO
            ]]
        else:
            return [PlayingTechnique.NORMAL] 