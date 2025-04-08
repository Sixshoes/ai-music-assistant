"""模型協調器模組

負責協調不同AI模型和工具間的工作流程，實現從指令到音樂生成的完整過程
"""

from .coordinator import ModelCoordinator
from .workflow import (
    TextToMusicWorkflow, 
    MelodyToArrangementWorkflow, 
    MusicAnalysisWorkflow,
    PitchCorrectionWorkflow,
    StyleTransferWorkflow,
    ImprovisationWorkflow
)
from .model_selector import ModelSelector
from .model_interface import (
    ModelInterface, 
    MagentaInterface, 
    Music21Interface, 
    BasicPitchInterface,
    ModelInterfaceFactory
)
from .logging_service import LoggingService, setup_logger
from .config import Config

__all__ = [
    "ModelCoordinator",
    "TextToMusicWorkflow",
    "MelodyToArrangementWorkflow",
    "MusicAnalysisWorkflow",
    "PitchCorrectionWorkflow",
    "StyleTransferWorkflow",
    "ImprovisationWorkflow",
    "ModelSelector",
    "ModelInterface",
    "MagentaInterface",
    "Music21Interface",
    "BasicPitchInterface",
    "ModelInterfaceFactory",
    "LoggingService",
    "setup_logger",
    "Config"
] 