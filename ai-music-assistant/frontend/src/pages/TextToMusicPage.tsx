import {
  Box,
  Button,
  Grid,
  Paper,
  Typography
} from '@mui/material';
import React, { useEffect, useState } from 'react';
// import type { Theme } from '@mui/material/styles';
import * as Tone from 'tone';
// import { Factory } from 'vexflow';
import { musicGenerationService } from '../services/MusicGenerationService';
import { Instrument, MusicGenre, MusicKey, MusicMood, MusicParameters, MusicResult, MusicStyle } from '../types/music';

// 引入新組件
import ExampleTemplates, { ExampleTemplate } from '../components/common/ExampleTemplates';
import ParameterPanel, { Parameter } from '../components/common/ParameterPanel';
import { IStep } from '../components/common/StepProgress';
import WorkflowLayout from '../components/layout/WorkflowLayout';
import MusicPlayer from '../components/MusicPlayer';
import ProgressIndicator, { ProcessStage } from '../components/ProgressIndicator';

// 確保能夠識別 AudioContext 和相關類型
declare global {
  interface Window {
    AudioContext: typeof AudioContext;
    webkitAudioContext: typeof AudioContext;
  }
}

// 聲明 setAudioContext 可以接受空值
declare module 'tone/build/esm/core/context/AudioContext' {
  interface AudioContextConstructor {
    new(contextOptions?: AudioContextOptions): AudioContext;
  }
}

// 定義工作流步驟
const WORKFLOW_STEPS: IStep[] = [
  { label: '描述音樂', description: '用文字描述您想要創作的音樂', status: 'active' },
  { label: '設置參數', description: '調整音樂生成的相關參數', status: 'pending' },
  { label: '生成音樂', description: '根據您的描述和參數生成音樂', status: 'pending' },
  { label: '編輯與分享', description: '編輯生成的音樂並分享您的創作', status: 'pending' }
];

// 定義處理階段
const PROCESS_STAGES: ProcessStage[] = [
  { id: 'prepare', label: '準備模型', status: 'pending' },
  { id: 'analyze', label: '分析文本描述', status: 'pending' },
  { id: 'generate', label: '創作音樂', status: 'pending' },
  { id: 'arrange', label: '音樂編排', status: 'pending' },
  { id: 'finalize', label: '最終處理', status: 'pending' }
];

// 範例模板
const EXAMPLE_TEMPLATES: ExampleTemplate[] = [
  {
    id: 'peaceful-piano',
    title: '舒緩鋼琴曲',
    description: '輕柔舒緩的鋼琴旋律，適合放鬆和冥想',
    category: 'Text2Music',
    difficulty: 'beginner',
    parameters: {
      description: '舒緩平靜的鋼琴獨奏，帶有溫暖的音色和緩慢的節奏，像一個陽光明媚的早晨',
      duration: 30,
      tempo: 75,
      key: 'C',
      genre: 'classical',
      instruments: ['piano'],
      complexity: 2,
      mood: 'peaceful',
      style: 'normal'
    },
    tags: ['舒緩', '鋼琴', '古典']
  },
  {
    id: 'epic-orchestral',
    title: '史詩管弦樂',
    description: '氣勢磅礴的管弦樂，適合壯麗場景或電影配樂',
    category: 'Text2Music',
    difficulty: 'intermediate',
    parameters: {
      description: '宏偉壯觀的管弦樂曲，有強烈的打擊樂和銅管樂器，充滿史詩感和激情',
      duration: 45,
      tempo: 110,
      key: 'D',
      genre: 'classical',
      instruments: ['strings', 'brass', 'drums'],
      complexity: 4,
      mood: 'epic',
      style: 'cinematic'
    },
    tags: ['史詩', '管弦樂', '電影']
  },
  {
    id: 'pop-song',
    title: '流行歌曲',
    description: '現代流行樂風格，朗朗上口的旋律與節奏',
    category: 'Text2Music',
    difficulty: 'beginner',
    parameters: {
      description: '充滿活力的流行歌曲，有朗朗上口的旋律、節奏吉他和現代鼓點',
      duration: 60,
      tempo: 120,
      key: 'G',
      genre: 'pop',
      instruments: ['piano', 'guitar', 'bass', 'drums'],
      complexity: 3,
      mood: 'happy',
      style: 'normal'
    },
    tags: ['流行', '輕快', '現代']
  }
];

