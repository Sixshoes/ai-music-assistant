import React from 'react';
import { Logger } from '../utils/Logger';

interface AudioControlsProps {
  isPlaying: boolean;
  onPlay: () => void;
  onPause: () => void;
  onStop: () => void;
  onVolumeChange: (volume: number) => void;
  currentVolume: number;
}

export const AudioControls: React.FC<AudioControlsProps> = ({
  isPlaying,
  onPlay,
  onPause,
  onStop,
  onVolumeChange,
  currentVolume,
}) => {
  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const volume = parseFloat(e.target.value);
    onVolumeChange(volume);
    Logger.info(`音量調整至: ${volume}`);
  };

  return (
    <div className="audio-controls">
      <button
        onClick={isPlaying ? onPause : onPlay}
        className="control-button"
        aria-label={isPlaying ? '暫停' : '播放'}
      >
        {isPlaying ? '⏸️' : '▶️'}
      </button>
      <button
        onClick={onStop}
        className="control-button"
        aria-label="停止"
      >
        ⏹️
      </button>
      <div className="volume-control">
        <label htmlFor="volume">音量:</label>
        <input
          type="range"
          id="volume"
          min="0"
          max="1"
          step="0.1"
          value={currentVolume}
          onChange={handleVolumeChange}
        />
      </div>
    </div>
  );
}; 