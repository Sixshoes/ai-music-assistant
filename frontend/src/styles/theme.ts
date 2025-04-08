import { alpha, createTheme, PaletteMode, responsiveFontSizes } from '@mui/material/styles';

// 統一設計系統常量
const BORDER_RADIUS = 8;
const SPACING_UNIT = 8;
const TRANSITION_DURATION = 0.2;

// 色彩系統基礎
const lightPalette = {
  primary: {
    main: '#1976d2',
    light: '#4791db',
    dark: '#115293',
    contrastText: '#ffffff',
  },
  secondary: {
    main: '#e91e63',
    light: '#ed4b82',
    dark: '#a31545',
    contrastText: '#ffffff',
  },
  success: {
    main: '#4caf50',
    light: '#81c784',
    dark: '#388e3c',
  },
  warning: {
    main: '#ff9800',
    light: '#ffb74d',
    dark: '#f57c00',
  },
  error: {
    main: '#f44336',
    light: '#e57373',
    dark: '#d32f2f',
  },
  info: {
    main: '#2196f3',
    light: '#64b5f6',
    dark: '#1976d2',
  },
  background: {
    default: '#f5f5f5',
    paper: '#ffffff',
    secondary: '#f8f9fa',
  },
  text: {
    primary: 'rgba(0, 0, 0, 0.87)',
    secondary: 'rgba(0, 0, 0, 0.6)',
    disabled: 'rgba(0, 0, 0, 0.38)',
  },
  divider: 'rgba(0, 0, 0, 0.12)',
  // 音樂應用特殊色彩
  music: {
    melody: '#3f51b5',
    chord: '#2196f3',
    bass: '#009688',
    drum: '#ff5722',
    waveform: '#1976d2',
    timeline: '#757575',
    notation: '#424242',
  },
};

// 暗色模式色彩系統
const darkPalette = {
  primary: {
    main: '#90caf9',
    light: '#e3f2fd',
    dark: '#42a5f5',
    contrastText: '#000000',
  },
  secondary: {
    main: '#f48fb1',
    light: '#ffc1e3',
    dark: '#bf5f82',
    contrastText: '#000000',
  },
  success: {
    main: '#81c784',
    light: '#c8e6c9',
    dark: '#66bb6a',
  },
  warning: {
    main: '#ffb74d',
    light: '#ffe0b2',
    dark: '#ffa726',
  },
  error: {
    main: '#e57373',
    light: '#ffcdd2',
    dark: '#ef5350',
  },
  info: {
    main: '#64b5f6',
    light: '#e3f2fd',
    dark: '#42a5f5',
  },
  background: {
    default: '#121212',
    paper: '#1e1e1e',
    secondary: '#2d2d2d',
  },
  text: {
    primary: 'rgba(255, 255, 255, 0.87)',
    secondary: 'rgba(255, 255, 255, 0.6)',
    disabled: 'rgba(255, 255, 255, 0.38)',
  },
  divider: 'rgba(255, 255, 255, 0.12)',
  // 音樂應用特殊色彩 - 暗色模式
  music: {
    melody: '#7986cb',
    chord: '#64b5f6',
    bass: '#4db6ac',
    drum: '#ff8a65',
    waveform: '#64b5f6',
    timeline: '#bdbdbd',
    notation: '#e0e0e0',
  },
};

