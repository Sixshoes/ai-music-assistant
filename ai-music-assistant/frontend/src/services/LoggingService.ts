/**
 * LoggingService - 統一管理應用程序日誌
 * 提供不同級別的日誌輸出，並支援發展/生產環境的日誌控制
 */

interface LogOptions {
  tags?: string[];
  level?: string;
  timestamp?: boolean;
}

interface LogEntry {
  message: string;
  data?: any;
  options?: LogOptions;
  timestamp: Date;
  level: string;
}

class LoggingService {
  private logs: LogEntry[] = [];
  private maxLogs: number = 1000;
  private consoleOutputEnabled: boolean = true;
  private serverLogEnabled: boolean = false;
  private serverLogEndpoint: string = '/api/logs';
  
  constructor() {
    // 檢查環境配置
    this.consoleOutputEnabled = process.env.NODE_ENV !== 'production' || localStorage.getItem('debug') === 'true';
    this.serverLogEnabled = process.env.NODE_ENV === 'production';
  }
  
  /**
   * 記錄 INFO 級別日誌
   */
  public info(message: string, data?: any, options?: LogOptions): void {
    this.log(message, data, { ...(options || {}), level: 'info' });
  }
  
  /**
   * 記錄 DEBUG 級別日誌
   */
  public debug(message: string, data?: any, options?: LogOptions): void {
    this.log(message, data, { ...(options || {}), level: 'debug' });
  }
  
  /**
   * 記錄 WARN 級別日誌
   */
  public warn(message: string, data?: any, options?: LogOptions): void {
    this.log(message, data, { ...(options || {}), level: 'warn' });
  }
  
  /**
   * 記錄 ERROR 級別日誌
   */
  public error(message: string, data?: any, options?: LogOptions): void {
    this.log(message, data, { ...(options || {}), level: 'error' });
  }
  
  /**
   * 記錄日誌
   */
  private log(message: string, data?: any, options?: LogOptions): void {
    const timestamp = new Date();
    const level = options?.level || 'info';
    const tags = options?.tags || [];
    
    // 創建日誌條目
    const logEntry: LogEntry = {
      message,
      data,
      options,
      timestamp,
      level
    };
    
    // 添加到內部日誌
    this.logs.push(logEntry);
    
    // 確保日誌不超過最大數量
    if (this.logs.length > this.maxLogs) {
      this.logs.shift();
    }
    
    // 輸出到控制台
    if (this.consoleOutputEnabled) {
      this.outputToConsole(logEntry, tags);
    }
    
    // 發送到伺服器
    if (this.serverLogEnabled) {
      this.sendToServer(logEntry);
    }
  }
  
  /**
   * 輸出日誌到控制台
   */
  private outputToConsole(log: LogEntry, tags: string[]): void {
    const tagString = tags.length > 0 ? `[${tags.join(',')}] ` : '';
    const timestamp = log.options?.timestamp !== false ? `[${log.timestamp.toISOString()}] ` : '';
    const message = `${timestamp}${tagString}${log.message}`;
    
    switch (log.level) {
      case 'info':
        console.info(message, log.data || '');
        break;
      case 'debug':
        console.debug(message, log.data || '');
        break;
      case 'warn':
        console.warn(message, log.data || '');
        break;
      case 'error':
        console.error(message, log.data || '');
        break;
      default:
        console.log(message, log.data || '');
    }
  }
  
  /**
   * 發送日誌到伺服器
   */
  private async sendToServer(log: LogEntry): Promise<void> {
    try {
      const body = JSON.stringify({
        message: log.message,
        data: log.data,
        level: log.level,
        timestamp: log.timestamp.toISOString(),
        tags: log.options?.tags || []
      });
      
      // 使用 fetch API 發送日誌
      const response = await fetch(this.serverLogEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body
      });
      
      if (!response.ok) {
        console.error('發送日誌到伺服器失敗:', response.status, response.statusText);
      }
    } catch (error) {
      console.error('發送日誌到伺服器時出錯:', error);
    }
  }
  
  /**
   * 獲取所有日誌
   */
  public getLogs(): LogEntry[] {
    return [...this.logs];
  }
  
  /**
   * 清除所有日誌
   */
  public clearLogs(): void {
    this.logs = [];
  }
  
  /**
   * 啟用/禁用控制台輸出
   */
  public enableConsoleOutput(enabled: boolean): void {
    this.consoleOutputEnabled = enabled;
  }
  
  /**
   * 啟用/禁用伺服器日誌
   */
  public enableServerLog(enabled: boolean): void {
    this.serverLogEnabled = enabled;
  }
}

// 導出默認的 Logger 實例
export const Logger = new LoggingService();
export default Logger; 