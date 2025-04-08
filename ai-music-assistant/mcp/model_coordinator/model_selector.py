"""模型選擇器

實現智能模型選擇與切換邏輯，為不同的任務選擇最合適的模型
"""

from typing import Dict, List, Any, Optional, Set, Tuple
import logging
import json
import os
from datetime import datetime
from collections import defaultdict

from ..mcp_schema import (
    MCPCommand, 
    ModelType, 
    CommandType,
    MusicParameters
)

logger = logging.getLogger(__name__)


class ModelSelector:
    """模型選擇器類別
    
    實現智能模型選擇與切換邏輯
    """
    
    def __init__(self, performance_history_path: str = None):
        """初始化模型選擇器
        
        Args:
            performance_history_path: 模型性能歷史記錄檔案路徑
        """
        # 設定性能歷史記錄檔案路徑
        self.performance_history_path = performance_history_path or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "model_performance_history.json"
        )
        
        # 模型能力映射
        self.model_capabilities = {
            ModelType.MAGENTA: {
                "capabilities": [
                    "melody_generation",
                    "accompaniment_generation",
                    "drum_pattern_generation",
                    "arrangement",
                    "style_transfer",
                    "neural_loops"
                ],
                "preferred_for": [
                    CommandType.TEXT_TO_MUSIC,
                    CommandType.MELODY_TO_ARRANGEMENT,
                    CommandType.IMPROVISATION,
                    CommandType.STYLE_TRANSFER
                ],
                "strength_score": {
                    CommandType.TEXT_TO_MUSIC: 0.85,
                    CommandType.MELODY_TO_ARRANGEMENT: 0.9,
                    CommandType.IMPROVISATION: 0.8,
                    CommandType.STYLE_TRANSFER: 0.85,
                    CommandType.MUSIC_ANALYSIS: 0.6
                },
                "characteristics": {
                    "neural_based": True,
                    "realtime_capable": False,
                    "memory_intensive": True,
                    "quality_score": 0.85,
                    "latency": "high"
                }
            },
            ModelType.MUSIC21: {
                "capabilities": [
                    "music_theory_analysis",
                    "chord_identification",
                    "score_generation",
                    "voice_leading",
                    "counterpoint",
                    "form_analysis"
                ],
                "preferred_for": [
                    CommandType.MUSIC_ANALYSIS
                ],
                "strength_score": {
                    CommandType.MUSIC_ANALYSIS: 0.95,
                    CommandType.MELODY_TO_ARRANGEMENT: 0.65,
                    CommandType.TEXT_TO_MUSIC: 0.3,
                    CommandType.IMPROVISATION: 0.75
                },
                "characteristics": {
                    "neural_based": False,
                    "realtime_capable": True,
                    "memory_intensive": False,
                    "quality_score": 0.8,
                    "latency": "low"
                }
            },
            ModelType.BASIC_PITCH: {
                "capabilities": [
                    "audio_to_midi",
                    "pitch_detection",
                    "pitch_correction",
                    "audio_analysis",
                    "transcription"
                ],
                "preferred_for": [
                    CommandType.PITCH_CORRECTION
                ],
                "strength_score": {
                    CommandType.PITCH_CORRECTION: 0.95,
                    CommandType.MUSIC_ANALYSIS: 0.5,
                    CommandType.MELODY_TO_ARRANGEMENT: 0.6
                },
                "characteristics": {
                    "neural_based": True,
                    "realtime_capable": False,
                    "memory_intensive": False,
                    "quality_score": 0.9,
                    "latency": "medium"
                }
            },
            # 新增模型: DDSP (Differentiable Digital Signal Processing)
            ModelType.DDSP: {
                "capabilities": [
                    "timbre_transfer",
                    "audio_synthesis",
                    "instrument_modeling",
                    "audio_effects"
                ],
                "preferred_for": [
                    CommandType.STYLE_TRANSFER
                ],
                "strength_score": {
                    CommandType.STYLE_TRANSFER: 0.9,
                    CommandType.PITCH_CORRECTION: 0.8,
                    CommandType.TEXT_TO_MUSIC: 0.6
                },
                "characteristics": {
                    "neural_based": True,
                    "realtime_capable": False,
                    "memory_intensive": True,
                    "quality_score": 0.9,
                    "latency": "high"
                }
            },
            # 新增模型: MuseNet
            ModelType.MUSENET: {
                "capabilities": [
                    "melody_generation",
                    "multi_instrument_composition",
                    "style_imitation",
                    "long_form_composition"
                ],
                "preferred_for": [
                    CommandType.TEXT_TO_MUSIC,
                    CommandType.IMPROVISATION
                ],
                "strength_score": {
                    CommandType.TEXT_TO_MUSIC: 0.9,
                    CommandType.IMPROVISATION: 0.85,
                    CommandType.STYLE_TRANSFER: 0.8,
                    CommandType.MELODY_TO_ARRANGEMENT: 0.85
                },
                "characteristics": {
                    "neural_based": True,
                    "realtime_capable": False,
                    "memory_intensive": True,
                    "quality_score": 0.9,
                    "latency": "high"
                }
            },
            # 新增輕量級模型: RNNComposer
            ModelType.RNN_COMPOSER: {
                "capabilities": [
                    "melody_generation",
                    "chord_progression",
                    "simple_arrangement"
                ],
                "preferred_for": [
                    CommandType.IMPROVISATION
                ],
                "strength_score": {
                    CommandType.IMPROVISATION: 0.8,
                    CommandType.TEXT_TO_MUSIC: 0.75,
                    CommandType.MELODY_TO_ARRANGEMENT: 0.7
                },
                "characteristics": {
                    "neural_based": True,
                    "realtime_capable": True,
                    "memory_intensive": False,
                    "quality_score": 0.75,
                    "latency": "low"
                }
            }
        }
        
        # 指令需求映射
        self.command_requirements = {
            CommandType.TEXT_TO_MUSIC: [
                "melody_generation", 
                "accompaniment_generation"
            ],
            CommandType.MELODY_TO_ARRANGEMENT: [
                "accompaniment_generation"
            ],
            CommandType.MUSIC_ANALYSIS: [
                "music_theory_analysis", 
                "chord_identification"
            ],
            CommandType.PITCH_CORRECTION: [
                "pitch_detection", 
                "pitch_correction"
            ],
            CommandType.STYLE_TRANSFER: [
                "style_transfer", 
                "melody_generation", 
                "arrangement"
            ],
            CommandType.IMPROVISATION: [
                "melody_generation", 
                "chord_identification"
            ]
        }
        
        # 參數偏好映射
        self.parameter_preferences = {
            "genre": {
                "jazz": [ModelType.MAGENTA, ModelType.MUSENET],
                "classical": [ModelType.MUSIC21, ModelType.MUSENET],
                "electronic": [ModelType.MAGENTA, ModelType.DDSP],
                "folk": [ModelType.RNN_COMPOSER, ModelType.MUSIC21],
                "pop": [ModelType.MAGENTA, ModelType.MUSENET],
                "rock": [ModelType.MAGENTA, ModelType.RNN_COMPOSER],
                "ambient": [ModelType.DDSP]
            },
            "form": {
                "sonata": [ModelType.MUSIC21],
                "theme_variations": [ModelType.MUSIC21],
                "through_composed": [ModelType.MAGENTA, ModelType.MUSENET],
                "verse_chorus": [ModelType.MAGENTA, ModelType.RNN_COMPOSER]
            },
            "emotion": {
                "epic": [ModelType.MUSENET],
                "nostalgic": [ModelType.MUSIC21, ModelType.MUSENET],
                "energetic": [ModelType.MAGENTA, ModelType.RNN_COMPOSER],
                "calm": [ModelType.MUSIC21, ModelType.DDSP]
            },
            "complexity": {
                "high": [ModelType.MAGENTA, ModelType.MUSENET, ModelType.MUSIC21],
                "low": [ModelType.RNN_COMPOSER]
            }
        }
        
        # 初始化性能歷史記錄
        self.performance_history = self._load_performance_history()
        
        # 上下文記憶: 記錄最近的指令和選用的模型
        self.context_memory = {
            "recent_commands": [],
            "preferred_models": defaultdict(list)
        }
        
        # 最大上下文記憶長度
        self.max_context_memory = 10
        
        logger.info("模型選擇器初始化完成")
    
    def _load_performance_history(self) -> Dict[str, Any]:
        """載入模型性能歷史記錄
        
        Returns:
            Dict[str, Any]: 模型性能歷史記錄
        """
        default_history = {
            "model_success_rates": {str(model): 0.9 for model in ModelType},
            "command_type_models": {},
            "command_parameter_models": {}
        }
        
        if not os.path.exists(self.performance_history_path):
            logger.info(f"性能歷史記錄檔案不存在，創建新檔案: {self.performance_history_path}")
            with open(self.performance_history_path, 'w', encoding='utf-8') as f:
                json.dump(default_history, f, indent=2, ensure_ascii=False)
            return default_history
        
        try:
            with open(self.performance_history_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
            return history
        except Exception as e:
            logger.error(f"載入性能歷史記錄失敗: {str(e)}")
            return default_history
    
    def _save_performance_history(self) -> None:
        """保存模型性能歷史記錄"""
        try:
            with open(self.performance_history_path, 'w', encoding='utf-8') as f:
                json.dump(self.performance_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存性能歷史記錄失敗: {str(e)}")
    
    def update_model_performance(self, model: ModelType, command_type: CommandType, 
                                success: bool, parameters: Optional[Dict[str, Any]] = None) -> None:
        """更新模型性能記錄
        
        Args:
            model: 模型類型
            command_type: 指令類型
            success: 是否成功
            parameters: 指令參數
        """
        model_str = str(model)
        command_type_str = str(command_type)
        
        # 更新全局成功率
        if model_str not in self.performance_history["model_success_rates"]:
            self.performance_history["model_success_rates"][model_str] = 0.9  # 初始默認值
        
        current_rate = self.performance_history["model_success_rates"][model_str]
        # 使用加權平均，讓新記錄影響較大
        self.performance_history["model_success_rates"][model_str] = current_rate * 0.8 + (1.0 if success else 0.0) * 0.2
        
        # 按指令類型更新
        if command_type_str not in self.performance_history["command_type_models"]:
            self.performance_history["command_type_models"][command_type_str] = {}
        
        if model_str not in self.performance_history["command_type_models"][command_type_str]:
            self.performance_history["command_type_models"][command_type_str][model_str] = 0.9  # 初始默認值
        
        current_type_rate = self.performance_history["command_type_models"][command_type_str][model_str]
        self.performance_history["command_type_models"][command_type_str][model_str] = current_type_rate * 0.7 + (1.0 if success else 0.0) * 0.3
        
        # 按參數更新
        if parameters:
            for param_name, param_value in parameters.items():
                if isinstance(param_value, (str, int, float, bool)):
                    key = f"{param_name}:{param_value}"
                    
                    if key not in self.performance_history["command_parameter_models"]:
                        self.performance_history["command_parameter_models"][key] = {}
                    
                    if model_str not in self.performance_history["command_parameter_models"][key]:
                        self.performance_history["command_parameter_models"][key][model_str] = 0.9  # 初始默認值
                    
                    current_param_rate = self.performance_history["command_parameter_models"][key][model_str]
                    self.performance_history["command_parameter_models"][key][model_str] = current_param_rate * 0.7 + (1.0 if success else 0.0) * 0.3
        
        # 更新上下文記憶
        self.context_memory["preferred_models"][command_type_str].append((model_str, success))
        while len(self.context_memory["preferred_models"][command_type_str]) > self.max_context_memory:
            self.context_memory["preferred_models"][command_type_str].pop(0)
        
        # 保存更新後的記錄
        self._save_performance_history()
    
    def select_models(self, command: MCPCommand, available_models: List[ModelType]) -> List[Tuple[ModelType, float, str]]:
        """為指令選擇合適的模型
        
        Args:
            command: MCP指令
            available_models: 可用模型列表
            
        Returns:
            List[Tuple[ModelType, float, str]]: 模型、得分和選擇原因的列表，按得分降序排序
        """
        logger.info(f"為指令類型 {command.command_type} 選擇模型")
        
        # 更新上下文記憶
        self.context_memory["recent_commands"].append({
            "command_type": str(command.command_type),
            "timestamp": datetime.now().isoformat(),
            "parameters": command.parameters.model_dump() if command.parameters else {}
        })
        while len(self.context_memory["recent_commands"]) > self.max_context_memory:
            self.context_memory["recent_commands"].pop(0)
        
        # 如果指令有明確的模型偏好，且偏好的模型可用，優先使用
        if command.model_preferences:
            preferred_models = [model for model in command.model_preferences if model in available_models]
            if preferred_models:
                return [(model, 1.0, "用戶指定偏好") for model in preferred_models]
        
        # 計算每個可用模型的得分
        model_scores = []
        
        for model in available_models:
            score, reason = self._calculate_model_score(model, command)
            model_scores.append((model, score, reason))
        
        # 按得分降序排序
        model_scores.sort(key=lambda x: x[1], reverse=True)
        
        logger.info(f"模型得分: {[(str(m), s) for m, s, _ in model_scores]}")
        return model_scores
    
    def select_best_model(self, command: MCPCommand, available_models: List[ModelType]) -> Tuple[ModelType, str]:
        """選擇最佳模型
        
        Args:
            command: MCP指令
            available_models: 可用模型列表
            
        Returns:
            Tuple[ModelType, str]: 最佳模型和選擇原因
        """
        if not available_models:
            raise ValueError("沒有可用的模型")
        
        model_scores = self.select_models(command, available_models)
        best_model, _, reason = model_scores[0]
        
        logger.info(f"選擇最佳模型: {best_model}, 原因: {reason}")
        return best_model, reason
    
    def get_ensemble_models(self, command: MCPCommand, available_models: List[ModelType], 
                           min_score: float = 0.7, max_models: int = 3) -> List[Tuple[ModelType, float, str]]:
        """獲取適合組合使用的模型
        
        Args:
            command: MCP指令
            available_models: 可用模型列表
            min_score: 最低模型得分要求
            max_models: 最大模型數量
            
        Returns:
            List[Tuple[ModelType, float, str]]: 模型、得分和選擇原因列表
        """
        model_scores = self.select_models(command, available_models)
        
        # 過濾得分達標的模型
        qualified_models = [m for m in model_scores if m[1] >= min_score]
        
        # 限制模型數量
        return qualified_models[:max_models]
    
    def _calculate_model_score(self, model: ModelType, command: MCPCommand) -> Tuple[float, str]:
        """計算模型得分
        
        Args:
            model: 模型類型
            command: MCP指令
            
        Returns:
            Tuple[float, str]: 得分和得分原因
        """
        score = 0.0
        reasons = []
        
        # 檢查模型是否擁有指令所需的能力
        required_capabilities = self.command_requirements.get(command.command_type, [])
        model_capabilities = self.model_capabilities.get(model, {}).get("capabilities", [])
        
        capability_match_count = sum(1 for cap in required_capabilities if cap in model_capabilities)
        capability_match_ratio = capability_match_count / len(required_capabilities) if required_capabilities else 0
        
        score += capability_match_ratio * 0.4
        if capability_match_ratio > 0:
            reasons.append(f"具備 {capability_match_count}/{len(required_capabilities)} 所需能力")
        
        # 檢查模型是否為該指令類型的首選
        preferred_for = self.model_capabilities.get(model, {}).get("preferred_for", [])
        if command.command_type in preferred_for:
            score += 0.2
            reasons.append("指令類型首選模型")
        
        # 考慮模型在該指令類型上的得分
        strength_score = self.model_capabilities.get(model, {}).get("strength_score", {}).get(command.command_type, 0)
        score += strength_score * 0.15
        if strength_score > 0.7:
            reasons.append(f"擅長此類指令 (強度:{strength_score:.1f})")
        
        # 考慮歷史性能記錄
        model_str = str(model)
        command_type_str = str(command.command_type)
        
        if model_str in self.performance_history["model_success_rates"]:
            success_rate = self.performance_history["model_success_rates"][model_str]
            score += success_rate * 0.05
            
            if success_rate > 0.9:
                reasons.append("歷史高成功率")
        
        if command_type_str in self.performance_history["command_type_models"] and model_str in self.performance_history["command_type_models"][command_type_str]:
            type_success_rate = self.performance_history["command_type_models"][command_type_str][model_str]
            score += type_success_rate * 0.1
            
            if type_success_rate > 0.9:
                reasons.append(f"對{command.command_type}有良好表現")
        
        # 考慮音樂參數偏好
        if command.parameters:
            param_preference_count = 0
            param_total = 0
            
            for param_name, param_values in self.parameter_preferences.items():
                param_value = getattr(command.parameters, param_name, None)
                if param_value:
                    param_total += 1
                    
                    if param_value in param_values and model in param_values[param_value]:
                        param_preference_count += 1
                        score += 0.05
                        reasons.append(f"參數偏好匹配: {param_name}={param_value}")
                    
                    # 檢查歷史參數性能
                    key = f"{param_name}:{param_value}"
                    if key in self.performance_history["command_parameter_models"] and model_str in self.performance_history["command_parameter_models"][key]:
                        param_success_rate = self.performance_history["command_parameter_models"][key][model_str]
                        score += param_success_rate * 0.05
            
            # 如果多項參數都有匹配，給予額外獎勵
            if param_preference_count > 1 and param_total > 0:
                bonus = min(0.15, param_preference_count / param_total * 0.15)
                score += bonus
        
        # 考慮上下文記憶中的最近表現
        if command_type_str in self.context_memory["preferred_models"]:
            recent_model_successes = [s for m, s in self.context_memory["preferred_models"][command_type_str] if m == model_str]
            if recent_model_successes:
                recent_success_rate = sum(1 for s in recent_model_successes if s) / len(recent_model_successes)
                score += recent_success_rate * 0.05
                
                if recent_success_rate > 0.8 and len(recent_model_successes) >= 3:
                    reasons.append("近期良好表現")
        
        # 根據模型特性調整得分
        characteristics = self.model_capabilities.get(model, {}).get("characteristics", {})
        
        # 如果指令參數明確要求高品質，增加高品質模型的分數
        if command.parameters and getattr(command.parameters, "complexity", None) and getattr(command.parameters, "complexity", 0) > 7:
            quality_score = characteristics.get("quality_score", 0.5)
            score += quality_score * 0.1
            
            if quality_score > 0.8:
                reasons.append("高品質輸出能力")
        
        # 考慮資源限制和延遲要求
        latency = characteristics.get("latency", "medium")
        if hasattr(command, "performance_requirements") and getattr(command, "performance_requirements", {}).get("low_latency", False):
            if latency == "low":
                score += 0.1
                reasons.append("符合低延遲要求")
            elif latency == "high":
                score -= 0.1
        
        # 根據模型特性和指令類型調整得分
        if command.command_type == CommandType.PITCH_CORRECTION and model == ModelType.BASIC_PITCH:
            score += 0.15
            reasons.append("專門設計用於音高校正")
        
        elif command.command_type == CommandType.MUSIC_ANALYSIS and model == ModelType.MUSIC21:
            score += 0.15
            reasons.append("專門設計用於音樂理論分析")
        
        elif command.command_type in [CommandType.TEXT_TO_MUSIC, CommandType.MELODY_TO_ARRANGEMENT] and model == ModelType.MAGENTA:
            score += 0.15
            reasons.append("專門設計用於音樂生成和編曲")
        
        elif command.command_type == CommandType.STYLE_TRANSFER and model == ModelType.DDSP:
            score += 0.15
            reasons.append("專門設計用於音色轉換")
        
        elif command.command_type == CommandType.TEXT_TO_MUSIC and model == ModelType.MUSENET:
            score += 0.15
            reasons.append("擅長根據文字描述創作音樂")
        
        elif command.command_type == CommandType.IMPROVISATION and model == ModelType.RNN_COMPOSER:
            score += 0.1
            reasons.append("適合即時音樂即興創作")
        
        # 生成綜合原因
        if not reasons:
            reason = "基本兼容性"
        elif len(reasons) == 1:
            reason = reasons[0]
        else:
            # 選擇最重要的兩個原因
            sorted_reasons = sorted(reasons, key=lambda x: len(x))  # 簡單假設較短的原因更重要
            reason = f"{sorted_reasons[0]}、{sorted_reasons[1]}"
            if len(sorted_reasons) > 2:
                reason += f" 等{len(reasons)}個因素"
        
        return min(score, 1.0), reason 