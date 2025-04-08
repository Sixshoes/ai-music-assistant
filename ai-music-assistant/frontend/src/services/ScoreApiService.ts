import axios from 'axios';
import { Logger } from './LoggingService';

interface ScoreExportOptions {
  format: 'musicxml' | 'pdf' | 'midi' | 'svg';
  scoreData: any;
  filename?: string;
}

interface MuseScoreIntegrationOptions {
  midiData: string;
  format: 'pdf' | 'mscz' | 'png' | 'svg';
}

class ScoreApiService {
  private baseUrl: string = '/api';
  
  /**
   * 檢查 MuseScore 整合狀態
   */
  async checkMuseScoreStatus(): Promise<boolean> {
    try {
      Logger.info('檢查 MuseScore 整合狀態', {}, { tags: ['SCORE_API'] });
      
      // 在開發環境下模擬
      if (process.env.NODE_ENV === 'development') {
        return true;
      }
      
      const response = await axios.get(`${this.baseUrl}/score/musescore-status`);
      return response.data?.available || false;
    } catch (error) {
      Logger.error('檢查 MuseScore 整合狀態失敗', error, { tags: ['SCORE_API'] });
      return false;
    }
  }
  
  /**
   * 將 MusicXML 轉換為指定格式
   */
  async exportScore(options: ScoreExportOptions): Promise<string> {
    try {
      Logger.info('匯出樂譜', { format: options.format }, { tags: ['SCORE_API'] });
      
      // 在開發環境下模擬
      if (process.env.NODE_ENV === 'development') {
        // 返回模擬的 base64 數據
        return this.getMockExportData(options.format);
      }
      
      const response = await axios.post(`${this.baseUrl}/score/export`, {
        score_data: options.scoreData,
        format: options.format,
        filename: options.filename
      });
      
      return response.data?.data || '';
    } catch (error) {
      Logger.error('匯出樂譜失敗', error, { tags: ['SCORE_API'] });
      throw new Error('匯出樂譜失敗');
    }
  }
  
  /**
   * 使用 MuseScore 處理 MIDI 數據
   */
  async processWithMuseScore(options: MuseScoreIntegrationOptions): Promise<string> {
    try {
      Logger.info('使用 MuseScore 處理 MIDI', { format: options.format }, { tags: ['SCORE_API'] });
      
      // 在開發環境下模擬
      if (process.env.NODE_ENV === 'development') {
        return this.getMockExportData(options.format);
      }
      
      const response = await axios.post(`${this.baseUrl}/score/musescore-process`, {
        midi_data: options.midiData,
        format: options.format
      });
      
      return response.data?.data || '';
    } catch (error) {
      Logger.error('使用 MuseScore 處理 MIDI 失敗', error, { tags: ['SCORE_API'] });
      throw new Error('使用 MuseScore 處理 MIDI 失敗');
    }
  }
  
  /**
   * 解析 MusicXML 數據
   */
  async parseMusicXML(xmlData: string): Promise<any> {
    try {
      Logger.info('解析 MusicXML', { size: xmlData.length }, { tags: ['SCORE_API'] });
      
      // 在開發環境下模擬
      if (process.env.NODE_ENV === 'development') {
        // 返回模擬的解析結果
        return {
          timeSignature: '4/4',
          keySignature: 'C',
          tempo: 120,
          instruments: ['piano'],
          measures: 4,
          notes: [
            { key: 'C/4', duration: 'q' },
            { key: 'D/4', duration: 'q' },
            { key: 'E/4', duration: 'q' },
            { key: 'F/4', duration: 'q' }
          ]
        };
      }
      
      const response = await axios.post(`${this.baseUrl}/score/parse-musicxml`, {
        xml_data: xmlData
      });
      
      return response.data?.score_data || {};
    } catch (error) {
      Logger.error('解析 MusicXML 失敗', error, { tags: ['SCORE_API'] });
      throw new Error('解析 MusicXML 失敗');
    }
  }

