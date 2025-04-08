import DownloadIcon from '@mui/icons-material/Download';
import PauseIcon from '@mui/icons-material/Pause';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import RepeatIcon from '@mui/icons-material/Repeat';
import RepeatOneIcon from '@mui/icons-material/RepeatOne';
import ReplayIcon from '@mui/icons-material/Replay';
import VolumeDownIcon from '@mui/icons-material/VolumeDown';
import VolumeMuteIcon from '@mui/icons-material/VolumeMute';
import VolumeUpIcon from '@mui/icons-material/VolumeUp';
import WavesIcon from '@mui/icons-material/Waves';
import {
    Box,
    CircularProgress,
    Grid,
    IconButton,
    Paper,
    Slider,
    Tooltip,
    Typography,
} from '@mui/material';
import React, { memo, useCallback, useEffect, useRef, useState } from 'react';

import { useAction, useAppStateSelector } from '../../hooks/useAppStateSelector';

// 格式化時間（秒）為 mm:ss 格式
const formatTime = (seconds: number): string => {
  if (isNaN(seconds)) return '00:00';
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

interface MusicPlayerProps {
  audioUrl?: string;
  title?: string;
  onDownload?: () => void;
  showWaveform?: boolean;
  autoPlay?: boolean;
}

// 使用 memo 包裝組件以避免不必要的重新渲染
const MusicPlayer: React.FC<MusicPlayerProps> = memo(({
  audioUrl,
  title = '音樂播放器',
  onDownload,
  showWaveform = false,
  autoPlay = false,
}) => {
  // 從全局狀態獲取播放器相關狀態
  const playerState = useAppStateSelector(state => state.musicPlayer);
  
  // 使用 actions 更新全局狀態
  const setPlaying = useAction<boolean>('SET_PLAYING');
  const setCurrentTime = useAction<number>('SET_CURRENT_TIME');
  const setDuration = useAction<number>('SET_DURATION');
  const setVolume = useAction<number>('SET_VOLUME');
  const setLoop = useAction<boolean>('SET_LOOP');
  
  // 本地狀態，僅用於UI渲染或暫時狀態
  const [loading, setLoading] = useState(false);
  const [audioReady, setAudioReady] = useState(false);
  const [draggingTime, setDraggingTime] = useState(false);
  
  // Refs
  const audioRef = useRef<HTMLAudioElement | null>(null);
  
  // 設置音頻源
  useEffect(() => {
    const setupAudio = async () => {
      try {
        if (!audioRef.current || !audioUrl) return;
        
        setLoading(true);
        setAudioReady(false);
        
        audioRef.current.src = audioUrl;
        
        // 應用全局音量設置
        audioRef.current.volume = playerState.volume;
        audioRef.current.loop = playerState.loop;
        
        // 如果設置了自動播放，則在音頻加載完成後播放
        if (autoPlay) {
          const playPromise = audioRef.current.play();
          if (playPromise) {
            playPromise.catch(error => {
              console.warn('自動播放失敗:', error);
              setPlaying(false);
            });
          }
        }
      } catch (error) {
        console.error('設置音頻時出錯:', error);
      } finally {
        setLoading(false);
      }
    };
    
    setupAudio();
    
    // 清理函數
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.src = '';
      }
    };
  }, [audioUrl, autoPlay, playerState.volume, playerState.loop, setPlaying]);
  
  // 更新音頻元素的時間監聽器
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    
    // 時間更新事件
    const handleTimeUpdate = () => {
      if (!draggingTime) {
        setCurrentTime(audio.currentTime);
      }
    };
    
    // 持續時間元數據加載完成事件
    const handleLoadedMetadata = () => {
      setDuration(audio.duration);
      setAudioReady(true);
    };
    
    // 播放事件
    const handlePlay = () => setPlaying(true);
    
    // 暫停事件
    const handlePause = () => setPlaying(false);
    
    // 播放結束事件
    const handleEnded = () => {
      if (!playerState.loop) {
        setPlaying(false);
        setCurrentTime(0);
      }
    };
    
    // 添加事件監聽器
    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('loadedmetadata', handleLoadedMetadata);
    audio.addEventListener('play', handlePlay);
    audio.addEventListener('pause', handlePause);
    audio.addEventListener('ended', handleEnded);
    
    // 清理事件監聽器
    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
      audio.removeEventListener('play', handlePlay);
      audio.removeEventListener('pause', handlePause);
      audio.removeEventListener('ended', handleEnded);
    };
  }, [draggingTime, playerState.loop, setCurrentTime, setDuration, setPlaying]);
  
  // 同步播放狀態與音頻元素
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio || !audioReady) return;
    
    if (playerState.isPlaying && audio.paused) {
      const playPromise = audio.play();
      if (playPromise) {
        playPromise.catch(() => {
          setPlaying(false);
        });
      }
    } else if (!playerState.isPlaying && !audio.paused) {
      audio.pause();
    }
  }, [playerState.isPlaying, audioReady, setPlaying]);
  
  // 同步音量
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = playerState.volume;
    }
  }, [playerState.volume]);
  
  // 同步循環設置
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.loop = playerState.loop;
    }
  }, [playerState.loop]);
  
  // 播放/暫停切換
  const togglePlay = useCallback(() => {
    setPlaying(!playerState.isPlaying);
  }, [playerState.isPlaying, setPlaying]);
  
  // 循環切換
  const toggleLoop = useCallback(() => {
    setLoop(!playerState.loop);
  }, [playerState.loop, setLoop]);
  
  // 重播
  const handleReplay = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.currentTime = 0;
      setCurrentTime(0);
      setPlaying(true);
    }
  }, [setCurrentTime, setPlaying]);
  
  // 時間滑塊變更（拖動中）
  const handleTimeChange = (_: Event, value: number | number[]) => {
    setCurrentTime(value as number);
  };
  
  // 時間滑塊變更結束（釋放）
  const handleTimeChangeCommitted = (_: Event | React.SyntheticEvent, value: number | number[]) => {
    if (audioRef.current) {
      audioRef.current.currentTime = value as number;
    }
    setDraggingTime(false);
  };
  
  // 時間滑塊拖動開始
  const handleTimeSliderStart = () => {
    setDraggingTime(true);
  };
  
  // 音量滑塊變更
  const handleVolumeChange = (_: Event, value: number | number[]) => {
    setVolume(value as number);
  };
  
  // 獲取音量圖標
  const getVolumeIcon = () => {
    if (playerState.volume === 0) return <VolumeMuteIcon />;
    if (playerState.volume < 0.5) return <VolumeDownIcon />;
    return <VolumeUpIcon />;
  };
  
  return (
    <Paper 
      elevation={3} 
      sx={{ 
        p: 2,
        borderRadius: 2,
        bgcolor: 'background.paper',
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      <audio ref={audioRef} preload="metadata" />
      
      {/* 標題 */}
      <Typography 
        variant="subtitle1" 
        sx={{ 
          mb: 1, 
          textAlign: 'center',
          fontWeight: 'medium',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap'
        }}
      >
        {title}
      </Typography>
      
      {/* 波形顯示 */}
      {showWaveform && (
        <Box 
          sx={{ 
            height: 60, 
            mb: 1, 
            bgcolor: 'action.hover',
            borderRadius: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
        >
          <WavesIcon sx={{ opacity: 0.6 }} />
        </Box>
      )}
      
      {/* 時間滑塊 */}
      <Box sx={{ px: 1 }}>
        <Slider
          value={playerState.currentTime}
          max={playerState.duration || 100}
          onChange={handleTimeChange}
          onChangeCommitted={handleTimeChangeCommitted}
          onMouseDown={handleTimeSliderStart}
          onTouchStart={handleTimeSliderStart}
          disabled={!audioReady || loading}
          aria-label="音樂播放時間"
          size="small"
          sx={{ mt: 1, mb: 0 }}
        />
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: -1, mb: 1.5 }}>
          <Typography variant="caption" color="text.secondary">
            {formatTime(playerState.currentTime)}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {formatTime(playerState.duration)}
          </Typography>
        </Box>
      </Box>
      
      {/* 控制按鈕 */}
      <Grid container spacing={1} alignItems="center">
        <Grid item xs={7} sm={8}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            {/* 播放/暫停按鈕 */}
            <IconButton 
              onClick={togglePlay}
              disabled={!audioReady || loading}
              color="primary"
              size="large"
            >
              {loading ? (
                <CircularProgress size={24} />
              ) : playerState.isPlaying ? (
                <PauseIcon />
              ) : (
                <PlayArrowIcon />
              )}
            </IconButton>
            
            {/* 重播按鈕 */}
            <IconButton 
              onClick={handleReplay}
              disabled={!audioReady || loading}
              size="small"
            >
              <ReplayIcon fontSize="small" />
            </IconButton>
            
            {/* 循環按鈕 */}
            <Tooltip title={playerState.loop ? "關閉循環" : "開啟循環"}>
              <IconButton 
                onClick={toggleLoop}
                color={playerState.loop ? "primary" : "default"}
                disabled={!audioReady || loading}
                size="small"
              >
                {playerState.loop ? <RepeatOneIcon fontSize="small" /> : <RepeatIcon fontSize="small" />}
              </IconButton>
            </Tooltip>
            
            {/* 下載按鈕（如果提供了下載處理程序） */}
            {onDownload && (
              <IconButton onClick={onDownload} size="small">
                <DownloadIcon fontSize="small" />
              </IconButton>
            )}
          </Box>
        </Grid>
        
        {/* 音量控制 */}
        <Grid item xs={5} sm={4}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <IconButton size="small" onClick={() => setVolume(playerState.volume === 0 ? 0.5 : 0)}>
              {getVolumeIcon()}
            </IconButton>
            <Slider
              value={playerState.volume}
              onChange={handleVolumeChange}
              min={0}
              max={1}
              step={0.01}
              aria-label="音量"
              size="small"
              sx={{ mx: 1 }}
            />
          </Box>
        </Grid>
      </Grid>
    </Paper>
  );
});

MusicPlayer.displayName = 'MusicPlayer';

export default MusicPlayer; 