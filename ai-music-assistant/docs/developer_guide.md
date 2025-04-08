# AI 音樂助手開發指南

## 開發環境設置

### 系統需求

- **作業系統**：Windows 10+, macOS 10.14+, Linux
- **開發工具**：
  - Node.js 16.x+
  - npm 8.x+ 或 yarn 1.22+
  - Git
- **IDE 建議**：
  - Visual Studio Code
  - WebStorm
  - Atom

### 配置開發環境

1. 克隆專案倉庫

```bash
git clone https://github.com/example/ai-music-assistant.git
cd ai-music-assistant
```

2. 安裝依賴

```bash
# 安裝前端依賴
cd frontend
npm install

# 安裝後端依賴
cd ../backend
npm install
```

3. 啟動開發服務器

```bash
# 啟動前端開發服務器
cd frontend
npm run dev

# 啟動後端開發服務器
cd ../backend
npm run dev
```

## 專案結構

```
ai-music-assistant/
├── frontend/              # 前端代碼
│   ├── src/               # 源代碼
│   │   ├── components/    # React 組件
│   │   ├── pages/         # 頁面組件
│   │   ├── services/      # 服務類
│   │   ├── types/         # TypeScript 類型定義
│   │   ├── utils/         # 工具函數
│   │   ├── App.tsx        # 主應用組件
│   │   └── main.tsx       # 應用入口
│   ├── public/            # 靜態資源
│   ├── package.json       # 依賴配置
│   └── vite.config.ts     # Vite 配置
│
├── backend/               # 後端代碼
│   ├── src/               # 源代碼
│   │   ├── controllers/   # 控制器
│   │   ├── models/        # 數據模型
│   │   ├── routes/        # API 路由
│   │   ├── services/      # 服務類
│   │   ├── utils/         # 工具函數
│   │   └── server.ts      # 服務器入口
│   └── package.json       # 依賴配置
│
├── mcp/                   # Model Context Protocol 實現
│   ├── src/               # 源代碼
│   ├── models/            # 模型定義
│   └── transformers/      # 數據轉換器
│
├── docs/                  # 文檔
│   ├── architecture.md    # 架構設計文檔
│   ├── api_reference.md   # API 參考文檔
│   ├── user_guide.md      # 用戶指南
│   └── developer_guide.md # 開發指南
│
└── resources/             # 資源文件
    └── samples/           # 示例音頻和 MIDI 文件
```

## 核心架構

AI 音樂助手採用分層架構，各層職責明確：

### 前端架構

- **React** + **TypeScript** + **Material UI** 構建用戶界面
- **狀態管理**：使用 React 的 Context API 和 hooks 進行狀態管理
- **API 通信**：使用 Axios 處理 HTTP 請求
- **音頻處理**：使用 Tone.js 和 Web Audio API
- **樂譜渲染**：使用 VexFlow 渲染樂譜

### 後端架構

- **Node.js** + **Express** 構建 API 服務器
- **API 設計**：RESTful API 設計風格
- **數據處理**：使用 Model Context Protocol (MCP) 統一模型交互格式
- **異步處理**：使用 Promise 和 async/await 處理異步操作

### Model Context Protocol (MCP)

MCP 是整個系統的核心協議，定義了前端和不同 AI 模型之間的標準化通信格式：

```
前端 <-> MCP <-> 音樂生成模型
            <-> 音頻處理模型
            <-> 樂理分析模型
```

## 代碼風格和最佳實踐

### 命名約定

- **文件名**：
  - React 組件：PascalCase (例如 `MusicPlayer.tsx`)
  - 服務和工具：camelCase (例如 `musicGenerationService.ts`)
  - 類型定義：camelCase 並以 `.d.ts` 結尾
- **變量和函數**：camelCase (例如 `generateMusic`)
- **類和接口**：PascalCase (例如 `MusicGenerator`)
- **常量**：UPPER_SNAKE_CASE (例如 `MAX_AUDIO_LENGTH`)

### 代碼組織

- 每個組件一個文件
- 相關功能組合成服務類
- 使用 TypeScript 類型系統確保類型安全

### 註釋規範

- 使用 JSDoc 風格註釋
- 關鍵功能、參數和返回值必須有註釋

