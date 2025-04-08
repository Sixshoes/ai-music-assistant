import {
  CloudUpload,
  Mic,
  MusicNote,
  PlayArrow,
  RestartAlt,
  Save,
  Stop
} from '@mui/icons-material';
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Container,
  FormControl,
  Grid,
  IconButton,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Slider,
  Stack,
  Tooltip,
  Typography
} from '@mui/material';
import React, { useEffect, useRef, useState } from 'react';

// 確保能夠識別 AudioContext 和 MediaRecorder 類型
declare global {
  interface Window {
    AudioContext: typeof AudioContext;
    webkitAudioContext: typeof AudioContext;
  }
}

// 模擬 API 服務
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const mockProcessMelody = async (audioUrl: string, params: any): Promise<any> => {
  // 模擬 API 延遲
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  // 使用這些參數來模擬不同的響應
  console.log(`處理音頻數據，參數:`, params);
  
  return {
    success: true,
    midi_data: 'mock_midi_data_base64',
    audio_data: 'mock_audio_data_base64',
    sheet_music: 'mock_sheet_music_data',
    analysis: {
      key: params.key || 'C',
      tempo: params.tempo || 120,
      chord_progression: ['C', 'Am', 'F', 'G'],
      genre: params.genre || 'pop'
    }
  };
};

