import {
    AutoGraph,
    Check,
    Close,
    Edit,
    GraphicEq,
    Info,
    LibraryMusic,
    MusicNote,
    PianoOutlined,
    ViewList
} from '@mui/icons-material';
import {
    Alert,
    Box,
    Button,
    Chip,
    CircularProgress,
    Divider,
    Grid,
    List,
    ListItem,
    ListItemText,
    Paper,
    Tab,
    Tabs,
    TextField,
    Tooltip,
    Typography
} from '@mui/material';
import React, { useEffect, useRef, useState } from 'react';
import {
    Bar,
    BarChart,
    Cell,
    Legend,
    Pie,
    PieChart,
    RechartsTooltip,
    ResponsiveContainer,
    XAxis,
    YAxis
} from 'recharts';

// 音符類型定義
interface Note {
  pitch: number;
  duration: number;
  startTime?: number;
  velocity?: number;
}

// 更詳細的音樂理論反饋接口
interface MusicTheoryFeedback {
  score: number;
  key: string;
  tempo?: number;
  timeSignature?: string;
  chords: string[];
  chordNumerals?: string[];
  progression: string;
  suggestions: string[];
  errors: string[];
  warnings: string[];
  structure?: {[section: string]: number[]};
  melodyAnalysis?: {
    pitchRange: number;
    averagePitch: number;
    mostCommonInterval: number;
    rhythmicDiversity: number;
  };
  harmonyAnalysis?: {
    diatonicPercentage: number;
    dissonanceLevel: number;
    colorChords: string[];
  };
}

// 互動式和弦進行項
interface ChordItem {
  symbol: string;
  numeral: string;
  duration: number;
  isEditing: boolean;
  originalSymbol?: string;
  id: string;
}

interface TheoryAnalyzerProps {
  musicData?: string;
  midiFile?: File;
  notes?: Note[];
  onAnalysisComplete?: (analysis: MusicTheoryFeedback) => void;
}

// 顏色常量
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#A569BD', '#EC7063', '#5499C7', '#52BE80'];