```typescript
/**
 * 分析音樂結構並返回理論分析結果
 * 
 * @param audioData - Base64 編碼的音頻數據
 * @param options - 分析選項
 * @returns 音樂理論分析結果
 */
function analyzeMusicStructure(audioData: string, options?: AnalysisOptions): Promise<AnalysisResult> {
  // 實現...
}
```

## 前端開發指南

### 組件開發

#### 組件設計原則

- **單一職責**：每個組件應專注於單一功能
- **可重用性**：組件應設計為可重用
- **可測試性**：組件應易於測試
- **無狀態優先**：盡可能使用無狀態組件

#### 新增組件步驟

1. 在 `src/components` 目錄創建新組件文件
2. 使用 TypeScript 定義 props 接口
3. 實現組件功能
4. 導出組件

```typescript
// src/components/TempoControl.tsx
import React from 'react';

interface TempoControlProps {
  /** 當前速度值 (BPM) */
  value: number;
  /** 速度變化回調函數 */
  onChange: (newValue: number) => void;
  /** 最小速度值 */
  min?: number;
  /** 最大速度值 */
  max?: number;
}

/**
 * 速度控制組件，用於調整音樂速度
 */
export const TempoControl: React.FC<TempoControlProps> = ({
  value,
  onChange,
  min = 40,
  max = 220
}) => {
  // 組件實現
  return (
    <div className="tempo-control">
      {/* 實現細節 */}
    </div>
  );
};
```

### 服務開發

服務類負責處理業務邏輯和 API 通信。

#### 新增服務步驟

1. 在 `src/services` 目錄創建新服務文件
2. 定義服務類接口和方法
3. 實現服務功能
4. 導出服務實例

```typescript
// src/services/AudioProcessingService.ts
import { Logger } from './LoggingService';

export interface AudioProcessingOptions {
  normalize?: boolean;
  trim?: boolean;
  fadeIn?: number;
  fadeOut?: number;
}

class AudioProcessingService {
  /**
   * 處理音頻數據
   * 
   * @param audioData - Base64 編碼的音頻數據
   * @param options - 處理選項
   * @returns 處理後的音頻數據
   */
  async processAudio(audioData: string, options: AudioProcessingOptions = {}): Promise<string> {
    try {
      Logger.info('開始處理音頻', { options }, { tags: ['AUDIO'] });
      
      // 實現處理邏輯
      
      return processedData;
    } catch (error) {
      Logger.error('音頻處理失敗', error, { tags: ['AUDIO'] });
      throw new Error('音頻處理失敗: ' + (error instanceof Error ? error.message : String(error)));
    }
  }
  
  // 其他方法...
}

// 導出服務實例
export const audioProcessingService = new AudioProcessingService();
```

### 狀態管理

使用 React Context API 和 hooks 管理應用狀態。

#### 新增全局狀態步驟

1. 在 `src/contexts` 目錄創建新上下文文件
2. 定義上下文類型和初始狀態
3. 創建 Context 和 Provider 組件
4. 導出自定義 hook 以訪問狀態

```typescript
// src/contexts/MusicPlayerContext.tsx
import React, { createContext, useContext, useState, ReactNode } from 'react';

interface MusicPlayerState {
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  volume: number;
}

interface MusicPlayerContextType {
  state: MusicPlayerState;
  play: () => void;
  pause: () => void;
  setVolume: (volume: number) => void;
  seek: (time: number) => void;
}

const initialState: MusicPlayerState = {
  isPlaying: false,
  currentTime: 0,
  duration: 0,
  volume: 0.8
};

const MusicPlayerContext = createContext<MusicPlayerContextType | undefined>(undefined);

export const MusicPlayerProvider: React.FC<{children: ReactNode}> = ({ children }) => {
  const [state, setState] = useState<MusicPlayerState>(initialState);
  
  // 實現方法
  const play = () => setState(prev => ({ ...prev, isPlaying: true }));
  const pause = () => setState(prev => ({ ...prev, isPlaying: false }));
  const setVolume = (volume: number) => setState(prev => ({ ...prev, volume }));
  const seek = (time: number) => setState(prev => ({ ...prev, currentTime: time }));
  
  return (
    <MusicPlayerContext.Provider value={{ state, play, pause, setVolume, seek }}>
      {children}
    </MusicPlayerContext.Provider>
  );
};

// 自定義 hook
export const useMusicPlayer = (): MusicPlayerContextType => {
  const context = useContext(MusicPlayerContext);
  if (context === undefined) {
    throw new Error('useMusicPlayer must be used within a MusicPlayerProvider');
  }
  return context;
};
```

