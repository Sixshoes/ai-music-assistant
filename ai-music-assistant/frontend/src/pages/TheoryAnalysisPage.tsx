import {
    Assignment,
    CloudUpload,
    LibraryMusic,
    MusicNote
} from '@mui/icons-material';
import {
    Alert,
    Box,
    Button,
    CircularProgress,
    Container,
    Divider,
    Grid,
    Paper,
    Tab,
    Tabs,
    Typography,
} from '@mui/material';
import React, { useState } from 'react';
import MusicPlayer from '../components/MusicPlayer';
import TheoryAnalyzer from '../components/TheoryAnalyzer';
import Logger from '../services/LoggingService';

// 筆記類型定義
interface Note {
  pitch: number;
  duration: number;
  startTime?: number;
  velocity?: number;
}

const TheoryAnalysisPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<number>(0);
  const [midiFile, setMidiFile] = useState<File | null>(null);
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [notes, setNotes] = useState<Note[]>([]);
  const [uploading, setUploading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  // 處理文件上傳
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setError('');

    if (file.type.includes('audio')) {
      setAudioFile(file);
      const url = URL.createObjectURL(file);
      setAudioUrl(url);
      
      // 如果是MIDI文件，也設置MIDI文件
      if (file.type.includes('midi')) {
        setMidiFile(file);
        // 提取MIDI文件中的音符數據
        extractMidiNotes(file);
      } else {
        // 音頻文件需要先轉換為MIDI
        setMidiFile(null);
        setNotes([]);
        // 這裡應該調用音頻轉MIDI的API
      }
      
      Logger.info('上傳音樂文件', { name: file.name, type: file.type, size: file.size });
    } else {
      setError('請上傳有效的音頻或MIDI文件');
    }
  };

  // 從MIDI文件提取音符
  const extractMidiNotes = async (file: File) => {
    setUploading(true);
    
    try {
      // 實際應用中這裡應該調用API來解析MIDI文件
      // 模擬解析過程
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 生成模擬音符數據
      const mockNotes: Note[] = [];
      for (let i = 0; i < 20; i++) {
        mockNotes.push({
          pitch: 60 + Math.floor(Math.random() * 12),
          duration: 0.25 + Math.random() * 0.75,
          startTime: i * 0.5,
          velocity: 64 + Math.floor(Math.random() * 32)
        });
      }
      
      setNotes(mockNotes);
      Logger.info('從MIDI文件提取了音符數據', { noteCount: mockNotes.length });
    } catch (error) {
      console.error('解析MIDI文件失敗:', error);
      setError('無法讀取MIDI文件中的音符數據');
    } finally {
      setUploading(false);
    }
  };

  // 處理分析完成
  const handleAnalysisComplete = (analysis: any) => {
    Logger.info('音樂理論分析完成', { key: analysis.key, score: analysis.score });
  };

  // 處理標籤變更
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  // 重置上傳
  const handleReset = () => {
    setAudioFile(null);
    setMidiFile(null);
    setAudioUrl(null);
    setNotes([]);
    setError('');
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        音樂理論分析
      </Typography>
      
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={handleTabChange}>
          <Tab icon={<CloudUpload />} iconPosition="start" label="上傳文件" />
          <Tab icon={<Assignment />} iconPosition="start" label="分析結果" disabled={!midiFile && notes.length === 0} />
        </Tabs>
      </Box>
      
      {activeTab === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" gutterBottom>
                上傳音樂文件
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
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
                    
                    {uploading && (
                      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                        <CircularProgress size={24} sx={{ mr: 1 }} />
                        <Typography variant="body2">處理中...</Typography>
                      </Box>
                    )}
                  </Box>
                ) : (
                  <>
                    <LibraryMusic sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
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
                        onChange={handleFileUpload}
                      />
                    </Button>
                  </>
                )}
              </Box>
              
              {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}
              
              <Button
                fullWidth
                variant="contained"
                color="primary"
                size="large"
                startIcon={<MusicNote />}
                disabled={!midiFile && notes.length === 0}
                onClick={() => setActiveTab(1)}
              >
                進行音樂理論分析
              </Button>
            </Paper>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" gutterBottom>
                分析說明
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              <Typography variant="body1" paragraph>
                音樂理論分析器將對您的音樂作品進行深度分析，包括：
              </Typography>
              
              <Box component="ul" sx={{ pl: 2 }}>
                <Box component="li" sx={{ mb: 1 }}>
                  <Typography variant="body1">
                    <strong>調性和和弦分析</strong> - 識別作品的調性和和弦進行
                  </Typography>
                </Box>
                <Box component="li" sx={{ mb: 1 }}>
                  <Typography variant="body1">
                    <strong>旋律特徵分析</strong> - 評估旋律的音程、範圍和節奏特點
                  </Typography>
                </Box>
                <Box component="li" sx={{ mb: 1 }}>
                  <Typography variant="body1">
                    <strong>和聲檢測</strong> - 檢查不協和和弦、平行五度等常見和聲問題
                  </Typography>
                </Box>
                <Box component="li" sx={{ mb: 1 }}>
                  <Typography variant="body1">
                    <strong>結構分析</strong> - 識別樂曲的各個部分和整體結構
                  </Typography>
                </Box>
                <Box component="li">
                  <Typography variant="body1">
                    <strong>改進建議</strong> - 提供基於音樂理論的改進建議
                  </Typography>
                </Box>
              </Box>
              
              <Alert severity="info" sx={{ mt: 3 }}>
                為獲得最佳結果，請上傳清晰的MIDI文件或高質量的音頻文件。
              </Alert>
            </Paper>
          </Grid>
        </Grid>
      )}
      
      {activeTab === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper elevation={3} sx={{ p: 3 }}>
              {audioUrl && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    音樂文件
                  </Typography>
                  <MusicPlayer audioUrl={audioUrl} />
                </Box>
              )}
              
              <TheoryAnalyzer 
                midiFile={midiFile} 
                notes={notes}
                onAnalysisComplete={handleAnalysisComplete}
              />
            </Paper>
          </Grid>
        </Grid>
      )}
    </Container>
  );
};

export default TheoryAnalysisPage; 