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
    OLLAMA = "ollama"
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
    techniques: List[str] = None  # 演奏技巧
    
    # 旋律參數
    melodic_character: str = "flowing"  # 旋律特性
    harmonic_complexity: str = "moderate"  # 和聲複雜度
    rhythmic_features: str = "regular"  # 節奏特徵
    
    def __post_init__(self):
        # 初始化可能的None值
        if self.cultural_elements is None:
            self.cultural_elements = []
        if self.instruments is None:
            self.instruments = ["piano"]
        if self.techniques is None:
            self.techniques = []
    
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
            "techniques": self.techniques,
            "melodic_character": self.melodic_character,
            "harmonic_complexity": self.harmonic_complexity,
            "rhythmic_features": self.rhythmic_features
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
                provider_type: LLMProviderType = LLMProviderType.OLLAMA):
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
            elif provider_type == LLMProviderType.OLLAMA:
                self.llm_api_url = "http://localhost:11434/api/generate"
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
        
        # 先從描述中提取明確指定的樂理參數
        extracted_params = self._extract_explicit_parameters(description)
        logger.info(f"從描述中提取的明確參數: {extracted_params}")
        
        # 構建提示詞，告訴LLM哪些參數已經確定
        prompt = self._build_analysis_prompt(description, extracted_params)
        
        # 呼叫LLM
        response = self._call_llm(prompt)
        
        # 解析響應
        music_req = self._parse_analysis_response(response, description)
        
        # 合併明確提取的參數和LLM生成的參數，以明確提取的為準
        for key, value in extracted_params.items():
            if value is not None:
                setattr(music_req, key, value)
        
        return music_req
    
    def _extract_explicit_parameters(self, description: str) -> Dict[str, Any]:
        """從描述中提取明確指定的樂理參數
        
        Args:
            description: 用戶的音樂創作需求描述
            
        Returns:
            Dict[str, Any]: 提取的參數字典
        """
        import re
        
        # 初始化參數字典
        params = {
            "key": None,          # 調性
            "tempo": None,        # 速度
            "time_signature": None, # 拍號
            "genre": None,        # 風格
            "instruments": None,  # 樂器
            "duration": None      # 持續時間
        }
        
        # 提取調性
        # 例如: "C調", "降B大調", "A小調", "F#小調"
        key_pattern = r'([ABCDEFG](?:#|b|升|降)?)\s*(大|小|major|minor|maj|min)?調'
        key_match = re.search(key_pattern, description, re.IGNORECASE)
        if key_match:
            key_name = key_match.group(1)
            key_type = key_match.group(2) if key_match.group(2) else "major"
            
            # 轉換中文符號為英文符號
            key_name = key_name.replace('升', '#').replace('降', 'b')
            
            # 轉換中文大小調為英文
            if key_type in ["小", "minor", "min"]:
                key = f"{key_name} minor"
            else:
                key = key_name
                
            params["key"] = key
        
        # 提取速度
        # 例如: "120BPM", "速度為90", "速度90", "90拍每分鐘"
        tempo_pattern = r'(\d+)\s*(BPM|bpm|拍每分鐘|每分鐘|速度)'
        tempo_match = re.search(tempo_pattern, description)
        if tempo_match:
            params["tempo"] = int(tempo_match.group(1))
        
        # 提取拍號
        # 例如: "4/4拍", "3/4拍子", "拍號為6/8"
        time_sig_pattern = r'(\d+)/(\d+)\s*(拍|拍子|節拍|拍號)'
        time_sig_match = re.search(time_sig_pattern, description)
        if time_sig_match:
            params["time_signature"] = f"{time_sig_match.group(1)}/{time_sig_match.group(2)}"
        
        # 提取風格
        # 常見音樂風格關鍵詞
        genres = {
            "古典": "classical", "古典樂": "classical", "古典音樂": "classical",
            "爵士": "jazz", "爵士樂": "jazz",
            "搖滾": "rock", "搖滾樂": "rock",
            "流行": "pop", "流行樂": "pop",
            "電子": "electronic", "電子樂": "electronic",
            "民謠": "folk", "民謠音樂": "folk",
            "藍調": "blues", "藍調音樂": "blues",
            "嘻哈": "hip hop", "說唱": "hip hop",
            "鄉村": "country", "鄉村音樂": "country",
            "R&B": "r&b", "節奏藍調": "r&b",
            "拉丁": "latin", "拉丁音樂": "latin",
            "reggae": "reggae", "雷鬼": "reggae",
            "funk": "funk", "放克": "funk",
            "金屬": "metal", "重金屬": "metal",
            "disco": "disco", "迪斯科": "disco",
            "舞曲": "dance", "舞蹈音樂": "dance"
        }
        
        for zh_genre, en_genre in genres.items():
            if zh_genre in description:
                params["genre"] = en_genre
                break
        
        # 提取樂器
        # 常見樂器列表
        instruments = {
            "鋼琴": "piano", "電鋼琴": "electric piano", 
            "吉他": "guitar", "電吉他": "electric guitar", "木吉他": "acoustic guitar",
            "小提琴": "violin", "中提琴": "viola", "大提琴": "cello", "低音提琴": "bass",
            "長笛": "flute", "短笛": "piccolo", "單簧管": "clarinet", "雙簧管": "oboe",
            "薩克斯風": "saxophone", "薩克斯": "saxophone",
            "小號": "trumpet", "長號": "trombone", "法國號": "french horn", "大號": "tuba",
            "鼓": "drums", "架子鼓": "drums", "打擊樂": "percussion",
            "合成器": "synthesizer", "電子琴": "synthesizer",
            "bass": "bass", "貝斯": "bass",
            "鋼片琴": "vibraphone", "木琴": "xylophone", "馬林巴": "marimba",
            "豎琴": "harp", "手風琴": "accordion",
            "琵琶": "pipa", "古箏": "guzheng", "二胡": "erhu"
        }
        
        extracted_instruments = []
        for zh_inst, en_inst in instruments.items():
            if zh_inst in description:
                extracted_instruments.append(en_inst)
        
        if extracted_instruments:
            params["instruments"] = extracted_instruments
        
        # 提取持續時間
        # 例如: "2分鐘", "30秒", "1分30秒"
        duration_pattern = r'(\d+)\s*(分鐘|分|min|minute|minutes)'
        duration_match = re.search(duration_pattern, description)
        if duration_match:
            minutes = int(duration_match.group(1))
            params["duration"] = minutes * 60  # 轉換為秒
        
        sec_pattern = r'(\d+)\s*(秒鐘|秒|s|second|seconds)'
        sec_match = re.search(sec_pattern, description)
        if sec_match:
            if params["duration"] is not None:  # 已經有分鐘
                params["duration"] += int(sec_match.group(1))
            else:
                params["duration"] = int(sec_match.group(1))
        
        return params
    
    def _build_analysis_prompt(self, description: str, extracted_params: Dict[str, Any] = None) -> str:
        """構建分析提示詞
        
        Args:
            description: 用戶的音樂創作需求描述
            extracted_params: 從描述中提取的明確參數
            
        Returns:
            str: 提示詞
        """
        # 如果沒有提供提取的參數，使用空字典
        extracted_params = extracted_params or {}
        
        # 構建提示詞基本部分
        prompt = f"""
作為一位音樂理論和作曲專家，請深入分析並拆解以下音樂創作需求:

"{description}"

請提取所有重要的音樂元素和參數，並以JSON格式回應，包含以下欄位:
"""
        
        # 添加已經提取的參數信息
        if any(v is not None for v in extracted_params.values()):
            prompt += "\n根據分析，以下參數已經明確確定:\n"
            
            if extracted_params.get("key"):
                prompt += f"- key: \"{extracted_params['key']}\" (已確定)\n"
            
            if extracted_params.get("tempo"):
                prompt += f"- tempo: {extracted_params['tempo']} (已確定)\n"
            
            if extracted_params.get("time_signature"):
                prompt += f"- time_signature: \"{extracted_params['time_signature']}\" (已確定)\n"
            
            if extracted_params.get("genre"):
                prompt += f"- genre: \"{extracted_params['genre']}\" (已確定)\n"
            
            if extracted_params.get("instruments"):
                instruments_str = ", ".join([f'"{inst}"' for inst in extracted_params['instruments']])
                prompt += f"- instruments: [{instruments_str}] (已確定)\n"
            
            if extracted_params.get("duration"):
                prompt += f"- duration: {extracted_params['duration']} (已確定)\n"
            
            prompt += "\n請在保留上述確定參數的前提下，分析其他參數:\n"
        
        # 添加所有可能的參數欄位
        prompt += """
- genre: 音樂風格 (如classical, jazz, pop, rock, electronic, folk等)
- mood: 情感氛圍 (如happy, sad, energetic, calm, mysterious, tense等)
- tempo: 建議的速度值 (BPM數值，如60-180)
- key: 建議的調性 (如C, D, A minor等)
- time_signature: 建議的拍號 (如4/4, 3/4, 6/8等)
- form: 曲式結構 (如binary, ternary, verse-chorus, sonata, theme and variations等)
- duration: 建議的曲目長度 (單位為秒，如30-300)
- section_count: 建議的段落數量 (如2-5)
- cultural_elements: 文化元素 (陣列，如["Chinese", "Middle Eastern"]等)
- instruments: 建議的樂器 (陣列，如["piano", "violin", "cello"]等)
- techniques: 建議的演奏技巧 (陣列，如["tremolo", "pizzicato", "legato"]等)
- melodic_character: 旋律特性 (如flowing, angular, repetitive, varied等)
- harmonic_complexity: 和聲複雜度 (如simple, moderate, complex等)
- rhythmic_features: 節奏特徵 (如regular, syncopated, complex等)

請確保拆解全面而準確，考慮用戶描述中暗示的所有音樂特徵和風格元素。你的分析將被用來指導後續的音樂創作過程。

只需返回JSON格式的結果，無需任何其他解釋文字。
"""
        return prompt
    
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
你的分析將幫助音樂創作者理解並實現他們的音樂願景。"""
        
        try:
            if self.provider_type == LLMProviderType.OLLAMA:
                return self._call_ollama(prompt, system_message)
            elif self.provider_type == LLMProviderType.OPENAI:
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
    
    def _call_ollama(self, prompt: str, system_message: str) -> str:
        """呼叫Ollama
        
        Args:
            prompt: 提示詞
            system_message: 系統消息
            
        Returns:
            str: 模型回應
        """
        model_name = os.environ.get("OLLAMA_MODEL", "llama3")  # 默認使用llama3
        
        payload = {
            "model": model_name,
            "prompt": f"{system_message}\n\n{prompt}",
            "stream": False,
            "options": {
                "temperature": 0.3,  # 使用較低的溫度以獲得更確定性的回應
                "num_predict": 2048
            }
        }
        
        response = requests.post(self.llm_api_url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        return result.get("response", "")
    
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
        
        payload = {
            "inputs": f"{system_message}\n\n{prompt}",
            "parameters": {
                "max_new_tokens": 1024,
                "temperature": 0.3,  # 使用較低的溫度以獲得更確定性的回應
                "return_full_text": False
            }
        }
        
        response = requests.post(self.llm_api_url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        # 根據返回格式解析
        if isinstance(result, list) and len(result) > 0:
            return result[0].get('generated_text', '')
        elif isinstance(result, dict):
            return result.get('generated_text', '')
        else:
            return ""
    
    def _parse_analysis_response(self, response: str, original_description: str) -> MusicRequirement:
        """解析分析回應
        
        Args:
            response: LLM回應
            original_description: 原始描述
            
        Returns:
            MusicRequirement: 解析後的音樂需求參數
        """
        try:
            # 嘗試提取JSON部分
            import re
            
            # 查找JSON對象
            json_match = re.search(r'(\{.*\})', response, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
                json_data = json.loads(json_str)
                
                # 添加原始描述
                json_data["description"] = original_description
                
                # 如果沒有指定樂器但有指定風格，則根據風格推薦樂器
                if not json_data.get("instruments") and json_data.get("genre"):
                    json_data["instruments"] = self.recommend_instruments_for_genre(json_data["genre"])
                
                # 創建MusicRequirement對象
                return MusicRequirement.from_dict(json_data)
                
            else:
                logger.warning("無法從回應中提取JSON，使用默認參數")
                
        except Exception as e:
            logger.error(f"解析分析回應時出錯: {str(e)}\n回應: {response}")
        
        # 如果解析失敗，返回默認參數
        return MusicRequirement(description=original_description)
    
    def recommend_instruments_for_genre(self, genre: str) -> List[str]:
        """根據音樂風格推薦合適的樂器配置
        
        使用LLM來推薦適合特定音樂風格的樂器組合
        
        Args:
            genre: 音樂風格
            
        Returns:
            List[str]: 推薦的樂器列表
        """
        prompt = f"""作為專業音樂家和編曲專家，請推薦最適合"{genre}"風格的5-8種樂器。
