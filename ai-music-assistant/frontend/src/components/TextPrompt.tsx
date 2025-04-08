import React, { useState, useRef, useEffect } from 'react';

interface SuggestionInfo {
  text: string;
  description: string;
  category: 'style' | 'emotion' | 'instruments' | 'generic';
}

interface TextPromptProps {
  onSubmit: (prompt: string) => void;
  placeholder?: string;
  initialValue?: string;
  label?: string;
  isLoading?: boolean;
  suggestions?: SuggestionInfo[];
  onAnalyzeKeywords?: (text: string) => void;
}

const TextPrompt: React.FC<TextPromptProps> = ({
  onSubmit,
  placeholder = '輸入文字提示...',
  initialValue = '',
  label = '創作提示',
  isLoading = false,
  suggestions = [],
  onAnalyzeKeywords
}) => {
  const [prompt, setPrompt] = useState<string>(initialValue);
  const [showSuggestions, setShowSuggestions] = useState<boolean>(false);
  const [filteredSuggestions, setFilteredSuggestions] = useState<SuggestionInfo[]>([]);
  const [highlightedText, setHighlightedText] = useState<string>('');
  const [keywords, setKeywords] = useState<{[key: string]: string}>({});
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);
  
  // 根據內容自動調整文本框高度
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${textarea.scrollHeight}px`;
    }
  }, [prompt]);
  
  // 點擊外部關閉建議
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (suggestionsRef.current && !suggestionsRef.current.contains(event.target as Node) && 
          textareaRef.current && !textareaRef.current.contains(event.target as Node)) {
        setShowSuggestions(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);
  
  // 文字分析和關鍵詞識別
  useEffect(() => {
    const analyzeText = async () => {
      // 關鍵詞檢測邏輯
      const styleKeywords = ['流行', '搖滾', '古典', '爵士', '電子', '鄉村', '嘻哈', '藍調'];
      const emotionKeywords = ['快樂', '悲傷', '興奮', '平靜', '憤怒', '柔和', '激動', '浪漫', '神秘'];
      const instrumentKeywords = ['鋼琴', '吉他', '貝斯', '小提琴', '大提琴', '長笛', '薩克斯風', '鼓'];
      
      const detectedKeywords: {[key: string]: string} = {};
      
      // 檢測風格關鍵詞
      styleKeywords.forEach(keyword => {
        if (prompt.includes(keyword)) {
          detectedKeywords.style = keyword;
        }
      });
      
      // 檢測情感關鍵詞
      emotionKeywords.forEach(keyword => {
        if (prompt.includes(keyword)) {
          detectedKeywords.emotion = keyword;
        }
      });
      
      // 檢測樂器關鍵詞
      instrumentKeywords.forEach(keyword => {
        if (prompt.includes(keyword)) {
          detectedKeywords.instrument = keyword;
        }
      });
      
      setKeywords(detectedKeywords);
      
      // 如果有關鍵詞分析回調，調用它
      if (onAnalyzeKeywords) {
        onAnalyzeKeywords(prompt);
      }
      
      // 根據輸入的文字過濾相關建議
      if (prompt.trim()) {
        const filtered = suggestions.filter(suggestion => 
          suggestion.text.toLowerCase().includes(prompt.toLowerCase()) || 
          prompt.toLowerCase().includes(suggestion.text.toLowerCase().substring(0, 3))
        );
        setFilteredSuggestions(filtered.slice(0, 5)); // 限制最多5個建議
      } else {
        setFilteredSuggestions([]);
      }
    };
    
    const debounce = setTimeout(analyzeText, 300);
    return () => clearTimeout(debounce);
  }, [prompt, suggestions, onAnalyzeKeywords]);
  
  // 處理輸入變化
  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setPrompt(e.target.value);
    setShowSuggestions(true);
  };
  
  // 提交表單
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (prompt.trim() && !isLoading) {
      onSubmit(prompt.trim());
    }
  };
  
  // 應用建議
  const applySuggestion = (suggestion: SuggestionInfo) => {
    setPrompt(suggestion.text);
    setShowSuggestions(false);
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };
  
  // 處理快捷鍵
  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Ctrl+Enter 提交
    if (e.ctrlKey && e.key === 'Enter') {
      handleSubmit(e);
    }
    // 按Esc關閉建議
    if (e.key === 'Escape') {
      setShowSuggestions(false);
    }
  };
  
  // 根據識別的關鍵詞標記文本
  const getHighlightedText = () => {
    let text = prompt;
    Object.entries(keywords).forEach(([type, keyword]) => {
      const colorMap: {[key: string]: string} = {
        style: '#4a90e2',
        emotion: '#e2774a',
        instrument: '#4ae299'
      };
      const color = colorMap[type] || '#999';
      text = text.replace(new RegExp(keyword, 'g'), `<span style="color: ${color}; font-weight: bold;">${keyword}</span>`);
    });
    return text;
  };
  
  return (
    <div className="text-prompt">
      <form onSubmit={handleSubmit}>
        <label className="prompt-label">{label}</label>
        
        <div className="textarea-container">
          <textarea
            ref={textareaRef}
            value={prompt}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={isLoading}
            onClick={() => filteredSuggestions.length > 0 && setShowSuggestions(true)}
            className="prompt-textarea"
            rows={3}
          />
          
          {keywords && Object.keys(keywords).length > 0 && (
            <div className="keyword-tags">
              {Object.entries(keywords).map(([type, keyword], index) => (
                <span key={index} className={`keyword-tag ${type}`}>
                  {keyword}
                </span>
              ))}
            </div>
          )}
          
          {showSuggestions && filteredSuggestions.length > 0 && (
            <div className="suggestions-dropdown" ref={suggestionsRef}>
              {filteredSuggestions.map((suggestion, index) => (
                <div 
                  key={index} 
                  className={`suggestion-item ${suggestion.category}`}
                  onClick={() => applySuggestion(suggestion)}
                >
                  <span className="suggestion-text">{suggestion.text}</span>
                  <span className="suggestion-description">{suggestion.description}</span>
                </div>
              ))}
            </div>
          )}
        </div>
        
        <div className="prompt-footer">
          <div className="prompt-info">
            <span className="character-count">{prompt.length} 字符</span>
            <span className="shortcut-hint">按 Ctrl+Enter 提交</span>
            {Object.keys(keywords).length > 0 && (
              <span className="keyword-hint">識別到 {Object.keys(keywords).length} 個關鍵詞</span>
            )}
          </div>
          
          <button 
            type="submit" 
            className={`submit-button ${isLoading ? 'loading' : ''}`}
            disabled={isLoading || !prompt.trim()}
          >
            {isLoading ? '處理中...' : '提交'}
          </button>
        </div>
      </form>
      
      <style>
        {`
          .text-prompt {
            width: 100%;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            border-radius: 8px;
            background-color: #f9f9f9;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
          }
          
          .prompt-label {
            display: block;
            margin-bottom: 10px;
            font-weight: bold;
            font-size: 16px;
          }
          
          .textarea-container {
            position: relative;
            margin-bottom: 15px;
          }
          
          .prompt-textarea {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 16px;
            line-height: 1.5;
            resize: none;
            transition: all 0.3s;
            background-color: #fff;
          }
          
          .prompt-textarea:focus {
            border-color: #4a90e2;
            outline: none;
            box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
          }
          
          .prompt-textarea:disabled {
            background-color: #f5f5f5;
            cursor: not-allowed;
          }
          
          .keyword-tags {
            display: flex;
            flex-wrap: wrap;
            margin-top: 8px;
            gap: 5px;
          }
          
          .keyword-tag {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
          }
          
          .keyword-tag.style {
            background-color: #e6f0ff;
            color: #4a90e2;
          }
          
          .keyword-tag.emotion {
            background-color: #ffefe6;
            color: #e2774a;
          }
          
          .keyword-tag.instrument {
            background-color: #e6fff0;
            color: #4ae299;
          }
          
          .suggestions-dropdown {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background-color: #fff;
            border: 1px solid #ddd;
            border-top: none;
            border-radius: 0 0 6px 6px;
            max-height: 200px;
            overflow-y: auto;
            z-index: 10;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
          }
          
          .suggestion-item {
            padding: 10px 12px;
            cursor: pointer;
            transition: background-color 0.2s;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-left: 3px solid transparent;
          }
          
          .suggestion-item:hover {
            background-color: #f2f8ff;
          }
          
          .suggestion-item.style {
            border-left-color: #4a90e2;
          }
          
          .suggestion-item.emotion {
            border-left-color: #e2774a;
          }
          
          .suggestion-item.instruments {
            border-left-color: #4ae299;
          }
          
          .suggestion-text {
            font-weight: 500;
          }
          
          .suggestion-description {
            font-size: 12px;
            color: #999;
          }
          
          .prompt-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
          }
          
          .prompt-info {
            display: flex;
            flex-direction: column;
            font-size: 12px;
            color: #666;
          }
          
          .character-count {
            margin-bottom: 4px;
          }
          
          .shortcut-hint {
            color: #999;
          }
          
          .keyword-hint {
            color: #4a90e2;
            margin-top: 4px;
          }
          
          .submit-button {
            padding: 10px 20px;
            background-color: #4a90e2;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
          }
          
          .submit-button:hover:not(:disabled) {
            background-color: #3a7bc8;
            transform: translateY(-2px);
          }
          
          .submit-button:disabled {
            background-color: #b3b3b3;
            cursor: not-allowed;
          }
          
          .submit-button.loading {
            position: relative;
            padding-left: 40px;
          }
          
          .submit-button.loading:before {
            content: '';
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            width: 16px;
            height: 16px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 1s linear infinite;
          }
          
          @keyframes spin {
            to { transform: translateY(-50%) rotate(360deg); }
          }
        `}
      </style>
    </div>
  );
};

export default TextPrompt; 