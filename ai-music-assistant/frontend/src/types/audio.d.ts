// 定義 Web Audio API 的類型
interface Window {
  AudioContext: typeof AudioContext;
  webkitAudioContext: typeof AudioContext;
}

// 確保 MediaRecorder 和相關類型被正確識別
interface MediaRecorderOptions {
  mimeType?: string;
  audioBitsPerSecond?: number;
  videoBitsPerSecond?: number;
  bitsPerSecond?: number;
}

interface MediaRecorderErrorEvent extends Event {
  readonly name: string;
}

interface MediaRecorderDataAvailableEvent extends Event {
  readonly data: Blob;
}

interface MediaRecorderEventMap {
  'dataavailable': MediaRecorderDataAvailableEvent;
  'error': MediaRecorderErrorEvent;
  'pause': Event;
  'resume': Event;
  'start': Event;
  'stop': Event;
}

interface MediaRecorder extends EventTarget {
  readonly mimeType: string;
  readonly state: 'inactive' | 'recording' | 'paused';
  readonly stream: MediaStream;
  readonly audioBitsPerSecond: number;
  readonly videoBitsPerSecond: number;

  ondataavailable: ((this: MediaRecorder, ev: MediaRecorderDataAvailableEvent) => any) | null;
  onerror: ((this: MediaRecorder, ev: MediaRecorderErrorEvent) => any) | null;
  onpause: ((this: MediaRecorder, ev: Event) => any) | null;
  onresume: ((this: MediaRecorder, ev: Event) => any) | null;
  onstart: ((this: MediaRecorder, ev: Event) => any) | null;
  onstop: ((this: MediaRecorder, ev: Event) => any) | null;

  start(timeslice?: number): void;
  stop(): void;
  pause(): void;
  resume(): void;
  requestData(): void;

  addEventListener<K extends keyof MediaRecorderEventMap>(
    type: K,
    listener: (this: MediaRecorder, ev: MediaRecorderEventMap[K]) => any,
    options?: boolean | AddEventListenerOptions
  ): void;
  addEventListener(
    type: string,
    listener: EventListenerOrEventListenerObject,
    options?: boolean | AddEventListenerOptions
  ): void;
  removeEventListener<K extends keyof MediaRecorderEventMap>(
    type: K,
    listener: (this: MediaRecorder, ev: MediaRecorderEventMap[K]) => any,
    options?: boolean | EventListenerOptions
  ): void;
  removeEventListener(
    type: string,
    listener: EventListenerOrEventListenerObject,
    options?: boolean | EventListenerOptions
  ): void;
}

interface MediaRecorderConstructor {
  new(stream: MediaStream, options?: MediaRecorderOptions): MediaRecorder;
  isTypeSupported(mimeType: string): boolean;
}

declare var MediaRecorder: MediaRecorderConstructor; 