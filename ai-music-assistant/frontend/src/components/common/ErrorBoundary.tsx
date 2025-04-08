import { Box, Button, Container, Paper, Typography } from '@mui/material';
import React, { Component, ErrorInfo, ReactNode } from 'react';
import { useAppState } from '../../context/AppStateContext';

interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

/**
 * 錯誤狀態消費者組件 - 用於在錯誤邊界中訪問全局狀態
 */
const ErrorBoundaryContent: React.FC<{
  error: Error | null;
  errorInfo: ErrorInfo | null;
  resetError: () => void;
}> = ({ error, errorInfo, resetError }) => {
  // 使用全局狀態，在需要時可以記錄錯誤或通知用戶
  const { dispatch } = useAppState();
  
  const handleReportError = () => {
    // 可以實現錯誤報告功能
    console.log('報告錯誤:', error, errorInfo);
    
    // 可以在全局狀態中設置錯誤消息
    dispatch({
      type: 'SET_ERROR',
      payload: '應用程序遇到錯誤，我們已經記錄並會盡快修復。'
    });
  };
  
  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Paper
        elevation={3}
        sx={{
          p: 4,
          borderRadius: 2,
          backgroundColor: 'background.paper',
          border: '1px solid',
          borderColor: 'error.main',
        }}
      >
        <Typography variant="h4" color="error" gutterBottom>
          發生錯誤
        </Typography>
        
        <Typography variant="body1" paragraph>
          應用程序遇到了問題。這可能是由於暫時性問題或未預期的錯誤導致的。
        </Typography>
        
        <Box sx={{ my: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1, overflowX: 'auto' }}>
          <Typography variant="body2" component="pre" fontFamily="monospace">
            {error?.toString() || '未知錯誤'}
          </Typography>
          
          {errorInfo && (
            <Typography 
              variant="body2" 
              component="pre" 
              fontFamily="monospace" 
              sx={{ mt: 2, fontSize: '0.75rem' }}
            >
              {errorInfo.componentStack}
            </Typography>
          )}
        </Box>
        
        <Box sx={{ display: 'flex', gap: 2, mt: 3, flexWrap: 'wrap' }}>
          <Button 
            variant="contained" 
            color="primary" 
            onClick={resetError}
          >
            重試
          </Button>
          <Button 
            variant="outlined" 
            color="secondary" 
            onClick={() => window.location.href = '/'}
          >
            返回首頁
          </Button>
          <Button 
            variant="text" 
            color="inherit"
            onClick={handleReportError}
          >
            報告此問題
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

/**
 * 錯誤邊界類組件
 * 用於捕獲子組件樹中的 JavaScript 錯誤
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    // 更新狀態，下一次渲染將顯示後備 UI
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // 可以將錯誤日誌發送到服務
    console.error('ErrorBoundary caught an error', error, errorInfo);
    this.setState({
      errorInfo,
    });
  }

  resetError = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        <ErrorBoundaryContent
          error={this.state.error}
          errorInfo={this.state.errorInfo}
          resetError={this.resetError}
        />
      );
    }

    return this.props.children;
  }
} 