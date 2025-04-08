/**
 * ResourcePreloader - 資源預加載服務
 * 提前加載常用資源，優化頁面載入速度
 */

import { Logger } from './LoggingService';

// 資源類型定義
type ResourceType = 'image' | 'audio' | 'font' | 'json';

// 資源項定義
interface Resource {
  url: string;
  type: ResourceType;
  priority: number; // 0-10，值越大優先級越高
  key?: string;     // 可選的標識符
}

// 加載資源的狀態
interface ResourceStatus {
  loaded: boolean;
  error: boolean;
  timestamp: number;
  resource: Resource;
}

class ResourcePreloader {
  private resources: Map<string, ResourceStatus> = new Map();
  private imageCache: Map<string, HTMLImageElement> = new Map();
  private audioCache: Map<string, ArrayBuffer> = new Map();
  private jsonCache: Map<string, any> = new Map();
  private fontCache: Set<string> = new Set();
  
  // 已加載的資源計數
  private loadedCount: number = 0;
  
  // 是否已初始化
  private initialized: boolean = false;
  
  // 常用圖片資源路徑列表
  private commonImagePaths: string[] = [
    '/images/logo.png',
    '/images/hero-bg.jpg',
    '/images/text-to-music.jpg',
    '/images/melody-arrangement.jpg',
    '/images/music-theory.jpg',
    '/images/placeholder-cover.jpg',
    '/favicon.ico'
  ];
  
  // 常用音頻資源路徑列表
  private commonAudioPaths: string[] = [
    '/sounds/note-c4.mp3',
    '/sounds/note-e4.mp3',
    '/sounds/note-g4.mp3',
    '/sounds/click.mp3'
  ];
  
  // 常用字體資源列表
  private commonFonts: string[] = [
    'Noto Sans TC',
    'Roboto',
    'Roboto Mono'
  ];

  constructor() {
    Logger.info('初始化資源預加載器', null, { tags: ['PRELOAD'] });
  }

  /**
   * 初始化預加載服務並開始加載常用資源
   */
  initialize(): void {
    if (this.initialized) {
      return;
    }
    
    Logger.info('開始預加載常用資源', null, { tags: ['PRELOAD'] });
    
    // 註冊常用圖片資源
    this.commonImagePaths.forEach((path, index) => {
      this.registerResource({
        url: path,
        type: 'image',
        priority: 10 - index  // 先列出的優先級更高
      });
    });
    
    // 註冊常用音頻資源
    this.commonAudioPaths.forEach((path, index) => {
      this.registerResource({
        url: path,
        type: 'audio',
        priority: 5 - index
      });
    });
    
    // 註冊常用字體
    this.commonFonts.forEach((font, index) => {
      this.preloadFont(font);
    });
    
    // 開始加載資源
    this.preloadResources();
    
    this.initialized = true;
  }

  /**
   * 註冊需要預加載的資源
   * @param resource 資源信息
   */
  registerResource(resource: Resource): void {
    const key = resource.key || resource.url;
    
    if (this.resources.has(key)) {
      Logger.debug(`資源已註冊: ${key}`, null, { tags: ['PRELOAD'] });
      return;
    }
    
    this.resources.set(key, {
      loaded: false,
      error: false,
      timestamp: Date.now(),
      resource
    });
    
    Logger.debug(`註冊資源: ${resource.type} - ${key}`, null, { tags: ['PRELOAD'] });
  }

  /**
   * 預加載所有註冊的資源
   */
  preloadResources(): void {
    // 按優先級排序資源
    const sortedResources = Array.from(this.resources.entries())
      .filter(([_, status]) => !status.loaded && !status.error)
      .sort((a, b) => b[1].resource.priority - a[1].resource.priority);
    
    // 批次加載資源
    const batchSize = 3; // 同時加載的資源數量
    
    for (let i = 0; i < Math.min(batchSize, sortedResources.length); i++) {
      const [key, status] = sortedResources[i];
      this.loadResource(key, status.resource);
    }
  }

  /**
   * 加載單個資源
   * @param key 資源鍵
   * @param resource 資源信息
   */
  private async loadResource(key: string, resource: Resource): Promise<void> {
    const maxRetries = 3;
    let retryCount = 0;

    const tryLoad = async (): Promise<void> => {
      try {
        switch (resource.type) {
          case 'image':
            await this.preloadImage(resource.url, key);
            break;
          case 'audio':
            await this.preloadAudio(resource.url, key);
            break;
          case 'json':
            await this.preloadJson(resource.url, key);
            break;
        }
        
        // 更新資源狀態
        const status = this.resources.get(key);
        if (status) {
          status.loaded = true;
          status.timestamp = Date.now();
          this.loadedCount++;
        }
        
        Logger.debug(`成功加載資源: ${resource.type} - ${key}`, null, { tags: ['PRELOAD'] });
      } catch (error) {
        if (retryCount < maxRetries) {
          retryCount++;
          Logger.warn(`資源加載失敗，正在重試 (${retryCount}/${maxRetries}): ${resource.type} - ${key}`, error, { tags: ['PRELOAD'] });
          await new Promise(resolve => setTimeout(resolve, 1000 * retryCount)); // 延遲重試
          return tryLoad();
        }
        
        Logger.error(`資源加載失敗: ${resource.type} - ${key}`, error, { tags: ['PRELOAD'] });
        
        // 更新錯誤狀態
        const status = this.resources.get(key);
        if (status) {
          status.error = true;
        }
      }
    };

    await tryLoad();
    // 檢查是否有更多資源需要加載
    this.preloadResources();
  }