const MelodyToArrangementPage: React.FC = () => {
  // 錄音狀態
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [recordedAudio, setRecordedAudio] = useState<string | null>(null);
  const [recordingTime, setRecordingTime] = useState<number>(0);
  const [audioContext, setAudioContext] = useState<AudioContext | null>(null);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const audioChunks = useRef<Blob[]>([]);
  const recordingTimer = useRef<NodeJS.Timeout | null>(null);
  
  // 處理狀態
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string>('');
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  
  // 音樂參數設置
  const [tempo, setTempo] = useState<number>(120);
  const [key, setKey] = useState<string>('C');
  const [genre, setGenre] = useState<string>('pop');
  const [selectedInstruments, setSelectedInstruments] = useState<string[]>(['piano', 'strings', 'bass', 'drums']);
  
  // 初始化音頻上下文
  useEffect(() => {
    const initAudioContext = () => {
      try {
        const audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
        setAudioContext(audioCtx);
      } catch (e) {
        console.error('無法創建音頻上下文', e);
        setError('您的瀏覽器不支持錄音功能，請嘗試使用最新版 Chrome 或 Firefox');
      }
    };
    
    initAudioContext();
    
    return () => {
      if (audioContext) {
        audioContext.close();
      }
      if (recordingTimer.current) {
        clearInterval(recordingTimer.current);
      }
    };
  }, []);
  
  // 開始錄音
  const startRecording = async () => {
    try {
      setError('');
      audioChunks.current = [];
      
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          audioChunks.current.push(e.data);
        }
      };
      
      recorder.onstop = () => {
        const audioBlob = new Blob(audioChunks.current, { type: 'audio/wav' });
        const audioUrl = URL.createObjectURL(audioBlob);
        setRecordedAudio(audioUrl);
        
        // 將 Blob 轉換為 base64
        const reader = new FileReader();
        reader.readAsDataURL(audioBlob);
        reader.onloadend = () => {
          const base64data = reader.result as string;
          // 儲存錄音的 base64 數據以便後續處理
          setRecordedAudio(base64data);
          console.log('錄音完成，準備好上傳');
        };
      };
      
      recorder.start();
      setMediaRecorder(recorder);
      setIsRecording(true);
      setRecordingTime(0);
      
      // 設置計時器更新錄音時間
      recordingTimer.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
      
    } catch (err) {
      console.error('錄音失敗', err);
      setError('無法啟動錄音，請確認已授予麥克風權限');
    }
  };
  
  // 停止錄音
  const stopRecording = () => {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
      
      // 停止所有音軌
      mediaRecorder.stream.getTracks().forEach(track => track.stop());
      
      setIsRecording(false);
      if (recordingTimer.current) {
        clearInterval(recordingTimer.current);
      }
    }
  };
  
  // 上傳音頻文件
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setError('');
      const reader = new FileReader();
      reader.onload = () => {
        setRecordedAudio(reader.result as string);
      };
      reader.onerror = () => {
        setError('文件讀取失敗');
      };
      reader.readAsDataURL(file);
    }
  };
  
  // 處理旋律
  const handleProcessMelody = async () => {
    if (!recordedAudio) {
      setError('請先錄製或上傳旋律');
      return;
    }
    
    setError('');
    setLoading(true);
    
    try {
      const params = {
        tempo,
        key,
        genre,
        instruments: selectedInstruments
      };
      
      // 使用實際的錄音數據和參數調用 API
      const response = await mockProcessMelody(recordedAudio, params);
      setResult(response);
      
    } catch (err) {
      setError('處理旋律時發生錯誤');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  // 播放/停止音頻
  const handlePlayback = () => {
    if (isPlaying) {
      // 停止播放邏輯
      setIsPlaying(false);
    } else if (recordedAudio) {
      // 播放錄音
      const audio = new Audio(recordedAudio);
      audio.onended = () => setIsPlaying(false);
      audio.play();
      setIsPlaying(true);
    }
  };
  
  // 處理儀器選擇
  const handleInstrumentToggle = (instrument: string) => {
    if (selectedInstruments.includes(instrument)) {
      setSelectedInstruments(selectedInstruments.filter(i => i !== instrument));
    } else {
      setSelectedInstruments([...selectedInstruments, instrument]);
    }
  };
  
  // 下載生成的文件
  const handleDownload = (type: 'midi' | 'audio' | 'sheet') => {
    if (result) {
      // 實際下載邏輯
      console.log(`下載 ${type} 文件`);
    }
  };
  
  // 重置
  const handleReset = () => {
    setRecordedAudio(null);
    setResult(null);
    setError('');
  };
  
  // 格式化時間
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };
  
  const instruments = [
    { value: 'piano', label: '鋼琴' },
    { value: 'guitar', label: '吉他' },
    { value: 'strings', label: '弦樂' },
    { value: 'drums', label: '鼓組' },
    { value: 'bass', label: '貝斯' },
    { value: 'synth', label: '合成器' }
  ];
  
  return (
    <Container maxWidth="lg">
      <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 4 }}>
        旋律到編曲
      </Typography>
      
      <Grid container spacing={4}>
        <Grid item xs={12} md={6}>
          {/* 錄音區域 */}
          <Paper elevation={3} sx={{ p: 3, mb: 4, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              錄製或上傳旋律
            </Typography>
            
            <Box sx={{ mb: 3, display: 'flex', justifyContent: 'center', alignItems: 'center', flexDirection: 'column' }}>
              {isRecording ? (
                <Box sx={{ position: 'relative', width: 120, height: 120, mb: 2 }}>
                  <CircularProgress size={120} variant="determinate" value={(recordingTime / 30) * 100} />
                  <Box
                    sx={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      bottom: 0,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <Typography variant="h5" color="primary">
                      {formatTime(recordingTime)}
                    </Typography>
                  </Box>
                </Box>
              ) : (
                recordedAudio ? (
                  <Box sx={{ mb: 2 }}>
                    <IconButton
                      color="primary"
                      size="large"
                      onClick={handlePlayback}
                      sx={{ border: '2px solid', borderRadius: '50%', p: 2, mb: 1 }}
                    >
                      {isPlaying ? <Stop fontSize="large" /> : <PlayArrow fontSize="large" />}
                    </IconButton>
                    <Typography variant="body2" align="center">
                      {isPlaying ? '點擊停止' : '點擊播放'}
                    </Typography>
                  </Box>
                ) : (
                  <IconButton
                    color="primary"
                    size="large"
                    onClick={startRecording}
                    sx={{ border: '2px solid', borderRadius: '50%', p: 2, mb: 1 }}
                  >
                    <Mic fontSize="large" />
                  </IconButton>
                )
              )}
              
              {isRecording ? (
                <Button
                  variant="contained"
                  color="secondary"
                  startIcon={<Stop />}
                  onClick={stopRecording}
                >
                  停止錄音
                </Button>
              ) : (
                <Stack direction="row" spacing={2}>
                  {recordedAudio && (
                    <Button
                      variant="outlined"
                      startIcon={<RestartAlt />}
                      onClick={handleReset}
                    >
                      重新開始
                    </Button>
                  )}
                  
                  {!recordedAudio && (
                    <Button
                      variant="outlined"
                      component="label"
                      startIcon={<CloudUpload />}
                    >
                      上傳音頻
                      <input
                        type="file"
                        hidden
                        accept="audio/*"
                        onChange={handleFileUpload}
                      />
                    </Button>
                  )}
                </Stack>
              )}
            </Box>
            
            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}
            
            {/* 參數設置 */}
            <Typography variant="subtitle1" gutterBottom>
              編曲參數
            </Typography>
            
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>調性</InputLabel>
                  <Select
                    value={key}
                    label="調性"
                    onChange={(e) => setKey(e.target.value)}
                    disabled={loading}
                  >
                    <MenuItem value="C">C 大調</MenuItem>
                    <MenuItem value="G">G 大調</MenuItem>
                    <MenuItem value="D">D 大調</MenuItem>
                    <MenuItem value="A">A 大調</MenuItem>
                    <MenuItem value="Am">A 小調</MenuItem>
                    <MenuItem value="Em">E 小調</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>風格</InputLabel>
                  <Select
                    value={genre}
                    label="風格"
                    onChange={(e) => setGenre(e.target.value)}
                    disabled={loading}
                  >
                    <MenuItem value="pop">流行</MenuItem>
                    <MenuItem value="jazz">爵士</MenuItem>
                    <MenuItem value="classical">古典</MenuItem>
                    <MenuItem value="rock">搖滾</MenuItem>
                    <MenuItem value="electronic">電子</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12}>
                <Typography gutterBottom>速度 (BPM)</Typography>
                <Slider
                  value={tempo}
                  min={60}
                  max={180}
                  step={1}
                  marks={[
                    { value: 60, label: '60' },
                    { value: 120, label: '120' },
                    { value: 180, label: '180' }
                  ]}
                  valueLabelDisplay="auto"
                  onChange={(_, newValue) => setTempo(newValue as number)}
                  disabled={loading}
                />
              </Grid>
            </Grid>
            
            <Typography variant="subtitle1" gutterBottom>
              選擇樂器
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap sx={{ mb: 3 }}>
              {instruments.map(instrument => (
                <Chip
                  key={instrument.value}
                  label={instrument.label}
                  color={selectedInstruments.includes(instrument.value) ? "primary" : "default"}
                  onClick={() => handleInstrumentToggle(instrument.value)}
                  sx={{ mb: 1 }}
                  disabled={loading}
                />
              ))}
            </Stack>
            
            <Button
              fullWidth
              variant="contained"
              color="primary"
              size="large"
              onClick={handleProcessMelody}
              disabled={!recordedAudio || loading}
              startIcon={loading ? <CircularProgress size={20} /> : <MusicNote />}
            >
              {loading ? '處理中...' : '生成編曲'}
            </Button>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={6}>
          {/* 結果顯示區域 */}
          <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              生成結果
            </Typography>
            
            {!result && !loading ? (
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '80%', color: 'text.secondary' }}>
                <Typography variant="body1" align="center">
                  錄製或上傳旋律後，點擊「生成編曲」按鈕開始處理
                </Typography>
              </Box>
            ) : loading ? (
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '80%', flexDirection: 'column' }}>
                <CircularProgress size={60} sx={{ mb: 2 }} />
                <Typography variant="body1">
                  正在處理您的旋律...
                </Typography>
              </Box>
            ) : result ? (
              <>
                <Box sx={{ mb: 3, p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    音樂分析
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">調性</Typography>
                      <Typography variant="body1">{result.analysis.key}</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">速度</Typography>
                      <Typography variant="body1">{result.analysis.tempo} BPM</Typography>
                    </Grid>
                    <Grid item xs={12}>
                      <Typography variant="body2" color="text.secondary">和弦進行</Typography>
                      <Typography variant="body1">{result.analysis.chord_progression.join(' - ')}</Typography>
                    </Grid>
                  </Grid>
                </Box>
                
                <Box sx={{ bgcolor: 'background.paper', p: 2, borderRadius: 1, mb: 3 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    樂譜預覽
                  </Typography>
                  <Box
                    sx={{
                      height: 200,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      border: '1px dashed grey',
                      bgcolor: 'background.default'
                    }}
                  >
                    <Typography color="text.secondary">
                      樂譜預覽 (需整合樂譜渲染庫)
                    </Typography>
                  </Box>
                </Box>
                
                <Stack direction="row" spacing={2} sx={{ justifyContent: 'space-between', flexWrap: 'wrap' }}>
                  <Button
                    variant="contained"
                    startIcon={isPlaying ? <Stop /> : <PlayArrow />}
                    onClick={handlePlayback}
                  >
                    {isPlaying ? '停止' : '播放'}
                  </Button>
                  
                  <Stack direction="row" spacing={1}>
                    <Tooltip title="下載 MIDI 文件">
                      <Button
                        variant="outlined"
                        startIcon={<Save />}
                        onClick={() => handleDownload('midi')}
                      >
                        MIDI
                      </Button>
                    </Tooltip>
                    
                    <Tooltip title="下載 MP3 文件">
                      <Button
                        variant="outlined"
                        startIcon={<Save />}
                        onClick={() => handleDownload('audio')}
                      >
                        MP3
                      </Button>
                    </Tooltip>
                    
                    <Tooltip title="下載樂譜">
                      <Button
                        variant="outlined"
                        startIcon={<MusicNote />}
                        onClick={() => handleDownload('sheet')}
                      >
                        樂譜
                      </Button>
                    </Tooltip>
                  </Stack>
                </Stack>
              </>
            ) : null}
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default MelodyToArrangementPage; 