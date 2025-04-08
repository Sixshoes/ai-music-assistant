import axios from 'axios';
import React, { useEffect, useRef, useState } from 'react';

interface AudioRecorderProps {
  onRecordingComplete: (audioBlob: Blob, audioUrl: string) => void;
  maxDuration?: number; // 最大錄音時長，秒
}

interface AudioSegment {
  id: string;
  blob: Blob;
  url: string;
  duration: number;
}

const AudioRecorder: React.FC<AudioRecorderProps> = ({ 
  onRecordingComplete, 
  maxDuration = 60 
}) => {
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [recordingTime, setRecordingTime] = useState<number>(0);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [audioSegments, setAudioSegments] = useState<AudioSegment[]>([]);
  const [selectedSegmentId, setSelectedSegmentId] = useState<string | null>(null);
  const [waveformData, setWaveformData] = useState<number[]>([]);
  const [isPaused, setIsPaused] = useState<boolean>(false);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const waveformCanvasRef = useRef<HTMLCanvasElement | null>(null);
  const animationFrameRef = useRef<number | null>(null);

  // 清理函數
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
      audioSegments.forEach(segment => {
        URL.revokeObjectURL(segment.url);
      });
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, [audioUrl, audioSegments]);

  // 波形顯示初始化及更新
  useEffect(() => {
    if (isRecording && waveformCanvasRef.current && analyserRef.current) {
      drawWaveform();
    }
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isRecording]);

  // 繪製波形圖
  const drawWaveform = () => {
    if (!analyserRef.current || !waveformCanvasRef.current) return;

    const analyser = analyserRef.current;
    const canvas = waveformCanvasRef.current;
    const canvasCtx = canvas.getContext('2d');
    
    if (!canvasCtx) return;
    
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    
    const draw = () => {
      if (!analyser || !canvasCtx) return;
      
      analyser.getByteTimeDomainData(dataArray);
      
      canvasCtx.fillStyle = 'rgb(240, 240, 240)';
      canvasCtx.fillRect(0, 0, canvas.width, canvas.height);
      
      canvasCtx.lineWidth = 2;
      canvasCtx.strokeStyle = isRecording ? 'rgb(220, 0, 0)' : 'rgb(0, 0, 0)';
      canvasCtx.beginPath();
      
      const sliceWidth = canvas.width / bufferLength;
      let x = 0;
      
      for (let i = 0; i < bufferLength; i++) {
        const v = dataArray[i] / 128.0;
        const y = v * canvas.height / 2;
        
        if (i === 0) {
          canvasCtx.moveTo(x, y);
        } else {
          canvasCtx.lineTo(x, y);
        }
        
        x += sliceWidth;
      }
      
      canvasCtx.lineTo(canvas.width, canvas.height / 2);
      canvasCtx.stroke();
      
      // 更新波形數據用於可能的保存
      const normalizedData = Array.from(dataArray).map(val => val / 255);
      setWaveformData(normalizedData.slice(0, 100)); // 僅保留部分數據以減小狀態大小
      
      animationFrameRef.current = requestAnimationFrame(draw);
    };
    
    animationFrameRef.current = requestAnimationFrame(draw);
  };

  // 開始錄音
  const startRecording = async () => {
    try {
      // 重置狀態
      setAudioUrl(null);
      audioChunksRef.current = [];
      setRecordingTime(0);
      setIsPaused(false);
      
      // 獲取音頻流
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: { 
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        } 
      });
      
      streamRef.current = stream;
      
      // 設置音頻上下文和分析器
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      audioContextRef.current = audioContext;
      
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 2048;
      analyserRef.current = analyser;
      
      const source = audioContext.createMediaStreamSource(stream);
      source.connect(analyser);
      
      // 創建MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      mediaRecorderRef.current = mediaRecorder;
      
      // 設置數據處理
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      // 錄音結束時的處理
      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm;codecs=opus' });
        const url = URL.createObjectURL(audioBlob);
        
        // 創建新的音頻片段
        const newSegment: AudioSegment = {
          id: Date.now().toString(),
          blob: audioBlob,
          url,
          duration: recordingTime
        };
        
        setAudioSegments(prev => [...prev, newSegment]);
        setSelectedSegmentId(newSegment.id);
        setAudioUrl(url);
        
        // 通知父元件
        onRecordingComplete(audioBlob, url);
        
        // 停止所有軌道
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
        }
      };
      
      // 開始錄音
      mediaRecorder.start(100); // 每100ms生成一個數據塊，提高實時性
      setIsRecording(true);
      
      // 開始計時
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => {
          const newTime = prev + 1;
          // 達到最大時間自動停止
          if (newTime >= maxDuration && mediaRecorderRef.current?.state === 'recording') {
            stopRecording();
            return maxDuration;
          }
          return newTime;
        });
      }, 1000);
    } catch (error) {
      console.error('錄音失敗:', error);
      alert('無法訪問麥克風，請確保已授予權限');
    }
  };

  // 暫停錄音
  const pauseRecording = () => {
    if (mediaRecorderRef.current?.state === 'recording') {
      mediaRecorderRef.current.pause();
      setIsPaused(true);
      
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  };

  // 恢復錄音
  const resumeRecording = () => {
    if (mediaRecorderRef.current?.state === 'paused') {
      mediaRecorderRef.current.resume();
      setIsPaused(false);
      
      // 恢復計時
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => {
          const newTime = prev + 1;
          // 達到最大時間自動停止
          if (newTime >= maxDuration && mediaRecorderRef.current?.state === 'recording') {
            stopRecording();
            return maxDuration;
          }
          return newTime;
        });
      }, 1000);
    }
  };

  // 停止錄音
  const stopRecording = () => {
    if (mediaRecorderRef.current?.state === 'recording' || mediaRecorderRef.current?.state === 'paused') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsPaused(false);
      
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
      
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }
    }
  };

  // 上傳錄音到服務器
  const uploadRecording = async () => {
    if (audioSegments.length === 0) return;
    
    try {
      setIsProcessing(true);
      
      // 如果有多個片段，先合併
      let finalBlob: Blob;
      if (audioSegments.length > 1) {
        finalBlob = await mergeAudioSegments();
      } else {
        finalBlob = audioSegments[0].blob;
      }
      
      // 創建FormData
      const formData = new FormData();
      formData.append('audio', finalBlob, 'recording.webm');
      
      // 發送到服務器
      const response = await axios.post('/api/audio/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      console.log('上傳成功:', response.data);
      alert('錄音已成功上傳!');
      setIsProcessing(false);
    } catch (error) {
      console.error('上傳失敗:', error);
      alert('上傳錄音失敗，請稍後再試');
      setIsProcessing(false);
    }
  };

  // 合併多個音頻片段
  const mergeAudioSegments = async (): Promise<Blob> => {
    return new Promise(async (resolve, reject) => {
      try {
        // 創建音頻上下文
        const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
        
        // 解碼每個音頻片段
        const audioBuffers = await Promise.all(
          audioSegments.map(segment => 
            new Promise<AudioBuffer>((resolve, reject) => {
              const fileReader = new FileReader();
              fileReader.onload = async (event) => {
                try {
                  const arrayBuffer = event.target?.result as ArrayBuffer;
                  const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
                  resolve(audioBuffer);
                } catch (e) {
                  reject(e);
                }
              };
              fileReader.onerror = reject;
              fileReader.readAsArrayBuffer(segment.blob);
            })
          )
        );
        
        // 計算總長度
        const totalLength = audioBuffers.reduce((total, buffer) => total + buffer.length, 0);
        
        // 創建新的音頻緩衝區
        const mergedBuffer = audioContext.createBuffer(
          audioBuffers[0].numberOfChannels,
          totalLength,
          audioBuffers[0].sampleRate
        );
        
        // 複製每個緩衝區的數據
        let offset = 0;
        for (const buffer of audioBuffers) {
          for (let channel = 0; channel < buffer.numberOfChannels; channel++) {
            const channelData = buffer.getChannelData(channel);
            mergedBuffer.copyToChannel(channelData, channel, offset);
          }
          offset += buffer.length;
        }
        
        // 將合併後的緩衝區轉換為Blob
        const mediaStreamSource = audioContext.createMediaStreamDestination();
        const sourceNode = audioContext.createBufferSource();
        sourceNode.buffer = mergedBuffer;
        sourceNode.connect(mediaStreamSource);
        sourceNode.start(0);
        
        const mediaRecorder = new MediaRecorder(mediaStreamSource.stream);
        const chunks: Blob[] = [];
        
        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            chunks.push(event.data);
          }
        };
        
        mediaRecorder.onstop = () => {
          const mergedBlob = new Blob(chunks, { type: 'audio/webm;codecs=opus' });
          resolve(mergedBlob);
        };
        
        mediaRecorder.start();
        
        // 等待緩衝區處理完成
        setTimeout(() => {
          mediaRecorder.stop();
          sourceNode.disconnect();
          audioContext.close();
        }, mergedBuffer.duration * 1000 + 100);
      } catch (error) {
        console.error('合併音頻片段失敗:', error);
        reject(error);
      }
    });
  };

  // 選擇片段
  const selectSegment = (segmentId: string) => {
    setSelectedSegmentId(segmentId);
    const segment = audioSegments.find(s => s.id === segmentId);
    if (segment) {
      setAudioUrl(segment.url);
    }
  };

  // 刪除片段
  const deleteSegment = (segmentId: string) => {
    const segmentToDelete = audioSegments.find(s => s.id === segmentId);
    if (segmentToDelete) {
      URL.revokeObjectURL(segmentToDelete.url);
    }
    
    const updatedSegments = audioSegments.filter(s => s.id !== segmentId);
    setAudioSegments(updatedSegments);
    
    if (segmentId === selectedSegmentId) {
      if (updatedSegments.length > 0) {
        selectSegment(updatedSegments[updatedSegments.length - 1].id);
      } else {
        setSelectedSegmentId(null);
        setAudioUrl(null);
      }
    }
  };

  // 格式化時間
  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  // 請求執行音高修正
  const correctPitch = async () => {
    if (!selectedSegmentId) return;
    
    try {
      setIsProcessing(true);
      
      const selectedSegment = audioSegments.find(s => s.id === selectedSegmentId);
      if (!selectedSegment) return;
      
      // 創建FormData
      const formData = new FormData();
      formData.append('audio', selectedSegment.blob, 'correction_input.webm');
      
      // 發送到服務器進行音高修正
      const response = await axios.post('/api/audio/correct-pitch', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        responseType: 'blob'
      });
      
      // 處理返回的修正後音頻
      const correctedBlob = response.data;
      const correctedUrl = URL.createObjectURL(correctedBlob);
      
      // 創建新的音頻片段
      const newSegment: AudioSegment = {
        id: `corrected-${Date.now().toString()}`,
        blob: correctedBlob,
        url: correctedUrl,
        duration: selectedSegment.duration
      };
      
      setAudioSegments(prev => [...prev, newSegment]);
      setSelectedSegmentId(newSegment.id);
      setAudioUrl(correctedUrl);
      
      setIsProcessing(false);
      console.log('音高修正成功');
    } catch (error) {
      console.error('音高修正失敗:', error);
      alert('音高修正處理失敗，請稍後再試');
      setIsProcessing(false);
    }
  };

  return (
    <div className="audio-recorder">
      <div className="recorder-display">
        <div className="time-display">
          {formatTime(recordingTime)} {isRecording && <span className="recording-indicator">●</span>}
        </div>
        
        <canvas 
          ref={waveformCanvasRef} 
          className="waveform-display" 
          width="360" 
          height="80"
        />
        
        {audioUrl && (
          <audio controls src={audioUrl} className="audio-preview" />
        )}
      </div>
      
      <div className="recorder-controls">
        {!isRecording ? (
          <button 
            onClick={startRecording} 
            className="record-button"
            disabled={isProcessing}
          >
            開始錄音
          </button>
        ) : (
          <>
            {!isPaused ? (
              <button onClick={pauseRecording} className="pause-button">
                暫停錄音
              </button>
            ) : (
              <button onClick={resumeRecording} className="resume-button">
                繼續錄音
              </button>
            )}
            <button onClick={stopRecording} className="stop-button">
              停止錄音
            </button>
          </>
        )}
      </div>
      
      {audioSegments.length > 0 && (
        <div className="segments-container">
          <h3>錄音片段</h3>
          <div className="segments-list">
            {audioSegments.map(segment => (
              <div 
                key={segment.id}
                className={`segment-item ${selectedSegmentId === segment.id ? 'selected' : ''}`}
                onClick={() => selectSegment(segment.id)}
              >
                <span className="segment-duration">{formatTime(segment.duration)}</span>
                <button 
                  className="segment-delete-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteSegment(segment.id);
                  }}
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
          
          <div className="segments-actions">
            <button 
              onClick={uploadRecording} 
              className="upload-button"
              disabled={isProcessing}
            >
              {isProcessing ? '處理中...' : '上傳錄音'}
            </button>
            
            <button
              onClick={correctPitch}
              className="correct-button"
              disabled={!selectedSegmentId || isProcessing}
            >
              {isProcessing ? '處理中...' : '音高修正'}
            </button>
          </div>
        </div>
      )}
      
      <style>
        {`
          .audio-recorder {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 16px;
            background-color: #f9f9f9;
            max-width: 400px;
            margin: 0 auto;
          }
          
          .recorder-display {
            margin-bottom: 16px;
          }
          
          .time-display {
            font-size: 24px;
            text-align: center;
            margin-bottom: 12px;
            font-family: monospace;
          }
          
          .recording-indicator {
            color: red;
            animation: blink 1s infinite;
          }
          
          .waveform-display {
            width: 100%;
            height: 80px;
            background-color: #f0f0f0;
            border-radius: 4px;
            margin-bottom: 12px;
          }
          
          .audio-preview {
            width: 100%;
            margin-top: 8px;
          }
          
          .recorder-controls {
            display: flex;
            justify-content: center;
            gap: 12px;
            margin-bottom: 16px;
          }
          
          button {
            padding: 8px 16px;
            border-radius: 4px;
            border: none;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.2s;
          }
          
          .record-button {
            background-color: #4caf50;
            color: white;
          }
          
          .stop-button {
            background-color: #f44336;
            color: white;
          }
          
          .pause-button {
            background-color: #ff9800;
            color: white;
          }
          
          .resume-button {
            background-color: #2196f3;
            color: white;
          }
          
          .upload-button {
            background-color: #2196f3;
            color: white;
          }
          
          .correct-button {
            background-color: #9c27b0;
            color: white;
          }
          
          button:hover {
            opacity: 0.9;
            transform: translateY(-2px);
          }
          
          button:disabled {
            background-color: #cccccc;
            cursor: not-allowed;
            transform: none;
          }
          
          .segments-container {
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid #ddd;
          }
          
          .segments-container h3 {
            margin-top: 0;
            margin-bottom: 8px;
            font-size: 16px;
          }
          
          .segments-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-bottom: 16px;
            max-height: 200px;
            overflow-y: auto;
          }
          
          .segment-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 12px;
            background-color: #e9e9e9;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.2s;
          }
          
          .segment-item.selected {
            background-color: #bbdefb;
            border-left: 3px solid #2196f3;
          }
          
          .segment-item:hover {
            background-color: #e0e0e0;
          }
          
          .segment-delete-btn {
            background: none;
            border: none;
            color: #f44336;
            cursor: pointer;
            font-size: 16px;
            padding: 0 4px;
          }
          
          .segments-actions {
            display: flex;
            justify-content: space-between;
            gap: 8px;
          }
          
          @keyframes blink {
            0% { opacity: 1; }
            50% { opacity: 0; }
            100% { opacity: 1; }
          }
        `}
      </style>
    </div>
  );
};

export default AudioRecorder; 