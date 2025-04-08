/**
 * Jest 測試設置文件
 */

// 引入 Jest DOM 擴展
import '@testing-library/jest-dom';

// 模擬 window.matchMedia (許多組件依賴此功能)
window.matchMedia = window.matchMedia || function() {
  return {
    matches: false,
    addListener: jest.fn(),
    removeListener: jest.fn(),
  };
};

// 模擬 localStorage
const localStorageMock = (function() {
  let store = {};
  return {
    getItem: jest.fn(key => store[key] || null),
    setItem: jest.fn((key, value) => {
      store[key] = value.toString();
    }),
    removeItem: jest.fn(key => {
      delete store[key];
    }),
    clear: jest.fn(() => {
      store = {};
    }),
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// 模擬 Tone.js (音頻處理庫)
jest.mock('tone', () => ({
  start: jest.fn(),
  Transport: {
    start: jest.fn(),
    stop: jest.fn(),
    bpm: {
      value: 120,
    },
  },
  Player: jest.fn().mockImplementation(() => ({
    toDestination: jest.fn().mockReturnThis(),
    autostart: false,
    loop: false,
    start: jest.fn(),
    stop: jest.fn(),
  })),
}));

// 靜音控制台錯誤 (可選，取決於你的測試需求)
// console.error = jest.fn();
// console.warn = jest.fn();

// 清理測試後的模擬
afterEach(() => {
  jest.clearAllMocks();
}); 