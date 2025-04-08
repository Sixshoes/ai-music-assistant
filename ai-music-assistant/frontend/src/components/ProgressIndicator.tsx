import { Check, Pending } from '@mui/icons-material';
import {
    Box,
    CircularProgress,
    Divider,
    Fade,
    LinearProgress,
    Paper,
    Stack,
    Typography,
    useTheme
} from '@mui/material';
import React from 'react';

// 定義階段狀態類型
export type StageStatus = 'pending' | 'active' | 'completed' | 'error';

// 定義處理階段接口
export interface ProcessStage {
  id: string;
  label: string;
  status: StageStatus;
  progress?: number; // 0-100
  message?: string;
}

// 組件屬性接口
interface ProgressIndicatorProps {
  stages: ProcessStage[];
  currentStage: number;
  totalProgress?: number; // 0-100
  showDetails?: boolean;
  variant?: 'linear' | 'circular' | 'stages';
  size?: 'small' | 'medium' | 'large';
}

/**
 * 增強型進度指示器組件
 * 顯示多階段處理流程的進度，提供詳細的視覺反饋
 */
const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
  stages,
  currentStage,
  totalProgress = 0,
  showDetails = true,
  variant = 'stages',
  size = 'medium'
}) => {
  const theme = useTheme();
  
  // 獲取尺寸相關值
  const getDimension = () => {
    switch (size) {
      case 'small':
        return { 
          height: 4, 
          circleSize: 40, 
          fontSize: 'caption.fontSize', 
          spacing: 1,
          padding: 1.5
        };
      case 'large':
        return { 
          height: 8, 
          circleSize: 80, 
          fontSize: 'h6.fontSize', 
          spacing: 3,
          padding: 3
        };
      case 'medium':
      default:
        return { 
          height: 6, 
          circleSize: 60, 
          fontSize: 'body1.fontSize', 
          spacing: 2,
          padding: 2
        };
    }
  };
  
  const dimensions = getDimension();
  
  // 圓形進度指示器
  if (variant === 'circular') {
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', p: dimensions.padding }}>
        <Box sx={{ position: 'relative', display: 'inline-flex' }}>
          <CircularProgress 
            variant="determinate" 
            value={totalProgress} 
            size={dimensions.circleSize} 
            thickness={4}
          />
          <Box
            sx={{
              top: 0,
              left: 0,
              bottom: 0,
              right: 0,
              position: 'absolute',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Typography
              variant="caption"
              component="div"
              sx={{ fontSize: dimensions.fontSize }}
            >
              {`${Math.round(totalProgress)}%`}
            </Typography>
          </Box>
        </Box>
        
        {showDetails && currentStage < stages.length && (
          <Typography
            variant="body2"
            sx={{ 
              mt: 1, 
              color: 'text.secondary',
              textAlign: 'center'
            }}
          >
            {stages[currentStage].label}
            {stages[currentStage].message && (
              <Typography 
                component="div" 
                variant="caption" 
                sx={{ color: 'text.secondary', mt: 0.5 }}
              >
                {stages[currentStage].message}
              </Typography>
            )}
          </Typography>
        )}
      </Box>
    );
  }
  
  // 線性進度指示器
  if (variant === 'linear') {
    return (
      <Box sx={{ width: '100%', p: dimensions.padding }}>
        <LinearProgress 
          variant="determinate" 
          value={totalProgress} 
          sx={{ height: dimensions.height, borderRadius: dimensions.height / 2 }}
        />
        
        {showDetails && (
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
            <Typography variant="body2" color="text.secondary">
              {currentStage < stages.length ? stages[currentStage].label : '完成'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {`${Math.round(totalProgress)}%`}
            </Typography>
          </Box>
        )}
        
        {showDetails && currentStage < stages.length && stages[currentStage].message && (
          <Typography variant="caption" color="text.secondary">
            {stages[currentStage].message}
          </Typography>
        )}
      </Box>
    );
  }
  
  // 階段式進度指示器 (默認)
  return (
    <Paper elevation={0} sx={{ p: dimensions.padding, bgcolor: 'background.default', width: '100%' }}>
      {/* 總進度條 */}
      <LinearProgress 
        variant="determinate" 
        value={totalProgress} 
        sx={{ 
          height: dimensions.height, 
          borderRadius: dimensions.height / 2,
          mb: 2
        }}
      />
      
      {/* 階段列表 */}
      {showDetails && (
        <Stack spacing={1} divider={<Divider flexItem />}>
          {stages.map((stage, index) => (
            <Fade in={true} key={stage.id} timeout={300} style={{ transitionDelay: `${index * 100}ms` }}>
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center',
                opacity: stage.status === 'pending' ? 0.6 : 1
              }}>
                {/* 階段狀態圖標 */}
                <Box 
                  sx={{ 
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    width: 24,
                    height: 24,
                    borderRadius: '50%',
                    bgcolor: stage.status === 'completed' 
                      ? 'success.main' 
                      : stage.status === 'error'
                      ? 'error.main'
                      : stage.status === 'active'
                      ? 'primary.main'
                      : 'action.disabled',
                    mr: 1.5,
                    color: 'white'
                  }}
                >
                  {stage.status === 'completed' ? (
                    <Check fontSize="small" />
                  ) : stage.status === 'active' ? (
                    <CircularProgress size={16} color="inherit" />
                  ) : (
                    <Pending fontSize="small" />
                  )}
                </Box>
                
                {/* 階段信息 */}
                <Box sx={{ flex: 1 }}>
                  <Typography 
                    variant="body2" 
                    sx={{ 
                      fontWeight: stage.status === 'active' ? 600 : 400,
                      color: stage.status === 'error' 
                        ? 'error.main' 
                        : stage.status === 'active'
                        ? 'text.primary'
                        : 'text.secondary'
                    }}
                  >
                    {stage.label}
                  </Typography>
                  
                  {stage.message && stage.status === 'active' && (
                    <Typography variant="caption" color="text.secondary">
                      {stage.message}
                    </Typography>
                  )}
                </Box>
                
                {/* 階段進度 */}
                {stage.status === 'active' && stage.progress !== undefined && (
                  <Typography variant="caption" color="primary" sx={{ ml: 1 }}>
                    {Math.round(stage.progress)}%
                  </Typography>
                )}
              </Box>
            </Fade>
          ))}
        </Stack>
      )}
    </Paper>
  );
};

export default ProgressIndicator; 