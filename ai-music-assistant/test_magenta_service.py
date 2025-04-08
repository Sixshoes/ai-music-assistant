#!/usr/bin/env python
"""
測試 Magenta 服務

此腳本用於測試模擬 Magenta 服務的功能。
"""

import os
import sys
import logging
from pathlib import Path

# 設置日誌記錄
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 設置環境變量以使用模擬服務
os.environ["USE_MOCK_MAGENTA"] = "true"

# 將當前目錄添加到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent))

# 導入服務
try:
    from backend.music_generation import MagentaService, get_service_status
    
    # 打印服務狀態
    status = get_service_status()
    logger.info(f"服務狀態: {status}")
    
    # 創建服務實例
    service = MagentaService()
    
    # 創建一個簡單的音樂參數對象
    class MusicParameters:
        def __init__(self):
            self.tempo = 120
            self.key = "C"
            self.genre = "jazz"
            
    params = MusicParameters()
    
    # 測試生成旋律
    logger.info("測試生成旋律...")
    melody = service.generate_melody(params)
    logger.info(f"生成了 {len(melody)} 個音符")
    
    # 測試生成伴奏
    logger.info("測試生成伴奏...")
    accompaniment = service.generate_accompaniment(melody, params)
    logger.info(f"生成了 {len(accompaniment.get('chords', []))} 個和弦音符")
    logger.info(f"生成了 {len(accompaniment.get('bass', []))} 個低音音符")
    
    # 測試生成鼓點
    logger.info("測試生成鼓點...")
    drums = service.generate_drum_pattern(params)
    logger.info(f"生成了 {len(drums)} 個鼓點音符")
    
    # 測試生成完整編曲
    logger.info("測試生成完整編曲...")
    arrangement = service.generate_full_arrangement(melody, params)
    logger.info(f"MIDI 文件位置: {arrangement.get('midi_path', 'unknown')}")
    
    logger.info("所有測試完成!")
    
except ImportError as e:
    logger.error(f"導入錯誤: {e}")
except Exception as e:
    logger.error(f"測試過程中發生錯誤: {e}")
    import traceback
    traceback.print_exc() 