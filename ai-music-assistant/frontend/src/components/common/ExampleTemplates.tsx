import {
    AutoAwesome,
    Description,
    Folder,
    Info,
    MusicNote,
    PlayArrow
} from '@mui/icons-material';
import {
    Box,
    Button,
    Card,
    CardActionArea,
    CardActions,
    CardContent,
    CardMedia,
    Chip,
    Grid,
    IconButton,
    Paper,
    Tooltip,
    Typography,
    useTheme
} from '@mui/material';
import React from 'react';

// 定義範例模板數據接口
export interface ExampleTemplate {
  id: string;
  title: string;
  description: string;
  thumbnail?: string;
  category: string;
  difficulty?: 'beginner' | 'intermediate' | 'advanced';
  parameters: Record<string, any>;
  tags?: string[];
}

// 組件屬性接口
interface ExampleTemplatesProps {
  templates: ExampleTemplate[];
  onSelect: (template: ExampleTemplate) => void;
  columns?: 1 | 2 | 3 | 4;
}

/**
 * 範例模板組件
 * 以卡片網格形式展示不同的預設範例，便於用戶快速選擇和開始
 */
const ExampleTemplates: React.FC<ExampleTemplatesProps> = ({
  templates,
  onSelect,
  columns = 3
}) => {
  const theme = useTheme();

  // 獲取難度等級的顯示樣式
  const getDifficultyProps = (difficulty?: 'beginner' | 'intermediate' | 'advanced') => {
    switch (difficulty) {
      case 'beginner':
        return {
          label: '初學者',
          color: 'success' as const
        };
      case 'intermediate':
        return {
          label: '中級',
          color: 'primary' as const
        };
      case 'advanced':
        return {
          label: '高級',
          color: 'error' as const
        };
      default:
        return {
          label: '初學者',
          color: 'success' as const
        };
    }
  };

  // 獲取類別圖標
  const getCategoryIcon = (category: string) => {
    switch (category.toLowerCase()) {
      case 'text2music':
      case 'text':
        return <Description fontSize="small" />;
      case 'melody':
      case 'arrangement':
        return <MusicNote fontSize="small" />;
      case 'analysis':
        return <Info fontSize="small" />;
      default:
        return <Folder fontSize="small" />;
    }
  };

  return (
    <Paper elevation={0} sx={{ p: 2, bgcolor: 'background.default' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <AutoAwesome sx={{ mr: 1, color: theme.palette.primary.main }} />
        <Typography variant="h6" component="div">
          模板範例
        </Typography>
      </Box>

      <Grid container spacing={2}>
        {templates.map((template) => (
          <Grid item xs={12} sm={6} md={12 / columns} key={template.id}>
            <Card 
              elevation={1} 
              sx={{ 
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                transition: 'transform 0.2s, box-shadow 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: theme.shadows[4]
                }
              }}
            >
              <CardActionArea 
                onClick={() => onSelect(template)}
                sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', alignItems: 'stretch' }}
              >
                {template.thumbnail ? (
                  <CardMedia
                    component="img"
                    height="140"
                    image={template.thumbnail}
                    alt={template.title}
                  />
                ) : (
                  <Box 
                    sx={{ 
                      height: 120, 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      backgroundColor: 'action.hover'
                    }}
                  >
                    <MusicNote sx={{ fontSize: 48, opacity: 0.5 }} />
                  </Box>
                )}
                
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 1 }}>
                    <Chip 
                      icon={getCategoryIcon(template.category)}
                      label={template.category}
                      size="small"
                      sx={{ mr: 1 }}
                    />
                    
                    {template.difficulty && (
                      <Chip
                        label={getDifficultyProps(template.difficulty).label}
                        color={getDifficultyProps(template.difficulty).color}
                        size="small"
                        variant="outlined"
                      />
                    )}
                  </Box>
                  
                  <Typography 
                    gutterBottom 
                    variant="subtitle1" 
                    component="div" 
                    sx={{ fontWeight: 500, mt: 1 }}
                  >
                    {template.title}
                  </Typography>
                  
                  <Typography 
                    variant="body2" 
                    color="text.secondary"
                    sx={{ 
                      display: '-webkit-box',
                      overflow: 'hidden',
                      WebkitBoxOrient: 'vertical',
                      WebkitLineClamp: 3,
                    }}
                  >
                    {template.description}
                  </Typography>
                </CardContent>
              </CardActionArea>
              
              {template.tags && template.tags.length > 0 && (
                <Box sx={{ px: 2, py: 1, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {template.tags.slice(0, 3).map((tag, index) => (
                    <Chip 
                      key={index} 
                      label={tag} 
                      size="small" 
                      variant="outlined"
                      sx={{ height: 20, '& .MuiChip-label': { px: 1, py: 0.5 } }}
                    />
                  ))}
                  {template.tags.length > 3 && (
                    <Tooltip title={template.tags.slice(3).join(', ')}>
                      <Chip 
                        label={`+${template.tags.length - 3}`} 
                        size="small" 
                        sx={{ height: 20, '& .MuiChip-label': { px: 1, py: 0.5 } }}
                      />
                    </Tooltip>
                  )}
                </Box>
              )}
              
              <CardActions sx={{ display: 'flex', justifyContent: 'space-between', px: 2, pb: 2 }}>
                <Button 
                  size="small" 
                  startIcon={<PlayArrow />}
                  onClick={() => onSelect(template)}
                >
                  使用此模板
                </Button>
                
                <Tooltip title="查看詳情">
                  <IconButton 
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelect(template);
                    }}
                  >
                    <Info fontSize="small" />
                  </IconButton>
                </Tooltip>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Paper>
  );
};

export default ExampleTemplates; 