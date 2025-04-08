# 音樂創作處理模型 (MCP) API 參考文檔

本文檔提供了 MCP (Music Creation Processing) 模型的詳細 API 說明。MCP 是 AI 音樂創作助手的核心數據模型，定義了音樂生成和處理所需的各種數據結構。

## 核心枚舉類型

### MusicKey

```python
class MusicKey(str, Enum):
    """音樂調性枚舉"""
    C_MAJOR = "C"
    G_MAJOR = "G"
    # ... 其他調性
    A_MINOR = "Am"
    E_MINOR = "Em"
    # ... 其他小調
```

**說明:**
定義了支持的音樂調性，包括大調和小調。

### TimeSignature

```python
class TimeSignature(str, Enum):
    """拍號枚舉"""
    TWO_FOUR = "2/4"
    THREE_FOUR = "3/4"
    FOUR_FOUR = "4/4"
    THREE_EIGHT = "3/8"
    SIX_EIGHT = "6/8"
    NINE_EIGHT = "9/8"
    TWELVE_EIGHT = "12/8"
```

**說明:**
定義了支持的拍號。

### Genre

```python
class Genre(str, Enum):
    """音樂風格枚舉"""
    POP = "pop"
    ROCK = "rock"
    JAZZ = "jazz"
    CLASSICAL = "classical"
    ELECTRONIC = "electronic"
    # ... 其他風格
```

**說明:**
定義了支持的音樂風格。

### InstrumentType

```python
class InstrumentType(str, Enum):
    """樂器類型枚舉"""
    PIANO = "piano"
    GUITAR = "guitar"
    BASS = "bass"
    DRUMS = "drums"
    # ... 其他樂器
```

**說明:**
定義了支持的樂器類型。

### CommandStatus

```python
class CommandStatus(str, Enum):
    """命令狀態枚舉"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

**說明:**
定義了命令處理的各種狀態。

## 核心數據模型

### Note

```python
class Note(BaseModel):
    """音符模型"""
    pitch: int = Field(..., description="MIDI音高 (0-127)", ge=0, le=127)
    start_time: float = Field(..., description="開始時間（秒）", ge=0)
    duration: float = Field(..., description="持續時間（秒）", gt=0)
    velocity: int = Field(64, description="力度 (1-127)", ge=1, le=127)
```

**屬性:**
- `pitch`: MIDI 音高，範圍 0-127
- `start_time`: 開始時間（秒）
- `duration`: 持續時間（秒）
- `velocity`: 力度（音量），範圍 1-127

**說明:**
定義了一個音符的基本屬性，包括音高、開始時間、持續時間和力度。

### MelodyInput

```python
class MelodyInput(BaseModel):
    """旋律輸入模型"""
    notes: List[Note] = Field(..., description="旋律音符序列")
    tempo: Optional[int] = Field(None, description="旋律速度", ge=40, le=240)
```

**屬性:**
- `notes`: 音符列表
- `tempo`: 旋律速度（可選）

**說明:**
用於表示輸入的旋律。

### MusicParameters

```python
class MusicParameters(BaseModel):
    """音樂參數模型"""
    description: str = Field(
        default="自動生成的音樂",
        description="音樂描述"
    )
    tempo: int = Field(
        default=120,
        ge=40,
        le=240,
        description="速度（每分鐘拍數）"
    )
    key: MusicKey = Field(
        default=MusicKey.C_MAJOR,
        description="調性"
    )
    time_signature: TimeSignature = Field(
        default=TimeSignature.FOUR_FOUR,
        description="拍號"
    )
    genre: Genre = Field(
        default=Genre.POP,
        description="音樂風格"
    )
    instruments: List[InstrumentType] = Field(
        default=[InstrumentType.PIANO],
        description="樂器列表"
    )
    duration: int = Field(
        default=60,
        ge=10,
        le=300,
        description="時長（秒）"
    )
    complexity: int = Field(
        default=3,
        ge=1,
        le=5,
        description="複雜度（1-5）"
    )
