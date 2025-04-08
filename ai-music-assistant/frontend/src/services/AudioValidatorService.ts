import { Logger } from '../utils/Logger';

export interface AudioValidationResult {
  isValid: boolean;
  errorMessage?: string;
  audioData?: ArrayBuffer;
  mimeType?: string;
}

export class AudioValidatorService {
  private static readonly SUPPORTED_MIME_TYPES = [
    'audio/wav',
    'audio/x-wav',
    'audio/wave',
    'audio/x-pn-wav',
    'audio/mp3',
    'audio/mpeg',
    'audio/mp4',
    'audio/x-m4a',
    'audio/aac',
    'audio/ogg',
    'audio/webm'
  ];

  private static readonly MIME_TYPE_MAP: Record<string, string> = {
    'mp3': 'audio/mpeg',
    'mpeg': 'audio/mpeg',
    'wav': 'audio/wav',
    'wave': 'audio/wave',
    'm4a': 'audio/x-m4a',
    'aac': 'audio/aac',
    'ogg': 'audio/ogg',
    'webm': 'audio/webm'
  };

  /**
   * 根據文件擴展名獲取MIME類型
   * @param filename 文件名
   * @returns MIME類型
   */
  private static getMimeTypeFromFilename(filename: string): string {
    const extension = filename.split('.').pop()?.toLowerCase() || '';
    return this.MIME_TYPE_MAP[extension] || 'audio/wav';
  }

  /**
   * 將Base64字符串轉換為ArrayBuffer
   * @param base64String Base64字符串
   * @returns ArrayBuffer
   */
  private static base64ToArrayBuffer(base64String: string): ArrayBuffer {
    try {
      const binaryString = atob(base64String);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      return bytes.buffer;
    } catch (error) {
      throw new Error('Base64解碼失敗：數據格式無效或已損壞');
    }
  }

  /**
   * 驗證音頻文件格式
   * @param file 音頻文件
   * @returns 驗證結果
   */
  static async validateAudioFile(file: File): Promise<AudioValidationResult> {
    try {
      // 獲取正確的MIME類型
      const mimeType = this.getMimeTypeFromFilename(file.name);
      
      // 檢查MIME類型
      if (!this.SUPPORTED_MIME_TYPES.includes(mimeType.toLowerCase())) {
        return {
          isValid: false,
          errorMessage: `不支持的音頻格式：${mimeType}，支持的格式：${this.SUPPORTED_MIME_TYPES.join(', ')}`
        };
      }

      // 檢查文件類型
      if (!file.type.includes('audio')) {
        return {
          isValid: false,
          errorMessage: '請上傳音頻文件 (MP3, WAV, MIDI 等)'
        };
      }

      // 讀取文件為ArrayBuffer
      let audioData: ArrayBuffer;
      try {
        audioData = await file.arrayBuffer();
      } catch (error) {
        throw new Error('讀取音頻文件失敗：文件可能已損壞或格式不正確');
      }
      
      // 檢查WAV文件頭（僅對WAV格式進行詳細檢查）
      if (mimeType.includes('wav')) {
        try {
          const header = new Uint8Array(audioData.slice(0, 12));
          const headerStr = String.fromCharCode.apply(null, Array.from(header));
          
          if (!headerStr.includes('RIFF') || !headerStr.includes('WAVE')) {
            return {
              isValid: false,
              errorMessage: '無效的WAV文件格式：缺少RIFF或WAVE標識'
            };
          }

          // 解析fmt塊
          const fmtStart = new Uint8Array(audioData).findIndex((_, i, arr) => 
            arr[i] === 'f'.charCodeAt(0) &&
            arr[i+1] === 'm'.charCodeAt(0) &&
            arr[i+2] === 't'.charCodeAt(0) &&
            arr[i+3] === ' '.charCodeAt(0)
          );

          if (fmtStart === -1) {
            return {
              isValid: false,
              errorMessage: '無效的WAV文件：缺少fmt塊'
            };
          }

          // 解析音頻參數
          const fmtData = new DataView(audioData.slice(fmtStart + 8, fmtStart + 24));
          const audioFormat = fmtData.getUint16(0, true);
          const channels = fmtData.getUint16(2, true);
          const sampleRate = fmtData.getUint32(4, true);
          const bitsPerSample = fmtData.getUint16(14, true);

          // 驗證採樣率
          if (sampleRate !== 44100) {
            return {
              isValid: false,
              errorMessage: `不支持的採樣率：${sampleRate}Hz，需要44100Hz`
            };
          }

          // 驗證位深度
          if (bitsPerSample !== 16) {
            return {
              isValid: false,
              errorMessage: `不支持的位深度：${bitsPerSample}位，需要16位`
            };
          }

          // 驗證聲道數
          if (channels !== 1 && channels !== 2) {
            return {
              isValid: false,
              errorMessage: `不支持的聲道數：${channels}，需要1或2聲道`
            };
          }
        } catch (error) {
          throw new Error('WAV文件解析失敗：文件結構可能已損壞');
        }
      }

      Logger.info('音頻格式驗證通過', { 
        mimeType,
        fileName: file.name
      });

      return {
        isValid: true,
        audioData,
        mimeType
      };

    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : '未知錯誤';
      Logger.error('音頻格式驗證失敗', error);
      return {
        isValid: false,
        errorMessage: `音頻格式驗證失敗: ${errorMessage}`
      };
    }
  }

  /**
   * 驗證Base64編碼的音頻數據
   * @param audioDataUrl Base64編碼的音頻數據URL
   * @returns 驗證結果
   */
  static async validateBase64Audio(audioDataUrl: string): Promise<AudioValidationResult> {
    try {
      // 從data URL中提取實際數據
      let audioData: string;
      let mimeType = 'audio/wav';
      
      if (audioDataUrl.startsWith('data:audio/')) {
        try {
          const [header, encoded] = audioDataUrl.split(',');
          if (!encoded) {
            throw new Error('Base64數據缺失');
          }
          const format = header.split(';')[0].split('/')[1];
          mimeType = `audio/${format}`;
          
          if (!this.SUPPORTED_MIME_TYPES.includes(mimeType.toLowerCase())) {
            return {
              isValid: false,
              errorMessage: `不支持的音頻格式：${mimeType}，支持的格式：${this.SUPPORTED_MIME_TYPES.join(', ')}`
            };
          }
          
          audioData = encoded;
        } catch (error) {
          throw new Error('解析Data URL失敗：格式無效');
        }
      } else {
        audioData = audioDataUrl;
      }

      // 將Base64轉換為ArrayBuffer
      let arrayBuffer: ArrayBuffer;
      try {
        arrayBuffer = this.base64ToArrayBuffer(audioData);
      } catch (error) {
        throw new Error('Base64解碼失敗：數據格式無效或已損壞');
      }

      // 使用validateAudioFile方法驗證
      const result = await this.validateAudioFile(new File([arrayBuffer], 'audio.wav', { type: mimeType }));
      return {
        ...result,
        mimeType
      };

    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : '未知錯誤';
      Logger.error('Base64音頻數據驗證失敗', error);
      return {
        isValid: false,
        errorMessage: `Base64音頻數據驗證失敗: ${errorMessage}`
      };
    }
  }
} 