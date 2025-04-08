import {
    MusicNote,
    Pause,
    PlayArrow,
    Repeat,
    Stop,
    VolumeOff,
    VolumeUp,
    ZoomIn,
    ZoomOut
} from '@mui/icons-material';
import {
    Box,
    CircularProgress,
    IconButton,
    Paper,
    Slider,
    Tooltip,
    Typography,
    useMediaQuery,
    useTheme
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import React, { useEffect, useRef, useState } from 'react';

interface MusicVisualizerProps {
  audioUrl?: string;
  scoreData?: any;
  title?: string;
  showWaveform?: boolean;
  showScoreView?: boolean;
  onTimeUpdate?: (time: number) => void;
}

const MusicVisualizer: React.FC<MusicVisualizerProps> = ({
  audioUrl,
  scoreData,
  title = '音樂視覺化',
  showWaveform = true,
  showScoreView = true,
  onTimeUpdate
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  // 狀態
  const [isLoading, setIsLoading] = useState(true);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.8);
  const [isMuted, setIsMuted] = useState(false);
  const [zoom, setZoom] = useState(100);
  const [error, setError] = useState<string | null>(null);
  
  // 引用
  const audioRef = useRef<HTMLAudioElement>(null);
  const waveformCanvasRef = useRef<HTMLCanvasElement>(null);
  const scoreContainerRef = useRef<HTMLDivElement>(null);
  const animationFrameRef = useRef<number | null>(null);
  
  // 波形數據
  const [waveformData, setWaveformData] = useState<Float32Array | null>(null);
  
  // 音頻緩衝區分析器
  const [audioContext, setAudioContext] = useState<AudioContext | null>(null);
  const [analyser, setAnalyser] = useState<AnalyserNode | null>(null);
  
  // 初始化音頻上下文和分析器
  useEffect(() => {
    if (audioUrl && showWaveform) {
      try {
        const context = new (window.AudioContext || (window as any).webkitAudioContext)();
        const analyserNode = context.createAnalyser();
        analyserNode.fftSize = 2048;
        
        setAudioContext(context);
        setAnalyser(analyserNode);
      } catch (err) {
        console.error('無法創建音頻上下文:', err);
        setError('您的瀏覽器不支持音頻分析功能。');
      }
    }
    
    return () => {
      if (audioContext) {
        audioContext.close();
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [audioUrl, showWaveform]);
  
  // 連接音頻源和分析器
  useEffect(() => {
    const connectAudio = async () => {
      if (!audioRef.current || !audioContext || !analyser || !audioUrl) return;
      
      try {
        // 從URL獲取音頻數據
        const response = await fetch(audioUrl);
        const arrayBuffer = await response.arrayBuffer();
        
        // 解碼音頻數據
        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
        
        // 獲取波形數據
        const samples = new Float32Array(audioBuffer.length);
        const channel = audioBuffer.getChannelData(0);
        for (let i = 0; i < audioBuffer.length; i++) {
          samples[i] = channel[i];
        }
        
        setWaveformData(samples);
        setIsLoading(false);
        
        // 處理媒體元素連接
        if (audioRef.current) {
          const source = audioContext.createMediaElementSource(audioRef.current);
          source.connect(analyser);
          analyser.connect(audioContext.destination);
        }
      } catch (err) {
        console.error('音頻數據處理錯誤:', err);
        setError('無法處理音頻數據。');
        setIsLoading(false);
      }
    };
    
    connectAudio();
  }, [audioUrl, audioContext, analyser]);
  
  // 繪製波形
  useEffect(() => {
    if (!showWaveform || !waveformCanvasRef.current || !waveformData || isLoading) return;
    
    const canvas = waveformCanvasRef.current;
    const canvasCtx = canvas.getContext('2d');
    if (!canvasCtx) return;
    
    // 確保高清顯示
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    canvasCtx.scale(dpr, dpr);
    canvas.style.width = rect.width + 'px';
    canvas.style.height = rect.height + 'px';
    
    // 繪製波形
    canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
    
    const primaryColor = theme.palette.mode === 'dark' 
      ? theme.palette.primary.light 
      : theme.palette.primary.main;
    
    const secondaryColor = theme.palette.mode === 'dark'
      ? alpha(theme.palette.primary.light, 0.3)
      : alpha(theme.palette.primary.main, 0.2);
    
    // 繪製背景網格
    canvasCtx.strokeStyle = secondaryColor;
    canvasCtx.lineWidth = 1;
    
    // 水平線
    const gridStepY = rect.height / 4;
    for (let i = 0; i <= 4; i++) {
      const y = i * gridStepY;
      canvasCtx.beginPath();
      canvasCtx.moveTo(0, y);
      canvasCtx.lineTo(rect.width, y);
      canvasCtx.stroke();
    }
    
    // 垂直線
    const gridStepX = rect.width / 8;
    for (let i = 0; i <= 8; i++) {
      const x = i * gridStepX;
      canvasCtx.beginPath();
      canvasCtx.moveTo(x, 0);
      canvasCtx.lineTo(x, rect.height);
      canvasCtx.stroke();
    }
    
    // 繪製波形
    canvasCtx.strokeStyle = primaryColor;
    canvasCtx.lineWidth = 2;
    canvasCtx.beginPath();
    
    // 調整採樣率以適應顯示
    const sliceWidth = rect.width / (waveformData.length / 100);
    let x = 0;
    
    for (let i = 0; i < waveformData.length; i += 100) {
      const y = (waveformData[i] * rect.height / 2) + (rect.height / 2);
      if (i === 0) {
        canvasCtx.moveTo(x, y);
      } else {
        canvasCtx.lineTo(x, y);
      }
      x += sliceWidth;
    }
    
    canvasCtx.stroke();
    
    // 繪製播放位置指示器
    if (audioRef.current && duration > 0) {
      const playheadX = (currentTime / duration) * rect.width;
      canvasCtx.strokeStyle = theme.palette.secondary.main;
      canvasCtx.lineWidth = 2;
      canvasCtx.beginPath();
      canvasCtx.moveTo(playheadX, 0);
      canvasCtx.lineTo(playheadX, rect.height);
      canvasCtx.stroke();
    }
  }, [waveformData, isLoading, theme, showWaveform, currentTime, duration, zoom]);
  
  // 實時更新音頻播放
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    
    const handleTimeUpdate = () => {
      setCurrentTime(audio.currentTime);
      if (onTimeUpdate) {
        onTimeUpdate(audio.currentTime);
      }
      
      // 如果顯示波形，更新波形繪製
      if (showWaveform && waveformCanvasRef.current && waveformData) {
        drawWaveform();
      }
    };
    
    const handleLoadedMetadata = () => {
      setDuration(audio.duration);
      setIsLoading(false);
    };
    
    const handleEnded = () => {
      setIsPlaying(false);
      setCurrentTime(0);
      audio.currentTime = 0;
    };
    
    const handleError = () => {
      setError('加載音頻時發生錯誤。');
      setIsLoading(false);
    };
    
    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('loadedmetadata', handleLoadedMetadata);
    audio.addEventListener('ended', handleEnded);
    audio.addEventListener('error', handleError);
    
    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
      audio.removeEventListener('ended', handleEnded);
      audio.removeEventListener('error', handleError);
    };
  }, [onTimeUpdate, showWaveform, waveformData]);
  
  // 繪製波形函數
  const drawWaveform = () => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
    
    if (!analyser || !waveformCanvasRef.current) return;
    
    const canvas = waveformCanvasRef.current;
    const canvasCtx = canvas.getContext('2d');
    if (!canvasCtx) return;
    
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    
    const draw = () => {
      animationFrameRef.current = requestAnimationFrame(draw);
      
      analyser.getByteTimeDomainData(dataArray);
      
      // 使用與靜態繪製相同的方法，但使用實時數據
      const rect = canvas.getBoundingClientRect();
      canvasCtx.clearRect(0, 0, rect.width, rect.height);
      
      const primaryColor = theme.palette.mode === 'dark' 
        ? theme.palette.primary.light 
        : theme.palette.primary.main;
      
      // 繪製波形
      canvasCtx.strokeStyle = primaryColor;
      canvasCtx.lineWidth = 2;
      canvasCtx.beginPath();
      
      const sliceWidth = rect.width / bufferLength;
      let x = 0;
      
      for (let i = 0; i < bufferLength; i++) {
        const v = dataArray[i] / 128.0;
        const y = v * rect.height / 2;
        
        if (i === 0) {
          canvasCtx.moveTo(x, y);
        } else {
          canvasCtx.lineTo(x, y);
        }
        
        x += sliceWidth;
      }
      
      canvasCtx.lineTo(rect.width, rect.height / 2);
      canvasCtx.stroke();
      
      // 繪製播放位置指示器
      if (audioRef.current && duration > 0) {
        const playheadX = (currentTime / duration) * rect.width;
        canvasCtx.strokeStyle = theme.palette.secondary.main;
        canvasCtx.lineWidth = 2;
        canvasCtx.beginPath();
        canvasCtx.moveTo(playheadX, 0);
        canvasCtx.lineTo(playheadX, rect.height);
        canvasCtx.stroke();
      }
    };
    
    draw();
  };
  
  // 播放控制
  const togglePlay = () => {
    const audio = audioRef.current;
    if (!audio) return;
    
    if (isPlaying) {
      audio.pause();
    } else {
      // 如果音頻上下文被暫停，恢復它
      if (audioContext && audioContext.state === 'suspended') {
        audioContext.resume();
      }
      audio.play();
    }
    
    setIsPlaying(!isPlaying);
  };
  
  const stopPlay = () => {
    const audio = audioRef.current;
    if (!audio) return;
    
    audio.pause();
    audio.currentTime = 0;
    setIsPlaying(false);
    setCurrentTime(0);
  };
  
  const handleSeek = (event: any, value: number | number[]) => {
    const audio = audioRef.current;
    if (!audio) return;
    
    const seekTime = typeof value === 'number' ? value : value[0];
    audio.currentTime = seekTime;
    setCurrentTime(seekTime);
  };
  
  const handleVolumeChange = (event: any, value: number | number[]) => {
    const audio = audioRef.current;
    if (!audio) return;
    
    const newVolume = typeof value === 'number' ? value : value[0];
    audio.volume = newVolume;
    setVolume(newVolume);
    
    if (newVolume === 0) {
      setIsMuted(true);
    } else if (isMuted) {
      setIsMuted(false);
    }
  };
  
  const toggleMute = () => {
    const audio = audioRef.current;
    if (!audio) return;
    
    const newMuteState = !isMuted;
    audio.muted = newMuteState;
    setIsMuted(newMuteState);
  };
  
  // 格式化時間
  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };
  
  // 縮放控制
  const handleZoomChange = (newZoom: number) => {
    setZoom(Math.max(50, Math.min(200, newZoom)));
  };
  
  return (
    <Paper 
      elevation={2} 
      sx={{ 
        p: 2, 
        borderRadius: 2,
        bgcolor: theme.palette.background.paper,
        boxShadow: theme.shadows[3],
        overflow: 'hidden'
      }}
    >
      <Box sx={{ mb: 2 }}>
        <Typography variant="h6" gutterBottom>{title}</Typography>
        
        {/* 音頻元素 */}
        <audio ref={audioRef} src={audioUrl} style={{ display: 'none' }} />
        
        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress size={40} />
          </Box>
        ) : error ? (
          <Box sx={{ p: 2, textAlign: 'center', color: 'error.main' }}>
            <Typography>{error}</Typography>
          </Box>
        ) : (
          <>
            {/* 波形顯示 */}
            {showWaveform && (
              <Box sx={{ position: 'relative', mb: 2 }}>
                <Box 
                  sx={{ 
                    height: 150, 
                    bgcolor: alpha(theme.palette.background.default, 0.4),
                    borderRadius: 1,
                    border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
                    overflow: 'hidden',
                    transition: 'all 0.3s ease',
                    cursor: 'pointer',
                    '&:hover': {
                      boxShadow: `0 0 0 2px ${alpha(theme.palette.primary.main, 0.2)}`
                    }
                  }}
                  onClick={(e) => {
                    if (!audioRef.current) return;
                    
                    const rect = e.currentTarget.getBoundingClientRect();
                    const clickX = e.clientX - rect.left;
                    const percentX = clickX / rect.width;
                    
                    const seekTime = percentX * duration;
                    audioRef.current.currentTime = seekTime;
                    setCurrentTime(seekTime);
                  }}
                >
                  <canvas 
                    ref={waveformCanvasRef} 
                    style={{ 
                      width: '100%', 
                      height: '100%',
                      transform: `scaleX(${zoom / 100})`
                    }}
                  />
                </Box>
                
                {/* 時間軸 */}
                <Box 
                  sx={{ 
                    display: 'flex', 
                    justifyContent: 'space-between',
                    mt: 0.5,
                    px: 1,
                    fontSize: '0.75rem',
                    color: theme.palette.text.secondary
                  }}
                >
                  <span>{formatTime(currentTime)}</span>
                  <span>{formatTime(duration)}</span>
                </Box>
              </Box>
            )}
            
            {/* 樂譜視圖 */}
            {showScoreView && scoreData && (
              <Box 
                ref={scoreContainerRef}
                sx={{ 
                  mb: 2, 
                  height: 200, 
                  bgcolor: alpha(theme.palette.background.default, 0.4),
                  borderRadius: 1,
                  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
                  overflow: 'auto',
                  p: 1
                }}
              >
                {/* 樂譜渲染區域 */}
                <Box sx={{ 
                  transform: `scale(${zoom / 100})`,
                  transformOrigin: 'top left',
                  transition: 'transform 0.3s ease'
                }}>
                  {scoreData ? (
                    <Typography>樂譜視圖: 需要整合VexFlow或其他樂譜渲染庫</Typography>
                  ) : (
                    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                      <MusicNote sx={{ mr: 1, opacity: 0.5 }} />
                      <Typography variant="body2" color="text.secondary">沒有可用的樂譜數據</Typography>
                    </Box>
                  )}
                </Box>
              </Box>
            )}
            
            {/* 控制面板 */}
            <Box sx={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 1 }}>
              {/* 播放控制 */}
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <IconButton onClick={stopPlay} size="small">
                  <Stop />
                </IconButton>
                
                <IconButton 
                  onClick={togglePlay} 
                  color="primary" 
                  sx={{ 
                    mx: 1,
                    backgroundColor: alpha(theme.palette.primary.main, 0.1),
                    '&:hover': {
                      backgroundColor: alpha(theme.palette.primary.main, 0.2)
                    },
                    transition: 'all 0.2s ease'
                  }}
                >
                  {isPlaying ? <Pause /> : <PlayArrow />}
                </IconButton>
                
                <IconButton 
                  onClick={() => {
                    if (!audioRef.current) return;
                    audioRef.current.currentTime = 0;
                    setCurrentTime(0);
                  }} 
                  size="small"
                >
                  <Repeat />
                </IconButton>
              </Box>
              
              {/* 進度條 */}
              <Box sx={{ flexGrow: 1, mx: 2 }}>
                <Slider
                  value={currentTime}
                  max={duration}
                  onChange={handleSeek}
                  aria-label="播放進度"
                  size="small"
                  sx={{
                    color: theme.palette.primary.main,
                    '& .MuiSlider-thumb': {
                      transition: 'transform 0.1s ease',
                      '&:hover': {
                        transform: 'scale(1.3)'
                      }
                    }
                  }}
                />
              </Box>
              
              {/* 音量控制 */}
              {!isMobile && (
                <Box sx={{ display: 'flex', alignItems: 'center', minWidth: 100 }}>
                  <IconButton onClick={toggleMute} size="small">
                    {isMuted ? <VolumeOff /> : <VolumeUp />}
                  </IconButton>
                  <Slider
                    value={isMuted ? 0 : volume}
                    max={1}
                    min={0}
                    step={0.01}
                    onChange={handleVolumeChange}
                    aria-label="音量"
                    size="small"
                    sx={{ ml: 1, maxWidth: 80 }}
                  />
                </Box>
              )}
              
              {/* 縮放控制 */}
              {(showWaveform || showScoreView) && (
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Tooltip title="縮小">
                    <IconButton 
                      size="small" 
                      onClick={() => handleZoomChange(zoom - 10)}
                      disabled={zoom <= 50}
                    >
                      <ZoomOut fontSize="small" />
                    </IconButton>
                  </Tooltip>
                  
                  <Typography variant="caption" sx={{ mx: 0.5 }}>
                    {zoom}%
                  </Typography>
                  
                  <Tooltip title="放大">
                    <IconButton 
                      size="small" 
                      onClick={() => handleZoomChange(zoom + 10)}
                      disabled={zoom >= 200}
                    >
                      <ZoomIn fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
              )}
            </Box>
          </>
        )}
      </Box>
    </Paper>
  );
};

export default MusicVisualizer; 