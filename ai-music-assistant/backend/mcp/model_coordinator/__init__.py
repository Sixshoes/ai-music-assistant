"""模型協調器模組

提供協調模型和工作流程的功能
"""

from .coordinator import ModelCoordinator
from .workflow import TextToMusicWorkflow
from .music_generator import MusicGenerator
from .score_generator import ScoreGenerator
from .analysis import MusicAnalysis
from .logger import setup_logger
from .config import Config
from .utils import save_command, get_command

__all__ = [
    'ModelCoordinator',
    'TextToMusicWorkflow',
    'MusicGenerator',
    'ScoreGenerator',
    'MusicAnalysis',
    'setup_logger',
    'Config',
    'save_command',
    'get_command'
] 