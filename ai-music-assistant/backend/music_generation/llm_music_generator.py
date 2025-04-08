"""LLM音樂生成器

透過大語言模型直接生成音樂內容，而非僅用於生成參數
"""

import os
import logging
import json
import requests
import base64
import tempfile
from typing import Dict, Any, List, Optional, Tuple, Union
from enum import Enum
from dataclasses import dataclass

import numpy as np

# 嘗試導入 MCP 相關模組
try:
    from mcp.mcp_schema import MusicParameters, Note, MelodyInput, Genre
except ImportError:
    try:
        from backend.mcp.mcp_schema import MusicParameters, Note, MelodyInput, Genre
    except ImportError:
        # 如果導入失敗，創建簡單的替代類
        logger = logging.getLogger(__name__)
        logger.warning("無法導入任何MCP模塊，使用內置替代類")
                
        class Genre:
            POP = "pop"
            ROCK = "rock"
            JAZZ = "jazz"
            CLASSICAL = "classical"
            ELECTRONIC = "electronic"
            BLUES = "blues"
            COUNTRY = "country"
        
        class Note:
            def __init__(self, pitch=0, start_time=0, duration=0, velocity=0):
                self.pitch = pitch
                self.start_time = start_time
                self.duration = duration
                self.velocity = velocity
                
        class MelodyInput:
            def __init__(self, notes=None):
                self.notes = notes or []
                
        class MusicParameters:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)

# 配置日誌
logger = logging.getLogger(__name__)

@dataclass
class LLMGenerationConfig:
    """LLM生成配置"""
    temperature: float = 0.7
    max_tokens: int = 2048
    model_name: str = "default"
    prompt_template: str = ""
    system_message: str = """你是一位世界級的音樂編曲大師，擁有數十年的專業作曲和編曲經驗。
你精通各種音樂風格、音樂理論和編曲技巧，曾為無數成功音樂作品提供創作。
你能夠創作出結構完整、情感豐富且具有專業品質的完整樂曲，而不僅僅是簡短的音樂片段。
你對旋律發展、和聲進行、音樂結構和樂器編配都有深刻的理解。
無論接收到什麼樣的音樂創作需求，你都能輸出完整的、專業水準的、可演奏的音樂內容。"""


class LLMProviderType(Enum):
    """LLM提供商類型"""
    OPENAI = "openai"
    OLLAMA = "ollama"
    LMSTUDIO = "lmstudio"
    HUGGINGFACE = "huggingface"


