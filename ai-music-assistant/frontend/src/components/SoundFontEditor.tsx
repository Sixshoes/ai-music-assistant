import { MusicNote, Save } from '@mui/icons-material';
import {
    Box,
    Button,
    Divider,
    FormControl,
    Grid,
    InputLabel,
    MenuItem,
    Paper,
    Select,
    Slider,
    Tab,
    Tabs,
    TextField,
    Typography,
} from '@mui/material';
import React, { useEffect, useState } from 'react';
import Logger from '../services/LoggingService';
import { SoundParameters, SoundPreset } from '../services/SynthesizerService';

interface SoundFontEditorProps {
  preset: SoundPreset | null;
  onSave: (preset: SoundPreset) => void;
  onPreview: () => void;
}

const SoundFontEditor: React.FC<SoundFontEditorProps> = ({
  preset,
  onSave,
  onPreview,
}) => {
  const [parameters, setParameters] = useState<SoundParameters | null>(null);
  const [presetName, setPresetName] = useState('');
  const [editorTab, setEditorTab] = useState(0);
  
  // 當預設變更時更新參數
  useEffect(() => {
    if (preset) {
      setParameters(preset.parameters);
      setPresetName(preset.name);
    }
  }, [preset]);
  
  // 處理標籤頁變更
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setEditorTab(newValue);
  };
  
  // 處理參數變更
  const handleParameterChange = (key: string, value: number) => {
    if (!parameters) return;
    
    setParameters({
      ...parameters,
      [key]: value,
    });
    
    Logger.debug('音色參數已更新', { key, value }, { tags: ['SOUND_FONT'] });
  };
  
  // 保存預設
  const handleSavePreset = () => {
    if (!preset || !parameters) return;
    
    const updatedPreset: SoundPreset = {
      ...preset,
      name: presetName,
      parameters,
      updatedAt: new Date(),
    };
    
    onSave(updatedPreset);
  };
  
  // 音色參數滑塊
  const ParameterSlider = ({ 
    label, 
    min, 
    max, 
    step, 
    value, 
    onChange 
  }: { 
    label: string; 
    min: number; 
    max: number; 
    step: number; 
    value: number; 
    onChange: (value: number) => void; 
  }) => {
    return (
      <Box sx={{ mb: 2 }}>
        <Typography variant="body2" gutterBottom>
          {label}: {value}
        </Typography>
        <Slider
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(_, newValue) => onChange(newValue as number)}
          valueLabelDisplay="auto"
        />
      </Box>
    );
  };
  
  if (!preset || !parameters) {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography variant="body1">
          請先選擇一個音色預設進行編輯
        </Typography>
      </Paper>
    );
  }
  
  return (
    <Paper sx={{ p: 3 }}>
      <Box sx={{ mb: 3 }}>
        <TextField
          fullWidth
          label="預設名稱"
          value={presetName}
          onChange={(e) => setPresetName(e.target.value)}
          variant="outlined"
          sx={{ mb: 2 }}
        />
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            startIcon={<MusicNote />}
            onClick={onPreview}
          >
            試聽
          </Button>
          <Button
            variant="outlined"
            startIcon={<Save />}
            onClick={handleSavePreset}
          >
            保存預設
          </Button>
        </Box>
      </Box>
      
      <Divider sx={{ my: 2 }} />
      
      <Tabs value={editorTab} onChange={handleTabChange} sx={{ mb: 2 }}>
        <Tab label="基本參數" />
        <Tab label="進階參數" />
        {preset.fontId.includes('dexed') && <Tab label="FM參數" />}
      </Tabs>
      
      {editorTab === 0 && (
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <ParameterSlider
              label="音量"
              min={0}
              max={1}
              step={0.01}
              value={parameters.volume}
              onChange={(value) => handleParameterChange('volume', value)}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <ParameterSlider
              label="起音時間"
              min={0.001}
              max={2}
              step={0.001}
              value={parameters.attack}
              onChange={(value) => handleParameterChange('attack', value)}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <ParameterSlider
              label="衰減時間"
              min={0.001}
              max={2}
              step={0.001}
              value={parameters.decay}
              onChange={(value) => handleParameterChange('decay', value)}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <ParameterSlider
              label="持續電平"
              min={0}
              max={1}
              step={0.01}
              value={parameters.sustain}
              onChange={(value) => handleParameterChange('sustain', value)}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <ParameterSlider
              label="釋放時間"
              min={0.001}
              max={5}
              step={0.001}
              value={parameters.release}
              onChange={(value) => handleParameterChange('release', value)}
            />
          </Grid>
        </Grid>
      )}
      
      {editorTab === 1 && (
        <Typography variant="body1">
          進階參數編輯功能即將推出...
        </Typography>
      )}
      
      {editorTab === 2 && preset.fontId.includes('dexed') && (
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>演算法</InputLabel>
              <Select
                value={parameters.algorithm || 0}
                onChange={(e) => handleParameterChange('algorithm', Number(e.target.value))}
                label="演算法"
              >
                {[0, 1, 2, 3, 4, 5, 6, 7].map((alg) => (
                  <MenuItem key={alg} value={alg}>
                    演算法 {alg + 1}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6}>
            <ParameterSlider
              label="回饋量"
              min={0}
              max={1}
              step={0.01}
              value={parameters.feedback || 0}
              onChange={(value) => handleParameterChange('feedback', value)}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <ParameterSlider
              label="調製指數"
              min={0}
              max={5}
              step={0.1}
              value={parameters.modulationIndex || 0}
              onChange={(value) => handleParameterChange('modulationIndex', value)}
            />
          </Grid>
          
          <Grid item xs={12}>
            <Typography variant="subtitle1" gutterBottom>
              振盪器設定
            </Typography>
            
            {parameters.operators && parameters.operators.map((op, index) => (
              <Paper key={index} sx={{ p: 2, mb: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  振盪器 {index + 1}
                </Typography>
                
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <ParameterSlider
                      label="頻率比"
                      min={0.1}
                      max={10}
                      step={0.1}
                      value={op.frequency}
                      onChange={(value) => {
                        const updatedOperators = [...parameters.operators!];
                        updatedOperators[index] = { ...op, frequency: value };
                        handleParameterChange('operators', updatedOperators);
                      }}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <ParameterSlider
                      label="音量"
                      min={0}
                      max={1}
                      step={0.01}
                      value={op.volume}
                      onChange={(value) => {
                        const updatedOperators = [...parameters.operators!];
                        updatedOperators[index] = { ...op, volume: value };
                        handleParameterChange('operators', updatedOperators);
                      }}
                    />
                  </Grid>
                </Grid>
              </Paper>
            ))}
          </Grid>
        </Grid>
      )}
    </Paper>
  );
};

export default SoundFontEditor; 