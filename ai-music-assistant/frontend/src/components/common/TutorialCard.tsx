import {
    Close,
    ExpandMore as ExpandMoreIcon,
    HelpOutlineOutlined,
    KeyboardArrowRight,
    LightbulbOutlined,
    PlayCircleOutline
} from '@mui/icons-material';
import {
    Box,
    Button,
    Card,
    CardContent,
    CardMedia,
    Chip,
    Collapse,
    IconButton,
    Paper,
    styled,
    Tooltip,
    Typography
} from '@mui/material';
import React, { useState } from 'react';

// 定義展開按鈕的樣式
const ExpandButton = styled((props: any) => {
  const { expand, ...other } = props;
  return <IconButton {...other} />;
})(({ theme, expand }) => ({
  transform: !expand ? 'rotate(0deg)' : 'rotate(180deg)',
  marginLeft: 'auto',
  transition: theme.transitions.create('transform', {
    duration: theme.transitions.duration.shortest,
  }),
}));

// 定義教學卡片的屬性接口
export interface TutorialCardProps {
  title: string;
  description: string;
  steps?: string[];
  image?: string;
  dismissible?: boolean;
  actionText?: string;
  onAction?: () => void;
  variant?: 'tip' | 'tutorial' | 'example';
  defaultExpanded?: boolean;
  onDismiss?: () => void;
}

/**
 * 教學卡片組件
 * 提供提示、教學和範例三種不同類型的卡片，幫助用戶學習使用產品
 */
const TutorialCard: React.FC<TutorialCardProps> = ({
  title,
  description,
  steps,
  image,
  dismissible = true,
  actionText,
  onAction,
  variant = 'tutorial',
  defaultExpanded = false,
  onDismiss
}) => {
  const [expanded, setExpanded] = useState(defaultExpanded);

  // 根據不同的卡片類型設置不同的圖標和顏色
  const getVariantProps = () => {
    switch (variant) {
      case 'tip':
        return {
          icon: <LightbulbOutlined />,
          color: 'info',
          label: '提示'
        };
      case 'example':
        return {
          icon: <PlayCircleOutline />,
          color: 'success',
          label: '範例'
        };
      case 'tutorial':
      default:
        return {
          icon: <HelpOutlineOutlined />,
          color: 'primary',
          label: '教學'
        };
    }
  };

  const variantProps = getVariantProps();

  // 處理展開/收起
  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  // 處理關閉卡片
  const handleDismiss = () => {
    if (onDismiss) {
      onDismiss();
    }
  };

  return (
    <Paper elevation={1} sx={{ mb: 3, overflow: 'hidden', borderRadius: 2 }}>
      <Card sx={{ 
        position: 'relative',
        borderLeft: `4px solid ${
          variant === 'tip' 
            ? theme => theme.palette.info.main 
            : variant === 'example' 
            ? theme => theme.palette.success.main 
            : theme => theme.palette.primary.main
        }`
      }}>
        <Box sx={{ 
          display: 'flex', 
          flexDirection: 'row', 
          alignItems: 'flex-start', 
          p: 2 
        }}>
          <Box 
            sx={{ 
              mr: 2, 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center'
            }}
          >
            {variantProps.icon}
          </Box>
          
          <Box sx={{ flex: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
              <Typography variant="subtitle1" component="div" sx={{ fontWeight: 600 }}>
                {title}
              </Typography>
              <Chip 
                label={variantProps.label} 
                color={variantProps.color === 'primary' ? 'primary' : variantProps.color === 'success' ? 'success' : 'info'} 
                size="small" 
                sx={{ ml: 1, height: 20, '& .MuiChip-label': { px: 1, py: 0 } }} 
              />
            </Box>
            
            <Typography variant="body2" color="text.secondary">
              {description}
            </Typography>
            
            {(steps || image) && (
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                <Button 
                  size="small" 
                  endIcon={<KeyboardArrowRight />} 
                  onClick={handleExpandClick}
                  sx={{ textTransform: 'none' }}
                >
                  {expanded ? '收起詳情' : '查看詳情'}
                </Button>
                
                {onAction && actionText && (
                  <Button 
                    size="small" 
                    color="primary" 
                    variant="contained" 
                    sx={{ ml: 1, textTransform: 'none' }}
                    onClick={onAction}
                  >
                    {actionText}
                  </Button>
                )}
                
                <ExpandButton
                  expand={expanded}
                  onClick={handleExpandClick}
                  aria-expanded={expanded}
                  aria-label="顯示更多"
                  sx={{ ml: 'auto' }}
                >
                  <ExpandMoreIcon />
                </ExpandButton>
              </Box>
            )}
          </Box>
          
          {dismissible && (
            <Tooltip title="關閉">
              <IconButton 
                size="small" 
                onClick={handleDismiss}
                sx={{ 
                  position: 'absolute', 
                  top: 8, 
                  right: 8
                }}
              >
                <Close fontSize="small" />
              </IconButton>
            </Tooltip>
          )}
        </Box>
        
        <Collapse in={expanded} timeout="auto" unmountOnExit>
          <CardContent sx={{ pt: 0 }}>
            {steps && steps.length > 0 && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  步驟:
                </Typography>
                <Box component="ol" sx={{ pl: 2, mb: 0 }}>
                  {steps.map((step, index) => (
                    <Typography component="li" variant="body2" key={index} sx={{ mb: 0.5 }}>
                      {step}
                    </Typography>
                  ))}
                </Box>
              </Box>
            )}
            
            {image && (
              <CardMedia
                component="img"
                image={image}
                alt={title}
                sx={{ 
                  borderRadius: 1,
                  maxHeight: 200,
                  objectFit: 'contain',
                  bgcolor: 'background.default'
                }}
              />
            )}
          </CardContent>
        </Collapse>
      </Card>
    </Paper>
  );
};

export default TutorialCard; 