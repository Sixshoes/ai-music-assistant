"""日誌服務模組

提供統一的指令處理日誌記錄功能
"""

import os
import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List

from ..mcp_schema import MCPCommand, MCPResponse, ModelType, ProcessingStatus


class LoggingService:
    """日誌服務類別
    
    為MCP指令處理提供可追蹤的日誌系統
    """
    
    def __init__(self, log_dir: str = None):
        """初始化日誌服務
        
        Args:
            log_dir: 日誌文件目錄，如果未指定則使用默認值
        """
        self.log_dir = log_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
        
        # 確保日誌目錄存在
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 設置模型調用日誌
        self.model_logger = logging.getLogger("model_coordinator.model_calls")
        self._setup_model_logger()
        
        # 設置指令處理日誌
        self.command_logger = logging.getLogger("model_coordinator.commands")
        self._setup_command_logger()
        
        # 設置模型決策日誌
        self.decision_logger = logging.getLogger("model_coordinator.decisions")
        self._setup_decision_logger()
        
        # 設置性能追蹤日誌
        self.performance_logger = logging.getLogger("model_coordinator.performance")
        self._setup_performance_logger()
    
    def _setup_model_logger(self):
        """設置模型調用日誌"""
        handler = logging.FileHandler(os.path.join(self.log_dir, "model_calls.log"))
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.model_logger.addHandler(handler)
        self.model_logger.setLevel(logging.INFO)
    
    def _setup_command_logger(self):
        """設置指令處理日誌"""
        handler = logging.FileHandler(os.path.join(self.log_dir, "commands.log"))
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.command_logger.addHandler(handler)
        self.command_logger.setLevel(logging.INFO)
    
    def _setup_decision_logger(self):
        """設置模型決策日誌"""
        handler = logging.FileHandler(os.path.join(self.log_dir, "decisions.log"))
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.decision_logger.addHandler(handler)
        self.decision_logger.setLevel(logging.INFO)
    
    def _setup_performance_logger(self):
        """設置性能追蹤日誌"""
        handler = logging.FileHandler(os.path.join(self.log_dir, "performance.log"))
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.performance_logger.addHandler(handler)
        self.performance_logger.setLevel(logging.INFO)
    
    def log_command_received(self, command_id: str, command: MCPCommand):
        """記錄收到的MCP指令
        
        Args:
            command_id: 指令ID
            command: MCP指令
        """
        self.command_logger.info(f"收到指令 {command_id}: 類型={command.command_type}")
        
        # 將指令詳情記錄為JSON格式
        details = {
            "command_id": command_id,
            "command_type": str(command.command_type),
            "created_at": datetime.now().isoformat(),
            "model_preferences": [str(m) for m in command.model_preferences] if command.model_preferences else None,
            "has_text_input": bool(command.text_input),
            "has_melody_input": bool(command.melody_input),
            "has_audio_input": bool(command.audio_input),
            "parameters": command.parameters.model_dump() if command.parameters else None
        }
        
        # 記錄詳細指令到JSON文件
        json_path = os.path.join(self.log_dir, f"command_{command_id}.json")
        with open(json_path, 'w') as f:
            json.dump(details, f, indent=2)
    
    def log_command_completed(self, command_id: str, response: MCPResponse, processing_time: float):
        """記錄指令完成
        
        Args:
            command_id: 指令ID
            response: MCP回應
            processing_time: 處理時間（秒）
        """
        self.command_logger.info(
            f"指令 {command_id} 完成: 狀態={response.status}, 處理時間={processing_time:.2f}秒"
        )
        
        # 將響應詳情記錄為JSON格式
        details = {
            "command_id": command_id,
            "status": str(response.status),
            "processing_time": processing_time,
            "completed_at": datetime.now().isoformat(),
            "models_used": [str(m) for m in response.models_used] if response.models_used else None,
            "has_music_data": bool(response.music_data),
            "has_analysis": bool(response.analysis),
            "error": response.error,
        }
        
        # 記錄詳細回應到JSON文件
        json_path = os.path.join(self.log_dir, f"response_{command_id}.json")
        with open(json_path, 'w') as f:
            json.dump(details, f, indent=2)
    
    def log_model_call(self, model_type: ModelType, operation: str, input_params: Dict[str, Any], execution_time: float):
        """記錄模型調用
        
        Args:
            model_type: 模型類型
            operation: 操作名稱
            input_params: 輸入參數摘要
            execution_time: 執行時間（秒）
        """
        self.model_logger.info(
            f"模型調用: {model_type} - {operation}, 執行時間={execution_time:.3f}秒"
        )
        
        # 記錄性能數據
        self.performance_logger.info(
            f"{model_type},{operation},{execution_time:.3f}"
        )
    
    def log_model_selection_decision(self, command_id: str, command_type: str, 
                                   available_models: List[ModelType], 
                                   selected_model: ModelType,
                                   selection_reason: str):
        """記錄模型選擇決策
        
        Args:
            command_id: 指令ID
            command_type: 指令類型
            available_models: 可用模型列表
            selected_model: 選擇的模型
            selection_reason: 選擇原因
        """
        self.decision_logger.info(
            f"模型選擇決策: 指令={command_id}, 類型={command_type}, "
            f"選擇={selected_model}, 原因={selection_reason}"
        )
        
        # 將決策詳情記錄為JSON格式
        details = {
            "command_id": command_id,
            "command_type": command_type,
            "timestamp": datetime.now().isoformat(),
            "available_models": [str(m) for m in available_models],
            "selected_model": str(selected_model),
            "selection_reason": selection_reason
        }
        
        # 記錄決策到JSON文件
        json_path = os.path.join(self.log_dir, f"decision_{command_id}_{int(time.time())}.json")
        with open(json_path, 'w') as f:
            json.dump(details, f, indent=2)
    
    def log_workflow_step(self, command_id: str, step_name: str, status: str, details: Dict[str, Any] = None):
        """記錄工作流程步驟
        
        Args:
            command_id: 指令ID
            step_name: 步驟名稱
            status: 步驟狀態
            details: 詳細信息
        """
        self.command_logger.info(
            f"工作流程步驟: 指令={command_id}, 步驟={step_name}, 狀態={status}"
        )
        
        if details:
            # 記錄步驟詳情到JSON文件
            json_path = os.path.join(self.log_dir, f"step_{command_id}_{step_name}_{int(time.time())}.json")
            with open(json_path, 'w') as f:
                # 確保可序列化
                serializable_details = {}
                for k, v in details.items():
                    if isinstance(v, (str, int, float, bool, list, dict, type(None))):
                        serializable_details[k] = v
                    else:
                        serializable_details[k] = str(v)
                
                json.dump(serializable_details, f, indent=2)
    
    def log_error(self, command_id: str, error_type: str, error_message: str, stack_trace: Optional[str] = None):
        """記錄錯誤
        
        Args:
            command_id: 指令ID
            error_type: 錯誤類型
            error_message: 錯誤消息
            stack_trace: 堆棧跟踪
        """
        self.command_logger.error(
            f"錯誤: 指令={command_id}, 類型={error_type}, 消息={error_message}"
        )
        
        # 記錄錯誤詳情到JSON文件
        details = {
            "command_id": command_id,
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_message": error_message,
            "stack_trace": stack_trace
        }
        
        json_path = os.path.join(self.log_dir, f"error_{command_id}_{int(time.time())}.json")
        with open(json_path, 'w') as f:
            json.dump(details, f, indent=2)


def setup_logger(logger_name: str, log_level: int = logging.INFO) -> logging.Logger:
    """設置並返回一個日誌記錄器
    
    Args:
        logger_name: 日誌記錄器名稱
        log_level: 日誌級別，默認為 INFO
        
    Returns:
        logging.Logger: 配置好的日誌記錄器
    """
    # 創建日誌記錄器
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    
    # 檢查是否已經有處理器，避免重複添加
    if not logger.handlers:
        # 創建控制台處理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        
        # 創建格式化器
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        # 添加處理器到日誌記錄器
        logger.addHandler(console_handler)
        
        # 創建文件處理器
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.FileHandler(os.path.join(log_dir, f"{logger_name}.log"))
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        
        # 添加文件處理器
        logger.addHandler(file_handler)
    
    return logger 