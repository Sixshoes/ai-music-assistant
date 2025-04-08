"""Magenta 模型管理器

負責 Magenta 模型的評估、組合、選擇和參數調優
"""

import os
import logging
import tempfile
import json
from typing import Dict, Any, List, Optional, Tuple, Union
from enum import Enum
from dataclasses import dataclass
import random
import requests

import numpy as np
import tensorflow as tf
from tensorflow.keras.metrics import Mean

# Magenta 模型導入
from magenta.models.melody_rnn import melody_rnn_model
from magenta.models.performance_rnn import performance_model
from magenta.models.music_vae import configs as music_vae_configs
from magenta.models.music_vae.trained_model import TrainedModel as MusicVAEModel
from magenta.models.drums_rnn import drums_rnn_model
from magenta.models.improv_rnn import improv_rnn_model
from magenta.models.polyphony_rnn import polyphony_rnn_model
from magenta.models.pianoroll_rnn_nade import pianoroll_rnn_nade_model

from magenta.music import midi_io
from magenta.music import constants
from magenta.music import sequences_lib
from magenta.music.protobuf import generator_pb2
from magenta.music.protobuf import music_pb2

from ...mcp.mcp_schema import MusicParameters, Note

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Magenta 模型類型"""
    MELODY_RNN = "melody_rnn"
    PERFORMANCE_RNN = "performance_rnn"
    MUSIC_VAE = "music_vae"
    DRUMS_RNN = "drums_rnn"
    IMPROV_RNN = "improv_rnn"
    POLYPHONY_RNN = "polyphony_rnn"
    PIANOROLL_RNN_NADE = "pianoroll_rnn_nade"


@dataclass
class ModelConfiguration:
    """模型配置"""
    model_type: ModelType
    checkpoint_path: str
    config_name: str
    generation_steps: int = 128
    temperature: float = 1.0
    beam_size: int = 1
    branch_factor: int = 1
    
    # 特定於 MusicVAE 的參數
    vae_temperature: float = 0.2
    vae_z_size: int = 512


@dataclass
class EvaluationMetrics:
    """模型評估指標"""
    coherence_score: float = 0.0  # 音樂連貫性評分
    diversity_score: float = 0.0  # 音樂多樣性評分
    complexity_score: float = 0.0  # 音樂複雜度評分
    style_match_score: float = 0.0  # 風格匹配度評分
    harmonic_score: float = 0.0  # 和聲合理性評分
    
    @property
    def total_score(self) -> float:
        """總評分"""
        return (self.coherence_score + self.diversity_score + 
                self.complexity_score + self.style_match_score + 
                self.harmonic_score) / 5.0


class MagentaModelManager:
    """Magenta 模型管理器
    
    負責模型評估、組合、選擇和參數調優
    """
    
    def __init__(self, models_dir: str = "models", llm_api_key: Optional[str] = None, llm_api_url: Optional[str] = None):
        """初始化 Magenta 模型管理器
        
        Args:
            models_dir: 模型存儲目錄
            llm_api_key: 大語言模型 API 密鑰（如有）
            llm_api_url: 大語言模型 API URL（如有）
        """
        self.models_dir = models_dir
        self.loaded_models: Dict[str, Any] = {}
        self.model_configs: Dict[str, ModelConfiguration] = {}
        self.evaluation_results: Dict[str, EvaluationMetrics] = {}
        self.optimal_combinations: List[Dict[str, Any]] = []
        self.llm_api_key = llm_api_key
        self.llm_api_url = llm_api_url
        self.style_cache: Dict[str, Dict[str, Any]] = {}  # 風格參數緩存
        
        # 確保模型目錄存在
        os.makedirs(models_dir, exist_ok=True)
        
        # 初始化 TensorFlow 設置
        self._setup_tensorflow()
        
        logger.info("Magenta 模型管理器初始化完成")
    
    def _setup_tensorflow(self):
        """設置 TensorFlow 環境"""
        # 限制 GPU 記憶體增長
        gpus = tf.config.experimental.list_physical_devices('GPU')
        if gpus:
            try:
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
                logger.info(f"找到 {len(gpus)} 個 GPU 並設置記憶體增長")
            except RuntimeError as e:
                logger.error(f"設置 GPU 記憶體增長失敗: {e}")
    
    def register_model(self, model_id: str, config: ModelConfiguration):
        """註冊模型配置
        
        Args:
            model_id: 模型唯一標識符
            config: 模型配置
        """
        self.model_configs[model_id] = config
        logger.info(f"註冊模型: {model_id}, 類型: {config.model_type.value}")
    
    def load_model(self, model_id: str) -> Any:
        """加載模型
        
        Args:
            model_id: 模型唯一標識符
            
        Returns:
            Any: 加載的模型
        """
        if model_id in self.loaded_models:
            return self.loaded_models[model_id]
        
        if model_id not in self.model_configs:
            raise ValueError(f"無法找到模型配置: {model_id}")
        
        config = self.model_configs[model_id]
        model_type = config.model_type
        
        try:
            if model_type == ModelType.MELODY_RNN:
                model = self._load_melody_rnn(config)
            elif model_type == ModelType.PERFORMANCE_RNN:
                model = self._load_performance_rnn(config)
            elif model_type == ModelType.MUSIC_VAE:
                model = self._load_music_vae(config)
            elif model_type == ModelType.DRUMS_RNN:
                model = self._load_drums_rnn(config)
            elif model_type == ModelType.IMPROV_RNN:
                model = self._load_improv_rnn(config)
            elif model_type == ModelType.POLYPHONY_RNN:
                model = self._load_polyphony_rnn(config)
            elif model_type == ModelType.PIANOROLL_RNN_NADE:
                model = self._load_pianoroll_rnn_nade(config)
            else:
                raise ValueError(f"不支持的模型類型: {model_type}")
            
            self.loaded_models[model_id] = model
            logger.info(f"成功加載模型: {model_id}")
            return model
        
        except Exception as e:
            logger.error(f"加載模型 {model_id} 失敗: {e}")
            raise
    
    def _load_melody_rnn(self, config: ModelConfiguration) -> Any:
        """加載 MelodyRNN 模型
        
        Args:
            config: 模型配置
            
        Returns:
            Any: 加載的模型
        """
        # 模擬加載 MelodyRNN 模型，實際實現請替換為實際代碼
        logger.info(f"加載 MelodyRNN 模型: {config.config_name}")
        # 實際加載代碼在這裡
        return {"type": "melody_rnn", "config": config}
    
    def _load_performance_rnn(self, config: ModelConfiguration) -> Any:
        """加載 PerformanceRNN 模型
        
        Args:
            config: 模型配置
            
        Returns:
            Any: 加載的模型
        """
        logger.info(f"加載 PerformanceRNN 模型: {config.config_name}")
        # 實際加載代碼在這裡
        return {"type": "performance_rnn", "config": config}
    
    def _load_music_vae(self, config: ModelConfiguration) -> Any:
        """加載 MusicVAE 模型
        
        Args:
            config: 模型配置
            
        Returns:
            Any: 加載的模型
        """
        logger.info(f"加載 MusicVAE 模型: {config.config_name}")
        # 實際加載代碼在這裡
        return {"type": "music_vae", "config": config}
    
    def _load_drums_rnn(self, config: ModelConfiguration) -> Any:
        """加載 DrumsRNN 模型
        
        Args:
            config: 模型配置
            
        Returns:
            Any: 加載的模型
        """
        logger.info(f"加載 DrumsRNN 模型: {config.config_name}")
        # 實際加載代碼在這裡
        return {"type": "drums_rnn", "config": config}
    
    def _load_improv_rnn(self, config: ModelConfiguration) -> Any:
        """加載 ImprovRNN 模型
        
        Args:
            config: 模型配置
            
        Returns:
            Any: 加載的模型
        """
        logger.info(f"加載 ImprovRNN 模型: {config.config_name}")
        # 實際加載代碼在這裡
        return {"type": "improv_rnn", "config": config}
    
    def _load_polyphony_rnn(self, config: ModelConfiguration) -> Any:
        """加載 PolyphonyRNN 模型
        
        Args:
            config: 模型配置
            
        Returns:
            Any: 加載的模型
        """
        logger.info(f"加載 PolyphonyRNN 模型: {config.config_name}")
        # 實際加載代碼在這裡
        return {"type": "polyphony_rnn", "config": config}
    
    def _load_pianoroll_rnn_nade(self, config: ModelConfiguration) -> Any:
        """加載 PianorollRNNNADE 模型
        
        Args:
            config: 模型配置
            
        Returns:
            Any: 加載的模型
        """
        logger.info(f"加載 PianorollRNNNADE 模型: {config.config_name}")
        # 實際加載代碼在這裡
        return {"type": "pianoroll_rnn_nade", "config": config}
    
    def evaluate_model(self, model_id: str, test_inputs: List[Any]) -> EvaluationMetrics:
        """評估模型表現
        
        Args:
            model_id: 模型唯一標識符
            test_inputs: 測試輸入
            
        Returns:
            EvaluationMetrics: 評估指標
        """
        model = self.load_model(model_id)
        config = self.model_configs[model_id]
        
        logger.info(f"評估模型: {model_id}")
        
        # 模擬評估過程，實際實現需要替換
        metrics = EvaluationMetrics(
            coherence_score=random.uniform(0.6, 0.9),
            diversity_score=random.uniform(0.5, 0.95),
            complexity_score=random.uniform(0.4, 0.85),
            style_match_score=random.uniform(0.7, 0.95),
            harmonic_score=random.uniform(0.6, 0.9)
        )
        
        self.evaluation_results[model_id] = metrics
        logger.info(f"模型 {model_id} 評估完成，總分: {metrics.total_score:.2f}")
        
        return metrics
    
    def find_optimal_combinations(self, 
                               task_requirements: Dict[str, Any], 
                               num_combinations: int = 3) -> List[Dict[str, Any]]:
        """尋找最佳模型組合
        
        Args:
            task_requirements: 任務需求
            num_combinations: 要返回的最佳組合數量
            
        Returns:
            List[Dict[str, Any]]: 最佳模型組合列表
        """
        logger.info(f"尋找最佳模型組合，任務: {task_requirements}")
        
        # 確保所有模型都已評估
        for model_id in self.model_configs:
            if model_id not in self.evaluation_results:
                self.evaluate_model(model_id, [])  # 空測試集，實際應該使用有意義的測試數據
        
        # 按照任務類型選擇合適的模型
        task_type = task_requirements.get('task_type', 'melody_generation')
        genre = task_requirements.get('genre', 'general')
        
        suitable_models = []
        
        for model_id, metrics in self.evaluation_results.items():
            config = self.model_configs[model_id]
            
            # 根據任務類型篩選模型
            if task_type == 'melody_generation' and config.model_type in [ModelType.MELODY_RNN, ModelType.MUSIC_VAE]:
                suitable_models.append((model_id, metrics))
            elif task_type == 'performance_generation' and config.model_type == ModelType.PERFORMANCE_RNN:
                suitable_models.append((model_id, metrics))
            elif task_type == 'drums_generation' and config.model_type == ModelType.DRUMS_RNN:
                suitable_models.append((model_id, metrics))
            elif task_type == 'accompaniment_generation' and config.model_type in [ModelType.IMPROV_RNN, ModelType.POLYPHONY_RNN]:
                suitable_models.append((model_id, metrics))
            elif task_type == 'full_arrangement' and config.model_type == ModelType.PIANOROLL_RNN_NADE:
                suitable_models.append((model_id, metrics))
        
        # 按照總分排序
        suitable_models.sort(key=lambda x: x[1].total_score, reverse=True)
        
        # 選擇頂部模型
        top_models = suitable_models[:num_combinations]
        
        # 創建組合
        combinations = []
        for model_id, metrics in top_models:
            config = self.model_configs[model_id]
            combinations.append({
                'model_id': model_id,
                'model_type': config.model_type.value,
                'config_name': config.config_name,
                'metrics': {
                    'coherence': metrics.coherence_score,
                    'diversity': metrics.diversity_score,
                    'complexity': metrics.complexity_score,
                    'style_match': metrics.style_match_score,
                    'harmonic': metrics.harmonic_score,
                    'total': metrics.total_score
                },
                'optimal_parameters': self.optimize_parameters(model_id, task_requirements)
            })
        
        self.optimal_combinations = combinations
        logger.info(f"找到 {len(combinations)} 個最佳模型組合")
        
        return combinations
    
    def optimize_parameters(self, model_id: str, task_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """優化模型參數
        
        Args:
            model_id: 模型唯一標識符
            task_requirements: 任務需求
            
        Returns:
            Dict[str, Any]: 優化後的參數
        """
        config = self.model_configs[model_id]
        
        # 根據任務需求和模型類型調整參數
        genre = task_requirements.get('genre', 'general')
        complexity = task_requirements.get('complexity', 'medium')
        
        # 從預定義參數或使用大語言模型生成參數
        if self.llm_api_key and genre.lower() not in ["classical", "jazz", "pop", "electronic", "general"]:
            # 對於未知風格，使用大語言模型生成參數
            genre_params = self.generate_style_params_with_llm(genre, task_requirements)
        else:
            # 使用預定義的風格參數
            genre_params = self.get_predefined_style_params().get(genre.lower(), 
                                                                self.get_predefined_style_params()["general"])
            
        # 選擇風格參數集
        selected_genre_params = genre_params
        
        # 根據複雜度選擇溫度參數
        if complexity == 'high':
            temperature = selected_genre_params["temperature"]["high"]
            note_density = selected_genre_params["note_density"]["high"]
            harmonic_complexity = selected_genre_params["harmonic_complexity"]["high"]
            rhythm_regularity = selected_genre_params["rhythm_regularity"]["high"]
            polyphony_level = selected_genre_params["polyphony_level"]["high"]
        elif complexity == 'low':
            temperature = selected_genre_params["temperature"]["low"]
            note_density = selected_genre_params["note_density"]["low"]
            harmonic_complexity = selected_genre_params["harmonic_complexity"]["low"]
            rhythm_regularity = selected_genre_params["rhythm_regularity"]["low"]
            polyphony_level = selected_genre_params["polyphony_level"]["low"]
        else:  # medium
            temperature = selected_genre_params["temperature"]["medium"]
            note_density = selected_genre_params["note_density"]["medium"]
            harmonic_complexity = selected_genre_params["harmonic_complexity"]["medium"]
            rhythm_regularity = selected_genre_params["rhythm_regularity"]["medium"]
            polyphony_level = selected_genre_params["polyphony_level"]["medium"]
        
        # 基於任務類型調整生成步數
        task_type = task_requirements.get('task_type', 'melody_generation')
        if task_type == 'melody_generation':
            base_steps = 128
        elif task_type == 'performance_generation':
            base_steps = 512
        elif task_type == 'full_arrangement':
            base_steps = 256
        else:
            base_steps = 192
        
        # 應用風格特定的步數乘數
        steps = int(base_steps * selected_genre_params["steps_multiplier"])
        
        # 創建優化後的參數
        optimal_params = {
            'temperature': temperature,
            'generation_steps': steps,
            'beam_size': 1 if temperature > 1.0 else 5,  # 高溫度時降低束搜索寬度
            'note_density': note_density,
            'harmonic_complexity': harmonic_complexity,
            'rhythm_regularity': rhythm_regularity,
            'polyphony_level': polyphony_level,
            'recommended_track_count': selected_genre_params["track_count"]["recommend"],
            'recommended_track_roles': selected_genre_params["track_roles"],
        }
        
        # 模型特定參數
        if config.model_type == ModelType.MUSIC_VAE:
            optimal_params['vae_temperature'] = min(0.5, temperature)
        
        logger.info(f"優化模型 {model_id} 參數: {optimal_params}")
        
        return optimal_params
    
    def get_predefined_style_params(self) -> Dict[str, Dict[str, Any]]:
        """獲取預定義的風格參數
        
        Returns:
            Dict[str, Dict[str, Any]]: 風格參數字典
        """
        # 風格精細參數映射 - 確保不同風格有合適的參數設置
        return {
            "classical": {
                "temperature": {"low": 0.3, "medium": 0.6, "high": 0.9},
                "steps_multiplier": 1.2,  # 更長的生成步數以適應古典音樂的結構
                "note_density": {"low": 0.5, "medium": 0.7, "high": 0.9},
                "harmonic_complexity": {"low": 0.6, "medium": 0.75, "high": 0.9},
                "rhythm_regularity": {"low": 0.8, "medium": 0.7, "high": 0.5},
                "polyphony_level": {"low": 2, "medium": 4, "high": 6},  # 複音程度
                "track_count": {"min": 4, "recommend": 8, "max": 12},  # 音軌數量建議
                "track_roles": ["melody", "counter_melody", "harmony", "bass", "strings", "woodwinds", "brass", "percussion"],
            },
            "jazz": {
                "temperature": {"low": 0.6, "medium": 0.9, "high": 1.2},
                "steps_multiplier": 1.0,
                "note_density": {"low": 0.4, "medium": 0.6, "high": 0.8},
                "harmonic_complexity": {"low": 0.7, "medium": 0.85, "high": 0.95},
                "rhythm_regularity": {"low": 0.5, "medium": 0.4, "high": 0.3},
                "polyphony_level": {"low": 2, "medium": 3, "high": 4},
                "track_count": {"min": 3, "recommend": 5, "max": 7},
                "track_roles": ["piano", "bass", "drums", "saxophone", "trumpet"],
            },
            "pop": {
                "temperature": {"low": 0.4, "medium": 0.7, "high": 0.9},
                "steps_multiplier": 0.9,
                "note_density": {"low": 0.4, "medium": 0.6, "high": 0.8},
                "harmonic_complexity": {"low": 0.5, "medium": 0.6, "high": 0.7},
                "rhythm_regularity": {"low": 0.8, "medium": 0.7, "high": 0.6},
                "polyphony_level": {"low": 1, "medium": 2, "high": 3},
                "track_count": {"min": 3, "recommend": 5, "max": 7},
                "track_roles": ["vocal", "guitar", "bass", "drums", "keyboard"],
            },
            "electronic": {
                "temperature": {"low": 0.5, "medium": 0.8, "high": 1.1},
                "steps_multiplier": 0.8,
                "note_density": {"low": 0.6, "medium": 0.8, "high": 0.9},
                "harmonic_complexity": {"low": 0.4, "medium": 0.5, "high": 0.7},
                "rhythm_regularity": {"low": 0.9, "medium": 0.8, "high": 0.7},
                "polyphony_level": {"low": 1, "medium": 2, "high": 3},
                "track_count": {"min": 3, "recommend": 6, "max": 8},
                "track_roles": ["lead", "bass", "drum", "arpeggio", "pad", "effects"],
            },
            "general": {  # 默認值
                "temperature": {"low": 0.5, "medium": 0.8, "high": 1.0},
                "steps_multiplier": 1.0,
                "note_density": {"low": 0.5, "medium": 0.65, "high": 0.8},
                "harmonic_complexity": {"low": 0.5, "medium": 0.7, "high": 0.8},
                "rhythm_regularity": {"low": 0.7, "medium": 0.6, "high": 0.5},
                "polyphony_level": {"low": 2, "medium": 3, "high": 4},
                "track_count": {"min": 3, "recommend": 4, "max": 6},
                "track_roles": ["melody", "harmony", "bass", "rhythm"],
            }
        }
    
    def generate_style_params_with_llm(self, genre: str, task_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """使用大語言模型生成風格參數
        
        Args:
            genre: 音樂風格
            task_requirements: 任務需求
            
        Returns:
            Dict[str, Any]: 生成的風格參數
        """
        # 檢查緩存
        if genre.lower() in self.style_cache:
            logger.info(f"使用緩存中的風格參數: {genre}")
            return self.style_cache[genre.lower()]
        
        # 構建提示
        prompt = f"""
        我需要為音樂生成系統創建以下風格的參數配置: {genre}
        
        請根據這種音樂風格的特點，生成以下JSON格式的參數配置:
        {{
            "temperature": {{"low": 數值, "medium": 數值, "high": 數值}},
            "steps_multiplier": 數值,
            "note_density": {{"low": 數值, "medium": 數值, "high": 數值}},
            "harmonic_complexity": {{"low": 數值, "medium": 數值, "high": 數值}},
            "rhythm_regularity": {{"low": 數值, "medium": 數值, "high": 數值}},
            "polyphony_level": {{"low": 數值, "medium": 數值, "high": 數值}},
            "track_count": {{"min": 數值, "recommend": 數值, "max": 數值}},
            "track_roles": [適合該風格的樂器或音軌角色列表]
        }}
        
        其中:
        - temperature: 溫度參數影響生成的隨機性 (0.2-1.5之間)
        - steps_multiplier: 生成步數乘數 (0.5-2.0之間)
        - note_density: 音符密度 (0.1-1.0之間)
        - harmonic_complexity: 和聲複雜度 (0.1-1.0之間)
        - rhythm_regularity: 節奏規律性 (0.1-1.0之間)
        - polyphony_level: 複音層次 (1-10之間的整數)
        - track_count: 建議音軌數量
        - track_roles: 適合這種風格的樂器或音軌角色
        
        請僅返回JSON格式，不要有任何其他文字。
        """
            
        try:
            # 判斷使用何種LLM服務
            if self.llm_api_url and "ollama" in self.llm_api_url.lower():
                # 使用Ollama本地模型
                return self._generate_with_ollama(prompt, genre)
            elif self.llm_api_url and "huggingface" in self.llm_api_url.lower():
                # 使用Hugging Face API
                return self._generate_with_huggingface(prompt, genre)
            elif self.llm_api_url and ("localhost:1234" in self.llm_api_url.lower() or "lmstudio" in self.llm_api_url.lower()):
                # 使用LMStudio本地API
                return self._generate_with_lmstudio(prompt, genre)
            elif self.llm_api_key and self.llm_api_url:
                # 使用OpenAI或兼容API
                return self._generate_with_openai_compatible(prompt, genre)
            else:
                logger.warning("未提供大語言模型API資訊，使用一般風格參數")
                return self.get_predefined_style_params()["general"]
                
        except Exception as e:
            logger.error(f"調用大語言模型生成風格參數失敗: {e}")
            return self.get_predefined_style_params()["general"]
            
    def _generate_with_lmstudio(self, prompt: str, genre: str) -> Dict[str, Any]:
        """使用LMStudio本地API生成參數
        
        Args:
            prompt: 提示文本
            genre: 風格名稱
            
        Returns:
            Dict[str, Any]: 生成的參數
        """
        # LMStudio使用與OpenAI兼容的API格式
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": [
                {"role": "system", "content": "你是一個音樂專家助手，擅長為音樂生成系統提供參數配置。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5,
            "max_tokens": 1024,
            "stream": False
        }
        
        try:
            response = requests.post(self.llm_api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # 提取JSON
            import re
            json_match = re.search(r'({[\s\S]*})', content)
            if json_match:
                json_str = json_match.group(1)
                # 嘗試修復可能的JSON格式問題
                try:
                    params = json.loads(json_str)
                except json.JSONDecodeError:
                    fixed_json = self._try_fix_json(json_str)
                    if fixed_json:
                        params = fixed_json
                    else:
                        logger.error(f"無法修復JSON格式: {json_str}")
                        return self.get_predefined_style_params()["general"]
                
                # 緩存結果
                self.style_cache[genre.lower()] = params
                
                # 保存到磁盤以便將來使用
                self._save_style_params_to_disk(genre.lower(), params)
                
                logger.info(f"成功使用LMStudio生成風格參數: {genre}")
                return params
            else:
                logger.error(f"無法從LMStudio回應中提取JSON: {content}")
                return self.get_predefined_style_params()["general"]
                
        except Exception as e:
            logger.error(f"調用LMStudio生成風格參數失敗: {e}")
            return self.get_predefined_style_params()["general"]
    
    def _generate_with_openai_compatible(self, prompt: str, genre: str) -> Dict[str, Any]:
        """使用OpenAI兼容API生成參數
        
        Args:
            prompt: 提示文本
            genre: 風格名稱
            
        Returns:
            Dict[str, Any]: 生成的參數
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.llm_api_key}"
        }
        
        payload = {
            "model": "gpt-4" if "openai" in self.llm_api_url.lower() else "default", 
            "messages": [
                {"role": "system", "content": "你是一個音樂專家助手，擅長為音樂生成系統提供參數配置。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5
        }
        
        response = requests.post(self.llm_api_url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # 提取JSON
        import re
        json_match = re.search(r'({[\s\S]*})', content)
        if json_match:
            json_str = json_match.group(1)
            params = json.loads(json_str)
            
            # 緩存結果
            self.style_cache[genre.lower()] = params
            
            # 保存到磁盤以便將來使用
            self._save_style_params_to_disk(genre.lower(), params)
            
            logger.info(f"成功使用OpenAI兼容API生成風格參數: {genre}")
            return params
        else:
            logger.error(f"無法從API回應中提取JSON: {content}")
            return self.get_predefined_style_params()["general"]
    
    def _generate_with_ollama(self, prompt: str, genre: str) -> Dict[str, Any]:
        """使用Ollama本地模型生成參數
        
        Args:
            prompt: 提示文本
            genre: 風格名稱
            
        Returns:
            Dict[str, Any]: 生成的參數
        """
        # Ollama API格式
        ollama_url = self.llm_api_url
        model_name = os.environ.get("OLLAMA_MODEL", "llama3") # 預設使用llama3
        
        payload = {
            "model": model_name,
            "prompt": f"你是一個音樂專家助手，擅長為音樂生成系統提供參數配置。\n\n{prompt}",
            "stream": False,
            "options": {
                "temperature": 0.5,
                "num_predict": 1024
            }
        }
        
        try:
            response = requests.post(ollama_url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            content = result.get("response", "")
            
            # 提取JSON
            import re
            json_match = re.search(r'({[\s\S]*})', content)
            if json_match:
                json_str = json_match.group(1)
                params = json.loads(json_str)
                
                # 緩存結果
                self.style_cache[genre.lower()] = params
                
                # 保存到磁盤以便將來使用
                self._save_style_params_to_disk(genre.lower(), params)
                
                logger.info(f"成功使用Ollama生成風格參數: {genre}")
                return params
            else:
                logger.error(f"無法從Ollama回應中提取JSON: {content}")
                return self.get_predefined_style_params()["general"]
                
        except Exception as e:
            logger.error(f"調用Ollama生成風格參數失敗: {e}")
            return self.get_predefined_style_params()["general"]
    
    def _generate_with_huggingface(self, prompt: str, genre: str) -> Dict[str, Any]:
        """使用Hugging Face API生成參數
        
        Args:
            prompt: 提示文本
            genre: 風格名稱
            
        Returns:
            Dict[str, Any]: 生成的參數
        """
        headers = {
            "Authorization": f"Bearer {self.llm_api_key}",
            "Content-Type": "application/json"
        }
        
        # Hugging Face API的格式，針對不同模型可能需要調整
        payload = {
            "inputs": f"你是一個音樂專家助手，擅長為音樂生成系統提供參數配置。\n\n{prompt}",
            "parameters": {
                "max_new_tokens": 1024,
                "temperature": 0.5,
                "return_full_text": False
            }
        }
        
        try:
            response = requests.post(self.llm_api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            # HF API返回格式通常是列表
            result = response.json()
            content = ""
            
            # 根據不同HF模型的返回格式調整，這裡給出兩種情況的解析
            if isinstance(result, list) and len(result) > 0:
                content = result[0].get('generated_text', '')
            elif isinstance(result, dict):
                content = result.get('generated_text', '')
            
            # 提取JSON
            import re
            json_match = re.search(r'({[\s\S]*})', content)
            if json_match:
                json_str = json_match.group(1)
                # 嘗試修復可能的JSON格式問題
                json_str = json_str.replace("'", '"')  # 單引號替換為雙引號
                
                try:
                    params = json.loads(json_str)
                except json.JSONDecodeError:
                    # 如果解析失敗，嘗試更寬鬆的修復
                    fixed_json = self._try_fix_json(json_str)
                    if fixed_json:
                        params = fixed_json
                    else:
                        logger.error(f"無法修復JSON格式: {json_str}")
                        return self.get_predefined_style_params()["general"]
                
                # 緩存結果
                self.style_cache[genre.lower()] = params
                
                # 保存到磁盤以便將來使用
                self._save_style_params_to_disk(genre.lower(), params)
                
                logger.info(f"成功使用Hugging Face API生成風格參數: {genre}")
                return params
            else:
                logger.error(f"無法從Hugging Face回應中提取JSON: {content}")
                return self.get_predefined_style_params()["general"]
                
        except Exception as e:
            logger.error(f"調用Hugging Face API生成風格參數失敗: {e}")
            return self.get_predefined_style_params()["general"]
    
    def _try_fix_json(self, json_str: str) -> Optional[Dict[str, Any]]:
        """嘗試修復損壞的JSON字符串
        
        Args:
            json_str: 可能損壞的JSON字符串
            
        Returns:
            Optional[Dict[str, Any]]: 修復後的JSON對象，修復失敗則返回None
        """
        try:
            # 嘗試直接加載
            return json.loads(json_str)
        except json.JSONDecodeError:
            try:
                # 嘗試替換常見錯誤
                fixed = json_str.replace("'", '"')
                fixed = re.sub(r'([{,]\s*)(\w+)(\s*:)', r'\1"\2"\3', fixed)  # 為缺少引號的鍵添加引號
                fixed = re.sub(r',(\s*[}\]])', r'\1', fixed)  # 移除尾隨逗號
                
                return json.loads(fixed)
            except json.JSONDecodeError:
                # 如果仍然失敗，返回None
                return None
    
    def _save_style_params_to_disk(self, genre: str, params: Dict[str, Any]):
        """將風格參數保存到磁盤
        
        Args:
            genre: 風格名稱
            params: 風格參數
        """
        try:
            styles_dir = os.path.join(self.models_dir, "style_params")
            os.makedirs(styles_dir, exist_ok=True)
            
            file_path = os.path.join(styles_dir, f"{genre.lower()}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(params, f, indent=2, ensure_ascii=False)
                
            logger.info(f"風格參數已保存至: {file_path}")
        except Exception as e:
            logger.error(f"保存風格參數失敗: {e}")
    
    def load_style_params_from_disk(self):
        """從磁盤加載所有保存的風格參數"""
        try:
            styles_dir = os.path.join(self.models_dir, "style_params")
            if not os.path.exists(styles_dir):
                logger.info("風格參數目錄不存在，跳過加載")
                return
                
            for file_name in os.listdir(styles_dir):
                if file_name.endswith('.json'):
                    genre = file_name[:-5]  # 移除 .json 後綴
                    file_path = os.path.join(styles_dir, file_name)
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        params = json.load(f)
                        
                    self.style_cache[genre.lower()] = params
                    logger.info(f"已加載風格參數: {genre}")
            
            logger.info(f"成功加載 {len(self.style_cache)} 個風格參數")
        except Exception as e:
            logger.error(f"加載風格參數失敗: {e}")
    
    def save_evaluation_results(self, output_path: str = "evaluation_results.json"):
        """保存評估結果
        
        Args:
            output_path: 輸出文件路徑
        """
        results = {
            'model_evaluation': {model_id: self._metrics_to_dict(metrics) 
                               for model_id, metrics in self.evaluation_results.items()},
            'optimal_combinations': self.optimal_combinations
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"評估結果已保存至: {output_path}")
    
    def _metrics_to_dict(self, metrics: EvaluationMetrics) -> Dict[str, float]:
        """將評估指標轉換為字典
        
        Args:
            metrics: 評估指標
            
        Returns:
            Dict[str, float]: 指標字典
        """
        return {
            'coherence': metrics.coherence_score,
            'diversity': metrics.diversity_score,
            'complexity': metrics.complexity_score,
            'style_match': metrics.style_match_score,
            'harmonic': metrics.harmonic_score,
            'total': metrics.total_score
        }

    def get_style_parameters(self, genre: str, task_requirements: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """獲取特定風格的參數
        
        方便直接測試風格參數生成功能
        
        Args:
            genre: 音樂風格
            task_requirements: 任務需求（可選）
            
        Returns:
            Dict[str, Any]: 風格參數
        """
        if not task_requirements:
            task_requirements = {'complexity': 'medium'}
            
        if self.llm_api_key and genre.lower() not in self.get_predefined_style_params():
            return self.generate_style_params_with_llm(genre, task_requirements)
        else:
            return self.get_predefined_style_params().get(genre.lower(), 
                                                       self.get_predefined_style_params()["general"])


# 示例用法
if __name__ == "__main__":
    # 配置日誌
    logging.basicConfig(level=logging.INFO)
    
    # 從環境變量或配置文件獲取LLM服務設置
    llm_service = os.environ.get("LLM_SERVICE", "ollama").lower()
    
    # 根據所選服務設置參數
    if llm_service == "openai":
        # 使用OpenAI API (付費)
        llm_api_key = os.environ.get("OPENAI_API_KEY", None)
        llm_api_url = "https://api.openai.com/v1/chat/completions"
        
    elif llm_service == "huggingface" or llm_service == "hf":
        # 使用Hugging Face免費API (有限額度)
        llm_api_key = os.environ.get("HF_API_KEY", None)
        llm_api_url = os.environ.get("HF_API_URL", 
                     "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2")
        
    elif llm_service == "lmstudio":
        # 使用LMStudio本地模型 (免費)
        llm_api_key = None  # LMStudio本地API不需要API密鑰
        llm_api_url = os.environ.get("LMSTUDIO_API_URL", "http://localhost:1234/v1/chat/completions")
        
    else:  # 預設使用Ollama
        # 使用Ollama本地模型 (免費)
        llm_api_key = None  # Ollama不需要API密鑰
        llm_api_url = os.environ.get("OLLAMA_API_URL", "http://localhost:11434/api/generate")
        os.environ["OLLAMA_MODEL"] = os.environ.get("OLLAMA_MODEL", "llama3")  # 設置Ollama模型名稱
    
    # 創建模型管理器
    manager = MagentaModelManager(
        models_dir="models",
        llm_api_key=llm_api_key,
        llm_api_url=llm_api_url
    )
    
    # 嘗試從磁盤加載已保存的風格參數
    manager.load_style_params_from_disk()
    
    # 單獨測試風格參數生成功能
    test_style = os.environ.get("TEST_STYLE", "電子搖滾")
    print(f"嘗試獲取 '{test_style}' 風格參數：")
    
    try:
        style_params = manager.get_style_parameters(test_style)
        print(json.dumps(style_params, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"獲取風格參數失敗: {e}")
    
    # 註冊模型（示例配置）
    manager.register_model(
        "melody_rnn_basic",
        ModelConfiguration(
            model_type=ModelType.MELODY_RNN,
            checkpoint_path="models/melody_rnn/basic_rnn.mag",
            config_name="basic_rnn"
        )
    )
    
    manager.register_model(
        "melody_rnn_attention",
        ModelConfiguration(
            model_type=ModelType.MELODY_RNN,
            checkpoint_path="models/melody_rnn/attention_rnn.mag",
            config_name="attention_rnn"
        )
    )
    
    manager.register_model(
        "performance_rnn_base",
        ModelConfiguration(
            model_type=ModelType.PERFORMANCE_RNN,
            checkpoint_path="models/performance_rnn/performance.mag",
            config_name="performance"
        )
    )
    
    manager.register_model(
        "music_vae_mel16",
        ModelConfiguration(
            model_type=ModelType.MUSIC_VAE,
            checkpoint_path="models/music_vae/mel_16bar_small.mag",
            config_name="mel_16bar_small"
        )
    )
    
    # 評估模型
    for model_id in manager.model_configs:
        manager.evaluate_model(model_id, [])
    
    # 嘗試使用自訂風格生成參數
    task_req = {
        'task_type': 'melody_generation',
        'genre': test_style,  # 使用環境變量指定的風格
        'complexity': 'high'
    }
    
    # 尋找最佳組合
    optimal_combos = manager.find_optimal_combinations(task_req)
    print(f"\n最佳模型組合：")
    print(json.dumps(optimal_combos, indent=2, ensure_ascii=False))
    
    # 保存評估結果
    manager.save_evaluation_results() 