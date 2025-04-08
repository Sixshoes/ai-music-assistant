import { Box, Button, Typography } from '@mui/material';
import React from 'react';
import { Link } from 'react-router-dom';

const Home: React.FC = () => {
  return (
    <Box sx={{ textAlign: 'center', p: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom>
        AI 音樂助手
      </Typography>
      <Typography variant="h5" component="h2" gutterBottom>
        使用 AI 技術創作獨特的音樂
      </Typography>
      <Box sx={{ mt: 4 }}>
        <Button 
          component={Link} 
          to="/text-to-music" 
          variant="contained" 
          color="primary" 
          sx={{ m: 1 }}
        >
          文字生成音樂
        </Button>
        <Button 
          component={Link} 
          to="/theory" 
          variant="outlined" 
          sx={{ m: 1 }}
        >
          音樂理論分析
        </Button>
      </Box>
    </Box>
  );
};

export default Home; 