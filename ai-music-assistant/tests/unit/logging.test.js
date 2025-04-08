/**
 * LoggingService 單元測試
 */

// 使用 Jest 測試框架
describe('LoggingService', () => {
  let originalConsole;
  let mockConsole;
  let LoggingService;
  let Logger;

  // 在每個測試前設置模擬
  beforeEach(() => {
    // 備份原始控制台方法
    originalConsole = { 
      log: console.log,
      info: console.info,
      warn: console.warn,
      error: console.error
    };

    // 創建模擬控制台
    mockConsole = {
      log: jest.fn(),
      info: jest.fn(),
      warn: jest.fn(),
      error: jest.fn()
    };

    // 替換控制台方法
    console.log = mockConsole.log;
    console.info = mockConsole.info;
    console.warn = mockConsole.warn;
    console.error = mockConsole.error;

    // 重新導入日誌服務以使用模擬控制台
    jest.resetModules();
    const loggingModule = require('../../frontend/src/services/LoggingService');
    LoggingService = loggingModule.default;
    Logger = loggingModule.Logger;
  });

  // 在每個測試後恢復原始控制台方法
  afterEach(() => {
    console.log = originalConsole.log;
    console.info = originalConsole.info;
    console.warn = originalConsole.warn;
    console.error = originalConsole.error;
  });

  test('Logger 應該是單例模式', () => {
    expect(Logger).toBeDefined();
    const anotherLogger = LoggingService.getInstance();
    expect(Logger).toBe(anotherLogger);
  });

  test('debug 方法應該使用 console.log', () => {
    Logger.debug('測試訊息');
    expect(mockConsole.log).toHaveBeenCalledWith('[DEBUG] 測試訊息', '');
  });

  test('info 方法應該使用 console.info', () => {
    Logger.info('測試訊息');
    expect(mockConsole.info).toHaveBeenCalledWith('[INFO] 測試訊息', '');
  });

  test('warn 方法應該使用 console.warn', () => {
    Logger.warn('測試訊息');
    expect(mockConsole.warn).toHaveBeenCalledWith('[WARN] 測試訊息', '');
  });

  test('error 方法應該使用 console.error', () => {
    Logger.error('測試訊息');
    expect(mockConsole.error).toHaveBeenCalledWith('[ERROR] 測試訊息', '');
  });

  test('設置 LogLevel 後應該只顯示相應級別的日誌', () => {
    // 引入 LogLevel 枚舉
    const LogLevel = {
      DEBUG: 0,
      INFO: 1,
      WARN: 2,
      ERROR: 3,
    };

    // 設置日誌級別為 WARN
    Logger.setLogLevel(LogLevel.WARN);
    
    // 輸出各級別日誌
    Logger.debug('DEBUG 訊息');
    Logger.info('INFO 訊息');
    Logger.warn('WARN 訊息');
    Logger.error('ERROR 訊息');
    
    // 檢查調用情況
    expect(mockConsole.log).not.toHaveBeenCalled();
    expect(mockConsole.info).not.toHaveBeenCalled();
    expect(mockConsole.warn).toHaveBeenCalledWith('[WARN] WARN 訊息', '');
    expect(mockConsole.error).toHaveBeenCalledWith('[ERROR] ERROR 訊息', '');
  });

  test('標籤選項應該包含在日誌前綴中', () => {
    Logger.info('測試訊息', null, { tags: ['TEST', 'UNIT'] });
    expect(mockConsole.info).toHaveBeenCalledWith('[INFO] [TEST, UNIT] 測試訊息', '');
  });

  test('時間戳選項應該包含在日誌前綴中', () => {
    // 模擬 Date.toISOString
    const originalDateToISOString = Date.prototype.toISOString;
    Date.prototype.toISOString = jest.fn().mockReturnValue('2025-04-06T00:00:00.000Z');
    
    Logger.info('測試訊息', null, { showTimestamp: true });
    expect(mockConsole.info).toHaveBeenCalledWith('[INFO] 2025-04-06T00:00:00.000Z 測試訊息', '');
    
    // 恢復原始方法
    Date.prototype.toISOString = originalDateToISOString;
  });
}); 