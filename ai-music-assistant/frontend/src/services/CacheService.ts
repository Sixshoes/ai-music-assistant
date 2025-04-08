/**
 * CacheService - 緩存服務
 * 處理前端本地緩存以提高應用響應速度
 */

import { Logger } from './LoggingService';

// 定義緩存配置
interface CacheConfig {
  // 緩存生存時間（毫秒），0 代表永不過期
  ttl: number;
  // 最大緩存條目數
  maxEntries?: number;
  // 緩存區分名稱
  namespace?: string;
}

// 定義緩存項結構
interface CacheItem<T> {
  // 緩存的實際數據
  data: T;
  // 過期時間戳
  expiry: number;
  // 上次訪問時間戳
  lastAccessed: number;
}

// 定義默認緩存配置
const DEFAULT_CACHE_CONFIG: CacheConfig = {
  ttl: 3600000, // 1小時
  maxEntries: 100,
  namespace: 'app'
};

class CacheService {
  private caches: Map<string, Map<string, CacheItem<any>>> = new Map();
  private configs: Map<string, CacheConfig> = new Map();

  constructor() {
    // 初始化默認緩存
    this.createCache('default', DEFAULT_CACHE_CONFIG);

    // 每分鐘清理過期緩存
    setInterval(() => this.purgeExpiredItems(), 60000);
  }

  /**
   * 創建新的緩存命名空間
   * @param namespace 命名空間名稱
   * @param config 緩存配置
   */
  createCache(namespace: string, config: Partial<CacheConfig> = {}): void {
    const fullConfig: CacheConfig = { ...DEFAULT_CACHE_CONFIG, ...config, namespace };
    
    if (this.caches.has(namespace)) {
      Logger.warn(`緩存 ${namespace} 已存在，將被重置`, null, { tags: ['CACHE'] });
      this.caches.delete(namespace);
    }
    
    this.caches.set(namespace, new Map());
    this.configs.set(namespace, fullConfig);
    Logger.debug(`創建緩存命名空間: ${namespace}`, { config: fullConfig }, { tags: ['CACHE'] });
  }

  /**
   * 從緩存獲取數據
   * @param key 緩存鍵
   * @param namespace 命名空間，默認為 'default'
   * @returns 緩存數據或 null（如果未命中）
   */
  get<T>(key: string, namespace: string = 'default'): T | null {
    const cache = this.caches.get(namespace);
    if (!cache) {
      Logger.warn(`緩存命名空間 ${namespace} 不存在`, null, { tags: ['CACHE'] });
      return null;
    }

    const item = cache.get(key);
    if (!item) {
      return null;
    }

    // 檢查是否過期
    const now = Date.now();
    if (item.expiry !== 0 && now > item.expiry) {
      cache.delete(key);
      return null;
    }

    // 更新訪問時間
    item.lastAccessed = now;
    return item.data as T;
  }

  /**
   * 設置緩存數據
   * @param key 緩存鍵
   * @param data 要緩存的數據
   * @param namespace 命名空間，默認為 'default'
   * @param customTTL 自定義TTL，覆蓋命名空間配置
   * @returns 是否設置成功
   */
  set<T>(key: string, data: T, namespace: string = 'default', customTTL?: number): boolean {
    const cache = this.caches.get(namespace);
    const config = this.configs.get(namespace);
    
    if (!cache || !config) {
      Logger.warn(`緩存命名空間 ${namespace} 不存在`, null, { tags: ['CACHE'] });
      return false;
    }

    // 檢查是否需要清理空間
    if (config.maxEntries && cache.size >= config.maxEntries && !cache.has(key)) {
      this.evictLRU(namespace);
    }

    const now = Date.now();
    const ttl = customTTL !== undefined ? customTTL : config.ttl;
    
    const item: CacheItem<T> = {
      data,
      expiry: ttl === 0 ? 0 : now + ttl,
      lastAccessed: now
    };

    cache.set(key, item);
    Logger.debug(`設置緩存: ${namespace}:${key}`, { ttl, size: cache.size }, { tags: ['CACHE'] });
    return true;
  }

  /**
   * 刪除緩存項
   * @param key 緩存鍵
   * @param namespace 命名空間，默認為 'default'
   * @returns 是否刪除成功
   */
  delete(key: string, namespace: string = 'default'): boolean {
    const cache = this.caches.get(namespace);
    if (!cache) {
      return false;
    }
    
    const result = cache.delete(key);
    if (result) {
      Logger.debug(`刪除緩存: ${namespace}:${key}`, null, { tags: ['CACHE'] });
    }
    return result;
  }

  /**
   * 清除命名空間的所有緩存
   * @param namespace 命名空間，默認為 'default'
   * @returns 是否清除成功
   */
  clear(namespace: string = 'default'): boolean {
    const cache = this.caches.get(namespace);
    if (!cache) {
      return false;
    }
    
    cache.clear();
    Logger.debug(`清除緩存命名空間: ${namespace}`, null, { tags: ['CACHE'] });
    return true;
  }

  /**
   * 獲取緩存狀態統計
   * @returns 各命名空間的緩存狀態
   */
  getStats(): Record<string, { size: number; config: CacheConfig }> {
    const stats: Record<string, { size: number; config: CacheConfig }> = {};
    
    for (const [namespace, cache] of this.caches.entries()) {
      const config = this.configs.get(namespace);
      if (config) {
        stats[namespace] = {
          size: cache.size,
          config
        };
      }
    }
    
    return stats;
  }

  /**
   * 清理過期項目
   * @private
   */
  private purgeExpiredItems(): void {
    const now = Date.now();
    let purgedCount = 0;
    
    for (const [namespace, cache] of this.caches.entries()) {
      for (const [key, item] of cache.entries()) {
        if (item.expiry !== 0 && now > item.expiry) {
          cache.delete(key);
          purgedCount++;
        }
      }
    }
    
    if (purgedCount > 0) {
      Logger.debug(`清理過期緩存項: ${purgedCount} 項已刪除`, null, { tags: ['CACHE'] });
    }
  }

  /**
   * 根據LRU策略清除一個項目
   * @param namespace 命名空間
   * @private
   */
  private evictLRU(namespace: string): void {
    const cache = this.caches.get(namespace);
    if (!cache || cache.size === 0) {
      return;
    }
    
    let oldestKey: string | null = null;
    let oldestAccess = Infinity;
    
    for (const [key, item] of cache.entries()) {
      if (item.lastAccessed < oldestAccess) {
        oldestAccess = item.lastAccessed;
        oldestKey = key;
      }
    }
    
    if (oldestKey) {
      cache.delete(oldestKey);
      Logger.debug(`LRU清理: 從 ${namespace} 中刪除 ${oldestKey}`, null, { tags: ['CACHE'] });
    }
  }
}

// 導出服務實例
export const cacheService = new CacheService(); 