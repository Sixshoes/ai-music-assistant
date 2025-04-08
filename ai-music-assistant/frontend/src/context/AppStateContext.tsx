import React, { createContext, Dispatch, ReactNode, useContext, useReducer } from 'react';

// 定義應用狀態類型
export interface AppState {
  // 用戶界面狀態
  ui: {
    isLoading: boolean;
    activeView: string;
    errorMessage: string | null;
    successMessage: string | null;
  };
  // 音樂生成狀態
  musicGeneration: {
    generatingMusic: boolean;
    progress: number;
    currentStage: string;
  };
  // 音樂播放狀態
  musicPlayer: {
    isPlaying: boolean;
    currentTime: number;
    duration: number;
    volume: number;
    loop: boolean;
  };
  // 項目狀態
  projects: {
    currentProjectId: string | null;
    savedProjects: any[];
  };
  // 用戶偏好設置
  preferences: {
    defaultGenre: string;
    defaultTempo: number;
    defaultKey: string;
    favoriteInstruments: string[];
  };
}

// 定義動作類型
export type ActionType = 
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ACTIVE_VIEW'; payload: string }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_SUCCESS'; payload: string | null }
  | { type: 'SET_GENERATING_MUSIC'; payload: boolean }
  | { type: 'SET_PROGRESS'; payload: number }
  | { type: 'SET_CURRENT_STAGE'; payload: string }
  | { type: 'SET_PLAYING'; payload: boolean }
  | { type: 'SET_CURRENT_TIME'; payload: number }
  | { type: 'SET_DURATION'; payload: number }
  | { type: 'SET_VOLUME'; payload: number }
  | { type: 'SET_LOOP'; payload: boolean }
  | { type: 'SET_CURRENT_PROJECT'; payload: string | null }
  | { type: 'SET_SAVED_PROJECTS'; payload: any[] }
  | { type: 'ADD_SAVED_PROJECT'; payload: any }
  | { type: 'UPDATE_SAVED_PROJECT'; payload: { id: string; data: any } }
  | { type: 'REMOVE_SAVED_PROJECT'; payload: string }
  | { type: 'SET_DEFAULT_GENRE'; payload: string }
  | { type: 'SET_DEFAULT_TEMPO'; payload: number }
  | { type: 'SET_DEFAULT_KEY'; payload: string }
  | { type: 'SET_FAVORITE_INSTRUMENTS'; payload: string[] };

// 定義初始狀態
const initialState: AppState = {
  ui: {
    isLoading: false,
    activeView: 'home',
    errorMessage: null,
    successMessage: null,
  },
  musicGeneration: {
    generatingMusic: false,
    progress: 0,
    currentStage: '',
  },
  musicPlayer: {
    isPlaying: false,
    currentTime: 0,
    duration: 0,
    volume: 0.8,
    loop: false,
  },
  projects: {
    currentProjectId: null,
    savedProjects: [],
  },
  preferences: {
    defaultGenre: 'pop',
    defaultTempo: 120,
    defaultKey: 'C',
    favoriteInstruments: ['piano', 'guitar', 'drums', 'bass'],
  },
};

// 創建上下文
export const AppStateContext = createContext<{
  state: AppState;
  dispatch: Dispatch<ActionType>;
}>({
  state: initialState,
  dispatch: () => null,
});

