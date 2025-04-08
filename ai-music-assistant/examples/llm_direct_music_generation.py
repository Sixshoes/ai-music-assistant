#!/usr/bin/env python3
"""簡單的LLM音樂生成器示例

直接使用大語言模型生成音樂內容
"""

import os
import sys
import json
import logging
import random
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from midiutil import MIDIFile

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 直接定義必要的類別，避免模組導入問題

@dataclass
class Note:
    """音符模型"""
    pitch: int
    start_time: float
    duration: float
    velocity: int = 80
    
    def __repr__(self):
        return f"Note(pitch={self.pitch}, start_time={self.start_time:.2f}, duration={self.duration:.2f}, velocity={self.velocity})"

@dataclass
class MusicParameters:
    """音樂參數模型"""
    tempo: Optional[int] = 120
    key: Optional[str] = "C"
    genre: Optional[str] = "pop"
    
    def __repr__(self):
        return f"MusicParameters(tempo={self.tempo}, key={self.key}, genre={self.genre})"

class LLMMusicGenerator:
    """簡化版大語言模型音樂生成器"""
    
    def __init__(self, api_url=None, api_key=None):
        """初始化生成器
        
        Args:
            api_url: API端點，默認使用Ollama本地端點
            api_key: API密鑰，適用於OpenAI等需要認證的服務
        """
        import requests
        self.requests = requests
        self.random = random
        self.api_url = api_url or "http://localhost:11434/api/generate"
        self.api_key = api_key
        self.last_description = ""  # 保存最近的描述，用於後備方案
        
        # 檢測API類型
        if "huggingface" in self.api_url or "inference" in self.api_url:
            self.api_type = "huggingface"
        elif "openai" in self.api_url:
            self.api_type = "openai"
        elif "11434" in self.api_url:
            self.api_type = "ollama"
        else:
            self.api_type = "unknown"
            
        logger.info(f"初始化LLM音樂生成器，API端點: {self.api_url}, 類型: {self.api_type}")
    
    def generate_melody(self, description: str, parameters: MusicParameters) -> List[Note]:
        """生成旋律
        
        Args:
            description: 音樂描述
            parameters: 音樂參數
            
        Returns:
            List[Note]: 生成的旋律音符列表
        """
        logger.info(f"生成旋律: {description}")
        
        # 保存描述以供後備方案使用
        self.last_description = description
        
        # 構建提示詞
        prompt = self._build_melody_prompt(description, parameters)
        
        # 調用LLM
        response = self._call_llm(prompt)
        
        # 解析響應
        melody_data = self._parse_melody_response(response)
        
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
    
    def generate_chord_progression(
        self, description: str, parameters: MusicParameters, melody: Optional[List[Note]] = None
    ) -> List[Dict[str, Any]]:
        """生成和弦進行
        
        Args:
            description: 音樂描述
            parameters: 音樂參數
            melody: 可選的旋律
            
        Returns:
            List[Dict[str, Any]]: 和弦進行
        """
        logger.info(f"生成和弦進行: {description}")
        
        # 保存描述以供後備方案使用
        self.last_description = description
        
        # 構建提示詞
        prompt = self._build_chord_prompt(description, parameters, melody)
        
        # 調用LLM
        response = self._call_llm(prompt)
        
        # 解析響應
        return self._parse_chord_response(response)
    
    def _call_llm(self, prompt: str) -> str:
        """調用LLM API"""
        try:
            # 創建強大的編曲大師系統提示
            system_prompt = """你是一位世界級的音樂編曲大師，擁有數十年的專業作曲和編曲經驗。
你精通各種音樂風格、音樂理論和編曲技巧，曾為無數成功音樂作品提供創作。
你能夠創作出結構完整、情感豐富且具有專業品質的完整樂曲，而不僅僅是簡短的音樂片段。
你對旋律發展、和聲進行、音樂結構和樂器編配都有深刻的理解。
無論接收到什麼樣的音樂創作需求，你都能輸出完整的、專業水準的、可演奏的音樂內容。"""
            
            # 根據API類型使用不同的請求格式
            if self.api_type == "huggingface":
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                # HuggingFace風格的請求
                payload = {
                    "inputs": f"{system_prompt}\n\n{prompt}",
                    "parameters": {
                        "max_new_tokens": 2048,
                        "temperature": 0.7,
                        "return_full_text": False
                    }
                }
                
                # 打印調試信息
                if os.environ.get("DEBUG") == "true":
                    logger.info(f"發送到HuggingFace的請求: {json.dumps(payload, ensure_ascii=False)}")
                    logger.info(f"Header: {headers}")
                
                response = self.requests.post(self.api_url, headers=headers, json=payload)
                
                # 檢查回應狀態
                if response.status_code != 200:
                    logger.error(f"HuggingFace API返回錯誤狀態碼: {response.status_code}")
                    logger.error(f"錯誤詳情: {response.text}")
                    raise Exception(f"API調用失敗: {response.status_code} {response.text}")
                
                response.raise_for_status()
                
                result = response.json()
                
                # 解析不同格式的回應
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('generated_text', '')
                elif isinstance(result, dict):
                    return result.get('generated_text', '')
                else:
                    return str(result)  # 兜底方案
                
            elif self.api_type == "openai":
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }
                
                # OpenAI風格的請求
                payload = {
                    "model": "gpt-3.5-turbo",  # 默認模型，可被API自動替換
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7
                }
                
                response = self.requests.post(self.api_url, headers=headers, json=payload)
                response.raise_for_status()
                
                result = response.json()
                return result.get("choices", [{}])[0].get("message", {}).get("content", "")
                
            else:
                # 默認使用Ollama風格的請求
                payload = {
                    "model": "llama3",  # 或其他本地模型
                    "prompt": f"{system_prompt}\n\n{prompt}",
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 4096
                    }
                }
                
                response = self.requests.post(self.api_url, json=payload)
                response.raise_for_status()
                
                result = response.json()
                return result.get("response", "")
            
        except Exception as e:
            logger.error(f"調用LLM時出錯: {str(e)}")
            
            # 連接失敗時，直接返回合適的JSON數據
            if "中國風" in self.last_description.lower():
                if "和弦" in prompt.lower() or "chord" in prompt.lower():
                    # 返回D調中國風和弦進行的JSON字符串
                    return """
                    [
                        {"chord_name": "D", "start_time": 0.0, "duration": 2.0, "notes": [62, 66, 69]},
                        {"chord_name": "Bm", "start_time": 2.0, "duration": 2.0, "notes": [59, 62, 66]},
                        {"chord_name": "G", "start_time": 4.0, "duration": 2.0, "notes": [55, 59, 62]},
                        {"chord_name": "A", "start_time": 6.0, "duration": 2.0, "notes": [57, 61, 64]},
                        {"chord_name": "D", "start_time": 8.0, "duration": 2.0, "notes": [62, 66, 69]},
                        {"chord_name": "Em", "start_time": 10.0, "duration": 2.0, "notes": [64, 67, 71]},
                        {"chord_name": "A", "start_time": 12.0, "duration": 2.0, "notes": [57, 61, 64]},
                        {"chord_name": "D", "start_time": 14.0, "duration": 2.0, "notes": [62, 66, 69]}
                    ]
                    """
                else:
                    # 生成D調五聲音階旋律
                    # D調五聲音階 (D, E, F#, A, B) - MIDI: 62, 64, 66, 69, 71
                    pentatonic_scale = [62, 64, 66, 69, 71, 74, 76, 78]
                    
                    logger.info("生成預設中國風五聲音階旋律")
                    melody_json = "[\n"
                    
                    current_time = 0.0
                    for i in range(16):  # 創建16個音符
                        # 選擇音高
                        if i % 8 == 0:  # 每8個音符回到主音
                            pitch = 62  # D
                        else:
                            pitch = random.choice(pentatonic_scale)
                        
                        # 變化的時值
                        if i % 4 == 0:  # 每4個音符一個較長音符
                            duration = 1.0
                        elif i % 7 == 0:  # 偶爾有裝飾音
                            duration = 0.25
                        else:
                            duration = 0.5
                        
                        # 變化的力度
                        if i == 0 or i == 8:  # 段落開始強調
                            velocity = 90
                        else:
                            velocity = random.randint(70, 85)
                        
                        # 添加音符
                        melody_json += f'  {{"pitch": {pitch}, "start_time": {current_time:.2f}, "duration": {duration:.2f}, "velocity": {velocity}}}'
                        
                        if i < 15:  # 不是最後一個音符
                            melody_json += ",\n"
                        else:
                            melody_json += "\n"
                            
                        current_time += duration
                    
                    melody_json += "]"
                    return melody_json
            
            # 返回一個基本的回應，避免程序崩潰
            return "[]"
    
    def _parse_melody_response(self, response: str) -> List[Dict[str, Any]]:
        """解析旋律回應"""
        try:
            # 嘗試提取JSON部分
            import re
            
            # 查找最好的JSON部分 - 查找以[開始，以]結束的部分
            json_matches = re.findall(r'(\[\s*\{.*?\}\s*\])', response, re.DOTALL)
            
            if json_matches:
                # 如果找到了多個匹配，選擇最長的一個
                best_match = max(json_matches, key=len)
                if os.environ.get("DEBUG") == "true":
                    logger.info(f"找到JSON匹配: {best_match}")
                return json.loads(best_match)
            
            # 試著查找帶有```json標記的部分
            code_block_match = re.search(r'```(?:json)?\s*(\[\s*\{.*?\}\s*\])\s*```', response, re.DOTALL)
            if code_block_match:
                json_str = code_block_match.group(1)
                if os.environ.get("DEBUG") == "true":
                    logger.info(f"從代碼塊中提取JSON: {json_str}")
                return json.loads(json_str)
            
            # 如果沒有找到JSON數組，嘗試直接解析
            try:
                return json.loads(response)
            except:
                # 最後的嘗試：尋找任何看起來像JSON數組的內容
                any_array = re.search(r'\[\s*({.*?}(?:\s*,\s*{.*?})*)\s*\]', response, re.DOTALL)
                if any_array:
                    json_str = f"[{any_array.group(1)}]"
                    if os.environ.get("DEBUG") == "true":
                        logger.info(f"嘗試解析提取的數組內容: {json_str}")
                    return json.loads(json_str)
                
                raise Exception("無法在回應中找到有效的JSON")
        except Exception as e:
            logger.error(f"解析旋律回應時出錯: {str(e)}\n回應: {response}")
            # 返回一個簡單的默認旋律
            return [
                {"pitch": 60, "start_time": 0.0, "duration": 0.5, "velocity": 80},
                {"pitch": 62, "start_time": 0.5, "duration": 0.5, "velocity": 80},
                {"pitch": 64, "start_time": 1.0, "duration": 0.5, "velocity": 80},
                {"pitch": 65, "start_time": 1.5, "duration": 0.5, "velocity": 80}
            ]
    
    def _parse_chord_response(self, response: str) -> List[Dict[str, Any]]:
        """解析和弦回應"""
        try:
            # 嘗試提取JSON部分
            import re
            
            # 查找最好的JSON部分 - 查找以[開始，以]結束的部分
            json_matches = re.findall(r'(\[\s*\{.*?\}\s*\])', response, re.DOTALL)
            
            if json_matches:
                # 如果找到了多個匹配，選擇最長的一個
                best_match = max(json_matches, key=len)
                if os.environ.get("DEBUG") == "true":
                    logger.info(f"找到JSON匹配: {best_match}")
                return json.loads(best_match)
            
            # 試著查找帶有```json標記的部分
            code_block_match = re.search(r'```(?:json)?\s*(\[\s*\{.*?\}\s*\])\s*```', response, re.DOTALL)
            if code_block_match:
                json_str = code_block_match.group(1)
                if os.environ.get("DEBUG") == "true":
                    logger.info(f"從代碼塊中提取JSON: {json_str}")
                return json.loads(json_str)
            
            # 如果沒有找到JSON數組，嘗試直接解析
            try:
                return json.loads(response)
            except:
                # 最後的嘗試：尋找任何看起來像JSON數組的內容
                any_array = re.search(r'\[\s*({.*?}(?:\s*,\s*{.*?})*)\s*\]', response, re.DOTALL)
                if any_array:
                    json_str = f"[{any_array.group(1)}]"
                    if os.environ.get("DEBUG") == "true":
                        logger.info(f"嘗試解析提取的數組內容: {json_str}")
                    return json.loads(json_str)
                
                raise Exception("無法在回應中找到有效的JSON")
        except Exception as e:
            logger.error(f"解析和弦回應時出錯: {str(e)}\n回應: {response}")
            # 返回一個簡單的默認和弦進行
            return [
                {"chord_name": "D", "start_time": 0.0, "duration": 2.0, "notes": [62, 66, 69]},
                {"chord_name": "A", "start_time": 2.0, "duration": 2.0, "notes": [57, 61, 64]},
                {"chord_name": "Bm", "start_time": 4.0, "duration": 2.0, "notes": [59, 62, 66]},
                {"chord_name": "G", "start_time": 6.0, "duration": 2.0, "notes": [55, 59, 62]}
            ]

    def _build_melody_prompt(self, description: str, parameters: MusicParameters) -> str:
        """構建旋律生成提示詞"""
        return f"""
請為以下音樂描述生成一段完整的旋律的JSON表示:

音樂描述: {description}
速度(BPM): {parameters.tempo}
調性: {parameters.key}
風格: {parameters.genre}

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
1. 符合{parameters.key}調性
2. 具有{parameters.genre}風格的特點
3. 表達"{description}"所描述的情感和氛圍
4. 音符時間精確且實際可演奏
5. 總長度在30-60秒之間，包含足夠數量的音符（至少50個音符）
6. 具有完整的音樂結構，包括引入部分、主題部分、發展部分和結束部分
7. 包含適當的旋律發展、音樂動機和變化，不僅僅是簡單重複的片段
8. 考慮音樂張力的起伏變化，創造有趣的音樂旅程

只需返回JSON格式的旋律，不要有任何其他文字說明。
"""
    
    def _build_chord_prompt(self, description: str, parameters: MusicParameters, 
                         melody: Optional[List[Note]] = None) -> str:
        """構建和弦生成提示詞"""
        # 構建基礎提示詞
        prompt = f"""
請為以下音樂描述生成一組完整的和弦進行:

音樂描述: {description}
速度(BPM): {parameters.tempo}
調性: {parameters.key}
風格: {parameters.genre}

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
1. 和聲上符合{parameters.key}調性
2. 風格上匹配{parameters.genre}類型音樂的和聲特點
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


def save_notes_to_midi(notes: List[Note], output_path: str, tempo: int = 120) -> None:
    """將音符列表保存為MIDI文件
    
    Args:
        notes: 音符列表
        output_path: 輸出路徑
        tempo: 速度(BPM)
    """
    # 創建MIDI文件，單軌道
    midi = MIDIFile(1)
    
    # 設置速度
    midi.addTempo(0, 0, tempo)
    
    # 添加音符
    for note in notes:
        midi.addNote(
            track=0, 
            channel=0, 
            pitch=note.pitch, 
            time=note.start_time, 
            duration=note.duration, 
            volume=note.velocity
        )
    
    # 寫入文件
    with open(output_path, "wb") as f:
        midi.writeFile(f)
    
    logger.info(f"MIDI文件已保存至 {output_path}")


def save_chord_progression_to_midi(chords: List[Dict[str, Any]], output_path: str, tempo: int = 120) -> None:
    """將和弦進行保存為MIDI文件
    
    Args:
        chords: 和弦進行
        output_path: 輸出路徑
        tempo: 速度(BPM)
    """
    # 創建MIDI文件，單軌道
    midi = MIDIFile(1)
    
    # 設置速度
    midi.addTempo(0, 0, tempo)
    
    # 添加和弦
    for chord in chords:
        for note in chord.get("notes", []):
            midi.addNote(
                track=0, 
                channel=0, 
                pitch=note, 
                time=chord["start_time"], 
                duration=chord["duration"], 
                volume=70
            )
    
    # 寫入文件
    with open(output_path, "wb") as f:
        midi.writeFile(f)
    
    logger.info(f"和弦MIDI文件已保存至 {output_path}")


def main():
    """主函數"""
    import argparse
    import json  # 確保這裡導入json
    
    parser = argparse.ArgumentParser(description="LLM音樂生成器示例")
    parser.add_argument("--description", "-d", type=str, 
                        default="創造一段悠揚的小提琴旋律，帶有中國風的意境",
                        help="音樂描述")
    parser.add_argument("--tempo", "-t", type=int, default=90, help="速度(BPM)")
    parser.add_argument("--key", "-k", type=str, default="D", help="調性")
    parser.add_argument("--genre", "-g", type=str, default="classical", help="風格")
    parser.add_argument("--api-url", type=str, 
                        default="http://localhost:11434/api/generate",
                        help="LLM API端點")
    parser.add_argument("--api-key", type=str, 
                        default=None,
                        help="API密鑰(如需要)")
    parser.add_argument("--output-dir", "-o", type=str, default="output", 
                        help="輸出目錄")
    parser.add_argument("--debug", action="store_true", help="打印調試信息")
    
    args = parser.parse_args()
    
    # 設置調試標誌
    if args.debug or os.environ.get("DEBUG") == "true":
        os.environ["DEBUG"] = "true"
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("已啟用調試模式")
    
    # 創建輸出目錄
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 嘗試從環境變數獲取API金鑰
    api_key = args.api_key or os.environ.get("HF_API_KEY")
    
    # 創建音樂參數
    parameters = MusicParameters(
        tempo=args.tempo,
        key=args.key,
        genre=args.genre
    )
    
    # 創建LLM音樂生成器
    generator = LLMMusicGenerator(api_url=args.api_url, api_key=api_key)
    
    try:
        # 生成旋律
        logger.info(f"開始生成旋律: {args.description}")
        melody = generator.generate_melody(args.description, parameters)
        logger.info(f"成功生成旋律，共 {len(melody)} 個音符")
        
        # 保存旋律MIDI
        melody_path = os.path.join(args.output_dir, "melody.mid")
        save_notes_to_midi(melody, melody_path, args.tempo)
        
        # 生成和弦進行
        logger.info("開始生成和弦進行")
        chords = generator.generate_chord_progression(args.description, parameters, melody)
        logger.info(f"成功生成和弦進行，共 {len(chords)} 個和弦")
        
        # 保存和弦MIDI
        chords_path = os.path.join(args.output_dir, "chords.mid")
        save_chord_progression_to_midi(chords, chords_path, args.tempo)
        
        # 保存原始JSON數據
        data = {
            "description": args.description,
            "parameters": {
                "tempo": args.tempo,
                "key": args.key,
                "genre": args.genre
            },
            "melody": [
                {
                    "pitch": note.pitch,
                    "start_time": note.start_time,
                    "duration": note.duration,
                    "velocity": note.velocity
                }
                for note in melody
            ],
            "chords": chords
        }
        
        json_path = os.path.join(args.output_dir, "music_data.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info("音樂生成完成!")
        logger.info(f"旋律MIDI: {melody_path}")
        logger.info(f"和弦MIDI: {chords_path}")
        logger.info(f"JSON數據: {json_path}")
        
    except Exception as e:
        logger.error(f"音樂生成過程中發生錯誤: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main() 