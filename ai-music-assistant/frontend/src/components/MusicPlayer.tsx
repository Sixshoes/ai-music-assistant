import {
    Pause,
    PlayArrow,
    VolumeDown,
    VolumeOff,
    VolumeUp
} from '@mui/icons-material';
import {
    Box,
    Card,
    CardContent,
    IconButton,
    Slider,
    Typography,
    useMediaQuery,
    useTheme
} from '@mui/material';
import React, { useEffect, useRef, useState } from 'react';
import { AudioValidatorService } from '../services/AudioValidatorService';
import { Logger } from '../utils/Logger';

// 外部手勢庫，如果不需要可以移除
const hasTouchSupport = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

interface MusicPlayerProps {
  audioUrl: string;
  title?: string;
  showWaveform?: boolean;
  compact?: boolean;
  onError?: (error: string) => void;
}

const MusicPlayer: React.FC<MusicPlayerProps> = ({ 
  audioUrl, 
  title = '音樂播放', 
  showWaveform = false,
  compact = false,
  onError 
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isSmallDisplay = compact || isMobile;
  
  // 播放狀態
  const [isPlaying, setIsPlaying] = useState(false);
  const [duration, setDuration] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [volume, setVolume] = useState(0.8);
  const [isMuted, setIsMuted] = useState(false);
  
  // 觸控相關
  const [isSeeking, setIsSeeking] = useState(false);
  const [touchStartX, setTouchStartX] = useState(0);
  const [touchStartTime, setTouchStartTime] = useState(0);
  
  // 音頻格式相關
  const [mimeType, setMimeType] = useState<string>('audio/wav');
  const [error, setError] = useState<string | null>(null);
  
  // 引用
  const audioRef = useRef<HTMLAudioElement>(null);
  const progressContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const validateAndLoadAudio = async () => {
      try {
        // 驗證音頻格式
        const validationResult = await AudioValidatorService.validateBase64Audio(audioUrl);
        
        if (!validationResult.isValid) {
          const errorMessage = validationResult.errorMessage || '音頻格式驗證失敗';
          Logger.error('音頻格式驗證失敗', { error: errorMessage });
          setError(errorMessage);
          if (onError) {
            onError(errorMessage);
          }
          return;
        }

        // 設置MIME類型
        if (validationResult.mimeType) {
          setMimeType(validationResult.mimeType);
        }

        // 設置音頻源
        if (audioRef.current) {
          try {
            // 創建Blob並設置正確的MIME類型
            const binaryString = atob(audioUrl.split(',')[1] || audioUrl);
            const bytes = new Uint8Array(binaryString.length);
            for (let i = 0; i < binaryString.length; i++) {
              bytes[i] = binaryString.charCodeAt(i);
            }
            const blob = new Blob([bytes], { type: mimeType });
            const objectUrl = URL.createObjectURL(blob);
            audioRef.current.src = objectUrl;
            
            // 設置音量
            audioRef.current.volume = volume;

            // 添加錯誤監聽器
            audioRef.current.onerror = (e) => {
              const errorMessage = '音頻加載失敗：請檢查音頻文件是否完整且格式正確';
              Logger.error('音頻加載失敗', { error: e });
              setError(errorMessage);
              if (onError) {
                onError(errorMessage);
              }
            };

            // 清理舊的URL
            return () => {
              URL.revokeObjectURL(objectUrl);
            };
          } catch (error) {
            const errorMessage = '音頻數據處理失敗：請檢查音頻文件是否完整且格式正確';
            Logger.error('音頻數據處理失敗', { error });
            setError(errorMessage);
            if (onError) {
              onError(errorMessage);
            }
          }
        }

      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : '未知錯誤';
        Logger.error('加載音頻失敗', { error: errorMessage });
        setError(errorMessage);
        if (onError) {
          onError(errorMessage);
        }
      }
    };

    validateAndLoadAudio();
    
    // 清理函數
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.src = '';
      }
    };
  }, [audioUrl, onError, mimeType, volume]);

  // 播放控制
  const handlePlayPause = () => {
    if (audioRef.current) {
      try {
        if (isPlaying) {
          audioRef.current.pause();
        } else {
          const playPromise = audioRef.current.play();
          if (playPromise !== undefined) {
            playPromise.catch(error => {
              const errorMessage = '音頻播放失敗：請檢查音頻文件是否完整且格式正確';
              Logger.error('音頻播放失敗', { error });
              setError(errorMessage);
              if (onError) {
                onError(errorMessage);
              }
            });
          }
        }
        setIsPlaying(!isPlaying);
      } catch (error) {
        const errorMessage = '音頻控制失敗：請檢查音頻文件是否完整且格式正確';
        Logger.error('音頻控制失敗', { error });
        setError(errorMessage);
        if (onError) {
          onError(errorMessage);
        }
      }
    }
  };

  // 進度更新
  const handleTimeUpdate = () => {
    if (audioRef.current && !isSeeking) {
      setCurrentTime(audioRef.current.currentTime);
    }
  };

  // 加載元數據
  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
    }
  };

  // 播放結束
  const handleEnded = () => {
    setIsPlaying(false);
    setCurrentTime(0);
    if (audioRef.current) {
      audioRef.current.currentTime = 0;
    }
  };
  
  // 進度條拖動
  const handleProgressChange = (_: Event, newValue: number | number[]) => {
    const newTime = typeof newValue === 'number' ? newValue : newValue[0];
    setCurrentTime(newTime);
    if (audioRef.current) {
      audioRef.current.currentTime = newTime;
    }
  };
  
  // 音量控制
  const handleVolumeChange = (_: Event, newValue: number | number[]) => {
    const newVolume = typeof newValue === 'number' ? newValue : newValue[0];
    setVolume(newVolume);
    if (audioRef.current) {
      audioRef.current.volume = newVolume;
      setIsMuted(newVolume === 0);
    }
  };
  
  // 靜音切換
  const toggleMute = () => {
    if (audioRef.current) {
      const newMutedState = !isMuted;
      audioRef.current.muted = newMutedState;
      setIsMuted(newMutedState);
    }
  };
  
  // 觸控手勢支持
  const handleTouchStart = (e: React.TouchEvent) => {
    if (!progressContainerRef.current || !hasTouchSupport) return;
    
    setIsSeeking(true);
    setTouchStartX(e.touches[0].clientX);
    setTouchStartTime(currentTime);
  };
  
  const handleTouchMove = (e: React.TouchEvent) => {
    if (!progressContainerRef.current || !hasTouchSupport || !isSeeking) return;
    
    const containerRect = progressContainerRef.current.getBoundingClientRect();
    const containerWidth = containerRect.width;
    
    // 計算滑動距離對應的時間變化
    const touchDeltaX = e.touches[0].clientX - touchStartX;
    const timeChange = (touchDeltaX / containerWidth) * duration;
    let newTime = touchStartTime + timeChange;
    
    // 限制在合理範圍內
    newTime = Math.max(0, Math.min(newTime, duration));
    
    setCurrentTime(newTime);
    if (audioRef.current) {
      audioRef.current.currentTime = newTime;
    }
  };
  
  const handleTouchEnd = () => {
    if (!hasTouchSupport) return;
    setIsSeeking(false);
  };
  
  // 格式化時間
  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
  };

  // 音量圖標選擇
  const getVolumeIcon = () => {
    if (isMuted || volume === 0) return <VolumeOff />;
    if (volume < 0.5) return <VolumeDown />;
    return <VolumeUp />;
  };

  return (
    <Card 
      className="music-player" 
      sx={{ 
        width: '100%',
        boxShadow: 2,
        borderRadius: isSmallDisplay ? 1 : 2,
        overflow: 'hidden'
      }}
    >
      <CardContent 
        sx={{ 
          p: isSmallDisplay ? 1.5 : 2,
          '&:last-child': { pb: isSmallDisplay ? 1.5 : 2 }
        }}
      >
        {title && (
          <Typography 
            variant={isSmallDisplay ? "subtitle1" : "h6"} 
            component="h3" 
            sx={{ mb: 1 }}
          >
            {title}
          </Typography>
        )}
        
        {error ? (
          <Box 
            sx={{ 
              p: 2,
              bgcolor: 'error.light',
              color: 'error.contrastText',
              borderRadius: 1
            }}
          >
            <Typography variant="body2">{error}</Typography>
          </Box>
        ) : (
          <>
            <audio
              ref={audioRef}
              onTimeUpdate={handleTimeUpdate}
              onLoadedMetadata={handleLoadedMetadata}
              onEnded={handleEnded}
            />
            
            <Box 
              sx={{ 
                display: 'flex',
                flexDirection: isSmallDisplay ? 'column' : 'row',
                alignItems: 'center'
              }}
            >
              {/* 播放控制 */}
              <Box 
                sx={{ 
                  display: 'flex',
                  alignItems: 'center',
                  mr: isSmallDisplay ? 0 : 2,
                  mb: isSmallDisplay ? 1 : 0,
                  width: isSmallDisplay ? '100%' : 'auto',
                  justifyContent: isSmallDisplay ? 'space-between' : 'flex-start'
                }}
              >
                <IconButton 
                  onClick={handlePlayPause} 
                  disabled={!!error || duration === 0}
                  size={isSmallDisplay ? "medium" : "large"}
                  sx={{ 
                    mr: 1,
                    width: isSmallDisplay ? 44 : 48,
                    height: isSmallDisplay ? 44 : 48
                  }}
                >
                  {isPlaying ? <Pause /> : <PlayArrow />}
                </IconButton>
                
                <Typography variant="body2" sx={{ minWidth: 70, textAlign: 'center' }}>
                  {formatTime(currentTime)} / {formatTime(duration)}
                </Typography>
                
                {!isSmallDisplay && (
                  <Box 
                    sx={{ 
                      display: 'flex',
                      alignItems: 'center',
                      ml: 2
                    }}
                  >
                    <IconButton onClick={toggleMute} size="small">
                      {getVolumeIcon()}
                    </IconButton>
                    <Slider
                      value={isMuted ? 0 : volume}
                      onChange={handleVolumeChange}
                      min={0}
                      max={1}
                      step={0.01}
                      aria-label="音量"
                      sx={{ width: 100, ml: 1 }}
                    />
                  </Box>
                )}
              </Box>
              
              {/* 進度條 */}
              <Box 
                ref={progressContainerRef}
                sx={{ 
                  flexGrow: 1,
                  width: '100%',
                  touchAction: 'none', // 防止滑動衝突
                }}
                onTouchStart={handleTouchStart}
                onTouchMove={handleTouchMove}
                onTouchEnd={handleTouchEnd}
              >
                <Slider
                  value={currentTime}
                  onChange={handleProgressChange}
                  min={0}
                  max={duration || 1}
                  step={0.01}
                  aria-label="進度條"
                  disabled={duration === 0}
                  sx={{ 
                    '& .MuiSlider-thumb': {
                      width: isSmallDisplay ? 12 : 16, 
                      height: isSmallDisplay ? 12 : 16,
                    },
                    '& .MuiSlider-rail, & .MuiSlider-track': {
                      height: isSmallDisplay ? 4 : 6
                    }
                  }}
                />
              </Box>
            </Box>
            
            {/* 移動端音量控制 */}
            {isSmallDisplay && (
              <Box 
                sx={{ 
                  display: 'flex',
                  alignItems: 'center',
                  mt: 1
                }}
              >
                <IconButton onClick={toggleMute} size="small">
                  {getVolumeIcon()}
                </IconButton>
                <Slider
                  value={isMuted ? 0 : volume}
                  onChange={handleVolumeChange}
                  min={0}
                  max={1}
                  step={0.01}
                  aria-label="音量"
                  sx={{ flexGrow: 1, ml: 1 }}
                />
              </Box>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default MusicPlayer; 