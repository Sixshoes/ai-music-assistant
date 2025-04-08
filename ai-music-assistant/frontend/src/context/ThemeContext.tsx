import { PaletteMode } from '@mui/material';
import { ThemeProvider as MuiThemeProvider } from '@mui/material/styles';
import React, { createContext, ReactNode, useContext, useEffect, useState } from 'react';
import { getTheme } from '../styles/theme';

// 定義主題上下文類型
type ThemeContextType = {
  mode: PaletteMode;
  toggleTheme: () => void;
};

// 創建主題上下文
export const ThemeContext = createContext<ThemeContextType>({
  mode: 'light',
  toggleTheme: () => {},
});

// 主題提供者屬性接口
interface ThemeProviderProps {
  children: ReactNode;
}

// 主題提供者組件
export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  // 嘗試從本地存儲獲取主題偏好
  const getInitialMode = (): PaletteMode => {
    const savedMode = localStorage.getItem('themeMode');
    if (savedMode && (savedMode === 'light' || savedMode === 'dark')) {
      return savedMode;
    }
    
    // 檢查系統偏好
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    
    return 'light';
  };

  const [mode, setMode] = useState<PaletteMode>(getInitialMode);
  
  // 切換主題函數
  const toggleTheme = () => {
    setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
  };
  
  // 保存主題偏好到本地存儲
  useEffect(() => {
    localStorage.setItem('themeMode', mode);
    
    // 更新 body 類以便應用全局樣式
    if (mode === 'dark') {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
  }, [mode]);
  
  // 監聽系統主題變化
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const handleChange = (e: MediaQueryListEvent) => {
      if (!localStorage.getItem('themeMode')) {
        setMode(e.matches ? 'dark' : 'light');
      }
    };
    
    mediaQuery.addEventListener('change', handleChange);
    
    return () => {
      mediaQuery.removeEventListener('change', handleChange);
    };
  }, []);
  
  // 使用當前主題模式獲取主題
  const theme = getTheme(mode);
  
  return (
    <ThemeContext.Provider value={{ mode, toggleTheme }}>
      <MuiThemeProvider theme={theme}>
        {children}
      </MuiThemeProvider>
    </ThemeContext.Provider>
  );
};

// 自定義鉤子以方便使用主題上下文
export const useThemeContext = () => useContext(ThemeContext); 