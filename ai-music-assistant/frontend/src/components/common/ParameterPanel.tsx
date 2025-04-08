import { Info, Tune } from '@mui/icons-material';
import {
    Box,
    Chip,
    FormControl,
    FormHelperText,
    Grid,
    IconButton,
    InputLabel,
    MenuItem,
    Paper,
    Select,
    SelectChangeEvent,
    Slider,
    TextField,
    Tooltip,
    Typography
} from '@mui/material';
import React from 'react';

// 定義不同類型的參數
export type ParameterType = 'text' | 'select' | 'slider' | 'chips' | 'number';

// 定義參數選項接口
export interface ParameterOption {
  value: string | number;
  label: string;
  description?: string;
}

// 定義單個參數接口
export interface Parameter {
  id: string;
  label: string;
  type: ParameterType;
  value: any;
  options?: ParameterOption[];
  min?: number;
  max?: number;
  step?: number;
  marks?: { value: number; label: string }[];
  helper?: string;
  required?: boolean;
  placeholder?: string;
  disabled?: boolean;
}

// 參數面板屬性接口
interface ParameterPanelProps {
  title?: string;
  description?: string;
  parameters: Parameter[];
  onChange: (id: string, value: any) => void;
  columns?: 1 | 2 | 3 | 4;
  elevation?: number;
  showTuneIcon?: boolean;
}

/**
 * 參數面板組件
 * 提供統一的各類型參數輸入界面，支持文字、選擇、滑塊、標籤和數字等多種參數類型
 */
const ParameterPanel: React.FC<ParameterPanelProps> = ({
  title,
  description,
  parameters,
  onChange,
  columns = 2,
  elevation = 1,
  showTuneIcon = true
}) => {
  // 處理文本參數變化
  const handleTextChange = (id: string, e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(id, e.target.value);
  };

  // 處理數字參數變化
  const handleNumberChange = (id: string, e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value === '' ? '' : Number(e.target.value);
    onChange(id, value);
  };

  // 處理選擇參數變化
  const handleSelectChange = (id: string, e: SelectChangeEvent<string | number>) => {
    onChange(id, e.target.value);
  };

  // 處理滑塊參數變化
  const handleSliderChange = (id: string, value: number | number[]) => {
    onChange(id, value);
  };

  // 處理標籤參數變化
  const handleChipToggle = (id: string, option: string | number, currentValues: (string | number)[]) => {
    const newValues = currentValues.includes(option)
      ? currentValues.filter(value => value !== option)
      : [...currentValues, option];
    onChange(id, newValues);
  };

  // 計算每個參數的欄寬
  const getColumnWidth = () => {
    return 12 / columns;
  };

  return (
    <Paper elevation={elevation} sx={{ mb: 3 }}>
      <Box sx={{ p: 2 }}>
        {/* 標題區域 */}
        {title && (
          <Box sx={{ display: 'flex', alignItems: 'center', mb: description ? 1 : 2 }}>
            {showTuneIcon && <Tune sx={{ mr: 1, color: 'text.secondary' }} />}
            <Typography variant="h6" component="div">
              {title}
            </Typography>
          </Box>
        )}
        
        {/* 描述區域 */}
        {description && (
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {description}
          </Typography>
        )}
        
        {/* 參數網格 */}
        <Grid container spacing={3}>
          {parameters.map((param) => (
            <Grid item xs={12} md={getColumnWidth()} key={param.id}>
              {/* 文本參數 */}
              {param.type === 'text' && (
                <TextField
                  fullWidth
                  label={param.label}
                  value={param.value || ''}
                  onChange={(e) => handleTextChange(param.id, e as React.ChangeEvent<HTMLInputElement>)}
                  required={param.required}
                  placeholder={param.placeholder}
                  helperText={param.helper}
                  disabled={param.disabled}
                  multiline={param.id === 'description'}
                  rows={param.id === 'description' ? 4 : 1}
                />
              )}
              
              {/* 數字參數 */}
              {param.type === 'number' && (
                <TextField
                  fullWidth
                  label={param.label}
                  value={param.value}
                  onChange={(e) => handleNumberChange(param.id, e as React.ChangeEvent<HTMLInputElement>)}
                  required={param.required}
                  helperText={param.helper}
                  disabled={param.disabled}
                  type="number"
                  inputProps={{
                    min: param.min,
                    max: param.max,
                    step: param.step || 1
                  }}
                />
              )}
              
              {/* 選擇參數 */}
              {param.type === 'select' && (
                <FormControl fullWidth disabled={param.disabled}>
                  <InputLabel id={`${param.id}-label`} required={param.required}>
                    {param.label}
                  </InputLabel>
                  <Select
                    labelId={`${param.id}-label`}
                    value={param.value}
                    label={param.label}
                    onChange={(e) => handleSelectChange(param.id, e)}
                  >
                    {param.options?.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        <Box sx={{ display: 'flex', flexDirection: 'column' }}>
                          <Typography variant="body1">{option.label}</Typography>
                          {option.description && (
                            <Typography variant="caption" color="text.secondary">
                              {option.description}
                            </Typography>
                          )}
                        </Box>
                      </MenuItem>
                    ))}
                  </Select>
                  {param.helper && <FormHelperText>{param.helper}</FormHelperText>}
                </FormControl>
              )}
              
              {/* 滑塊參數 */}
              {param.type === 'slider' && (
                <Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Typography id={`${param.id}-slider-label`} gutterBottom>
                      {param.label}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {param.value}
                    </Typography>
                  </Box>
                  <Slider
                    value={param.value}
                    onChange={(_, value) => handleSliderChange(param.id, value)}
                    aria-labelledby={`${param.id}-slider-label`}
                    min={param.min}
                    max={param.max}
                    step={param.step}
                    marks={param.marks}
                    disabled={param.disabled}
                    valueLabelDisplay="auto"
                  />
                  {param.helper && (
                    <Typography variant="caption" color="text.secondary">
                      {param.helper}
                    </Typography>
                  )}
                </Box>
              )}
              
              {/* 標籤參數 */}
              {param.type === 'chips' && (
                <Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Typography variant="body1" gutterBottom>
                      {param.label}
                    </Typography>
                    {param.helper && (
                      <Tooltip title={param.helper}>
                        <IconButton size="small" sx={{ ml: 0.5 }}>
                          <Info fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    )}
                  </Box>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {param.options?.map((option) => (
                      <Chip
                        key={option.value}
                        label={option.label}
                        onClick={() => handleChipToggle(param.id, option.value, param.value)}
                        color={param.value.includes(option.value) ? "primary" : "default"}
                        variant={param.value.includes(option.value) ? "filled" : "outlined"}
                        disabled={param.disabled}
                      />
                    ))}
                  </Box>
                </Box>
              )}
            </Grid>
          ))}
        </Grid>
      </Box>
    </Paper>
  );
};

export default ParameterPanel; 