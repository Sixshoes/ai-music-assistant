"""工作流程

定義不同類型指令的處理工作流程
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import time
import random
import logging
import json

from ..mcp_schema import (
    MCPCommand,
    CommandType,
    MusicTheoryAnalysis,
    MusicKey,
    TimeSignature,
    ChordProgression,
    MusicParameters,
    ModelType
)


class Workflow(ABC):
    """工作流程抽象基類"""
    
    def __init__(self):
        """初始化工作流程"""
        self.logger = logging.getLogger(__name__)
    
    @abstractmethod
    def execute(self, command: MCPCommand, context: Dict[str, Any]) -> Dict[str, Any]:
        """執行工作流程
        
        Args:
            command: MCP指令對象
            context: 工作流程執行上下文，包含以下内容：
                - command_id: 指令ID
                - model_interface: 主要模型介面
                - additional_models: 額外可用的模型介面列表
                - logger_service: 日誌服務
            
        Returns:
            Dict[str, Any]: 處理結果字典
        """
        pass
    
    def cancel(self, command_id: str) -> bool:
        """取消工作流程的執行
        
        Args:
            command_id: 指令ID
        
        Returns:
            bool: 是否成功取消
        """
        self.logger.info(f"嘗試取消工作流程: {command_id}")
        # 基礎實現只記錄取消嘗試，子類可覆蓋提供實際取消邏輯
        return False


class TextToMusicWorkflow(Workflow):
    """文字到音樂工作流程"""
    
    def execute(self, command: MCPCommand, context: Dict[str, Any]) -> Dict[str, Any]:
        """執行文字到音樂工作流程
        
        Args:
            command: MCP指令對象
            context: 工作流程執行上下文
            
        Returns:
            Dict[str, Any]: 生成的音樂數據
        """
        command_id = context.get("command_id", "unknown")
        model_interface = context.get("model_interface")
        logger_service = context.get("logger_service")
        
        self.logger.info(f"執行文字到音樂工作流程，指令ID: {command_id}, 輸入文字: {command.text_input}")
        
        if command.command_type != CommandType.TEXT_TO_MUSIC:
            raise ValueError(f"不適用的指令類型 {command.command_type}，應為 {CommandType.TEXT_TO_MUSIC}")
        
        # 記錄工作流程步驟
        if logger_service:
            logger_service.log_workflow_step(
                command_id,
                "text_analysis",
                "started",
                {"text_input": command.text_input}
            )
        
        # 獲取參數或使用默認值
        params = command.parameters or MusicParameters()
        
        # 解析文本以擴充音樂參數
        params = self._analyze_text_input(command.text_input, params)
        
        # 記錄參數解析結果
        if logger_service:
            logger_service.log_workflow_step(
                command_id,
                "text_analysis",
                "completed",
                {"parameters": params.model_dump()}
            )
        
        # 通過模型接口生成旋律
        try:
            if logger_service:
                logger_service.log_workflow_step(command_id, "melody_generation", "started")
            
            melody = model_interface.generate_melody(params)
            
            if logger_service:
                logger_service.log_workflow_step(
                    command_id,
                    "melody_generation",
                    "completed",
                    {"note_count": len(melody)}
                )
        except Exception as e:
            self.logger.error(f"生成旋律時出錯: {str(e)}")
            if logger_service:
                logger_service.log_workflow_step(
                    command_id,
                    "melody_generation",
                    "failed",
                    {"error": str(e)}
                )
            raise
        
        # 通過模型接口生成伴奏
        try:
            if logger_service:
                logger_service.log_workflow_step(command_id, "accompaniment_generation", "started")
            
            accompaniment = model_interface.generate_accompaniment(melody, params)
            
            if logger_service:
                logger_service.log_workflow_step(
                    command_id,
                    "accompaniment_generation",
                    "completed",
                    {"track_count": len(accompaniment)}
                )
        except Exception as e:
            self.logger.error(f"生成伴奏時出錯: {str(e)}")
            if logger_service:
                logger_service.log_workflow_step(
                    command_id,
                    "accompaniment_generation",
                    "failed",
                    {"error": str(e)}
                )
            # 繼續，但使用空伴奏
            accompaniment = {"chords": [], "bass": []}
        
        # 嘗試使用 Music21 進行旋律分析
        analysis = None
        try:
            # 檢查是否有可用的 Music21 接口
            music21_interface = None
            for interface in context.get("additional_models", []):
                if interface.model_type == ModelType.MUSIC21:
                    music21_interface = interface
                    break
            
            if music21_interface:
                if logger_service:
                    logger_service.log_workflow_step(command_id, "melody_analysis", "started")
                
                analysis_result = music21_interface.analyze_melody(melody)
                analysis = analysis_result
                
                if logger_service:
                    logger_service.log_workflow_step(
                        command_id,
                        "melody_analysis",
                        "completed"
                    )
        except Exception as e:
            self.logger.warning(f"旋律分析時出錯: {str(e)}")
            if logger_service:
                logger_service.log_workflow_step(
                    command_id,
                    "melody_analysis",
                    "failed",
                    {"error": str(e)}
                )
        
        # 組合音樂數據
        midi_data = self._create_midi_data(melody, accompaniment, params)
        
        # 創建結果字典
        result = {
            "music_data": {
                "midi_data": json.dumps(midi_data),
                "audio_data": "data:audio/mpeg;base64,SGVsbG8gV29ybGQh",  # 示例base64音頻數據
                "tracks": {
                    "melody": melody,
                    "chords": accompaniment.get("chords", []),
                    "bass": accompaniment.get("bass", [])
                }
            },
            "analysis": analysis,
            "models_used": [model_interface.model_type],
            "suggestions": self._generate_suggestions(command.text_input, params)
        }
        
        # 如果使用了Music21接口，添加到已使用模型列表
        if music21_interface:
            result["models_used"].append(music21_interface.model_type)
        
        self.logger.info(f"文字到音樂工作流程完成，指令ID: {command_id}")
        return result
        
    def _analyze_text_input(self, text_input: str, params: MusicParameters) -> MusicParameters:
        """分析文本輸入，提取音樂參數
        
        Args:
            text_input: 輸入文字
            params: 初始音樂參數
            
        Returns:
            MusicParameters: 擴充後的音樂參數
        """
        # 如果已經有充分的參數，則不再分析
        if params.key and params.tempo and params.genre and params.emotion:
            return params
        
        # 簡單的關鍵詞分析
        param_updates = {}
        
        # 提取情感
        if not params.emotion:
            if any(keyword in text_input.lower() for keyword in ["快樂", "歡快", "歡喜", "開心"]):
                param_updates["emotion"] = "happy"
            elif any(keyword in text_input.lower() for keyword in ["悲傷", "憂鬱", "傷心", "哀傷"]):
                param_updates["emotion"] = "sad"
            elif any(keyword in text_input.lower() for keyword in ["平靜", "安寧", "寧靜", "放鬆"]):
                param_updates["emotion"] = "calm"
            elif any(keyword in text_input.lower() for keyword in ["神秘", "奇幻", "玄幻"]):
                param_updates["emotion"] = "mysterious"
            elif any(keyword in text_input.lower() for keyword in ["浪漫", "溫馨", "甜蜜"]):
                param_updates["emotion"] = "romantic"
        
        # 提取風格
        if not params.genre:
            if any(keyword in text_input.lower() for keyword in ["古典", "交響", "協奏", "奏鳴"]):
                param_updates["genre"] = "classical"
            elif any(keyword in text_input.lower() for keyword in ["爵士", "藍調", "自由"]):
                param_updates["genre"] = "jazz"
            elif any(keyword in text_input.lower() for keyword in ["流行", "通俗", "當代"]):
                param_updates["genre"] = "pop"
            elif any(keyword in text_input.lower() for keyword in ["搖滾", "重金屬", "龐克"]):
                param_updates["genre"] = "rock"
            elif any(keyword in text_input.lower() for keyword in ["電子", "舞曲", "節拍"]):
                param_updates["genre"] = "electronic"
        
        # 提取速度
        if not params.tempo:
            if any(keyword in text_input.lower() for keyword in ["快速", "急促", "迅速"]):
                param_updates["tempo"] = 140
            elif any(keyword in text_input.lower() for keyword in ["中速", "適中"]):
                param_updates["tempo"] = 100
            elif any(keyword in text_input.lower() for keyword in ["慢速", "緩慢", "舒緩"]):
                param_updates["tempo"] = 70
        
        # 更新參數
        if param_updates:
            params.update(param_updates)
        
        # 設置默認值
        if not params.tempo:
            params.tempo = 120
        if not params.key:
            params.key = "C"
        
        return params
        
    def _create_midi_data(self, melody: List[Any], accompaniment: Dict[str, List[Any]], params: MusicParameters) -> Dict[str, Any]:
        """創建MIDI數據
        
        Args:
            melody: 旋律音符列表
            accompaniment: 伴奏音符字典
            params: 音樂參數
            
        Returns:
            Dict[str, Any]: MIDI數據
        """
        midi_data = {
            "tempo": params.tempo or 120,
            "key": str(params.key) if params.key else "C",
            "time_signature": str(params.time_signature) if params.time_signature else "4/4",
            "instruments": {}
        }
        
        # 添加旋律
        if melody:
            notes = []
            for note in melody:
                notes.append({
                    "pitch": note.pitch,
                    "start_time": note.start_time,
                    "duration": note.duration,
                    "velocity": note.velocity
                })
            
            midi_data["instruments"]["melody"] = {
                "program": 0,  # 鋼琴
                "notes": notes
            }
        
        # 添加和弦
        if "chords" in accompaniment and accompaniment["chords"]:
            notes = []
            for note in accompaniment["chords"]:
                notes.append({
                    "pitch": note.pitch,
                    "start_time": note.start_time,
                    "duration": note.duration,
                    "velocity": note.velocity
                })
            
            midi_data["instruments"]["chords"] = {
                "program": 0,  # 鋼琴
                "notes": notes
            }
        
        # 添加低音
        if "bass" in accompaniment and accompaniment["bass"]:
            notes = []
            for note in accompaniment["bass"]:
                notes.append({
                    "pitch": note.pitch,
                    "start_time": note.start_time,
                    "duration": note.duration,
                    "velocity": note.velocity
                })
            
            midi_data["instruments"]["bass"] = {
                "program": 32,  # 原聲貝斯
                "notes": notes
            }
        
        return midi_data
    
    def _generate_suggestions(self, text_input: str, params: MusicParameters) -> List[str]:
        """生成音樂建議
        
        Args:
            text_input: 輸入文字
            params: 音樂參數
            
        Returns:
            List[str]: 建議列表
        """
        suggestions = []
        
        # 基於文本內容生成建議
        if "慢" in text_input and (params.tempo and params.tempo > 100):
            suggestions.append("考慮降低速度以更好地表達文本中提到的緩慢感覺")
        
        if "安靜" in text_input or "平靜" in text_input:
            suggestions.append("可以降低整體音量並使用更柔和的樂器來表達平靜的氛圍")
        
        # 添加通用建議
        suggestions.append("嘗試為音樂添加更多的動態變化，以增強表現力")
        suggestions.append("考慮在橋段部分使用不同的和聲進行，增加音樂的驚喜感")
        
        return suggestions


class MelodyToArrangementWorkflow(Workflow):
    """旋律到編曲工作流程"""
    
    def execute(self, command: MCPCommand, context: Dict[str, Any]) -> Dict[str, Any]:
        """執行旋律到編曲轉換工作流程
        
        Args:
            command: 旋律到編曲指令
            context: 工作流程執行上下文
            
        Returns:
            Dict[str, Any]: 生成的編曲數據
        """
        command_id = context.get("command_id", "unknown")
        model_interface = context.get("model_interface")
        logger_service = context.get("logger_service")
        
        if command.command_type != CommandType.MELODY_TO_ARRANGEMENT:
            raise ValueError(f"不適用的指令類型 {command.command_type}，應為 {CommandType.MELODY_TO_ARRANGEMENT}")
        
        # 記錄工作流程開始
        self.logger.info(f"執行旋律到編曲工作流程，指令ID: {command_id}")
        
        # 步驟 1: 獲取旋律輸入（MIDI或音頻）
        melody_data = None
        
        if command.melody_input:
            if logger_service:
                logger_service.log_workflow_step(
                    command_id,
                    "input_processing",
                    "completed",
                    {"input_type": "melody", "notes_count": len(command.melody_input.notes)}
                )
            melody_data = command.melody_input.notes
            
        elif command.audio_input:
            if logger_service:
                logger_service.log_workflow_step(
                    command_id,
                    "input_processing",
                    "started",
                    {"input_type": "audio"}
                )
            
            # 找到 BasicPitch 接口進行音頻轉旋律
            basic_pitch_interface = None
            for interface in context.get("additional_models", []):
                if interface.model_type == ModelType.BASIC_PITCH:
                    basic_pitch_interface = interface
                    break
            
            if not basic_pitch_interface:
                raise ValueError("處理音頻輸入需要 BasicPitch 模型，但該模型不可用")
            
            # 通過 BasicPitch 轉換音頻為旋律
            try:
                melody_input = basic_pitch_interface.audio_to_melody(command.audio_input.audio_data_url)
                melody_data = melody_input.notes
                
                if logger_service:
                    logger_service.log_workflow_step(
                        command_id,
                        "input_processing",
                        "completed",
                        {"input_type": "audio", "notes_count": len(melody_data)}
                    )
            except Exception as e:
                error_msg = f"音頻轉旋律失敗: {str(e)}"
                self.logger.error(error_msg)
                if logger_service:
                    logger_service.log_workflow_step(
                        command_id,
                        "input_processing",
                        "failed",
                        {"error": error_msg}
                    )
                raise ValueError(error_msg)
        else:
            raise ValueError("缺少旋律或音頻輸入")
        
        # 步驟 2: 分析旋律獲取調性和結構
        try:
            if logger_service:
                logger_service.log_workflow_step(command_id, "melody_analysis", "started")
            
            # 優先使用 Music21 進行分析
            music21_interface = None
            for interface in context.get("additional_models", []):
                if interface.model_type == ModelType.MUSIC21:
                    music21_interface = interface
                    break
            
            if music21_interface:
                analysis = music21_interface.analyze_melody(melody_data)
            else:
                # 退回到主模型的分析功能
                analysis = model_interface.analyze_melody(melody_data)
            
            if logger_service:
                logger_service.log_workflow_step(
                    command_id,
                    "melody_analysis",
                    "completed"
                )
        except Exception as e:
            error_msg = f"旋律分析失敗: {str(e)}"
            self.logger.error(error_msg)
            if logger_service:
                logger_service.log_workflow_step(
                    command_id,
                    "melody_analysis",
                    "failed",
                    {"error": error_msg}
                )
            # 創建一個基本分析
            analysis = {
                "key": "C",
                "tempo": command.parameters.tempo if command.parameters and command.parameters.tempo else 120,
                "time_signature": "4/4",
                "chord_progression": {
                    "chords": ["C", "Am", "F", "G"],
                    "durations": [1.0, 1.0, 1.0, 1.0]
                }
            }
        
        # 步驟 3: 生成和聲進行 (如果分析中還沒有的話)
        harmony = None
        if "chord_progression" in analysis:
            harmony = analysis["chord_progression"]
        
        # 步驟 4: 生成完整編曲
        try:
            if logger_service:
                logger_service.log_workflow_step(command_id, "arrangement_generation", "started")
            
            # 使用主模型生成伴奏
            params = command.parameters or MusicParameters()
            
            # 從分析結果更新參數
            param_updates = {}
            if "key" in analysis and analysis["key"]:
                param_updates["key"] = analysis["key"]
            if "tempo" in analysis and analysis["tempo"]:
                param_updates["tempo"] = analysis["tempo"]
            if "time_signature" in analysis and analysis["time_signature"]:
                param_updates["time_signature"] = analysis["time_signature"]
            
            if param_updates:
                params.update(param_updates)
            
            # 生成伴奏
            arrangement = model_interface.generate_accompaniment(melody_data, params)
            
            if logger_service:
                logger_service.log_workflow_step(
                    command_id,
                    "arrangement_generation",
                    "completed",
                    {"track_count": len(arrangement) if arrangement else 0}
                )
        except Exception as e:
            error_msg = f"編曲生成失敗: {str(e)}"
            self.logger.error(error_msg)
            if logger_service:
                logger_service.log_workflow_step(
                    command_id,
                    "arrangement_generation",
                    "failed",
                    {"error": error_msg}
                )
            # 返回空的伴奏
            arrangement = {"chords": [], "bass": []}
        
        # 組合音樂數據
        midi_data = self._create_midi_data(melody_data, arrangement, params)
        
        # 創建結果字典
        models_used = [model_interface.model_type]
        if music21_interface:
            models_used.append(music21_interface.model_type)
        if basic_pitch_interface:
            models_used.append(basic_pitch_interface.model_type)
        
        result = {
            "music_data": {
                "midi_data": json.dumps(midi_data),
                "audio_data": "data:audio/mpeg;base64,SGVsbG8gV29ybGQh",  # 示例base64音頻數據
                "tracks": {
                    "melody": melody_data,
                    "chords": arrangement.get("chords", []),
                    "bass": arrangement.get("bass", [])
                }
            },
            "analysis": analysis,
            "models_used": models_used,
            "suggestions": self._generate_suggestions(analysis) if isinstance(analysis, dict) else []
        }
        
        self.logger.info(f"旋律到編曲工作流程完成，指令ID: {command_id}")
        return result
    
    def _create_midi_data(self, melody: List[Any], arrangement: Dict[str, List[Any]], params: MusicParameters) -> Dict[str, Any]:
        """創建MIDI數據
        
        Args:
            melody: 旋律音符列表
            arrangement: 編曲音符字典
            params: 音樂參數
            
        Returns:
            Dict[str, Any]: MIDI數據
        """
        midi_data = {
            "tempo": params.tempo or 120,
            "key": str(params.key) if params.key else "C",
            "time_signature": str(params.time_signature) if params.time_signature else "4/4",
            "instruments": {}
        }
        
        # 添加旋律
        if melody:
            notes = []
            for note in melody:
                notes.append({
                    "pitch": note.pitch,
                    "start_time": note.start_time,
                    "duration": note.duration,
                    "velocity": note.velocity
                })
            
            midi_data["instruments"]["melody"] = {
                "program": 0,  # 鋼琴
                "notes": notes
            }
        
        # 添加和弦
        if "chords" in arrangement and arrangement["chords"]:
            notes = []
            for note in arrangement["chords"]:
                notes.append({
                    "pitch": note.pitch,
                    "start_time": note.start_time,
                    "duration": note.duration,
                    "velocity": note.velocity
                })
            
            midi_data["instruments"]["chords"] = {
                "program": 0,  # 鋼琴
                "notes": notes
            }
        
        # 添加低音
        if "bass" in arrangement and arrangement["bass"]:
            notes = []
            for note in arrangement["bass"]:
                notes.append({
                    "pitch": note.pitch,
                    "start_time": note.start_time,
                    "duration": note.duration,
                    "velocity": note.velocity
                })
            
            midi_data["instruments"]["bass"] = {
                "program": 32,  # 原聲貝斯
                "notes": notes
            }
        
        return midi_data
    
    def _generate_suggestions(self, analysis: Dict[str, Any]) -> List[str]:
        """生成音樂建議
        
        Args:
            analysis: 分析結果
            
        Returns:
            List[str]: 建議列表
        """
        suggestions = []
        
        # 從分析結果生成建議
        if "harmony_issues" in analysis and analysis["harmony_issues"]:
            for issue in analysis["harmony_issues"]:
                suggestions.append(f"和聲問題: {issue}")
        
        # 添加一些常規建議
        suggestions.append("考慮在伴奏中加入更多的節奏變化，增加音樂的活力")
        suggestions.append("可以嘗試在編曲中加入對比段落增加音樂的變化")
        
        # 如果分析包含了原始建議，合併它們
        if "suggestions" in analysis and analysis["suggestions"]:
            suggestions.extend(analysis["suggestions"])
        
        return suggestions 


class MusicAnalysisWorkflow(Workflow):
    """音樂分析工作流程"""

    def execute(self, command: MCPCommand, context: Dict[str, Any]) -> Dict[str, Any]:
        """執行音樂分析工作流程
        
        Args:
            command: MCP指令對象
            context: 工作流程執行上下文
            
        Returns:
            Dict[str, Any]: 音樂分析結果
        """
        command_id = context.get("command_id", "unknown")
        model_interface = context.get("model_interface")
        logger_service = context.get("logger_service")
        
        if command.command_type != CommandType.MUSIC_ANALYSIS:
            raise ValueError(f"不適用的指令類型 {command.command_type}，應為 {CommandType.MUSIC_ANALYSIS}")
        
        self.logger.info(f"執行音樂分析工作流程，指令ID: {command_id}")
        
        # 檢查輸入類型
        melody_data = None
        
        if command.melody_input:
            if logger_service:
                logger_service.log_workflow_step(
                    command_id,
                    "input_processing",
                    "completed",
                    {"input_type": "melody", "notes_count": len(command.melody_input.notes)}
                )
            melody_data = command.melody_input.notes
            
        elif command.audio_input:
            if logger_service:
                logger_service.log_workflow_step(
                    command_id,
                    "input_processing",
                    "started",
                    {"input_type": "audio"}
                )
            
            # 找到 BasicPitch 接口進行音頻轉旋律
            basic_pitch_interface = None
            for interface in context.get("additional_models", []):
                if interface.model_type == ModelType.BASIC_PITCH:
                    basic_pitch_interface = interface
                    break
            
            if not basic_pitch_interface:
                raise ValueError("處理音頻輸入需要 BasicPitch 模型，但該模型不可用")
            
            # 通過 BasicPitch 轉換音頻為旋律
            try:
                melody_input = basic_pitch_interface.audio_to_melody(command.audio_input.audio_data_url)
                melody_data = melody_input.notes
                
                if logger_service:
                    logger_service.log_workflow_step(
                        command_id,
                        "input_processing",
                        "completed",
                        {"input_type": "audio", "notes_count": len(melody_data)}
                    )
            except Exception as e:
                error_msg = f"音頻轉旋律失敗: {str(e)}"
                self.logger.error(error_msg)
                if logger_service:
                    logger_service.log_workflow_step(
                        command_id,
                        "input_processing",
                        "failed",
                        {"error": error_msg}
                    )
                raise ValueError(error_msg)
        else:
            raise ValueError("缺少旋律或音頻輸入")
        
        # 進行音樂分析
        try:
            if logger_service:
                logger_service.log_workflow_step(command_id, "music_analysis", "started")
            
            # Music21 是音樂分析的最佳選擇
            if model_interface.model_type == ModelType.MUSIC21:
                analysis = model_interface.analyze_melody(melody_data)
            else:
                # 嘗試找尋 Music21 介面
                music21_interface = None
                for interface in context.get("additional_models", []):
                    if interface.model_type == ModelType.MUSIC21:
                        music21_interface = interface
                        break
                
                if music21_interface:
                    analysis = music21_interface.analyze_melody(melody_data)
                    # 將 Music21 添加到已使用模型
                    models_used = [model_interface.model_type, music21_interface.model_type]
                else:
                    # 退回到主模型的分析功能
                    analysis = model_interface.analyze_melody(melody_data)
                    models_used = [model_interface.model_type]
            
            if logger_service:
                logger_service.log_workflow_step(
                    command_id,
                    "music_analysis",
                    "completed",
                    {"analysis_keys": list(analysis.keys()) if isinstance(analysis, dict) else "object"}
                )
        except Exception as e:
            error_msg = f"音樂分析失敗: {str(e)}"
            self.logger.error(error_msg)
            if logger_service:
                logger_service.log_workflow_step(
                    command_id,
                    "music_analysis",
                    "failed",
                    {"error": error_msg}
                )
            raise
        
        # 返回分析結果
        result = {
            "analysis": analysis,
            "models_used": models_used if 'models_used' in locals() else [model_interface.model_type],
            "suggestions": self._generate_suggestions(analysis) if isinstance(analysis, dict) and not "suggestions" in analysis else analysis.get("suggestions", [])
        }
        
        self.logger.info(f"音樂分析工作流程完成，指令ID: {command_id}")
        return result
    
    def _generate_suggestions(self, analysis: Dict[str, Any]) -> List[str]:
        """基於分析結果生成建議
        
        Args:
            analysis: 分析結果
            
        Returns:
            List[str]: 建議列表
        """
        suggestions = []
        
        # 從分析結果生成建議
        if "harmony_issues" in analysis and analysis["harmony_issues"]:
            for issue in analysis["harmony_issues"]:
                suggestions.append(f"和聲問題: {issue}")
        
        # 添加其他音樂理論相關建議
        if "key" in analysis and analysis["key"]:
            suggestions.append(f"曲目調性為 {analysis['key']}，可以考慮在創作中使用這個調性的特性")
        
        if "chord_progression" in analysis and isinstance(analysis["chord_progression"], dict):
            chord_progression = analysis["chord_progression"]
            if "chords" in chord_progression and len(chord_progression["chords"]) > 0:
                chords_str = " - ".join(chord_progression["chords"][:8])  # 只顯示前8個和弦
                suggestions.append(f"核心和弦進行: {chords_str}")
        
        return suggestions


class PitchCorrectionWorkflow(Workflow):
    """音高校正工作流程"""
    
    def execute(self, command: MCPCommand, context: Dict[str, Any]) -> Dict[str, Any]:
        """執行音高校正工作流程
        
        Args:
            command: MCP指令對象
            context: 工作流程執行上下文
            
        Returns:
            Dict[str, Any]: 校正後的音頻數據
        """
        command_id = context.get("command_id", "unknown")
        model_interface = context.get("model_interface")
        logger_service = context.get("logger_service")
        
        if command.command_type != CommandType.PITCH_CORRECTION:
            raise ValueError(f"不適用的指令類型 {command.command_type}，應為 {CommandType.PITCH_CORRECTION}")
        
        self.logger.info(f"執行音高校正工作流程，指令ID: {command_id}")
        
        # 檢查是否是 BasicPitch 模型
        if model_interface.model_type != ModelType.BASIC_PITCH:
            # 嘗試找到 BasicPitch 介面
            basic_pitch_interface = None
            for interface in context.get("additional_models", []):
                if interface.model_type == ModelType.BASIC_PITCH:
                    basic_pitch_interface = interface
                    break
            
            if basic_pitch_interface:
                model_interface = basic_pitch_interface
            else:
                raise ValueError("音高校正需要 BasicPitch 模型，但該模型不可用")
        
        # 檢查音頻輸入
        if not command.audio_input or not command.audio_input.audio_data_url:
            raise ValueError("音高校正需要音頻輸入")
        
        # 執行音高校正
        try:
            if logger_service:
                logger_service.log_workflow_step(command_id, "pitch_correction", "started")
            
            corrected_audio = model_interface.correct_pitch(command.audio_input.audio_data_url)
            
            if logger_service:
                logger_service.log_workflow_step(
                    command_id,
                    "pitch_correction",
                    "completed"
                )
        except Exception as e:
            error_msg = f"音高校正失敗: {str(e)}"
            self.logger.error(error_msg)
            if logger_service:
                logger_service.log_workflow_step(
                    command_id,
                    "pitch_correction",
                    "failed",
                    {"error": error_msg}
                )
            raise
        
        # 可選：分析原始和校正後的音頻
        analysis = None
        try:
            # 嘗試轉換音頻為旋律並分析
            melody_input = model_interface.audio_to_melody(corrected_audio)
            
            # 嘗試尋找 Music21 接口進行分析
            music21_interface = None
            for interface in context.get("additional_models", []):
                if interface.model_type == ModelType.MUSIC21:
                    music21_interface = interface
                    break
            
            if music21_interface:
                analysis = music21_interface.analyze_melody(melody_input.notes)
                models_used = [model_interface.model_type, music21_interface.model_type]
            else:
                # 使用 BasicPitch 的簡單分析
                analysis = model_interface.analyze_melody(melody_input.notes)
                models_used = [model_interface.model_type]
            
        except Exception as e:
            self.logger.warning(f"校正後音頻分析失敗: {str(e)}")
            models_used = [model_interface.model_type]
            # 繼續執行，不因分析失敗而中斷整個工作流程
        
        # 返回結果
        result = {
            "music_data": {
                "audio_data": corrected_audio
            },
            "analysis": analysis,
            "models_used": models_used if 'models_used' in locals() else [model_interface.model_type],
            "suggestions": [
                "已對音頻進行音高校正，在關鍵音符處修正了音準問題",
                "建議在正式錄製前進行充分的發聲練習",
                "可以嘗試使用更多的氣息支持來穩定音高"
            ]
        }
        
        self.logger.info(f"音高校正工作流程完成，指令ID: {command_id}")
        return result 


class StyleTransferWorkflow(Workflow):
    """風格轉換工作流程"""
    
    def execute(self, command: MCPCommand, context: Dict[str, Any]) -> Dict[str, Any]:
        """執行風格轉換工作流程
        
        Args:
            command: MCP指令對象
            context: 工作流程執行上下文
            
        Returns:
            Dict[str, Any]: 風格轉換後的音樂數據
        """
        command_id = context.get("command_id", "unknown")
        model_interface = context.get("model_interface")
        logger_service = context.get("logger_service")
        
        if command.command_type != CommandType.STYLE_TRANSFER:
            raise ValueError(f"不適用的指令類型 {command.command_type}，應為 {CommandType.STYLE_TRANSFER}")
        
        self.logger.info(f"執行風格轉換工作流程，指令ID: {command_id}")
        
        # 檢查輸入類型和目標風格
        melody_data = None
        
        if not command.parameters or not command.parameters.genre:
            raise ValueError("風格轉換需要指定目標風格參數")
        
        if command.melody_input:
            if logger_service:
                logger_service.log_workflow_step(
                    command_id,
                    "input_processing",
                    "completed",
                    {"input_type": "melody", "notes_count": len(command.melody_input.notes)}
                )
            melody_data = command.melody_input.notes
            
        elif command.audio_input:
            if logger_service:
                logger_service.log_workflow_step(
                    command_id,
                    "input_processing",
                    "started",
                    {"input_type": "audio"}
                )
            
            # 找到 BasicPitch 接口進行音頻轉旋律
            basic_pitch_interface = None
            for interface in context.get("additional_models", []):
                if interface.model_type == ModelType.BASIC_PITCH:
                    basic_pitch_interface = interface
                    break
            
            if not basic_pitch_interface:
                raise ValueError("處理音頻輸入需要 BasicPitch 模型，但該模型不可用")
            
            # 通過 BasicPitch 轉換音頻為旋律
            try:
                melody_input = basic_pitch_interface.audio_to_melody(command.audio_input.audio_data_url)
                melody_data = melody_input.notes
                
                if logger_service:
                    logger_service.log_workflow_step(
                        command_id,
                        "input_processing",
                        "completed",
                        {"input_type": "audio", "notes_count": len(melody_data)}
                    )
            except Exception as e:
                error_msg = f"音頻轉旋律失敗: {str(e)}"
                self.logger.error(error_msg)
                if logger_service:
                    logger_service.log_workflow_step(
                        command_id,
                        "input_processing",
                        "failed",
                        {"error": error_msg}
                    )
                raise ValueError(error_msg)
        else:
            raise ValueError("缺少旋律或音頻輸入")
        
        # 分析原始旋律以瞭解其結構
        try:
            if logger_service:
                logger_service.log_workflow_step(
                    command_id, 
                    "melody_analysis", 
                    "started"
                )
            
            # 尋找 Music21 接口進行分析
            music21_interface = None
            for interface in context.get("additional_models", []):
                if interface.model_type == ModelType.MUSIC21:
                    music21_interface = interface
                    break
            
            if music21_interface:
                analysis = music21_interface.analyze_melody(melody_data)
                models_used = [model_interface.model_type, music21_interface.model_type]
            else:
                # 使用主模型進行簡單分析
                analysis = model_interface.analyze_melody(melody_data)
                models_used = [model_interface.model_type]
            
            if logger_service:
                logger_service.log_workflow_step(
                    command_id,
                    "melody_analysis",
                    "completed"
                )
        except Exception as e:
            self.logger.warning(f"旋律分析失敗: {str(e)}")
            analysis = None
            models_used = [model_interface.model_type]
            if 'basic_pitch_interface' in locals() and basic_pitch_interface:
                models_used.append(basic_pitch_interface.model_type)
        
        # 執行風格轉換 (目前我們通過重新生成伴奏來模擬)
        try:
            if logger_service:
                logger_service.log_workflow_step(
                    command_id,
                    "style_transfer",
                    "started",
                    {"target_style": command.parameters.genre}
                )
            
            # 使用主模型生成指定風格的伴奏
            accompaniment = model_interface.generate_accompaniment(melody_data, command.parameters)
            
            if logger_service:
                logger_service.log_workflow_step(
                    command_id,
                    "style_transfer",
                    "completed"
                )
        except Exception as e:
            error_msg = f"風格轉換失敗: {str(e)}"
            self.logger.error(error_msg)
            if logger_service:
                logger_service.log_workflow_step(
                    command_id,
                    "style_transfer",
                    "failed",
                    {"error": error_msg}
                )
            raise
        
        # 組合音樂數據
        midi_data = self._create_midi_data(melody_data, accompaniment, command.parameters)
        
        # 返回結果
        result = {
            "music_data": {
                "midi_data": json.dumps(midi_data),
                "audio_data": "data:audio/mpeg;base64,SGVsbG8gV29ybGQh",  # 示例base64音頻數據
                "tracks": {
                    "melody": melody_data,
                    "chords": accompaniment.get("chords", []),
                    "bass": accompaniment.get("bass", [])
                }
            },
            "analysis": analysis,
            "models_used": models_used,
            "suggestions": [
                f"嘗試調整音量平衡以更好地突出 {command.parameters.genre} 風格的特點",
                "考慮為特定風格添加更多特色樂器",
                "可以進一步調整速度來增強風格感"
            ]
        }
        
        self.logger.info(f"風格轉換工作流程完成，指令ID: {command_id}")
        return result

    def _create_midi_data(self, melody: List[Any], accompaniment: Dict[str, List[Any]], params: MusicParameters) -> Dict[str, Any]:
        """創建MIDI數據
        
        Args:
            melody: 旋律音符列表
            accompaniment: 伴奏音符字典
            params: 音樂參數
            
        Returns:
            Dict[str, Any]: MIDI數據
        """
        midi_data = {
            "tempo": params.tempo or 120,
            "key": str(params.key) if params.key else "C",
            "time_signature": str(params.time_signature) if params.time_signature else "4/4",
            "instruments": {}
        }
        
        # 添加旋律
        if melody:
            notes = []
            for note in melody:
                notes.append({
                    "pitch": note.pitch,
                    "start_time": note.start_time,
                    "duration": note.duration,
                    "velocity": note.velocity
                })
            
            # 基於風格選擇樂器
            program = 0  # 默認鋼琴
            if params.genre:
                if params.genre == "jazz":
                    program = 56  # 小號
                elif params.genre == "rock":
                    program = 29  # 電吉他
                elif params.genre == "classical":
                    program = 40  # 小提琴
                elif params.genre == "electronic":
                    program = 80  # 合成器鉛聲
            
            midi_data["instruments"]["melody"] = {
                "program": program,
                "notes": notes
            }
        
        # 添加和弦
        if "chords" in accompaniment and accompaniment["chords"]:
            notes = []
            for note in accompaniment["chords"]:
                notes.append({
                    "pitch": note.pitch,
                    "start_time": note.start_time,
                    "duration": note.duration,
                    "velocity": note.velocity
                })
            
            # 選擇合適的伴奏樂器
            program = 0  # 默認鋼琴
            if params.genre:
                if params.genre == "jazz":
                    program = 0  # 鋼琴
                elif params.genre == "rock":
                    program = 30  # 失真吉他
                elif params.genre == "classical":
                    program = 48  # 弦樂合奏
                elif params.genre == "electronic":
                    program = 81  # 合成器墊聲
            
            midi_data["instruments"]["chords"] = {
                "program": program,
                "notes": notes
            }
        
        # 添加低音
        if "bass" in accompaniment and accompaniment["bass"]:
            notes = []
            for note in accompaniment["bass"]:
                notes.append({
                    "pitch": note.pitch,
                    "start_time": note.start_time,
                    "duration": note.duration,
                    "velocity": note.velocity
                })
            
            # 選擇合適的低音樂器
            program = 32  # 默認原聲貝斯
            if params.genre:
                if params.genre == "jazz":
                    program = 32  # 原聲貝斯
                elif params.genre == "rock":
                    program = 33  # 電貝斯
                elif params.genre == "classical":
                    program = 43  # 大提琴
                elif params.genre == "electronic":
                    program = 38  # 合成貝斯
            
            midi_data["instruments"]["bass"] = {
                "program": program,
                "notes": notes
            }
        
        return midi_data


class ImprovisationWorkflow(Workflow):
    """即興創作工作流程"""
    
    def execute(self, command: MCPCommand, context: Dict[str, Any]) -> Dict[str, Any]:
        """執行即興創作工作流程
        
        Args:
            command: MCP指令對象
            context: 工作流程執行上下文
            
        Returns:
            Dict[str, Any]: 即興創作的音樂數據
        """
        command_id = context.get("command_id", "unknown")
        model_interface = context.get("model_interface")
        logger_service = context.get("logger_service")
        
        if command.command_type != CommandType.IMPROVISATION:
            raise ValueError(f"不適用的指令類型 {command.command_type}，應為 {CommandType.IMPROVISATION}")
        
        self.logger.info(f"執行即興創作工作流程，指令ID: {command_id}")
        
        # 獲取參數或使用默認值
        params = command.parameters or MusicParameters()
        
        # 如果有文本描述，解析它以增強參數
        if command.text_input:
            if logger_service:
                logger_service.log_workflow_step(
                    command_id,
                    "text_analysis",
                    "started",
                    {"text_input": command.text_input}
                )
            
            params = self._analyze_text_input(command.text_input, params)
            
            if logger_service:
                logger_service.log_workflow_step(
                    command_id,
                    "text_analysis",
                    "completed",
                    {"parameters": params.model_dump()}
                )
        
        # 獲取旋律輸入（如果有）作為引導旋律
        primer_melody = None
        if command.melody_input and command.melody_input.notes:
            primer_melody = command.melody_input.notes
        
        # 使用主模型生成即興旋律
        try:
            if logger_service:
                logger_service.log_workflow_step(
                    command_id,
                    "improvisation_generation",
                    "started"
                )
            
            # 生成旋律
            melody = model_interface.generate_melody(params, primer_melody)
            
            if logger_service:
                logger_service.log_workflow_step(
                    command_id,
                    "improvisation_generation",
                    "completed",
                    {"melody_length": len(melody)}
                )
        except Exception as e:
            error_msg = f"即興創作失敗: {str(e)}"
            self.logger.error(error_msg)
            if logger_service:
                logger_service.log_workflow_step(
                    command_id,
                    "improvisation_generation",
                    "failed",
                    {"error": error_msg}
                )
            raise
        
        # 生成伴奏（可選）
        accompaniment = {"chords": [], "bass": []}
        models_used = [model_interface.model_type]
        
        if params.genre and params.genre != "solo":  # 如果不是獨奏風格
            try:
                if logger_service:
                    logger_service.log_workflow_step(
                        command_id,
                        "accompaniment_generation",
                        "started"
                    )
                
                # 生成伴奏
                accompaniment = model_interface.generate_accompaniment(melody, params)
                
                if logger_service:
                    logger_service.log_workflow_step(
                        command_id,
                        "accompaniment_generation",
                        "completed"
                    )
            except Exception as e:
                self.logger.warning(f"伴奏生成失敗: {str(e)}")
                if logger_service:
                    logger_service.log_workflow_step(
                        command_id,
                        "accompaniment_generation",
                        "failed",
                        {"error": str(e)}
                    )
                # 繼續執行，使用空伴奏
        
        # 組合音樂數據
        midi_data = self._create_midi_data(melody, accompaniment, params)
        
        # 嘗試使用Music21分析結果
        analysis = None
        try:
            # 尋找 Music21 接口進行分析
            music21_interface = None
            for interface in context.get("additional_models", []):
                if interface.model_type == ModelType.MUSIC21:
                    music21_interface = interface
                    break
            
            if music21_interface:
                analysis = music21_interface.analyze_melody(melody)
                models_used.append(music21_interface.model_type)
        except Exception as e:
            self.logger.warning(f"旋律分析失敗: {str(e)}")
            # 繼續執行，不因分析失敗而中斷整個工作流程
        
        # 返回結果
        result = {
            "music_data": {
                "midi_data": json.dumps(midi_data),
                "audio_data": "data:audio/mpeg;base64,SGVsbG8gV29ybGQh",  # 示例base64音頻數據
                "tracks": {
                    "melody": melody,
                    "chords": accompaniment.get("chords", []),
                    "bass": accompaniment.get("bass", [])
                }
            },
            "analysis": analysis,
            "models_used": models_used,
            "suggestions": self._generate_suggestions(command.text_input, params)
        }
        
        self.logger.info(f"即興創作工作流程完成，指令ID: {command_id}")
        return result
    
    def _analyze_text_input(self, text_input: str, params: MusicParameters) -> MusicParameters:
        """分析文本輸入，提取音樂參數
        
        Args:
            text_input: 輸入文字
            params: 初始音樂參數
            
        Returns:
            MusicParameters: 擴充後的音樂參數
        """
        # 如果已經有充分的參數，則不再分析
        if params.key and params.tempo and params.genre and params.emotion:
            return params
        
        # 簡單的關鍵詞分析
        param_updates = {}
        
        # 提取情感
        if not params.emotion:
            if any(keyword in text_input.lower() for keyword in ["快樂", "歡快", "歡喜", "開心"]):
                param_updates["emotion"] = "happy"
            elif any(keyword in text_input.lower() for keyword in ["悲傷", "憂鬱", "傷心", "哀傷"]):
                param_updates["emotion"] = "sad"
            elif any(keyword in text_input.lower() for keyword in ["平靜", "安寧", "寧靜", "放鬆"]):
                param_updates["emotion"] = "calm"
            elif any(keyword in text_input.lower() for keyword in ["神秘", "奇幻", "玄幻"]):
                param_updates["emotion"] = "mysterious"
            elif any(keyword in text_input.lower() for keyword in ["浪漫", "溫馨", "甜蜜"]):
                param_updates["emotion"] = "romantic"
        
        # 提取風格
        if not params.genre:
            if any(keyword in text_input.lower() for keyword in ["獨奏", "solo", "單獨"]):
                param_updates["genre"] = "solo"
            elif any(keyword in text_input.lower() for keyword in ["爵士", "藍調", "自由"]):
                param_updates["genre"] = "jazz"
            elif any(keyword in text_input.lower() for keyword in ["古典", "巴洛克", "奏鳴"]):
                param_updates["genre"] = "classical"
            elif any(keyword in text_input.lower() for keyword in ["搖滾", "硬式", "龐克"]):
                param_updates["genre"] = "rock"
            elif any(keyword in text_input.lower() for keyword in ["拉丁", "弗拉明戈", "桑巴"]):
                param_updates["genre"] = "latin"
        
        # 提取速度
        if not params.tempo:
            if any(keyword in text_input.lower() for keyword in ["快速", "急促", "迅速"]):
                param_updates["tempo"] = 140
            elif any(keyword in text_input.lower() for keyword in ["中速", "適中"]):
                param_updates["tempo"] = 100
            elif any(keyword in text_input.lower() for keyword in ["慢速", "緩慢", "舒緩"]):
                param_updates["tempo"] = 70
        
        # 更新參數
        if param_updates:
            params.update(param_updates)
        
        # 設置默認值
        if not params.tempo:
            params.tempo = 100
        if not params.key:
            params.key = "C"
        if not params.genre:
            params.genre = "jazz"  # 即興創作默認使用爵士風格
        
        return params
    
    def _create_midi_data(self, melody: List[Any], accompaniment: Dict[str, List[Any]], params: MusicParameters) -> Dict[str, Any]:
        """創建MIDI數據
        
        Args:
            melody: 旋律音符列表
            accompaniment: 伴奏音符字典
            params: 音樂參數
            
        Returns:
            Dict[str, Any]: MIDI數據
        """
        midi_data = {
            "tempo": params.tempo or 120,
            "key": str(params.key) if params.key else "C",
            "time_signature": str(params.time_signature) if params.time_signature else "4/4",
            "instruments": {}
        }
        
        # 選擇合適的即興演奏樂器
        program = 0  # 默認鋼琴
        if params.genre:
            if params.genre == "jazz":
                program = 66  # 薩克斯風
            elif params.genre == "rock":
                program = 29  # 電吉他
            elif params.genre == "classical":
                program = 73  # 長笛
            elif params.genre == "latin":
                program = 24  # 尼龍弦吉他
        
        # 添加旋律
        if melody:
            notes = []
            for note in melody:
                notes.append({
                    "pitch": note.pitch,
                    "start_time": note.start_time,
                    "duration": note.duration,
                    "velocity": note.velocity
                })
            
            midi_data["instruments"]["melody"] = {
                "program": program,
                "notes": notes
            }
        
        # 添加和弦
        if "chords" in accompaniment and accompaniment["chords"]:
            notes = []
            for note in accompaniment["chords"]:
                notes.append({
                    "pitch": note.pitch,
                    "start_time": note.start_time,
                    "duration": note.duration,
                    "velocity": note.velocity
                })
            
            midi_data["instruments"]["chords"] = {
                "program": 0,  # 鋼琴
                "notes": notes
            }
        
        # 添加低音
        if "bass" in accompaniment and accompaniment["bass"]:
            notes = []
            for note in accompaniment["bass"]:
                notes.append({
                    "pitch": note.pitch,
                    "start_time": note.start_time,
                    "duration": note.duration,
                    "velocity": note.velocity
                })
            
            midi_data["instruments"]["bass"] = {
                "program": 32,  # 原聲貝斯
                "notes": notes
            }
        
        return midi_data
    
    def _generate_suggestions(self, text_input: str, params: MusicParameters) -> List[str]:
        """生成音樂建議
        
        Args:
            text_input: 輸入文字
            params: 音樂參數
            
        Returns:
            List[str]: 建議列表
        """
        suggestions = []
        
        # 基於風格提供建議
        if params.genre == "jazz":
            suggestions.append("即興創作中嘗試加入更多的半音變化和藍調音階")
            suggestions.append("考慮使用更複雜的和聲進行，如ii-V-I進行")
        elif params.genre == "classical":
            suggestions.append("嘗試加入裝飾音和華彩段落以增強古典風格")
            suggestions.append("可以考慮使用對位技巧豐富音樂織體")
        elif params.genre == "rock":
            suggestions.append("可以加入更多的反覆動機和力度對比")
            suggestions.append("嘗試使用五度和弦進行增強搖滾風格")
        
        # 添加通用建議
        suggestions.append("在即興創作中，可以嘗試更自由的節奏表達")
        suggestions.append("多聽專業音樂家的即興演奏，學習他們的表達方式")
        
        return suggestions 