import {
    Analytics,
    DarkMode,
    KeyboardArrowDown,
    LibraryMusic,
    LightMode,
    Menu as MenuIcon,
    MusicNote,
    TextFields
} from '@mui/icons-material';
import {
    AppBar,
    Button,
    Drawer,
    IconButton,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Menu,
    MenuItem,
    Toolbar,
    Tooltip,
    Typography,
    useMediaQuery,
    useTheme
} from '@mui/material';
import React from 'react';
import { Link } from 'react-router-dom';
import { useThemeContext } from '../../context/ThemeContext';

const Header: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const { mode, toggleTheme } = useThemeContext();
  
  // 菜單狀態
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const [mobileOpen, setMobileOpen] = React.useState(false);
  
  const open = Boolean(anchorEl);
  
  // 桌面菜單處理函數
  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };
  
  const handleClose = () => {
    setAnchorEl(null);
  };
  
  // 移動端抽屜處理函數
  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };
  
  // 點擊移動端菜單項時關閉抽屜
  const handleMobileMenuClick = () => {
    setMobileOpen(false);
  };
  
  // 移動端抽屜內容
  const drawer = (
    <div>
      <List>
        <ListItem button component={Link} to="/" onClick={handleMobileMenuClick}>
          <ListItemText primary="首頁" />
        </ListItem>
        
        {/* 工具子菜單 */}
        <ListItem button component={Link} to="/text-to-music" onClick={handleMobileMenuClick}>
          <ListItemIcon>
            <TextFields fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="文字生成音樂" />
        </ListItem>
        
        <ListItem button component={Link} to="/analysis" onClick={handleMobileMenuClick}>
          <ListItemIcon>
            <Analytics fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="音樂分析" />
        </ListItem>
        
        <ListItem button component={Link} to="/soundfont" onClick={handleMobileMenuClick}>
          <ListItemIcon>
            <LibraryMusic fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="音色渲染" />
        </ListItem>
        
        <ListItem button component={Link} to="/theory" onClick={handleMobileMenuClick}>
          <ListItemIcon>
            <MusicNote fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="樂理分析" />
        </ListItem>
        
        <ListItem button component={Link} to="/arrangement" onClick={handleMobileMenuClick}>
          <ListItemIcon>
            <MusicNote fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="旋律編曲" />
        </ListItem>
        
        {/* 其他頁面 */}
        <ListItem button component={Link} to="/projects" onClick={handleMobileMenuClick}>
          <ListItemText primary="專案" />
        </ListItem>
        
        <ListItem button component={Link} to="/about" onClick={handleMobileMenuClick}>
          <ListItemText primary="關於" />
        </ListItem>
        
        {/* 主題切換按鈕 */}
        <ListItem button onClick={toggleTheme}>
          <ListItemIcon>
            {mode === 'dark' ? <LightMode fontSize="small" /> : <DarkMode fontSize="small" />}
          </ListItemIcon>
          <ListItemText primary={mode === 'dark' ? "切換亮色模式" : "切換暗色模式"} />
        </ListItem>
      </List>
    </div>
  );
  
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          AI Music Assistant
        </Typography>
        
        {/* 主題切換按鈕 */}
        <Tooltip title={mode === 'dark' ? "切換亮色模式" : "切換暗色模式"}>
          <IconButton 
            color="inherit" 
            onClick={toggleTheme}
            sx={{ 
              mr: 1,
              transition: 'transform 0.3s ease',
              '&:hover': { transform: 'rotate(30deg)' }
            }}
          >
            {mode === 'dark' ? <LightMode /> : <DarkMode />}
          </IconButton>
        </Tooltip>
        
        {isMobile ? (
          <>
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="end"
              onClick={handleDrawerToggle}
              sx={{ mr: 0 }}
              size="large"
            >
              <MenuIcon />
            </IconButton>
            <Drawer
              anchor="right"
              open={mobileOpen}
              onClose={handleDrawerToggle}
              sx={{
                '& .MuiDrawer-paper': { 
                  width: '75%', 
                  maxWidth: '300px',
                  boxSizing: 'border-box',
                },
              }}
            >
              {drawer}
            </Drawer>
          </>
        ) : (
          <>
            <Button 
              color="inherit" 
              component={Link} 
              to="/" 
              sx={{ mx: 1 }}
            >
              首頁
            </Button>
            
            <Button
              color="inherit"
              aria-controls={open ? 'tools-menu' : undefined}
              aria-haspopup="true"
              aria-expanded={open ? 'true' : undefined}
              onClick={handleClick}
              endIcon={<KeyboardArrowDown />}
              sx={{ mx: 1 }}
            >
              音樂工具
            </Button>
            <Menu
              id="tools-menu"
              anchorEl={anchorEl}
              open={open}
              onClose={handleClose}
              MenuListProps={{
                'aria-labelledby': 'basic-button',
              }}
            >
              <MenuItem onClick={handleClose} component={Link} to="/text-to-music">
                <TextFields sx={{ mr: 1 }} fontSize="small" />
                文字生成音樂
              </MenuItem>
              <MenuItem onClick={handleClose} component={Link} to="/analysis">
                <Analytics sx={{ mr: 1 }} fontSize="small" />
                音樂分析
              </MenuItem>
              <MenuItem onClick={handleClose} component={Link} to="/soundfont">
                <LibraryMusic sx={{ mr: 1 }} fontSize="small" />
                音色渲染
              </MenuItem>
              <MenuItem onClick={handleClose} component={Link} to="/theory">
                <MusicNote sx={{ mr: 1 }} fontSize="small" />
                樂理分析
              </MenuItem>
              <MenuItem onClick={handleClose} component={Link} to="/arrangement">
                <MusicNote sx={{ mr: 1 }} fontSize="small" />
                旋律編曲
              </MenuItem>
            </Menu>
            
            <Button 
              color="inherit" 
              component={Link} 
              to="/projects" 
              sx={{ mx: 1 }}
            >
              專案
            </Button>
            <Button 
              color="inherit" 
              component={Link} 
              to="/about" 
              sx={{ mx: 1 }}
            >
              關於
            </Button>
          </>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default Header; 