#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
大語言模型音樂生成示例程序
此程序演示如何使用大語言模型進行音樂創作意圖解析，然後生成MIDI音樂
"""

import os
import sys
import json
import logging
import requests
from typing import Dict, Any, Optional

# 嘗試導入MIDI工具
try:
    from midiutil import MIDIFile
except ImportError:
    print("缺少midiutil套件，請執行: pip install midiutil")
    sys.exit(1)

# 導入音樂生成函數
try:
    from standalone_app import create_simple_midi, create_midi_with_style, UserStyleManager
except ImportError:
    print("找不到standalone_app.py，請確保文件在當前目錄")
    sys.exit(1)

# 配置日誌
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LLMMusicIntentParser:
    """使用大語言模型解析音樂創作意圖"""
    
    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None):
        """初始化LLM意圖解析器
        
        Args:
            api_url: HuggingFace API端點
            api_key: HuggingFace API密鑰
        """
        self.api_url = api_url
        self.api_key = api_key
        self.use_hf = bool(api_url and api_key)
        
        if self.use_hf:
            logger.info(f"初始化HuggingFace意圖解析器，使用端點: {self.api_url}")
        else:
            logger.info("初始化模擬版LLM意圖解析器 (未提供API憑證)")
    
    def parse_intention(self, description: str) -> Dict[str, Any]:
        """解析用戶音樂創作意圖
        
        Args:
            description: 用戶描述的音樂創作意圖
            
        Returns:
            Dict: 解析後的音樂參數
        """
        logger.info(f"解析音樂創作意圖: {description}")
        
        # 嘗試使用HuggingFace API
        if self.use_hf:
            try:
                prompt = self._build_prompt(description)
                response = self._call_huggingface(prompt)
                parsed_params = self._parse_response(response)
                
                # 添加原始描述
                parsed_params["description"] = description
                return parsed_params
            except Exception as e:
                logger.error(f"使用HuggingFace API時發生錯誤: {str(e)}，將使用模擬分析")
        
        # 模擬LLM分析（當API不可用或未配置時）
        return self._simulate_analysis(description)
    
    def _build_prompt(self, description: str) -> str:
        """構建提示詞
        
        Args:
            description: 用戶描述
            
        Returns:
            str: 提示詞
        """
        return f"""
作為一位音樂理論和作曲專家，請深入分析以下音樂創作需求:

"{description}"

從中提取重要的音樂元素和參數，並以JSON格式回應，包含以下欄位:

- style: 音樂風格 ("古典", "爵士", "流行", "電子" 四選一)
- mood: 情感氛圍 (如"快樂", "悲傷", "激動", "平靜"等)
- tempo: 建議的速度值 (範圍60-180的整數)
- advanced_params: 包含以下高級參數 (均為0.0到1.0之間的小數):
  - rhythm_complexity: 節奏複雜度
  - harmony_richness: 和聲豐富度
  - note_density: 音符密度
  - velocity_dynamics: 力度變化
- timbre_description: 音色描述 (如"明亮", "溫暖", "柔和", "強勁", "夢幻"等)