class LLMMusicGenerator:
    """大語言模型音樂生成器
    
    直接利用大語言模型生成音樂內容，不僅僅是生成參數
    """
    
    def __init__(self, 
                llm_api_key: Optional[str] = None, 
                llm_api_url: Optional[str] = None,
                provider_type: LLMProviderType = LLMProviderType.OLLAMA,
                config: Optional[LLMGenerationConfig] = None):
        """初始化LLM音樂生成器
        
        Args:
            llm_api_key: 大語言模型API密鑰
            llm_api_url: 大語言模型API端點
            provider_type: 提供商類型
            config: 生成配置
        """
        self.llm_api_key = llm_api_key
        self.llm_api_url = llm_api_url
        self.provider_type = provider_type
        self.config = config or LLMGenerationConfig()
        
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
        
        logger.info(f"初始化LLM音樂生成器，提供商: {provider_type.value}")
    
    def generate_melody_representation(self, 
                                      description: str, 
                                      parameters: MusicParameters) -> List[Dict[str, Any]]:
        """生成旋律的JSON表示
        
        使用LLM生成旋律的JSON表示，包含音高、時值、力度等信息
        
        Args:
            description: 音樂描述
            parameters: 音樂參數
            
        Returns:
            List[Dict[str, Any]]: 旋律的JSON表示
        """
        logger.info(f"使用LLM生成旋律表示: {description}")
        
        # 構建提示詞
        prompt = self._build_melody_generation_prompt(description, parameters)
        
        # 呼叫LLM
        response = self._call_llm(prompt)
        
        # 解析響應
        melody_data = self._parse_melody_response(response)
        
        return melody_data
    
    def generate_melody(self, 
                       description: str, 
                       parameters: MusicParameters) -> List[Note]:
        """生成旋律
        
        使用LLM生成旋律，並轉換為Note對象列表
        
        Args:
            description: 音樂描述
            parameters: 音樂參數
            
        Returns:
            List[Note]: 生成的旋律音符列表
        """
        # 獲取旋律的JSON表示
        melody_data = self.generate_melody_representation(description, parameters)
        
        # 轉換為Note對象
        notes = []
        for note_data in melody_data:
            note = Note(
                pitch=note_data.get('pitch', 60),
                start_time=note_data.get('start_time', 0.0),
                duration=note_data.get('duration', 0.5),
                velocity=note_data.get('velocity', 80)
            )
            notes.append(note)
        
        return notes
    
    def generate_chord_progression(self, 
                                 description: str, 
                                 parameters: MusicParameters,
                                 melody: Optional[List[Note]] = None) -> List[Dict[str, Any]]:
        """生成和弦進行
        
        使用LLM生成和弦進行
        
        Args:
            description: 音樂描述
            parameters: 音樂參數
            melody: 可選的旋律，用於生成匹配旋律的和弦
            
        Returns:
            List[Dict[str, Any]]: 和弦進行，每個和弦包含名稱、開始時間、持續時間等
        """
        logger.info(f"使用LLM生成和弦進行: {description}")
        
        # 構建提示詞
        prompt = self._build_chord_progression_prompt(description, parameters, melody)
        
        # 呼叫LLM
        response = self._call_llm(prompt)
        
        # 解析響應
        chord_data = self._parse_chord_response(response)
        
        return chord_data
    
    def generate_arrangement_plan(self,
                                description: str,
                                parameters: MusicParameters) -> Dict[str, Any]:
        """生成編曲計劃
        
        由LLM提供完整的編曲計劃，包括樂器選擇、各聲部設計等
        
        Args:
            description: 音樂描述
            parameters: 音樂參數
            
        Returns:
            Dict[str, Any]: 編曲計劃
        """
        logger.info(f"使用LLM生成編曲計劃: {description}")
        
        # 確保樂器列表不為空
        if not hasattr(parameters, "instruments") or not parameters.instruments:
            genre = getattr(parameters, "genre", "")
            if genre:
                instruments = self.recommend_instruments_for_genre(genre)
                setattr(parameters, "instruments", instruments)
                logger.info(f"根據風格'{genre}'自動推薦的樂器: {instruments}")
        
        # 構建提示詞
        prompt = self._build_arrangement_prompt(description, parameters)
        
        # 呼叫LLM
        response = self._call_llm(prompt)
        
        # 解析響應
        arrangement_plan = self._parse_arrangement_response(response)
        
        return arrangement_plan
    
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
            "classical": ["piano", "violin", "cello", "flute", "clarinet"],
            "jazz": ["piano", "saxophone", "double bass", "drums", "trumpet"],
            "rock": ["electric guitar", "bass", "drums", "keyboards", "vocals"],
            "pop": ["piano", "guitar", "bass", "drums", "synthesizer"],
            "electronic": ["synthesizer", "drums", "bass", "sampler", "pad"],
            "folk": ["acoustic guitar", "violin", "mandolin", "harmonica", "banjo"],
            "chinese": ["erhu", "guzheng", "pipa", "dizi", "yangqin"],
            "japanese": ["koto", "shamisen", "shakuhachi", "taiko", "biwa"],
            "indian": ["sitar", "tabla", "bansuri", "tanpura", "sarod"],
            "arabic": ["oud", "qanun", "ney", "darbuka", "riq"],
            "african": ["djembe", "kora", "talking drum", "balafon", "shekere"],
            "latin": ["classical guitar", "bongos", "congas", "maracas", "trumpet"]
        }
        
        # 嘗試匹配最接近的風格
        genre_lower = genre.lower()
        for key in default_instruments:
            if key in genre_lower:
                return default_instruments[key]
        
        # 如果沒有匹配到任何風格，返回默認樂器
        return ["piano", "guitar", "bass", "drums"]
    
    def _build_melody_generation_prompt(self, 
                                      description: str, 
                                      parameters: MusicParameters) -> str:
        """構建旋律生成提示詞
        
        Args:
            description: 音樂描述
            parameters: 音樂參數
            
        Returns:
            str: 提示詞
        """
        # 提取參數
        tempo = getattr(parameters, 'tempo', 120)
        key = getattr(parameters, 'key', 'C')
        genre = getattr(parameters, 'genre', 'pop')
        
        # 構建基礎提示詞
        prompt = f"""
請為以下音樂描述生成一段完整的旋律的JSON表示:

音樂描述: {description}
速度(BPM): {tempo}
調性: {key}
風格: {genre}

請使用以下JSON格式表示旋律，其中每個音符包含音高、開始時間、持續時間和力度:

[
  {{
    "pitch": 60, // 代表C4的MIDI音高
    "start_time": 0.0, // 以秒為單位的開始時間
    "duration": 0.5, // 以秒為單位的持續時間
    "velocity": 80 // 力度，範圍0-127
  }},
  ...
]

生成的旋律應該:
1. 符合{key}調性
2. 具有{genre}風格的特點
3. 表達"{description}"所描述的情感和氛圍
4. 音符時間精確且實際可演奏
5. 總長度在30-60秒之間，包含足夠數量的音符（至少50個音符）
6. 具有完整的音樂結構，包括引入部分、主題部分、發展部分和結束部分
7. 包含適當的旋律發展、音樂動機和變化，不僅僅是簡單重複的片段
8. 考慮音樂張力的起伏變化，創造有趣的音樂旅程

只需返回JSON格式的旋律，不要有任何其他文字說明。
"""
        return prompt
    
    def _build_chord_progression_prompt(self,
                                      description: str,
                                      parameters: MusicParameters,
                                      melody: Optional[List[Note]] = None) -> str:
        """構建和弦進行生成提示詞
        
        Args:
            description: 音樂描述
            parameters: 音樂參數
            melody: 可選的旋律，用於生成匹配的和弦
            
        Returns:
            str: 提示詞
        """
        # 提取參數
        tempo = getattr(parameters, 'tempo', 120)
        key = getattr(parameters, 'key', 'C')
        genre = getattr(parameters, 'genre', 'pop')
        
        # 構建基礎提示詞
        prompt = f"""
請為以下音樂描述生成一組完整的和弦進行:

音樂描述: {description}
速度(BPM): {tempo}
調性: {key}
風格: {genre}

請使用以下JSON格式表示和弦進行:

[
  {{
    "chord_name": "C", // 和弦名稱
    "start_time": 0.0, // 以秒為單位的開始時間
    "duration": 2.0, // 以秒為單位的持續時間
    "notes": [60, 64, 67] // 和弦中的MIDI音符
  }},
  ...
]

"""
        # 如果提供了旋律，添加旋律信息
        if melody and len(melody) > 0:
            # 轉換旋律為簡化的JSON表示
            melody_json = []
            for note in melody:
                melody_json.append({
                    "pitch": note.pitch,
                    "start_time": note.start_time,
                    "duration": note.duration
                })
            
            # 添加旋律信息到提示詞
            prompt += f"""
以下是需要匹配的旋律:
{json.dumps(melody_json[:10], indent=2)}
{'...' if len(melody_json) > 10 else ''}

請確保和弦進行與上述旋律相匹配，支持旋律的發展和情感變化。
"""

        # 添加具體要求
        prompt += f"""
生成的和弦進行應該:
1. 和聲上符合{key}調性
2. 風格上匹配{genre}類型音樂的和聲特點
3. 表達"{description}"描述的情感和氛圍
4. 使用豐富多樣的和弦，包括各種和弦類型（大三和弦、小三和弦、七和弦、九和弦等）
5. 創建有效的和聲張力與釋放，包括不同的和弦級數（如I級、IV級、V級、ii級等）
6. 和弦進行應覆蓋整個樂曲長度，至少30-60秒
7. 包含清晰的和聲節奏，每個和弦的持續時間應該有所變化，以創造音樂感
8. 考慮和弦之間的平滑連接，使用適當的和弦進行技巧（如共同音、半音進行等）
9. 在關鍵的音樂段落轉折處使用適當的和弦變化

只需返回JSON格式的和弦進行，不要有任何其他文字說明。
"""
        return prompt
    
    def _build_arrangement_prompt(self,
                                description: str,
                                parameters: MusicParameters) -> str:
        """構建編曲計劃生成提示詞
        
        Args:
            description: 音樂描述
            parameters: 音樂參數
            
        Returns:
            str: 提示詞
        """
        # 提取參數
        tempo = getattr(parameters, 'tempo', 120)
        key = getattr(parameters, 'key', 'C')
        genre = getattr(parameters, 'genre', 'pop')
        
        # 構建基礎提示詞
        prompt = f"""
請為以下音樂描述生成一個完整的編曲計劃:

音樂描述: {description}
速度(BPM): {tempo}
調性: {key}
風格: {genre}

請使用以下JSON格式表示編曲計劃:

{{
  "arrangement_name": "作品名稱",
  "sections": [
    {{
      "name": "前奏",
      "duration_bars": 4,
      "instruments": [
        {{
          "name": "piano",
          "role": "harmony",
          "playing_style": "arpeggios",
          "dynamics": "mf"
        }},
        ...
      ]
    }},
    ...
  ],
  "instruments": [
    {{
      "name": "piano",
      "midi_program": 0,
      "description": "作為主要和聲支持"
    }},
    ...
  ],
  "overall_structure": "描述整體結構和發展",
  "suggested_mixing": "混音建議"
}}

編曲計劃應該:
1. 符合{genre}風格的典型編排
2. 包含適合該風格的樂器選擇
3. 有清晰的段落結構
4. 細節豐富並可實際實現
5. 表達"{description}"描述的情感和氛圍

只需返回JSON格式的編曲計劃，不要有任何其他文字說明。
"""
        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """呼叫大語言模型
        
        Args:
            prompt: 提示詞
            
        Returns:
            str: 模型回應
        """
        try:
            if self.provider_type == LLMProviderType.OLLAMA:
                return self._call_ollama(prompt)
            elif self.provider_type == LLMProviderType.OPENAI:
                return self._call_openai(prompt)
            elif self.provider_type == LLMProviderType.LMSTUDIO:
                return self._call_lmstudio(prompt)
            elif self.provider_type == LLMProviderType.HUGGINGFACE:
                return self._call_huggingface(prompt)
            else:
                logger.error(f"不支持的LLM提供商類型: {self.provider_type}")
                return "[]"  # 返回空JSON數組
        except Exception as e:
            logger.error(f"呼叫LLM時發生錯誤: {str(e)}")
            return "[]"  # 返回空JSON數組
    
    def _call_ollama(self, prompt: str) -> str:
        """呼叫Ollama
        
        Args:
            prompt: 提示詞
            
        Returns:
            str: 模型回應
        """
        model_name = os.environ.get("OLLAMA_MODEL", "llama3")  # 默認使用llama3
        
        payload = {
            "model": model_name,
            "prompt": f"{self.config.system_message}\n\n{prompt}",
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens
            }
        }
        
        response = requests.post(self.llm_api_url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        return result.get("response", "")
    
    def _call_openai(self, prompt: str) -> str:
        """呼叫OpenAI API
        
        Args:
            prompt: 提示詞
            
        Returns:
            str: 模型回應
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.llm_api_key}"
        }
        
        payload = {
            "model": self.config.model_name if self.config.model_name != "default" else "gpt-4",
            "messages": [
                {"role": "system", "content": self.config.system_message},
                {"role": "user", "content": prompt}
            ],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }
        
        response = requests.post(self.llm_api_url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        return result.get("choices", [{}])[0].get("message", {}).get("content", "")
    
    def _call_lmstudio(self, prompt: str) -> str:
        """呼叫LMStudio
        
        Args:
            prompt: 提示詞
            
        Returns:
            str: 模型回應
        """
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": [
                {"role": "system", "content": self.config.system_message},
                {"role": "user", "content": prompt}
            ],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "stream": False
        }
        
        response = requests.post(self.llm_api_url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        return result.get("choices", [{}])[0].get("message", {}).get("content", "")
    
    def _call_huggingface(self, prompt: str) -> str:
        """呼叫Hugging Face API
        
        Args:
            prompt: 提示詞
            
        Returns:
            str: 模型回應
        """
        headers = {
            "Authorization": f"Bearer {self.llm_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": f"{self.config.system_message}\n\n{prompt}",
            "parameters": {
                "max_new_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
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
    
    def _parse_melody_response(self, response: str) -> List[Dict[str, Any]]:
        """解析旋律回應
        
        Args:
            response: LLM回應
            
        Returns:
            List[Dict[str, Any]]: 解析後的旋律數據
        """
        try:
            # 嘗試提取JSON部分
            import re
            
            # 首先嘗試尋找完整的JSON數組
            json_match = re.search(r'(\[\s*\{.*\}\s*\])', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    logger.warning("找到JSON形式的字符串但無法解析，嘗試清理後再解析")
            
            # 如果未找到匹配的JSON數組或無法解析，嘗試清理回應中的所有文本
            # 移除非ASCII字符、註釋和可能導致解析錯誤的內容
            cleaned_response = re.sub(r'//.*?\n', '\n', response)  # 移除單行註釋
            cleaned_response = re.sub(r'/\*.*?\*/', '', cleaned_response, flags=re.DOTALL)  # 移除多行註釋
            cleaned_response = re.sub(r'[^\x00-\x7F]+', '', cleaned_response)  # 移除非ASCII字符
            
            # 嘗試找到數組的開始和結束
            start_idx = cleaned_response.find('[')
            end_idx = cleaned_response.rfind(']')
            
            if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                json_str = cleaned_response[start_idx:end_idx+1]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    logger.warning("清理後仍然無法解析JSON，使用默認旋律")
            
            # 如果所有嘗試都失敗，嘗試直接解析整個回應
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                logger.warning("無法直接解析回應為JSON，使用默認旋律")
            
            # 所有嘗試都失敗，返回默認旋律
            raise ValueError("無法從回應中提取有效的JSON")
            
        except Exception as e:
            logger.error(f"解析旋律回應時出錯: {str(e)}\n回應: {response}")
            # 返回一個更豐富的中國風默認旋律
            return [
                {"pitch": 62, "start_time": 0.0, "duration": 0.5, "velocity": 85},
                {"pitch": 64, "start_time": 0.5, "duration": 0.5, "velocity": 85},
                {"pitch": 67, "start_time": 1.0, "duration": 0.5, "velocity": 85},
                {"pitch": 69, "start_time": 1.5, "duration": 0.5, "velocity": 85},
                {"pitch": 74, "start_time": 2.0, "duration": 1.0, "velocity": 85},
                {"pitch": 72, "start_time": 3.0, "duration": 0.5, "velocity": 85},
                {"pitch": 69, "start_time": 3.5, "duration": 0.5, "velocity": 85},
                {"pitch": 67, "start_time": 4.0, "duration": 1.0, "velocity": 85},
                {"pitch": 64, "start_time": 5.0, "duration": 0.5, "velocity": 85},
                {"pitch": 62, "start_time": 5.5, "duration": 0.5, "velocity": 85},
                {"pitch": 64, "start_time": 6.0, "duration": 0.5, "velocity": 85},
                {"pitch": 67, "start_time": 6.5, "duration": 0.5, "velocity": 85},
                {"pitch": 69, "start_time": 7.0, "duration": 0.5, "velocity": 85},
                {"pitch": 67, "start_time": 7.5, "duration": 0.5, "velocity": 85},
                {"pitch": 64, "start_time": 8.0, "duration": 1.0, "velocity": 85},
                {"pitch": 62, "start_time": 9.0, "duration": 1.0, "velocity": 85}
            ]
    
    def _parse_chord_response(self, response: str) -> List[Dict[str, Any]]:
        """解析和弦回應
        
        Args:
            response: LLM回應
            
        Returns:
            List[Dict[str, Any]]: 解析後的和弦數據
        """
        try:
            # 嘗試提取JSON部分
            import re
            
            # 首先嘗試尋找完整的JSON數組
            json_match = re.search(r'(\[\s*\{.*\}\s*\])', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    logger.warning("找到JSON形式的字符串但無法解析，嘗試清理後再解析")
            
            # 如果未找到匹配的JSON數組或無法解析，嘗試清理回應中的所有文本
            cleaned_response = re.sub(r'//.*?\n', '\n', response)  # 移除單行註釋
            cleaned_response = re.sub(r'/\*.*?\*/', '', cleaned_response, flags=re.DOTALL)  # 移除多行註釋
            cleaned_response = re.sub(r'[^\x00-\x7F]+', '', cleaned_response)  # 移除非ASCII字符
            
            # 嘗試找到數組的開始和結束
            start_idx = cleaned_response.find('[')
            end_idx = cleaned_response.rfind(']')
            
            if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                json_str = cleaned_response[start_idx:end_idx+1]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    logger.warning("清理後仍然無法解析JSON，使用默認和弦進行")
            
            # 如果所有嘗試都失敗，嘗試直接解析整個回應
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                logger.warning("無法直接解析回應為JSON，使用默認和弦進行")
            
            # 所有嘗試都失敗，返回默認和弦進行
            raise ValueError("無法從回應中提取有效的JSON")
            
        except Exception as e:
            logger.error(f"解析和弦回應時出錯: {str(e)}\n回應: {response}")
            # 返回一個更豐富的中國風默認和弦進行
            return [
                {"chord_name": "D", "start_time": 0.0, "duration": 2.0, "notes": [62, 66, 69]},
                {"chord_name": "A", "start_time": 2.0, "duration": 2.0, "notes": [57, 61, 64]},
                {"chord_name": "Bm", "start_time": 4.0, "duration": 2.0, "notes": [59, 62, 66]},
                {"chord_name": "F#m", "start_time": 6.0, "duration": 2.0, "notes": [54, 57, 61]},
                {"chord_name": "G", "start_time": 8.0, "duration": 2.0, "notes": [55, 59, 62]},
                {"chord_name": "D", "start_time": 10.0, "duration": 2.0, "notes": [62, 66, 69]},
                {"chord_name": "Em", "start_time": 12.0, "duration": 2.0, "notes": [52, 55, 59]},
                {"chord_name": "A", "start_time": 14.0, "duration": 2.0, "notes": [57, 61, 64]}
            ]
    
    def _parse_arrangement_response(self, response: str) -> Dict[str, Any]:
        """解析編曲計劃回應
        
        Args:
            response: LLM回應
            
        Returns:
            Dict[str, Any]: 解析後的編曲計劃
        """
        try:
            # 嘗試提取JSON部分
            import re
            json_match = re.search(r'(\{\s*".*"\s*:.*\})', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                return json.loads(json_str)
            
            # 如果沒有找到JSON對象，嘗試直接解析
            return json.loads(response)
        except Exception as e:
            logger.error(f"解析編曲計劃回應時出錯: {str(e)}\n回應: {response}")
            # 返回一個簡單的默認編曲計劃
            return {
                "arrangement_name": "默認編曲",
                "sections": [
                    {
                        "name": "主段",
                        "duration_bars": 8,
                        "instruments": [
                            {
                                "name": "piano",
                                "role": "melody",
                                "playing_style": "legato",
                                "dynamics": "mf"
                            }
                        ]
                    }
                ],
                "instruments": [
                    {
                        "name": "piano",
                        "midi_program": 0,
                        "description": "主要樂器"
                    }
                ]
            }


# 使用示例
if __name__ == "__main__":
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
    
    # 創建生成器
    generator = LLMMusicGenerator(
        llm_api_key=llm_api_key,
        llm_api_url=llm_api_url,
        provider_type=provider
    )
    
    # 測試旋律生成
    parameters = MusicParameters(tempo=120, key="C", genre="pop")
    description = "一段輕快愉悅的旋律，適合春天的心情"
    
    try:
        melody_data = generator.generate_melody_representation(description, parameters)
        print("生成的旋律JSON表示:")
        print(json.dumps(melody_data, indent=2, ensure_ascii=False))
        
        melody = generator.generate_melody(description, parameters)
        print(f"生成了 {len(melody)} 個音符的旋律")
        
        # 測試和弦生成
        chord_data = generator.generate_chord_progression(description, parameters, melody)
        print("生成的和弦進行:")
        print(json.dumps(chord_data, indent=2, ensure_ascii=False))
        
        # 測試編曲計劃生成
        arrangement = generator.generate_arrangement_plan(description, parameters)
        print("生成的編曲計劃:")
        print(json.dumps(arrangement, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"測試過程中發生錯誤: {str(e)}") 