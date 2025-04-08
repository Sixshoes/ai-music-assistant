import React from 'react';
import { Container, Typography, Box } from '@mui/material';

const Compose: React.FC = () => {
  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h2" component="h1" gutterBottom>
          作曲工作室
        </Typography>
        <Typography variant="body1">
          在這裡開始您的音樂創作之旅。
        </Typography>
      </Box>
    </Container>
  );
};

export default Compose; 