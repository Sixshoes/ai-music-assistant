import { Box, Button, CircularProgress, Fade, Paper, SxProps, Zoom } from '@mui/material';
import { alpha, styled } from '@mui/material/styles';
import { motion } from 'framer-motion';
import React, { ReactNode, useEffect, useState } from 'react';

// 帶有淡入效果的容器
export const FadeInBox = ({ children, delay = 0, ...props }: {
  children: ReactNode;
  delay?: number;
  [key: string]: any;
}) => (
  <Fade in={true} timeout={500} style={{ transitionDelay: `${delay}ms` }}>
    <Box {...props}>
      {children}
    </Box>
  </Fade>
);

// 帶有縮放效果的容器
export const ZoomInBox = ({ children, delay = 0, ...props }: {
  children: ReactNode;
  delay?: number;
  [key: string]: any;
}) => (
  <Zoom in={true} timeout={500} style={{ transitionDelay: `${delay}ms` }}>
    <Box {...props}>
      {children}
    </Box>
  </Zoom>
);

// 帶有高級動畫效果的卡片
export const AnimatedCard = styled(Paper)(({ theme }) => ({
  borderRadius: theme.shape.borderRadius * 1.5,
  transition: 'transform 0.3s ease, box-shadow 0.3s ease',
  '&:hover': {
    transform: 'translateY(-6px)',
    boxShadow: theme.shadows[8],
  },
}));

// 帶有波紋效果的按鈕
export const PulseButton = styled(Button)(({ theme }) => ({
  position: 'relative',
  overflow: 'hidden',
  '&::after': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    background: alpha(theme.palette.primary.main, 0.4),
    opacity: 0,
    borderRadius: 'inherit',
    transform: 'scale(1.5)',
    transition: 'opacity 0.4s ease, transform 0.4s ease',
  },
  '&:hover::after': {
    opacity: 0.15,
    transform: 'scale(1)',
  },
}));

// 帶有載入狀態的按鈕
interface LoadingButtonProps {
  loading?: boolean;
  loadingPosition?: 'start' | 'end' | 'center';
  children: ReactNode;
  startIcon?: ReactNode;
  endIcon?: ReactNode;
  [key: string]: any;
}

export const LoadingButton = ({
  loading = false,
  loadingPosition = 'center',
  children,
  startIcon,
  endIcon,
  ...props
}: LoadingButtonProps) => {
  const renderLoader = () => (
    <CircularProgress
      size={20}
      color="inherit"
      thickness={5}
      sx={{ ml: loadingPosition === 'end' ? 1 : 0, mr: loadingPosition === 'start' ? 1 : 0 }}
    />
  );

  return (
    <Button
      startIcon={loadingPosition === 'start' && loading ? renderLoader() : startIcon}
      endIcon={loadingPosition === 'end' && loading ? renderLoader() : endIcon}
      disabled={loading}
      {...props}
    >
      {loadingPosition === 'center' && loading ? (
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          {renderLoader()}
          <Box component="span" sx={{ ml: 1, opacity: 0.7 }}>
            {children}
          </Box>
        </Box>
      ) : (
        children
      )}
    </Button>
  );
};

// 基於framer-motion的微動畫容器
export const MotionBox = styled(motion.div)({
  display: 'flex',
  width: '100%',
});

// 具有淺入效果的內容容器
export const SlideInContent = ({ children, direction = 'up', delay = 0, duration = 0.5 }: {
  children: ReactNode;
  direction?: 'up' | 'down' | 'left' | 'right';
  delay?: number;
  duration?: number;
}) => {
  const variants = {
    hidden: {
      opacity: 0,
      y: direction === 'up' ? 20 : direction === 'down' ? -20 : 0,
      x: direction === 'left' ? 20 : direction === 'right' ? -20 : 0,
    },
    visible: {
      opacity: 1,
      y: 0,
      x: 0,
      transition: {
        duration,
        delay,
        ease: 'easeOut',
      },
    },
  };

  return (
    <MotionBox
      initial="hidden"
      animate="visible"
      variants={variants}
    >
      {children}
    </MotionBox>
  );
};

// 帶有圈圈加載效果的內容包裝器
export const ContentLoader = ({ 
  loading, 
  children, 
  loaderSize = 40,
  minHeight = 200,
  sx = {}
}: {
  loading: boolean;
  children: ReactNode;
  loaderSize?: number;
  minHeight?: number;
  sx?: SxProps;
}) => {
  const [showContent, setShowContent] = useState(!loading);
  
  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (!loading && !showContent) {
      timer = setTimeout(() => setShowContent(true), 300);
    } else if (loading) {
      setShowContent(false);
    }
    
    return () => {
      if (timer) clearTimeout(timer);
    };
  }, [loading, showContent]);
  
  return (
    <Box sx={{ position: 'relative', minHeight, ...sx }}>
      {loading && (
        <Fade in={loading} timeout={300}>
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: (theme) => alpha(theme.palette.background.paper, 0.7),
              backdropFilter: 'blur(4px)',
              zIndex: 10,
            }}
          >
            <CircularProgress size={loaderSize} />
          </Box>
        </Fade>
      )}
      
      <Fade in={showContent} timeout={500}>
        <Box>
          {children}
        </Box>
      </Fade>
    </Box>
  );
};

// 順序出現的項目列表
export const StaggeredItems = ({ children, baseDelay = 100 }: {
  children: ReactNode[];
  baseDelay?: number;
}) => {
  const containerVariants = {
    hidden: {},
    visible: {
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 10 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {React.Children.map(children, (child, index) => (
        <motion.div
          key={index}
          variants={itemVariants}
          transition={{
            duration: 0.5,
            delay: (index * baseDelay) / 1000,
            ease: 'easeOut',
          }}
        >
          {child}
        </motion.div>
      ))}
    </motion.div>
  );
}; 