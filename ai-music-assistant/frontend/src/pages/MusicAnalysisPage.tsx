import {
  BarChart,
  Circle,
  Download,
  Equalizer,
  LibraryMusic,
  Piano,
  Upload
} from '@mui/icons-material';
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Container,
  Divider,
  Grid,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Paper,
  Typography
} from '@mui/material';
import axios from 'axios';
import React, { useState } from 'react';
import Logger from '../services/LoggingService';

// 確保能夠識別 AudioContext 類型
declare global {
  interface Window {
    AudioContext: typeof AudioContext;
    webkitAudioContext: typeof AudioContext;
  }
}

// 實際的 API 服務
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const analyzeMusic = async (audioBase64: string): Promise<any> => {
  try {
    Logger.info('發送音樂分析請求', { tags: ['API'] });
    const response = await axios.post('/api/analyze-music', {
      audio_data: audioBase64,
    }, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    Logger.debug('音樂分析響應', response.data, { tags: ['API'] });
    return response.data;
  } catch (error) {
    Logger.error('音樂分析請求失敗', error, { tags: ['API'] });
    throw error;
  }
};

// 開發模式使用的模擬數據
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const mockAnalyzeMusic = async (audioBase64: string): Promise<any> => {
  // 模擬 API 延遲
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  return {
    success: true,
    analysis: {
      key: 'C',
      tempo: 120,
      time_signature: '4/4',
      chord_progression: {
        chords: ['C', 'Am', 'F', 'G'],
        durations: [1.0, 1.0, 1.0, 1.0]
      },
      structure: {
        verse: [1, 5, 9, 13],
        chorus: [17, 21, 25, 29]
      },
      harmony_issues: [
        '在小節7-8可能存在不自然的和聲進行',
        '副歌部分的和聲可以更豐富'
      ],
      suggestions: [
        '考慮在副歌部分增加更強的力度對比',
        '可嘗試使用更豐富的和弦延伸音',
        '音域較窄，考慮擴展音域以增加音樂的表現力'
      ]
    }
  };
};

const MusicAnalysisPage: React.FC = () => {
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [result, setResult] = useState<any>(null);
  const isDevelopment = process.env.NODE_ENV === 'development';
  
  // 處理文件選擇
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (!file.type.includes('audio')) {
        setError('請上傳音頻文件 (MP3, WAV, MIDI 等)');
        return;
      }
      
      setError('');
      setAudioFile(file);
      
      // 創建音頻預覽URL
      const url = URL.createObjectURL(file);
      setAudioUrl(url);
      
      // 如果已經有結果，重置
      if (result) {
        setResult(null);
      }
      
      Logger.info('用戶選擇了音頻文件', { fileName: file.name, fileSize: file.size }, { tags: ['UI'] });
    }
  };
  
  // 分析音樂
  const handleAnalyzeMusic = async () => {
    if (!audioFile) {
      setError('請先上傳音樂文件');
      return;
    }
    
    setError('');
    setLoading(true);
    Logger.info('開始分析音樂', { fileName: audioFile.name }, { tags: ['ANALYSIS'] });
    
    try {
      // 將文件轉換為 base64
      const reader = new FileReader();
      
      reader.onload = async (e) => {
        try {
          const base64data = e.target?.result as string;
          // 開發模式使用模擬數據，生產模式調用實際API
          const response = isDevelopment 
            ? await mockAnalyzeMusic(base64data)
            : await analyzeMusic(base64data);
            
          setResult(response);
          Logger.info('音樂分析完成', null, { tags: ['ANALYSIS'] });
        } catch (err) {
          Logger.error('分析音樂時出錯', err, { tags: ['ANALYSIS'] });
          setError('分析音樂時發生錯誤');
        } finally {
          setLoading(false);
        }
      };
      
      reader.onerror = () => {
        Logger.error('讀取文件時出錯', null, { tags: ['FILE'] });
        setError('讀取文件時發生錯誤');
        setLoading(false);
      };
      
      reader.readAsDataURL(audioFile);
      
    } catch (err) {
      Logger.error('處理文件時出錯', err, { tags: ['FILE'] });
      setError('處理文件時發生錯誤');
      setLoading(false);
    }
  };
  
  // 重置
  const handleReset = () => {
    setAudioFile(null);
    setAudioUrl(null);
    setResult(null);
    setError('');
    Logger.debug('重置分析頁面狀態', null, { tags: ['UI'] });
  };
  
  // 匯出分析結果
  const handleExportAnalysis = () => {
    if (!result || !result.analysis) return;
    
    try {
      const analysisData = JSON.stringify(result.analysis, null, 2);
      const blob = new Blob([analysisData], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      
      const a = document.createElement('a');
      a.href = url;
      a.download = `music-analysis-${new Date().getTime()}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      Logger.info('匯出分析結果', null, { tags: ['EXPORT'] });
    } catch (err) {
      Logger.error('匯出分析結果失敗', err, { tags: ['EXPORT'] });
      setError('匯出分析結果失敗');
    }
  };
  
  return (
    <Container maxWidth="lg">
      <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 4 }}>
        音樂分析
      </Typography>
      
      <Grid container spacing={4}>
        <Grid item xs={12} md={5}>
          {/* 上傳區域 */}
          <Paper elevation={3} sx={{ p: 3, mb: 4, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              上傳音樂文件
            </Typography>
            
            <Box sx={{ 
              display: 'flex', 
              flexDirection: 'column', 
              alignItems: 'center', 
              justifyContent: 'center',
              border: '2px dashed #ccc',
              borderRadius: 2,
              p: 3,
              mb: 3,
              minHeight: 200,
              bgcolor: 'background.default'
            }}>
              {audioFile ? (
                <Box sx={{ width: '100%', textAlign: 'center' }}>
                  <Typography variant="body1" gutterBottom>
                    {audioFile.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {(audioFile.size / 1024 / 1024).toFixed(2)} MB
                  </Typography>
                  
                  {audioUrl && audioFile.type.includes('audio') && !audioFile.type.includes('midi') && (
                    <Box sx={{ my: 2 }}>
                      <audio controls src={audioUrl} style={{ width: '100%' }} />
                    </Box>
                  )}
                  
                  <Button 
                    variant="outlined" 
                    color="secondary" 
                    onClick={handleReset}
                    sx={{ mt: 1 }}
                  >
                    重新選擇
                  </Button>
                </Box>
              ) : (
                <>
                  <Upload sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="body1" gutterBottom align="center">
                    拖放音樂文件到此處，或點擊選擇
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom align="center">
                    支持 MP3, WAV, MIDI 等音樂格式
                  </Typography>
                  <Button
                    variant="contained"
                    component="label"
                    sx={{ mt: 2 }}
                  >
                    選擇文件
                    <input
                      type="file"
                      hidden
                      accept="audio/*,audio/midi"
                      onChange={handleFileChange}
                    />
                  </Button>
                </>
              )}
            </Box>
            
            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}
            
            <Button
              fullWidth
              variant="contained"
              color="primary"
              size="large"
              onClick={handleAnalyzeMusic}
              disabled={!audioFile || loading}
              startIcon={loading ? <CircularProgress size={20} /> : <BarChart />}
            >
              {loading ? '分析中...' : '分析音樂'}
            </Button>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={7}>
          {/* 分析結果區域 */}
          <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                分析結果
              </Typography>
              {result && (
                <Button 
                  variant="outlined" 
                  size="small" 
                  startIcon={<Download />}
                  onClick={handleExportAnalysis}
                >
                  匯出分析
                </Button>
              )}
            </Box>
            
            {!result && !loading ? (
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '80%', color: 'text.secondary' }}>
                <Typography variant="body1" align="center">
                  上傳音樂文件後，點擊「分析音樂」按鈕開始分析
                </Typography>
              </Box>
            ) : loading ? (
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '80%', flexDirection: 'column' }}>
                <CircularProgress size={60} sx={{ mb: 2 }} />
                <Typography variant="body1">
                  正在分析您的音樂...
                </Typography>
              </Box>
            ) : result ? (
              <Grid container spacing={3}>
                {/* 基本分析信息 */}
                <Grid item xs={12}>
                  <Box sx={{ mb: 2 }}>
                    <Grid container spacing={2}>
                      <Grid item xs={6} sm={3}>
                        <Paper elevation={0} sx={{ p: 2, bgcolor: 'background.default', height: '100%' }}>
                          <Typography variant="body2" color="text.secondary">調性</Typography>
                          <Typography variant="h6">{result.analysis.key}</Typography>
                        </Paper>
                      </Grid>
                      <Grid item xs={6} sm={3}>
                        <Paper elevation={0} sx={{ p: 2, bgcolor: 'background.default', height: '100%' }}>
                          <Typography variant="body2" color="text.secondary">速度</Typography>
                          <Typography variant="h6">{result.analysis.tempo} BPM</Typography>
                        </Paper>
                      </Grid>
                      <Grid item xs={6} sm={3}>
                        <Paper elevation={0} sx={{ p: 2, bgcolor: 'background.default', height: '100%' }}>
                          <Typography variant="body2" color="text.secondary">拍號</Typography>
                          <Typography variant="h6">{result.analysis.time_signature}</Typography>
                        </Paper>
                      </Grid>
                      <Grid item xs={6} sm={3}>
                        <Paper elevation={0} sx={{ p: 2, bgcolor: 'background.default', height: '100%' }}>
                          <Typography variant="body2" color="text.secondary">小節數</Typography>
                          <Typography variant="h6">
                            {(Object.values(result.analysis.structure)
                              .flat()
                              .slice(-1)[0] || 0).toString()}
                          </Typography>
                        </Paper>
                      </Grid>
                    </Grid>
                  </Box>
                </Grid>
                
                {/* 和弦進行 */}
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle1" gutterBottom>
                    <LibraryMusic sx={{ verticalAlign: 'middle', mr: 1 }} />
                    和弦進行
                  </Typography>
                  <Paper elevation={0} sx={{ p: 2, bgcolor: 'background.default' }}>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {result.analysis.chord_progression.chords.map((chord: string, index: number) => (
                        <Chip 
                          key={index} 
                          label={chord} 
                          variant="outlined" 
                          color={index % 4 === 0 ? "primary" : "default"}
                        />
                      ))}
                    </Box>
                  </Paper>
                </Grid>
                
                {/* 結構分析 */}
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle1" gutterBottom>
                    <Equalizer sx={{ verticalAlign: 'middle', mr: 1 }} />
                    結構分析
                  </Typography>
                  <Paper elevation={0} sx={{ p: 2, bgcolor: 'background.default' }}>
                    <List dense>
                      {Object.entries(result.analysis.structure).map(([section, measures]: [string, any]) => (
                        <ListItem key={section}>
                          <ListItemText 
                            primary={section.charAt(0).toUpperCase() + section.slice(1)}
                            secondary={`小節 ${measures[0]}-${measures[1] || measures[0]}`}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Paper>
                </Grid>
                
                <Grid item xs={12}>
                  <Divider sx={{ my: 1 }} />
                </Grid>
                
                {/* 改進建議 */}
                <Grid item xs={12}>
                  <Typography variant="subtitle1" gutterBottom>
                    <Piano sx={{ verticalAlign: 'middle', mr: 1 }} />
                    音樂改進建議
                  </Typography>
                  
                  {result.analysis.harmony_issues && result.analysis.harmony_issues.length > 0 && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="error" gutterBottom>
                        和聲問題:
                      </Typography>
                      <List dense>
                        {result.analysis.harmony_issues.map((issue: string, index: number) => (
                          <ListItem key={index}>
                            <ListItemIcon sx={{ minWidth: 30 }}>
                              <Circle sx={{ fontSize: 8 }} />
                            </ListItemIcon>
                            <ListItemText primary={issue} />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}
                  
                  {result.analysis.suggestions && result.analysis.suggestions.length > 0 && (
                    <Box>
                      <Typography variant="body2" color="primary" gutterBottom>
                        改進建議:
                      </Typography>
                      <List dense>
                        {result.analysis.suggestions.map((suggestion: string, index: number) => (
                          <ListItem key={index}>
                            <ListItemIcon sx={{ minWidth: 30 }}>
                              <Circle sx={{ fontSize: 8 }} />
                            </ListItemIcon>
                            <ListItemText primary={suggestion} />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}
                </Grid>
              </Grid>
            ) : null}
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default MusicAnalysisPage; 