請只回傳一個樂器名稱的JSON數組，格式如下：
["樂器1", "樂器2", "樂器3", ...]

請確保使用標準英文樂器名稱（如piano, violin, drums等），不要包含任何解釋或額外文字。"""
        
        try:
            # 呼叫LLM獲取推薦
            response = self._call_llm(prompt)
            
            # 解析回應中的JSON數組
            import re
            json_match = re.search(r'(\[.*\])', response, re.DOTALL)
            
            if json_match:
                instruments = json.loads(json_match.group(1))
                logger.info(f"為{genre}風格推薦的樂器: {instruments}")
                return instruments
                
        except Exception as e:
            logger.error(f"推薦樂器時出錯: {str(e)}")
        
        # 如果出錯或無法獲取推薦，返回默認樂器配置
        default_instruments = {
            "classical": ["piano", "violin", "cello", "flute"],
            "jazz": ["piano", "saxophone", "double bass", "drums"],
            "rock": ["electric guitar", "bass", "drums", "keyboards"],
            "pop": ["piano", "guitar", "bass", "drums", "synthesizer"],
            "electronic": ["synthesizer", "drums", "bass", "sampler"],
            "folk": ["acoustic guitar", "violin", "mandolin", "harmonica"],
            "chinese": ["erhu", "guzheng", "pipa", "dizi"],
            "japanese": ["koto", "shamisen", "shakuhachi", "taiko"],
            "indian": ["sitar", "tabla", "bansuri", "tanpura"]
        }
        
        # 嘗試匹配最接近的風格
        genre_lower = genre.lower()
        for key in default_instruments:
            if key in genre_lower:
                return default_instruments[key]
        
        # 如果沒有匹配到任何風格，返回默認樂器
        return ["piano"]


# 測試代碼
if __name__ == "__main__":
    # 設置日誌級別
    logging.basicConfig(level=logging.INFO)
    
    # 從環境變量獲取設置
    llm_service = os.environ.get("LLM_SERVICE", "ollama").lower()
    
    # 根據所選服務設置參數
    if llm_service == "openai":
        llm_api_key = os.environ.get("OPENAI_API_KEY")
        llm_api_url = "https://api.openai.com/v1/chat/completions"
        provider = LLMProviderType.OPENAI
    elif llm_service == "huggingface" or llm_service == "hf":
        llm_api_key = os.environ.get("HF_API_KEY")
        llm_api_url = os.environ.get("HF_API_URL")
        provider = LLMProviderType.HUGGINGFACE
    elif llm_service == "lmstudio":
        llm_api_key = None
        llm_api_url = "http://localhost:1234/v1/chat/completions"
        provider = LLMProviderType.LMSTUDIO
    else:  # 默認使用ollama
        llm_api_key = None
        llm_api_url = "http://localhost:11434/api/generate"
        provider = LLMProviderType.OLLAMA
    
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
        "幫我創作一首電子舞曲，具有強烈的節奏感和現代感"
    ]
    
    for desc in test_descriptions:
        print(f"\n分析音樂需求: {desc}")
        req = analyzer.analyze_music_requirement(desc)
        print("分析結果:")
        print(json.dumps(req.to_dict(), indent=2, ensure_ascii=False)) 