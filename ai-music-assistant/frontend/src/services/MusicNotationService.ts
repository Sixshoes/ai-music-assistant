import { Factory } from 'vexflow';
import * as Tone from 'tone';
import axios from 'axios';
import { Logger } from './LoggingService';
import { scoreApiService } from './ScoreApiService';

interface ScoreOptions {
  width?: number;
  height?: number;
  scale?: number;
}

interface ExportOptions {
  format: 'musicxml' | 'pdf' | 'midi' | 'svg';
  filename?: string;
}

interface NotationNote {
  key: string;
  duration: string;
  accidental?: string;
  dots?: number;
}

interface ScoreData {
  notes: NotationNote[];
  timeSignature?: string;
  keySignature?: string;
  clef?: 'treble' | 'bass' | 'alto' | 'tenor' | 'percussion';
  tempo?: number;
}

class MusicNotationService {
  private vexflowFactory: any = null;
  private renderer: any = null;
  private context: any = null;
  private musescoreEnabled: boolean = false;
  private activeMidiNotes: number[] = [];
  private synth: Tone.PolySynth | null = null;

  constructor() {
    this.initSynth();
    this.checkMuseScoreAvailability();
  }

  /**
   * 初始化 Tone.js 合成器以播放音符
   */
  private initSynth(): void {
    try {
      this.synth = new Tone.PolySynth(Tone.Synth).toDestination();
      Logger.info('已初始化音符播放合成器', {}, { tags: ['NOTATION'] });
    } catch (error) {
      Logger.error('初始化音符播放合成器失敗', error, { tags: ['NOTATION'] });
    }
  }

  /**
   * 檢查 MuseScore 整合是否可用
   */
  private async checkMuseScoreAvailability(): Promise<void> {
    try {
      this.musescoreEnabled = await scoreApiService.checkMuseScoreStatus();
      Logger.info('MuseScore 狀態檢查', { available: this.musescoreEnabled }, { tags: ['NOTATION'] });
    } catch (error) {
      this.musescoreEnabled = false;
      Logger.error('檢查 MuseScore 可用性失敗', error, { tags: ['NOTATION'] });
    }
  }

  /**
   * 檢查 MuseScore 是否可用
   */
  public isMuseScoreEnabled(): boolean {
    return this.musescoreEnabled;
  }

  /**
   * 初始化 VexFlow 渲染器
   */
  public initRenderer(container: HTMLElement, options?: ScoreOptions): void {
    try {
      const factory = new Factory({
        renderer: {
          elementId: container.id,
          width: options?.width || container.clientWidth,
          height: options?.height || 300,
        }
      });

      this.vexflowFactory = factory;
      this.renderer = factory.getRenderer();
      this.context = this.renderer.getContext();
      
      if (options?.scale) {
        this.context.scale(options.scale, options.scale);
      }
      
      Logger.info('初始化 VexFlow 渲染器', { containerId: container.id }, { tags: ['NOTATION'] });
    } catch (error) {
      Logger.error('初始化 VexFlow 渲染器失敗', error, { tags: ['NOTATION'] });
      throw new Error('初始化樂譜渲染器失敗');
    }
  }

  /**
   * 渲染樂譜
   */
  public renderScore(scoreData: ScoreData): void {
    if (!this.vexflowFactory) {
      throw new Error('樂譜渲染器尚未初始化');
    }

    try {
      // 清除先前的渲染
      this.context.clear();
      
      // 創建樂譜系統
      const system = this.vexflowFactory.System({
        width: this.renderer.width * 0.9,
        spaceBetweenStaves: 10
      });
      
      // 添加樂譜
      const score = system.addStave({
        voices: [
          this.vexflowFactory.Voice().addTickables(
            scoreData.notes.map(note => 
              this.vexflowFactory.StaveNote({
                keys: [note.key],
                duration: note.duration
              })
            )
          )
        ]
      });
      
      // 添加時間和調性標記
      if (scoreData.timeSignature) {
        score.addTimeSignature(scoreData.timeSignature);
      }
      
      if (scoreData.keySignature) {
        score.addKeySignature(scoreData.keySignature);
      }
      
      if (scoreData.clef) {
        score.addClef(scoreData.clef);
      }
      
      // 渲染樂譜
      this.vexflowFactory.draw();
      Logger.info('渲染樂譜', { notes: scoreData.notes.length }, { tags: ['NOTATION'] });
    } catch (error) {
      Logger.error('渲染樂譜失敗', error, { tags: ['NOTATION'] });
      throw new Error('渲染樂譜失敗');
    }
  }