const TheoryAnalyzer: React.FC<TheoryAnalyzerProps> = ({ 
  musicData,
  midiFile,
  notes,
  onAnalysisComplete
}) => {
  const [analyzing, setAnalyzing] = useState<boolean>(false);
  const [analyzed, setAnalyzed] = useState<boolean>(false);
  const [feedback, setFeedback] = useState<MusicTheoryFeedback | null>(null);
  const [customQuery, setCustomQuery] = useState<string>('');
  const [activeTab, setActiveTab] = useState<number>(0);
  const [chordItems, setChordItems] = useState<ChordItem[]>([]);
  const [pianoRollData, setPianoRollData] = useState<any[]>([]);
  const [structureData, setStructureData] = useState<any[]>([]);
  const [harmonyData, setHarmonyData] = useState<any[]>([]);
  const pianoRollRef = useRef<HTMLDivElement>(null);
  
  // 處理標籤變更
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };
  
  // 初始化和弦項
  useEffect(() => {
    if (feedback && feedback.chords) {
      const items = feedback.chords.map((chord, index) => ({
        symbol: chord,
        numeral: feedback.chordNumerals?.[index] || convertToNumeral(chord, feedback.key),
        duration: 1.0, // 預設持續時間
        isEditing: false,
        id: `chord-${index}-${Date.now()}`
      }));
      setChordItems(items);
      
      // 初始化和聲分析數據
      if (feedback.harmonyAnalysis) {
        const harmonyChartData = [
          { name: '調內和弦', value: feedback.harmonyAnalysis.diatonicPercentage },
          { name: '調外和弦', value: 100 - feedback.harmonyAnalysis.diatonicPercentage }
        ];
        setHarmonyData(harmonyChartData);
      }
      
      // 初始化結構數據
      if (feedback.structure) {
        const structureChartData = Object.entries(feedback.structure).map(([section, measures]) => ({
          name: section.charAt(0).toUpperCase() + section.slice(1),
          value: measures.length,
          measures: `${measures[0]}-${measures[measures.length - 1]}`
        }));
        setStructureData(structureChartData);
      }
    }
  }, [feedback]);
  
  // 將和弦轉換為級數標記(簡易版本)
  const convertToNumeral = (chordSymbol: string, keyStr: string): string => {
    // 在實際應用中，這應該是一個更複雜的函數，能夠正確解析和弦和調性
    const numerals = ["I", "ii", "iii", "IV", "V", "vi", "vii°"];
    const index = Math.floor(Math.random() * numerals.length);
    return numerals[index];
  };
  
  // 編輯和弦
  const toggleChordEdit = (id: string) => {
    setChordItems(items => items.map(item => 
      item.id === id 
        ? { ...item, isEditing: !item.isEditing, originalSymbol: item.isEditing ? undefined : item.symbol } 
        : item
    ));
  };
  
  // 更新和弦
  const updateChord = (id: string, newSymbol: string) => {
    setChordItems(items => items.map(item => 
      item.id === id ? { ...item, symbol: newSymbol } : item
    ));
  };
  
  // 取消和弦編輯
  const cancelChordEdit = (id: string) => {
    setChordItems(items => items.map(item => 
      item.id === id && item.originalSymbol
        ? { ...item, isEditing: false, symbol: item.originalSymbol, originalSymbol: undefined }
        : item
    ));
  };
  
  // 確認和弦編輯
  const confirmChordEdit = (id: string) => {
    setChordItems(items => items.map(item => 
      item.id === id
        ? { ...item, isEditing: false, originalSymbol: undefined, numeral: convertToNumeral(item.symbol, feedback?.key || 'C Major') }
        : item
    ));
    // 在實際應用中，這裡應該調用後端API以更新和弦分析
  };
  
  // 模擬分析過程
  const analyzeMusic = async () => {
    setAnalyzing(true);
    setAnalyzed(false);
    
    try {
      let result;
      
      if (midiFile) {
        // 處理MIDI文件
        const formData = new FormData();
        formData.append('midi_file', midiFile);
        
        // 在實際應用中替換為真實的API端點
        // const response = await axios.post('/api/analyze-music-theory', formData);
        // result = response.data;
        
        // 模擬響應
        result = getMockAnalysisResult();
      } else if (notes && notes.length > 0) {
        // 處理音符數據
        // const response = await axios.post('/api/analyze-notes', { notes });
        // result = response.data;
        
        // 模擬響應
        result = getMockAnalysisResult();
      } else if (musicData) {
        // 處理音樂數據字符串
        // const response = await axios.post('/api/analyze-music-data', { music_data: musicData });
        // result = response.data;
        
        // 模擬響應
        result = getMockAnalysisResult();
      } else {
        // 如果沒有提供數據，使用模擬數據
        result = getMockAnalysisResult();
      }
      
      setFeedback(result);
      
      // 生成鋼琴卷軸數據
      if (notes) {
        generatePianoRollData(notes);
      }
      
      setAnalyzed(true);
      
      if (onAnalysisComplete) {
        onAnalysisComplete(result);
      }
    } catch (error) {
      console.error('分析音樂時出錯:', error);
      setFeedback({
        score: 0,
        key: 'Unknown',
        chords: [],
        progression: '',
        suggestions: ['無法分析音樂，請檢查輸入數據'],
        errors: ['分析過程中發生錯誤'],
        warnings: []
      });
    } finally {
      setAnalyzing(false);
    }
  };
  
  // 生成鋼琴卷軸數據
  const generatePianoRollData = (notesList: Note[]) => {
    // 將音符數據轉換為鋼琴卷軸格式
    const rollData = notesList.map((note, index) => ({
      id: index,
      pitch: note.pitch,
      pitchName: getPitchName(note.pitch),
      duration: note.duration,
      startTime: note.startTime || index * 0.5,
      velocity: note.velocity || 64
    }));
    
    setPianoRollData(rollData);
  };
  
  // 獲取音高名稱
  const getPitchName = (midiPitch: number): string => {
    const noteNames = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
    const octave = Math.floor(midiPitch / 12) - 1;
    const noteName = noteNames[midiPitch % 12];
    return `${noteName}${octave}`;
  };
  
  // 處理自定義查詢
  const handleCustomQuery = async () => {
    if (!customQuery.trim()) return;
    
    setAnalyzing(true);
    
    try {
      // 實際應用中應該調用真實API
      // const response = await axios.post('/api/theory-query', {
      //   query: customQuery,
      //   context: feedback
      // });
      // const queryResponse = response.data.response;
      
      // 模擬響應
      const queryResponse = `關於"${customQuery}"的分析：在古典音樂中，常見的做法是使用調內的II-V-I進行增加和聲張力，您可以在第8小節後嘗試這個進行。`;
      
      // 更新反饋
      if (feedback) {
        setFeedback({
          ...feedback,
          suggestions: [...feedback.suggestions, queryResponse]
        });
      }
    } catch (error) {
      console.error('處理自定義查詢時出錯:', error);
    } finally {
      setAnalyzing(false);
      setCustomQuery('');
    }
  };
  
  // 獲取模擬分析結果
  const getMockAnalysisResult = (): MusicTheoryFeedback => {
    return {
      score: 85,
      key: 'C Major',
      tempo: 120,
      timeSignature: '4/4',
      chords: ['C', 'Am', 'F', 'G7', 'C', 'Dm7', 'G7', 'C'],
      chordNumerals: ['I', 'vi', 'IV', 'V7', 'I', 'ii7', 'V7', 'I'],
      progression: 'I - vi - IV - V7 - I - ii7 - V7 - I',
      suggestions: [
        '可以考慮在副歌部分使用 ii - V - I 進行增加緊張感',
        '嘗試在橋段使用轉調到相對小調增加對比',
        '可以加入七和弦增加和聲色彩'
      ],
      errors: [],
      warnings: [
        '第23小節存在平行五度',
        '低音部分跨度過大，可能造成演奏困難'
      ],
      structure: {
        'verse': [1, 5, 9, 13],
        'chorus': [17, 21, 25, 29],
        'bridge': [33, 37]
      },
      melodyAnalysis: {
        pitchRange: 19,
        averagePitch: 60,
        mostCommonInterval: 2,
        rhythmicDiversity: 0.7
      },
      harmonyAnalysis: {
        diatonicPercentage: 85,
        dissonanceLevel: 0.3,
        colorChords: ['F#dim7', 'Eb7']
      }
    };
  };
  
  // 渲染和弦進行可視化
  const renderChordProgression = () => {
    if (!chordItems.length) return null;
    
    return (
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle1" gutterBottom>
          和弦進行圖
        </Typography>
        <Paper 
          variant="outlined" 
          sx={{ 
            p: 2, 
            display: 'flex', 
            flexWrap: 'wrap', 
            alignItems: 'flex-end',
            minHeight: 120,
            position: 'relative'
          }}
        >
          {chordItems.map((item) => (
            <Box 
              key={item.id} 
              sx={{ 
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                m: 0.5,
                minWidth: 50
              }}
            >
              {item.isEditing ? (
                <>
                  <TextField
                    variant="standard"
                    value={item.symbol}
                    onChange={(e) => updateChord(item.id, e.target.value)}
                    size="small"
                    sx={{ width: 50, mb: 1 }}
                  />
                  <Box sx={{ display: 'flex', mt: 0.5 }}>
                    <IconButton 
                      size="small" 
                      color="primary"
                      onClick={() => confirmChordEdit(item.id)}
                    >
                      <Check fontSize="small" />
                    </IconButton>
                    <IconButton 
                      size="small" 
                      color="error"
                      onClick={() => cancelChordEdit(item.id)}
                    >
                      <Close fontSize="small" />
                    </IconButton>
                  </Box>
                </>
              ) : (
                <>
                  <Paper 
                    elevation={2}
                    sx={{ 
                      py: 1.5, 
                      px: 2,
                      borderRadius: 1,
                      bgcolor: 'primary.light',
                      color: 'primary.contrastText',
                      position: 'relative',
                      cursor: 'pointer',
                      '&:hover': {
                        bgcolor: 'primary.main',
                        '& .edit-icon': {
                          opacity: 1
                        }
                      }
                    }}
                    onClick={() => toggleChordEdit(item.id)}
                  >
                    <Typography variant="body1" fontWeight="bold">
                      {item.symbol}
                    </Typography>
                    <Edit 
                      className="edit-icon"
                      sx={{ 
                        position: 'absolute',
                        top: -8,
                        right: -8,
                        fontSize: 16,
                        bgcolor: 'background.paper',
                        borderRadius: '50%',
                        opacity: 0,
                        transition: 'opacity 0.2s'
                      }}
                    />
                  </Paper>
                  <Typography 
                    variant="caption" 
                    fontWeight="medium" 
                    sx={{ mt: 1 }}
                  >
                    {item.numeral}
                  </Typography>
                </>
              )}
            </Box>
          ))}
        </Paper>
      </Box>
    );
  };
  
  // 渲染結構分析
  const renderStructureAnalysis = () => {
    if (!structureData.length) return null;
    
    return (
      <Box sx={{ mb: 3, mt: 2 }}>
        <Typography variant="subtitle1" gutterBottom>
          曲式結構分析
        </Typography>
        <Paper variant="outlined" sx={{ p: 2, height: 300 }}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={structureData}
                cx="50%"
                cy="50%"
                labelLine={true}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
                nameKey="name"
                label={({ name, value, measures }) => `${name} (小節 ${measures})`}
              >
                {structureData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Legend />
              <RechartsTooltip 
                formatter={(value, name, props) => [
                  `${value} 小節`, 
                  `${name} 部分`
                ]}
              />
            </PieChart>
          </ResponsiveContainer>
        </Paper>
      </Box>
    );
  };
  
  // 渲染和聲分析
  const renderHarmonyAnalysis = () => {
    if (!harmonyData.length || !feedback?.harmonyAnalysis) return null;
    
    return (
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle1" gutterBottom>
          和聲成分分析
        </Typography>
        <Paper variant="outlined" sx={{ p: 2 }}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={harmonyData}
                    cx="50%"
                    cy="50%"
                    outerRadius={60}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {harmonyData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Legend />
                  <RechartsTooltip />
                </PieChart>
              </ResponsiveContainer>
            </Grid>
            <Grid item xs={12} md={6}>
              <List dense disablePadding>
                <ListItem>
                  <ListItemText 
                    primary="不協和度"
                    secondary={`${(feedback.harmonyAnalysis.dissonanceLevel * 100).toFixed(1)}%`}
                  />
                </ListItem>
                {feedback.harmonyAnalysis.colorChords.length > 0 && (
                  <ListItem>
                    <ListItemText 
                      primary="顏色和弦/調外和弦"
                      secondary={
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                          {feedback.harmonyAnalysis.colorChords.map((chord, index) => (
                            <Chip 
                              key={index} 
                              label={chord} 
                              size="small" 
                              variant="outlined"
                              color="secondary" 
                            />
                          ))}
                        </Box>
                      }
                    />
                  </ListItem>
                )}
              </List>
            </Grid>
          </Grid>
        </Paper>
      </Box>
    );
  };
  
  // 渲染旋律分析
  const renderMelodyAnalysis = () => {
    if (!feedback?.melodyAnalysis) return null;
    
    const melodyData = [
      { name: '音高範圍', value: feedback.melodyAnalysis.pitchRange },
      { name: '平均音高', value: feedback.melodyAnalysis.averagePitch },
      { name: '常見音程', value: feedback.melodyAnalysis.mostCommonInterval },
      { name: '節奏多樣性', value: feedback.melodyAnalysis.rhythmicDiversity * 100 }
    ];
    
    return (
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle1" gutterBottom>
          旋律特徵分析
        </Typography>
        <Paper variant="outlined" sx={{ p: 2, height: 250 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={melodyData}
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <XAxis dataKey="name" />
              <YAxis />
              <RechartsTooltip />
              <Bar dataKey="value" fill="#8884d8">
                {melodyData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Paper>
      </Box>
    );
  };
  
  // 渲染鋼琴卷軸
  const renderPianoRoll = () => {
    if (!pianoRollData.length) return null;
    
    // 簡易版本的鋼琴卷軸視圖
    return (
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle1" gutterBottom>
          鋼琴卷軸視圖
        </Typography>
        <Paper 
          variant="outlined" 
          sx={{ height: 200, overflow: 'auto' }}
          ref={pianoRollRef}
        >
          <Box sx={{ display: 'flex', position: 'relative', height: '100%', minWidth: 800 }}>
            {/* 鋼琴鍵盤參考 */}
            <Box sx={{ width: 50, borderRight: '1px solid #ddd', display: 'flex', flexDirection: 'column' }}>
              {Array.from({ length: 24 }).map((_, i) => {
                const isBlackKey = [1, 3, 6, 8, 10].includes((23 - i) % 12);
                return (
                  <Box 
                    key={i}
                    sx={{
                      height: 8,
                      bgcolor: isBlackKey ? '#333' : '#fff',
                      border: '1px solid #ddd',
                      color: isBlackKey ? '#fff' : '#000',
                      fontSize: '7px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                  >
                    {isBlackKey ? '' : getPitchName(72 - i)}
                  </Box>
                );
              })}
            </Box>
            
            {/* 音符視圖 */}
            <Box sx={{ flexGrow: 1, position: 'relative' }}>
              {/* 背景網格 */}
              {Array.from({ length: 24 }).map((_, i) => (
                <Box 
                  key={i}
                  sx={{
                    position: 'absolute',
                    left: 0,
                    top: i * 8,
                    right: 0,
                    height: 8,
                    bgcolor: [1, 3, 6, 8, 10].includes((23 - i) % 12) ? 'rgba(0,0,0,0.05)' : 'transparent',
                    borderBottom: '1px solid #eee'
                  }}
                />
              ))}
              
              {/* 音符塊 */}
              {pianoRollData.map((note) => {
                const octave = Math.floor(note.pitch / 12) - 1;
                const yPos = (127 - note.pitch) * 8 / 12;
                return (
                  <Tooltip key={note.id} title={`${note.pitchName} (音高: ${note.pitch}, 時長: ${note.duration})`}>
                    <Box
                      sx={{
                        position: 'absolute',
                        left: note.startTime * 50,
                        top: yPos,
                        width: note.duration * 50,
                        height: 8,
                        bgcolor: COLORS[octave % COLORS.length],
                        border: '1px solid rgba(0,0,0,0.2)',
                        borderRadius: '2px',
                        opacity: note.velocity / 127,
                        zIndex: 2
                      }}
                    />
                  </Tooltip>
                );
              })}
            </Box>
          </Box>
        </Paper>
      </Box>
    );
  };

  return (
    <Paper elevation={2} sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
        <LibraryMusic sx={{ mr: 1 }} />
        音樂理論分析器
      </Typography>
      
      {!analyzed && !analyzing && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="body2" sx={{ mb: 2 }}>
            分析您的音樂作品，獲取專業的音樂理論反饋和建議。
          </Typography>
          <Button 
            variant="contained" 
            onClick={analyzeMusic}
            startIcon={<MusicNote />}
          >
            開始分析
          </Button>
        </Box>
      )}
      
      {analyzing && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
          <Typography variant="body2" sx={{ ml: 2 }}>
            正在分析音樂理論結構...
          </Typography>
        </Box>
      )}
      
      {analyzed && feedback && (
        <>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Alert 
                severity={feedback.score >= 80 ? "success" : feedback.score >= 60 ? "info" : "warning"}
                icon={<Info />}
                sx={{ mb: 2 }}
              >
                總體評分：{feedback.score}/100 - {
                  feedback.score >= 80 ? "優秀" : 
                  feedback.score >= 60 ? "良好" : 
                  "需要改進"
                }
              </Alert>
              
              <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
                <Tabs 
                  value={activeTab} 
                  onChange={handleTabChange}
                  variant="scrollable"
                  scrollButtons="auto"
                >
                  <Tab icon={<PianoOutlined />} label="和弦分析" />
                  <Tab icon={<GraphicEq />} label="旋律分析" />
                  <Tab icon={<ViewList />} label="結構分析" />
                  <Tab icon={<AutoGraph />} label="建議與警告" />
                </Tabs>
              </Box>
            </Grid>
          </Grid>
          
          {/* 基本信息 */}
          <Box sx={{ mb: 3 }}>
            <Grid container spacing={2}>
              <Grid item xs={6} sm={3}>
                <Paper elevation={0} sx={{ p: 2, bgcolor: 'background.default', height: '100%' }}>
                  <Typography variant="body2" color="text.secondary">調性</Typography>
                  <Typography variant="h6">{feedback.key}</Typography>
                </Paper>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Paper elevation={0} sx={{ p: 2, bgcolor: 'background.default', height: '100%' }}>
                  <Typography variant="body2" color="text.secondary">速度</Typography>
                  <Typography variant="h6">{feedback.tempo || 'N/A'} BPM</Typography>
                </Paper>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Paper elevation={0} sx={{ p: 2, bgcolor: 'background.default', height: '100%' }}>
                  <Typography variant="body2" color="text.secondary">拍號</Typography>
                  <Typography variant="h6">{feedback.timeSignature || 'N/A'}</Typography>
                </Paper>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Paper elevation={0} sx={{ p: 2, bgcolor: 'background.default', height: '100%' }}>
                  <Typography variant="body2" color="text.secondary">和弦數</Typography>
                  <Typography variant="h6">
                    {feedback.chords.length}
                  </Typography>
                </Paper>
              </Grid>
            </Grid>
          </Box>
          
          {/* 內容區域 - 根據當前選中的標籤顯示不同內容 */}
          {activeTab === 0 && (
            <>
              {/* 和弦分析標籤 */}
              {renderChordProgression()}
              {renderHarmonyAnalysis()}
            </>
          )}
          
          {activeTab === 1 && (
            <>
              {/* 旋律分析標籤 */}
              {renderPianoRoll()}
              {renderMelodyAnalysis()}
            </>
          )}
          
          {activeTab === 2 && (
            <>
              {/* 結構分析標籤 */}
              {renderStructureAnalysis()}
              
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  詳細結構
                </Typography>
                <Paper variant="outlined" sx={{ p: 2 }}>
                  <List dense>
                    {feedback.structure && Object.entries(feedback.structure).map(([section, measures]) => (
                      <ListItem key={section}>
                        <ListItemText 
                          primary={section.charAt(0).toUpperCase() + section.slice(1)}
                          secondary={`小節 ${measures[0]}-${measures[measures.length - 1] || measures[0]}`}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Paper>
              </Box>
            </>
          )}
          
          {activeTab === 3 && (
            <>
              {/* 建議與警告標籤 */}
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Paper variant="outlined" sx={{ p: 2, height: '100%' }}>
                    <Typography variant="subtitle1" gutterBottom>
                      問題與警告
                    </Typography>
                    <Divider sx={{ mb: 2 }} />
                    
                    {feedback.errors.length === 0 && feedback.warnings.length === 0 ? (
                      <Typography variant="body2" color="text.secondary">
                        未發現嚴重問題。
                      </Typography>
                    ) : (
                      <List dense disablePadding>
                        {feedback.errors.map((error, index) => (
                          <ListItem key={`error-${index}`}>
                            <ListItemText 
                              primary={error} 
                              primaryTypographyProps={{ color: 'error' }}
                            />
                          </ListItem>
                        ))}
                        
                        {feedback.warnings.map((warning, index) => (
                          <ListItem key={`warning-${index}`}>
                            <ListItemText 
                              primary={warning} 
                              primaryTypographyProps={{ color: 'warning.main' }}
                            />
                          </ListItem>
                        ))}
                      </List>
                    )}
                  </Paper>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Paper variant="outlined" sx={{ p: 2 }}>
                    <Typography variant="subtitle1" gutterBottom>
                      建議與改進
                    </Typography>
                    <Divider sx={{ mb: 2 }} />
                    
                    <List dense disablePadding>
                      {feedback.suggestions.map((suggestion, index) => (
                        <ListItem key={`suggestion-${index}`}>
                          <ListItemText 
                            primary={suggestion} 
                            primaryTypographyProps={{ color: 'primary' }}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Paper>
                </Grid>
              </Grid>
            </>
          )}
          
          <Grid item xs={12}>
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                提出具體問題：
              </Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <TextField
                  fullWidth
                  size="small"
                  placeholder="例如：如何改進副歌部分的和聲？"
                  value={customQuery}
                  onChange={(e) => setCustomQuery(e.target.value)}
                  disabled={analyzing}
                />
                <Button 
                  variant="outlined" 
                  onClick={handleCustomQuery}
                  disabled={analyzing || !customQuery.trim()}
                >
                  詢問
                </Button>
              </Box>
            </Box>
          </Grid>
        </>
      )}
    </Paper>
  );
};

export default TheoryAnalyzer; 