  /**
   * 生成模擬的匯出數據（用於開發環境）
   */
  private getMockExportData(format: string): string {
    switch (format) {
      case 'pdf':
        return 'JVBERi0xLjQKJcOkw7zDtsOfCjIgMCBvYmoKPDwvTGVuZ3RoIDMgMCBSL0ZpbHRlci9GbGF0ZURlY29kZT4+CnN0cmVhbQp4nDPQM1Qo5ypUMABCM0MjBXNLI4WUXC4FQz0LhZTUYgV9S4XkjNQ8hZzUvBKF5PwihezUnJLM/DyF4pKCosRcrmKuQAWuXC4AaS4T6QplbmRzdHJlYW0KZW5kb2JqCgozIDAgb2JqCjg2CmVuZG9iagoKNSAwIG9iago8PC9MZW5ndGggNiAwIFIvRmlsdGVyL0ZsYXRlRGVjb2RlL0xlbmd0aDEgMjM1MTY+PgpzdHJlYW0KeJztXQd8VFX6P/feN';
      case 'musicxml':
        return 'PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPCFET0NUWVBFIHNjb3JlLXBhcnR3aXNlIFBVQkxJQyAiLS8vUmVjb3JkYXJlLy9EVEQgTXVzaWNYTUwgMy4xIFBhcnR3aXNlLy9FTiIgImh0dHA6Ly93d3cubXVzaWN4bWwub3JnL2R0ZHMvcGFydHdpc2UuZHRkIj4KPHNjb3JlLXBhcnR3aXNlIHZlcnNpb249IjMuMSI+CiAgPHBhcnQtbGlzdD4KICAgIDxzY29yZS1wYXJ0IGlkPSJQMSI+CiAgICAgIDxwYXJ0LW5hbWU+UGlhbm88L3BhcnQtbmFtZT4KICAgIDwvc2NvcmUtcGFydD4KICA8L3BhcnQtbGlzdD4KICA8cGFydCBpZD0iUDEiPgogICAgPG1lYXN1cmUgbnVtYmVyPSIxIj4KICAgICAgPGF0dHJpYnV0ZXM+CiAgICAgICAgPGRpdmlzaW9ucz4xPC9kaXZpc2lvbnM+CiAgICAgICAgPGtleT4KICAgICAgICAgIDxmaWZ0aHM+MDwvZmlmdGhzPgogICAgICAgIDwva2V5PgogICAgICAgIDx0aW1lPgogICAgICAgICAgPGJlYXRzPjQ8L2JlYXRzPgogICAgICAgICAgPGJlYXQtdHlwZT40PC9iZWF0LXR5cGU+CiAgICAgICAgPC90aW1lPgogICAgICAgIDxjbGVmPgogICAgICAgICAgPHNpZ24+Rzwvc2lnbj4KICAgICAgICAgIDxsaW5lPjI8L2xpbmU+CiAgICAgICAgPC9jbGVmPgogICAgICA8L2F0dHJpYnV0ZXM+CiAgICAgIDxub3RlPgogICAgICAgIDxwaXRjaD4KICAgICAgICAgIDxzdGVwPkM8L3N0ZXA+CiAgICAgICAgICA8b2N0YXZlPjQ8L29jdGF2ZT4KICAgICAgICA8L3BpdGNoPgogICAgICAgIDxkdXJhdGlvbj4xPC9kdXJhdGlvbj4KICAgICAgICA8dHlwZT5xdWFydGVyPC90eXBlPgogICAgICA8L25vdGU+CiAgICAgIDxub3RlPgogICAgICAgIDxwaXRjaD4KICAgICAgICAgIDxzdGVwPkQ8L3N0ZXA+CiAgICAgICAgICA8b2N0YXZlPjQ8L29jdGF2ZT4KICAgICAgICA8L3BpdGNoPgogICAgICAgIDxkdXJhdGlvbj4xPC9kdXJhdGlvbj4KICAgICAgICA8dHlwZT5xdWFydGVyPC90eXBlPgogICAgICA8L25vdGU+CiAgICAgIDxub3RlPgogICAgICAgIDxwaXRjaD4KICAgICAgICAgIDxzdGVwPkU8L3N0ZXA+CiAgICAgICAgICA8b2N0YXZlPjQ8L29jdGF2ZT4KICAgICAgICA8L3BpdGNoPgogICAgICAgIDxkdXJhdGlvbj4xPC9kdXJhdGlvbj4KICAgICAgICA8dHlwZT5xdWFydGVyPC90eXBlPgogICAgICA8L25vdGU+CiAgICAgIDxub3RlPgogICAgICAgIDxwaXRjaD4KICAgICAgICAgIDxzdGVwPkY8L3N0ZXA+CiAgICAgICAgICA8b2N0YXZlPjQ8L29jdGF2ZT4KICAgICAgICA8L3BpdGNoPgogICAgICAgIDxkdXJhdGlvbj4xPC9kdXJhdGlvbj4KICAgICAgICA8dHlwZT5xdWFydGVyPC90eXBlPgogICAgICA8L25vdGU+CiAgICA8L21lYXN1cmU+CiAgPC9wYXJ0Pgo8L3Njb3JlLXBhcnR3aXNlPg==';
      case 'midi':
        return 'TVRoZAAAAAYAAQABAeBNVHJrAAAAGQD/UQMHoSAA/1gEBAIYCAD/AAAA/y8ATVRyawAAABkA/1EDCKEgAP9YBAQCGAgA/wAAAP8vAA==';
      case 'svg':
        return 'PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI1MDAiIGhlaWdodD0iMjAwIj48ZyB0cmFuc2Zvcm09InRyYW5zbGF0ZSgxMCwgMzApIj48cGF0aCBkPSJNIDAgMCBMIDQ4MCAwIiBzdHJva2U9ImJsYWNrIiBzdHJva2Utd2lkdGg9IjEiLz48cGF0aCBkPSJNIDAgMTAgTCA0ODAgMTAiIHN0cm9rZT0iYmxhY2siIHN0cm9rZS13aWR0aD0iMSIvPjxwYXRoIGQ9Ik0gMCAyMCBMIDQ4MCAyMCIgc3Ryb2tlPSJibGFjayIgc3Ryb2tlLXdpZHRoPSIxIi8+PHBhdGggZD0iTSAwIDMwIEwgNDgwIDMwIiBzdHJva2U9ImJsYWNrIiBzdHJva2Utd2lkdGg9IjEiLz48cGF0aCBkPSJNIDAgNDAgTCA0ODAgNDAiIHN0cm9rZT0iYmxhY2siIHN0cm9rZS13aWR0aD0iMSIvPjx0ZXh0IHg9IjEwIiB5PSIwIiBmb250LWZhbWlseT0ic2VyaWYiIGZvbnQtc2l6ZT0iMjQiIGZpbGw9ImJsYWNrIj4mIzk4Mzg7PC90ZXh0Pjx0ZXh0IHg9IjQwIiB5PSIwIiBmb250LWZhbWlseT0ic2VyaWYiIGZvbnQtc2l6ZT0iMjQiIGZpbGw9ImJsYWNrIj4mIzExOTE7PC90ZXh0Pjx0ZXh0IHg9IjEwMCIgeT0iMTAiIGZvbnQtZmFtaWx5PSJzZXJpZiIgZm9udC1zaXplPSIyNCIgZmlsbD0iYmxhY2siPiYjOTgzODs8L3RleHQ+PHRleHQgeD0iMTQwIiB5PSIxMCIgZm9udC1mYW1pbHk9InNlcmlmIiBmb250LXNpemU9IjI0IiBmaWxsPSJibGFjayI+JiMxMTkxOzwvdGV4dD48dGV4dCB4PSIyMDAiIHk9IjIwIiBmb250LWZhbWlseT0ic2VyaWYiIGZvbnQtc2l6ZT0iMjQiIGZpbGw9ImJsYWNrIj4mIzk4Mzg7PC90ZXh0Pjx0ZXh0IHg9IjI0MCIgeT0iMjAiIGZvbnQtZmFtaWx5PSJzZXJpZiIgZm9udC1zaXplPSIyNCIgZmlsbD0iYmxhY2siPiYjMTE5MTs8L3RleHQ+PHRleHQgeD0iMzAwIiB5PSIzMCIgZm9udC1mYW1pbHk9InNlcmlmIiBmb250LXNpemU9IjI0IiBmaWxsPSJibGFjayI+JiM5ODM4OzwvdGV4dD48dGV4dCB4PSIzNDAiIHk9IjMwIiBmb250LWZhbWlseT0ic2VyaWYiIGZvbnQtc2l6ZT0iMjQiIGZpbGw9ImJsYWNrIj4mIzExOTE7PC90ZXh0Pjwvc3ZnPg==';
      case 'mscz':
        return 'UEsDBBQAAAgIAAAIIeyxjJBkCwAAABkAAAAIAAAATUVUQS1JTkZVWFANCnBLAQIUAxQAAAgIAAAIIeyxjJBkCwAAABkAAAAIAAAAAAAAAAEAIAAAAAAAAABNRVRBLUlORlBLBQYAAAAAAQABADYAAAAxAAAAAA==';
      default:
        return '';
    }
  }
}

// 導出服務實例
export const scoreApiService = new ScoreApiService(); 