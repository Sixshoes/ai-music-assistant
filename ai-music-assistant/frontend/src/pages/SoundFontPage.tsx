import {
    LibraryMusic,
    MusicNote,
    PlayArrow,
    Save,
    Stop
} from '@mui/icons-material';
import {
    Alert,
    Box,
    Button,
    CircularProgress,
    Container,
    FormControl,
    Grid,
    InputLabel,
    LinearProgress,
    MenuItem,
    Paper,
    Select,
    Tab,
    Tabs,
    Typography
} from '@mui/material';
import React, { useEffect, useRef, useState } from 'react';
import * as Tone from 'tone';
import SoundFontEditor from '../components/SoundFontEditor';
import Logger from '../services/LoggingService';
import synthesizerService, {
    RenderOptions,
    SoundFont,
    SoundPreset
} from '../services/SynthesizerService';

const SoundFontPage: React.FC = () => {
  // 狀態變數
  const [activeTab, setActiveTab] = useState(0);
  const [soundFonts, setSoundFonts] = useState<SoundFont[]>([]);
  const [presets, setPresets] = useState<SoundPreset[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedSoundFont, setSelectedSoundFont] = useState<string | null>(null);
  const [selectedPreset, setSelectedPreset] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [renderProgress, setRenderProgress] = useState(0);
  const [isRendering, setIsRendering] = useState(false);
  const [midiFile, setMidiFile] = useState<File | null>(null);
  const [outputFormat, setOutputFormat] = useState<'wav' | 'mp3' | 'ogg'>('wav');
  const [sampleRate, setSampleRate] = useState(44100);
  
  // 參考變數
  const audioPlayerRef = useRef<HTMLAudioElement | null>(null);
  const synthRef = useRef<Tone.Synth | null>(null);
  
  // 載入音色和預設
  useEffect(() => {
    loadSoundFontsAndPresets();
  }, []);
  
  // 載入音色和預設
  const loadSoundFontsAndPresets = async () => {
    try {
      setLoading(true);
      
      // 載入音色庫
      const fonts = await synthesizerService.getSoundFonts();
      setSoundFonts(fonts);
      
      // 載入預設
      const presetData = await synthesizerService.getPresets();
      setPresets(presetData);
      
      // 設置默認選擇
      if (fonts.length > 0) {
        setSelectedSoundFont(fonts[0].id);
      }
      
      setError(null);
    } catch (err) {
      Logger.error('載入音色庫失敗', err, { tags: ['SOUND_FONT'] });
      setError('載入音色庫時發生錯誤');
    } finally {
      setLoading(false);
    }
  };
  
  // 處理標籤頁變更
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };
  
  // 選擇音色
  const handleSoundFontChange = (event: React.ChangeEvent<{ value: unknown }>) => {
    setSelectedSoundFont(event.target.value as string);
    setSelectedPreset(null);
  };
  
  // 選擇預設
  const handlePresetChange = (event: React.ChangeEvent<{ value: unknown }>) => {
    setSelectedPreset(event.target.value as string);
  };
  
  // 獲取當前選擇的預設
  const getCurrentPreset = (): SoundPreset | null => {
    if (!selectedPreset) return null;
    return presets.find(p => p.id === selectedPreset) || null;
  };
  
  // 播放預覽
  const handlePlayPreview = async () => {
    if (isPlaying) {
      // 停止播放
      if (synthRef.current) {
        synthRef.current.triggerRelease(Tone.now());
        synthRef.current.dispose();
        synthRef.current = null;
      }
      setIsPlaying(false);
      return;
    }
    
    const currentPreset = getCurrentPreset();
    if (!currentPreset) return;
    
    // 開始播放
    try {
      setIsPlaying(true);
      
      // 使用服務播放預覽
      await synthesizerService.playNotePreview(currentPreset);
      
      // 播放完畢後設置狀態
      setIsPlaying(false);
    } catch (err) {
      Logger.error('播放預覽失敗', err, { tags: ['SOUND_FONT'] });
      setError('播放預覽時發生錯誤');
      setIsPlaying(false);
    }
  };
  
  // 保存自定義預設
  const handleSavePreset = async (preset: SoundPreset) => {
    try {
      setLoading(true);
      const savedPreset = await synthesizerService.savePreset(preset);
      
      // 更新預設列表
      setPresets(prev => {
        const index = prev.findIndex(p => p.id === savedPreset.id);
        if (index >= 0) {
          return prev.map(p => p.id === savedPreset.id ? savedPreset : p);
        } else {
          return [...prev, savedPreset];
        }
      });
      
      setSelectedPreset(savedPreset.id);
      setError(null);
      Logger.info('預設已保存', { presetName: savedPreset.name }, { tags: ['SOUND_FONT'] });
    } catch (err) {
      Logger.error('保存預設失敗', err, { tags: ['SOUND_FONT'] });
      setError('保存預設時發生錯誤');
    } finally {
      setLoading(false);
    }
  };
  
  // 選擇MIDI文件
  const handleMidiFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setMidiFile(file);
      Logger.info('已選擇MIDI文件', { fileName: file.name }, { tags: ['SOUND_FONT'] });
    }
  };
  
  // 渲染MIDI為音頻
  const handleRenderAudio = async () => {
    if (!midiFile || !selectedPreset) return;
    
    const currentPreset = getCurrentPreset();
    if (!currentPreset) return;
    
    try {
      setIsRendering(true);
      setRenderProgress(0);
      
      // 準備渲染選項
      const renderOptions: Partial<RenderOptions> = {
        format: outputFormat,
        sampleRate: sampleRate,
        bitDepth: 16,
        normalizeAudio: true,
        effects: []
      };
      
      // 模擬渲染進度
      const progressInterval = setInterval(() => {
        setRenderProgress(prev => {
          if (prev >= 95) {
            clearInterval(progressInterval);
            return 95;
          }
          return prev + 5;
        });
      }, 200);
      
      // 開始渲染
      const audioBlob = await synthesizerService.renderMidiToAudio(
        midiFile,
        currentPreset,
        renderOptions
      );
      
      // 渲染完成
      clearInterval(progressInterval);
      setRenderProgress(100);
      
      // 創建下載連結
      const audioUrl = URL.createObjectURL(audioBlob);
      const a = document.createElement('a');
      a.href = audioUrl;
      a.download = `${midiFile.name.replace(/\.[^/.]+$/, '')}_rendered.${outputFormat}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      
      // 清理資源
      setTimeout(() => {
        URL.revokeObjectURL(audioUrl);
      }, 100);
      
      setError(null);
      Logger.info('音頻渲染成功', { fileName: a.download }, { tags: ['SOUND_FONT'] });
    } catch (err) {
      Logger.error('渲染音頻失敗', err, { tags: ['SOUND_FONT'] });
      setError('渲染音頻時發生錯誤');
    } finally {
      setIsRendering(false);
    }
  };
  
  // 變更輸出格式
  const handleFormatChange = (event: React.ChangeEvent<{ value: unknown }>) => {
    setOutputFormat(event.target.value as 'wav' | 'mp3' | 'ogg');
  };
  
  // 變更採樣率
  const handleSampleRateChange = (event: React.ChangeEvent<{ value: unknown }>) => {
    setSampleRate(Number(event.target.value));
  };
  
  return (
    <Container maxWidth="lg">
      <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 4 }}>
        音色渲染與音訊輸出
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      <Paper sx={{ mb: 4 }}>
        <Tabs value={activeTab} onChange={handleTabChange} indicatorColor="primary" textColor="primary">
          <Tab label="音色瀏覽器" />
          <Tab label="音色編輯" />
          <Tab label="批量渲染" />
        </Tabs>
      </Paper>
      
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          {/* 音色瀏覽器標籤頁 */}
          {activeTab === 0 && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <Paper sx={{ p: 3, height: '100%' }}>
                  <Typography variant="h6" gutterBottom>
                    可用音色庫
                  </Typography>
                  <FormControl fullWidth sx={{ mb: 2 }}>
                    <InputLabel>選擇音色庫</InputLabel>
                    <Select
                      value={selectedSoundFont || ''}
                      onChange={handleSoundFontChange}
                      label="選擇音色庫"
                    >
                      {soundFonts.map(font => (
                        <MenuItem key={font.id} value={font.id}>
                          {font.name} ({font.type})
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  
                  {selectedSoundFont && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="body2" color="textSecondary" gutterBottom>
                        {soundFonts.find(f => f.id === selectedSoundFont)?.description}
                      </Typography>
                      <Button
                        variant="contained"
                        startIcon={isPlaying ? <Stop /> : <PlayArrow />}
                        onClick={handlePlayPreview}
                        sx={{ mt: 2 }}
                        disabled={!selectedPreset}
                      >
                        {isPlaying ? '停止預覽' : '播放預覽'}
                      </Button>
                    </Box>
                  )}
                </Paper>
              </Grid>
              
              <Grid item xs={12} md={8}>
                <Paper sx={{ p: 3, height: '100%' }}>
                  <Typography variant="h6" gutterBottom>
                    預設音色
                  </Typography>
                  <FormControl fullWidth sx={{ mb: 2 }}>
                    <InputLabel>選擇預設音色</InputLabel>
                    <Select
                      value={selectedPreset || ''}
                      onChange={handlePresetChange}
                      label="選擇預設音色"
                    >
                      {presets.filter(p => p.fontId === selectedSoundFont).map(preset => (
                        <MenuItem key={preset.id} value={preset.id}>
                          {preset.name} {preset.isFavorite ? '★' : ''}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  
                  {selectedPreset && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="subtitle1" gutterBottom>
                        參數預覽
                      </Typography>
                      <Grid container spacing={2}>
                        {Object.entries(presets.find(p => p.id === selectedPreset)?.parameters || {})
                          .filter(([key]) => !Array.isArray(presets.find(p => p.id === selectedPreset)?.parameters[key]))
                          .map(([key, value]) => (
                            <Grid item xs={6} key={key}>
                              <Typography variant="body2" color="textSecondary">
                                {key}: {value}
                              </Typography>
                            </Grid>
                          ))}
                      </Grid>
                      
                      <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
                        <Button
                          variant="contained"
                          startIcon={isPlaying ? <Stop /> : <MusicNote />}
                          onClick={handlePlayPreview}
                        >
                          {isPlaying ? '停止試聽' : '試聽'}
                        </Button>
                        <Button
                          variant="outlined"
                          startIcon={<Save />}
                          onClick={() => setActiveTab(1)}
                        >
                          編輯此預設
                        </Button>
                      </Box>
                    </Box>
                  )}
                </Paper>
              </Grid>
            </Grid>
          )}
          
          {/* 音色編輯標籤頁 */}
          {activeTab === 1 && (
            <SoundFontEditor
              preset={getCurrentPreset()}
              onSave={handleSavePreset}
              onPreview={handlePlayPreview}
            />
          )}
          
          {/* 批量渲染標籤頁 */}
          {activeTab === 2 && (
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                批量渲染
              </Typography>
              
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  選擇MIDI文件
                </Typography>
                <Button
                  variant="contained"
                  component="label"
                >
                  上傳MIDI文件
                  <input
                    type="file"
                    hidden
                    accept=".mid,.midi"
                    onChange={handleMidiFileChange}
                  />
                </Button>
                {midiFile && (
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    已選擇: {midiFile.name} ({(midiFile.size / 1024).toFixed(2)} KB)
                  </Typography>
                )}
              </Box>
              
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  選擇輸出設置
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth sx={{ mb: 2 }}>
                      <InputLabel>選擇音色</InputLabel>
                      <Select
                        value={selectedPreset || ''}
                        onChange={handlePresetChange}
                        label="選擇音色"
                      >
                        {presets.map(preset => (
                          <MenuItem key={preset.id} value={preset.id}>
                            {preset.name} - {soundFonts.find(f => f.id === preset.fontId)?.name || '未知音色庫'}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth sx={{ mb: 2 }}>
                      <InputLabel>輸出格式</InputLabel>
                      <Select
                        value={outputFormat}
                        onChange={handleFormatChange}
                        label="輸出格式"
                      >
                        <MenuItem value="wav">WAV</MenuItem>
                        <MenuItem value="mp3">MP3</MenuItem>
                        <MenuItem value="ogg">OGG</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth sx={{ mb: 2 }}>
                      <InputLabel>採樣率</InputLabel>
                      <Select
                        value={sampleRate}
                        onChange={handleSampleRateChange}
                        label="採樣率"
                      >
                        <MenuItem value={22050}>22.05 kHz</MenuItem>
                        <MenuItem value={44100}>44.1 kHz</MenuItem>
                        <MenuItem value={48000}>48 kHz</MenuItem>
                        <MenuItem value={96000}>96 kHz</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                </Grid>
              </Box>
              
              <Box sx={{ mb: 3 }}>
                <Button
                  variant="contained"
                  startIcon={<LibraryMusic />}
                  onClick={handleRenderAudio}
                  disabled={isRendering || !midiFile || !selectedPreset}
                >
                  開始渲染
                </Button>
              </Box>
              
              {isRendering && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" gutterBottom>
                    渲染進度: {renderProgress}%
                  </Typography>
                  <LinearProgress variant="determinate" value={renderProgress} />
                </Box>
              )}
            </Paper>
          )}
        </>
      )}
    </Container>
  );
};

export default SoundFontPage; 