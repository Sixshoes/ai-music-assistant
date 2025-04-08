# AI音樂創作助手

## 項目概述

這是一個基於AI的音樂創作輔助系統，能夠根據用戶的文字描述和意圖，自動分析並創作出符合要求的音樂。系統融合了自然語言理解、音樂理論和人工智能技術，提供從錄音、分析、編曲到生成的完整音樂創作流程。

## 主要功能特色

- **自然語言輸入**：使用自然語言描述您想要的音樂
- **意圖理解分析**：自動分析用戶描述中的風格、情感、速度、樂器等元素
- **增強型音頻錄製**：即時波形顯示，多段錄音管理，暫停繼續功能
- **專業音頻處理**：音高檢測與校正，音頻分析，音頻轉MIDI
- **自動編曲系統**：基於旋律自動生成和弦進行和多軌伴奏
- **AI輔助創作**：旋律補全，風格匹配，編曲建議
- **MIDI輸出**：產生標準MIDI檔案，支援播放與匯出

## 技術架構

- **前端**：React + TypeScript
- **後端**：FastAPI + Python
- **音頻處理**：使用Basic Pitch (Spotify)進行音高檢測
- **編曲系統**：自研音樂理論引擎，支援多種風格
- **AI模型**：整合Magenta音樂生成模型

## 系統工作原理

### 三階段創作流程

本系統採用「文本→參數→音樂」的三階段創作流程：

1. **意圖分析階段**
   - 分析用戶描述中的關鍵音樂元素
   - 識別音樂風格、情感氛圍、速度要求
   - 辨識特定樂器與文化元素等需求

2. **參數生成階段**
   - 將分析結果轉換為具體的音樂參數
   - 設定適合的和聲、節奏與旋律特徵
   - 基於風格模板調整參數值

3. **音樂創作階段**
   - 根據參數生成和弦進行
   - 創作符合風格和情感的旋律線條
   - 生成配合的低音聲部
   - 完成多聲部MIDI檔案

## 最新功能更新

### 完整時長音樂生成
- **延長音樂時長**：系統現在默認生成3分鐘(180秒)的完整音樂，提供完整的音樂體驗
- **結構化音樂創作**：音樂具有完整的起承轉合結構，包含前奏、主歌、副歌、橋段和尾聲等
- **動態發展曲線**：音樂隨時間推移具有自然的張力起伏，避免單調重複

### 動態風格生成
- **語言模型驅動的風格特徵**：不再依賴硬編碼的風格定義，而是使用大型語言模型動態生成風格特性
- **增強型音樂需求分析**：改進的分析器能夠更精確地提取用戶指定的音樂理論參數
- **融合型風格創作**：支援創建混合多種風格特徵的音樂，超越傳統風格分類的限制

### 多樂器編配強化
- **自動化樂器分配**：系統可根據音樂風格自動分配適合的樂器組合
- **多音軌處理**：每個樂器擁有獨立的音軌，實現更豐富的音樂層次感
- **角色化樂器設計**：根據樂器特性分配旋律、和聲、低音或打擊樂角色

### 樂理知識升級
- **增強的和弦處理**：支援複雜和弦進行、調式互換和轉調
- **豐富的和聲色彩**：根據音樂風格動態添加七和弦、九和弦等色彩音
- **精細的節奏控制**：支援多樣化的節奏型態和微妙的時值變化

## 安裝指南

### 基本依賴安裝

```bash
# 創建虛擬環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝基本依賴
pip install -r requirements.txt
```

### 可選依賴安裝

完整功能需要額外的庫，尤其是Magenta。如需完整功能，請安裝：

```bash
# 安裝TensorFlow (CPU版本)
pip install tensorflow>=2.12.0

# 安裝Magenta相關庫
pip install note-seq>=0.0.5
pip install magenta>=2.1.4

# 安裝FluidSynth (用於MIDI合成)
# MacOS: brew install fluidsynth
# Ubuntu: apt-get install fluidsynth
pip install pyfluidsynth>=0.2
```

## 啟動服務

### 啟動後端

```bash
cd ai-music-assistant
uvicorn backend.main:app --reload
```

### 啟動前端

```bash
cd ai-music-assistant/frontend
npm install
npm start
```

## 使用方法

### 命令行使用

使用命令行參數運行腳本：

```bash
python intention_based_music.py --description "創作一首平靜的古典音樂，帶有中國傳統元素，適合沉思和冥想。" --output output/meditation.mid --play
```

參數說明：
- `--description` 或 `-d`：音樂創作需求的文字描述（必要）
- `--output` 或 `-o`：輸出的MIDI文件路徑（預設為 output/intention_music.mid）
- `--play` 或 `-p`：生成後立即播放MIDI音樂
- `--debug`：啟用調試模式，顯示更多日誌信息

### 範例使用

以下是幾個使用範例：

1. 生成中國風古典音樂：
```bash
python intention_based_music.py --description "創作一首平靜的古典音樂，帶有中國傳統元素，適合沉思和冥想。請使用古箏和笛子作為主要樂器，速度緩慢而優雅。" --output output/chinese_meditation.mid
```

2. 生成咖啡廳爵士音樂：
```bash
python intention_based_music.py --description "創作一首歡快的爵士音樂，適合咖啡廳播放，帶有即興的感覺。" --output output/happy_jazz.mid --play
```

## 項目結構

### 前端目錄結構
```
frontend/src/
├── assets/           # 靜態資源文件（圖片、字體等）
├── components/       # 可重用的UI組件
│   ├── common/      # 通用組件（按鈕、輸入框等）
│   ├── layout/      # 布局組件（Header、Footer、Sidebar等）
│   └── features/    # 功能特定組件
├── hooks/           # 自定義React Hooks
├── pages/           # 頁面組件
├── services/        # API服務和數據處理
├── styles/          # 全局樣式和主題
├── types/           # TypeScript類型定義
├── utils/           # 工具函數
├── App.tsx          # 應用主組件
└── main.tsx         # 應用入口文件
```

### 後端模塊架構
```
backend/
├── audio_processing/  # 音頻處理模塊
├── music_generation/  # 音樂生成模塊
└── mcp/               # 模型協調器和管道
```

## 系統要求

- Python 3.9+
- Node.js 16+
- 推薦8GB以上內存，尤其在使用Magenta時
- (可選) GPU加速支持

## 授權協議

本項目採用MIT協議開源。

## 未來發展

- 整合外部大語言模型API，提升意圖理解能力
- 增加更多音樂風格與文化元素
- 支援更多音樂形式與樂章結構
- 添加音色模擬與音頻輸出功能 