```

**屬性:**
- `description`: 音樂描述
- `tempo`: 速度（BPM）
- `key`: 調性
- `time_signature`: 拍號
- `genre`: 音樂風格
- `instruments`: 樂器列表
- `duration`: 時長（秒）
- `complexity`: 複雜度等級

**說明:**
用於定義音樂生成的各種參數，控制生成音樂的特性。

### MCPCommand

```python
class MCPCommand(BaseModel):
    """MCP命令模型"""
    command_id: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y%m%d%H%M%S"),
        description="命令ID"
    )
    type: str = Field(
        ...,
        description="命令類型"
    )
    text_input: Optional[str] = Field(
        None,
        description="文字輸入"
    )
    audio_input: Optional[str] = Field(
        None,
        description="音頻輸入（Base64編碼）"
    )
    parameters: Optional[MusicParameters] = Field(
        None,
        description="音樂參數"
    )
    status: CommandStatus = Field(
        default=CommandStatus.PENDING,
        description="命令狀態"
    )
    result: Optional[Dict[str, Any]] = Field(
        None,
        description="處理結果"
    )
    error: Optional[str] = Field(
        None,
        description="錯誤信息"
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="創建時間"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="更新時間"
    )
    completed_at: Optional[datetime] = Field(
        None,
        description="完成時間"
    )
```

**屬性:**
- `command_id`: 命令ID
- `type`: 命令類型
- `text_input`: 文字輸入（可選）
- `audio_input`: 音頻輸入（可選）
- `parameters`: 音樂參數（可選）
- `status`: 命令狀態
- `result`: 處理結果（可選）
- `error`: 錯誤信息（可選）
- `created_at`: 創建時間
- `updated_at`: 更新時間
- `completed_at`: 完成時間（可選）

**說明:**
表示一個 MCP 命令，包含命令的所有相關信息。

### MCPResponse

```python
class MCPResponse(BaseModel):
    """MCP響應模型"""
    command_id: str = Field(
        ...,
        description="命令ID"
    )
    status: CommandStatus = Field(
        ...,
        description="命令狀態"
    )
    result: Optional[Dict[str, Any]] = Field(
        None,
        description="處理結果"
    )
    error: Optional[str] = Field(
        None,
        description="錯誤信息"
    )
```

**屬性:**
- `command_id`: 命令ID
- `status`: 命令狀態
- `result`: 處理結果（可選）
- `error`: 錯誤信息（可選）

**說明:**
表示對 MCP 命令的響應。

## 使用示例

### 創建音樂參數

```python
from backend.mcp.mcp_schema import MusicParameters, Genre, MusicKey, TimeSignature, InstrumentType

# 創建音樂參數
params = MusicParameters(
    description="活潑的流行歌曲",
    tempo=128,
    key=MusicKey.C_MAJOR,
    time_signature=TimeSignature.FOUR_FOUR,
    genre=Genre.POP,
    instruments=[InstrumentType.PIANO, InstrumentType.GUITAR, InstrumentType.DRUMS],
    duration=120,
    complexity=4
)
```

### 創建命令

```python
from backend.mcp.mcp_schema import MCPCommand

# 創建文本到音樂的命令
command = MCPCommand(
    type="text_to_music",
    text_input="創作一首輕快活潑的夏日流行歌曲，有鋼琴和吉他伴奏",
    parameters=params
)

# 命令ID可以用於跟踪處理狀態
command_id = command.command_id
```

### 處理響應

```python
from backend.mcp.mcp_schema import MCPResponse, CommandStatus

# 假設這是從系統接收到的響應
response = MCPResponse(
    command_id="20230415123456",
    status=CommandStatus.COMPLETED,
    result={
        "midi_path": "/path/to/output.mid",
        "audio_data": "base64_encoded_audio...",
        "duration": 120,
        "tempo": 128
    }
)

# 檢查狀態
if response.status == CommandStatus.COMPLETED:
    # 處理結果
    midi_path = response.result.get("midi_path")
    audio_data = response.result.get("audio_data")
    # ...
elif response.status == CommandStatus.FAILED:
    # 處理錯誤
    error_message = response.error
    # ...
```

## 進階用法

請參考 [命令處理文檔](../architecture/command_processing.md) 了解更多關於 MCP 命令處理流程的信息。 