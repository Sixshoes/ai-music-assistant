import { useMemo } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { theme } from '../styles/theme';

export const useTheme = () => {
  const currentTheme = useMemo(() => createTheme(theme), []);

  return {
    theme: currentTheme,
    ThemeProvider,
  };
}; 