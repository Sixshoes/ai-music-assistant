import * as Tone from 'tone';
import Logger from './LoggingService';

// 音色類型
export interface SoundFont {
  id: string;
  name: string;
  category: string;
  description: string;
  type: 'dexed' | 'octasine' | 'fluidsynth';
}

// 音色參數
export interface SoundParameters {
  // 通用參數
  attack: number;
  decay: number;
  sustain: number;
  release: number;
  volume: number;
  
  // FM合成參數
  algorithm?: number;
  feedback?: number;
  modulationIndex?: number;
  operators?: Array<{
    frequency: number;
    detune: number;
    volume: number;
    waveform: string;
  }>;
  
  // 其他特定參數
  [key: string]: any;
}

// 預設音色
export interface SoundPreset {
  id: string;
  name: string;
  fontId: string;
  parameters: SoundParameters;
  isFavorite: boolean;
  createdAt: Date;
  updatedAt?: Date;
  tags?: string[];
}

// 渲染選項
export interface RenderOptions {
  format: 'wav' | 'mp3' | 'ogg'; // 輸出格式
  sampleRate: number;           // 採樣率
  bitDepth: 16 | 24 | 32;       // 位元深度
  normalizeAudio: boolean;      // 是否標準化音量
  effects: Array<{              // 音訊效果
    type: string;
    settings: Record<string, any>;
  }>;
}

class SynthesizerService {
  // 獲取所有可用的音色庫
  async getSoundFonts(): Promise<SoundFont[]> {
    try {
      Logger.info('獲取音色庫列表', null, { tags: ['SYNTHESIZER'] });
      
      // 調用API獲取音色庫列表
      // const response = await axios.get('/api/soundfonts');
      // return response.data;
      
      // 開發模式下使用模擬數據
      return [
        {
          id: 'dexed1',
          name: 'DX7 Classic',
          category: 'FM合成',
          description: 'Dexed 經典 DX7 音色模擬',
          type: 'dexed'
        },
        {
          id: 'octasine1',
          name: 'OctaSine Basic',
          category: 'FM合成',
          description: 'OctaSine 基本 FM 音色',
          type: 'octasine'
        },
        {
          id: 'fluidsynth1',
          name: 'General MIDI',
          category: '采樣',
          description: 'FluidSynth 標準 GM 音色',
          type: 'fluidsynth'
        }
      ];
    } catch (error) {
      Logger.error('獲取音色庫失敗', error, { tags: ['SYNTHESIZER'] });
      throw error;
    }
  }
  
  // 獲取所有預設音色
  async getPresets(): Promise<SoundPreset[]> {
    try {
      Logger.info('獲取預設音色列表', null, { tags: ['SYNTHESIZER'] });
      
      // 調用API獲取預設列表
      // const response = await axios.get('/api/soundpresets');
      // return response.data;
      
      // 開發模式下使用模擬數據
      return [
        {
          id: 'preset1',
          name: '明亮鋼琴',
          fontId: 'fluidsynth1',
          parameters: {
            attack: 0.01,
            decay: 0.1,
            sustain: 0.8,
            release: 0.5,
            volume: 0.7
          },
          isFavorite: true,
          createdAt: new Date(),
          tags: ['鋼琴', '明亮']
        },
        {
          id: 'preset2',
          name: '復古合成器',
          fontId: 'dexed1',
          parameters: {
            attack: 0.05,
            decay: 0.2,
            sustain: 0.6,
            release: 0.3,
            volume: 0.75,
            algorithm: 3,
            feedback: 0.4,
            modulationIndex: 0.6,
            operators: [
              {
                frequency: 1,
                detune: 0,
                volume: 1,
                waveform: 'sine'
              },
              {
                frequency: 2,
                detune: 5,
                volume: 0.5,
                waveform: 'sine'
              }
            ]
          },
          isFavorite: false,
          createdAt: new Date(),
          tags: ['合成器', '復古']
        }
      ];
    } catch (error) {
      Logger.error('獲取預設音色失敗', error, { tags: ['SYNTHESIZER'] });
      throw error;
    }
  }
  
