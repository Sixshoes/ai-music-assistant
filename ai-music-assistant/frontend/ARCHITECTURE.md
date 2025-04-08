# 前端架構設計文檔

## 狀態管理架構

### 統一狀態管理系統

我們實現了一個基於 Context API 的統一狀態管理系統，提供類似 Redux 的功能，但更輕量且更易於整合到 React 應用中。

**主要組件：**

1. **`AppStateContext`** - 中央狀態存儲，負責管理全局應用狀態
2. **`AppStateProvider`** - 包裝整個應用的狀態提供者
3. **`useAppState`** - 自定義鉤子，用於獲取全局狀態和 dispatch 函數
4. **`useAppStateSelector`** - 性能優化的選擇器鉤子，僅在選擇的狀態部分變化時觸發重新渲染

**狀態結構：**

```typescript
{
  ui: {
    isLoading: boolean;
    activeView: string;
    errorMessage: string | null;
    successMessage: string | null;
  },
  musicGeneration: {
    generatingMusic: boolean;
    progress: number;
    currentStage: string;
  },
  musicPlayer: {
    isPlaying: boolean;
    currentTime: number;
    duration: number;
    volume: number;
    loop: boolean;
  },
  projects: {
    currentProjectId: string | null;
    savedProjects: any[];
  },
  preferences: {
    defaultGenre: string;
    defaultTempo: number;
    defaultKey: string;
    favoriteInstruments: string[];
  }
}
```

### 性能優化策略

1. **選擇性渲染** - 使用 `useAppStateSelector` 確保組件僅在相關狀態變化時重新渲染
2. **記憶化組件** - 使用 React.memo 包裝組件以避免不必要的重新渲染
3. **引用相等檢查** - 使用 lodash 的 `isEqual` 進行深度相等檢查
4. **本地狀態分離** - 將僅在組件內部使用的狀態與全局狀態分離

## 組件架構

### 模塊化設計

組件按照功能和職責進行模塊化分類：

- **佈局組件** - 處理頁面結構和整體佈局
- **UI 組件** - 純展示性組件，接受 props 並渲染 UI
- **容器組件** - 管理狀態並將數據傳遞給 UI 組件
- **功能組件** - 提供特定功能，如音樂播放器、音頻波形顯示等

### 錯誤處理

實現了全局錯誤邊界（ErrorBoundary）來捕獲和處理渲染過程中的錯誤：

- 防止整個應用因單個組件錯誤而崩潰
- 提供友好的錯誤消息和恢復機制
- 整合全局狀態進行錯誤報告

## 服務層架構

服務層負責處理業務邏輯和API通信：

1. **API 服務** - 處理與後端的通信
2. **領域服務** - 處理特定功能領域的邏輯，如音樂生成、音頻處理等
3. **工具服務** - 提供通用功能，如日誌記錄、緩存等

## 資源優化

### 代碼分割策略

使用 React 的 `lazy` 和 `Suspense` 實現代碼分割：

```jsx
const AppRoutes = lazy(() => import('./routes'));

// 在應用中使用
<Suspense fallback={<LoadingFallback />}>
  <AppRoutes />
</Suspense>
```

### 資源預加載

實現了資源預加載服務，預先加載關鍵資源：

```tsx
// 在應用啟動時初始化
resourcePreloader.initialize();
```

## 持久化機制

使用 localStorage 實現用戶偏好和項目數據的持久化：

```tsx
// 保存到本地存儲
localStorage.setItem('app_preferences', JSON.stringify(state.preferences));

// 從本地存儲加載
const savedPreferences = localStorage.getItem('app_preferences');
if (savedPreferences) {
  const preferences = JSON.parse(savedPreferences);
  // 恢復狀態
}
```

## 音頻處理優化

### MusicPlayer 組件優化

1. **懶加載資源** - 音頻資源按需加載
2. **狀態同步** - 通過 useEffect 保持音頻元素狀態與應用狀態同步
3. **事件節流** - 對頻繁的事件處理進行優化

## 後續優化方向

1. **緩存策略** - 實現更完善的數據和資源緩存
2. **服務工作線程** - 添加 Service Worker 支持離線使用
3. **Web Worker** - 將重計算任務移至後台線程
4. **虛擬滾動** - 優化長列表渲染
5. **代碼拆分** - 進一步優化初始加載時間 