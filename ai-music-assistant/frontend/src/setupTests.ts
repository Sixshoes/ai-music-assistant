import '@testing-library/jest-dom';
import { expect, afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import matchers from '@testing-library/jest-dom/matchers';
import { TextEncoder, TextDecoder } from 'util';

// 擴展 expect 的類型定義
expect.extend(matchers);

// 在每個測試後清理
afterEach(() => {
  cleanup();
});

// 添加必要的全局變量
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder as any;

// 模擬 ResizeObserver
class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}

window.ResizeObserver = ResizeObserver;

// 模擬 matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
}); 