  // 保存自定義預設
  async savePreset(preset: Partial<SoundPreset>): Promise<SoundPreset> {
    try {
      Logger.info('保存自定義預設', { presetName: preset.name }, { tags: ['SYNTHESIZER'] });
      
      // 調用API保存預設
      // const response = await axios.post('/api/soundpresets', preset);
      // return response.data;
      
      // 開發模式下模擬保存
      const newPreset: SoundPreset = {
        id: `preset-${Date.now()}`,
        name: preset.name || '未命名預設',
        fontId: preset.fontId || '',
        parameters: preset.parameters || {
          attack: 0.1,
          decay: 0.2,
          sustain: 0.5,
          release: 0.5,
          volume: 0.7
        },
        isFavorite: preset.isFavorite || false,
        createdAt: new Date(),
        updatedAt: new Date(),
        tags: preset.tags || []
      };
      
      return newPreset;
    } catch (error) {
      Logger.error('保存自定義預設失敗', error, { tags: ['SYNTHESIZER'] });
      throw error;
    }
  }
  
  // 創建合成器實例
  createSynth(preset: SoundPreset): Tone.Synth {
    try {
      Logger.info('創建合成器實例', { presetName: preset.name }, { tags: ['SYNTHESIZER'] });
      
      let synth: Tone.Synth;
      
      // 基於預設類型創建不同的合成器
      if (preset.fontId.includes('dexed')) {
        // FM合成器
        synth = new Tone.FMSynth({
          harmonicity: preset.parameters.modulationIndex || 1,
          modulationIndex: preset.parameters.feedback || 0.5,
          oscillator: {
            type: 'sine'
          },
          envelope: {
            attack: preset.parameters.attack,
            decay: preset.parameters.decay,
            sustain: preset.parameters.sustain,
            release: preset.parameters.release
          },
          modulation: {
            type: 'square'
          },
          modulationEnvelope: {
            attack: 0.01,
            decay: 0.5,
            sustain: 0.2,
            release: 0.1
          }
        });
      } else {
        // 默認PolySynth
        synth = new Tone.PolySynth(Tone.Synth, {
          oscillator: {
            type: 'sine'
          },
          envelope: {
            attack: preset.parameters.attack,
            decay: preset.parameters.decay,
            sustain: preset.parameters.sustain,
            release: preset.parameters.release
          }
        });
      }
      
      // 設置音量
      const volume = new Tone.Volume(Tone.gainToDb(preset.parameters.volume || 0.7));
      synth.chain(volume, Tone.Destination);
      
      return synth;
    } catch (error) {
      Logger.error('創建合成器失敗', error, { tags: ['SYNTHESIZER'] });
      throw error;
    }
  }
  
  // 播放音符預覽
  async playNotePreview(preset: SoundPreset, note: string = 'C4', duration: number = 1): Promise<void> {
    try {
      Logger.info('播放音符預覽', { preset: preset.name, note }, { tags: ['SYNTHESIZER'] });
      
      // 確保音頻上下文已啟動
      await Tone.start();
      
      // 創建合成器
      const synth = this.createSynth(preset);
      
      // 播放音符
      const now = Tone.now();
      synth.triggerAttack(note, now);
      synth.triggerRelease(now + duration);
      
      // 在指定時間後處理合成器
      return new Promise(resolve => {
        setTimeout(() => {
          synth.dispose();
          resolve();
        }, duration * 1000 + 100);
      });
    } catch (error) {
      Logger.error('播放音符預覽失敗', error, { tags: ['SYNTHESIZER'] });
      throw error;
    }
  }
  
