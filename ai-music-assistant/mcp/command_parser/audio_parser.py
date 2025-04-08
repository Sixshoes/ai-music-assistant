"""音訊指令解析器

解析音訊輸入，將其轉換為標準化的指令對象
"""

import base64
import os
import tempfile
from typing import Optional, Dict, Any

from ..mcp_schema import (
    MCPCommand,
    CommandType,
    AudioInput,
    MusicParameters
)


class AudioCommandParser:
    """音訊指令解析器類"""
    
    def __init__(self):
        """初始化解析器"""
        # 未來可考慮整合 basic_pitch 或其他音高檢測工具
        pass
    
    def parse_audio_data_url(self, audio_data_url: str) -> tuple:
        """解析 base64 編碼的音頻數據
        
        Args:
            audio_data_url: Base64 編碼的音頻數據 URL
            
        Returns:
            tuple: (音頻數據二進制, 格式)
        """
        # 從 data URL 中提取格式和實際數據
        # 格式: data:audio/wav;base64,ACTUAL_DATA
        try:
            header, encoded = audio_data_url.split(",", 1)
            audio_format = header.split(";")[0].split("/")[1]
            audio_data = base64.b64decode(encoded)
            return audio_data, audio_format
        except Exception as e:
            raise ValueError(f"無法解析音頻數據 URL: {e}")

    def save_temp_audio(self, audio_data: bytes, audio_format: str) -> str:
        """將音頻數據保存為臨時文件
        
        Args:
            audio_data: 音頻數據二進制
            audio_format: 音頻格式 (wav, mp3 等)
            
        Returns:
            str: 臨時文件路徑
        """
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, f"audio_input.{audio_format}")
        
        with open(temp_file, "wb") as f:
            f.write(audio_data)
        
        return temp_file

    def detect_melody_info(self, audio_file: str) -> Dict[str, Any]:
        """從音頻文件中檢測旋律信息
        
        Args:
            audio_file: 音頻文件路徑
            
        Returns:
            Dict[str, Any]: 包含旋律信息的字典
        """
        # 在此處使用 Basic Pitch 或類似工具檢測旋律信息
        # 目前僅返回模擬數據，實際實現需要集成音高檢測庫
        return {
            "estimated_tempo": 120,
            "estimated_key": "C",
            "has_vocals": True
        }

    def extract_parameters(self, audio_info: Dict[str, Any]) -> MusicParameters:
        """從音頻分析信息中提取音樂參數
        
        Args:
            audio_info: 音頻分析結果
            
        Returns:
            MusicParameters: 提取的音樂參數
        """
        # 從音頻分析結果中提取參數
        # 實際實現將依賴於音頻分析工具提供的信息
        return MusicParameters(
            tempo=audio_info.get("estimated_tempo"),
            # 其他參數可能需要進一步處理
        )

    def parse(self, audio_data_url: str, additional_text: Optional[str] = None) -> MCPCommand:
        """解析音訊數據為指令對象
        
        Args:
            audio_data_url: Base64編碼的音訊數據URL
            additional_text: 附加文字描述
            
        Returns:
            MCPCommand: 解析後的指令對象
        """
        # 創建音訊輸入對象
        audio_input = AudioInput(
            audio_data_url=audio_data_url,
            format="wav"  # 默認格式
        )
        
        # 如果有附加文字，可以提取額外參數
        parameters = None
        if additional_text:
            # 這裡可以使用TextCommandParser來解析附加文字
            # 簡化實現，假設沒有額外參數
            parameters = MusicParameters()
        
        # 創建並返回指令對象
        return MCPCommand(
            command_type=CommandType.MELODY_TO_ARRANGEMENT,
            text_input=additional_text,
            audio_input=audio_input,
            parameters=parameters
        ) 