# API 文檔

## 音樂生成 API

### 生成音樂
- **端點**: `/generate`
- **方法**: POST
- **描述**: 根據文本描述使用 AI 生成音樂
- **請求體**:
```json
{
  "description": "創作一首平靜的古典音樂，帶有中國傳統元素，適合沉思和冥想",
  "use_llm": false
}
```
- **參數說明**:
  - `description` (必需): 音樂創作需求的文字描述
  - `use_llm` (可選): 是否使用大語言模型進行增強分析，默認為 false

- **響應**:
```json
{
  "status": "success",
  "message": "音樂生成成功",
  "filename": "generated_music_123456.mid",
  "details": {
    "original_description": "創作一首平靜的古典音樂，帶有中國傳統元素，適合沉思和冥想",
    "output_file": "/path/to/output/generated_music_123456.mid",
    "stages": {
      "requirement_analysis": {
        "genre": "古典",
        "mood": "平靜",
        "tempo": 80,
        "key": "C",
        "instruments": ["piano", "guzheng", "dizi"]
      }
    }
  }
}
```

### 下載音樂文件
- **端點**: `/download/<filename>`
- **方法**: GET
- **描述**: 下載生成的MIDI音樂文件
- **路徑參數**:
  - `filename`: 生成音樂時返回的文件名

- **響應**: MIDI文件（二進制數據流）

## 錯誤處理

所有 API 在發生錯誤時都會返回以下格式的響應：

```json
{
  "status": "error",
  "message": "錯誤描述"
}
```

常見錯誤代碼：
- `400 Bad Request`: 請求參數無效或缺失
- `404 Not Found`: 請求的資源不存在
- `500 Internal Server Error`: 服務器內部錯誤

## 完整使用示例

### 步驟1: 生成音樂

```javascript
const response = await fetch('http://localhost:5000/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    description: '創作一首輕快的爵士音樂，適合咖啡廳播放',
    use_llm: false
  })
});

const result = await response.json();

if (result.status === 'success') {
  console.log(`音樂已生成，文件名: ${result.filename}`);
  // 使用結果的filename下載文件
} else {
  console.error(`生成失敗: ${result.message}`);
}
```

### 步驟2: 下載生成的音樂

```javascript
// 使用上一步獲取的文件名
const filename = result.filename;
window.location.href = `http://localhost:5000/download/${filename}`;
```

或使用HTML音頻播放器直接播放：

```html
<audio controls>
  <source src="http://localhost:5000/download/${filename}" type="audio/midi">
  您的瀏覽器不支持MIDI音頻播放。
</audio>
```

## 使用提示

1. 描述越詳細，生成的音樂越符合預期
2. 如果需要特定風格、情感或樂器，請在描述中明確指出
3. 使用大語言模型進行增強分析可以提供更精確的理解，但會增加處理時間
4. 生成的MIDI文件可以在任何支持MIDI的音樂軟件中打開和編輯

## 音頻處理 API

### 生成音樂
- **端點**: `/api/generate-music`
- **方法**: POST
- **描述**: 使用 AI 生成音樂
- **請求體**:
```json
{
  "prompt": "音樂風格描述",
  "duration": 30,
  "format": "mp3"
}
```
- **響應**:
```json
{
  "success": true,
  "audioUrl": "生成的音頻 URL",
  "duration": 30
}
```

### 驗證音頻
- **端點**: `/api/validate-audio`
- **方法**: POST
- **描述**: 驗證音頻文件的格式和質量
- **請求體**:
```json
{
  "audioUrl": "要驗證的音頻 URL"
}
```
- **響應**:
```json
{
  "valid": true,
  "format": "mp3",
  "duration": 30,
  "sampleRate": 44100
}
```

## 資源管理 API

### 預加載資源
- **端點**: `/api/preload-resources`
- **方法**: POST
- **描述**: 預加載必要的資源
- **請求體**:
```json
{
  "resources": [
    "resource1.mp3",
    "resource2.png"
  ]
}
```
- **響應**:
```json
{
  "success": true,
  "loadedResources": [
    "resource1.mp3",
    "resource2.png"
  ]
}
``` 