  // 渲染MIDI文件為音頻
  async renderMidiToAudio(midiFile: File, preset: SoundPreset, options: Partial<RenderOptions> = {}): Promise<Blob> {
    try {
      Logger.info('渲染MIDI為音頻', { fileName: midiFile.name, preset: preset.name }, { tags: ['SYNTHESIZER'] });
      
      // 在實際應用中，我們會將文件和設置發送到後端進行處理
      const formData = new FormData();
      formData.append('midi', midiFile);
      formData.append('preset', JSON.stringify(preset));
      formData.append('options', JSON.stringify(options));
      
      // 調用渲染API
      // const response = await axios.post('/api/render', formData, {
      //   responseType: 'blob'
      // });
      // return response.data;
      
      // 開發模式下模擬渲染過程
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // 創建一個示例音頻文件
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      const sampleRate = options.sampleRate || 44100;
      const duration = 5; // 假設5秒
      const numSamples = duration * sampleRate;
      const buffer = audioContext.createBuffer(2, numSamples, sampleRate);
      
      // 生成簡單的正弦波
      for (let channel = 0; channel < 2; channel++) {
        const output = buffer.getChannelData(channel);
        for (let i = 0; i < numSamples; i++) {
          output[i] = Math.sin(i * 440 * Math.PI * 2 / sampleRate) * 0.5;
        }
      }
      
      // 將 AudioBuffer 轉換為 WAV
      const offlineContext = new OfflineAudioContext(2, numSamples, sampleRate);
      const bufferSource = offlineContext.createBufferSource();
      bufferSource.buffer = buffer;
      bufferSource.connect(offlineContext.destination);
      bufferSource.start();
      
      const renderedBuffer = await offlineContext.startRendering();
      
      // 轉換為 Blob
      const wavBlob = await this._audioBufferToWav(renderedBuffer);
      return wavBlob;
    } catch (error) {
      Logger.error('渲染MIDI為音頻失敗', error, { tags: ['SYNTHESIZER'] });
      throw error;
    }
  }
  
  // 將 AudioBuffer 轉換為 WAV Blob
  private _audioBufferToWav(buffer: AudioBuffer): Promise<Blob> {
    return new Promise((resolve) => {
      const numChannels = buffer.numberOfChannels;
      const sampleRate = buffer.sampleRate;
      const format = 1; // PCM
      const bitDepth = 16;
      
      const bytesPerSample = bitDepth / 8;
      const blockAlign = numChannels * bytesPerSample;
      
      const dataSize = buffer.length * blockAlign;
      const headerSize = 44;
      const fileSize = headerSize + dataSize;
      
      const arrayBuffer = new ArrayBuffer(fileSize);
      const view = new DataView(arrayBuffer);
      
      // RIFF 識別
      this._writeString(view, 0, 'RIFF');
      view.setUint32(4, fileSize - 8, true);
      this._writeString(view, 8, 'WAVE');
      
      // fmt 塊
      this._writeString(view, 12, 'fmt ');
      view.setUint32(16, 16, true); // fmt 塊大小
      view.setUint16(20, format, true);
      view.setUint16(22, numChannels, true);
      view.setUint32(24, sampleRate, true);
      view.setUint32(28, sampleRate * blockAlign, true);
      view.setUint16(32, blockAlign, true);
      view.setUint16(34, bitDepth, true);
      
      // data 塊
      this._writeString(view, 36, 'data');
      view.setUint32(40, dataSize, true);
      
      // 寫入音頻數據
      let offset = 44;
      for (let i = 0; i < buffer.length; i++) {
        for (let channel = 0; channel < numChannels; channel++) {
          const sample = buffer.getChannelData(channel)[i];
          // 轉換為整數 (-32768 到 32767)
          const value = Math.max(-1, Math.min(1, sample));
          const int = value < 0 ? value * 0x8000 : value * 0x7FFF;
          view.setInt16(offset, int, true);
          offset += 2;
        }
      }
      
      const wavBlob = new Blob([arrayBuffer], { type: 'audio/wav' });
      resolve(wavBlob);
    });
  }
  
  // 將字符串寫入 DataView
  private _writeString(view: DataView, offset: number, string: string): void {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  }
}

export const synthesizerService = new SynthesizerService();
export default synthesizerService; 