## 後端開發指南

### API 開發

#### 設計原則

- 遵循 RESTful API 設計風格
- 使用標準 HTTP 狀態碼
- 提供清晰的錯誤信息
- 使用 JSON 作為數據交換格式

#### 新增 API 端點步驟

1. 在 `src/controllers` 創建控制器函數
2. 在 `src/routes` 定義路由
3. 添加輸入驗證
4. 實現錯誤處理

```typescript
// src/controllers/musicController.ts
import { Request, Response } from 'express';
import { musicService } from '../services/musicService';

export const analyzeMusicController = async (req: Request, res: Response) => {
  try {
    const { audioData } = req.body;
    
    // 驗證輸入
    if (!audioData) {
      return res.status(400).json({ detail: "音頻數據不能為空" });
    }
    
    // 處理請求
    const result = await musicService.analyzeMusic(audioData);
    
    // 返回結果
    return res.status(200).json(result);
  } catch (error) {
    console.error('音樂分析出錯:', error);
    return res.status(500).json({ 
      detail: "服務器處理請求時出錯",
      error: error instanceof Error ? error.message : String(error)
    });
  }
};
```

```typescript
// src/routes/musicRoutes.ts
import express from 'express';
import { analyzeMusicController } from '../controllers/musicController';

const router = express.Router();

router.post('/analyze', analyzeMusicController);

export default router;
```

### MCP 開發

#### 創建新的 MCP 處理器

1. 在 `mcp/transformers` 目錄創建新轉換器
2. 實現輸入轉換方法
3. 實現輸出轉換方法

```typescript
// mcp/transformers/melodyArrangementTransformer.ts
import { MCPCommand, MCPResponse } from '../models/mcp';
import { ArrangementModelInput, ArrangementModelOutput } from '../models/arrangement';

/**
 * 將 MCP 指令轉換為旋律編曲模型輸入
 */
export function transformToModelInput(command: MCPCommand): ArrangementModelInput {
  // 實現轉換邏輯
  return {
    // 模型所需的輸入格式
  };
}

/**
 * 將模型輸出轉換為 MCP 響應
 */
export function transformToMCPResponse(modelOutput: ArrangementModelOutput): MCPResponse {
  // 實現轉換邏輯
  return {
    // MCP 響應格式
  };
}
```

## 測試指南

### 單元測試

使用 Jest 和 React Testing Library 進行單元測試。

#### 組件測試

```typescript
// src/components/__tests__/TempoControl.test.tsx
import React from 'react';
import { render, fireEvent, screen } from '@testing-library/react';
import { TempoControl } from '../TempoControl';

describe('TempoControl', () => {
  test('renders with default props', () => {
    const handleChange = jest.fn();
    render(<TempoControl value={120} onChange={handleChange} />);
    
    expect(screen.getByText(/120/i)).toBeInTheDocument();
  });
  
  test('calls onChange when value changes', () => {
    const handleChange = jest.fn();
    render(<TempoControl value={120} onChange={handleChange} />);
    
    // 根據實際組件交互方式模擬操作
    fireEvent.click(screen.getByLabelText(/increase/i));
    
    expect(handleChange).toHaveBeenCalledWith(121);
  });
  
  // 更多測試...
});
```

#### 服務測試

```typescript
// src/services/__tests__/AudioProcessingService.test.ts
import { audioProcessingService } from '../AudioProcessingService';

// 模擬 Base64 音頻數據
const mockAudioData = 'data:audio/wav;base64,AAAA...';

describe('AudioProcessingService', () => {
  test('processes audio with default options', async () => {
    const result = await audioProcessingService.processAudio(mockAudioData);
    expect(result).toBeTruthy();
    // 根據具體實現添加更多斷言
  });
  
  test('normalizes audio correctly', async () => {
    const result = await audioProcessingService.processAudio(mockAudioData, { normalize: true });
    // 驗證結果
  });
  
  // 更多測試...
});
```

### 運行測試

```bash
# 運行所有測試
npm test

# 運行特定測試文件
npm test -- src/components/__tests__/TempoControl.test.tsx

# 運行測試覆蓋率報告
npm test -- --coverage
```

## 擴展功能指南

### 添加新的音樂生成模型

1. 在 `backend/src/services` 創建新的模型服務
2. 在 `mcp/transformers` 創建相應的轉換器
3. 在 `backend/src/controllers` 添加新的控制器
4. 在 `backend/src/routes` 註冊新的 API 端點

