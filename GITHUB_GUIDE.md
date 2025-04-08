# GitHub 發布指南

本指南將幫助您將 AI 音樂創作助手項目發布到 GitHub。

## 準備工作

1. 如果您還沒有 GitHub 帳號，請先在 [GitHub](https://github.com/) 註冊。
2. 安裝 Git：如果您還沒有安裝 Git，請訪問 [Git 官網](https://git-scm.com/) 下載並安裝。
3. 配置 Git：

```bash
git config --global user.name "您的用戶名"
git config --global user.email "您的郵箱"
```

## 步驟 1: 初始化本地 Git 倉庫

在項目根目錄中打開終端或命令行，運行以下命令：

```bash
# 初始化 Git 倉庫
git init

# 添加所有文件到暫存區
git add .

# 創建首次提交
git commit -m "初始化提交：整合前後端功能"
```

## 步驟 2: 在 GitHub 上創建倉庫

1. 登錄到您的 GitHub 帳號。
2. 點擊右上角的 "+" 圖標，選擇 "New repository"。
3. 輸入倉庫名稱，如 "ai-music-assistant"。
4. 添加描述：如 "AI 音樂創作助手：將文本描述轉換為 MIDI 音樂"。
5. 保持倉庫為公開（Public）以便其他人可以查看和使用。
6. 不要選擇初始化 README 和 .gitignore，因為我們已經有自己的文件。
7. 點擊 "Create repository"。

## 步驟 3: 將本地倉庫推送至 GitHub

GitHub 將顯示推送代碼的指令。複製並運行類似下面的命令：

```bash
# 添加遠程倉庫
git remote add origin https://github.com/您的用戶名/ai-music-assistant.git

# 推送代碼到 GitHub
git push -u origin main  # 或 git push -u origin master，取決於您的默認分支名稱
```

如果您使用 SSH 認證，命令可能略有不同：

```bash
git remote add origin git@github.com:您的用戶名/ai-music-assistant.git
git push -u origin main
```

## 步驟 4: 驗證發布結果

1. 訪問您的 GitHub 倉庫頁面：`https://github.com/您的用戶名/ai-music-assistant`
2. 確認所有文件和目錄都已成功上傳。
3. README.md 文件將自動在倉庫主頁顯示。

## 步驟 5: 添加 Topics 和 Releases

為了增加項目的可發現性：

1. 點擊倉庫頁面右側的 "About" 部分中的齒輪圖標。
2. 在 "Topics" 欄位中添加相關標籤，如：`music-generation`, `midi`, `ai`, `machine-learning`。
3. 點擊 "Save changes"。

要創建發行版本：

1. 點擊 "Releases" 部分。
2. 點擊 "Create a new release"。
3. 添加標籤，如 "v1.0.0"。
4. 提供發行版標題和描述。
5. 點擊 "Publish release"。

## 後續維護

當您對項目進行更改時，使用這些命令來更新 GitHub 倉庫：

```bash
# 添加更改的文件
git add .

# 提交更改
git commit -m "描述您所做的更改"

# 推送到 GitHub
git push
```

## 其他注意事項

1. **忽略敏感資訊**：確保 .gitignore 文件包含所有應該被忽略的文件和目錄，特別是包含 API 密鑰或敏感配置的文件。
2. **依賴管理**：請確保 requirements.txt 包含所有必要的依賴項。
3. **文檔維護**：保持 README.md 和其他文檔的更新，以反映項目的最新狀態。
4. **許可證**：如果還沒有，考慮添加開源許可證文件。

## 疑難解答

如果推送時遇到問題，可能是由於認證問題或分支名稱不同：

- 確認您有 GitHub 帳號的適當訪問權限。
- 嘗試使用個人訪問令牌（Personal Access Token）進行認證。
- 檢查當前的分支名稱：`git branch`，然後在 push 命令中使用正確的分支名稱。

如果需要更多幫助，請參考 [GitHub 文檔](https://docs.github.com/) 或提出問題。 