// 定義 reducer 函數
function appReducer(state: AppState, action: ActionType): AppState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, ui: { ...state.ui, isLoading: action.payload } };
    case 'SET_ACTIVE_VIEW':
      return { ...state, ui: { ...state.ui, activeView: action.payload } };
    case 'SET_ERROR':
      return { ...state, ui: { ...state.ui, errorMessage: action.payload } };
    case 'SET_SUCCESS':
      return { ...state, ui: { ...state.ui, successMessage: action.payload } };
    case 'SET_GENERATING_MUSIC':
      return { ...state, musicGeneration: { ...state.musicGeneration, generatingMusic: action.payload } };
    case 'SET_PROGRESS':
      return { ...state, musicGeneration: { ...state.musicGeneration, progress: action.payload } };
    case 'SET_CURRENT_STAGE':
      return { ...state, musicGeneration: { ...state.musicGeneration, currentStage: action.payload } };
    case 'SET_PLAYING':
      return { ...state, musicPlayer: { ...state.musicPlayer, isPlaying: action.payload } };
    case 'SET_CURRENT_TIME':
      return { ...state, musicPlayer: { ...state.musicPlayer, currentTime: action.payload } };
    case 'SET_DURATION':
      return { ...state, musicPlayer: { ...state.musicPlayer, duration: action.payload } };
    case 'SET_VOLUME':
      return { ...state, musicPlayer: { ...state.musicPlayer, volume: action.payload } };
    case 'SET_LOOP':
      return { ...state, musicPlayer: { ...state.musicPlayer, loop: action.payload } };
    case 'SET_CURRENT_PROJECT':
      return { ...state, projects: { ...state.projects, currentProjectId: action.payload } };
    case 'SET_SAVED_PROJECTS':
      return { ...state, projects: { ...state.projects, savedProjects: action.payload } };
    case 'ADD_SAVED_PROJECT':
      return { 
        ...state, 
        projects: { 
          ...state.projects, 
          savedProjects: [...state.projects.savedProjects, action.payload] 
        } 
      };
    case 'UPDATE_SAVED_PROJECT':
      return { 
        ...state, 
        projects: { 
          ...state.projects, 
          savedProjects: state.projects.savedProjects.map(
            project => project.id === action.payload.id 
              ? { ...project, ...action.payload.data } 
              : project
          ) 
        } 
      };
    case 'REMOVE_SAVED_PROJECT':
      return { 
        ...state, 
        projects: { 
          ...state.projects, 
          savedProjects: state.projects.savedProjects.filter(
            project => project.id !== action.payload
          ) 
        } 
      };
    case 'SET_DEFAULT_GENRE':
      return { ...state, preferences: { ...state.preferences, defaultGenre: action.payload } };
    case 'SET_DEFAULT_TEMPO':
      return { ...state, preferences: { ...state.preferences, defaultTempo: action.payload } };
    case 'SET_DEFAULT_KEY':
      return { ...state, preferences: { ...state.preferences, defaultKey: action.payload } };
    case 'SET_FAVORITE_INSTRUMENTS':
      return { ...state, preferences: { ...state.preferences, favoriteInstruments: action.payload } };
    default:
      return state;
  }
}

// AppState Provider 組件
interface AppStateProviderProps {
  children: ReactNode;
}

export const AppStateProvider: React.FC<AppStateProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // 初始化時從 localStorage 加載偏好設置和保存的項目
  React.useEffect(() => {
    try {
      // 加載偏好設置
      const savedPreferences = localStorage.getItem('app_preferences');
      if (savedPreferences) {
        const preferences = JSON.parse(savedPreferences);
        dispatch({ type: 'SET_DEFAULT_GENRE', payload: preferences.defaultGenre || 'pop' });
        dispatch({ type: 'SET_DEFAULT_TEMPO', payload: preferences.defaultTempo || 120 });
        dispatch({ type: 'SET_DEFAULT_KEY', payload: preferences.defaultKey || 'C' });
        dispatch({ 
          type: 'SET_FAVORITE_INSTRUMENTS', 
          payload: preferences.favoriteInstruments || ['piano', 'guitar', 'drums', 'bass'] 
        });
      }
      
      // 加載保存的項目
      const savedProjects = localStorage.getItem('saved_projects');
      if (savedProjects) {
        dispatch({ type: 'SET_SAVED_PROJECTS', payload: JSON.parse(savedProjects) });
      }
    } catch (error) {
      console.error('加載本地存儲數據失敗:', error);
    }
  }, []);
  
  // 當偏好設置或保存的項目更改時保存到 localStorage
  React.useEffect(() => {
    try {
      localStorage.setItem('app_preferences', JSON.stringify(state.preferences));
    } catch (error) {
      console.error('保存偏好設置失敗:', error);
    }
  }, [state.preferences]);
  
  React.useEffect(() => {
    try {
      localStorage.setItem('saved_projects', JSON.stringify(state.projects.savedProjects));
    } catch (error) {
      console.error('保存項目失敗:', error);
    }
  }, [state.projects.savedProjects]);

  return (
    <AppStateContext.Provider value={{ state, dispatch }}>
      {children}
    </AppStateContext.Provider>
  );
};

// 自定義 hook 用於訪問狀態和調度器
export const useAppState = () => useContext(AppStateContext); 