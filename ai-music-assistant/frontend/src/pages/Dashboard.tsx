import React from 'react';
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  CardMedia, 
  Grid, 
  Button, 
  Container, 
  Paper 
} from '@mui/material';
import { useNavigate } from 'react-router-dom';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();

  const features = [
    {
      title: '文字到音樂',
      description: '透過自然語言描述您的音樂想法，AI將幫您將其轉換成完整的音樂作品。',
      image: '/images/ai-music-assistant.png',
      path: '/text-to-music',
    },
    {
      title: '旋律到編曲',
      description: '哼唱或錄製簡單旋律，AI將為您完成和聲、編曲與配器。',
      image: '/images/ai-music-assistant.png',
      path: '/melody-to-arrangement',
    },
    {
      title: '音樂分析',
      description: '上傳您的音樂作品，獲取專業的樂理分析與改進建議。',
      image: '/images/ai-music-assistant.png',
      path: '/music-analysis',
    },
  ];

  return (
    <Container maxWidth="lg">
      {/* 頂部橫幅 */}
      <Paper
        sx={{
          position: 'relative',
          backgroundColor: 'rgba(0,0,0,0.7)',
          color: '#fff',
          mb: 4,
          overflow: 'hidden',
          backgroundSize: 'cover',
          backgroundRepeat: 'no-repeat',
          backgroundPosition: 'center',
          backgroundImage: 'url(/images/hero-bg.jpg)',
          boxShadow: '0 4px 15px rgba(0,0,0,0.2)',
          borderRadius: 2,
        }}
      >
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            bottom: 0,
            right: 0,
            left: 0,
            backgroundColor: 'rgba(0,0,0,.5)',
            backdropFilter: 'blur(2px)',
          }}
        />
        <Box
          sx={{
            position: 'relative',
            p: { xs: 3, md: 6 },
            py: { xs: 4, md: 8 },
          }}
        >
          <Typography component="h1" variant="h2" color="inherit" gutterBottom>
            AI 音樂創作助手
          </Typography>
          <Typography variant="h5" color="inherit" paragraph>
            運用人工智能技術，輕鬆創作專業音樂作品，無需專業音樂知識也能創作出優美動聽的音樂。
          </Typography>
          <Button variant="contained" color="primary" size="large" sx={{ mt: 2 }} onClick={() => navigate('/text-to-music')}>
            立即創作
          </Button>
        </Box>
      </Paper>

      {/* 功能卡片 */}
      <Typography variant="h4" component="h2" gutterBottom sx={{ mb: 4 }}>
        主要功能
      </Typography>
      <Grid container spacing={4}>
        {features.map((feature) => (
          <Grid item key={feature.title} xs={12} sm={6} md={4}>
            <Card
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                transition: 'transform 0.3s',
                '&:hover': {
                  transform: 'translateY(-8px)',
                  boxShadow: '0 12px 20px rgba(0,0,0,0.2)',
                },
              }}
            >
              <CardMedia
                component="img"
                height="140"
                image={feature.image || 'https://via.placeholder.com/300x140'}
                alt={feature.title}
              />
              <CardContent sx={{ flexGrow: 1 }}>
                <Typography gutterBottom variant="h5" component="h2">
                  {feature.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {feature.description}
                </Typography>
              </CardContent>
              <Box sx={{ p: 2 }}>
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => navigate(feature.path)}
                >
                  開始使用
                </Button>
              </Box>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* 底部介紹 */}
      <Box sx={{ mt: 8, mb: 4 }}>
        <Typography variant="h4" component="h2" gutterBottom>
          關於 AI 音樂助手
        </Typography>
        <Typography variant="body1" paragraph>
          AI音樂助手是基於 Model Context Protocol (MCP) 的智能音樂創作系統，旨在協助音樂創作者突破技術限制，釋放創意潛能。透過整合最先進的人工智能技術，我們提供了一個從靈感到完整音樂作品的一站式解決方案。
        </Typography>
        <Typography variant="body1" paragraph>
          無論您是專業音樂人還是音樂愛好者，我們的工具都能讓您輕鬆創作、編曲並優化音樂，同時學習音樂理論知識，提升您的創作能力。
        </Typography>
      </Box>
    </Container>
  );
};

export default Dashboard; 