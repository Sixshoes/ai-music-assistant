"""音樂需求分析器

通過大語言模型理解和拆解用戶的音樂創作需求
"""

import os
import logging
import json
import requests
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMProviderType(str, Enum):
    """LLM提供商類型"""
    OPENAI = "openai"
    HUGGINGFACE = "huggingface"
    LMSTUDIO = "lmstudio"

@dataclass
class MusicRequirement:
    """音樂需求參數"""
    # 基本參數
    description: str  # 原始描述
    genre: str = "classical"  # 音樂風格
    mood: str = "neutral"  # 情感氛圍
    tempo: int = 120  # 速度
    key: str = "C"  # 調性
    time_signature: str = "4/4"  # 拍號
    
    # 結構參數
    form: str = "binary"  # 曲式結構 (binary, ternary, verse-chorus, etc.)
    duration: int = 30  # 預期持續時間（秒）
    section_count: int = 2  # 段落數量
    
    # 風格參數
    cultural_elements: List[str] = None  # 文化元素
    instruments: List[str] = None  # 樂器
    instrument_roles: Dict[str, str] = None  # 樂器角色分配
    techniques: List[str] = None  # 演奏技巧
    
    # 旋律參數
    melodic_character: str = "flowing"  # 旋律特性
    harmonic_complexity: str = "moderate"  # 和聲複雜度
    rhythmic_features: str = "regular"  # 節奏特徵
    
    # 增加音樂完整性相關參數
    has_intro: bool = False  # 是否有前奏
    has_outro: bool = False  # 是否有尾聲
    has_bridge: bool = False  # 是否有橋段
    song_structure: List[str] = None  # 歌曲結構 (例如 ["verse", "chorus", "verse", "chorus", "bridge", "chorus"])
    
    # 增加用戶指定的專業樂理參數
    music_theory_params: Dict[str, Any] = None  # 用戶指定的樂理參數
    
    # 敘事元素分析
    narrative_setting: str = None  # 敘事場景
    cultural_background: str = None  # 文化背景
    time_period: str = None  # 時代背景
    occasion: str = None  # 適用場合
    
    # 音色質感分析
    timbre_character: str = None  # 音色質感特徵 (如明亮/黯淡、溫暖/冷峻)
    sound_layers: int = 3  # 音色層次
    spatial_character: str = None  # 空間感特徵
    
    # 音樂表現技巧建議
    harmony_suggestions: List[str] = None  # 和聲語言建議
    arrangement_techniques: List[str] = None  # 配器技巧建議
    development_techniques: List[str] = None  # 發展技巧建議
    
    def __post_init__(self):
        # 初始化可能的None值
        if self.cultural_elements is None:
            self.cultural_elements = []
        if self.instruments is None:
            self.instruments = ["piano"]
        if self.instrument_roles is None:
            self.instrument_roles = {"piano": "melody"}
        if self.techniques is None:
            self.techniques = []
        if self.song_structure is None:
            self.song_structure = ["A", "B"] if self.form == "binary" else ["A", "B", "A"]
        if self.music_theory_params is None:
            self.music_theory_params = {}
        if self.harmony_suggestions is None:
            self.harmony_suggestions = []
        if self.arrangement_techniques is None:
            self.arrangement_techniques = []
        if self.development_techniques is None:
            self.development_techniques = []
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "description": self.description,
            "genre": self.genre,
            "mood": self.mood,
            "tempo": self.tempo,
            "key": self.key,
            "time_signature": self.time_signature,
            "form": self.form,
            "duration": self.duration,
            "section_count": self.section_count,
            "cultural_elements": self.cultural_elements,
            "instruments": self.instruments,
            "instrument_roles": self.instrument_roles,
            "techniques": self.techniques,
            "melodic_character": self.melodic_character,
            "harmonic_complexity": self.harmonic_complexity,
            "rhythmic_features": self.rhythmic_features,
            "has_intro": self.has_intro,
            "has_outro": self.has_outro,
            "has_bridge": self.has_bridge,
            "song_structure": self.song_structure,
            "music_theory_params": self.music_theory_params,
            "narrative_setting": self.narrative_setting,
            "cultural_background": self.cultural_background,
            "time_period": self.time_period,
            "occasion": self.occasion,
            "timbre_character": self.timbre_character,
            "sound_layers": self.sound_layers,
            "spatial_character": self.spatial_character,
            "harmony_suggestions": self.harmony_suggestions,
            "arrangement_techniques": self.arrangement_techniques,
            "development_techniques": self.development_techniques
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MusicRequirement':
        """從字典創建"""
        return cls(**data)

