import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { Link } from 'react-router-dom';

const NotFound: React.FC = () => {
  return (
    <Box sx={{ textAlign: 'center', p: 4 }}>
      <Typography variant="h2" component="h1" gutterBottom>
        404
      </Typography>
      <Typography variant="h4" component="h2" gutterBottom>
        頁面未找到
      </Typography>
      <Typography variant="body1" sx={{ mb: 4 }}>
        您請求的頁面不存在或已被移動
      </Typography>
      <Button component={Link} to="/" variant="contained" color="primary">
        返回首頁
      </Button>
    </Box>
  );
};

export default NotFound; 