請確保拆解全面而準確，考慮用戶描述中暗示的所有音樂特徵和風格元素。
我只需要JSON格式的結果，不要任何其他解釋文字。
"""
    
    def _call_huggingface(self, prompt: str) -> str:
        """呼叫HuggingFace API
        
        Args:
            prompt: 提示詞
            
        Returns:
            str: API回應
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 1024,
                "temperature": 0.3,
                "return_full_text": False
            }
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            
            # 根據返回格式解析
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', '')
            elif isinstance(result, dict):
                return result.get('generated_text', '')
            else:
                return ""
                
        except Exception as e:
            logger.error(f"呼叫HuggingFace API時發生錯誤: {str(e)}")
            raise
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """解析API回應
        
        Args:
            response: API回應
            
        Returns:
            Dict: 解析後的參數
        """
        try:
            # 嘗試提取JSON部分
            import re
            
            # 查找JSON對象
            json_match = re.search(r'(\{.*\})', response, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
                parsed_data = json.loads(json_str)
                
                # 將英文風格映射回中文（如果需要）
                style_map_en_to_zh = {
                    "classical": "古典",
                    "jazz": "爵士",
                    "pop": "流行",
                    "electronic": "電子"
                }
                
                # 檢查風格是否為英文，如果是則轉換為中文
                style = parsed_data.get("style", "").lower()
                if style in style_map_en_to_zh:
                    parsed_data["style"] = style_map_en_to_zh[style]
                    logger.info(f"將英文風格 '{style}' 映射為中文風格 '{style_map_en_to_zh[style]}'")
                
                return parsed_data
                
            else:
                logger.warning("無法從回應中提取JSON，將使用模擬分析")
                
        except Exception as e:
            logger.error(f"解析回應時出錯: {str(e)}")
        
        # 解析失敗時使用默認參數
        return {
            "style": "古典",
            "mood": "平靜",
            "tempo": 100,
            "advanced_params": {
                "rhythm_complexity": 0.5,
                "harmony_richness": 0.5,
                "note_density": 0.5,
                "velocity_dynamics": 0.5
            },
            "timbre_description": "明亮"
        }
    
    def _simulate_analysis(self, description: str) -> Dict[str, Any]:
        """模擬LLM分析
        
        Args:
            description: 用戶描述
            
        Returns:
            Dict: 模擬分析結果
        """
        # 簡單關鍵詞匹配來模擬LLM分析
        style = "古典"  # 預設風格
        mood = "平靜"   # 預設情感
        tempo = 100     # 預設速度
        
        # 風格識別
        description_lower = description.lower()
        if any(word in description_lower for word in ["爵士", "藍調", "搖擺"]):
            style = "爵士"
        elif any(word in description_lower for word in ["流行", "現代", "通俗"]):
            style = "流行"
        elif any(word in description_lower for word in ["電子", "舞曲", "節拍"]):
            style = "電子"
        
        # 情感識別
        if any(word in description_lower for word in ["快樂", "歡快", "歡樂", "輕快", "喜悅"]):
            mood = "快樂"
        elif any(word in description_lower for word in ["悲傷", "憂鬱", "傷感", "憂愁", "哀愁"]):
            mood = "悲傷"
        elif any(word in description_lower for word in ["激動", "激昂", "熱烈", "熱情", "活潑"]):
            mood = "激動"
        
        # 速度識別
        if any(word in description_lower for word in ["快速", "快節奏", "急促", "活躍"]):
            tempo = 140
        elif any(word in description_lower for word in ["中速", "適中", "中等"]):
            tempo = 100
        elif any(word in description_lower for word in ["慢速", "緩慢", "從容", "悠閒"]):
            tempo = 70
        
        # 音色識別
        timbre = "明亮"  # 預設音色
        if any(word in description_lower for word in ["溫暖", "柔美", "圓潤"]):
            timbre = "溫暖"
        elif any(word in description_lower for word in ["強勁", "有力", "厚重"]):
            timbre = "強勁"
        elif any(word in description_lower for word in ["夢幻", "空靈", "飄渺"]):
            timbre = "夢幻"
        
        # 模擬聲音豐富度和復雜度參數
        advanced_params = {
            "rhythm_complexity": 0.5,
            "harmony_richness": 0.5,
            "note_density": 0.5,
            "velocity_dynamics": 0.5
        }
        
        # 調整高級參數
        if "複雜" in description_lower:
            advanced_params["rhythm_complexity"] = 0.8
            advanced_params["harmony_richness"] = 0.7
        elif "簡單" in description_lower:
            advanced_params["rhythm_complexity"] = 0.3
            advanced_params["harmony_richness"] = 0.3
        
        if "豐富" in description_lower:
            advanced_params["note_density"] = 0.7
            advanced_params["velocity_dynamics"] = 0.7
        elif "簡約" in description_lower:
            advanced_params["note_density"] = 0.3
        
        # 返回模擬的分析結果
        result = {
            "description": description,
            "style": style,
            "mood": mood,
            "tempo": tempo,
            "advanced_params": advanced_params,
            "timbre_description": timbre
        }
        
        logger.info(f"模擬LLM分析結果: {json.dumps(result, ensure_ascii=False)}")
        return result

def create_music_from_description(description: str, output_path: str = None, hf_api_url: str = None, hf_api_key: str = None) -> str:
    """從用戶描述創建音樂
    
    Args:
        description: 用戶描述
        output_path: 輸出路徑 (可選)
        hf_api_url: HuggingFace API端點 (可選)
        hf_api_key: HuggingFace API密鑰 (可選)
        
    Returns:
        str: 生成的MIDI文件路徑
    """
    logger.info(f"從描述創建音樂: {description}")
    
    # 使用LLM解析意圖
    try:
        intent_parser = LLMMusicIntentParser(api_url=hf_api_url, api_key=hf_api_key)
        music_params = intent_parser.parse_intention(description)
        
        logger.info("解析後的音樂參數:")
        logger.info(f"  風格: {music_params.get('style', '古典')}")
        logger.info(f"  情感: {music_params.get('mood', '平靜')}")
        logger.info(f"  速度: {music_params.get('tempo', 100)}")
        logger.info(f"  音色描述: {music_params.get('timbre_description', '明亮')}")
        
        # 如果未提供輸出路徑，生成一個默認路徑
        if output_path is None:
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"llm_music_{music_params.get('style', '古典')}.mid")
        
        # 確保輸出目錄存在
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # 使用從LLM獲得的參數生成音樂
        user_style_manager = UserStyleManager()
        
        style = music_params.get('style', '古典')
        tempo = music_params.get('tempo', 100)
        timbre_description = music_params.get('timbre_description', '明亮')
        advanced_params = music_params.get('advanced_params', {})
        
        # 處理可能包含中文的文件名
        try:
            # 構建安全的文件名
            basename = os.path.splitext(os.path.basename(output_path))[0]
            dirname = os.path.dirname(output_path)
            safe_basename = ''.join(c for c in basename if ord(c) < 128)
            if not safe_basename:
                # 使用風格和情感作為文件名
                style_en = {"古典": "classical", "爵士": "jazz", "流行": "pop", "電子": "electronic"}.get(style, "music")
                mood_en = {"快樂": "happy", "悲傷": "sad", "激動": "excited", "平靜": "calm"}.get(
                    music_params.get('mood', ''), "neutral")
                safe_basename = f"llm_music_{style_en}_{mood_en}"
            
            safe_output_path = os.path.join(dirname, f"{safe_basename}.mid")
            logger.info(f"使用安全文件名: {safe_output_path}")
            
            # 從Hugging Face取得的參數中提取所需信息
            tempo = music_params.get('tempo', 100)
            
            try:
                # 嘗試使用create_midi_with_style生成音樂
                logger.info(f"嘗試使用風格化生成 ({style})...")
                result_path = create_midi_with_style(
                    style=style,
                    filename=safe_output_path,
                    custom_temperature=0.5,
                    timbre_description=timbre_description,
                    advanced_params=advanced_params,
                    user_style_manager=user_style_manager
                )
                logger.info(f"風格化生成成功: {result_path}")
                return result_path
            except Exception as e:
                # 如果風格化生成失敗，使用簡單MIDI生成
                logger.warning(f"風格化生成失敗 ({str(e)})，使用簡單MIDI生成...")
                result_path = create_simple_midi(
                    filename=safe_output_path,
                    tempo=tempo,
                    timbre_name=None
                )
                logger.info(f"簡單MIDI生成成功: {result_path}")
                return result_path
            
        except Exception as e:
            logger.error(f"創建音樂時發生錯誤: {str(e)}")
            
            # 創建一個簡單的MIDI文件作為後備
            logger.info("生成簡單的MIDI文件作為後備")
            if output_path is None:
                output_dir = "output"
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, "simple_fallback.mid")
            
            # 確保後備文件名也是安全的
            basename = os.path.splitext(os.path.basename(output_path))[0]
            dirname = os.path.dirname(output_path)
            safe_basename = ''.join(c for c in basename if ord(c) < 128)
            if not safe_basename:
                safe_basename = "simple_fallback"
            
            safe_fallback_path = os.path.join(dirname, f"{safe_basename}.mid")
            return create_simple_midi(filename=safe_fallback_path, tempo=100)
        
    except Exception as e:
        logger.error(f"創建音樂時發生錯誤: {str(e)}")
        
        # 創建一個簡單的MIDI文件作為後備
        logger.info("生成簡單的MIDI文件作為後備")
        if output_path is None:
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "simple_fallback.mid")
        
        return create_simple_midi(filename=output_path, tempo=100)

