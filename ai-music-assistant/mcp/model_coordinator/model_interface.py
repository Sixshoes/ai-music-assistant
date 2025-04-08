"""模型介面適配器

為不同模型提供統一的調用介面，實現模型的無縫整合
"""

import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple, Union

from ..mcp_schema import ModelType, MusicParameters, Note, MelodyInput, CommandType

# 模型服務導入
try:
    from ...backend.music_generation.magenta_service import MagentaService
except ImportError:
    MagentaService = None

try:
    from ...backend.music_theory.music21_service import Music21Service
except ImportError:
    Music21Service = None

try:
    from ...backend.audio_processing.basic_pitch_service import BasicPitchService
except ImportError:
    BasicPitchService = None

from .logging_service import LoggingService

logger = logging.getLogger(__name__)


class ModelInterface(ABC):
    """模型介面抽象基類"""
    
    @abstractmethod
    def generate_melody(self, params: MusicParameters, primer_melody: Optional[List[Note]] = None) -> List[Note]:
        """生成旋律"""
        pass
    
    @abstractmethod
    def generate_accompaniment(self, melody: List[Note], params: MusicParameters) -> Dict[str, List[Note]]:
        """生成伴奏"""
        pass
    
    @abstractmethod
    def analyze_melody(self, melody: List[Note]) -> Dict[str, Any]:
        """分析旋律"""
        pass
    
    @abstractmethod
    def audio_to_melody(self, audio_data: str) -> MelodyInput:
        """將音訊轉換為旋律"""
        pass
    
    @abstractmethod
    def correct_pitch(self, audio_data: str) -> str:
        """校正音高"""
        pass


class MagentaInterface(ModelInterface):
    """Magenta模型接口"""
    
    def __init__(self, logger_service: LoggingService = None):
        self.model_type = ModelType.MAGENTA
        self.logger_service = logger_service
        
        if MagentaService is None:
            raise ImportError("無法導入MagentaService，請確保已安裝所需依賴")
        
        self.service = MagentaService()
        logger.info("Magenta介面初始化完成")
    
    def generate_melody(self, params: MusicParameters, primer_melody: Optional[List[Note]] = None) -> List[Note]:
        """使用Magenta生成旋律
        
        Args:
            params: 音樂參數
            primer_melody: 引導旋律（可選）
            
        Returns:
            List[Note]: 生成的旋律
        """
        start_time = time.time()
        
        try:
            melody = self.service.generate_melody(
                parameters=params,
                primer_melody=primer_melody,
                num_steps=128,
                temperature=0.8
            )
            
            exec_time = time.time() - start_time
            if self.logger_service:
                self.logger_service.log_model_call(
                    self.model_type,
                    "generate_melody",
                    {"primer_length": len(primer_melody) if primer_melody else 0},
                    exec_time
                )
            
            return melody
        except Exception as e:
            logger.error(f"Magenta生成旋律失敗: {str(e)}")
            raise
    
    def generate_accompaniment(self, melody: List[Note], params: MusicParameters) -> Dict[str, List[Note]]:
        """使用Magenta生成伴奏
        
        Args:
            melody: 旋律音符
            params: 音樂參數
            
        Returns:
            Dict[str, List[Note]]: 各聲部伴奏
        """
        start_time = time.time()
        
        try:
            accompaniment = self.service.generate_accompaniment(
                melody=melody,
                parameters=params
            )
            
            exec_time = time.time() - start_time
            if self.logger_service:
                self.logger_service.log_model_call(
                    self.model_type,
                    "generate_accompaniment",
                    {"melody_length": len(melody)},
                    exec_time
                )
            
            return accompaniment
        except Exception as e:
            logger.error(f"Magenta生成伴奏失敗: {str(e)}")
            raise
    
    def analyze_melody(self, melody: List[Note]) -> Dict[str, Any]:
        """分析旋律（不是Magenta的主要功能，調用Music21實現）
        
        Args:
            melody: 旋律音符
            
        Returns:
            Dict[str, Any]: 分析結果
        """
        logger.warning("Magenta不擅長旋律分析，建議使用Music21")
        
        # 簡單分析
        if not melody:
            return {"error": "空旋律"}
        
        return {
            "note_count": len(melody),
            "duration": max([n.start_time + n.duration for n in melody]) if melody else 0
        }
    
    def audio_to_melody(self, audio_data: str) -> MelodyInput:
        """將音訊轉換為旋律（Magenta不直接支持）
        
        Args:
            audio_data: 音訊數據
            
        Returns:
            MelodyInput: 提取的旋律
        """
        logger.error("Magenta不支持音訊到旋律轉換，請使用BasicPitch")
        raise NotImplementedError("Magenta不支持音訊到旋律轉換")
    
    def correct_pitch(self, audio_data: str) -> str:
        """校正音高（Magenta不直接支持）
        
        Args:
            audio_data: 音訊數據
            
        Returns:
            str: 校正後的音訊數據
        """
        logger.error("Magenta不支持音高校正，請使用BasicPitch")
        raise NotImplementedError("Magenta不支持音高校正")


