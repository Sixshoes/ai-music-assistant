"""協調器模組

負責協調各個組件的工作
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ..mcp_schema import MCPCommand, CommandStatus
from .workflow import TextToMusicWorkflow
from .exceptions import CommandProcessingError
from .utils import save_command

logger = logging.getLogger(__name__)

class ModelCoordinator:
    """模型協調器類"""
    
    def __init__(self):
        """初始化協調器"""
        self.workflows = {
            "text_to_music": TextToMusicWorkflow()
        }
        
    async def process_command(self, command: MCPCommand) -> None:
        """處理命令
        
        Args:
            command: 要處理的命令
        """
        try:
            logger.info(f"開始處理指令 {command.command_id} 類型: {command.command_type}")
            
            # 獲取對應的工作流程
            workflow = self.workflows.get(command.command_type)
            if not workflow:
                raise CommandProcessingError(
                    command.command_id,
                    f"不支持的命令類型: {command.command_type}"
                )
            
            # 執行工作流程
            result = await workflow.execute(command)
            
            # 更新命令狀態
            command.status = CommandStatus.COMPLETED
            command.completed_at = datetime.now()
            command.result = result
            
            # 保存命令
            save_command(command)
            
        except Exception as e:
            logger.error(f"處理命令時發生錯誤: {str(e)}")
            command.status = CommandStatus.FAILED
            command.error = str(e)
            command.completed_at = datetime.now()
            save_command(command)
            raise CommandProcessingError(command.command_id, str(e)) 