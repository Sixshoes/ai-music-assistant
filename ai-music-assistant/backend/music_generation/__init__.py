"""音樂生成模組

包含各種音樂生成服務和工具
"""

import os
import importlib
import logging
from typing import Dict, Any, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)

# 環境變量設置
USE_MOCK = os.environ.get("USE_MOCK_MAGENTA", "true").lower() == "true"

# 檢查 Magenta 是否可用
MAGENTA_AVAILABLE = False
try:
    import magenta
    MAGENTA_AVAILABLE = True
    logger.info("成功導入 Magenta 模組")
except ImportError:
    logger.warning("無法導入 Magenta 模組，將使用模擬服務")

# 根據環境條件選擇適當的服務
if USE_MOCK or not MAGENTA_AVAILABLE:
    try:
        from .mock_magenta_service import MagentaService
        logger.info("使用模擬 Magenta 服務")
    except ImportError as e:
        try:
            from .magenta_service import MagentaService
            logger.warning("使用真實 Magenta 服務（因模擬服務不可用），但部分功能可能受限")
        except ImportError:
            logger.error("無法導入任何 Magenta 服務，音樂生成功能將不可用")
            
            # 創建一個最小化的服務以避免程序崩潰
            class MagentaService:
                def __init__(self, *args, **kwargs):
                    logger.error("使用最小服務，大多數功能將返回空結果")
                
                def generate_melody(self, *args, **kwargs):
                    return []
                
                def generate_accompaniment(self, *args, **kwargs):
                    return {"chords": [], "bass": []}
                
                def generate_drum_pattern(self, *args, **kwargs):
                    return []
                
                def melody_to_midi(self, *args, **kwargs):
                    return ""
                
                def generate_full_arrangement(self, *args, **kwargs):
                    return {"melody": [], "chords": [], "bass": [], "drums": []}
else:
    try:
        from .magenta_service import MagentaService
        logger.info("使用真實 Magenta 服務")
    except ImportError:
        logger.warning("無法導入真實 Magenta 服務，將回退使用模擬服務")
        try:
            from .mock_magenta_service import MagentaService
            logger.info("回退使用模擬 Magenta 服務")
        except ImportError:
            logger.error("無法導入任何 Magenta 服務，音樂生成功能將不可用")
            
            # 創建一個最小化的服務以避免程序崩潰
            class MagentaService:
                def __init__(self, *args, **kwargs):
                    logger.error("使用最小服務，大多數功能將返回空結果")
                
                def generate_melody(self, *args, **kwargs):
                    return []
                
                def generate_accompaniment(self, *args, **kwargs):
                    return {"chords": [], "bass": []}
                
                def generate_drum_pattern(self, *args, **kwargs):
                    return []
                
                def melody_to_midi(self, *args, **kwargs):
                    return ""
                
                def generate_full_arrangement(self, *args, **kwargs):
                    return {"melody": [], "chords": [], "bass": [], "drums": []}

# 添加輔助函數
def get_service_status():
    """獲取服務狀態信息
    
    Returns:
        dict: 包含服務狀態的字典
    """
    return {
        "mock_mode": USE_MOCK,
        "magenta_available": MAGENTA_AVAILABLE,
        "service_type": "模擬" if (USE_MOCK or not MAGENTA_AVAILABLE) else "真實"
    }

# 導出主要類
try:
    from .magenta_service import MagentaService
except ImportError as e:
    logging.warning(f"無法導入 MagentaService: {str(e)}")

# 導出自動編曲模組
try:
    from .accompaniment_generator import ChordGenerator, AccompanimentGenerator
except ImportError as e:
    logging.warning(f"無法導入自動編曲模組: {str(e)}")

# 版本
__version__ = '0.1.0'

# 匯出 MagentaService
from .magenta_service import MagentaService
from .mock_magenta_service import MagentaService as MockMagentaService

# 匯出 Performance RNN 服務
from .performance_rnn_service import PerformanceRNNService

# 匯出 Music VAE 服務
from .music_vae_service import MusicVAEService

# 匯出新的模組
from .magenta_model_manager import (
    MagentaModelManager, 
    ModelType, 
    ModelConfiguration,
    EvaluationMetrics
)

from .timbre_engine import (
    TimbreEngine,
    TimbreInstrument,
    TimbrePreset
)

from .harmony_optimizer import (
    HarmonyOptimizer,
    Scale,
    ChordType,
    Chord,
    KeySignature
)

try:
    from .llm_music_generator import LLMMusicGenerator, LLMProviderType, LLMGenerationConfig

    # 導出所有類
    __all__ = [
        'MagentaService',
        'MockMagentaService',
        'MusicVAEService',
        'PerformanceRNNService',
        'HarmonyOptimizer',
        'Scale',
        'ChordType',
        'TimbreEngine',
        'SoundFont',
        'MagentaModelManager',
        'ModelType',
        'ModelConfiguration',
        'EvaluationMetrics',
        'LLMMusicGenerator',
        'LLMProviderType',
        'LLMGenerationConfig'
    ]
    
    logger.info("已成功加載音樂生成模組")
    
except ImportError as e:
    logger.warning(f"加載音樂生成模組時發生錯誤: {str(e)}")
    
    # 定義假的類以避免導入錯誤
    class MagentaService:
        pass
    
    class MockMagentaService:
        pass
    
    class MusicVAEService:
        pass
    
    class PerformanceRNNService:
        pass
    
    class HarmonyOptimizer:
        pass
    
    class Scale:
        MAJOR = "major"
        MINOR = "minor"
    
    class ChordType:
        MAJOR = "major"
        MINOR = "minor"
    
    class TimbreEngine:
        pass
    
    class SoundFont:
        pass
    
    class MagentaModelManager:
        pass
    
    class ModelType:
        pass
    
    class ModelConfiguration:
        pass
    
    class EvaluationMetrics:
        pass
    
    class LLMMusicGenerator:
        pass
    
    class LLMProviderType:
        pass
    
    class LLMGenerationConfig:
        pass
    
    __all__ = [
        'MagentaService',
        'MockMagentaService',
        'MusicVAEService',
        'PerformanceRNNService',
        'HarmonyOptimizer',
        'Scale',
        'ChordType',
        'TimbreEngine',
        'SoundFont',
        'MagentaModelManager',
        'ModelType',
        'ModelConfiguration',
        'EvaluationMetrics',
        'LLMMusicGenerator',
        'LLMProviderType',
        'LLMGenerationConfig'
    ] 