class Music21Interface(ModelInterface):
    """Music21模型接口"""
    
    def __init__(self, logger_service: LoggingService = None):
        self.model_type = ModelType.MUSIC21
        self.logger_service = logger_service
        
        if Music21Service is None:
            raise ImportError("無法導入Music21Service，請確保已安裝所需依賴")
        
        self.service = Music21Service()
        logger.info("Music21介面初始化完成")
    
    def generate_melody(self, params: MusicParameters, primer_melody: Optional[List[Note]] = None) -> List[Note]:
        """使用Music21生成旋律（不是Music21的主要功能）
        
        Args:
            params: 音樂參數
            primer_melody: 引導旋律（可選）
            
        Returns:
            List[Note]: 生成的旋律
        """
        logger.warning("Music21不擅長旋律生成，建議使用Magenta")
        
        # 這只是個簡單模擬，實際上Music21不專長於旋律生成
        import random
        
        notes = []
        key = params.key.value if params.key else "C"
        
        # 簡單的音符映射
        pitch_map = {
            "C": [60, 62, 64, 65, 67, 69, 71, 72],  # C大調音階
            "Am": [57, 59, 60, 62, 64, 65, 67, 69]  # A小調音階
        }
        
        pitches = pitch_map.get(key, pitch_map["C"])
        duration = 0.25  # 四分音符
        
        # 生成16個音符的簡單旋律
        for i in range(16):
            pitch = random.choice(pitches)
            note = Note(
                pitch=pitch,
                start_time=i * duration,
                duration=duration,
                velocity=64 + random.randint(-10, 10)
            )
            notes.append(note)
        
        if self.logger_service:
            self.logger_service.log_model_call(
                self.model_type,
                "generate_melody",
                {"key": key},
                0.1  # 模擬執行時間
            )
        
        return notes
    
    def generate_accompaniment(self, melody: List[Note], params: MusicParameters) -> Dict[str, List[Note]]:
        """使用Music21生成伴奏（有限的功能）
        
        Args:
            melody: 旋律音符
            params: 音樂參數
            
        Returns:
            Dict[str, List[Note]]: 各聲部伴奏
        """
        start_time = time.time()
        
        try:
            # 首先分析旋律以獲取和弦進行
            analysis = self.analyze_melody(melody)
            
            # 生成簡單伴奏
            chords = []
            chord_notes = []
            
            if "chord_progression" in analysis and analysis["chord_progression"].chords:
                chord_progression = analysis["chord_progression"]
                
                # 簡單的和弦音符映射
                chord_map = {
                    "C": [60, 64, 67],  # C大三和弦
                    "Dm": [62, 65, 69],  # D小三和弦
                    "Em": [64, 67, 71],  # E小三和弦
                    "F": [65, 69, 72],   # F大三和弦
                    "G": [67, 71, 74],   # G大三和弦
                    "Am": [69, 72, 76],  # A小三和弦
                    # 其他和弦...
                }
                
                # 為每個和弦創建伴奏音符
                current_time = 0.0
                for i, chord_name in enumerate(chord_progression.chords):
                    duration = chord_progression.durations[i] if i < len(chord_progression.durations) else 1.0
                    
                    # 獲取和弦音符
                    chord_pitches = chord_map.get(chord_name, chord_map["C"])
                    
                    # 為每個和弦音創建音符
                    for pitch in chord_pitches:
                        note = Note(
                            pitch=pitch,
                            start_time=current_time,
                            duration=duration,
                            velocity=50  # 較輕的力度
                        )
                        chord_notes.append(note)
                    
                    # 創建低音
                    bass_pitch = chord_pitches[0] - 24  # 降兩個八度
                    bass_note = Note(
                        pitch=bass_pitch,
                        start_time=current_time,
                        duration=duration,
                        velocity=60
                    )
                    chords.append(bass_note)
                    
                    current_time += duration
            
            exec_time = time.time() - start_time
            if self.logger_service:
                self.logger_service.log_model_call(
                    self.model_type,
                    "generate_accompaniment",
                    {"melody_length": len(melody)},
                    exec_time
                )
            
            return {
                "chords": chord_notes,
                "bass": chords
            }
        except Exception as e:
            logger.error(f"Music21生成伴奏失敗: {str(e)}")
            # 返回空伴奏，而不是完全失敗
            return {"chords": [], "bass": []}
    
    def analyze_melody(self, melody: List[Note]) -> Dict[str, Any]:
        """使用Music21分析旋律
        
        Args:
            melody: 旋律音符
            
        Returns:
            Dict[str, Any]: 分析結果
        """
        start_time = time.time()
        
        try:
            # 將音符轉換為MelodyInput格式
            melody_input = MelodyInput(notes=melody)
            
            # 執行分析
            analysis = self.service.analyze_melody(melody)
            
            exec_time = time.time() - start_time
            if self.logger_service:
                self.logger_service.log_model_call(
                    self.model_type,
                    "analyze_melody",
                    {"melody_length": len(melody)},
                    exec_time
                )
            
            # 將分析結果轉換為字典
            return analysis.model_dump()
        except Exception as e:
            logger.error(f"Music21分析旋律失敗: {str(e)}")
            # 返回基本分析結果
            return {
                "key": "C",
                "tempo": 120,
                "time_signature": "4/4",
                "chord_progression": {
                    "chords": ["C", "Am", "F", "G"],
                    "durations": [1.0, 1.0, 1.0, 1.0]
                },
                "structure": {"verse": [1, 4], "chorus": [5, 8]},
                "harmony_issues": [],
                "suggestions": ["無法進行詳細分析，請檢查輸入旋律"]
            }
    
    def audio_to_melody(self, audio_data: str) -> MelodyInput:
        """將音訊轉換為旋律（Music21不直接支持）
        
        Args:
            audio_data: 音訊數據
            
        Returns:
            MelodyInput: 提取的旋律
        """
        logger.error("Music21不支持音訊到旋律轉換，請使用BasicPitch")
        raise NotImplementedError("Music21不支持音訊到旋律轉換")
    
    def correct_pitch(self, audio_data: str) -> str:
        """校正音高（Music21不直接支持）
        
        Args:
            audio_data: 音訊數據
            
        Returns:
            str: 校正後的音訊數據
        """
        logger.error("Music21不支持音高校正，請使用BasicPitch")
        raise NotImplementedError("Music21不支持音高校正")


