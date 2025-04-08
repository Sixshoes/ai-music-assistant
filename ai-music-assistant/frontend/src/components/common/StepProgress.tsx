import { CheckCircle, Error, RadioButtonUnchecked } from '@mui/icons-material';
import { Box, Paper, Step, StepContent, StepLabel, Stepper, Typography, styled } from '@mui/material';
import React from 'react';

// 定義步驟狀態類型
export type StepStatus = 'completed' | 'active' | 'pending' | 'error';

// 定義單個步驟的接口
export interface IStep {
  label: string;
  description?: string;
  status: StepStatus;
}

// 組件屬性接口
interface StepProgressProps {
  steps: IStep[];
  activeStep: number;
  vertical?: boolean;
  showContent?: boolean;
}

// 自定義樣式
const StyledStepLabel = styled(StepLabel)(({ theme }) => ({
  '.MuiStepLabel-label': {
    fontWeight: 600,
  },
  '.MuiStepLabel-label.Mui-active': {
    color: theme.palette.primary.main,
    fontWeight: 700,
  },
  '.MuiStepLabel-label.Mui-completed': {
    color: theme.palette.success.main,
  },
  '.MuiStepLabel-label.Mui-error': {
    color: theme.palette.error.main,
  },
}));

// 自定義圖標
const CustomStepIcon = ({ status }: { status: StepStatus }) => {
  switch (status) {
    case 'completed':
      return <CheckCircle color="success" />;
    case 'error':
      return <Error color="error" />;
    case 'active':
      return <RadioButtonUnchecked color="primary" />;
    default:
      return <RadioButtonUnchecked color="disabled" />;
  }
};

/**
 * 步驟進度指示器組件
 * 提供水平和垂直兩種模式，支持步驟狀態與內容顯示
 */
const StepProgress: React.FC<StepProgressProps> = ({
  steps,
  activeStep,
  vertical = false,
  showContent = true,
}) => {
  return (
    <Box sx={{ width: '100%' }}>
      <Stepper 
        activeStep={activeStep} 
        orientation={vertical ? 'vertical' : 'horizontal'}
        sx={{ mb: 2 }}
      >
        {steps.map((step, index) => (
          <Step key={index} completed={step.status === 'completed'} expanded={showContent && index === activeStep}>
            <StyledStepLabel 
              error={step.status === 'error'}
              StepIconComponent={() => <CustomStepIcon status={step.status} />}
            >
              {step.label}
            </StyledStepLabel>
            
            {vertical && showContent && step.description && (
              <StepContent>
                <Paper elevation={0} sx={{ p: 2, bgcolor: 'background.default', mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    {step.description}
                  </Typography>
                </Paper>
              </StepContent>
            )}
          </Step>
        ))}
      </Stepper>
      
      {!vertical && showContent && steps[activeStep]?.description && (
        <Paper elevation={0} sx={{ p: 2, bgcolor: 'background.default', mt: 2 }}>
          <Typography variant="body2" color="text.secondary">
            {steps[activeStep].description}
          </Typography>
        </Paper>
      )}
    </Box>
  );
};

export default StepProgress; 