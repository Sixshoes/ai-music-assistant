"""異常定義模組"""

class MCPError(Exception):
    """MCP基礎異常類"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class CommandNotFoundError(MCPError):
    """找不到命令異常"""
    def __init__(self, command_id: str):
        super().__init__(f"找不到命令: {command_id}")

class CommandProcessingError(MCPError):
    """命令處理異常"""
    def __init__(self, command_id: str, message: str):
        super().__init__(f"處理命令 {command_id} 時發生錯誤: {message}")

class AudioGenerationError(MCPError):
    """音頻生成異常"""
    def __init__(self, message: str):
        super().__init__(f"生成音頻時發生錯誤: {message}")

class ScoreGenerationError(MCPError):
    """樂譜生成異常"""
    def __init__(self, message: str):
        super().__init__(f"生成樂譜時發生錯誤: {message}")

class InvalidParameterError(MCPError):
    """無效參數異常"""
    def __init__(self, parameter: str, message: str):
        super().__init__(f"參數 {parameter} 無效: {message}")

class MIDIGenerationError(MCPError):
    """MIDI生成異常"""
    def __init__(self, message: str):
        super().__init__(f"生成MIDI時發生錯誤: {message}")

class SoundFontNotFoundError(MCPError):
    """找不到音色庫異常"""
    def __init__(self, path: str):
        super().__init__(f"找不到音色庫文件: {path}")

class AudioConversionError(MCPError):
    """音頻轉換異常"""
    def __init__(self, message: str):
        super().__init__(f"轉換音頻時發生錯誤: {message}") 