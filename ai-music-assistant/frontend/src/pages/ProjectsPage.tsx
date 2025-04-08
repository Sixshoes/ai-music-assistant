import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActions,
  CardMedia,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Chip,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Divider
} from '@mui/material';
import {
  Add,
  MoreVert,
  MusicNote,
  PlayArrow,
  Delete,
  Edit,
  Download,
  Folder,
  Sort
} from '@mui/icons-material';

// 模擬專案數據
const mockProjects = [
  {
    id: '1',
    title: '夏日旋律',
    description: '輕快的流行風格作品，適合廣告配樂',
    date: '2023-06-15',
    genre: 'pop',
    key: 'C',
    tempo: 120,
    thumbnailUrl: 'https://via.placeholder.com/300x150?text=Summer+Melody',
    fileType: 'midi'
  },
  {
    id: '2',
    title: '雨夜思緒',
    description: '慢板鋼琴曲，富有情感的小調作品',
    date: '2023-05-22',
    genre: 'classical',
    key: 'Am',
    tempo: 85,
    thumbnailUrl: 'https://via.placeholder.com/300x150?text=Rainy+Night',
    fileType: 'mp3'
  },
  {
    id: '3',
    title: '山間小溪',
    description: '自然環境音樂，結合民謠元素',
    date: '2023-04-10',
    genre: 'folk',
    key: 'G',
    tempo: 95,
    thumbnailUrl: 'https://via.placeholder.com/300x150?text=Mountain+Stream',
    fileType: 'midi'
  },
  {
    id: '4',
    title: '都市節拍',
    description: '電子舞曲風格，現代都市感',
    date: '2023-03-28',
    genre: 'electronic',
    key: 'F',
    tempo: 128,
    thumbnailUrl: 'https://via.placeholder.com/300x150?text=Urban+Beat',
    fileType: 'mp3'
  }
];

