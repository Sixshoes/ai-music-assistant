# AI 音樂助手 API 參考文檔

## 基本信息

- 基礎URL: `http://localhost:8000`
- API前綴: `/api`
- 接受和返回格式: JSON

## 認證

目前API不需要認證，但未來可能會添加基於JWT的認證機制。

## 錯誤處理

所有API錯誤都會返回適當的HTTP狀態碼和包含錯誤詳情的JSON響應:

```json
{
  "detail": "錯誤信息描述"
}
```

## API端點

### 1. 文字到音樂轉換

將自然語言描述轉換為音樂。

**請求**

```
POST /api/text-to-music
```

**請求體**

```json
{
  "text": "一首輕快的C大調流行歌曲，有鋼琴和弦樂，適合電影開場",
  "parameters": {
    "tempo": 120,
    "key": "C",
    "genre": "pop",
    "instruments": ["piano", "strings"]
  }
}
```

**響應**

```json
{
  "message": "文字指令已接收，正在處理",
  "command_id": "abc123def456"
}
```

### 2. 音頻到編曲轉換

將錄製的旋律轉換為完整編曲。

**請求**

```
POST /api/audio-to-music
```

**請求體**

```json
{
  "audio_data_url": "data:audio/wav;base64,BASE64_ENCODED_AUDIO_DATA",
  "additional_text": "流行風格編曲，C大調",
  "parameters": {
    "tempo": 120,
    "key": "C",
    "genre": "pop",
    "instruments": ["piano", "guitar", "bass", "drums"]
  }
}
```

**響應**

```json
{
  "message": "音頻指令已接收，正在處理",
  "command_id": "abc123def456"
}
```

### 3. 獲取指令處理狀態

檢查指令處理狀態。

**請求**

```
POST /api/command-status
```

**請求體**

```json
{
  "command_id": "abc123def456"
}
```

**響應**

```json
{
  "status": "completed", // or "processing", "error", "not_found"
  "command_type": "text_to_music"
}
```

### 4. 取消處理指令

取消正在處理的指令。

**請求**

```
DELETE /api/cancel-command/{command_id}
```

**響應**

```json
{
  "message": "指令已取消",
  "command_id": "abc123def456"
}
```

### 5. 獲取音樂生成結果

當指令處理完成後，獲取音樂生成結果。

**請求**

```
GET /api/music-result/{command_id}
```

**響應**

```json
{
  "music_data": {
    "midi_data": "BASE64_ENCODED_MIDI_DATA",
    "audio_data": "BASE64_ENCODED_AUDIO_DATA",
    "score_data": {
      "musicxml": "MUSICXML_DATA",
      "pdf": "BASE64_ENCODED_PDF_DATA"
    }
  },
  "analysis": {
    "key": "C",
    "chord_progression": {
      "chords": ["C", "Am", "F", "G"],
      "durations": [1.0, 1.0, 1.0, 1.0]
    },
    "time_signature": "4/4",
    "tempo": 120,
    "structure": {
      "verse": [1, 5, 9, 13],
      "chorus": [17, 21, 25, 29]
    },
    "harmony_issues": [],
    "suggestions": [
      "嘗試在副歌部分增加更強的力度對比",
      "考慮使用更豐富的和弦延伸音"
    ]
  }
}
```

## 數據模型

### 音樂參數

```typescript
interface MusicParameters {
  key?: string;        // 調性，例如 "C", "Am"
  tempo?: number;      // 速度 (BPM)，範圍 40-240
  time_signature?: string;  // 拍號，例如 "4/4", "3/4"
  genre?: string;      // 風格，例如 "pop", "jazz"
  emotion?: string;    // 情感，例如 "happy", "sad"
  instruments?: string[];  // 樂器列表
  duration?: number;   // 音樂長度 (秒)
}
```

### 音樂理論分析結果

```typescript
interface MusicTheoryAnalysis {
  key: string;         // 偵測到的調性
  chord_progression: {
    chords: string[];  // 和弦標記列表
    durations: number[];  // 每個和弦的持續時間
  };
  time_signature: string;  // 偵測到的拍號
  tempo: number;       // 偵測到的速度 (BPM)
  structure: {         // 結構分析
    [section: string]: number[];  // 段落標記和小節數
  };
  harmony_issues?: string[];  // 和聲問題清單
  suggestions?: string[];  // 改進建議
}
```

## 狀態碼

- `200 OK`: 請求成功完成
- `202 Accepted`: 請求已接受，但處理尚未完成
- `400 Bad Request`: 請求無效或格式錯誤
- `404 Not Found`: 找不到資源
- `500 Internal Server Error`: 伺服器內部錯誤

## 使用限制

- 音頻文件大小限制: 10MB
- 處理時間限制: 60秒/請求
- 速率限制: 10個請求/分鐘 