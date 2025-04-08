"""音頻處理模組

提供音頻分析、音高提取和節奏分析功能
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# 嘗試導入相依套件
try:
    import librosa
    from basic_pitch import ICASSP_2022_MODEL_PATH
    from basic_pitch.inference import predict
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"音頻處理相依套件導入失敗: {str(e)}")
    logger.warning("AudioProcessor 將以有限功能運行，或者可能無法運行")
    DEPENDENCIES_AVAILABLE = False

class AudioProcessor:
    """音頻處理器"""
    
    def __init__(self):
        """初始化音頻處理器"""
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """加載Basic Pitch模型"""
        try:
            if not DEPENDENCIES_AVAILABLE:
                logger.warning("由於相依套件缺失，無法加載Basic Pitch模型")
                return
                
            self.model = ICASSP_2022_MODEL_PATH
            logger.info("Basic Pitch模型加載成功")
        except Exception as e:
            logger.error(f"加載Basic Pitch模型失敗: {str(e)}")
            raise
    
    def analyze_audio(self, audio_data: np.ndarray, sample_rate: int) -> Dict:
        """分析音頻數據
        
        Args:
            audio_data: 音頻數據
            sample_rate: 採樣率
            
        Returns:
            Dict: 分析結果，包含音高、節奏等信息
        """
        if not DEPENDENCIES_AVAILABLE:
            logger.error("缺少必要的相依套件，無法分析音頻")
            return {"error": "缺少必要的相依套件，無法分析音頻"}
            
        try:
            # 提取音高
            pitch_data = self._extract_pitch(audio_data, sample_rate)
            
            # 分析節奏
            rhythm_data = self._analyze_rhythm(audio_data, sample_rate)
            
            # 分析音色
            timbre_data = self._analyze_timbre(audio_data, sample_rate)
            
            return {
                "pitch": pitch_data,
                "rhythm": rhythm_data,
                "timbre": timbre_data
            }
        
        except Exception as e:
            logger.error(f"音頻分析失敗: {str(e)}")
            raise
    
    def _extract_pitch(self, audio_data: np.ndarray, sample_rate: int) -> Dict:
        """提取音高
        
        Args:
            audio_data: 音頻數據
            sample_rate: 採樣率
            
        Returns:
            Dict: 音高數據
        """
        try:
            if not DEPENDENCIES_AVAILABLE:
                return {"error": "缺少必要的相依套件，無法提取音高"}
                
            # 使用Basic Pitch提取音高
            model_output, midi_data, note_events = predict(
                self.model,
                audio_data,
                sample_rate
            )
            
            return {
                "midi_data": midi_data,
                "note_events": note_events,
                "confidence": model_output["confidence"]
            }
        
        except Exception as e:
            logger.error(f"音高提取失敗: {str(e)}")
            raise
    
    def _analyze_rhythm(self, audio_data: np.ndarray, sample_rate: int) -> Dict:
        """分析節奏
        
        Args:
            audio_data: 音頻數據
            sample_rate: 採樣率
            
        Returns:
            Dict: 節奏數據
        """
        try:
            if not DEPENDENCIES_AVAILABLE:
                return {"error": "缺少必要的相依套件，無法分析節奏"}
                
            # 提取節奏特徵
            onset_env = librosa.onset.onset_strength(
                y=audio_data,
                sr=sample_rate
            )
            
            # 檢測節拍
            tempo, beats = librosa.beat.beat_track(
                onset_envelope=onset_env,
                sr=sample_rate
            )
            
            # 分析節奏模式
            rhythm_pattern = self._analyze_rhythm_pattern(beats, sample_rate)
            
            return {
                "tempo": tempo,
                "beats": beats.tolist(),
                "pattern": rhythm_pattern
            }
        
        except Exception as e:
            logger.error(f"節奏分析失敗: {str(e)}")
            raise
    
    def _analyze_timbre(self, audio_data: np.ndarray, sample_rate: int) -> Dict:
        """分析音色
        
        Args:
            audio_data: 音頻數據
            sample_rate: 採樣率
            
        Returns:
            Dict: 音色數據
        """
        try:
            if not DEPENDENCIES_AVAILABLE:
                return {"error": "缺少必要的相依套件，無法分析音色"}
                
            # 提取MFCC特徵
            mfcc = librosa.feature.mfcc(
                y=audio_data,
                sr=sample_rate
            )
            
            # 提取色譜質心
            spectral_centroid = librosa.feature.spectral_centroid(
                y=audio_data,
                sr=sample_rate
            )
            
            # 提取色譜滾降
            spectral_rolloff = librosa.feature.spectral_rolloff(
                y=audio_data,
                sr=sample_rate
            )
            
            return {
                "mfcc": mfcc.tolist(),
                "spectral_centroid": spectral_centroid.tolist(),
                "spectral_rolloff": spectral_rolloff.tolist()
            }
        
        except Exception as e:
            logger.error(f"音色分析失敗: {str(e)}")
            raise
    
    def _analyze_rhythm_pattern(self, beats: np.ndarray, sample_rate: int) -> Dict:
        """分析節奏模式
        
        Args:
            beats: 節拍位置
            sample_rate: 採樣率
            
        Returns:
            Dict: 節奏模式數據
        """
        try:
            # 計算節拍間隔
            beat_intervals = np.diff(beats)
            
            # 分析節奏模式
            pattern = {
                "intervals": beat_intervals.tolist(),
                "regularity": np.std(beat_intervals),
                "complexity": len(np.unique(beat_intervals))
            }
            
            return pattern
        
        except Exception as e:
            logger.error(f"節奏模式分析失敗: {str(e)}")
            raise 