def main():
    """主函數"""
    import argparse
    import os
    
    # 解析命令行參數
    parser = argparse.ArgumentParser(description="使用大語言模型創建音樂")
    parser.add_argument("--description", "-d", type=str, help="音樂創作描述")
    parser.add_argument("--output", "-o", type=str, help="輸出MIDI文件路徑")
    parser.add_argument("--interactive", "-i", action="store_true", help="互動模式")
    parser.add_argument("--hf-api-url", type=str, help="HuggingFace API URL")
    parser.add_argument("--hf-api-key", type=str, help="HuggingFace API Key")
    
    args = parser.parse_args()
    
    # 從環境變量獲取API設置 (如果未提供)
    hf_api_url = args.hf_api_url or os.environ.get("HF_API_URL")
    hf_api_key = args.hf_api_key or os.environ.get("HF_API_KEY")
    
    if hf_api_url and hf_api_key:
        logger.info("使用HuggingFace API進行音樂創作")
    else:
        logger.info("未提供HuggingFace API憑證，將使用模擬LLM分析")
    
    if args.interactive:
        print("歡迎使用大語言模型音樂創作助手！")
        print("請描述您想要創建的音樂，或輸入'exit'退出。")
        
        while True:
            description = input("\n請描述您想要的音樂: ")
            if description.lower() == 'exit':
                break
                
            output_path = input("請輸入輸出文件路徑 (留空使用默認路徑): ")
            output_path = output_path if output_path else None
            
            midi_path = create_music_from_description(
                description, 
                output_path,
                hf_api_url=hf_api_url,
                hf_api_key=hf_api_key
            )
            print(f"音樂已生成: {midi_path}")
            
            # 提供播放提示
            if os.name == 'posix':  # macOS, Linux等
                print("在終端中使用以下命令嘗試播放:")
                print(f"  timidity {midi_path}")
            elif os.name == 'nt':  # Windows
                print("在Windows中，您可以雙擊MIDI文件來播放它")
    
    elif args.description:
        # 使用命令行參數
        midi_path = create_music_from_description(
            args.description, 
            args.output,
            hf_api_url=hf_api_url,
            hf_api_key=hf_api_key
        )
        print(f"音樂已生成: {midi_path}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 