// 創建主題獲取函數
export const getTheme = (mode: PaletteMode = 'light') => {
  const palette = mode === 'light' ? lightPalette : darkPalette;
  
  return responsiveFontSizes(createTheme({
    palette: {
      mode,
      ...palette,
    },
    typography: {
      fontFamily: [
        '-apple-system',
        'BlinkMacSystemFont',
        '"Segoe UI"',
        'Roboto',
        '"Helvetica Neue"',
        'Arial',
        'sans-serif',
      ].join(','),
      h4: {
        fontSize: '1.75rem',
        fontWeight: 600,
        '@media (max-width:600px)': {
          fontSize: '1.5rem',
        },
      },
      h5: {
        fontSize: '1.5rem',
        fontWeight: 600,
        '@media (max-width:600px)': {
          fontSize: '1.25rem',
        },
      },
      h6: {
        fontSize: '1.25rem',
        fontWeight: 600,
        '@media (max-width:600px)': {
          fontSize: '1.125rem',
        },
      },
      subtitle1: {
        fontWeight: 600,
      },
    },
    shape: {
      borderRadius: BORDER_RADIUS,
    },
    spacing: SPACING_UNIT,
    transitions: {
      duration: {
        shortest: 150,
        shorter: 200,
        short: 250,
        standard: 300,
        complex: 375,
        enteringScreen: 225,
        leavingScreen: 195,
      },
    },
    components: {
      MuiCssBaseline: {
        styleOverrides: (theme) => ({
          body: {
            transition: theme.transitions.create(['background-color', 'color'], {
              duration: theme.transitions.duration.standard,
            }),
          },
        }),
      },
      MuiButton: {
        styleOverrides: {
          root: {
            textTransform: 'none',
            borderRadius: BORDER_RADIUS,
            transition: `all ${TRANSITION_DURATION}s ease`,
            '@media (max-width:600px)': {
              minHeight: '42px',
              padding: '8px 16px',
            },
            '&:hover': {
              transform: 'translateY(-2px)',
              boxShadow: `0 4px 8px ${alpha(palette.primary.main, 0.2)}`,
            },
          },
          containedPrimary: {
            boxShadow: `0 2px 4px ${alpha(palette.primary.main, 0.2)}`,
          },
          containedSecondary: {
            boxShadow: `0 2px 4px ${alpha(palette.secondary.main, 0.2)}`,
          },
        },
      },
      MuiIconButton: {
        styleOverrides: {
          root: {
            transition: `all ${TRANSITION_DURATION}s ease`,
            '@media (max-width:600px)': {
              padding: '12px',
            },
            '&:hover': {
              transform: 'scale(1.1)',
              backgroundColor: alpha(palette.primary.main, 0.1),
            },
          },
        },
      },
      MuiInputBase: {
        styleOverrides: {
          root: {
            transition: `all ${TRANSITION_DURATION}s ease`,
            '@media (max-width:600px)': {
              fontSize: '1rem',
            },
          },
        },
      },
      MuiDialog: {
        styleOverrides: {
          paper: {
            borderRadius: BORDER_RADIUS * 1.5,
            '@media (max-width:600px)': {
              margin: '16px',
              width: 'calc(100% - 32px)',
              maxWidth: '100%',
            },
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          rounded: {
            borderRadius: BORDER_RADIUS,
          },
          elevation1: {
            boxShadow: mode === 'dark' 
              ? '0 2px 10px 0 rgba(0,0,0,0.2)' 
              : '0 2px 10px 0 rgba(0,0,0,0.1)',
          },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            borderRadius: BORDER_RADIUS,
            transition: `all ${TRANSITION_DURATION}s ease`,
            '@media (max-width:600px)': {
              padding: '12px',
            },
          },
        },
      },
      MuiTableCell: {
        styleOverrides: {
          root: {
            '@media (max-width:600px)': {
              padding: '8px 12px',
            },
          },
        },
      },
      // 自定義組件樣式
      MuiLinearProgress: {
        styleOverrides: {
          root: {
            borderRadius: BORDER_RADIUS / 2,
            height: 8,
            backgroundColor: alpha(palette.primary.main, 0.1),
          },
        },
      },
      MuiSlider: {
        styleOverrides: {
          root: {
            transition: `all ${TRANSITION_DURATION}s ease`,
            '&:hover': {
              '& .MuiSlider-thumb': {
                boxShadow: `0 0 0 8px ${alpha(palette.primary.main, 0.16)}`,
              },
            },
          },
          thumb: {
            transition: `all ${TRANSITION_DURATION}s ease`,
          },
        },
      },
    },
  }));
};

// 導出默認亮色主題
export const theme = getTheme('light');

// 導出暗色主題
export const darkTheme = getTheme('dark'); 