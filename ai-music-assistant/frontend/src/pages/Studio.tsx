import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Box, 
  Tabs, 
  Tab, 
  Typography, 
  Paper, 
  CircularProgress,
  LinearProgress,
  Grid
} from '@mui/material';
import { useLocation } from 'react-router-dom';
import TextPrompt from '../components/TextPrompt';
import MusicPlayer from '../components/MusicPlayer';
import AudioRecorder from '../components/AudioRecorder';
import MusicEditor from '../components/MusicEditor';
import TheoryAnalyzer from '../components/TheoryAnalyzer';

// 將在下一步實現這些組件
// import MusicEditor from '../components/MusicEditor';
// import TheoryAnalyzer from '../components/TheoryAnalyzer';

const Studio = () => {
  const location = useLocation();
  const [mode, setMode] = useState<string>('text'); // 'text', 'melody', 'analysis'
  const [loading, setLoading] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // 從 URL 參數中讀取模式
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const modeParam = params.get('mode');
    if (modeParam && ['text', 'melody', 'analysis'].includes(modeParam)) {
      setMode(modeParam);
    }
  }, [location]);

  // 模擬創作過程
  const simulateCreation = (prompt: string) => {
    setLoading(true);
    setProgress(0);
    setError(null);

    // 模擬進度更新
    const interval = setInterval(() => {
      setProgress((prevProgress) => {
        const newProgress = prevProgress + 10;
        if (newProgress >= 100) {
          clearInterval(interval);
          setLoading(false);
          // 模擬創作結果
          setResult({
            musicUrl: '/path/to/generated/music.mp3',
            sheetMusicUrl: '/path/to/sheet/music.png',
            analysis: {
              key: 'C Major',
              tempo: 120,
              chords: ['C', 'G', 'Am', 'F'],
              structure: 'Verse - Chorus - Verse - Chorus - Bridge - Chorus'
            }
          });
          return 100;
        }
        return newProgress;
      });
    }, 500);

    // 模擬API調用
    setTimeout(() => {
      clearInterval(interval);
      setLoading(false);
      setProgress(100);
    }, 5000);
  };

  // 處理錯誤
  const handleError = (message: string) => {
    setError(message);
    setLoading(false);
  };

  // 處理文字提示提交
  const handleTextPromptSubmit = (prompt: string) => {
    console.log('處理文字提示:', prompt);
    simulateCreation(prompt);
  };

  // 處理音頻錄製完成
  const handleRecordingComplete = (audioBlob: Blob) => {
    console.log('處理錄音完成:', audioBlob);
    // 這裡會上傳音頻並處理旋律編曲
    simulateCreation('從錄製的旋律創作');
  };

  // 處理分析完成
  const handleAnalysisComplete = (analysis: any) => {
    console.log('分析完成:', analysis);
    // 在實際應用中，可以更新結果或執行其他操作
  };

  // 處理樂譜變更
  const handleScoreChange = (score: string) => {
    console.log('樂譜變更:', score);
    // 在實際應用中，可以保存樂譜或執行其他操作
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 2 }}>
      <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
        <Tabs
          value={mode}
          onChange={(e, newValue) => setMode(newValue)}
          indicatorColor="primary"
          textColor="primary"
          centered
        >
          <Tab label="文字轉音樂" value="text" />
          <Tab label="旋律編曲" value="melody" />
          <Tab label="音樂分析" value="analysis" />
        </Tabs>
      </Paper>

      <Box sx={{ mb: 4 }}>
        {mode === 'text' && (
          <Box>
            <Typography variant="h5" gutterBottom>
              透過文字描述創作音樂
            </Typography>
            <Typography variant="body1" sx={{ mb: 2 }}>
              描述您想要的音樂風格、情緒、節奏或樂器。越詳細的描述將產生越符合您期望的結果。
            </Typography>
            <TextPrompt onSubmit={handleTextPromptSubmit} />
          </Box>
        )}

        {mode === 'melody' && (
          <Box>
            <Typography variant="h5" gutterBottom>
              旋律編曲
            </Typography>
            <Typography variant="body1" sx={{ mb: 2 }}>
              錄製一段簡單的旋律，我們將為您創作完整的編曲，或使用編輯器直接創作。
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <AudioRecorder onRecordingComplete={handleRecordingComplete} />
              </Grid>
              <Grid item xs={12} md={6}>
                <MusicEditor onScoreChange={handleScoreChange} />
              </Grid>
            </Grid>
          </Box>
        )}

        {mode === 'analysis' && (
          <Box>
            <Typography variant="h5" gutterBottom>
              音樂理論分析
            </Typography>
            <Typography variant="body1" sx={{ mb: 2 }}>
              上傳或創作音樂，獲取專業的樂理分析與建議。
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <TextPrompt 
                  onSubmit={handleTextPromptSubmit} 
                  placeholder="描述您想要分析的音樂類型或上傳音樂文件" 
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TheoryAnalyzer onAnalysisComplete={handleAnalysisComplete} />
              </Grid>
            </Grid>
          </Box>
        )}
      </Box>

      {loading && (
        <Box sx={{ width: '100%', mt: 2, mb: 4 }}>
          <Typography variant="body2" sx={{ mb: 1 }}>
            正在創作中... {progress}%
          </Typography>
          <LinearProgress 
            variant="determinate" 
            value={progress} 
            sx={{ height: 10, borderRadius: 5 }} 
          />
        </Box>
      )}

      {error && (
        <Paper elevation={1} sx={{ p: 2, mb: 3, bgcolor: '#ffebee' }}>
          <Typography color="error">{error}</Typography>
        </Paper>
      )}

      {result && (
        <Grid container spacing={3} sx={{ mt: 2 }}>
          <Grid item xs={12} md={6}>
            <Paper elevation={2} sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                生成的音樂
              </Typography>
              <MusicPlayer audioUrl={result.musicUrl} title="生成的音樂作品" artist="AI 音樂助手" />
            </Paper>
          </Grid>
          <Grid item xs={12} md={6}>
            <Paper elevation={2} sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                樂譜 & 分析
              </Typography>
              {result.sheetMusicUrl && (
                <Box sx={{ mb: 2, textAlign: 'center' }}>
                  <img 
                    src={result.sheetMusicUrl} 
                    alt="Sheet Music" 
                    style={{ maxWidth: '100%', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }} 
                  />
                </Box>
              )}
              {result.analysis && (
                <Box>
                  <Typography variant="subtitle1">音樂分析：</Typography>
                  <Typography>調性: {result.analysis.key}</Typography>
                  <Typography>速度: {result.analysis.tempo} BPM</Typography>
                  <Typography>和弦進行: {result.analysis.chords.join(' - ')}</Typography>
                  <Typography>結構: {result.analysis.structure}</Typography>
                </Box>
              )}
            </Paper>
          </Grid>
        </Grid>
      )}
    </Container>
  );
};

export default Studio; 