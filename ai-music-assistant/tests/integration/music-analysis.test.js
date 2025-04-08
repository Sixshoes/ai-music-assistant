/**
 * 音樂分析頁面整合測試
 */

// 使用 Jest 和 React Testing Library
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import axios from 'axios';
import MusicAnalysisPage from '../../frontend/src/pages/MusicAnalysisPage';

// 模擬 axios
jest.mock('axios');

// 模擬 LoggingService
jest.mock('../../frontend/src/services/LoggingService', () => ({
  default: {
    info: jest.fn(),
    debug: jest.fn(),
    warn: jest.fn(),
    error: jest.fn(),
  },
  Logger: {
    info: jest.fn(),
    debug: jest.fn(),
    warn: jest.fn(),
    error: jest.fn(),
  }
}));

describe('MusicAnalysisPage 整合測試', () => {
  beforeEach(() => {
    // 重置所有模擬
    jest.clearAllMocks();
    
    // 模擬 process.env
    process.env.NODE_ENV = 'development';
    
    // 模擬 URL.createObjectURL 和 revokeObjectURL
    global.URL.createObjectURL = jest.fn().mockReturnValue('mock-url');
    global.URL.revokeObjectURL = jest.fn();
    
    // 模擬 document 方法
    document.createElement = jest.fn().mockImplementation((tag) => {
      if (tag === 'a') {
        return {
          href: '',
          download: '',
          click: jest.fn(),
        };
      }
      return {};
    });
    document.body.appendChild = jest.fn();
    document.body.removeChild = jest.fn();
  });
  
  test('應該正確渲染上傳區域', () => {
    render(<MusicAnalysisPage />);
    
    // 檢查標題和上傳按鈕是否存在
    expect(screen.getByText('音樂分析')).toBeInTheDocument();
    expect(screen.getByText('上傳音樂文件')).toBeInTheDocument();
    expect(screen.getByText('選擇文件')).toBeInTheDocument();
  });
  
  test('上傳非音頻文件應該顯示錯誤', () => {
    render(<MusicAnalysisPage />);
    
    // 模擬文件上傳
    const file = new File(['test'], 'test.txt', { type: 'text/plain' });
    const input = screen.getByLabelText('選擇文件');
    
    fireEvent.change(input, { target: { files: [file] } });
    
    // 檢查錯誤訊息
    expect(screen.getByText('請上傳音頻文件 (MP3, WAV, MIDI 等)')).toBeInTheDocument();
  });
  
  test('上傳音頻文件後應該顯示音頻預覽', async () => {
    render(<MusicAnalysisPage />);
    
    // 模擬音頻文件上傳
    const file = new File(['audio-content'], 'test.mp3', { type: 'audio/mpeg' });
    const input = screen.getByLabelText('選擇文件');
    
    fireEvent.change(input, { target: { files: [file] } });
    
    // 檢查文件名是否顯示
    expect(screen.getByText('test.mp3')).toBeInTheDocument();
    
    // 檢查音頻預覽元素是否存在
    const audioElement = screen.getByRole('audio');
    expect(audioElement).toHaveAttribute('src', 'mock-url');
  });
  
  test('點擊分析按鈕應該處理音樂分析', async () => {
    render(<MusicAnalysisPage />);
    
    // 模擬音頻文件上傳
    const file = new File(['audio-content'], 'test.mp3', { type: 'audio/mpeg' });
    const input = screen.getByLabelText('選擇文件');
    
    fireEvent.change(input, { target: { files: [file] } });
    
    // 模擬 FileReader
    global.FileReader = jest.fn().mockImplementation(() => {
      return {
        readAsDataURL: jest.fn(),
        onload: null,
        result: 'data:audio/mpeg;base64,YXVkaW8tY29udGVudA==',
      };
    });
    
    // 模擬API響應
    const mockResponse = {
      data: {
        success: true,
        analysis: {
          key: 'C',
          tempo: 120,
          time_signature: '4/4',
          chord_progression: {
            chords: ['C', 'G', 'Am', 'F'],
            durations: [1, 1, 1, 1]
          },
          structure: {
            verse: [1, 8],
            chorus: [9, 16]
          },
          harmony_issues: ['和弦進行有些單調'],
          suggestions: ['可以嘗試添加七和弦增加豐富度']
        }
      }
    };
    
    axios.post.mockResolvedValue(mockResponse);
    
    // 點擊分析按鈕
    const analyzeButton = screen.getByText('分析音樂');
    fireEvent.click(analyzeButton);
    
    // 等待分析完成
    await waitFor(() => {
      expect(screen.getByText('C')).toBeInTheDocument();
      expect(screen.getByText('120 BPM')).toBeInTheDocument();
      expect(screen.getByText('4/4')).toBeInTheDocument();
      expect(screen.getByText('和弦進行')).toBeInTheDocument();
      expect(screen.getByText('結構分析')).toBeInTheDocument();
      expect(screen.getByText('音樂改進建議')).toBeInTheDocument();
    });
  });
  
  test('點擊匯出按鈕應該創建下載連結', async () => {
    render(<MusicAnalysisPage />);
    
    // 模擬已有分析結果
    const mockResult = {
      success: true,
      analysis: {
        key: 'C',
        tempo: 120,
        time_signature: '4/4',
        chord_progression: {
          chords: ['C', 'G', 'Am', 'F'],
          durations: [1, 1, 1, 1]
        },
        structure: {
          verse: [1, 8],
          chorus: [9, 16]
        },
        harmony_issues: ['和弦進行有些單調'],
        suggestions: ['可以嘗試添加七和弦增加豐富度']
      }
    };
    
    // 設置分析結果
    await waitFor(() => {
      screen.getByText('匯出分析');
    });
    
    // 點擊匯出按鈕
    const exportButton = screen.getByText('匯出分析');
    fireEvent.click(exportButton);
    
    // 檢查下載連結是否創建
    expect(document.createElement).toHaveBeenCalledWith('a');
    expect(document.body.appendChild).toHaveBeenCalled();
    expect(document.body.removeChild).toHaveBeenCalled();
  });
}); 