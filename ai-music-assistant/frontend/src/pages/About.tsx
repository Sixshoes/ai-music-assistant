import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const About: React.FC = () => {
  return (
    <Box sx={{ p: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          關於 AI 音樂助手
        </Typography>
        <Typography variant="body1" paragraph>
          AI 音樂助手是一個結合人工智能技術的音樂創作工具，幫助音樂愛好者和專業人士更輕鬆地創作音樂。
        </Typography>
        <Typography variant="body1" paragraph>
          我們的目標是讓音樂創作變得更加直觀和高效，無論您是否有音樂理論基礎，都能輕鬆創作出優美的旋律和完整的樂曲。
        </Typography>
        <Typography variant="h5" component="h2" sx={{ mt: 3 }} gutterBottom>
          主要功能
        </Typography>
        <Typography variant="body1" component="ul">
          <li>文本生成音樂：通過文字描述生成音樂</li>
          <li>音樂理論分析：分析和理解音樂理論</li>
          <li>旋律編曲：將簡單旋律發展為完整編曲</li>
          <li>音樂工作室：提供完整的音樂創作環境</li>
        </Typography>
      </Paper>
    </Box>
  );
};

export default About; 