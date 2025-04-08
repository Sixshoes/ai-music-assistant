# 整合版README - AI音樂創作助手

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

- **前端**：HTML + CSS + JavaScript (原生)
- **後端**：Flask + Python
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

## 使用方法

### 整合版前後端應用

我們現在提供了整合版的前後端應用，可以通過Web界面直接創建音樂：

#### 啟動後端服務

```bash
# 啟動Flask後端
python app.py
```

後端服務將在 http://localhost:5000 上運行。

#### 訪問前端界面

前端界面位於 `frontend/src/index.html`，可以通過任何靜態文件服務器或直接在瀏覽器中打開。

在前端界面中，您可以：
1. 輸入自然語言描述您想要的音樂
2. 選擇是否使用大語言模型進行增強分析
3. 點擊"生成音樂"按鈕
4. 等待後端處理完成後，您可以直接在瀏覽器中播放生成的MIDI音樂
5. 下載MIDI文件以便在其他軟件中使用

### 命令行使用

系統仍然保留了命令行使用方式，適合進階用戶或自動化處理：

#### 互動模式

```bash
python text_to_music.py --interactive --play
```

#### 命令行模式

```bash
python text_to_music.py --description "創作一首平靜的古典音樂，帶有中國傳統元素，適合沉思和冥想" --output output/chinese_meditation.mid --play
```

參數說明：
- `--description` 或 `-d`：音樂創作需求的文字描述（必要）
- `--output` 或 `-o`：輸出的MIDI文件路徑（預設為 output/music_output.mid）
- `--play` 或 `-p`：生成後立即播放MIDI音樂
- `--use-llm`：使用大語言模型進行更精確的分析（需要額外配置）
- `--interactive` 或 `-i`：啟用互動模式

## 項目結構

### 前端目錄結構
```
frontend/
└── src/
    ├── index.html      # 主頁面
    ├── scripts/        # JavaScript文件
    │   └── main.js     # 主腳本文件
    └── styles/         # CSS樣式文件
        └── main.css    # 主樣式文件
```

### 後端文件
```
app.py                        # Flask後端應用
text_to_music.py              # 文本到音樂轉換工具
music_creation_pipeline.py    # 音樂創作流水線
music_parameters.py           # 音樂參數管理模塊
music_requirement_analyzer.py # 音樂需求分析模塊
```

## 系統要求

- Python 3.9+
- 現代瀏覽器 (Chrome, Firefox, Safari, Edge)
- 推薦8GB以上內存，尤其在使用Magenta時
- (可選) GPU加速支持

## 新增特性 (最新版本)

- **整合前後端界面**：提供了直觀的Web界面，無需命令行即可創建音樂
- **即時音樂預覽**：直接在瀏覽器中預覽生成的MIDI音樂
- **輕鬆下載**：一鍵下載生成的音樂文件
- **模型選擇**：可選擇是否使用大語言模型進行增強分析

## 已知問題和限制

- MIDI播放需要瀏覽器支持，部分瀏覽器可能需要額外的MIDI播放器插件
- 大語言模型增強分析需要額外配置API密鑰
- 在低配置設備上，音樂生成可能較慢

## 未來發展計劃

- 整合外部大語言模型API，提升意圖理解能力
- 增加更多音樂風格與文化元素
- 支援更多音樂形式與樂章結構
- 添加音色模擬與音頻輸出功能
- 開發更豐富的前端界面，提供更多自定義選項

## GitHub使用說明

本項目已上傳至GitHub，您可以通過以下命令克隆：

```bash
git clone https://github.com/yourusername/ai-music-assistant.git
cd ai-music-assistant
```

請確保按照上述安裝指南安裝所有依賴後再使用。

## 貢獻指南

歡迎貢獻代碼或提出建議！請遵循以下步驟：

1. Fork本倉庫
2. 創建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟Pull Request

## 授權協議

本項目採用MIT協議開源。

## 致謝

感謝所有音樂理論與自然語言處理相關研究者，本項目建立在這些基礎上，希望促進音樂科技的發展與應用。 