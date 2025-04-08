import { Close } from '@mui/icons-material';
import { Alert, AlertColor, AlertTitle, Box, IconButton, Snackbar, Typography } from '@mui/material';
import React from 'react';

export type FeedbackType = AlertColor | 'info' | 'success' | 'warning' | 'error';

export interface FeedbackToastProps {
  open: boolean;
  message: string;
  type: FeedbackType;
  details?: string;
  solution?: string;
  duration?: number;
  position?: 'top' | 'top-right' | 'top-left' | 'bottom' | 'bottom-right' | 'bottom-left' | 'center';
  onClose: () => void;
}

/**
 * 反饋通知組件
 * 顯示操作結果、錯誤、警告等反饋信息
 */
const FeedbackToast: React.FC<FeedbackToastProps> = ({
  open,
  message,
  type = 'info',
  details,
  solution,
  duration = 6000,
  position = 'bottom',
  onClose
}) => {
  // 根據 position 屬性設置 Snackbar 的定位
  const getSnackbarPosition = () => {
    switch (position) {
      case 'top':
        return { vertical: 'top', horizontal: 'center' };
      case 'top-right':
        return { vertical: 'top', horizontal: 'right' };
      case 'top-left':
        return { vertical: 'top', horizontal: 'left' };
      case 'bottom':
        return { vertical: 'bottom', horizontal: 'center' };
      case 'bottom-right':
        return { vertical: 'bottom', horizontal: 'right' };
      case 'bottom-left':
        return { vertical: 'bottom', horizontal: 'left' };
      case 'center':
        return { vertical: 'top', horizontal: 'center' };
      default:
        return { vertical: 'bottom', horizontal: 'center' };
    }
  };
  
  const { vertical, horizontal } = getSnackbarPosition() as {
    vertical: 'top' | 'bottom';
    horizontal: 'left' | 'center' | 'right';
  };

  return (
    <Snackbar
      open={open}
      autoHideDuration={duration}
      onClose={onClose}
      anchorOrigin={{ vertical, horizontal }}
      sx={{
        maxWidth: '100%',
        width: { xs: '95%', sm: '400px' },
        '& .MuiPaper-root': {
          width: '100%'
        }
      }}
    >
      <Alert
        severity={type}
        onClose={onClose}
        sx={{
          width: '100%',
          boxShadow: 3,
          '& .MuiAlert-message': {
            width: '100%'
          }
        }}
        action={
          <IconButton
            aria-label="close"
            color="inherit"
            size="small"
            onClick={onClose}
          >
            <Close fontSize="small" />
          </IconButton>
        }
      >
        <AlertTitle sx={{ fontWeight: 600 }}>{message}</AlertTitle>
        
        {details && (
          <Typography variant="body2" sx={{ mt: 0.5, mb: 1 }}>
            {details}
          </Typography>
        )}
        
        {solution && (
          <Box sx={{ mt: 1, pt: 1, borderTop: '1px solid rgba(0,0,0,0.1)' }}>
            <Typography variant="body2" fontWeight="500">
              建議解決方法: {solution}
            </Typography>
          </Box>
        )}
      </Alert>
    </Snackbar>
  );
};

export default FeedbackToast; 