  /**
   * 解析 MusicXML 字符串
   */
  public parseMusicXML(xmlString: string): ScoreData {
    try {
      Logger.info('解析 MusicXML', { size: xmlString.length }, { tags: ['NOTATION'] });
      
      // 簡單的解析邏輯，實際實現中需要更複雜的解析
      const parser = new DOMParser();
      const xmlDoc = parser.parseFromString(xmlString, 'text/xml');
      
      // 提取基本信息
      const notes: NotationNote[] = [];
      const notesElements = xmlDoc.getElementsByTagName('note');
      
      for (let i = 0; i < notesElements.length; i++) {
        const noteEl = notesElements[i];
        const pitchEl = noteEl.getElementsByTagName('pitch')[0];
        
        if (pitchEl) {
          const step = pitchEl.getElementsByTagName('step')[0]?.textContent || 'C';
          const octave = pitchEl.getElementsByTagName('octave')[0]?.textContent || '4';
          const duration = noteEl.getElementsByTagName('type')[0]?.textContent || 'quarter';
          
          notes.push({
            key: `${step}/${octave}`,
            duration: this.mapMusicXmlDurationToVexFlow(duration),
          });
        }
      }
      
      // 提取其他信息
      const timeSignature = this.extractTimeSignature(xmlDoc);
      const keySignature = this.extractKeySignature(xmlDoc);
      const clef = this.extractClef(xmlDoc);
      const tempo = this.extractTempo(xmlDoc);
      
      return {
        notes,
        timeSignature,
        keySignature,
        clef: clef as any,
        tempo
      };
    } catch (error) {
      Logger.error('解析 MusicXML 失敗', error, { tags: ['NOTATION'] });
      throw new Error('解析 MusicXML 失敗');
    }
  }

  /**
   * 播放音符
   */
  public playNote(midiNote: number): void {
    if (!this.synth) return;
    
    try {
      const noteName = this.midiNoteToName(midiNote);
      this.synth.triggerAttack(noteName);
      this.activeMidiNotes.push(midiNote);
      
      Logger.debug('播放音符', { note: noteName, midi: midiNote }, { tags: ['NOTATION'] });
    } catch (error) {
      Logger.error('播放音符失敗', error, { tags: ['NOTATION'] });
    }
  }

  /**
   * 停止播放音符
   */
  public stopNote(midiNote: number): void {
    if (!this.synth) return;
    
    try {
      const noteName = this.midiNoteToName(midiNote);
      this.synth.triggerRelease(noteName);
      this.activeMidiNotes = this.activeMidiNotes.filter(n => n !== midiNote);
      
      Logger.debug('停止播放音符', { note: noteName, midi: midiNote }, { tags: ['NOTATION'] });
    } catch (error) {
      Logger.error('停止播放音符失敗', error, { tags: ['NOTATION'] });
    }
  }

  /**
   * 停止所有播放中的音符
   */
  public stopAllNotes(): void {
    if (!this.synth) return;
    
    try {
      this.synth.releaseAll();
      this.activeMidiNotes = [];
      Logger.debug('停止所有音符', {}, { tags: ['NOTATION'] });
    } catch (error) {
      Logger.error('停止所有音符失敗', error, { tags: ['NOTATION'] });
    }
  }

  /**
   * 匯出樂譜
   */
  public async exportScore(scoreData: any, options: ExportOptions): Promise<string> {
    try {
      Logger.info('匯出樂譜', { format: options.format }, { tags: ['NOTATION'] });
      
      // 使用 ScoreApiService 來處理匯出邏輯
      const exportedData = await scoreApiService.exportScore({
        format: options.format,
        scoreData: scoreData,
        filename: options.filename
      });
      
      const mimeTypes: Record<string, string> = {
        'musicxml': 'application/vnd.recordare.musicxml+xml',
        'pdf': 'application/pdf',
        'midi': 'audio/midi',
        'svg': 'image/svg+xml'
      };
      
      // 創建並觸發下載
      const filename = options.filename || `score.${options.format}`;
      const blob = this.base64ToBlob(exportedData, mimeTypes[options.format]);
      const url = URL.createObjectURL(blob);
      
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      return url;
    } catch (error) {
      Logger.error('匯出樂譜失敗', error, { tags: ['NOTATION'] });
      throw new Error(`匯出樂譜失敗：${error instanceof Error ? error.message : '未知錯誤'}`);
    }
  }

