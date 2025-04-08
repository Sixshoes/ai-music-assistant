"""命令解析器模組

提供文字和音頻命令的解析功能
"""

import base64
import logging
import re
from typing import Optional, Dict, Any, List, Tuple

from .mcp_schema import MCPCommand, MusicParameters, Genre, InstrumentType, MusicKey, TimeSignature
from .style_manager import StyleManager

logger = logging.getLogger(__name__)

class TextCommandParser:
    """文字命令解析器"""
    
    def __init__(self):
        """初始化文字命令解析器"""
        self.style_manager = StyleManager()
        self.context_history = []  # 用於存儲上下文歷史
        
        # 初始化關鍵詞映射
        self._init_keyword_mappings()
        
    def _init_keyword_mappings(self):
        """初始化各種關鍵詞映射"""
        # 風格關鍵詞映射到 Genre 枚舉
        self.style_keywords = {
            '流行': Genre.POP,
            '搖滾': Genre.ROCK,
            '爵士': Genre.JAZZ,
            '古典': Genre.CLASSICAL,
            '藍調': Genre.BLUES,
            '電子': Genre.ELECTRONIC,
            '鄉村': Genre.COUNTRY,
            '嘻哈': Genre.HIP_HOP,
            '民謠': Genre.FOLK,
            '拉丁': Genre.LATIN,
            '輕音樂': Genre.EASY_LISTENING
        }
        
        # 情感關鍵詞映射到音樂參數調整
        self.emotion_keywords = {
            '快樂': {'tempo_mod': 1.2, 'key_preference': 'major', 'intensity': 0.7},
            '悲傷': {'tempo_mod': 0.8, 'key_preference': 'minor', 'intensity': 0.4},
            '興奮': {'tempo_mod': 1.3, 'key_preference': 'major', 'intensity': 0.9},
            '平靜': {'tempo_mod': 0.7, 'key_preference': 'major', 'intensity': 0.3},
            '憤怒': {'tempo_mod': 1.1, 'key_preference': 'minor', 'intensity': 0.8},
            '柔和': {'tempo_mod': 0.6, 'key_preference': 'major', 'intensity': 0.3},
            '激動': {'tempo_mod': 1.2, 'key_preference': 'minor', 'intensity': 0.8},
            '浪漫': {'tempo_mod': 0.9, 'key_preference': 'major', 'intensity': 0.5},
            '神秘': {'tempo_mod': 0.8, 'key_preference': 'minor', 'intensity': 0.6}
        }
        
        # 樂器關鍵詞映射
        self.instrument_keywords = {
            '鋼琴': InstrumentType.PIANO,
            '吉他': InstrumentType.GUITAR,
            '電吉他': InstrumentType.ELECTRIC_GUITAR,
            '貝斯': InstrumentType.BASS,
            '鼓': InstrumentType.DRUMS,
            '小提琴': InstrumentType.VIOLIN,
            '大提琴': InstrumentType.CELLO,
            '長笛': InstrumentType.FLUTE,
            '薩克斯風': InstrumentType.SAXOPHONE,
            '小號': InstrumentType.TRUMPET,
            '合成器': InstrumentType.SYNTH,
            '弦樂': InstrumentType.STRINGS,
            '管樂': InstrumentType.WOODWINDS,
            '銅管': InstrumentType.BRASS
        }
        
        # 速度關鍵詞映射
        self.tempo_keywords = {
            '很慢': 60,
            '慢': 80,
            '中等': 100,
            '快': 120,
            '很快': 140,
            '極快': 160
        }
        
        # 複雜度關鍵詞映射
        self.complexity_keywords = {
            '簡單': 0.3,
            '普通': 0.5,
            '複雜': 0.7,
            '非常複雜': 0.9
        }
    
    def extract_parameters(self, text: str) -> Dict[str, Any]:
        """從文字中提取音樂參數
        
        Args:
            text: 文字描述
            
        Returns:
            Dict[str, Any]: 提取的參數字典
        """
        extracted_params = {}
        
        # 提取風格
        for keyword, genre in self.style_keywords.items():
            if keyword in text:
                extracted_params['genre'] = genre
                logger.info(f"從文字中識別到風格: {keyword} -> {genre}")
                break
        
        # 提取情感並調整參數
        for keyword, params in self.emotion_keywords.items():
            if keyword in text:
                if 'tempo' not in extracted_params and 'tempo_mod' in params:
                    base_tempo = 100  # 默認基礎速度
                    extracted_params['tempo'] = int(base_tempo * params['tempo_mod'])
                
                if 'key_preference' in params:
                    extracted_params['key_preference'] = params['key_preference']
                
                if 'intensity' in params:
                    extracted_params['intensity'] = params['intensity']
                
                logger.info(f"從文字中識別到情感: {keyword}, 調整參數: {params}")
                break
        
        # 提取樂器
        instruments = []
        for keyword, instrument in self.instrument_keywords.items():
            if keyword in text:
                instruments.append(instrument)
                logger.info(f"從文字中識別到樂器: {keyword} -> {instrument}")
        
        if instruments:
            extracted_params['instruments'] = instruments
        
        # 提取速度
        for keyword, tempo in self.tempo_keywords.items():
            if keyword in text:
                extracted_params['tempo'] = tempo
                logger.info(f"從文字中識別到速度: {keyword} -> {tempo}")
                break
        
        # 提取複雜度
        for keyword, complexity in self.complexity_keywords.items():
            if keyword in text:
                extracted_params['complexity'] = complexity
                logger.info(f"從文字中識別到複雜度: {keyword} -> {complexity}")
                break
        
        # 尋找特定的音樂參數模式
        # 檢查是否有指定調號
        key_match = re.search(r'([CDEFGAB])(?:#|b)?(?:\s*(大調|小調|調))?', text)
        if key_match:
            key_name = key_match.group(1)
            key_type = key_match.group(2) if key_match.group(2) else '大調'
            
            key_map = {
                'C': 'C', 'D': 'D', 'E': 'E', 'F': 'F', 'G': 'G', 'A': 'A', 'B': 'B'
            }
            
            key_type_map = {
                '大調': 'major',
                '小調': 'minor',
                '調': 'major'  # 默認大調
            }
            
            if key_name in key_map:
                key_str = f"{key_map[key_name]}_{key_type_map.get(key_type, 'major')}"
                try:
                    extracted_params['key'] = MusicKey(key_str)
                    logger.info(f"從文字中識別到調號: {key_str}")
                except ValueError:
                    logger.warning(f"無法映射調號: {key_str}")
        
        # 提取拍號
        time_sig_match = re.search(r'(\d+)/(\d+)', text)
        if time_sig_match:
            numerator = time_sig_match.group(1)
            denominator = time_sig_match.group(2)
            time_sig_str = f"{numerator}_{denominator}"
            
            try:
                extracted_params['time_signature'] = TimeSignature(time_sig_str)
                logger.info(f"從文字中識別到拍號: {time_sig_str}")
            except ValueError:
                logger.warning(f"無法映射拍號: {time_sig_str}")
        
        return extracted_params
    
    def analyze_semantic_context(self, text: str) -> Dict[str, Any]:
        """分析文本的語義上下文
        
        Args:
            text: 文字描述
            
        Returns:
            Dict[str, Any]: 語義分析結果
        """
        # 這裡可以接入更複雜的 NLP 分析，目前使用簡單規則
        context = {
            'theme': None,
            'mood': None,
            'structure': None
        }
        
        # 主題識別
        themes = ['愛情', '自然', '城市', '旅行', '冒險', '回憶']
        for theme in themes:
            if theme in text:
                context['theme'] = theme
                break
        
        # 情緒識別 (除了已經在情感關鍵詞中映射的)
        additional_moods = ['輕鬆', '思考', '懷舊', '夢幻']
        for mood in additional_moods:
            if mood in text:
                context['mood'] = mood
                break
        
        # 結構識別
        structures = {
            '起承轉合': '四段式',
            '前奏': '有前奏',
            '副歌': '有副歌',
            '間奏': '有間奏',
            '重複': '有重複段落'
        }
        
        for keyword, structure in structures.items():
            if keyword in text:
                context['structure'] = structure
                break
        
        return context
    
    def add_to_context_history(self, text: str, parameters: Dict[str, Any]):
        """添加到上下文歷史，用於跨會話保存參數偏好
        
        Args:
            text: 文字描述
            parameters: 提取的參數
        """
        # 只保留最近的 5 條記錄
        if len(self.context_history) >= 5:
            self.context_history.pop(0)
        
        self.context_history.append({
            'text': text,
            'parameters': parameters
        })
    
    def get_context_aware_parameters(self, current_params: Dict[str, Any]) -> Dict[str, Any]:
        """根據歷史上下文調整當前參數
        
        Args:
            current_params: 當前從文本提取的參數
            
        Returns:
            Dict[str, Any]: 調整後的參數
        """
        # 如果沒有歷史記錄，直接返回當前參數
        if not self.context_history:
            return current_params
        
        # 獲取最近一次的參數作為基準
        last_params = self.context_history[-1]['parameters']
        
        # 合併參數，當前參數優先
        merged_params = {}
        merged_params.update(last_params)
        merged_params.update(current_params)
        
        return merged_params
    
    def suggest_models(self, parameters: Dict[str, Any]) -> List[str]:
        """根據參數建議使用的 Magenta 模型
        
        Args:
            parameters: 音樂參數
            
        Returns:
            List[str]: 建議的模型列表，按優先級排序
        """
        suggested_models = []
        
        # 提取關鍵參數
        genre = parameters.get('genre', None)
        instruments = parameters.get('instruments', [])
        complexity = parameters.get('complexity', 0.5)
        
        # 根據風格和複雜度推薦基礎模型
        if genre in [Genre.CLASSICAL, Genre.JAZZ] or complexity > 0.7:
            suggested_models.append("performance_rnn")  # 更適合複雜的音樂形式
        else:
            suggested_models.append("melody_rnn")  # 適合簡單的旋律
        
        # 如果需要生成和聲或多聲部音樂
        if complexity > 0.5 or len(instruments) > 2:
            suggested_models.append("polyphony_rnn")
        
        # 如果有鼓或節奏要求
        if InstrumentType.DRUMS in instruments:
            suggested_models.append("drums_rnn")
        
        # 如果有具體的鋼琴要求
        if InstrumentType.PIANO in instruments:
            suggested_models.append("pianoroll_rnn_nade")
        
        # 如果列表為空，至少提供默認建議
        if not suggested_models:
            suggested_models = ["melody_rnn", "polyphony_rnn"]
        
        return suggested_models
    
    def parse(self, text: str, parameters: Optional[Dict[str, Any]] = None) -> MCPCommand:
        """解析文字命令
        
        Args:
            text: 文字描述
            parameters: 音樂參數
            
        Returns:
            解析後的命令對象
        """
        try:
            # 從文字中提取參數
            extracted_params = self.extract_parameters(text)
            
            # 分析語義上下文
            context = self.analyze_semantic_context(text)
            
            # 如果有提供參數，合併提取的參數
            if parameters:
                # 合併提取的參數和提供的參數，提供的參數優先
                merged_params = {}
                merged_params.update(extracted_params)
                merged_params.update(parameters)
                extracted_params = merged_params
            
            # 應用上下文感知參數調整
            context_aware_params = self.get_context_aware_parameters(extracted_params)
            
            # 建議模型
            suggested_models = self.suggest_models(context_aware_params)
            
            # 添加到上下文歷史
            self.add_to_context_history(text, context_aware_params)
            
            # 轉換枚舉類型
            if "genre" in context_aware_params and not isinstance(context_aware_params["genre"], Genre):
                context_aware_params["genre"] = Genre(context_aware_params["genre"])
            if "key" in context_aware_params and not isinstance(context_aware_params["key"], MusicKey):
                context_aware_params["key"] = MusicKey(context_aware_params["key"])
            if "time_signature" in context_aware_params and not isinstance(context_aware_params["time_signature"], TimeSignature):
                context_aware_params["time_signature"] = TimeSignature(context_aware_params["time_signature"])
            if "instruments" in context_aware_params:
                processed_instruments = []
                for i in context_aware_params["instruments"]:
                    if not isinstance(i, InstrumentType):
                        try:
                            processed_instruments.append(InstrumentType(i))
                        except ValueError:
                            logger.warning(f"無法轉換為樂器類型: {i}")
                    else:
                        processed_instruments.append(i)
                context_aware_params["instruments"] = processed_instruments
            
            # 創建音樂參數對象
            music_params = MusicParameters(**context_aware_params)
            
            # 創建命令
            command = MCPCommand(
                type="text_to_music",
                text_input=text,
                parameters=music_params,
                metadata={
                    "context": context,
                    "suggested_models": suggested_models
                }
            )
            
            return command
            
        except Exception as e:
            logger.error(f"解析文字命令時發生錯誤: {str(e)}")
            raise

class AudioCommandParser:
    """音頻命令解析器"""
    
    def parse(self, audio_data_url: str, additional_text: Optional[str] = None) -> MCPCommand:
        """解析音頻命令
        
        Args:
            audio_data_url: 音頻數據URL
            additional_text: 額外文字描述
            
        Returns:
            解析後的命令對象
        """
        try:
            # 解析音頻數據
            if audio_data_url.startswith("data:audio/"):
                audio_data = base64.b64decode(audio_data_url.split(",")[1])
            else:
                audio_data = base64.b64decode(audio_data_url)
            
            # 如果有額外文字，使用文字命令解析器處理
            parameters = None
            if additional_text:
                text_parser = TextCommandParser()
                text_command = text_parser.parse(additional_text)
                parameters = text_command.parameters
            else:
                parameters = MusicParameters()
            
            # 創建命令
            command = MCPCommand(
                type="audio_to_music",
                audio_input=audio_data,
                text_input=additional_text if additional_text else "",
                parameters=parameters
            )
            
            return command
            
        except Exception as e:
            logger.error(f"解析音頻命令時發生錯誤: {str(e)}")
            raise 