### 添加新的音樂分析功能

1. 在 `backend/src/services` 擴展分析服務
2. 更新 API 和轉換器以支持新功能
3. 在前端添加對應的 UI 組件和服務方法

### 實現多人協作功能

協作功能預留接口已在 `frontend/src/services/CollaborationService.ts` 中定義。要實現完整功能：

1. 選擇適當的 WebSocket 或 WebRTC 庫
2. 在後端實現實時通信服務
3. 擴展前端協作服務以連接實時服務
4. 添加協作操作的 UI 組件

### 實現歌聲合成功能

歌聲合成功能預留接口已在 `frontend/src/services/VoiceSynthesisService.ts` 中定義。要實現完整功能：

1. 整合開源歌聲合成引擎（如 Sinsy 或 WORLD）
2. 實現歌詞和旋律同步對齊功能
3. 擴展前端界面以支持歌詞輸入和編輯
4. 添加歌聲參數調整界面

## 部署指南

### 前端部署

#### 生產構建

```bash
cd frontend
npm run build
```

生成的靜態文件位於 `frontend/dist` 目錄，可部署到任何靜態網站託管服務。

#### 使用 Docker

```bash
# 使用提供的 Dockerfile 構建鏡像
docker build -t ai-music-assistant-frontend ./frontend

# 運行容器
docker run -p 80:80 ai-music-assistant-frontend
```

### 後端部署

#### 使用 PM2

```bash
# 全局安裝 PM2
npm install -g pm2

# 啟動後端服務
cd backend
pm2 start dist/server.js --name ai-music-api

# 設置開機自啟
pm2 startup
pm2 save
```

#### 使用 Docker

```bash
# 使用提供的 Dockerfile 構建鏡像
docker build -t ai-music-assistant-backend ./backend

# 運行容器
docker run -p 8000:8000 ai-music-assistant-backend
```

### 完整部署（Docker Compose）

使用 Docker Compose 可以一鍵部署整個應用：

```bash
# 啟動所有服務
docker-compose up -d

# 查看日誌
docker-compose logs -f

# 停止服務
docker-compose down
```

## 常見問題解答

### Q: 如何調試前端和後端之間的通信？

A: 可以使用瀏覽器的開發者工具的網絡面板監控 API 請求，或在前端和後端添加詳細的日誌輸出。

### Q: 如何處理大型音頻文件的性能問題？

A: 考慮以下策略：
- 前端進行文件壓縮後再上傳
- 使用流式處理而非一次性加載
- 實現分片上傳功能
- 增加服務器處理超時限制

### Q: 開發時如何模擬 AI 模型響應？

A: 使用 `mock` 目錄下的示例響應數據，或在 `development` 環境中添加模擬服務響應。

## 貢獻指南

### 提交規範

使用 Angular 提交規範：

```
<type>(<scope>): <subject>

<body>

<footer>
```

類型 (type) 包括：
- **feat**: 新功能
- **fix**: 錯誤修復
- **docs**: 文檔更改
- **style**: 不影響代碼含義的更改（空格、格式化等）
- **refactor**: 既不修復錯誤也不添加功能的代碼更改
- **perf**: 改進性能的代碼更改
- **test**: 添加缺失的測試或修正現有測試
- **chore**: 構建過程或輔助工具的變動

### 分支策略

- **main**: 穩定的生產版本
- **develop**: 開發版本
- **feature/\***: 新功能分支
- **bugfix/\***: 錯誤修復分支
- **release/\***: 發布準備分支

### 貢獻步驟

1. Fork 倉庫
2. 創建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

## 附錄

### 有用的資源

- [React 官方文檔](https://reactjs.org/)
- [TypeScript 官方文檔](https://www.typescriptlang.org/)
- [Material UI 組件庫](https://material-ui.com/)
- [Tone.js 音頻處理庫](https://tonejs.github.io/)
- [VexFlow 樂譜渲染庫](https://github.com/0xfe/vexflow)

### 相關技術探索

以下技術可能對項目的未來發展有幫助：

- **WebAssembly**: 提高音頻處理性能
- **IndexedDB**: 本地存儲大型音頻文件
- **WebRTC**: 實時協作功能
- **Web Workers**: 將耗時操作移至背景線程
- **Service Workers**: 離線功能支持 