const ProjectsPage: React.FC = () => {
  // 狀態管理
  const [projects, setProjects] = useState(mockProjects);
  const [openNewProject, setOpenNewProject] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');
  const [newProjectDescription, setNewProjectDescription] = useState('');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<'date' | 'title'>('date');
  const [sortAnchorEl, setSortAnchorEl] = useState<null | HTMLElement>(null);
  const [filterBy, setFilterBy] = useState<string | null>(null);
  
  // 打開專案選項菜單
  const handleOpenMenu = (event: React.MouseEvent<HTMLButtonElement>, projectId: string) => {
    setAnchorEl(event.currentTarget);
    setSelectedProjectId(projectId);
  };
  
  // 關閉專案選項菜單
  const handleCloseMenu = () => {
    setAnchorEl(null);
    setSelectedProjectId(null);
  };
  
  // 打開排序菜單
  const handleOpenSortMenu = (event: React.MouseEvent<HTMLButtonElement>) => {
    setSortAnchorEl(event.currentTarget);
  };
  
  // 關閉排序菜單
  const handleCloseSortMenu = () => {
    setSortAnchorEl(null);
  };
  
  // 設置排序方式
  const handleSetSort = (sort: 'date' | 'title') => {
    setSortBy(sort);
    handleCloseSortMenu();
  };
  
  // 過濾專案
  const handleFilter = (genre: string | null) => {
    setFilterBy(genre);
  };
  
  // 刪除專案
  const handleDeleteProject = () => {
    if (selectedProjectId) {
      setProjects(projects.filter(project => project.id !== selectedProjectId));
      handleCloseMenu();
    }
  };
  
  // 新增專案
  const handleAddProject = () => {
    if (newProjectName.trim()) {
      const newProject = {
        id: `${Date.now()}`,
        title: newProjectName,
        description: newProjectDescription || '無描述',
        date: new Date().toISOString().split('T')[0],
        genre: 'other',
        key: 'C',
        tempo: 120,
        thumbnailUrl: 'https://via.placeholder.com/300x150?text=New+Project',
        fileType: 'midi'
      };
      
      setProjects([newProject, ...projects]);
      setNewProjectName('');
      setNewProjectDescription('');
      setOpenNewProject(false);
    }
  };
  
  // 排序專案
  const sortedProjects = [...projects].sort((a, b) => {
    if (sortBy === 'date') {
      return new Date(b.date).getTime() - new Date(a.date).getTime();
    } else {
      return a.title.localeCompare(b.title);
    }
  });
  
  // 過濾專案
  const filteredProjects = filterBy 
    ? sortedProjects.filter(project => project.genre === filterBy)
    : sortedProjects;
  
  // 獲取所有可用的風格
  const allGenres = Array.from(new Set(projects.map(project => project.genre)));
  
  return (
    <Container maxWidth="lg">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" component="h1">
          我的專案
        </Typography>
        
        <Box>
          <Button
            variant="outlined"
            startIcon={<Sort />}
            onClick={handleOpenSortMenu}
            sx={{ mr: 1 }}
          >
            {sortBy === 'date' ? '按日期排序' : '按名稱排序'}
          </Button>
          
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setOpenNewProject(true)}
          >
            新增專案
          </Button>
        </Box>
        
        <Menu
          anchorEl={sortAnchorEl}
          open={Boolean(sortAnchorEl)}
          onClose={handleCloseSortMenu}
        >
          <MenuItem onClick={() => handleSetSort('date')}>
            <ListItemText primary="按日期排序" />
          </MenuItem>
          <MenuItem onClick={() => handleSetSort('title')}>
            <ListItemText primary="按名稱排序" />
          </MenuItem>
        </Menu>
      </Box>
      
      {/* 過濾器 */}
      <Box sx={{ mb: 3, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
        <Chip 
          label="全部" 
          color={filterBy === null ? "primary" : "default"}
          onClick={() => handleFilter(null)}
        />
        {allGenres.map(genre => (
          <Chip 
            key={genre}
            label={
              genre === 'pop' ? '流行' :
              genre === 'classical' ? '古典' :
              genre === 'folk' ? '民謠' :
              genre === 'electronic' ? '電子' :
              genre
            }
            color={filterBy === genre ? "primary" : "default"}
            onClick={() => handleFilter(genre)}
          />
        ))}
      </Box>
      
      {/* 專案列表 */}
      {filteredProjects.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Folder sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            沒有找到專案
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {filterBy ? '嘗試更改過濾條件或' : ''}開始創建您的第一個專案吧！
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setOpenNewProject(true)}
            sx={{ mt: 2 }}
          >
            新增專案
          </Button>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {filteredProjects.map(project => (
            <Grid item key={project.id} xs={12} sm={6} md={4}>
              <Card sx={{ 
                height: '100%', 
                display: 'flex', 
                flexDirection: 'column',
                transition: 'transform 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 6
                }
              }}>
                <CardMedia
                  component="img"
                  height="140"
                  image={project.thumbnailUrl}
                  alt={project.title}
                />
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Typography variant="h6" component="div" gutterBottom>
                      {project.title}
                    </Typography>
                    <IconButton 
                      aria-label="more" 
                      size="small"
                      onClick={(e) => handleOpenMenu(e, project.id)}
                    >
                      <MoreVert />
                    </IconButton>
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {project.description}
                  </Typography>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Chip 
                      size="small" 
                      label={`${project.key} | ${project.tempo} BPM`} 
                      variant="outlined"
                    />
                    <Chip 
                      size="small" 
                      label={project.fileType.toUpperCase()} 
                      color="primary"
                      variant="outlined"
                    />
                  </Box>
                  
                  <Typography variant="caption" color="text.secondary">
                    創建於 {project.date}
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button 
                    size="small" 
                    startIcon={<PlayArrow />}
                  >
                    播放
                  </Button>
                  <Button 
                    size="small" 
                    startIcon={<Edit />}
                  >
                    編輯
                  </Button>
                  <Button 
                    size="small" 
                    startIcon={<Download />}
                  >
                    下載
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
      
      {/* 專案選項菜單 */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleCloseMenu}
      >
        <MenuItem onClick={handleCloseMenu}>
          <ListItemIcon>
            <PlayArrow fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="播放" />
        </MenuItem>
        <MenuItem onClick={handleCloseMenu}>
          <ListItemIcon>
            <Edit fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="編輯" />
        </MenuItem>
        <MenuItem onClick={handleCloseMenu}>
          <ListItemIcon>
            <Download fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="下載" />
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleDeleteProject}>
          <ListItemIcon>
            <Delete fontSize="small" color="error" />
          </ListItemIcon>
          <ListItemText primary="刪除" primaryTypographyProps={{ color: 'error' }} />
        </MenuItem>
      </Menu>
      
      {/* 新增專案對話框 */}
      <Dialog open={openNewProject} onClose={() => setOpenNewProject(false)}>
        <DialogTitle>新增專案</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="專案名稱"
            type="text"
            fullWidth
            variant="outlined"
            value={newProjectName}
            onChange={(e) => setNewProjectName(e.target.value)}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="專案描述"
            type="text"
            fullWidth
            variant="outlined"
            multiline
            rows={3}
            value={newProjectDescription}
            onChange={(e) => setNewProjectDescription(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenNewProject(false)}>取消</Button>
          <Button 
            onClick={handleAddProject}
            variant="contained"
            disabled={!newProjectName.trim()}
          >
            創建
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ProjectsPage; 