class BasicPitchInterface(ModelInterface):
    """BasicPitch模型接口"""
    
    def __init__(self, logger_service: LoggingService = None):
        self.model_type = ModelType.BASIC_PITCH
        self.logger_service = logger_service
        
        if BasicPitchService is None:
            raise ImportError("無法導入BasicPitchService，請確保已安裝所需依賴")
        
        self.service = BasicPitchService()
        logger.info("BasicPitch介面初始化完成")
    
    def generate_melody(self, params: MusicParameters, primer_melody: Optional[List[Note]] = None) -> List[Note]:
        """生成旋律（BasicPitch不支持）
        
        Args:
            params: 音樂參數
            primer_melody: 引導旋律（可選）
            
        Returns:
            List[Note]: 生成的旋律
        """
        logger.error("BasicPitch不支持旋律生成，請使用Magenta")
        raise NotImplementedError("BasicPitch不支持旋律生成")
    
    def generate_accompaniment(self, melody: List[Note], params: MusicParameters) -> Dict[str, List[Note]]:
        """生成伴奏（BasicPitch不支持）
        
        Args:
            melody: 旋律音符
            params: 音樂參數
            
        Returns:
            Dict[str, List[Note]]: 各聲部伴奏
        """
        logger.error("BasicPitch不支持伴奏生成，請使用Magenta")
        raise NotImplementedError("BasicPitch不支持伴奏生成")
    
    def analyze_melody(self, melody: List[Note]) -> Dict[str, Any]:
        """分析旋律（BasicPitch有限支持）
        
        Args:
            melody: 旋律音符
            
        Returns:
            Dict[str, Any]: 分析結果
        """
        logger.warning("BasicPitch不擅長旋律分析，建議使用Music21")
        
        # 簡單分析
        if not melody:
            return {"error": "空旋律"}
        
        return {
            "note_count": len(melody),
            "pitch_range": {
                "min": min([n.pitch for n in melody]),
                "max": max([n.pitch for n in melody])
            },
            "duration": max([n.start_time + n.duration for n in melody]) if melody else 0
        }
    
    def audio_to_melody(self, audio_data: str) -> MelodyInput:
        """將音訊轉換為旋律
        
        Args:
            audio_data: 音訊數據
            
        Returns:
            MelodyInput: 提取的旋律
        """
        start_time = time.time()
        
        try:
            # 首先將Base64音訊數據保存為臨時文件
            import tempfile
            import base64
            import os
            
            # 從data URL提取實際的base64數據
            if "base64," in audio_data:
                audio_data = audio_data.split("base64,")[1]
            
            # 解碼並保存為臨時文件
            audio_bytes = base64.b64decode(audio_data)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_path = temp_file.name
                temp_file.write(audio_bytes)
            
            try:
                # 調用BasicPitch服務
                melody_input = self.service.audio_to_melody(temp_path)
                
                exec_time = time.time() - start_time
                if self.logger_service:
                    self.logger_service.log_model_call(
                        self.model_type,
                        "audio_to_melody",
                        {"audio_size": len(audio_data)},
                        exec_time
                    )
                
                return melody_input
            finally:
                # 清理臨時文件
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            logger.error(f"BasicPitch音訊轉旋律失敗: {str(e)}")
            raise
    
    def correct_pitch(self, audio_data: str) -> str:
        """校正音高
        
        Args:
            audio_data: 音訊數據
            
        Returns:
            str: 校正後的音訊數據
        """
        start_time = time.time()
        
        try:
            # 首先將Base64音訊數據保存為臨時文件
            import tempfile
            import base64
            import os
            
            # 從data URL提取實際的base64數據
            if "base64," in audio_data:
                audio_data = audio_data.split("base64,")[1]
            
            # 解碼並保存為臨時文件
            audio_bytes = base64.b64decode(audio_data)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_path = temp_file.name
                temp_file.write(audio_bytes)
            
            try:
                # 調用BasicPitch的音高校正
                corrected_path = self.service.correct_pitch(temp_path)
                
                # 將校正後的音頻讀回為base64
                with open(corrected_path, "rb") as corrected_file:
                    corrected_data = base64.b64encode(corrected_file.read()).decode('utf-8')
                
                exec_time = time.time() - start_time
                if self.logger_service:
                    self.logger_service.log_model_call(
                        self.model_type,
                        "correct_pitch",
                        {"audio_size": len(audio_data)},
                        exec_time
                    )
                
                # 返回data URL格式
                return f"data:audio/wav;base64,{corrected_data}"
            finally:
                # 清理臨時文件
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                if os.path.exists(corrected_path) and corrected_path != temp_path:
                    os.unlink(corrected_path)
                    
        except Exception as e:
            logger.error(f"BasicPitch音高校正失敗: {str(e)}")
            raise


class ModelInterfaceFactory:
    """模型介面工廠類，用於創建對應模型類型的介面"""
    
    @staticmethod
    def create_interface(model_type: ModelType, logger_service: Optional[LoggingService] = None) -> ModelInterface:
        """創建模型介面
        
        Args:
            model_type: 模型類型
            logger_service: 日誌服務
            
        Returns:
            ModelInterface: 對應的模型介面
            
        Raises:
            ValueError: 不支援的模型類型
        """
        if model_type == ModelType.MAGENTA:
            return MagentaInterface(logger_service)
        elif model_type == ModelType.MUSIC21:
            return Music21Interface(logger_service)
        elif model_type == ModelType.BASIC_PITCH:
            return BasicPitchInterface(logger_service)
        elif model_type == ModelType.DDSP:
            return DDSPInterface(logger_service)
        elif model_type == ModelType.MUSENET:
            return MuseNetInterface(logger_service)
        elif model_type == ModelType.RNN_COMPOSER:
            return RNNComposerInterface(logger_service)
        else:
            raise ValueError(f"不支援的模型類型: {model_type}") 