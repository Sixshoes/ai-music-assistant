# 代碼規範與工具使用指南

此文檔描述了專案的代碼規範與工具使用方法，所有開發者都應該遵循這些規範，以確保代碼品質和一致性。

## 核心原則

1. **乾淨的代碼** - 代碼應該易於閱讀和理解
2. **無未使用的變數和導入** - 保持代碼整潔，移除未使用的元素
3. **一致的格式** - 使用自動化工具確保所有代碼風格一致
4. **早期發現問題** - 使用靜態分析工具儘早發現潛在問題

## 設置開發環境

### 前端 (TypeScript/React)

1. 安裝 VSCode 插件:
   - ESLint
   - Prettier
   - TypeScript
   
2. 在 VSCode 中使用已配置好的設置:
   - 保存時自動格式化
   - 保存時自動修復 ESLint 問題
   - 保存時自動整理導入

### 後端 (Python)

1. 安裝 VSCode 插件:
   - Pylint
   - Black Formatter
   - isort
   
2. 安裝 Python 工具:
   ```
   pip install pylint mypy autoflake isort black
   ```

## 常用命令

### 前端

```bash
# 檢查代碼問題
npm run lint

# 修復代碼問題
npm run lint:fix

# 格式化代碼
npm run format
```

### 後端

```bash
# 運行 Pylint 檢查
npm run pylint

# 格式化 Python 代碼
npm run pyformat
```

## 代碼風格指南

### TypeScript/React

1. **命名約定**:
   - 使用駝峰式命名法 (`camelCase`) 命名變數和函數
   - 使用帕斯卡命名法 (`PascalCase`) 命名類和 React 組件
   - 使用全大寫 (`UPPER_CASE`) 命名常量

2. **導入規則**:
   - 導入應該按照下列順序排列:
     1. 核心 React 導入
     2. 第三方庫導入
     3. 項目內部導入
     4. 樣式和資源導入
   - 移除未使用的導入

3. **使用 TypeScript 類型**:
   - 總是為函數參數和返回值定義類型
   - 使用接口定義組件 props
   - 使用類型推斷減少冗餘

### Python

1. **命名約定**:
   - 使用蛇形命名法 (`snake_case`) 命名變數和函數
   - 使用帕斯卡命名法 (`PascalCase`) 命名類
   - 使用全大寫 (`UPPER_CASE`) 命名常量

2. **導入規則**:
   - 導入應該按照下列順序排列:
     1. 標準庫導入
     2. 相關第三方導入
     3. 本地應用/庫特定導入
   - 每組導入之間應該用一行空行分隔
   - 使用 `isort` 自動整理導入

3. **代碼註釋**:
   - 使用文檔字符串 (docstrings) 描述模塊、類和函數
   - 針對複雜的邏輯添加行內註釋
   - 遵循 [Google Python 風格指南](https://google.github.io/styleguide/pyguide.html) 的註釋格式

## 常見問題與解決方案

### 問題: Lint 錯誤無法自動修復

如果自動修復未能解決所有問題，請嘗試:
1. 手動檢查錯誤消息
2. 對於前端，運行 `npm run lint -- --debug` 獲取更詳細信息
3. 對於 Python，運行 `pylint --verbose backend/path/to/file.py`

### 問題: Git Hooks 不工作

如果 Git Hooks 不工作，請確保:
1. Husky 已正確安裝 `npm install husky --save-dev`
2. 鉤子文件有執行權限 `chmod +x .husky/pre-commit`
3. 本地 Git 配置未禁用 hooks `git config core.hooksPath .husky`

---

如有任何疑問或建議，請聯繫技術負責人。 