class MusicRequirementAnalyzer:
    """音樂需求分析器
    
    利用大語言模型理解和拆解用戶的音樂創作需求
    """
    
    def __init__(self, 
                llm_api_key: Optional[str] = None, 
                llm_api_url: Optional[str] = None,
                provider_type: LLMProviderType = LLMProviderType.HUGGINGFACE):
        """初始化音樂需求分析器
        
        Args:
            llm_api_key: 大語言模型API密鑰
            llm_api_url: 大語言模型API端點
            provider_type: 提供商類型
        """
        self.llm_api_key = llm_api_key
        self.llm_api_url = llm_api_url
        self.provider_type = provider_type
        
        # 設置默認URL (如果未提供)
        if not self.llm_api_url:
            if provider_type == LLMProviderType.OPENAI:
                self.llm_api_url = "https://api.openai.com/v1/chat/completions"
            elif provider_type == LLMProviderType.LMSTUDIO:
                self.llm_api_url = "http://localhost:1234/v1/chat/completions"
            elif provider_type == LLMProviderType.HUGGINGFACE:
                self.llm_api_url = os.environ.get("HF_API_URL", "")
        
        logger.info(f"初始化音樂需求分析器，提供商: {provider_type.value}")
    
    def analyze_music_requirement(self, description: str) -> MusicRequirement:
        """分析音樂需求
        
        Args:
            description: 用戶的音樂創作需求描述
            
        Returns:
            MusicRequirement: 解析後的音樂需求參數
        """
        logger.info(f"分析音樂需求: {description}")
        
        # 首先，提取用戶可能提供的樂理知識
        music_theory_params = self._extract_music_theory_params(description)
        
        try:
            # 第一階段：敘事到樂器的規劃
            narrative_analysis = self._analyze_narrative_instruments(description)
            
            # 第二階段：情緒到音樂參數的映射
            emotion_params = self._analyze_emotion_parameters(description)
            
            # 第三階段：參數到音樂表現的轉化
            expression_techniques = self._analyze_expression_techniques(description)
            
            # 檢查是否有任何API調用返回錯誤信息
            if isinstance(narrative_analysis, dict) and "error" in narrative_analysis:
                # API調用失敗，使用模擬數據
                logger.warning("API調用失敗，切換到模擬LLM模式")
                return self._simulate_llm_response(description)
                
            # 綜合所有分析結果
            music_req = self._combine_analysis_results(
                description, 
                narrative_analysis, 
                emotion_params, 
                expression_techniques
            )
        except Exception as e:
            logger.error(f"LLM分析過程中出錯: {str(e)}")
            # 發生錯誤時也使用模擬數據
            logger.warning("遇到錯誤，切換到模擬LLM模式")
            return self._simulate_llm_response(description)
        
        # 將提取的樂理參數整合到分析結果中
        if music_theory_params:
            music_req.music_theory_params = music_theory_params
            logger.info(f"發現用戶指定的樂理參數: {music_theory_params}")
            
            # 這裡可以將指定的樂理參數覆蓋到對應的基本參數中
            for key, value in music_theory_params.items():
                if key == "key" and hasattr(music_req, "key"):
                    music_req.key = value
                elif key == "tempo" and hasattr(music_req, "tempo"):
                    music_req.tempo = value
                elif key == "time_signature" and hasattr(music_req, "time_signature"):
                    music_req.time_signature = value
                # 等等其他參數的轉換...
        
        return music_req
    
    def _extract_music_theory_params(self, description: str) -> Dict[str, Any]:
        """從用戶描述中提取樂理參數
        
        Args:
            description: 用戶描述
            
        Returns:
            Dict[str, Any]: 提取的樂理參數
        """
        # 構建專門用於提取樂理參數的提示詞
        prompt = f"""
作為一位專業的音樂理論分析專家，請從以下描述中提取所有明確的樂理指示和參數：

"{description}"

請僅提取明確指定的樂理參數，不要猜測或推斷。包括但不限於：

1. 調性 (如C大調、降E小調等)
2. 節拍/拍號 (如4/4、3/4、6/8等)
3. 速度標記或BPM (如Allegro、120BPM等)
4. 和弦進行 (如I-IV-V-I、ii-V-I等)
5. 音階/調式 (如大調、自然小調、多利安調式等)
6. 歌曲結構 (如AABA、verse-chorus等)
7. 旋律輪廓或特徵
8. 和聲要求 (如和聲複雜度、特定和聲技術等)
9. 節奏特點 (如切分音、三連音等)
10. 其他具體的音樂技術要求

只返回JSON格式的技術參數，不需要解釋。如果描述中沒有明確的樂理參數，則返回空JSON對象。
"""
        
        # 呼叫LLM專門分析樂理參數
        response = self._call_llm(prompt)
        
        # 嘗試提取JSON
        try:
            import re
            
            # 查找JSON對象
            json_match = re.search(r'(\{.*\})', response, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
                params = json.loads(json_str)
                return params
            else:
                logger.info("未找到用戶指定的樂理參數")
                return {}
                
        except Exception as e:
            logger.error(f"解析樂理參數時出錯: {str(e)}")
            return {}
    
    def _analyze_narrative_instruments(self, description: str) -> Dict[str, Any]:
        """第一階段：分析敘事場景並規劃樂器
        
        Args:
            description: 用戶描述
            
        Returns:
            Dict[str, Any]: 敘事和樂器分析結果
        """
        prompt = f"""
作為一位專業的音樂配器專家，請分析以下音樂描述的敘事場景，並規劃最適合的樂器組合：

"{description}"

請提供詳細的JSON格式分析，包含以下內容：
1. narrative_setting: 從描述中提取的敘事場景或情境
2. cultural_background: 作品的文化背景
3. time_period: 音樂風格所屬的時代背景
4. occasion: 適合的場合（如電影配樂、遊戲音樂、婚禮等）
5. instruments: 根據敘事最適合的4-6種樂器陣列
6. instrument_roles: 每種樂器應該扮演的角色（如melody主旋律、harmony和聲、bass低音、percussion打擊樂等）
7. timbre_character: 整體音色的特性描述（如明亮、溫暖、黯淡、冷峻等）
8. sound_layers: 建議的音色層次數量（2-5）
9. spatial_character: 建議的空間感特徵（如寬廣、親密等）

請確保選擇的樂器組合能夠完美地表達描述中的敘事元素和氛圍，並具有良好的平衡性。

只需返回JSON格式的結果，無需任何解釋文字。
"""
        
        # 呼叫LLM分析
        response = self._call_llm(prompt)
        
        # 嘗試解析JSON
        try:
            import re
            json_match = re.search(r'(\{.*\})', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(1))
                return result
            else:
                logger.warning("無法從敘事分析回應中提取JSON")
                return {}
        except Exception as e:
            logger.error(f"解析敘事分析結果時出錯: {str(e)}")
            return {}
    
    def _analyze_emotion_parameters(self, description: str) -> Dict[str, Any]:
        """第二階段：分析情緒並映射為音樂參數
        
        Args:
            description: 用戶描述
            
        Returns:
            Dict[str, Any]: 情緒和參數分析結果
        """
        prompt = f"""
作為一位情感音樂分析專家，請解析以下描述中的情緒元素，並將其轉換為具體的音樂參數：

"{description}"

請提供詳細的JSON格式分析，包含以下內容：
1. mood: 主要情感氛圍
2. secondary_mood: 次要情感氛圍（如有）
3. emotional_intensity: 情感強度（1-10）
4. emotional_variation: 情感變化程度（1-10）
5. tempo: 建議的速度值（BPM）
6. key: 建議的調性
7. time_signature: 建議的拍號
8. melodic_character: 旋律特性（如flowing, angular, repetitive等）
9. harmonic_complexity: 和聲複雜度（simple, moderate, complex）
10. rhythmic_features: 節奏特徵（如regular, syncopated, complex等）
11. dynamic_range: 力度變化範圍（narrow, moderate, wide）

請確保參數與描述中的情感表達完全匹配，並考慮不同情感之間的微妙關係。

只需返回JSON格式的結果，無需任何解釋文字。
"""
        
        # 呼叫LLM分析
        response = self._call_llm(prompt)
        
        # 嘗試解析JSON
        try:
            import re
            json_match = re.search(r'(\{.*\})', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(1))
                return result
            else:
                logger.warning("無法從情緒分析回應中提取JSON")
                return {}
        except Exception as e:
            logger.error(f"解析情緒分析結果時出錯: {str(e)}")
            return {}
    
    def _analyze_expression_techniques(self, description: str) -> Dict[str, Any]:
        """第三階段：分析表現技巧建議
        
        Args:
            description: 用戶描述
            
        Returns:
            Dict[str, Any]: 表現技巧分析結果
        """
        prompt = f"""
作為一位作曲和編曲專家，請根據以下音樂描述，提供專業的音樂表現技巧建議：

"{description}"

請提供詳細的JSON格式分析，包含以下內容：
1. harmony_suggestions: 和聲語言建議（如合適的和弦進行模式、替代和聲、調式互換建議等）的陣列
2. arrangement_techniques: 針對樂器編排的技巧建議（如聲部處理方法、特色演奏技巧等）的陣列
3. development_techniques: 主題發展技巧（如模進、反向、變奏等）和段落轉換處理方法的陣列
4. climax_building: 音樂高潮構建技巧
5. texture_techniques: 織體處理技巧（如複音、單音、賦格等）
6. special_effects: 特殊音效或技巧建議

請確保建議專業且具體，能夠直接應用於作曲和編曲過程。

只需返回JSON格式的結果，無需任何解釋文字。
"""
        
        # 呼叫LLM分析
        response = self._call_llm(prompt)
        
        # 嘗試解析JSON
        try:
            import re
            json_match = re.search(r'(\{.*\})', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(1))
                return result
            else:
                logger.warning("無法從表現技巧分析回應中提取JSON")
                return {}
        except Exception as e:
            logger.error(f"解析表現技巧分析結果時出錯: {str(e)}")
            return {}
    
    def _combine_analysis_results(self, description: str, narrative: Dict[str, Any], 
                                 emotion: Dict[str, Any], expression: Dict[str, Any]) -> MusicRequirement:
        """綜合三階段分析結果
        
        Args:
            description: 原始描述
            narrative: 敘事分析結果
            emotion: 情緒分析結果
            expression: 表現技巧分析結果
            
        Returns:
            MusicRequirement: 完整的音樂需求
        """
        # 創建基礎需求對象
        music_req = MusicRequirement(description=description)
        
        # 整合敘事分析結果
        if narrative:
            music_req.instruments = narrative.get("instruments", ["piano"])
            music_req.instrument_roles = narrative.get("instrument_roles", {"piano": "melody"})
            music_req.cultural_elements = narrative.get("cultural_elements", [])
            music_req.narrative_setting = narrative.get("narrative_setting")
            music_req.cultural_background = narrative.get("cultural_background")
            music_req.time_period = narrative.get("time_period")
            music_req.occasion = narrative.get("occasion")
            music_req.timbre_character = narrative.get("timbre_character")
            music_req.sound_layers = narrative.get("sound_layers", 3)
            music_req.spatial_character = narrative.get("spatial_character")
        
        # 整合情緒分析結果
        if emotion:
            music_req.genre = emotion.get("genre", music_req.genre)
            music_req.mood = emotion.get("mood", music_req.mood)
            music_req.tempo = emotion.get("tempo", music_req.tempo)
            music_req.key = emotion.get("key", music_req.key)
            music_req.time_signature = emotion.get("time_signature", music_req.time_signature)
            music_req.melodic_character = emotion.get("melodic_character", music_req.melodic_character)
            music_req.harmonic_complexity = emotion.get("harmonic_complexity", music_req.harmonic_complexity)
            music_req.rhythmic_features = emotion.get("rhythmic_features", music_req.rhythmic_features)
        
        # 整合表現技巧分析結果
        if expression:
            music_req.harmony_suggestions = expression.get("harmony_suggestions", [])
            music_req.arrangement_techniques = expression.get("arrangement_techniques", [])
            music_req.development_techniques = expression.get("development_techniques", [])
            music_req.techniques = expression.get("special_effects", music_req.techniques)
        
        # 判斷歌曲結構和完整性
        has_structure = set(["verse", "chorus", "bridge", "intro", "outro"]).intersection(
            set(emotion.get("form", "").lower().split("-")))
        if has_structure:
            music_req.has_intro = True
            music_req.has_outro = True
            music_req.has_bridge = True
            # 簡單的結構生成邏輯
            music_req.song_structure = ["intro", "verse", "chorus", "verse", "chorus", "bridge", "chorus", "outro"]
        
        return music_req
    
    def _call_llm(self, prompt: str) -> str:
        """呼叫大語言模型
        
        Args:
            prompt: 提示詞
            
        Returns:
            str: 模型回應
        """
        system_message = """你是一位世界級的音樂理論和音樂分析專家，擁有深厚的理論基礎和實踐經驗。
你能準確理解任何音樂描述和創作需求，並將其拆解成具體的音樂參數和元素。
你對各種音樂風格、文化背景和演奏技巧都有專業級的了解。
你的分析將幫助音樂創作者理解並實現他們的音樂願景。
你能夠識別出描述中的專業樂理知識，並確保它們被正確地轉換為具體參數。"""
        
        try:
            if self.provider_type == LLMProviderType.OPENAI:
                return self._call_openai(prompt, system_message)
            elif self.provider_type == LLMProviderType.LMSTUDIO:
                return self._call_lmstudio(prompt, system_message)
            elif self.provider_type == LLMProviderType.HUGGINGFACE:
                return self._call_huggingface(prompt, system_message)
            else:
                logger.error(f"不支持的LLM提供商類型: {self.provider_type}")
                return "{}"  # 返回空JSON對象
        except Exception as e:
            logger.error(f"呼叫LLM時發生錯誤: {str(e)}")
            return "{}"  # 返回空JSON對象
    
    def _call_openai(self, prompt: str, system_message: str) -> str:
        """呼叫OpenAI API
        
        Args:
            prompt: 提示詞
            system_message: 系統消息
            
        Returns:
            str: 模型回應
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.llm_api_key}"
        }
        
        payload = {
            "model": "gpt-4",  # 使用強大的模型進行參數解析
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,  # 使用較低的溫度以獲得更確定性的回應
            "max_tokens": 1024
        }
        
        response = requests.post(self.llm_api_url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        return result.get("choices", [{}])[0].get("message", {}).get("content", "")
    
    def _call_lmstudio(self, prompt: str, system_message: str) -> str:
        """呼叫LMStudio
        
        Args:
            prompt: 提示詞
            system_message: 系統消息
            
        Returns:
            str: 模型回應
        """
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,  # 使用較低的溫度以獲得更確定性的回應
            "max_tokens": 1024,
            "stream": False
        }
        
        response = requests.post(self.llm_api_url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        return result.get("choices", [{}])[0].get("message", {}).get("content", "")
    
    def _call_huggingface(self, prompt: str, system_message: str) -> str:
        """呼叫Hugging Face API
        
        Args:
            prompt: 提示詞
            system_message: 系統消息
            
        Returns:
            str: 模型回應
        """
        headers = {
            "Authorization": f"Bearer {self.llm_api_key}",
            "Content-Type": "application/json"
        }
        
        # 嘗試更簡單的請求格式
        try:
            # 標準格式
            payload = {
                "inputs": f"{system_message}\n\n{prompt}",
                "parameters": {
                    "max_new_tokens": 1024,
                    "temperature": 0.3,
                    "return_full_text": False
                }
            }
            
            response = requests.post(self.llm_api_url, headers=headers, json=payload)
            
            if response.status_code != 200:
                # 如果標準格式失敗，嘗試簡化格式
                logger.info(f"嘗試簡化請求格式")
                simple_payload = {
                    "inputs": f"{system_message}\n\n{prompt}"
                }
                response = requests.post(self.llm_api_url, headers=headers, json=simple_payload)
            
            response.raise_for_status()
            
            result = response.json()
            
            # 根據返回格式解析
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', '')
            elif isinstance(result, dict):
                return result.get('generated_text', '')
            else:
                return str(result)
                
        except Exception as e:
            logger.error(f"Hugging Face API調用錯誤: {str(e)}")
            logger.error(f"請確保API密鑰正確並且有訪問權限")
            # 返回出錯信息，便於後續分析
            return f"""{{
                "error": "API調用失敗: {str(e)}",
                "suggestion": "請檢查API密鑰和模型權限"
            }}"""

    def _simulate_llm_response(self, description: str) -> MusicRequirement:
        """模擬LLM響應，在API調用失敗時使用
        
        Args:
            description: 用戶描述
            
        Returns:
            MusicRequirement: 生成的音樂需求
        """
        logger.info("使用模擬LLM響應生成音樂需求")
        
        # 創建基礎需求對象
        music_req = MusicRequirement(description=description)
        
        # 提取關鍵詞
        description_lower = description.lower()
        
        # 設置風格
        if "中國" in description_lower or "古箏" in description_lower or "笛子" in description_lower:
            music_req.genre = "中國傳統"
            music_req.cultural_elements = ["Chinese"]
            music_req.cultural_background = "中國傳統文化"
        elif "爵士" in description_lower:
            music_req.genre = "爵士"
        elif "古典" in description_lower:
            music_req.genre = "古典"
        elif "搖滾" in description_lower:
            music_req.genre = "搖滾"
        elif "電子" in description_lower:
            music_req.genre = "電子"
        else:
            # 默認為古典
            music_req.genre = "古典"
        
        # 設置情感
        if "平靜" in description_lower or "沉靜" in description_lower or "寧靜" in description_lower:
            music_req.mood = "平靜"
        elif "快樂" in description_lower or "歡快" in description_lower:
            music_req.mood = "快樂"
        elif "悲傷" in description_lower or "憂傷" in description_lower:
            music_req.mood = "悲傷"
        elif "激昂" in description_lower or "熱情" in description_lower:
            music_req.mood = "激動"
        else:
            music_req.mood = "平靜"  # 默認為平靜
        
        # 設置速度
        if "快" in description_lower:
            music_req.tempo = 120
        elif "慢" in description_lower:
            music_req.tempo = 70
        else:
            # 根據情感設置默認速度
            if music_req.mood == "平靜":
                music_req.tempo = 75
            elif music_req.mood == "快樂":
                music_req.tempo = 110
            elif music_req.mood == "悲傷":
                music_req.tempo = 65
            elif music_req.mood == "激動":
                music_req.tempo = 130
            else:
                music_req.tempo = 90  # 完全默認值
        
        # 設置樂器
        if "鋼琴" in description_lower:
            music_req.instruments = ["piano"]
            music_req.instrument_roles = {"piano": "melody"}
        elif "吉他" in description_lower:
            music_req.instruments = ["guitar"]
            music_req.instrument_roles = {"guitar": "melody"}
        elif "管弦樂" in description_lower or "交響樂" in description_lower:
            music_req.instruments = ["violin", "cello", "flute", "french_horn", "piano"]
            music_req.instrument_roles = {
                "violin": "melody",
                "cello": "bass",
                "flute": "harmony",
                "french_horn": "harmony",
                "piano": "harmony"
            }
        elif "中國" in description_lower:
            music_req.instruments = ["guzheng", "dizi", "erhu", "pipa"]
            music_req.instrument_roles = {
                "guzheng": "melody",
                "dizi": "harmony",
                "erhu": "melody",
                "pipa": "harmony"
            }
        elif "爵士" in description_lower:
            music_req.instruments = ["piano", "saxophone", "bass", "drums"]
            music_req.instrument_roles = {
                "piano": "harmony",
                "saxophone": "melody",
                "bass": "bass",
                "drums": "percussion"
            }
        else:
            # 默認使用鋼琴
            music_req.instruments = ["piano"]
            music_req.instrument_roles = {"piano": "melody"}
        
        # 場景和音色設置
        if "茶館" in description_lower or "茶室" in description_lower:
            music_req.narrative_setting = "傳統茶館"
            music_req.occasion = "茶館/茶室背景音樂"
            music_req.timbre_character = "溫暖、明亮"
            music_req.spatial_character = "親密、包圍感"
        elif "電影" in description_lower:
            music_req.narrative_setting = "電影場景"
            music_req.occasion = "電影配樂"
            music_req.timbre_character = "豐富、層次感強"
            music_req.spatial_character = "寬廣、有深度"
        elif "遊戲" in description_lower:
            music_req.narrative_setting = "遊戲場景"
            music_req.occasion = "遊戲背景音樂"
            music_req.timbre_character = "清晰、動態範圍大"
            music_req.spatial_character = "環繞感、沉浸式"
        else:
            # 默認
            music_req.narrative_setting = "一般聆聽場景"
            music_req.occasion = "個人聆聽"
            music_req.timbre_character = "自然、平衡"
            music_req.spatial_character = "適中"
        
        # 設置音樂理論參數
        music_req.melodic_character = "flowing" if music_req.mood in ["平靜", "悲傷"] else "rhythmic"
        music_req.harmonic_complexity = "simple" if music_req.genre in ["流行", "電子"] else "moderate"
        music_req.rhythmic_features = "regular" if music_req.mood in ["平靜"] else "varied"
        
        # 設置表現技巧建議
        if music_req.genre == "中國傳統":
            music_req.harmony_suggestions = ["五聲音階和聲", "空五度與四度和聲", "平行四度進行"]
            music_req.arrangement_techniques = ["傳統音色模仿", "裝飾音和滑音運用", "主副旋律交替"]
            music_req.development_techniques = ["主題變奏", "引子-主題-尾聲結構", "循環式發展"]
        elif music_req.genre == "古典":
            music_req.harmony_suggestions = ["功能和聲進行", "屬七和弦使用", "二級副屬和弦"]
            music_req.arrangement_techniques = ["對比式器樂編配", "主副旋律協作", "聲部獨立性"]
            music_req.development_techniques = ["動機發展", "模進", "主題與變奏"]
        elif music_req.genre == "爵士":
            music_req.harmony_suggestions = ["七和弦與九和弦", "替代和聲", "藍調進行"]
            music_req.arrangement_techniques = ["即興風格演奏", "走音低音", "切分節奏演奏"]
            music_req.development_techniques = ["主題-獨奏-主題結構", "呼應式發展", "藍調十二小節"]
        
        # 設置歌曲結構
        if "完整" in description_lower:
            music_req.has_intro = True
            music_req.has_outro = True
            music_req.has_bridge = True
            music_req.song_structure = ["intro", "verse", "chorus", "verse", "chorus", "bridge", "chorus", "outro"]
        else:
            # 簡單的AB結構
            music_req.song_structure = ["A", "B", "A"]
        
        # 返回模擬的音樂需求
        return music_req


# 測試代碼
if __name__ == "__main__":
    # 設置日誌級別
    logging.basicConfig(level=logging.INFO)
    
    # 從環境變量獲取設置
    llm_service = os.environ.get("LLM_SERVICE", "huggingface").lower()
    
    # 根據所選服務設置參數
    if llm_service == "openai":
        llm_api_key = os.environ.get("OPENAI_API_KEY")
        llm_api_url = "https://api.openai.com/v1/chat/completions"
        provider = LLMProviderType.OPENAI
    elif llm_service == "lmstudio":
        llm_api_key = None
        llm_api_url = "http://localhost:1234/v1/chat/completions"
        provider = LLMProviderType.LMSTUDIO
    else:  # 默認使用huggingface
        llm_api_key = os.environ.get("HF_API_KEY")
        llm_api_url = os.environ.get("HF_API_URL")
        provider = LLMProviderType.HUGGINGFACE
    
    # 創建需求分析器
    analyzer = MusicRequirementAnalyzer(
        llm_api_key=llm_api_key,
        llm_api_url=llm_api_url,
        provider_type=provider
    )
    
    # 測試分析功能
    test_descriptions = [
        "創造一段悠揚的小提琴旋律，帶有中國風的意境",
        "我想要一段輕快的爵士鋼琴，適合咖啡廳播放",
        "幫我創作一首電子舞曲，具有強烈的節奏感和現代感",
        "我想要一首C大調、4/4拍的古典風格鋼琴小品，速度為120BPM，有AABA的結構",
        "創作一首具有完整性的搖滾歌曲，包含前奏、主歌、副歌、橋段和尾聲，使用小調和屬七和弦"
    ]
    
    for desc in test_descriptions:
        print(f"\n分析音樂需求: {desc}")
        req = analyzer.analyze_music_requirement(desc)
        print("分析結果:")
        print(json.dumps(req.to_dict(), indent=2, ensure_ascii=False)) 