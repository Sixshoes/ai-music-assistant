import { NavigateNext } from '@mui/icons-material';
import { Box, Button, Container, Paper, Typography, useMediaQuery, useTheme } from '@mui/material';
import React, { ReactNode, useEffect, useState } from 'react';
import FeedbackToast, { FeedbackType } from '../common/FeedbackToast';
import StepProgress, { IStep } from '../common/StepProgress';
import TutorialCard from '../common/TutorialCard';

// 定義工作流布局的屬性接口
interface WorkflowLayoutProps {
  title: string;
  description?: string;
  steps: IStep[];
  activeStep: number;
  children: ReactNode;
  onNextStep?: () => void;
  onPrevStep?: () => void;
  isNextDisabled?: boolean;
  isPrevDisabled?: boolean;
  isProcessing?: boolean;
  tutorials?: {
    title: string;
    description: string;
    steps?: string[];
    image?: string;
    variant?: 'tip' | 'tutorial' | 'example';
  }[];
  showTutorial?: boolean;
  onTutorialDismiss?: () => void;
  feedbackMessage?: {
    message: string;
    type: FeedbackType;
    details?: string;
    solution?: string;
  };
  onFeedbackClose?: () => void;
}

/**
 * 工作流布局組件
 * 為三大功能（文字生成音樂、旋律編曲和音樂分析）提供統一的頁面結構
 * 整合了步驟導航、教學提示和反饋通知
 */
const WorkflowLayout: React.FC<WorkflowLayoutProps> = ({
  title,
  description,
  steps,
  activeStep,
  children,
  onNextStep,
  onPrevStep,
  isNextDisabled = false,
  isPrevDisabled = false,
  isProcessing = false,
  tutorials = [],
  showTutorial = true,
  onTutorialDismiss,
  feedbackMessage,
  onFeedbackClose,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isTablet = useMediaQuery(theme.breakpoints.between('sm', 'md'));
  
  const [showFeedback, setShowFeedback] = useState(!!feedbackMessage);
  // 滾動位置追蹤
  const [scrolledDown, setScrolledDown] = useState(false);

  // 管理反饋通知的顯示
  const handleFeedbackClose = () => {
    setShowFeedback(false);
    if (onFeedbackClose) {
      onFeedbackClose();
    }
  };
  
  // 監聽滾動，以便在手機上顯示固定的導航按鈕
  useEffect(() => {
    const handleScroll = () => {
      const scrolled = window.scrollY > 100;
      setScrolledDown(scrolled);
    };
    
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <Container 
      maxWidth="lg" 
      sx={{ 
        py: isMobile ? 2 : 4,
        px: isMobile ? 1 : 2
      }}
    >
      {/* 頁面標題 */}
      <Typography 
        variant={isMobile ? "h5" : "h4"} 
        component="h1" 
        gutterBottom 
        sx={{ 
          mb: isMobile ? 1 : 2,
          fontSize: isMobile ? '1.5rem' : undefined
        }}
      >
        {title}
      </Typography>
      
      {description && (
        <Typography 
          variant="body1" 
          color="text.secondary" 
          sx={{ 
            mb: isMobile ? 2 : 4,
            fontSize: isMobile ? '0.9rem' : undefined
          }}
        >
          {description}
        </Typography>
      )}
      
      {/* 步驟導航 */}
      <Paper 
        elevation={1} 
        sx={{ 
          p: isMobile ? 2 : 3, 
          mb: isMobile ? 2 : 4,
          borderRadius: isMobile ? '8px' : '12px'
        }}
      >
        <StepProgress 
          steps={steps} 
          activeStep={activeStep} 
          vertical={isMobile || isTablet}
          showContent={true}
        />
      </Paper>
      
      {/* 教學卡片 */}
      {showTutorial && tutorials.length > 0 && (
        <Box sx={{ mb: isMobile ? 2 : 4 }}>
          {tutorials.map((tutorial, index) => (
            <TutorialCard
              key={index}
              title={tutorial.title}
              description={tutorial.description}
              steps={tutorial.steps}
              image={tutorial.image}
              variant={tutorial.variant}
              dismissible={true}
              onDismiss={onTutorialDismiss}
            />
          ))}
        </Box>
      )}
      
      {/* 主要內容區域 */}
      <Box sx={{ mb: isMobile ? 7 : 4 }}>
        {children}
      </Box>
      
      {/* 導航按鈕 - 桌面版 */}
      {!isMobile && (
        <Box 
          sx={{ 
            display: 'flex', 
            justifyContent: 'space-between',
            pt: 2,
            borderTop: `1px solid ${theme.palette.divider}`
          }}
        >
          <Button
            variant="outlined"
            onClick={onPrevStep}
            disabled={isPrevDisabled || isProcessing || activeStep === 0}
            size="large"
          >
            上一步
          </Button>
          
          <Button
            variant="contained"
            endIcon={<NavigateNext />}
            onClick={onNextStep}
            disabled={isNextDisabled || isProcessing}
            size="large"
          >
            {activeStep >= steps.length - 1 ? '完成' : '下一步'}
          </Button>
        </Box>
      )}
      
      {/* 導航按鈕 - 移動版（固定在底部） */}
      {isMobile && (
        <Box 
          sx={{ 
            position: 'fixed',
            bottom: 0,
            left: 0,
            right: 0,
            display: 'flex', 
            justifyContent: 'space-between',
            padding: '12px 16px',
            backgroundColor: scrolledDown ? theme.palette.background.paper : 'transparent',
            boxShadow: scrolledDown ? '0 -2px 10px rgba(0,0,0,0.1)' : 'none',
            transition: 'background-color 0.3s, box-shadow 0.3s',
            zIndex: 100,
          }}
        >
          <Button
            variant="outlined"
            onClick={onPrevStep}
            disabled={isPrevDisabled || isProcessing || activeStep === 0}
            sx={{ 
              minWidth: '100px',
              minHeight: '44px',
              borderRadius: '22px'
            }}
            color="inherit"
          >
            上一步
          </Button>
          
          <Button
            variant="contained"
            endIcon={<NavigateNext />}
            onClick={onNextStep}
            disabled={isNextDisabled || isProcessing}
            sx={{ 
              minWidth: '100px',
              minHeight: '44px',
              borderRadius: '22px'
            }}
            color="primary"
          >
            {activeStep >= steps.length - 1 ? '完成' : '下一步'}
          </Button>
        </Box>
      )}
      
      {/* 反饋通知 */}
      {feedbackMessage && (
        <FeedbackToast
          open={showFeedback}
          message={feedbackMessage.message}
          type={feedbackMessage.type}
          details={feedbackMessage.details}
          solution={feedbackMessage.solution}
          onClose={handleFeedbackClose}
          position={isMobile ? "bottom" : "top-right"}
        />
      )}
    </Container>
  );
};

export default WorkflowLayout; 