import { Box, CircularProgress } from '@mui/material';
import React, { lazy, Suspense } from 'react';
import { Route, Routes } from 'react-router-dom';

// 頁面懶加載包裝器
const lazyLoad = (Component: React.LazyExoticComponent<React.ComponentType<any>>) => (
  <Suspense
    fallback={
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
      </Box>
    }
  >
    <Component />
  </Suspense>
);

// 懶加載頁面組件
const Home = lazy(() => import('../pages/Home'));
const About = lazy(() => import('../pages/About'));
// const TextToMusicPage = lazy(() => import('../pages/TextToMusicPage'));
const TestPage = lazy(() => import('../pages/TestPage'));
const MusicAnalysisPage = lazy(() => import('../pages/MusicAnalysisPage'));
const SoundFontPage = lazy(() => import('../pages/SoundFontPage'));
const TheoryAnalysisPage = lazy(() => import('../pages/TheoryAnalysisPage'));
const MelodyToArrangementPage = lazy(() => import('../pages/MelodyToArrangementPage'));
const ProjectsPage = lazy(() => import('../pages/ProjectsPage'));
const Studio = lazy(() => import('../pages/Studio'));
const Dashboard = lazy(() => import('../pages/Dashboard'));
const NotFound = lazy(() => import('../pages/NotFound'));

const AppRoutes: React.FC = () => {
  return (
    <Routes>
      <Route path="/" element={lazyLoad(Home)} />
      <Route path="/about" element={lazyLoad(About)} />
      <Route path="/text-to-music" element={lazyLoad(TestPage)} />
      <Route path="/analysis" element={lazyLoad(MusicAnalysisPage)} />
      <Route path="/soundfont" element={lazyLoad(SoundFontPage)} />
      <Route path="/theory" element={lazyLoad(TheoryAnalysisPage)} />
      <Route path="/arrangement" element={lazyLoad(MelodyToArrangementPage)} />
      <Route path="/projects" element={lazyLoad(ProjectsPage)} />
      <Route path="/studio" element={lazyLoad(Studio)} />
      <Route path="/dashboard" element={lazyLoad(Dashboard)} />
      <Route path="*" element={lazyLoad(NotFound)} />
    </Routes>
  );
};

export default AppRoutes; 