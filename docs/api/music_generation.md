# 音樂生成 API 參考文檔

本文檔提供了 AI 音樂創作助手的音樂生成 API 的詳細說明。

## MagentaService 類

`MagentaService` 是音樂生成的核心服務類，提供了多種音樂生成功能。

### 初始化

```python
def __init__(self, model_path_dict: Optional[Dict[str, str]] = None)
```

**參數:**
- `model_path_dict`: 模型路徑字典，如 `{"melody_rnn": "/path/to/model"}`

**說明:**
初始化 Magenta 服務，加載必要的模型。

### 生成旋律

```python
def generate_melody(self, 
                   parameters: MusicParameters, 
                   primer_melody: Optional[List[Note]] = None,
                   num_steps: int = 128,
                   temperature: float = 1.0) -> List[Note]
```

**參數:**
- `parameters`: 音樂參數，包含調性、速度等設置
- `primer_melody`: 引導旋律，如果提供則基於此旋律繼續生成
- `num_steps`: 生成的步數
- `temperature`: 生成的溫度參數，越高結果越隨機

**返回:**
- `List[Note]`: 生成的旋律音符列表

**說明:**
根據提供的參數生成旋律。可以選擇性地提供一個引導旋律，系統將基於此生成後續部分。

### 生成伴奏

```python
def generate_accompaniment(self, 
                          melody: List[Note], 
                          parameters: MusicParameters) -> Dict[str, List[Note]]
```

**參數:**
- `melody`: 主旋律音符列表
- `parameters`: 音樂參數

**返回:**
- `Dict[str, List[Note]]`: 各聲部伴奏音符，如 `{"chords": [...], "bass": [...]}`

**說明:**
為給定的旋律生成配和的伴奏，包括和弦和低音部分。

### 生成鼓點模式

```python
def generate_drum_pattern(self, 
                         parameters: MusicParameters, 
                         num_measures: int = 4) -> List[Note]
```

**參數:**
- `parameters`: 音樂參數
- `num_measures`: 小節數

**返回:**
- `List[Note]`: 鼓點音符列表

**說明:**
生成符合音樂風格的鼓點模式。

### 文本到旋律轉換

```python
def text_to_melody(self, text: str, parameters: MusicParameters) -> List[Note]
```

**參數:**
- `text`: 文本描述
- `parameters`: 音樂參數

**返回:**
- `List[Note]`: 生成的旋律音符列表

**說明:**
根據文本描述生成旋律。可以使用自然語言描述想要的音樂風格和情感。

### 生成完整編曲

```python
def generate_full_arrangement(self,
                             melody: Optional[List[Note]] = None,
                             parameters: Optional[MusicParameters] = None,
                             suggested_models: Optional[List[str]] = None) -> Dict[str, Any]
```

**參數:**
- `melody`: 主旋律，如未提供則自動生成
- `parameters`: 音樂參數
- `suggested_models`: 推薦使用的模型列表

**返回:**
- `Dict[str, Any]`: 包含各聲部的完整編曲

**說明:**
生成包含主旋律、和弦、低音和鼓點的完整音樂編曲。

### 旋律轉MIDI

```python
def melody_to_midi(self, melody: List[Note], output_path: str, tempo: int = 120) -> str
```

**參數:**
- `melody`: 旋律音符列表
- `output_path`: 輸出 MIDI 文件路徑
- `tempo`: 速度 (BPM)

**返回:**
- `str`: MIDI 文件路徑

**說明:**
將旋律轉換為 MIDI 文件格式，便於在其他音樂軟件中使用。

### 編曲轉音頻

```python
def create_audio_from_arrangement(self, 
                                 arrangement: Dict[str, List[Note]], 
                                 parameters: MusicParameters) -> str
```

**參數:**
- `arrangement`: 編曲，包含各個部分的音符
- `parameters`: 音樂參數

**返回:**
- `str`: Base64編碼的音頻數據

**說明:**
將編曲轉換為可播放的音頻格式，返回Base64編碼的數據。

### 生成封面圖片

```python
def generate_cover_image(self, 
                        melody: List[Note], 
                        parameters: MusicParameters) -> str
```

**參數:**
- `melody`: 旋律音符列表
- `parameters`: 音樂參數

**返回:**
- `str`: Base64編碼的圖片數據

**說明:**
根據音樂內容生成適合的封面圖片。

## 使用示例

```python
# 初始化服務
magenta_service = MagentaService()

# 創建音樂參數
from backend.mcp.mcp_schema import MusicParameters, Genre
params = MusicParameters(
    tempo=120,
    key="C",
    genre=Genre.POP,
    description="輕快的流行音樂"
)

# 從文本生成旋律
melody = magenta_service.text_to_melody("輕快活潑的夏日旋律", params)

# 生成完整編曲
arrangement = magenta_service.generate_full_arrangement(melody, params)

# 轉換為MIDI文件
midi_path = magenta_service.melody_to_midi(melody, "output.mid", params.tempo)

# 生成音頻
audio_data = magenta_service.create_audio_from_arrangement(arrangement, params)
```

## 進階用法

請參考 [進階音樂生成指南](../user_guide/features/advanced_generation.md) 了解更多高級用法和技巧。 