# 開發貢獻指南

本指南提供了如何為 AI 音樂創作助手項目做出貢獻的詳細說明。我們歡迎所有形式的貢獻，包括功能開發、錯誤修復、文檔改進和測試用例添加。

## 開發環境設置

### 前提條件

- Python 3.8+
- Node.js 14+
- Docker (可選，用於容器化開發)
- Git

### 設置步驟

1. **克隆代碼庫**

```bash
git clone https://github.com/your-org/ai-music-assistant.git
cd ai-music-assistant
```

2. **設置後端環境**

```bash
# 創建虛擬環境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 安裝依賴
pip install -r backend/requirements.txt
pip install -r backend/requirements-dev.txt  # 開發依賴
```

3. **設置前端環境**

```bash
cd frontend
npm install
```

4. **安裝開發工具**

```bash
# 安裝代碼品質工具
pip install black isort mypy pylint
npm install -g eslint prettier
```

5. **配置數據庫**

開發時可以使用本地 SQLite 數據庫進行測試，設置方法：

```bash
cd backend
python scripts/setup_dev_db.py
```

6. **啟動開發服務器**

```bash
# 啟動後端服務
cd backend
python main.py --dev

# 啟動前端服務 (在另一個終端)
cd frontend
npm run dev
```

## 開發工作流程

我們採用基於功能分支的工作流程：

1. **創建功能分支**

```bash
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/issue-description
```

2. **進行開發**

在本地進行開發和測試。確保您的代碼遵循項目的編碼規範。

3. **提交更改**

```bash
git add .
git commit -m "feat: add your feature description"
# 或
git commit -m "fix: fix the issue description"
```

我們使用 [Conventional Commits](https://www.conventionalcommits.org/) 規範。提交消息應遵循以下格式：

- `feat: 新功能`
- `fix: 修復錯誤`
- `docs: 文檔更改`
- `style: 格式修改（不影響代碼運行）`
- `refactor: 代碼重構（既不是新功能也不是 bug 修復）`
- `perf: 改進性能`
- `test: 添加測試`
- `chore: 構建過程或輔助工具的變動`

4. **運行測試**

```bash
# 後端測試
cd backend
pytest

# 前端測試
cd frontend
npm test
```

5. **代碼風格檢查**

```bash
# 後端代碼檢查
cd backend
black .
isort .
pylint **/*.py

# 前端代碼檢查
cd frontend
npm run lint
npm run format
```

6. **提交 Pull Request**

推送您的分支到代碼庫並創建 Pull Request：

```bash
git push origin feature/your-feature-name
```

然後在 GitHub 上創建 Pull Request，填寫 PR 模板中的信息。

## 擴展指南

### 添加新的音樂生成模型

1. 在 `backend/music_generation/models/` 目錄下創建新的模型文件：

```python
# my_new_model.py
from typing import List, Dict, Any
from backend.mcp.mcp_schema import Note, MusicParameters

class MyNewModel:
    def __init__(self, model_path: str = None):
        # 初始化模型
        pass
        
    def generate(self, parameters: MusicParameters) -> List[Note]:
        # 使用模型生成音樂
        pass
```

2. 在 `backend/music_generation/__init__.py` 中注冊您的模型：

```python
from .my_new_model import MyNewModel

# 添加到可用模型字典
AVAILABLE_MODELS = {
    # ... 現有模型 ...
    "my_new_model": MyNewModel,
}
```

3. 添加模型文檔：

在 `docs/api/models/` 目錄下創建模型文檔，描述其功能和參數。

### 添加新的音頻效果

1. 在 `backend/audio_processing/effects/` 目錄下創建新的效果處理器：

```python
# my_effect.py
from typing import Dict, Any
import numpy as np

def apply_my_effect(audio_data: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    # 實現效果處理邏輯
    return processed_audio
```

2. 在 `backend/audio_processing/effects/__init__.py` 中注冊效果：

```python
from .my_effect import apply_my_effect

AVAILABLE_EFFECTS = {
    # ... 現有效果 ...
    "my_effect": apply_my_effect,
}
```

3. 添加效果文檔：

在 `docs/api/effects/` 目錄下創建效果文檔，描述其功能和參數。

### 添加前端組件

1. 在 `frontend/src/components/` 目錄下創建新組件：

```tsx
// MyComponent.tsx
import React from 'react';

interface MyComponentProps {
  // 定義屬性
}

export const MyComponent: React.FC<MyComponentProps> = (props) => {
  // 實現組件
  return (
    <div className="my-component">
      {/* 組件內容 */}
    </div>
  );
};
```

2. 創建相應的測試文件：

```tsx
// MyComponent.test.tsx
import { render, screen } from '@testing-library/react';
import { MyComponent } from './MyComponent';

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent />);
    // 添加斷言
  });
});
```

3. 添加組件文檔：

在 `docs/frontend/components/` 目錄下創建組件文檔。

## 代碼審查標準

所有代碼貢獻都需要經過代碼審查。審查者將考慮以下方面：

1. **功能性**：代碼是否按預期工作？
2. **可讀性**：代碼是否易於理解？
3. **可維護性**：代碼結構是否合理？
4. **測試覆蓋**：是否有足夠的測試？
5. **文檔**：是否有充分的文檔？
6. **性能**：代碼是否有性能問題？
7. **安全性**：代碼是否有安全漏洞？

## 發布流程

我們使用語義化版本控制（[SemVer](https://semver.org/)）來管理版本：

- **主版本**（X.0.0）：不向後兼容的變更
- **次版本**（0.X.0）：向後兼容的功能新增
- **修訂版本**（0.0.X）：向後兼容的錯誤修復

發布流程如下：

1. 更新 `CHANGELOG.md`
2. 更新版本號
3. 創建發布分支
4. 運行完整測試套件
5. 創建發布標籤
6. 生成發布包
7. 發布到正式環境

## 支持和交流

- **問題和討論**：使用 GitHub Issues 和 Discussions
- **實時討論**：加入我們的 Discord 服務器
- **開發者郵件列表**：訂閱我們的開發者郵件列表

## 行為準則

我們希望所有貢獻者遵守我們的行為準則。詳情請參閱 [CODE_OF_CONDUCT.md](../../CODE_OF_CONDUCT.md)。

## 許可證

本項目遵循 MIT 許可證。詳情請參閱 [LICENSE](../../LICENSE) 文件。 