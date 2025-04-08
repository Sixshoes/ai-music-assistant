# REST API 參考文檔

本文檔提供了 AI 音樂創作助手的 REST API 詳細說明。這些 API 端點允許開發者與系統交互，生成、處理和管理音樂內容。

## 身份認證

所有 API 請求都需要身份認證。使用 Bearer 令牌進行身份驗證：

```
Authorization: Bearer YOUR_API_KEY
```

## 基礎 URL

```
https://api.ai-music-assistant.com/v1
```

## 音樂生成 API

### 從文本生成音樂

**端點:** `/generate/text-to-music`

**方法:** POST

**描述:** 根據文本描述生成音樂

**請求體:**
```json
{
  "text": "創作一首輕快活潑的夏日流行歌曲，有鋼琴和吉他伴奏",
  "parameters": {
    "tempo": 120,
    "key": "C",
    "genre": "pop",
    "duration": 60,
    "complexity": 3,
    "instruments": ["piano", "guitar", "drums"]
  },
  "output_format": "mp3"
}
```

**響應:**
```json
{
  "command_id": "20230415123456",
  "status": "pending",
  "estimated_time": 30
}
```

### 查詢生成狀態

**端點:** `/commands/{command_id}`

**方法:** GET

**描述:** 查詢命令處理狀態

**參數:**
- `command_id`: 命令ID

**響應:**
```json
{
  "command_id": "20230415123456",
  "status": "completed",
  "result": {
    "audio_url": "https://storage.ai-music-assistant.com/audio/20230415123456.mp3",
    "midi_url": "https://storage.ai-music-assistant.com/midi/20230415123456.mid",
    "sheet_music_url": "https://storage.ai-music-assistant.com/sheet/20230415123456.pdf",
    "duration": 60,
    "tempo": 120,
    "key": "C",
    "genre": "pop"
  },
  "created_at": "2023-04-15T12:34:56Z",
  "completed_at": "2023-04-15T12:35:26Z"
}
```

### 提交旋律生成伴奏

**端點:** `/generate/accompaniment`

**方法:** POST

**描述:** 為上傳的旋律生成伴奏

**請求體:**
```json
{
  "midi_data": "base64_encoded_midi_data...",
  "parameters": {
    "genre": "jazz",
    "complexity": 4,
    "instruments": ["piano", "bass", "drums"]
  },
  "output_format": "mp3"
}
```

**響應:**
```json
{
  "command_id": "20230415123457",
  "status": "pending",
  "estimated_time": 20
}
```

## 音樂編輯 API

### 修改音樂參數

**端點:** `/edit/parameters`

**方法:** POST

**描述:** 修改已生成音樂的參數

**請求體:**
```json
{
  "music_id": "20230415123456",
  "parameters": {
    "tempo": 130,
    "key": "G",
    "instruments": ["piano", "guitar", "bass", "drums"]
  }
}
```

**響應:**
```json
{
  "command_id": "20230415123458",
  "status": "pending",
  "estimated_time": 15
}
```

### 混合音樂片段

**端點:** `/edit/mix`

**方法:** POST

**描述:** 混合多個音樂片段

**請求體:**
```json
{
  "segments": [
    {
      "music_id": "20230415123456",
      "start_time": 0,
      "duration": 30
    },
    {
      "music_id": "20230415123457",
      "start_time": 0,
      "duration": 30
    }
  ],
  "crossfade_duration": 5,
  "output_format": "mp3"
}
```

**響應:**
```json
{
  "command_id": "20230415123459",
  "status": "pending",
  "estimated_time": 25
}
```

## 音樂分析 API

### 分析音樂特性

**端點:** `/analyze/features`

**方法:** POST

**描述:** 分析音樂特性

**請求體:**
```json
{
  "audio_url": "https://storage.ai-music-assistant.com/audio/20230415123456.mp3"
}
```

**響應:**
```json
{
  "command_id": "20230415123460",
  "status": "completed",
  "result": {
    "tempo": 122,
    "key": "C",
    "time_signature": "4/4",
    "genre_probabilities": {
      "pop": 0.8,
      "rock": 0.15,
      "electronic": 0.05
    },
    "mood": "upbeat",
    "energy": 0.75,
    "danceability": 0.82
  }
}
```

### 提取音樂元素

**端點:** `/analyze/extract`

**方法:** POST

**描述:** 從音頻中提取音樂元素

**請求體:**
```json
{
  "audio_url": "https://storage.ai-music-assistant.com/audio/20230415123456.mp3",
  "elements": ["melody", "chords", "beats"]
}
```

**響應:**
```json
{
  "command_id": "20230415123461",
  "status": "pending",
  "estimated_time": 30
}
```

## 資源管理 API

### 列出用戶音樂

**端點:** `/resources/music`

**方法:** GET

**描述:** 列出用戶的音樂資源

**參數:**
- `page`: 頁碼（默認為1）
- `limit`: 每頁數量（默認為20）
- `sort_by`: 排序依據（created_at, title, duration）
- `sort_order`: 排序順序（asc, desc）

**響應:**
```json
{
  "total": 42,
  "page": 1,
  "limit": 20,
  "items": [
    {
      "id": "20230415123456",
      "title": "輕快的夏日旋律",
      "description": "創作一首輕快活潑的夏日流行歌曲，有鋼琴和吉他伴奏",
      "duration": 60,
      "genre": "pop",
      "created_at": "2023-04-15T12:34:56Z",
      "audio_url": "https://storage.ai-music-assistant.com/audio/20230415123456.mp3",
      "midi_url": "https://storage.ai-music-assistant.com/midi/20230415123456.mid"
    },
    // ...更多項目
  ]
}
```

### 刪除音樂資源

**端點:** `/resources/music/{music_id}`

**方法:** DELETE

**描述:** 刪除音樂資源

**參數:**
- `music_id`: 音樂資源ID

**響應:**
```json
{
  "success": true,
  "message": "音樂資源已刪除"
}
```

## 錯誤處理

所有 API 在發生錯誤時都會返回以下格式的響應：

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "錯誤描述",
    "details": {
      // 可選的錯誤詳情
    }
  }
}
```

### 常見錯誤代碼

- `INVALID_REQUEST`: 請求格式或參數無效
- `AUTHENTICATION_ERROR`: 身份驗證失敗
- `PERMISSION_DENIED`: 沒有權限執行操作
- `RESOURCE_NOT_FOUND`: 請求的資源不存在
- `GENERATION_FAILED`: 音樂生成失敗
- `PROCESSING_ERROR`: 處理過程中發生錯誤
- `RATE_LIMIT_EXCEEDED`: 超出 API 使用限制
- `INTERNAL_ERROR`: 內部服務器錯誤

## 速率限制

API 有以下速率限制：

- 基本用戶：每分鐘 10 個請求，每天 100 個請求
- 專業用戶：每分鐘 30 個請求，每天 500 個請求
- 企業用戶：自定義限制

超出限制時，API 將返回 `429 Too Many Requests` 狀態碼和 `RATE_LIMIT_EXCEEDED` 錯誤。

## 更多資源

- [API SDK 與代碼示例](../development/sdk.md)
- [API 客戶端工具](../tools/api_clients.md)
- [最佳實踐與優化](../guides/api_best_practices.md) 