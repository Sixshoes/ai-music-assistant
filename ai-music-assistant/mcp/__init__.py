"""
音樂創作處理 (Music Creation Processing) 模塊

提供音樂創作、處理和分析的統一接口和數據模型
"""

# 嘗試導入完整版 mcp_schema，如果失敗則使用簡化版
try:
    # 導出主要的類和枚舉
    from .mcp_schema import (
        CommandType,
        ModelType,
        ProcessingStatus,
        CommandStatus,
        MusicKey,
        TimeSignature,
        Genre,
        Emotion,
        InstrumentType,
        MusicalForm,
        Note,
        MelodyInput,
        AudioInput,
        ChordProgression,
        MusicParameters,
        ScoreData,
        MusicData,
        MusicTheoryAnalysis,
        MCPCommand,
        MCPResponse
    )
except ImportError:
    import logging
    logging.warning("無法導入完整版 mcp_schema，使用簡化版 mcp_schema_simple")
    
    # 使用簡化版
    from .mcp_schema_simple import (
        CommandType,
        ModelType,
        ProcessingStatus,
        CommandStatus,
        MusicKey,
        TimeSignature,
        Genre,
        Emotion,
        InstrumentType,
        MusicalForm,
        Note,
        MelodyInput,
        AudioInput,
        ChordProgression,
        MusicParameters,
        ScoreData,
        MusicData,
        MusicTheoryAnalysis,
        MCPCommand,
        MCPResponse
    )

__all__ = [
    'CommandType',
    'ModelType',
    'ProcessingStatus',
    'CommandStatus',
    'MusicKey',
    'TimeSignature',
    'Genre',
    'Emotion',
    'InstrumentType',
    'MusicalForm',
    'Note',
    'MelodyInput',
    'AudioInput',
    'ChordProgression',
    'MusicParameters',
    'ScoreData',
    'MusicData',
    'MusicTheoryAnalysis',
    'MCPCommand',
    'MCPResponse'
] 