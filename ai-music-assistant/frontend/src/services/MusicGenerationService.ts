import axios, { AxiosInstance } from 'axios';
import { 
  MusicParameters, 
  MusicResult, 
  /* @ts-ignore - 未使用但為將來使用保留 */
  // MusicAnalysis, 
  CommandResponse, 
  CommandStatus, 
  MelodyInput, 
  AudioInput, 
  /* @ts-ignore - 未使用但為將來使用保留 */
  // CommandType,
  /* @ts-ignore - 未使用但為將來使用保留 */
  // ProcessingStatus,
  ModelType,
  MusicCommand,
  /* @ts-ignore - 未使用但為將來使用保留 */
  // MusicData 
} from '../types/music';
import { cacheService } from './CacheService';
import { Logger } from './LoggingService';

/**
 * 音樂生成服務類，處理與後端 API 的通信
 */
class MusicGenerationService {
  private baseUrl: string = '/api';
  private apiClient: AxiosInstance;
  private pollInterval: number = 1000; // 默認輪詢間隔（毫秒）
  private readonly CACHE_NAMESPACE = 'music-generation';
  private readonly RESULT_CACHE_TTL = 3600000; // 1小時
  
  constructor() {
    // 初始化axios客戶端
    this.apiClient = axios.create({
      baseURL: this.baseUrl,
      timeout: 30000, // 30秒超時
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    // 錯誤處理攔截器
    this.apiClient.interceptors.response.use(
      response => response,
      error => {
        console.error('API請求失敗', error);
        if (error.response) {
          console.error('狀態碼:', error.response.status);
          console.error('響應數據:', error.response.data);
        }
        return Promise.reject(error);
      }
    );
    
    // 創建音樂生成專用緩存
    cacheService.createCache(this.CACHE_NAMESPACE, {
      ttl: this.RESULT_CACHE_TTL,
      maxEntries: 50  // 限制緩存條目數量以節省內存
    });
    
    Logger.info('初始化音樂生成服務', null, { tags: ['MUSIC'] });
  }
  
  /**
   * 設置輪詢間隔
   * @param milliseconds 毫秒數
   */
  setPollInterval(milliseconds: number): void {
    this.pollInterval = milliseconds;
  }
  
  /**
   * 文字描述生成音樂
   * 
   * @param text 文字描述
   * @param parameters 音樂參數
   * @param modelPreferences 偏好使用的模型
   * @returns 指令ID及狀態
   */
  async generateMusicFromText(
    text: string, 
    parameters?: MusicParameters, 
    modelPreferences?: ModelType[]
  ): Promise<CommandResponse> {
    try {
      // 生成緩存鍵
      const cacheKey = `text_${this.hashInput(text)}_${this.hashInput(JSON.stringify(parameters || {}))}_${this.hashInput(JSON.stringify(modelPreferences || []))}`;
      
      // 檢查緩存
      const cachedResult = cacheService.get<CommandResponse>(cacheKey, this.CACHE_NAMESPACE);
      if (cachedResult) {
        Logger.info('使用緩存的音樂生成結果', { cacheKey }, { tags: ['MUSIC', 'CACHE'] });
        return cachedResult;
      }
      
      // 沒有緩存，執行API請求
      const command: MusicCommand = {
        command_type: 'text_to_music',
        text_input: text,
        parameters,
        model_preferences: modelPreferences
      };
      
      Logger.info('發起文本到音樂請求', { textLength: text.length }, { tags: ['MUSIC', 'API'] });
      const response = await this.apiClient.post('/commands', command);
      
      // 緩存結果
      cacheService.set(cacheKey, response.data, this.CACHE_NAMESPACE);
      return response.data;
    } catch (error) {
      Logger.error('文本到音樂請求失敗', error, { tags: ['MUSIC', 'API'] });
      throw error;
    }
  }
  
  /**
   * 旋律生成編曲
   * 
   * @param melodyInput 旋律輸入
   * @param additionalText 附加文字描述
   * @param parameters 音樂參數
   * @returns 指令ID及狀態
   */
  async generateArrangementFromMelody(
    melodyInput: MelodyInput,
    additionalText?: string,
    parameters?: MusicParameters
  ): Promise<CommandResponse> {
    try {
      const command: MusicCommand = {
        command_type: 'melody_to_arrangement',
        text_input: additionalText,
        melody_input: melodyInput,
        parameters
      };
      
      const response = await this.apiClient.post('/commands', command);
      return response.data;
    } catch (error) {
      console.error('旋律生成編曲請求失敗', error);
      throw error;
    }
  }
  
  /**
   * 音頻生成編曲
   * 
   * @param audioDataUrl 音頻數據URL (base64)
   * @param additionalText 附加文字描述
   * @param parameters 音樂參數
   * @returns 指令ID及狀態
   */
  async generateArrangementFromAudio(
    audioDataUrl: string, 
    format: string = 'wav',
    additionalText?: string, 
    parameters?: MusicParameters
  ): Promise<CommandResponse> {
    try {
      const audioInput: AudioInput = {
        audio_data_url: audioDataUrl,
        format
      };
      
      const command: MusicCommand = {
        command_type: 'pitch_correction',
        text_input: additionalText,
        audio_input: audioInput,
        parameters
      };
      
      const response = await this.apiClient.post('/commands', command);
      return response.data;
    } catch (error) {
      console.error('音頻生成編曲請求失敗', error);
      throw error;
    }
  }
  
  /**
   * 分析音樂
   * 
   * @param audioDataUrl 音頻數據URL (base64)
   * @param format 格式
   * @returns 指令ID及狀態
   */
  async analyzeMusicFromAudio(
    audioDataUrl: string,
    format: string = 'wav'
  ): Promise<CommandResponse> {
    try {
      const audioInput: AudioInput = {
        audio_data_url: audioDataUrl,
        format
      };
      
      const command: MusicCommand = {
        command_type: 'music_analysis',
        audio_input: audioInput
      };
      
      const response = await this.apiClient.post('/commands', command);
      return response.data;
    } catch (error) {
      console.error('音樂分析請求失敗', error);
      throw error;
    }
  }
  
  /**
   * 風格轉換
   * 
   * @param audioDataUrl 音頻數據URL (base64)
   * @param targetStyle 目標風格
   * @param parameters 音樂參數
   * @returns 指令ID及狀態
   */
  async transferStyle(
    audioDataUrl: string,
    targetStyle: string,
    parameters?: MusicParameters
  ): Promise<CommandResponse> {
    try {
      const audioInput: AudioInput = {
        audio_data_url: audioDataUrl,
        format: 'wav'
      };
      
      const command: MusicCommand = {
        command_type: 'style_transfer',
        text_input: targetStyle,
        audio_input: audioInput,
        parameters
      };
      
      const response = await this.apiClient.post('/commands', command);
      return response.data;
    } catch (error) {
      console.error('風格轉換請求失敗', error);
      throw error;
    }
  }
  
  /**
   * 即興演奏
   * 
   * @param chordProgression 和弦進行
   * @param parameters 音樂參數
   * @returns 指令ID及狀態
   */
  async generateImprovisation(
    chordProgression: string,
    parameters?: MusicParameters
  ): Promise<CommandResponse> {
    try {
      const command: MusicCommand = {
        command_type: 'improvisation',
        text_input: chordProgression,
        parameters
      };
      
      const response = await this.apiClient.post('/commands', command);
      return response.data;
    } catch (error) {
      console.error('即興演奏請求失敗', error);
      throw error;
    }
  }
  
  /**
   * 獲取指令處理狀態
   * 
   * @param commandId 指令ID
   * @returns 處理狀態
   */
  async getCommandStatus(commandId: string): Promise<CommandStatus> {
    try {
      const response = await this.apiClient.get(`/commands/${commandId}/status`);
      return response.data;
    } catch (error) {
      console.error('獲取指令狀態失敗', error);
      throw error;
    }
  }
  
  /**
   * 取消正在處理的指令
   * 
   * @param commandId 指令ID
   * @returns 取消狀態
   */
  async cancelCommand(commandId: string): Promise<CommandResponse> {
    try {
      const response = await this.apiClient.delete(`/commands/${commandId}`);
      return response.data;
    } catch (error) {
      console.error('取消指令失敗', error);
      throw error;
    }
  }
  
  /**
   * 獲取音樂生成結果，使用緩存優化
   * 
   * @param commandId 指令ID
   * @returns 音樂生成結果
   */
  async getMusicResult(commandId: string): Promise<MusicResult> {
    try {
      // 檢查緩存
      const cacheKey = `result_${commandId}`;
      const cachedResult = cacheService.get<MusicResult>(cacheKey, this.CACHE_NAMESPACE);
      
      if (cachedResult) {
        Logger.info('使用緩存的音樂結果', { commandId }, { tags: ['MUSIC', 'CACHE'] });
        return cachedResult;
      }
      
      Logger.info('獲取音樂結果', { commandId }, { tags: ['MUSIC', 'API'] });
      // 開發環境使用模擬數據
      if (process.env.NODE_ENV === 'development') {
        const mockResult = this._getMockMusicResult(commandId);
        cacheService.set(cacheKey, mockResult, this.CACHE_NAMESPACE);
        return mockResult;
      }
      
      // 生產環境調用API
      const response = await this.apiClient.get(`/music-result/${commandId}`);
      
      // 緩存結果
      cacheService.set(cacheKey, response.data, this.CACHE_NAMESPACE);
      return response.data;
    } catch (error) {
      Logger.error('獲取音樂結果失敗', error, { tags: ['MUSIC', 'API'] });
      throw error;
    }
  }
  
  /**
   * 生成模擬音樂結果數據 (僅用於開發)
   */
  private _getMockMusicResult(commandId: string): MusicResult {
    return {
      command_id: commandId,
      status: 'completed',
      music_data: {
        audio_data: 'data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA=',  // 一個有效的空WAV檔案的base64編碼
        midi_data: 'TVRoZAAAAAYAAQABAeBNVHJrAAAAGQD/UQMHoSAA/1gEBAIYCAD/AAAA/y8ATVRyawAAABkA/1EDCKEgAP9YBAQCGAgA/wAAAP8vAA==',
        score_data: {
          musicxml: '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">\n<score-partwise version="3.1">\n  <part-list>\n    <score-part id="P1">\n      <part-name>Piano</part-name>\n    </score-part>\n  </part-list>\n  <part id="P1">\n    <measure number="1">\n      <attributes>\n        <divisions>1</divisions>\n        <key>\n          <fifths>0</fifths>\n        </key>\n        <time>\n          <beats>4</beats>\n          <beat-type>4</beat-type>\n        </time>\n        <clef>\n          <sign>G</sign>\n          <line>2</line>\n        </clef>\n      </attributes>\n      <note>\n        <pitch>\n          <step>C</step>\n          <octave>4</octave>\n        </pitch>\n        <duration>4</duration>\n        <type>whole</type>\n      </note>\n    </measure>\n  </part>\n</score-partwise>',
          pdf: 'JVBERi0xLjQKJcOkw7zDtsOfCjIgMCBvYmoKPDwvTGVuZ3RoIDMgMCBSL0ZpbHRlci9GbGF0ZURlY29kZT4+CnN0cmVhbQp4nDPQM1Qo5ypUMABCM0MjBXNLI4WUXC4FQz0LhZTUYgV9S4XkjNQ8hZzUvBKF5PwihezUnJLM/DyF4pKCosRcrmKuQAWuXC4AaS4T6QplbmRzdHJlYW0KZW5kb2JqCgozIDAgb2JqCjg2CmVuZG9iagoKNSAwIG9iago8PC9MZW5ndGggNiAwIFIvRmlsdGVyL0ZsYXRlRGVjb2RlL0xlbmd0aDEgMjM1MTY+PgpzdHJlYW0KeJztXQd8VFX6P/feN',
          svg: '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="100" height="100">\n  <circle cx="50" cy="50" r="40" stroke="black" stroke-width="3" fill="red" />\n</svg>'
        }
      },
      analysis: {
        key: 'C',
        time_signature: '4/4',
        chord_progression: {
          chords: ['C', 'G', 'Am', 'F'],
          durations: [1, 1, 1, 1]
        },
        tempo: 120,
        structure: {
          intro: [0, 4],
          verse: [4, 12],
          chorus: [12, 20],
          outro: [20, 24]
        }
      },
      suggestions: ['建議使用更多和聲變化', '考慮在副歌部分增加力度']
    };
  }
  
  /**
   * 輪詢直到命令完成處理或失敗
   * 
   * @param commandId 指令ID
   * @param maxAttempts 最大嘗試次數
   * @returns 音樂結果
   */
  async pollUntilComplete(commandId: string, maxAttempts: number = 60): Promise<MusicResult> {
    let attempts = 0;
    
    while (attempts < maxAttempts) {
      const status = await this.getCommandStatus(commandId);
      
      if (status.status === 'completed') {
        return this.getMusicResult(commandId);
      }
      
      if (status.status === 'failed' || status.status === 'cancelled') {
        throw new Error(`命令處理失敗: ${status.error || '未知錯誤'}`);
      }
      
      // 等待下一次輪詢
      await new Promise(resolve => setTimeout(resolve, this.pollInterval));
      attempts++;
    }
    
    throw new Error(`輪詢超時: 命令處理時間過長`);
  }
  
  /**
   * 將 Base64 編碼的數據下載為文件
   * 
   * @param base64Data Base64 編碼的數據
   * @param filename 文件名
   * @param mimeType MIME 類型
   */
  downloadBase64File(base64Data: string, filename: string, mimeType: string): void {
    // 處理 Data URL 格式
    const dataUrl = base64Data.includes('base64,') 
      ? base64Data 
      : `data:${mimeType};base64,${base64Data}`;
    
    const link = document.createElement('a');
    link.href = dataUrl;
    link.download = filename;
    link.click();
  }
  
  /**
   * 下載 MIDI 文件
   * 
   * @param base64MidiData Base64 編碼的 MIDI 數據
   * @param filename 文件名 (默認為 "generated_music.mid")
   */
  downloadMidi(base64MidiData: string, filename: string = "generated_music.mid"): void {
    this.downloadBase64File(base64MidiData, filename, 'audio/midi');
  }
  
  /**
   * 下載音頻文件
   * 
   * @param base64AudioData Base64 編碼的音頻數據
   * @param filename 文件名 (默認為 "generated_music.mp3")
   */
  downloadAudio(base64AudioData: string, filename: string = "generated_music.mp3"): void {
    this.downloadBase64File(base64AudioData, filename, 'audio/mpeg');
  }
  
  /**
   * 下載樂譜文件
   * 
   * @param base64ScoreData Base64 編碼的樂譜數據
   * @param format 樂譜格式 ("pdf" 或 "musicxml")
   * @param filename 文件名 (默認基於格式)
   */
  downloadScore(base64ScoreData: string, format: 'pdf' | 'musicxml' | 'svg', filename?: string): void {
    const mimeTypes = {
      'pdf': 'application/pdf',
      'musicxml': 'application/vnd.recordare.musicxml+xml',
      'svg': 'image/svg+xml'
    };
    
    const defaultNames = {
      'pdf': 'score.pdf',
      'musicxml': 'score.musicxml',
      'svg': 'score.svg'
    };
    
    this.downloadBase64File(
      base64ScoreData, 
      filename || defaultNames[format], 
      mimeTypes[format]
    );
  }
  
  /**
   * 清除特定指令的緩存
   * 
   * @param commandId 指令ID
   */
  clearResultCache(commandId: string): void {
    const cacheKey = `result_${commandId}`;
    cacheService.delete(cacheKey, this.CACHE_NAMESPACE);
    Logger.debug('清除音樂結果緩存', { commandId }, { tags: ['MUSIC', 'CACHE'] });
  }
  
  /**
   * 清除所有音樂生成相關的緩存
   */
  clearAllCaches(): void {
    cacheService.clear(this.CACHE_NAMESPACE);
    Logger.info('清除所有音樂生成緩存', null, { tags: ['MUSIC', 'CACHE'] });
  }
  
  /**
   * 為輸入生成雜湊值，用於緩存鍵
   * 
   * @private
   * @param input 輸入字符串
   * @returns 雜湊字符串
   */
  private hashInput(input: string): string {
    // 簡單的雜湊實現，實際應用可以使用更複雜的算法
    let hash = 0;
    for (let i = 0; i < input.length; i++) {
      const char = input.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // 轉換為32位整數
    }
    return hash.toString(16);
  }
}

// 導出服務實例
export const musicGenerationService = new MusicGenerationService(); 