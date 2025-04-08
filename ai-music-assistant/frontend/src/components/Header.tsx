import {
    BarChart,
    Edit,
    GitHub,
    Home as HomeIcon,
    Info,
    LibraryMusic,
    Menu as MenuIcon,
    MusicNote
} from '@mui/icons-material';
import {
    AppBar,
    Box,
    Button,
    Divider,
    Drawer,
    IconButton,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Toolbar,
    Typography,
    useMediaQuery,
    useTheme
} from '@mui/material';
import React, { useState } from 'react';
import { Link as RouterLink, useLocation } from 'react-router-dom';

const Header: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [drawerOpen, setDrawerOpen] = useState(false);
  const location = useLocation();

  const toggleDrawer = () => {
    setDrawerOpen(!drawerOpen);
  };

  const navItems = [
    { text: '首頁', icon: <HomeIcon />, path: '/' },
    { text: '生成音樂', icon: <MusicNote />, path: '/generate' },
    { text: '音樂編輯', icon: <Edit />, path: '/editor' },
    { text: '音樂分析', icon: <BarChart />, path: '/analysis' },
    { text: '理論分析', icon: <LibraryMusic />, path: '/theory' },
  ];

  const drawer = (
    <Box sx={{ width: 250 }} role="presentation" onClick={toggleDrawer}>
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
        <MusicNote fontSize="large" sx={{ mr: 1 }} />
        <Typography variant="h6" component="div">
          AI 音樂助手
        </Typography>
      </Box>
      <Divider />
      <List>
        {navItems.map((item) => (
          <ListItem 
            button 
            key={item.text} 
            component={RouterLink} 
            to={item.path}
            selected={location.pathname === item.path}
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
      <Divider />
      <List>
        <ListItem button component="a" href="https://github.com/your-repo/ai-music-assistant" target="_blank">
          <ListItemIcon><GitHub /></ListItemIcon>
          <ListItemText primary="GitHub" />
        </ListItem>
        <ListItem button component={RouterLink} to="/about">
          <ListItemIcon><Info /></ListItemIcon>
          <ListItemText primary="關於" />
        </ListItem>
      </List>
    </Box>
  );

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          {isMobile && (
            <IconButton
              size="large"
              edge="start"
              color="inherit"
              aria-label="menu"
              sx={{ mr: 2 }}
              onClick={toggleDrawer}
            >
              <MenuIcon />
            </IconButton>
          )}
          
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            AI 音樂助手
          </Typography>
          
          {!isMobile && (
            <Box sx={{ display: 'flex' }}>
              {navItems.map((item) => (
                <Button 
                  key={item.text}
                  component={RouterLink}
                  to={item.path}
                  color="inherit"
                  startIcon={item.icon}
                  sx={{
                    mx: 0.5,
                    bgcolor: location.pathname === item.path ? 'rgba(255,255,255,0.15)' : 'transparent'
                  }}
                >
                  {item.text}
                </Button>
              ))}
            </Box>
          )}
        </Toolbar>
      </AppBar>
      
      <Drawer
        anchor="left"
        open={drawerOpen}
        onClose={toggleDrawer}
      >
        {drawer}
      </Drawer>
    </>
  );
};

export default Header; 