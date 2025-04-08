"""MCP 包

音樂創作處理器包
"""

from .mcp_schema import *
from .model_coordinator import *
from .command_parser import *

__all__ = [
    'MCPCommand',
    'MCPResponse',
    'MusicParameters',
    'CommandStatus',
    'MusicKey',
    'Genre',
    'InstrumentType',
    'TimeSignature',
    'ModelCoordinator',
    'TextToMusicWorkflow',
    'MusicGenerator',
    'ScoreGenerator',
    'MusicAnalysis',
    'setup_logger',
    'Config',
    'TextCommandParser',
    'AudioCommandParser'
]

__version__ = "1.0.0" 