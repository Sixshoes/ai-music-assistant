"""音頻格式驗證工具

提供音頻數據格式驗證功能
"""

import base64
import struct
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class AudioValidator:
    """音頻格式驗證器"""
    
    @staticmethod
    def validate_audio_data(audio_data: bytes) -> Tuple[bool, str]:
        """驗證音頻數據格式
        
        Args:
            audio_data: 音頻數據
            
        Returns:
            Tuple[bool, str]: (是否有效, 錯誤信息)
        """
        try:
            # 檢查WAV文件頭
            if not audio_data.startswith(b'RIFF'):
                return False, "無效的WAV文件頭：缺少RIFF標識"
            
            if b'WAVE' not in audio_data[:12]:
                return False, "無效的WAV文件頭：缺少WAVE標識"
            
            # 解析fmt塊
            fmt_start = audio_data.find(b'fmt ')
            if fmt_start == -1:
                return False, "無效的WAV文件：缺少fmt塊"
            
            # 解析音頻參數
            fmt_data = audio_data[fmt_start:fmt_start+24]
            audio_format, channels, sample_rate, byte_rate, block_align, bits_per_sample = struct.unpack('<HHIIHH', fmt_data[8:24])
            
            # 驗證採樣率
            if sample_rate != 44100:
                return False, f"不支持的採樣率：{sample_rate}Hz，需要44100Hz"
            
            # 驗證位深度
            if bits_per_sample != 16:
                return False, f"不支持的位深度：{bits_per_sample}位，需要16位"
            
            # 驗證聲道數
            if channels not in [1, 2]:
                return False, f"不支持的聲道數：{channels}，需要1或2聲道"
            
            return True, "音頻格式驗證通過"
            
        except Exception as e:
            logger.error(f"音頻格式驗證失敗: {str(e)}")
            return False, f"音頻格式驗證失敗: {str(e)}"
    
    @staticmethod
    def validate_base64_audio(audio_data_url: str) -> Tuple[bool, str, Optional[bytes]]:
        """驗證Base64編碼的音頻數據
        
        Args:
            audio_data_url: Base64編碼的音頻數據URL
            
        Returns:
            Tuple[bool, str, Optional[bytes]]: (是否有效, 錯誤信息, 解碼後的音頻數據)
        """
        try:
            # 從data URL中提取實際數據
            if audio_data_url.startswith("data:audio/"):
                header, encoded = audio_data_url.split(",", 1)
                audio_format = header.split(";")[0].split("/")[1]
                if audio_format.lower() != "wav":
                    return False, f"不支持的音頻格式：{audio_format}，需要WAV格式", None
                audio_data = base64.b64decode(encoded)
            else:
                audio_data = base64.b64decode(audio_data_url)
            
            # 驗證音頻數據
            is_valid, error_msg = AudioValidator.validate_audio_data(audio_data)
            return is_valid, error_msg, audio_data if is_valid else None
            
        except Exception as e:
            logger.error(f"Base64音頻數據驗證失敗: {str(e)}")
            return False, f"Base64音頻數據驗證失敗: {str(e)}", None 