  /**
   * 將 Base64 轉換為 Blob
   */
  private base64ToBlob(base64: string, mimeType: string): Blob {
    const byteCharacters = atob(base64);
    const byteArrays = [];
    
    for (let offset = 0; offset < byteCharacters.length; offset += 1024) {
      const slice = byteCharacters.slice(offset, offset + 1024);
      const byteNumbers = new Array(slice.length);
      
      for (let i = 0; i < slice.length; i++) {
        byteNumbers[i] = slice.charCodeAt(i);
      }
      
      byteArrays.push(new Uint8Array(byteNumbers));
    }
    
    return new Blob(byteArrays, { type: mimeType });
  }

  /**
   * 將 MIDI 音符轉換為音符名稱
   */
  private midiNoteToName(midiNote: number): string {
    const noteNames = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
    const octave = Math.floor(midiNote / 12) - 1;
    const noteName = noteNames[midiNote % 12];
    return `${noteName}${octave}`;
  }

  /**
   * 從 MusicXML 提取拍號
   */
  private extractTimeSignature(xmlDoc: Document): string | undefined {
    try {
      const beats = xmlDoc.getElementsByTagName('beats')[0]?.textContent;
      const beatType = xmlDoc.getElementsByTagName('beat-type')[0]?.textContent;
      return beats && beatType ? `${beats}/${beatType}` : undefined;
    } catch (error) {
      return undefined;
    }
  }

  /**
   * 從 MusicXML 提取調號
   */
  private extractKeySignature(xmlDoc: Document): string | undefined {
    try {
      const fifths = xmlDoc.getElementsByTagName('fifths')[0]?.textContent;
      if (!fifths) return undefined;
      
      const fifthsNum = parseInt(fifths, 10);
      if (isNaN(fifthsNum)) return undefined;
      
      // 根據五度圈位置獲取調性
      const keyMap: Record<number, string> = {
        0: 'C',
        1: 'G',
        2: 'D',
        3: 'A',
        4: 'E',
        5: 'B',
        6: 'F#',
        7: 'C#',
        -1: 'F',
        -2: 'Bb',
        -3: 'Eb',
        -4: 'Ab',
        -5: 'Db',
        -6: 'Gb',
        -7: 'Cb'
      };
      
      return keyMap[fifthsNum];
    } catch (error) {
      return undefined;
    }
  }

  /**
   * 從 MusicXML 提取譜號
   */
  private extractClef(xmlDoc: Document): string | undefined {
    try {
      const sign = xmlDoc.getElementsByTagName('sign')[0]?.textContent;
      if (!sign) return undefined;
      
      const clefMap: Record<string, string> = {
        'G': 'treble',
        'F': 'bass',
        'C': 'alto',
      };
      
      return clefMap[sign] || 'treble';
    } catch (error) {
      return undefined;
    }
  }

  /**
   * 從 MusicXML 提取速度
   */
  private extractTempo(xmlDoc: Document): number | undefined {
    try {
      const tempo = xmlDoc.getElementsByTagName('sound')[0]?.getAttribute('tempo');
      return tempo ? parseInt(tempo, 10) : undefined;
    } catch (error) {
      return undefined;
    }
  }

  /**
   * 將 MusicXML 音符類型轉換為 VexFlow 音符類型
   */
  private mapMusicXmlDurationToVexFlow(xmlDuration: string): string {
    const durationMap: Record<string, string> = {
      'whole': 'w',
      'half': 'h',
      'quarter': 'q',
      'eighth': '8',
      'sixteenth': '16',
      'thirty-second': '32',
      'sixty-fourth': '64'
    };
    
    return durationMap[xmlDuration] || 'q';
  }
}

// 導出服務實例
export const musicNotationService = new MusicNotationService(); 