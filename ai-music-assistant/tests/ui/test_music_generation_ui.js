/**
 * AI 音樂助手 UI 自動化測試
 * 
 * 使用 Playwright 測試音樂生成界面
 */

const { test, expect } = require('@playwright/test');

// 測試音樂生成表單
test('音樂生成表單應正確運作', async ({ page }) => {
  // 訪問首頁
  await page.goto('http://localhost:3000');
  
  // 等待頁面加載
  await page.waitForSelector('.music-generator-form');
  
  // 填寫表單
  await page.fill('textarea[name="textPrompt"]', '創作一首快樂的流行歌曲');
  await page.selectOption('select[name="key"]', 'C');
  await page.fill('input[name="tempo"]', '120');
  await page.selectOption('select[name="genre"]', 'pop');
  
  // 提交表單
  await page.click('button[type="submit"]');
  
  // 等待生成過程
  await page.waitForSelector('.loading-indicator', { state: 'visible' });
  await page.waitForSelector('.loading-indicator', { state: 'hidden', timeout: 30000 });
  
  // 驗證結果區域顯示
  const resultSection = await page.waitForSelector('.music-result-section');
  expect(resultSection).not.toBeNull();
  
  // 驗證音樂播放器存在
  const audioPlayer = await page.waitForSelector('.audio-player');
  expect(audioPlayer).not.toBeNull();
  
  // 驗證可視化元素顯示
  const visualization = await page.waitForSelector('.music-visualization');
  expect(visualization).not.toBeNull();
});

// 測試錯誤處理
test('應正確處理錯誤狀態', async ({ page }) => {
  // 模擬伺服器離線狀態
  await page.route('**/api/generate', route => {
    route.fulfill({
      status: 500,
      body: JSON.stringify({
        status: 'error',
        message: '伺服器錯誤'
      })
    });
  });
  
  // 訪問首頁
  await page.goto('http://localhost:3000');
  
  // 填寫並提交表單
  await page.fill('textarea[name="textPrompt"]', '測試錯誤處理');
  await page.click('button[type="submit"]');
  
  // 驗證錯誤訊息顯示
  const errorMessage = await page.waitForSelector('.error-message');
  expect(await errorMessage.textContent()).toContain('伺服器錯誤');
});

// 測試響應式設計
test('界面應適應不同螢幕尺寸', async ({ page }) => {
  // 訪問首頁
  await page.goto('http://localhost:3000');
  
  // 測試桌面視圖
  await page.setViewportSize({ width: 1280, height: 800 });
  let formLayout = await page.evaluate(() => {
    const form = document.querySelector('.music-generator-form');
    return window.getComputedStyle(form).display;
  });
  expect(formLayout).toBe('flex');
  
  // 測試平板視圖
  await page.setViewportSize({ width: 768, height: 1024 });
  let isTabletLayout = await page.evaluate(() => {
    return document.querySelector('.tablet-layout') !== null;
  });
  expect(isTabletLayout).toBe(true);
  
  // 測試手機視圖
  await page.setViewportSize({ width: 375, height: 667 });
  let isMobileLayout = await page.evaluate(() => {
    return document.querySelector('.mobile-layout') !== null;
  });
  expect(isMobileLayout).toBe(true);
});

// 測試歷史記錄功能
test('歷史記錄功能應正常工作', async ({ page }) => {
  // 模擬歷史記錄API回應
  await page.route('**/api/history', route => {
    route.fulfill({
      status: 200,
      body: JSON.stringify({
        status: 'success',
        data: [
          { 
            id: '1', 
            title: '快樂的流行歌曲', 
            date: '2025-04-01T10:30:00',
            parameters: { tempo: 120, key: 'C', genre: 'pop' }
          },
          { 
            id: '2', 
            title: '憂鬱的爵士曲', 
            date: '2025-04-02T14:20:00',
            parameters: { tempo: 90, key: 'Am', genre: 'jazz' }
          }
        ]
      })
    });
  });
  
  // 訪問首頁
  await page.goto('http://localhost:3000');
  
  // 點擊歷史記錄按鈕
  await page.click('.history-button');
  
  // 等待歷史列表加載
  await page.waitForSelector('.history-list');
  
  // 驗證列表項目
  const historyItems = await page.$$('.history-item');
  expect(historyItems.length).toBe(2);
  
  // 點擊第一個歷史項目
  await historyItems[0].click();
  
  // 驗證加載了正確的參數
  const textValue = await page.inputValue('textarea[name="textPrompt"]');
  expect(textValue).toBe('快樂的流行歌曲');
  
  const tempoValue = await page.inputValue('input[name="tempo"]');
  expect(tempoValue).toBe('120');
});

// 測試使用者優先設定
test('使用者優先設定應被保存和加載', async ({ page }) => {
  // 訪問首頁
  await page.goto('http://localhost:3000');
  
  // 打開設定面板
  await page.click('.settings-button');
  
  // 修改主題設定
  await page.click('input[name="darkTheme"]');
  
  // 修改默認速度
  await page.fill('input[name="defaultTempo"]', '110');
  
  // 修改默認調性
  await page.selectOption('select[name="defaultKey"]', 'G');
  
  // 保存設定
  await page.click('.save-settings-button');
  
  // 重新加載頁面
  await page.reload();
  
  // 打開設定面板
  await page.click('.settings-button');
  
  // 驗證設定已保存
  const darkThemeChecked = await page.isChecked('input[name="darkTheme"]');
  expect(darkThemeChecked).toBe(true);
  
  const defaultTempo = await page.inputValue('input[name="defaultTempo"]');
  expect(defaultTempo).toBe('110');
  
  const defaultKey = await page.inputValue('select[name="defaultKey"]');
  expect(defaultKey).toBe('G');
  
  // 驗證界面是否套用了深色主題
  const hasDarkTheme = await page.evaluate(() => {
    return document.body.classList.contains('dark-theme');
  });
  expect(hasDarkTheme).toBe(true);
}); 