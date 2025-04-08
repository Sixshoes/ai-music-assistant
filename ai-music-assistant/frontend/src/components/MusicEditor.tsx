import {
    Download,
    GraphicEq,
    MoreVert,
    MusicNote,
    PlayArrow,
    Save,
    Splitscreen,
    Stop,
    Tune,
    ZoomIn,
    ZoomOut
} from '@mui/icons-material';
import {
    Alert,
    Box,
    Button,
    Chip,
    CircularProgress,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Divider,
    FormControl,
    IconButton,
    InputLabel,
    ListItemIcon,
    ListItemText,
    Menu,
    MenuItem,
    Paper,
    Select,
    Slider,
    Stack,
    Tab,
    Tabs,
    TextField,
    Tooltip,
    Typography
} from '@mui/material';
import React, { useEffect, useRef, useState } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { musicNotationService } from '../services/MusicNotationService';

interface MusicEditorProps {
  initialScore?: string;
  onScoreChange?: (score: string) => void;
}

const MusicEditor: React.FC<MusicEditorProps> = ({ 
  initialScore = '', 
  onScoreChange 
}) => {
  const [editorLoaded, setEditorLoaded] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentInstrument, setCurrentInstrument] = useState('piano');
  const [tempo, setTempo] = useState(120);
  const [zoom, setZoom] = useState(100);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [moreMenuAnchor, setMoreMenuAnchor] = useState<null | HTMLElement>(null);
  const [exportDialogOpen, setExportDialogOpen] = useState(false);
  const [selectedExportFormat, setSelectedExportFormat] = useState<'musicxml' | 'pdf' | 'midi' | 'svg'>('pdf');
  const [exportFilename, setExportFilename] = useState('樂譜');
  const [scoreData, setScoreData] = useState<any>(null);
  const [currentView, setCurrentView] = useState<'score' | 'parts'>('score');
  const [musescoreAvailable, setMusescoreAvailable] = useState(false);
  
  const editorContainerRef = useRef<HTMLDivElement>(null);
  const vexflowContainerRef = useRef<HTMLDivElement>(null);
  const musescoreContainerRef = useRef<HTMLDivElement>(null);
  const webviewRef = useRef<HTMLIFrameElement | null>(null);

  const instruments = [
    { value: 'piano', label: '鋼琴' },
    { value: 'violin', label: '小提琴' },
    { value: 'guitar', label: '吉他' },
    { value: 'flute', label: '長笛' },
    { value: 'trumpet', label: '小號' },
    { value: 'string_ensemble', label: '弦樂合奏' },
    { value: 'woodwind_ensemble', label: '木管合奏' },
    { value: 'full_orchestra', label: '管弦樂團' }
  ];

  // 載入編輯器和初始化樂譜顯示功能
  useEffect(() => {
    const loadEditor = async () => {
      try {
        setLoading(true);
        console.log('載入樂譜編輯器...');
        
        // 檢查 MuseScore 整合是否可用
        // @ts-ignore - 暫時忽略類型檢查直到 MusicNotationService 完全實現
        const musescoreEnabled = musicNotationService.isMuseScoreEnabled();
        setMusescoreAvailable(musescoreEnabled);
        
        // 初始化 VexFlow 樂譜渲染
        if (vexflowContainerRef.current) {
          vexflowContainerRef.current.id = `vexflow-container-${uuidv4()}`;
          musicNotationService.initRenderer(vexflowContainerRef.current, {
            width: vexflowContainerRef.current.clientWidth,
            height: 300,
            scale: zoom / 100
          });
        }
        
        // 若提供初始樂譜數據，則載入
        if (initialScore) {
          try {
            const parsedScore = JSON.parse(initialScore);
            setScoreData(parsedScore);
            renderScore(parsedScore);
          } catch (parseError) {
            console.error('解析初始樂譜數據失敗:', parseError);
          }
        } else {
          // 載入示例樂譜
          loadExampleScore();
        }
        
        setEditorLoaded(true);
        setLoading(false);
      } catch (err) {
        console.error('載入編輯器失敗:', err);
        setError('無法載入音樂編輯器。請檢查您的網絡連接或重新整理頁面。');
        setLoading(false);
      }
    };

    loadEditor();

    return () => {
      // 清理代碼
      if (isPlaying) {
        stopPlayback();
      }
      musicNotationService.stopAllNotes();
    };
  }, []);
  
  // 處理縮放變化時重新渲染樂譜
  useEffect(() => {
    if (editorLoaded && vexflowContainerRef.current && scoreData) {
      musicNotationService.initRenderer(vexflowContainerRef.current, {
        width: vexflowContainerRef.current.clientWidth,
        height: 300,
        scale: zoom / 100
      });
      renderScore(scoreData);
    }
  }, [zoom, editorLoaded]);
  
  // 載入示例樂譜
  const loadExampleScore = () => {
    const exampleMusicXML = `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1">
  <part-list>
    <score-part id="P1">
      <part-name>Piano</part-name>
    </score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>1</divisions>
        <key>
          <fifths>0</fifths>
        </key>
        <time>
          <beats>4</beats>
          <beat-type>4</beat-type>
        </time>
        <clef>
          <sign>G</sign>
          <line>2</line>
        </clef>
      </attributes>
      <note>
        <pitch>
          <step>C</step>
          <octave>4</octave>
        </pitch>
        <duration>1</duration>
        <type>quarter</type>
      </note>
      <note>
        <pitch>
          <step>D</step>
          <octave>4</octave>
        </pitch>
        <duration>1</duration>
        <type>quarter</type>
      </note>
      <note>
        <pitch>
          <step>E</step>
          <octave>4</octave>
        </pitch>
        <duration>1</duration>
        <type>quarter</type>
      </note>
      <note>
        <pitch>
          <step>F</step>
          <octave>4</octave>
        </pitch>
        <duration>1</duration>
        <type>quarter</type>
      </note>
    </measure>
  </part>
</score-partwise>`;

    try {
      const parsedScore = musicNotationService.parseMusicXML(exampleMusicXML);
      setScoreData(parsedScore);
      renderScore(parsedScore);
    } catch (error) {
      console.error('載入示例樂譜失敗:', error);
    }
  };
  
  // 渲染樂譜
  const renderScore = (data: any) => {
    if (!editorLoaded || !vexflowContainerRef.current) return;
    
    try {
      musicNotationService.renderScore(data);
    } catch (error) {
      console.error('渲染樂譜失敗:', error);
      setError('渲染樂譜失敗。請檢查樂譜數據格式是否正確。');
    }
  };

  // 播放音樂
  const startPlayback = () => {
    if (!editorLoaded) return;
    
    console.log('開始播放，速度:', tempo);
    setIsPlaying(true);
    // 實際實現時會調用音樂播放 API
    // TODO: 實現真正的樂譜播放功能
  };

  // 停止播放
  const stopPlayback = () => {
    if (!editorLoaded) return;
    
    console.log('停止播放');
    setIsPlaying(false);
    musicNotationService.stopAllNotes();
  };

  // 切換樂器
  const changeInstrument = (event: any) => {
    const newInstrument = event.target.value;
    console.log('切換樂器到:', newInstrument);
    setCurrentInstrument(newInstrument);
    // 實際實現時會更改樂器音色
  };

  // 調整速度
  const changeTempo = (event: Event, newValue: number | number[]) => {
    const newTempo = newValue as number;
    console.log('調整速度到:', newTempo);
    setTempo(newTempo);
    // 實際實現時會更改播放速度
  };

  // 調整縮放
  const changeZoom = (event: Event, newValue: number | number[]) => {
    const newZoom = newValue as number;
    console.log('調整縮放到:', newZoom);
    setZoom(newZoom);
  };

  // 儲存樂譜
  const saveScore = () => {
    if (!editorLoaded || !scoreData) return;
    
    console.log('儲存樂譜');
    const scoreDataString = JSON.stringify(scoreData);
    if (onScoreChange) {
      onScoreChange(scoreDataString);
    }
  };

  // 添加音符
  const addNote = (note: string) => {
    if (!editorLoaded || !scoreData) return;
    
    console.log('添加音符:', note);
    // 添加音符到樂譜數據
    const updatedScoreData = { ...scoreData };
    // 添加一個新音符到音符陣列
    // 這裡使用簡單的音符數據示例，實際應用中需要更複雜的處理
    const newNote = {
      key: 'C/4', // 默認 C4
      duration: 'q' // 默認四分音符
    };
    
    switch (note) {
      case 'whole':
        newNote.duration = 'w';
        break;
      case 'half':
        newNote.duration = 'h';
        break;
      case 'quarter':
        newNote.duration = 'q';
        break;
      case 'eighth':
        newNote.duration = '8';
        break;
      case 'sixteenth':
        newNote.duration = '16';
        break;
    }
    
    updatedScoreData.notes = [...(updatedScoreData.notes || []), newNote];
    setScoreData(updatedScoreData);
    renderScore(updatedScoreData);
  };
  
  // 打開更多操作菜單
  const handleOpenMoreMenu = (event: React.MouseEvent<HTMLElement>) => {
    setMoreMenuAnchor(event.currentTarget);
  };
  
  // 關閉更多操作菜單
  const handleCloseMoreMenu = () => {
    setMoreMenuAnchor(null);
  };
  
  // 打開匯出對話框
  const handleOpenExportDialog = () => {
    handleCloseMoreMenu();
    setExportDialogOpen(true);
  };
  
  // 關閉匯出對話框
  const handleCloseExportDialog = () => {
    setExportDialogOpen(false);
  };
  
  // 執行匯出
  const handleExport = async () => {
    try {
      setLoading(true);
      await musicNotationService.exportScore(
        scoreData, 
        {
          format: selectedExportFormat,
          filename: `${exportFilename}.${selectedExportFormat}`
        }
      );
      setExportDialogOpen(false);
    } catch (error) {
      console.error('匯出樂譜失敗:', error);
      setError(`匯出樂譜失敗：${error instanceof Error ? error.message : '未知錯誤'}`);
    } finally {
      setLoading(false);
    }
  };
  
  // 切換分頁
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };
  
  // 切換視圖（整體樂譜或分部樂譜）
  const toggleView = () => {
    setCurrentView(currentView === 'score' ? 'parts' : 'score');
  };
  
  // 重置縮放
  const resetZoom = () => {
    setZoom(100);
  };

  return (
    <Paper elevation={2} sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          音樂編輯器 {musescoreAvailable && <Chip size="small" color="success" label="MuseScore 整合" sx={{ ml: 1 }} />}
        </Typography>
        
        <Tooltip title="更多選項">
          <IconButton onClick={handleOpenMoreMenu}>
            <MoreVert />
          </IconButton>
        </Tooltip>
        
        <Menu
          anchorEl={moreMenuAnchor}
          open={Boolean(moreMenuAnchor)}
          onClose={handleCloseMoreMenu}
        >
          <MenuItem onClick={handleOpenExportDialog}>
            <ListItemIcon>
              <Download fontSize="small" />
            </ListItemIcon>
            <ListItemText>匯出樂譜</ListItemText>
          </MenuItem>
          <MenuItem onClick={toggleView}>
            <ListItemIcon>
              <Splitscreen fontSize="small" />
            </ListItemIcon>
            <ListItemText>{currentView === 'score' ? '顯示分部樂譜' : '顯示完整樂譜'}</ListItemText>
          </MenuItem>
          <MenuItem onClick={resetZoom}>
            <ListItemIcon>
              <ZoomIn fontSize="small" />
            </ListItemIcon>
            <ListItemText>重置縮放</ListItemText>
          </MenuItem>
        </Menu>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 2 }}>
        <Tab icon={<MusicNote />} label="基本編輯" />
        <Tab icon={<Tune />} label="樂譜設定" />
        <Tab icon={<GraphicEq />} label="演奏提示" />
      </Tabs>

      <Box sx={{ display: activeTab === 0 ? 'block' : 'none' }}>
        <Box sx={{ display: 'flex', mb: 2, gap: 2, flexWrap: 'wrap' }}>
          <Button
            variant="contained"
            color={isPlaying ? "secondary" : "primary"}
            startIcon={isPlaying ? <Stop /> : <PlayArrow />}
            onClick={isPlaying ? stopPlayback : startPlayback}
            disabled={!editorLoaded || loading}
          >
            {isPlaying ? '停止' : '播放'}
          </Button>
          
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel id="instrument-select-label">樂器</InputLabel>
            <Select
              labelId="instrument-select-label"
              value={currentInstrument}
              label="樂器"
              onChange={changeInstrument}
              disabled={!editorLoaded || loading}
            >
              {instruments.map((instrument) => (
                <MenuItem key={instrument.value} value={instrument.value}>
                  {instrument.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Box sx={{ width: 150 }}>
            <Typography variant="caption" color="text.secondary">
              速度: {tempo} BPM
            </Typography>
            <Slider
              size="small"
              value={tempo}
              min={40}
              max={240}
              onChange={changeTempo}
              disabled={!editorLoaded || loading}
            />
          </Box>

          <Tooltip title="縮放">
            <Stack direction="row" spacing={1} alignItems="center" sx={{ ml: 'auto' }}>
              <IconButton 
                size="small" 
                onClick={() => setZoom(Math.max(50, zoom - 10))}
                disabled={!editorLoaded || loading || zoom <= 50}
              >
                <ZoomOut fontSize="small" />
              </IconButton>
              <Typography variant="body2">{zoom}%</Typography>
              <IconButton 
                size="small" 
                onClick={() => setZoom(Math.min(200, zoom + 10))}
                disabled={!editorLoaded || loading || zoom >= 200}
              >
                <ZoomIn fontSize="small" />
              </IconButton>
            </Stack>
          </Tooltip>

          <Button
            variant="outlined"
            startIcon={<Save />}
            onClick={saveScore}
            disabled={!editorLoaded || loading}
          >
            儲存
          </Button>
        </Box>

        <Box 
          ref={editorContainerRef}
          sx={{ 
            flexGrow: 1, 
            border: '1px solid #ccc', 
            borderRadius: 1,
            overflow: 'hidden',
            position: 'relative',
            bgcolor: '#f5f5f5',
            minHeight: '300px'
          }}
        >
          {loading ? (
            <Box 
              sx={{ 
                display: 'flex', 
                justifyContent: 'center', 
                alignItems: 'center', 
                height: '100%',
                flexDirection: 'column'
              }}
            >
              <CircularProgress size={40} />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                處理中...
              </Typography>
            </Box>
          ) : !editorLoaded ? (
            <Box 
              sx={{ 
                display: 'flex', 
                justifyContent: 'center', 
                alignItems: 'center', 
                height: '100%',
                flexDirection: 'column'
              }}
            >
              <MusicNote sx={{ fontSize: 60, color: 'rgba(0, 0, 0, 0.2)' }} />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                正在載入編輯器...
              </Typography>
            </Box>
          ) : currentView === 'score' ? (
            <Box ref={vexflowContainerRef} sx={{ width: '100%', height: '100%', p: 2 }} />
          ) : (
            <Box ref={musescoreContainerRef} sx={{ width: '100%', height: '100%', p: 2 }}>
              <Typography variant="subtitle2" gutterBottom>分部樂譜視圖</Typography>
              {/* 在這裡加入分部樂譜顯示內容 */}
              <Alert severity="info">分部樂譜功能開發中</Alert>
            </Box>
          )}
        </Box>

        <Stack direction="row" spacing={1} sx={{ mt: 2, overflowX: 'auto', pb: 1 }}>
          <Tooltip title="新增全音符">
            <Button 
              variant="outlined" 
              size="small" 
              onClick={() => addNote('whole')}
              disabled={!editorLoaded || loading}
            >
              <img src="/images/whole-note.svg" alt="全音符" width="20" height="20" />
            </Button>
          </Tooltip>
          <Tooltip title="新增二分音符">
            <Button 
              variant="outlined" 
              size="small" 
              onClick={() => addNote('half')}
              disabled={!editorLoaded || loading}
            >
              <img src="/images/half-note.svg" alt="二分音符" width="20" height="20" />
            </Button>
          </Tooltip>
          <Tooltip title="新增四分音符">
            <Button 
              variant="outlined" 
              size="small" 
              onClick={() => addNote('quarter')}
              disabled={!editorLoaded || loading}
            >
              <img src="/images/quarter-note.svg" alt="四分音符" width="20" height="20" />
            </Button>
          </Tooltip>
          <Tooltip title="新增八分音符">
            <Button 
              variant="outlined" 
              size="small" 
              onClick={() => addNote('eighth')}
              disabled={!editorLoaded || loading}
            >
              <img src="/images/eighth-note.svg" alt="八分音符" width="20" height="20" />
            </Button>
          </Tooltip>
          <Tooltip title="新增十六分音符">
            <Button 
              variant="outlined" 
              size="small" 
              onClick={() => addNote('sixteenth')}
              disabled={!editorLoaded || loading}
            >
              <img src="/images/sixteenth-note.svg" alt="十六分音符" width="20" height="20" />
            </Button>
          </Tooltip>
          <Divider orientation="vertical" flexItem />
          <Tooltip title="休止符">
            <Button 
              variant="outlined" 
              size="small" 
              onClick={() => addNote('rest')}
              disabled={!editorLoaded || loading}
            >
              <img src="/images/quarter-rest.svg" alt="休止符" width="20" height="20" />
            </Button>
          </Tooltip>
          <Tooltip title="升記號">
            <Button 
              variant="outlined" 
              size="small" 
              disabled={!editorLoaded || loading}
            >
              <span style={{ fontSize: '16px' }}>#</span>
            </Button>
          </Tooltip>
          <Tooltip title="降記號">
            <Button 
              variant="outlined" 
              size="small" 
              disabled={!editorLoaded || loading}
            >
              <span style={{ fontSize: '16px' }}>♭</span>
            </Button>
          </Tooltip>
        </Stack>
      </Box>

      <Box sx={{ display: activeTab === 1 ? 'block' : 'none' }}>
        <Alert severity="info" sx={{ mb: 2 }}>
          樂譜設定功能開發中。您將可以在這裡調整樂譜的時間標記、調號、拍號和其他排版選項。
        </Alert>
        <Box sx={{ height: '300px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            樂譜設定功能即將推出...
          </Typography>
        </Box>
      </Box>

      <Box sx={{ display: activeTab === 2 ? 'block' : 'none' }}>
        <Alert severity="info" sx={{ mb: 2 }}>
          演奏提示功能開發中。您將可以在這裡添加演奏技巧、強弱記號、詮釋提示等。
        </Alert>
        <Box sx={{ height: '300px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            演奏提示功能即將推出...
          </Typography>
        </Box>
      </Box>
      
      {/* 匯出對話框 */}
      <Dialog open={exportDialogOpen} onClose={handleCloseExportDialog}>
        <DialogTitle>匯出樂譜</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2, mb: 3 }}>
            <InputLabel>格式</InputLabel>
            <Select
              value={selectedExportFormat}
              onChange={(e) => setSelectedExportFormat(e.target.value as any)}
              label="格式"
            >
              <MenuItem value="pdf">PDF 文件</MenuItem>
              <MenuItem value="musicxml">MusicXML 文件</MenuItem>
              <MenuItem value="midi">MIDI 文件</MenuItem>
              <MenuItem value="svg">SVG 圖像</MenuItem>
            </Select>
          </FormControl>
          <TextField
            label="檔案名稱"
            fullWidth
            value={exportFilename}
            onChange={(e) => setExportFilename(e.target.value)}
            helperText={`將匯出為 ${exportFilename}.${selectedExportFormat}`}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseExportDialog}>取消</Button>
          <Button 
            onClick={handleExport} 
            variant="contained" 
            disabled={loading || !exportFilename.trim()}
            startIcon={loading ? <CircularProgress size={16} /> : <Download />}
          >
            {loading ? '處理中...' : '匯出'}
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default MusicEditor; 