"""模型協調器

負責協調不同AI模型和工具間的工作流程，實現從指令到音樂生成的完整過程
"""

import uuid
import logging
import time
import traceback
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Set

from ..mcp_schema import (
    MCPCommand,
    MCPResponse,
    CommandType,
    ProcessingStatus,
    MusicTheoryAnalysis,
    ModelType,
    MusicData
)
from .workflow import (
    Workflow, 
    TextToMusicWorkflow, 
    MelodyToArrangementWorkflow,
    MusicAnalysisWorkflow,
    PitchCorrectionWorkflow,
    StyleTransferWorkflow,
    ImprovisationWorkflow
)
from .model_selector import ModelSelector
from .model_interface import ModelInterfaceFactory, ModelInterface
from .logging_service import LoggingService

class ModelCoordinator:
    """模型協調器類別，協調不同模型和工具的工作流程"""
    
    def __init__(self):
        """初始化模型協調器"""
        # 工作流程映射
        self.workflows: Dict[CommandType, Workflow] = {
            CommandType.TEXT_TO_MUSIC: TextToMusicWorkflow(),
            CommandType.MELODY_TO_ARRANGEMENT: MelodyToArrangementWorkflow(),
            CommandType.MUSIC_ANALYSIS: MusicAnalysisWorkflow(),
            CommandType.PITCH_CORRECTION: PitchCorrectionWorkflow(),
            CommandType.STYLE_TRANSFER: StyleTransferWorkflow(),
            CommandType.IMPROVISATION: ImprovisationWorkflow()
        }
        
        # 活躍命令追蹤
        self.active_commands: Dict[str, Dict[str, Any]] = {}
        
        # 可用模型集合
        self.available_models: Set[ModelType] = {
            ModelType.MAGENTA,
            ModelType.MUSIC21,
            ModelType.BASIC_PITCH
        }
        
        # 模型介面緩存
        self.model_interfaces: Dict[ModelType, ModelInterface] = {}
        
        # 初始化日誌服務
        self.logger_service = LoggingService()
        
        # 初始化模型選擇器
        self.model_selector = ModelSelector()
        
        # 標準記錄器設定
        self.logger = logging.getLogger(__name__)
        self.logger.info("模型協調器初始化完成")
    
    def register_workflow(self, command_type: CommandType, workflow: Workflow) -> None:
        """註冊新的工作流程
        
        Args:
            command_type: 指令類型
            workflow: 對應的工作流程實例
        """
        self.logger.info(f"註冊新工作流程: {command_type}")
        self.workflows[command_type] = workflow
    
    def register_model(self, model_type: ModelType) -> None:
        """註冊可用模型
        
        Args:
            model_type: 模型類型
        """
        self.logger.info(f"註冊可用模型: {model_type}")
        self.available_models.add(model_type)
    
    def unregister_model(self, model_type: ModelType) -> None:
        """取消註冊模型
        
        Args:
            model_type: 模型類型
        """
        if model_type in self.available_models:
            self.logger.info(f"取消註冊模型: {model_type}")
            self.available_models.remove(model_type)
            # 釋放模型介面
            if model_type in self.model_interfaces:
                del self.model_interfaces[model_type]
    
    def get_model_interface(self, model_type: ModelType) -> ModelInterface:
        """獲取模型介面
        
        Args:
            model_type: 模型類型
            
        Returns:
            ModelInterface: 模型介面
            
        Raises:
            ValueError: 如果模型類型不可用
        """
        if model_type not in self.available_models:
            raise ValueError(f"模型 {model_type} 不可用")
        
        # 如果介面已存在，直接返回
        if model_type in self.model_interfaces:
            return self.model_interfaces[model_type]
        
        # 否則創建新介面
        try:
            interface = ModelInterfaceFactory.create_interface(model_type, self.logger_service)
            self.model_interfaces[model_type] = interface
            return interface
        except Exception as e:
            self.logger.error(f"創建模型介面失敗: {model_type}, 錯誤: {str(e)}")
            raise
    
    def process_command(self, command: MCPCommand, command_id: str = None) -> MCPResponse:
        """處理MCP指令
        
        Args:
            command: MCP指令對象
            command_id: 指令ID (若為None則自動生成)
            
        Returns:
            MCPResponse: 處理結果回應
        """
        # 生成命令ID (如果未提供)
        if command_id is None:
            command_id = str(uuid.uuid4())
        
        start_time = time.time()
        self.logger.info(f"開始處理指令 {command_id} 類型: {command.command_type}")
        
        # 記錄接收指令
        self.logger_service.log_command_received(command_id, command)
        
        try:
            # 檢查是否支援指令類型
            if command.command_type not in self.workflows:
                error_msg = f"不支援的指令類型: {command.command_type}"
                self.logger.error(error_msg)
                self.logger_service.log_error(command_id, "UnsupportedCommandType", error_msg)
                return MCPResponse(
                    command_id=command_id,
                    status=ProcessingStatus.FAILED,
                    error=error_msg,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
            
            # 獲取對應工作流程
            workflow = self.workflows[command.command_type]
            
            # 獲取可用模型
            available_models = self._get_available_models(command)
            
            # 選擇最佳模型
            best_model, selection_reason = self.model_selector.select_best_model(command, available_models)
            
            # 記錄模型選擇決策
            self.logger_service.log_model_selection_decision(
                command_id,
                str(command.command_type),
                available_models,
                best_model,
                selection_reason
            )
            
            # 獲取所選模型的介面
            model_interface = self.get_model_interface(best_model)
            
            # 將命令加入活躍命令列表
            self.active_commands[command_id] = {
                "command": command,
                "status": ProcessingStatus.PROCESSING,
                "start_time": start_time,
                "selected_model": best_model
            }
            
            # 設置工作流程執行環境
            workflow_context = {
                "command_id": command_id,
                "model_interface": model_interface,
                "additional_models": [self.get_model_interface(m) for m in available_models if m != best_model],
                "logger_service": self.logger_service
            }
            
            # 記錄工作流程開始
            self.logger_service.log_workflow_step(
                command_id, 
                "workflow_start", 
                "started",
                {"workflow_type": str(command.command_type), "selected_model": str(best_model)}
            )
            
            # 執行工作流程
            result = workflow.execute(command, workflow_context)
            
            # 計算處理時間
            processing_time = time.time() - start_time
            
            # 更新活躍命令狀態
            self.active_commands[command_id]["status"] = ProcessingStatus.COMPLETED
            self.active_commands[command_id]["result"] = result
            self.active_commands[command_id]["processing_time"] = processing_time
            self.active_commands[command_id]["models_used"] = result.get("models_used", [best_model])
            
            # 建立並返回回應
            music_data = None
            if "music_data" in result:
                if isinstance(result["music_data"], dict):
                    # 處理原始字典
                    music_data = MusicData(**result["music_data"])
                else:
                    # 已經是MusicData對象
                    music_data = result["music_data"]
            
            # 記錄成功處理
            self.logger.info(f"指令 {command_id} 處理完成，耗時: {processing_time:.2f}秒")
            
            # 記錄工作流程完成
            self.logger_service.log_workflow_step(
                command_id, 
                "workflow_complete", 
                "completed",
                {"processing_time": processing_time}
            )
            
            # 構建回應
            response = MCPResponse(
                command_id=command_id,
                status=ProcessingStatus.COMPLETED,
                music_data=music_data,
                analysis=result.get("analysis"),
                suggestions=result.get("suggestions"),
                models_used=result.get("models_used", [best_model]),
                processing_time=processing_time,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # 記錄指令完成
            self.logger_service.log_command_completed(command_id, response, processing_time)
            
            return response
            
        except Exception as e:
            # 計算處理時間
            processing_time = time.time() - start_time
            
            # 獲取堆棧追踪
            stack_trace = traceback.format_exc()
            
            # 記錄錯誤
            self.logger.error(f"處理指令 {command_id} 時發生錯誤: {str(e)}", exc_info=True)
            self.logger_service.log_error(
                command_id, 
                type(e).__name__, 
                str(e), 
                stack_trace
            )
            
            # 更新活躍命令狀態
            if command_id in self.active_commands:
                self.active_commands[command_id]["status"] = ProcessingStatus.FAILED
                self.active_commands[command_id]["error"] = str(e)
                self.active_commands[command_id]["processing_time"] = processing_time
            
            # 返回錯誤回應
            response = MCPResponse(
                command_id=command_id,
                status=ProcessingStatus.FAILED,
                error=str(e),
                processing_time=processing_time,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # 記錄指令完成（失敗）
            self.logger_service.log_command_completed(command_id, response, processing_time)
            
            return response
    
    def _get_available_models(self, command: MCPCommand) -> List[ModelType]:
        """獲取可用的模型清單，優先考慮命令中的模型偏好
        
        Args:
            command: MCP指令對象
            
        Returns:
            List[ModelType]: 可用模型列表
        """
        # 如果命令指定了模型偏好且在可用模型中，優先使用
        if command.model_preferences:
            preferred_models = [model for model in command.model_preferences if model in self.available_models]
            if preferred_models:
                return preferred_models
        
        # 根據指令類型過濾合適的模型
        suitable_models = []
        
        if command.command_type == CommandType.TEXT_TO_MUSIC:
            suitable_models = [ModelType.MAGENTA]
            
        elif command.command_type == CommandType.MELODY_TO_ARRANGEMENT:
            suitable_models = [ModelType.MAGENTA, ModelType.MUSIC21]
            
        elif command.command_type == CommandType.MUSIC_ANALYSIS:
            suitable_models = [ModelType.MUSIC21, ModelType.MAGENTA]
            
        elif command.command_type == CommandType.PITCH_CORRECTION:
            suitable_models = [ModelType.BASIC_PITCH]
            
        elif command.command_type == CommandType.STYLE_TRANSFER:
            suitable_models = [ModelType.MAGENTA]
            
        elif command.command_type == CommandType.IMPROVISATION:
            suitable_models = [ModelType.MAGENTA, ModelType.MUSIC21]
        
        # 確保所有模型都是可用的
        suitable_models = [model for model in suitable_models if model in self.available_models]
        
        # 如果沒有合適的模型，則返回所有可用模型
        if not suitable_models:
            return list(self.available_models)
        
        return suitable_models
    
    def get_command_status(self, command_id: str) -> Dict[str, Any]:
        """獲取指令處理狀態
        
        Args:
            command_id: 指令ID
            
        Returns:
            Dict[str, Any]: 包含指令狀態的字典
        """
        if command_id not in self.active_commands:
            return {"status": ProcessingStatus.FAILED, "error": "找不到指定命令"}
        
        command_info = self.active_commands[command_id]
        
        status_info = {
            "status": command_info["status"],
            "command_type": command_info["command"].command_type
        }
        
        # 如果有錯誤，則添加錯誤信息
        if "error" in command_info:
            status_info["error"] = command_info["error"]
        
        # 如果有結果，則添加處理時間和使用的模型
        if "processing_time" in command_info:
            status_info["processing_time"] = command_info["processing_time"]
        
        if "models_used" in command_info:
            status_info["models_used"] = [str(m) for m in command_info["models_used"]]
        elif "selected_model" in command_info:
            status_info["models_used"] = [str(command_info["selected_model"])]
        
        # 如果處理中，計算已過時間
        if command_info["status"] == ProcessingStatus.PROCESSING:
            status_info["elapsed_time"] = time.time() - command_info["start_time"]
        
        return status_info
    
    def cancel_command(self, command_id: str) -> bool:
        """取消正在處理的指令
        
        Args:
            command_id: 指令ID
            
        Returns:
            bool: 是否成功取消
        """
        if command_id not in self.active_commands:
            self.logger.warning(f"嘗試取消不存在的命令: {command_id}")
            return False
        
        command_info = self.active_commands[command_id]
        
        if command_info["status"] == ProcessingStatus.PROCESSING:
            # 標記為取消
            command_info["status"] = ProcessingStatus.CANCELLED
            
            # 如果工作流程支持取消，通知工作流程
            command_type = command_info["command"].command_type
            if command_type in self.workflows:
                workflow = self.workflows[command_type]
                if hasattr(workflow, 'cancel') and callable(getattr(workflow, 'cancel')):
                    workflow.cancel(command_id)
            
            # 記錄取消
            self.logger_service.log_workflow_step(
                command_id, 
                "workflow_cancelled", 
                "cancelled",
                {"cancelled_at": datetime.now().isoformat()}
            )
            
            self.logger.info(f"命令 {command_id} 已取消")
            return True
        
        self.logger.warning(f"嘗試取消非處理中命令: {command_id}, 當前狀態: {command_info['status']}")
        return False
    
    def get_active_commands(self) -> Dict[str, Dict[str, Any]]:
        """獲取所有活躍的命令
        
        Returns:
            Dict[str, Dict[str, Any]]: 命令ID到命令信息的映射
        """
        # 返回簡化的命令資訊
        result = {}
        for cmd_id, cmd_info in self.active_commands.items():
            result[cmd_id] = {
                "command_type": cmd_info["command"].command_type,
                "status": cmd_info["status"],
                "start_time": cmd_info.get("start_time"),
                "processing_time": cmd_info.get("processing_time")
            }
            
            if "selected_model" in cmd_info:
                result[cmd_id]["selected_model"] = str(cmd_info["selected_model"])
            
            if "models_used" in cmd_info:
                result[cmd_id]["models_used"] = [str(m) for m in cmd_info["models_used"]]
        
        return result
    
    def clean_completed_commands(self, max_age_seconds: int = 3600) -> int:
        """清理已完成的舊命令
        
        Args:
            max_age_seconds: 保留命令的最大年齡(秒)
            
        Returns:
            int: 清理的命令數量
        """
        current_time = time.time()
        completed_statuses = [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED, ProcessingStatus.CANCELLED]
        
        to_remove = []
        for cmd_id, cmd_info in self.active_commands.items():
            if cmd_info["status"] in completed_statuses:
                # 檢查是否過舊
                if "start_time" in cmd_info and (current_time - cmd_info["start_time"]) > max_age_seconds:
                    to_remove.append(cmd_id)
        
        # 移除舊命令
        for cmd_id in to_remove:
            del self.active_commands[cmd_id]
        
        cleaned_count = len(to_remove)
        if cleaned_count > 0:
            self.logger.info(f"已清理 {cleaned_count} 個舊命令")
        
        return cleaned_count