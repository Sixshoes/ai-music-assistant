"""文字指令解析器

解析自然語言文字描述，將其轉換為標準化的指令對象
"""

import re
import logging
from typing import Dict, Any, Optional, List, Tuple
import jieba
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

from ..mcp_schema import (
    MCPCommand,
    CommandType,
    MusicParameters,
    MusicKey,
    TimeSignature,
    Genre,
    Emotion,
    InstrumentType,
    MusicalForm,
    ModelType
)

# 嘗試下載必要的nltk資源（僅在初次運行時需要）
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

class TextCommandParser:
    """文字指令解析器類"""
    
    def __init__(self):
        """初始化解析器"""
        self.logger = logging.getLogger(__name__)
        self.lemmatizer = WordNetLemmatizer()
        
        # 初始化關鍵字匹配模式
        self.key_patterns = {
            key.value: re.compile(r'\b' + re.escape(key.value) + r'\b', re.IGNORECASE)
            for key in MusicKey
        }
        
        self.genre_patterns = {
            genre.value: re.compile(r'\b' + re.escape(genre.value) + r'\b', re.IGNORECASE)
            for genre in Genre
        }
        
        self.emotion_patterns = {
            emotion.value: re.compile(r'\b' + re.escape(emotion.value) + r'\b', re.IGNORECASE)
            for emotion in Emotion
        }
        
        self.instrument_patterns = {
            instrument.value: re.compile(r'\b' + re.escape(instrument.value) + r'\b', re.IGNORECASE)
            for instrument in InstrumentType
        }
        
        self.form_patterns = {
            form.value: re.compile(r'\b' + re.escape(form.value) + r'\b', re.IGNORECASE)
            for form in MusicalForm
        }
        
        # 正則表達式模式
        self.tempo_pattern = re.compile(r'(\d+)\s*(bpm|拍|速度)', re.IGNORECASE)
        self.duration_pattern = re.compile(r'(\d+)\s*(秒|分鐘|分|s|min)', re.IGNORECASE)
        self.complexity_pattern = re.compile(r'複雜度\s*(\d+)|复杂度\s*(\d+)|complexity\s*(\d+)', re.IGNORECASE)
        
        # 命令類型關鍵詞映射
        self.command_type_keywords = {
            CommandType.TEXT_TO_MUSIC: [
                'generate', 'create', '生成', '創作', '作曲', 'compose', 'write', 'music', '音樂'
            ],
            CommandType.MELODY_TO_ARRANGEMENT: [
                'arrange', 'arrangement', '編曲', '和聲', 'harmonize', 'accompany', 'accompaniment'
            ],
            CommandType.MUSIC_ANALYSIS: [
                'analyze', 'analysis', '分析', 'theory', '理論', 'understand', 'explain'
            ],
            CommandType.PITCH_CORRECTION: [
                'correct', 'fix', 'tune', '修正', '校正', '調音', 'autotune', 'pitch'
            ],
            CommandType.STYLE_TRANSFER: [
                'transfer', 'style', 'transform', '風格轉換', '風格', '轉換'
            ],
            CommandType.IMPROVISATION: [
                'improvise', 'jam', 'solo', '即興', '即兴演奏', '即兴'
            ]
        }
        
        # 模型偏好關鍵詞映射
        self.model_keywords = {
            ModelType.MAGENTA: ['magenta', 'google', '谷歌'],
            ModelType.MUSICGEN: ['musicgen', 'facebook', 'meta'],
            ModelType.TRANSFORMER: ['transformer', 'attention', '注意力'],
            ModelType.LSTM: ['lstm', 'recurrent', 'rnn', '循環'],
            ModelType.GAN: ['gan', 'generative adversarial', '對抗'],
            ModelType.DIFFUSION: ['diffusion', 'stable', '擴散']
        }
    
    def parse(self, text: str) -> MCPCommand:
        """解析文字描述為指令對象
        
        Args:
            text: 文字描述
            
        Returns:
            MCPCommand: 解析後的指令對象
        """
        self.logger.info(f"解析文字指令: {text}")
        
        # 識別命令類型
        command_type = self._identify_command_type(text)
        self.logger.debug(f"識別命令類型: {command_type}")
        
        # 提取參數
        parameters = self._extract_parameters(text)
        self.logger.debug(f"提取參數: {parameters}")
        
        # 提取模型偏好
        model_preferences = self._extract_model_preferences(text)
        self.logger.debug(f"提取模型偏好: {model_preferences}")
        
        # 創建並返回指令對象
        return MCPCommand(
            command_type=command_type,
            text_input=text,
            parameters=parameters,
            model_preferences=model_preferences
        )
    
    def _identify_command_type(self, text: str) -> CommandType:
        """識別命令類型
        
        Args:
            text: 文字描述
            
        Returns:
            CommandType: 識別的命令類型
        """
        # 預處理文字
        processed_text = text.lower()
        
        # 分詞處理（支持中英文）
        tokens = []
        # 英文分詞
        english_tokens = word_tokenize(processed_text)
        tokens.extend([self.lemmatizer.lemmatize(token) for token in english_tokens])
        
        # 中文分詞
        chinese_tokens = jieba.cut(processed_text)
        tokens.extend(chinese_tokens)
        
        # 計算每種命令類型的匹配分數
        type_scores = {}
        for cmd_type, keywords in self.command_type_keywords.items():
            score = sum(1 for keyword in keywords if keyword in processed_text)
            type_scores[cmd_type] = score
        
        # 默認為文本到音樂
        if all(score == 0 for score in type_scores.values()):
            return CommandType.TEXT_TO_MUSIC
        
        # 返回得分最高的命令類型
        return max(type_scores.items(), key=lambda x: x[1])[0]
    
    def _extract_parameters(self, text: str) -> MusicParameters:
        """從文字描述中提取音樂參數
        
        Args:
            text: 文字描述
            
        Returns:
            MusicParameters: 提取的音樂參數
        """
        # 提取各項參數
        key = self._extract_key(text)
        tempo = self._extract_tempo(text)
        time_signature = self._extract_time_signature(text)
        genre = self._extract_genre(text)
        emotion = self._extract_emotion(text)
        instruments = self._extract_instruments(text)
        duration = self._extract_duration(text)
        form = self._extract_form(text)
        complexity = self._extract_complexity(text)
        
        # 創建並返回參數對象
        return MusicParameters(
            key=key,
            tempo=tempo,
            time_signature=time_signature,
            genre=genre,
            emotion=emotion,
            instruments=instruments,
            duration=duration,
            form=form,
            complexity=complexity
        )
    
    def _extract_key(self, text: str) -> Optional[MusicKey]:
        """提取調性
        
        Args:
            text: 文字描述
            
        Returns:
            Optional[MusicKey]: 提取的調性，如果未找到則為None
        """
        # 直接匹配調性名稱
        for key_str, pattern in self.key_patterns.items():
            if pattern.search(text):
                # 將字符串轉換為枚舉值
                for key in MusicKey:
                    if key.value == key_str:
                        return key
        
        # 中文調性關鍵詞匹配
        key_words = {
            "C大調": MusicKey.C_MAJOR, "C大调": MusicKey.C_MAJOR, "C大": MusicKey.C_MAJOR,
            "G大調": MusicKey.G_MAJOR, "G大调": MusicKey.G_MAJOR, "G大": MusicKey.G_MAJOR,
            "D大調": MusicKey.D_MAJOR, "D大调": MusicKey.D_MAJOR, "D大": MusicKey.D_MAJOR,
            "A大調": MusicKey.A_MAJOR, "A大调": MusicKey.A_MAJOR, "A大": MusicKey.A_MAJOR,
            "E大調": MusicKey.E_MAJOR, "E大调": MusicKey.E_MAJOR, "E大": MusicKey.E_MAJOR,
            "B大調": MusicKey.B_MAJOR, "B大调": MusicKey.B_MAJOR, "B大": MusicKey.B_MAJOR,
            "升F大調": MusicKey.F_SHARP_MAJOR, "升F大调": MusicKey.F_SHARP_MAJOR, "F升大": MusicKey.F_SHARP_MAJOR,
            "升C大調": MusicKey.C_SHARP_MAJOR, "升C大调": MusicKey.C_SHARP_MAJOR, "C升大": MusicKey.C_SHARP_MAJOR,
            "F大調": MusicKey.F_MAJOR, "F大调": MusicKey.F_MAJOR, "F大": MusicKey.F_MAJOR,
            "降B大調": MusicKey.B_FLAT_MAJOR, "降B大调": MusicKey.B_FLAT_MAJOR, "B降大": MusicKey.B_FLAT_MAJOR,
            "降E大調": MusicKey.E_FLAT_MAJOR, "降E大调": MusicKey.E_FLAT_MAJOR, "E降大": MusicKey.E_FLAT_MAJOR,
            "降A大調": MusicKey.A_FLAT_MAJOR, "降A大调": MusicKey.A_FLAT_MAJOR, "A降大": MusicKey.A_FLAT_MAJOR,
            "降D大調": MusicKey.D_FLAT_MAJOR, "降D大调": MusicKey.D_FLAT_MAJOR, "D降大": MusicKey.D_FLAT_MAJOR,
            "降G大調": MusicKey.G_FLAT_MAJOR, "降G大调": MusicKey.G_FLAT_MAJOR, "G降大": MusicKey.G_FLAT_MAJOR,
            "降C大調": MusicKey.C_FLAT_MAJOR, "降C大调": MusicKey.C_FLAT_MAJOR, "C降大": MusicKey.C_FLAT_MAJOR,
            
            "A小調": MusicKey.A_MINOR, "A小调": MusicKey.A_MINOR, "A小": MusicKey.A_MINOR,
            "E小調": MusicKey.E_MINOR, "E小调": MusicKey.E_MINOR, "E小": MusicKey.E_MINOR,
            "B小調": MusicKey.B_MINOR, "B小调": MusicKey.B_MINOR, "B小": MusicKey.B_MINOR,
            "升F小調": MusicKey.F_SHARP_MINOR, "升F小调": MusicKey.F_SHARP_MINOR, "F升小": MusicKey.F_SHARP_MINOR,
            "升C小調": MusicKey.C_SHARP_MINOR, "升C小调": MusicKey.C_SHARP_MINOR, "C升小": MusicKey.C_SHARP_MINOR,
            "升G小調": MusicKey.G_SHARP_MINOR, "升G小调": MusicKey.G_SHARP_MINOR, "G升小": MusicKey.G_SHARP_MINOR,
            "升D小調": MusicKey.D_SHARP_MINOR, "升D小调": MusicKey.D_SHARP_MINOR, "D升小": MusicKey.D_SHARP_MINOR,
            "升A小調": MusicKey.A_SHARP_MINOR, "升A小调": MusicKey.A_SHARP_MINOR, "A升小": MusicKey.A_SHARP_MINOR,
            "D小調": MusicKey.D_MINOR, "D小调": MusicKey.D_MINOR, "D小": MusicKey.D_MINOR,
            "G小調": MusicKey.G_MINOR, "G小调": MusicKey.G_MINOR, "G小": MusicKey.G_MINOR,
            "C小調": MusicKey.C_MINOR, "C小调": MusicKey.C_MINOR, "C小": MusicKey.C_MINOR,
            "F小調": MusicKey.F_MINOR, "F小调": MusicKey.F_MINOR, "F小": MusicKey.F_MINOR,
            "降B小調": MusicKey.B_FLAT_MINOR, "降B小调": MusicKey.B_FLAT_MINOR, "B降小": MusicKey.B_FLAT_MINOR,
            "降E小調": MusicKey.E_FLAT_MINOR, "降E小调": MusicKey.E_FLAT_MINOR, "E降小": MusicKey.E_FLAT_MINOR,
            "降A小調": MusicKey.A_FLAT_MINOR, "降A小调": MusicKey.A_FLAT_MINOR, "A降小": MusicKey.A_FLAT_MINOR,
        }
        
        for key_word, key_value in key_words.items():
            if key_word in text:
                return key_value
        
        return None
    
    def _extract_tempo(self, text: str) -> Optional[int]:
        """提取速度
        
        Args:
            text: 文字描述
            
        Returns:
            Optional[int]: 提取的速度，如果未找到則為None
        """
        # 直接匹配數字+BPM
        match = self.tempo_pattern.search(text)
        if match:
            tempo = int(match.group(1))
            # 確保在有效範圍內
            if 40 <= tempo <= 240:
                return tempo
            # 如果超出範圍，則限制在有效範圍內
            return max(40, min(tempo, 240))
        
        # 根據關鍵詞推斷速度
        tempo_keywords = {
            "極慢": 40, "极慢": 40, "very slow": 40, 
            "慢": 60, "slow": 60,
            "中慢": 80, "medium slow": 80,
            "中速": 100, "moderate": 100, "medium": 100,
            "中快": 120, "medium fast": 120,
            "快": 140, "fast": 140,
            "極快": 180, "极快": 180, "very fast": 180
        }
        
        for keyword, value in tempo_keywords.items():
            if keyword in text.lower():
                return value
        
        # 如果是舞曲類型，可根據舞曲類型推斷速度
        dance_tempos = {
            "華爾滋": 90, "华尔兹": 90, "waltz": 90,
            "探戈": 120, "tango": 120,
            "狐步舞": 120, "foxtrot": 120,
            "倫巴": 100, "伦巴": 100, "rumba": 100,
            "恰恰": 130, "chacha": 130,
            "森巴": 100, "samba": 100
        }
        
        for dance, tempo in dance_tempos.items():
            if dance in text.lower():
                return tempo
                
        return None
    
    def _extract_time_signature(self, text: str) -> Optional[TimeSignature]:
        """提取拍號
        
        Args:
            text: 文字描述
            
        Returns:
            Optional[TimeSignature]: 提取的拍號，如果未找到則為None
        """
        # 直接匹配拍號字符串
        time_sig_patterns = {
            "4/4": TimeSignature.FOUR_FOUR,
            "3/4": TimeSignature.THREE_FOUR,
            "6/8": TimeSignature.SIX_EIGHT,
            "2/4": TimeSignature.TWO_FOUR,
            "5/4": TimeSignature.FIVE_FOUR,
            "7/8": TimeSignature.SEVEN_EIGHT,
            "12/8": TimeSignature.TWELVE_EIGHT,
            "9/8": TimeSignature.NINE_EIGHT,
            "3/8": TimeSignature.THREE_EIGHT
        }
        
        for pattern, value in time_sig_patterns.items():
            if pattern in text:
                return value
        
        # 中文描述匹配
        chinese_patterns = {
            "四四拍": TimeSignature.FOUR_FOUR,
            "三四拍": TimeSignature.THREE_FOUR,
            "六八拍": TimeSignature.SIX_EIGHT,
            "二四拍": TimeSignature.TWO_FOUR,
            "五四拍": TimeSignature.FIVE_FOUR,
            "七八拍": TimeSignature.SEVEN_EIGHT,
            "十二八拍": TimeSignature.TWELVE_EIGHT,
            "九八拍": TimeSignature.NINE_EIGHT,
            "三八拍": TimeSignature.THREE_EIGHT
        }
        
        for pattern, value in chinese_patterns.items():
            if pattern in text:
                return value
                
        # 根據風格推斷拍號
        if "華爾滋" in text or "华尔兹" in text or "waltz" in text.lower():
            return TimeSignature.THREE_FOUR
            
        if "進行曲" in text or "进行曲" in text or "march" in text.lower():
            return TimeSignature.FOUR_FOUR
            
        return None
    
    def _extract_genre(self, text: str) -> Optional[Genre]:
        """提取風格
        
        Args:
            text: 文字描述
            
        Returns:
            Optional[Genre]: 提取的風格，如果未找到則為None
        """
        # 直接匹配風格名稱
        for genre_str, pattern in self.genre_patterns.items():
            if pattern.search(text):
                # 將字符串轉換為枚舉值
                for genre in Genre:
                    if genre.value == genre_str:
                        return genre
        
        # 中文風格關鍵詞匹配
        genre_keywords = {
            "古典": Genre.CLASSICAL, "交響": Genre.CLASSICAL, "交响": Genre.CLASSICAL, "室內樂": Genre.CLASSICAL,
            "搖滾": Genre.ROCK, "摇滚": Genre.ROCK, "硬摇": Genre.ROCK,
            "爵士": Genre.JAZZ, "爵士樂": Genre.JAZZ, "藍調爵士": Genre.JAZZ,
            "流行": Genre.POP, "大眾": Genre.POP, "通俗": Genre.POP,
            "電子": Genre.ELECTRONIC, "电子": Genre.ELECTRONIC, "合成器": Genre.ELECTRONIC, "舞曲": Genre.ELECTRONIC,
            "鄉村": Genre.COUNTRY, "乡村": Genre.COUNTRY, "鄉村民謠": Genre.COUNTRY,
            "藍調": Genre.BLUES, "蓝调": Genre.BLUES, "布鲁斯": Genre.BLUES,
            "嘻哈": Genre.HIP_HOP, "饒舌": Genre.HIP_HOP, "说唱": Genre.HIP_HOP, "rap": Genre.HIP_HOP,
            "民謠": Genre.FOLK, "民歌": Genre.FOLK, "傳統": Genre.FOLK, "传统": Genre.FOLK,
            "R&B": Genre.RNB, "節奏藍調": Genre.RNB, "灵魂乐": Genre.RNB,
            "氛圍": Genre.AMBIENT, "环境": Genre.AMBIENT, "ambient": Genre.AMBIENT,
            "放克": Genre.FUNK, "funk": Genre.FUNK,
            "拉丁": Genre.LATIN, "latin": Genre.LATIN, "巴萨诺瓦": Genre.LATIN, "桑巴": Genre.LATIN,
            "世界音樂": Genre.WORLD, "民族音樂": Genre.WORLD, "world music": Genre.WORLD
        }
        
        for keyword, genre in genre_keywords.items():
            if keyword in text.lower():
                return genre
                
        return None
    
    def _extract_emotion(self, text: str) -> Optional[Emotion]:
        """提取情感
        
        Args:
            text: 文字描述
            
        Returns:
            Optional[Emotion]: 提取的情感，如果未找到則為None
        """
        # 直接匹配情感名稱
        for emotion_str, pattern in self.emotion_patterns.items():
            if pattern.search(text):
                # 將字符串轉換為枚舉值
                for emotion in Emotion:
                    if emotion.value == emotion_str:
                        return emotion
        
        # 中文情感關鍵詞匹配
        emotion_keywords = {
            "快樂": Emotion.HAPPY, "歡樂": Emotion.HAPPY, "开心": Emotion.HAPPY, "喜悦": Emotion.HAPPY,
            "悲傷": Emotion.SAD, "憂鬱": Emotion.SAD, "伤心": Emotion.SAD, "难过": Emotion.SAD, "哀伤": Emotion.SAD,
            "平靜": Emotion.CALM, "安詳": Emotion.CALM, "平和": Emotion.CALM, "宁静": Emotion.CALM, "舒适": Emotion.CALM,
            "活力": Emotion.ENERGETIC, "精力": Emotion.ENERGETIC, "活跃": Emotion.ENERGETIC, "兴奋": Emotion.ENERGETIC,
            "浪漫": Emotion.ROMANTIC, "溫柔": Emotion.ROMANTIC, "温柔": Emotion.ROMANTIC, "美好": Emotion.ROMANTIC,
            "黑暗": Emotion.DARK, "沉重": Emotion.DARK, "阴郁": Emotion.DARK, "悲怆": Emotion.DARK,
            "史詩": Emotion.EPIC, "壯觀": Emotion.EPIC, "宏伟": Emotion.EPIC, "壮阔": Emotion.EPIC, "恢宏": Emotion.EPIC,
            "懷舊": Emotion.NOSTALGIC, "回憶": Emotion.NOSTALGIC, "怀旧": Emotion.NOSTALGIC, "追忆": Emotion.NOSTALGIC,
            "神秘": Emotion.MYSTERIOUS, "奇异": Emotion.MYSTERIOUS, "迷幻": Emotion.MYSTERIOUS,
            "遊戲": Emotion.PLAYFUL, "玩樂": Emotion.PLAYFUL, "轻松": Emotion.PLAYFUL, "愉悦": Emotion.PLAYFUL,
            "焦慮": Emotion.ANXIOUS, "担忧": Emotion.ANXIOUS, "紧张": Emotion.ANXIOUS, "不安": Emotion.ANXIOUS,
            "希望": Emotion.HOPEFUL, "期待": Emotion.HOPEFUL, "向往": Emotion.HOPEFUL, "光明": Emotion.HOPEFUL,
            "夢幻": Emotion.DREAMY, "梦幻": Emotion.DREAMY, "迷离": Emotion.DREAMY, "恍惚": Emotion.DREAMY,
            "憤怒": Emotion.ANGRY, "愤怒": Emotion.ANGRY, "激昂": Emotion.ANGRY, "激动": Emotion.ANGRY
        }
        
        for keyword, emotion in emotion_keywords.items():
            if keyword in text.lower():
                return emotion
                
        return None
    
    def _extract_instruments(self, text: str) -> Optional[List[InstrumentType]]:
        """提取樂器
        
        Args:
            text: 文字描述
            
        Returns:
            Optional[List[InstrumentType]]: 提取的樂器列表，如果未找到則為None
        """
        instruments = []
        
        # 直接匹配樂器名稱
        for instrument_str, pattern in self.instrument_patterns.items():
            if pattern.search(text):
                # 將字符串轉換為枚舉值
                for instrument in InstrumentType:
                    if instrument.value == instrument_str and instrument not in instruments:
                        instruments.append(instrument)
        
        # 中文樂器關鍵詞匹配
        instrument_keywords = {
            "鋼琴": InstrumentType.PIANO, "钢琴": InstrumentType.PIANO, "piano": InstrumentType.PIANO,
            "吉他": InstrumentType.GUITAR, "guitar": InstrumentType.GUITAR, "电吉他": InstrumentType.GUITAR, "木吉他": InstrumentType.GUITAR,
            "鼓": InstrumentType.DRUMS, "架子鼓": InstrumentType.DRUMS, "drum": InstrumentType.DRUMS, "打击乐器": InstrumentType.DRUMS,
            "貝斯": InstrumentType.BASS, "贝司": InstrumentType.BASS, "bass": InstrumentType.BASS, "低音吉他": InstrumentType.BASS,
            "弦樂": InstrumentType.STRINGS, "小提琴": InstrumentType.STRINGS, "大提琴": InstrumentType.STRINGS, "中提琴": InstrumentType.STRINGS, "弦乐": InstrumentType.STRINGS, "violin": InstrumentType.STRINGS, "cello": InstrumentType.STRINGS,
            "銅管": InstrumentType.BRASS, "小號": InstrumentType.BRASS, "長號": InstrumentType.BRASS, "圆号": InstrumentType.BRASS, "trumpet": InstrumentType.BRASS, "trombone": InstrumentType.BRASS,
            "管樂": InstrumentType.WOODWINDS, "長笛": InstrumentType.WOODWINDS, "單簧管": InstrumentType.WOODWINDS, "木管": InstrumentType.WOODWINDS, "flute": InstrumentType.WOODWINDS, "clarinet": InstrumentType.WOODWINDS,
            "合成器": InstrumentType.SYNTH, "合成": InstrumentType.SYNTH, "電子琴": InstrumentType.SYNTH, "电子琴": InstrumentType.SYNTH, "synth": InstrumentType.SYNTH,
            "人聲": InstrumentType.VOCAL, "聲樂": InstrumentType.VOCAL, "歌聲": InstrumentType.VOCAL, "合唱": InstrumentType.VOCAL, "vocal": InstrumentType.VOCAL, "voice": InstrumentType.VOCAL,
            "風琴": InstrumentType.ORGAN, "管風琴": InstrumentType.ORGAN, "organ": InstrumentType.ORGAN,
            "打擊樂": InstrumentType.PERCUSSION, "打击乐": InstrumentType.PERCUSSION, "percussion": InstrumentType.PERCUSSION, "敲击乐器": InstrumentType.PERCUSSION,
            "豎琴": InstrumentType.HARP, "竖琴": InstrumentType.HARP, "harp": InstrumentType.HARP,
            "馬林巴": InstrumentType.MARIMBA, "马林巴": InstrumentType.MARIMBA, "木琴": InstrumentType.MARIMBA, "marimba": InstrumentType.MARIMBA,
            "手風琴": InstrumentType.ACCORDION, "手风琴": InstrumentType.ACCORDION, "accordion": InstrumentType.ACCORDION
        }
        
        for keyword, instrument in instrument_keywords.items():
            if keyword in text.lower() and instrument not in instruments:
                instruments.append(instrument)
        
        # 根據風格推斷可能的樂器
        if not instruments:
            genre = self._extract_genre(text)
            if genre:
                if genre == Genre.ROCK:
                    instruments = [InstrumentType.GUITAR, InstrumentType.DRUMS, InstrumentType.BASS]
                elif genre == Genre.CLASSICAL:
                    instruments = [InstrumentType.PIANO, InstrumentType.STRINGS]
                elif genre == Genre.JAZZ:
                    instruments = [InstrumentType.PIANO, InstrumentType.BRASS, InstrumentType.BASS, InstrumentType.DRUMS]
                elif genre == Genre.ELECTRONIC:
                    instruments = [InstrumentType.SYNTH, InstrumentType.DRUMS]
        
        return instruments if instruments else None
    
    def _extract_duration(self, text: str) -> Optional[int]:
        """提取時長
        
        Args:
            text: 文字描述
            
        Returns:
            Optional[int]: 提取的時長（秒），如果未找到則為None
        """
        match = self.duration_pattern.search(text)
        if match:
            value = int(match.group(1))
            unit = match.group(2).lower()
            
            # 轉換為秒
            if "分" in unit or "min" in unit:  # 分鐘
                duration = value * 60
            else:  # 秒
                duration = value
            
            # 確保在有效範圍內
            return max(5, min(duration, 600))
        
        # 根據描述推斷長度
        if "短" in text or "brief" in text.lower() or "short" in text.lower():
            return 60  # 1分鐘
        elif "中等長度" in text or "medium length" in text.lower():
            return 180  # 3分鐘
        elif "長" in text or "long" in text.lower():
            return 300  # 5分鐘
            
        return None
    
    def _extract_form(self, text: str) -> Optional[MusicalForm]:
        """提取音樂形式
        
        Args:
            text: 文字描述
            
        Returns:
            Optional[MusicalForm]: 提取的音樂形式，如果未找到則為None
        """
        # 直接匹配形式名稱
        for form_str, pattern in self.form_patterns.items():
            if pattern.search(text):
                # 將字符串轉換為枚舉值
                for form in MusicalForm:
                    if form.value == form_str:
                        return form
        
        # 中文形式關鍵詞匹配
        form_keywords = {
            "主歌副歌": MusicalForm.VERSE_CHORUS, "verse chorus": MusicalForm.VERSE_CHORUS,
            "ABA": MusicalForm.ABA, "三段體": MusicalForm.ABA, "三段体": MusicalForm.ABA,
            "迴旋": MusicalForm.RONDO, "回旋": MusicalForm.RONDO, "rondo": MusicalForm.RONDO,
            "通作": MusicalForm.THROUGH_COMPOSED, "贯穿": MusicalForm.THROUGH_COMPOSED, "through composed": MusicalForm.THROUGH_COMPOSED,
            "主題變奏": MusicalForm.THEME_VARIATIONS, "主题变奏": MusicalForm.THEME_VARIATIONS, "变奏曲": MusicalForm.THEME_VARIATIONS, "theme and variations": MusicalForm.THEME_VARIATIONS,
            "奏鳴曲": MusicalForm.SONATA, "奏鸣曲": MusicalForm.SONATA, "sonata": MusicalForm.SONATA,
            "二段體": MusicalForm.BINARY, "二段体": MusicalForm.BINARY, "binary": MusicalForm.BINARY,
            "三段體": MusicalForm.TERNARY, "三段体": MusicalForm.TERNARY, "ternary": MusicalForm.TERNARY
        }
        
        for keyword, form in form_keywords.items():
            if keyword in text.lower():
                return form
                
        return None
    
    def _extract_complexity(self, text: str) -> Optional[int]:
        """提取複雜度
        
        Args:
            text: 文字描述
            
        Returns:
            Optional[int]: 提取的複雜度（1-10），如果未找到則為None
        """
        # 直接匹配複雜度數字
        match = self.complexity_pattern.search(text)
        if match:
            # 獲取第一個非None的捕獲組
            for group in match.groups():
                if group is not None:
                    complexity = int(group)
                    # 確保在有效範圍內
                    return max(1, min(complexity, 10))
        
        # 根據關鍵詞推斷複雜度
        complexity_keywords = {
            "簡單": 2, "简单": 2, "simple": 2, "easy": 2,
            "基礎": 3, "基础": 3, "basic": 3,
            "一般": 5, "普通": 5, "normal": 5, "regular": 5,
            "進階": 7, "高級": 7, "高级": 7, "advanced": 7,
            "複雜": 8, "复杂": 8, "complex": 8,
            "專業": 9, "专业": 9, "professional": 9,
            "極致": 10, "极致": 10, "extreme": 10, "virtuosic": 10
        }
        
        for keyword, value in complexity_keywords.items():
            if keyword in text.lower():
                return value
                
        return None
        
    def _extract_model_preferences(self, text: str) -> Optional[List[ModelType]]:
        """提取模型偏好
        
        Args:
            text: 文字描述
            
        Returns:
            Optional[List[ModelType]]: 提取的模型偏好列表，如果未找到則為None
        """
        models = []
        
        # 檢查文本中的模型關鍵詞
        for model_type, keywords in self.model_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    models.append(model_type)
                    break
        
        return models if models else None 