  /**
   * 預加載圖片
   * @param url 圖片URL
   * @param key 可選的資源鍵
   */
  private preloadImage(url: string, key: string = url): Promise<void> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      
      img.onload = () => {
        this.imageCache.set(key, img);
        resolve();
      };
      
      img.onerror = (error) => {
        // 圖片加載失敗時，嘗試使用備用圖片
        console.warn(`圖片 ${url} 加載失敗，使用備用圖片`);
        const fallbackImg = new Image();
        fallbackImg.onload = () => {
          this.imageCache.set(key, fallbackImg);
          resolve();
        };
        fallbackImg.onerror = () => {
          reject(error);
        };
        // 使用placeholder.png作為備用圖片
        fallbackImg.src = '/images/placeholder.png';
      };
      
      img.src = url;
    });
  }

  /**
   * 預加載音頻
   * @param url 音頻URL
   * @param key 可選的資源鍵
   */
  private preloadAudio(url: string, key: string = url): Promise<void> {
    return new Promise((resolve, reject) => {
      fetch(url)
        .then((response) => {
          if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
          }
          return response.arrayBuffer();
        })
        .then((buffer) => {
          this.audioCache.set(key, buffer);
          resolve();
        })
        .catch((error) => {
          reject(error);
        });
    });
  }

  /**
   * 預加載JSON數據
   * @param url JSON URL
   * @param key 可選的資源鍵
   */
  private preloadJson(url: string, key: string = url): Promise<void> {
    return new Promise((resolve, reject) => {
      fetch(url)
        .then((response) => {
          if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
          }
          return response.json();
        })
        .then((data) => {
          this.jsonCache.set(key, data);
          resolve();
        })
        .catch((error) => {
          reject(error);
        });
    });
  }

  /**
   * 預加載字體
   * @param fontFamily 字體名稱
   */
  private preloadFont(fontFamily: string): void {
    try {
      // 將字體名稱添加到緩存中
      this.fontCache.add(fontFamily);
      
      // 在 head 中添加預加載字體的 link 標籤
      if (typeof window !== 'undefined') {
        // 創建 link 元素
        const link = window.document.createElement('link');
        link.rel = 'preload';
        link.href = `https://fonts.googleapis.com/css2?family=${encodeURIComponent(fontFamily.replace(/ /g, '+'))}&display=swap`;
        link.as = 'style';
        
        // 將 link 添加到 head
        window.document.head.appendChild(link);
        
        Logger.debug(`添加字體預加載 link: ${fontFamily}`, null, { tags: ['PRELOAD'] });
      }
    } catch (error) {
      Logger.error(`字體預加載出錯: ${fontFamily}`, error, { tags: ['PRELOAD'] });
    }
  }

  /**
   * 獲取預加載的圖片
   * @param key 圖片鍵
   */
  getImage(key: string): HTMLImageElement | null {
    return this.imageCache.get(key) || null;
  }

  /**
   * 獲取預加載的音頻數據
   * @param key 音頻鍵
   */
  getAudio(key: string): ArrayBuffer | null {
    return this.audioCache.get(key) || null;
  }

  /**
   * 獲取預加載的JSON數據
   * @param key JSON鍵
   */
  getJson(key: string): any | null {
    return this.jsonCache.get(key) || null;
  }

  /**
   * 獲取預加載狀態
   */
  getStatus(): { total: number; loaded: number; progress: number } {
    const total = this.resources.size;
    return {
      total,
      loaded: this.loadedCount,
      progress: total > 0 ? (this.loadedCount / total) : 0
    };
  }

  /**
   * 清除所有預加載的資源
   */
  clearCache(): void {
    this.imageCache.clear();
    this.audioCache.clear();
    this.jsonCache.clear();
    this.fontCache.clear();
    this.loadedCount = 0;
    
    this.resources.forEach((status) => {
      status.loaded = false;
      status.error = false;
    });
    
    Logger.info('清除資源預加載緩存', null, { tags: ['PRELOAD'] });
  }
}

// 導出服務實例
export const resourcePreloader = new ResourcePreloader(); 