// 定義初始參數
const initialParameters: MusicParameters = {
  description: '',
  duration: 30,
  tempo: 120,
  key: 'C' as MusicKey,
  genre: 'pop' as MusicGenre,
  instruments: ['piano' as Instrument],
  complexity: 3,
  mood: 'happy' as MusicMood,
  style: 'normal' as MusicStyle
};

interface TextToMusicPageProps {}

const TextToMusicPage: React.FC<TextToMusicPageProps> = () => {
  // 工作流狀態
  const [steps, setSteps] = useState<IStep[]>(WORKFLOW_STEPS);
  const [activeStep, setActiveStep] = useState(0);
  
  // 參數狀態
  const [parameters, setParameters] = useState<MusicParameters>(initialParameters);
  const [showTutorials, setShowTutorials] = useState(true);

  // 處理狀態
  const [processingStages, setProcessingStages] = useState<ProcessStage[]>(PROCESS_STAGES);
  const [currentProcessStage, setCurrentProcessStage] = useState(0);
  const [totalProgress, setTotalProgress] = useState(0);
  const [generating, setGenerating] = useState(false);
  
  // 結果狀態
  const [result, setResult] = useState<MusicResult | null>(null);
  const [feedbackMessage, setFeedbackMessage] = useState<any>(null);

  // 初始化音頻上下文
  useEffect(() => {
    const initAudioContext = async () => {
      try {
        if (Tone.context.state !== 'running') {
          await Tone.start();
          await Tone.context.resume();
        }
      } catch (error) {
        console.error('初始化音頻上下文時出錯:', error);
        setFeedbackMessage({
          message: '初始化音頻上下文失敗',
          type: 'error',
          details: '您的瀏覽器可能不支持音頻功能',
          solution: '請嘗試使用最新版本的Chrome或Firefox瀏覽器'
        });
      }
    };

    initAudioContext();
  }, []);

  // 參數變更處理函數
  const handleParameterChange = (id: string, value: any) => {
    setParameters(prevParams => ({
      ...prevParams,
      [id]: value
    }));
  };

  // 步驟導航處理函數
  const handleNextStep = () => {
    if (activeStep === 0 && !parameters.description) {
      setFeedbackMessage({
        message: '請輸入音樂描述',
        type: 'warning',
        solution: '添加一些文字來描述您想要的音樂風格和情感'
      });
      return;
    }
    
    if (activeStep < steps.length - 1) {
      // 更新步驟狀態
      const updatedSteps = [...steps];
      updatedSteps[activeStep].status = 'completed';
      updatedSteps[activeStep + 1].status = 'active';
      setSteps(updatedSteps);
      
      // 第二步到第三步時開始生成音樂
      if (activeStep === 1) {
        handleGenerate();
      }
      
      setActiveStep(prevStep => prevStep + 1);
    }
  };

  const handlePrevStep = () => {
    if (activeStep > 0) {
      // 更新步驟狀態
      const updatedSteps = [...steps];
      updatedSteps[activeStep].status = 'pending';
      updatedSteps[activeStep - 1].status = 'active';
      setSteps(updatedSteps);
      
      setActiveStep(prevStep => prevStep - 1);
    }
  };

  // 音樂生成處理函數
  const handleGenerate = async () => {
    try {
      if (Tone.context.state !== 'running') {
        await Tone.start();
        await Tone.context.resume();
      }
      
      setGenerating(true);
      
      // 模擬處理階段和進度
      simulateProcessingProgress();
      
      const requestParams = {
        text: parameters.description || '',
        parameters: {
          description: parameters.description || '',
          tempo: parameters.tempo,
          key: parameters.key,
          genre: parameters.genre,
          instruments: parameters.instruments,
          duration: parameters.duration,
          complexity: parameters.complexity,
          mood: parameters.mood,
          style: parameters.style
        }
      };
      
      // 實際API調用
      const response = await musicGenerationService.generateMusicFromText(
        requestParams.text,
        requestParams.parameters
      );
      
      const resultData = await musicGenerationService.getMusicResult(response.command_id);
      setResult(resultData);
      
      // 更新步驟狀態以顯示成功
      const updatedSteps = [...steps];
      updatedSteps[2].status = 'completed';
      updatedSteps[3].status = 'active';
      setSteps(updatedSteps);
      
      // 顯示成功消息
      setFeedbackMessage({
        message: '音樂生成成功',
        type: 'success',
        details: '您可以播放、編輯或下載生成的音樂'
      });
      
    } catch (error) {
      console.error('生成音樂時出錯:', error);
      
      // 更新步驟狀態以顯示錯誤
      const updatedSteps = [...steps];
      updatedSteps[2].status = 'error';
      setSteps(updatedSteps);
      
      // 顯示錯誤消息
      setFeedbackMessage({
        message: '生成音樂失敗',
        type: 'error',
        details: error instanceof Error ? error.message : '發生未知錯誤',
        solution: '請檢查網絡連接並嘗試使用更簡單的描述'
      });
      
    } finally {
      setGenerating(false);
      // 結束進度模擬
      setCurrentProcessStage(PROCESS_STAGES.length - 1);
      setTotalProgress(100);
    }
  };

  // 模擬處理進度的函數
  const simulateProcessingProgress = () => {
    let stageIndex = 0;
    const stagesCount = PROCESS_STAGES.length;
    
    // 更新第一個階段狀態
    const firstStageUpdate = [...PROCESS_STAGES];
    firstStageUpdate[0].status = 'active';
    setProcessingStages(firstStageUpdate);
    
    const interval = setInterval(() => {
      // 更新當前階段的進度
      const progressIncrement = Math.random() * 5 + 3; // 3-8%
      setTotalProgress(prev => {
        const maxForStage = ((stageIndex + 1) / stagesCount) * 100;
        return Math.min(prev + progressIncrement, maxForStage - 5);
      });
      
      // 檢查是否需要前進到下一階段
      if (totalProgress >= (stageIndex / stagesCount) * 100 + 30) {
        if (stageIndex < stagesCount - 1) {
          stageIndex++;
          setCurrentProcessStage(stageIndex);
          
          // 更新階段狀態
          const updatedStages = [...processingStages];
          if (stageIndex > 0) {
            updatedStages[stageIndex - 1].status = 'completed';
          }
          updatedStages[stageIndex].status = 'active';
          setProcessingStages(updatedStages);
        }
      }
      
      // 生成完成或取消時停止模擬
      if (!generating || stageIndex === stagesCount - 1 && totalProgress >= 95) {
        clearInterval(interval);
      }
    }, 800);
    
    // 保存interval ID以便清理
    return () => clearInterval(interval);
  };

  // 範例模板選擇處理函數
  const handleTemplateSelect = (template: ExampleTemplate) => {
    setParameters(template.parameters as MusicParameters);
    setFeedbackMessage({
      message: `已選擇「${template.title}」模板`,
      type: 'info',
      details: '模板參數已自動填充'
    });
  };

  // 關閉教學提示
  const handleTutorialDismiss = () => {
    setShowTutorials(false);
  };

  // 關閉反饋消息
  const handleFeedbackClose = () => {
    setFeedbackMessage(null);
  };

  // 將參數轉換為Parameter[]格式
  const getDescriptionParameter = (): Parameter[] => {
    return [
      {
        id: 'description',
        label: '音樂描述',
        type: 'text',
        value: parameters.description,
        required: true,
        placeholder: '請描述您想要的音樂，例如：輕柔舒緩的鋼琴音樂，帶有一絲憂傷的情感...',
        helper: '描述越詳細，生成的音樂效果越好'
      }
    ];
  };

  const getBasicParameters = (): Parameter[] => {
    return [
      {
        id: 'genre',
        label: '音樂風格',
        type: 'select',
        value: parameters.genre,
        options: [
          { value: 'pop', label: '流行音樂' },
          { value: 'rock', label: '搖滾音樂' },
          { value: 'classical', label: '古典音樂' },
          { value: 'jazz', label: '爵士樂' },
          { value: 'electronic', label: '電子音樂' },
          { value: 'folk', label: '民謠' },
          { value: 'blues', label: '藍調' }
        ]
      },
      {
        id: 'mood',
        label: '情感氛圍',
        type: 'select',
        value: parameters.mood,
        options: [
          { value: 'happy', label: '歡快' },
          { value: 'sad', label: '憂傷' },
          { value: 'peaceful', label: '平靜' },
          { value: 'energetic', label: '活力' },
          { value: 'epic', label: '壯麗' }
        ]
      },
      {
        id: 'key',
        label: '調性',
        type: 'select',
        value: parameters.key,
        options: [
          { value: 'C', label: 'C 大調' },
          { value: 'G', label: 'G 大調' },
          { value: 'D', label: 'D 大調' },
          { value: 'A', label: 'A 大調' },
          { value: 'F', label: 'F 大調' },
          { value: 'Bb', label: 'Bb 大調' },
          { value: 'Am', label: 'A 小調' },
          { value: 'Em', label: 'E 小調' },
          { value: 'Dm', label: 'D 小調' }
        ]
      },
      {
        id: 'duration',
        label: '時長 (秒)',
        type: 'number',
        value: parameters.duration,
        min: 15,
        max: 180,
        step: 15
      }
    ];
  };

  const getAdvancedParameters = (): Parameter[] => {
    return [
      {
        id: 'tempo',
        label: '速度 (BPM)',
        type: 'slider',
        value: parameters.tempo,
        min: 60,
        max: 180,
        step: 5,
        marks: [
          { value: 60, label: '60' },
          { value: 120, label: '120' },
          { value: 180, label: '180' }
        ]
      },
      {
        id: 'complexity',
        label: '複雜度',
        type: 'slider',
        value: parameters.complexity,
        min: 1,
        max: 5,
        step: 1,
        marks: [
          { value: 1, label: '簡單' },
          { value: 3, label: '中等' },
          { value: 5, label: '複雜' }
        ]
      },
      {
        id: 'instruments',
        label: '樂器',
        type: 'chips',
        value: parameters.instruments,
        options: [
          { value: 'piano', label: '鋼琴' },
          { value: 'guitar', label: '吉他' },
          { value: 'strings', label: '弦樂' },
          { value: 'bass', label: '貝斯' },
          { value: 'drums', label: '鼓組' },
          { value: 'violin', label: '小提琴' },
          { value: 'cello', label: '大提琴' },
          { value: 'flute', label: '長笛' },
          { value: 'trumpet', label: '小號' },
          { value: 'saxophone', label: '薩克斯風' }
        ],
        helper: '選擇多個樂器來創建更豐富的音樂編排'
      },
      {
        id: 'style',
        label: '演奏風格',
        type: 'select',
        value: parameters.style,
        options: [
          { value: 'normal', label: '標準' },
          { value: 'cinematic', label: '電影配樂' },
          { value: 'ambient', label: '環境音樂' },
          { value: 'lofi', label: 'Lo-Fi' },
          { value: 'orchestral', label: '管弦樂' }
        ]
      }
    ];
  };

  // 教學提示內容
  const tutorials = [
    {
      title: '使用文字生成音樂',
      description: '通過描述您想要的音樂風格、情感和樂器，AI 將為您創作獨特的音樂作品',
      steps: [
        '輸入詳細的音樂描述，包括風格、情感和樂器等',
        '調整基本和高級參數以獲得更好的結果',
        '生成音樂後，您可以播放、編輯和分享您的創作'
      ],
      variant: 'tutorial' as const
    }
  ];

  // 渲染不同步驟的內容
  const renderStepContent = () => {
    switch (activeStep) {
      case 0: // 描述音樂
        return (
          <Grid container spacing={4}>
            <Grid item xs={12} md={7}>
              <ParameterPanel
                title="描述您想要的音樂"
                description="使用詳細的描述來幫助 AI 理解您想要的音樂風格、情感和樂器"
                parameters={getDescriptionParameter()}
                onChange={handleParameterChange}
                columns={1}
              />
            </Grid>
            <Grid item xs={12} md={5}>
              <ExampleTemplates
                templates={EXAMPLE_TEMPLATES}
                onSelect={handleTemplateSelect}
                columns={1}
              />
            </Grid>
          </Grid>
        );
        
      case 1: // 設置參數
        return (
          <Grid container spacing={4}>
            <Grid item xs={12} md={6}>
              <ParameterPanel
                title="基本參數"
                parameters={getBasicParameters()}
                onChange={handleParameterChange}
                columns={2}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <ParameterPanel
                title="高級參數"
                parameters={getAdvancedParameters()}
                onChange={handleParameterChange}
                columns={2}
              />
            </Grid>
          </Grid>
        );
        
      case 2: // 生成音樂
        return (
          <Paper elevation={1} sx={{ p: 3 }}>
            <Box sx={{ maxWidth: 600, mx: 'auto', textAlign: 'center', py: 2 }}>
              <Typography variant="h6" gutterBottom>
                正在生成您的音樂
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                正在根據您的描述和參數創作音樂，這可能需要一些時間...
              </Typography>
              
              <ProgressIndicator
                stages={processingStages}
                currentStage={currentProcessStage}
                totalProgress={totalProgress}
                variant="stages"
                size="medium"
              />
            </Box>
          </Paper>
        );
        
      case 3: // 編輯與分享
        return (
          <Paper elevation={1} sx={{ p: 3 }}>
            {result?.music_data ? (
              <Grid container spacing={4}>
                <Grid item xs={12} md={5}>
                  <Box sx={{ textAlign: 'center', mb: 3 }}>
                    <img 
                      src={result.music_data.cover_image || '/images/placeholder.png'} 
                      alt="音樂封面" 
                      style={{ 
                        width: '100%', 
                        maxWidth: 300, 
                        borderRadius: 8,
                        boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
                      }} 
                    />
                  </Box>
                  
                  <Typography variant="h6" gutterBottom>
                    生成的音樂信息
                  </Typography>
                  
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      <strong>描述:</strong> {parameters.description}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      <strong>風格:</strong> {parameters.genre}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      <strong>調性:</strong> {parameters.key}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      <strong>速度:</strong> {parameters.tempo} BPM
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      <strong>時長:</strong> {parameters.duration} 秒
                    </Typography>
                  </Box>
                </Grid>
                
                <Grid item xs={12} md={7}>
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="h6" gutterBottom>
                      播放與編輯
                    </Typography>
                    
                    {result.music_data.audio_data && (
                      <MusicPlayer 
                        audioUrl={result.music_data.audio_data} 
                        title="生成的音樂" 
                      />
                    )}
                  </Box>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Button 
                      variant="outlined" 
                      onClick={() => {/* 打開編輯器 */}}
                    >
                      編輯音樂
                    </Button>
                    
                    <Button 
                      variant="contained" 
                      onClick={() => {/* 下載音樂 */}}
                    >
                      下載音樂
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            ) : (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="h6" color="text.secondary">
                  尚未生成音樂
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  請返回上一步並生成音樂
                </Typography>
              </Box>
            )}
          </Paper>
        );
        
      default:
        return null;
    }
  };

  return (
    <WorkflowLayout
      title="文字生成音樂"
      description="通過文字描述來創作獨特的音樂作品，讓AI幫您將想法轉化為優美的旋律"
      steps={steps}
      activeStep={activeStep}
      onNextStep={handleNextStep}
      onPrevStep={handlePrevStep}
      isNextDisabled={activeStep === 2 && generating}
      isPrevDisabled={activeStep === 2 && generating}
      isProcessing={generating}
      tutorials={showTutorials ? tutorials : []}
      showTutorial={showTutorials}
      onTutorialDismiss={handleTutorialDismiss}
      feedbackMessage={feedbackMessage}
      onFeedbackClose={handleFeedbackClose}
    >
      {renderStepContent()}
    </WorkflowLayout>
  );
};

export default TextToMusicPage; 