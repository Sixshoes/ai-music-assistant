"""主程序模組

提供 Web API 服務
"""

import os
import json
import asyncio
import logging
import traceback
from datetime import datetime
from typing import Optional, Dict, Any, List, Union
import tempfile
import shutil
import sys

# 將當前目錄添加到路徑中，以便能夠正確導入模組
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, Depends, status, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse

# 嘗試導入pydantic，如果不可用則使用簡單替代模型
try:
    from pydantic import BaseModel, Field
    USE_PYDANTIC = True
except ImportError:
    logger.warning("無法導入pydantic，使用基本類型替代。某些功能可能不可用。")
    USE_PYDANTIC = False
    
    # 創建簡單替代類
    class BaseModel:
        def __init__(self, **data):
            for key, value in data.items():
                setattr(self, key, value)
                
    # 簡單的Field替代函數
    def Field(*args, **kwargs):
        return None

from backend.mcp.mcp_schema import (
    MCPCommand,
    MCPResponse,
    MusicParameters,
    CommandStatus
)
from backend.mcp.model_coordinator import (
    ModelCoordinator,
    setup_logger,
    Config
)
from backend.mcp.error_types import (
    MCPError, 
    ErrorCode, 
    ErrorCategory, 
    ErrorSeverity,
    input_validation_error,
    model_error,
    storage_error,
    system_error
)
from backend.mcp.storage import (
    CommandStorage,
    CacheService,
    generate_id
)

# 導入音頻處理模組
from backend.audio_processing.basic_pitch_service import BasicPitchService
from backend.audio_processing.audio_processor import AudioProcessor

# 導入自動編曲模組
from backend.music_generation.accompaniment_generator.chord_generator import ChordGenerator
from backend.music_generation.accompaniment_generator.accompaniment_generator import AccompanimentGenerator

# 導入音樂理論 API 路由
from music_theory.music_theory_api import router as theory_router

# 設置日誌
logger = setup_logger("main")

# 創建配置
config = Config()

# 創建指令存儲
command_storage = CommandStorage(
    storage_type=config.get("storage.command_storage_type", "sqlite"),
    db_path=config.get("storage.command_db_path", "data/commands.db"),
    base_dir=config.get("storage.command_dir", "data/commands")
)

# 創建結果緩存
result_cache = CacheService(
    storage_type=config.get("storage.cache_storage_type", "sqlite"),
    namespace="results",
    default_ttl=config.get("storage.result_cache_ttl", 86400),  # 默認緩存1天
    db_path=config.get("storage.cache_db_path", "data/cache.db"),
    base_dir=config.get("storage.cache_dir", "data/cache")
)

# 創建進度緩存
progress_cache = CacheService(
    storage_type="sqlite",
    namespace="progress",
    default_ttl=1800,  # 默認緩存30分鐘
    db_path="data/progress.db"
)

# 創建應用
app = FastAPI(
    title="AI Music Assistant API",
    description="AI 音樂助手 API",
    version="0.1.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 掛載靜態文件
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

# 註冊路由
app.include_router(theory_router)

# 默認參數
default_parameters = MusicParameters(
    description="自動生成的音樂",
    tempo=120,
    key="C",
    time_signature="4/4",
    genre="pop",
    instruments=["piano"],
    duration=60,
    complexity=3
)

# 活躍的任務進度
active_tasks = {}

# 初始化音頻處理服務
try:
    basic_pitch_service = BasicPitchService()
    audio_processor = AudioProcessor()
    logger.info("音頻處理服務初始化成功")
except Exception as e:
    logger.warning(f"音頻處理服務初始化失敗: {str(e)}")
    logger.warning("音頻處理相關功能將不可用")
    # 創建空的對象以避免引用錯誤
    basic_pitch_service = None
    audio_processor = None

# 初始化自動編曲服務
try:
    chord_generator = ChordGenerator()
    accompaniment_generator = AccompanimentGenerator()
    logger.info("自動編曲服務初始化成功")
except Exception as e:
    logger.warning(f"自動編曲服務初始化失敗: {str(e)}")
    logger.warning("自動編曲相關功能將不可用")
    # 創建空的對象以避免引用錯誤
    chord_generator = None
    accompaniment_generator = None


# 自定義錯誤處理器
@app.exception_handler(MCPError)
async def mcp_error_handler(request: Request, exc: MCPError):
    """處理 MCPError 異常
    
    Args:
        request: 請求對象
        exc: MCPError 異常
        
    Returns:
        自定義錯誤響應
    """
    logger.error(f"MCPError: {exc.message} [Code: {exc.error_code.value}]")
    
    return JSONResponse(
        status_code=exc.get_http_status_code(),
        content=exc.to_dict()
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """處理一般異常
    
    Args:
        request: 請求對象
        exc: 異常
        
    Returns:
        自定義錯誤響應
    """
    # 獲取堆疊追蹤
    stack_trace = traceback.format_exc()
    logger.error(f"未處理的異常: {str(exc)}", exc_info=True)
    
    # 創建系統錯誤
    error = system_error(
        message=f"服務器內部錯誤: {str(exc)}",
        error_code=ErrorCode.INTERNAL_SERVER_ERROR,
        details={"stack_trace": stack_trace}
    )
    
    return JSONResponse(
        status_code=error.get_http_status_code(),
        content=error.to_dict()
    )


# 任務狀態更新函數
async def update_task_progress(command_id: str, status: str, progress: float, message: str):
    """更新任務進度
    
    Args:
        command_id: 指令ID
        status: 狀態
        progress: 進度 (0-100)
        message: 進度消息
    """
    progress_data = {
        "command_id": command_id,
        "status": status,
        "progress": progress,
        "message": message,
        "updated_at": datetime.now()
    }
    
    # 更新緩存
    await progress_cache.set(command_id, progress_data)
    
    # 更新活躍任務
    active_tasks[command_id] = progress_data


# 任務管理函數
async def process_command_task(
    command_id: str,
    command: MCPCommand,
    background_tasks: BackgroundTasks
):
    """處理指令任務
    
    Args:
        command_id: 指令ID
        command: 指令對象
        background_tasks: 背景任務
    """
    try:
        # 更新任務狀態為處理中
        await update_task_progress(command_id, "PROCESSING", 10, "初始化處理...")
        
        # 處理指令
        coordinator = ModelCoordinator()
        
        # 更新狀態
        await update_task_progress(command_id, "PROCESSING", 30, "模型處理中...")
        
        # 處理
        result = await coordinator.process_command(command, command_id)
        
        # 更新狀態
        await update_task_progress(command_id, "COMPLETED", 100, "處理完成")
        
        # 緩存結果
        await result_cache.set(command_id, result.model_dump())
        
        # 更新指令狀態
        await command_storage.update_command_status(
            command_id,
            CommandStatus.COMPLETED,
            result=result.model_dump()
        )
        
        # 清理舊指令和過期緩存（作為背景任務）
        background_tasks.add_task(command_storage.cleanup_old_commands)
        background_tasks.add_task(result_cache.cleanup_expired)
        
    except Exception as e:
        # 記錄錯誤
        error_message = str(e)
        stack_trace = traceback.format_exc()
        logger.error(f"任務處理錯誤: {error_message}", exc_info=True)
        
        # 更新緩存狀態
        await update_task_progress(command_id, "FAILED", 0, f"處理失敗: {error_message}")
        
        # 更新指令狀態
        await command_storage.update_command_status(
            command_id, 
            CommandStatus.FAILED,
            error=error_message
        )
        
        if isinstance(e, MCPError):
            error_data = e.to_dict()
        else:
            # 將一般錯誤轉換為系統錯誤
            error = system_error(
                message=f"任務處理錯誤: {error_message}",
                details={"stack_trace": stack_trace},
                command_id=command_id
            )
            error_data = error.to_dict()
        
        # 緩存錯誤結果
        await result_cache.set(
            command_id,
            {
                "command_id": command_id,
                "status": "FAILED",
                "error": error_data
            }
        )
    finally:
        # 從活躍任務中移除
        if command_id in active_tasks:
            # 保留10分鐘後自動從活躍任務列表中刪除
            await asyncio.sleep(600)
            if command_id in active_tasks:
                del active_tasks[command_id]


@app.get("/")
async def read_root():
    """根路由處理器"""
    return {"message": "歡迎使用 AI 音樂助手"}


@app.post("/api/command", response_model=MCPResponse)
async def process_command(command: MCPCommand, background_tasks: BackgroundTasks) -> MCPResponse:
    """處理命令
    
    Args:
        command: 命令對象
        background_tasks: 背景任務
        
    Returns:
        命令處理響應
    """
    try:
        # 生成指令ID
        command_id = command.command_id or generate_id()
        
        # 記錄命令開始處理
        logger.info(
            f"開始處理命令: id={command_id}, "
            f"type={command.command_type}, "
            f"text_input={command.text_input}"
        )
        
        # 複製命令並設置ID和狀態
        command_with_id = command.model_copy(deep=True)
        command_with_id.command_id = command_id
        command_with_id.status = CommandStatus.PENDING
        command_with_id.created_at = datetime.now()
        command_with_id.updated_at = datetime.now()
        
        # 保存命令
        save_result = await command_storage.save_command(command_with_id)
        if not save_result:
            logger.error(f"保存命令失敗: {save_result.message}")
            raise storage_error(
                message=f"保存命令失敗: {save_result.message}",
                error_code=ErrorCode.STORAGE_WRITE_FAILURE,
                command_id=command_id
            )
        
        # 初始化進度追蹤
        await update_task_progress(command_id, "PENDING", 0, "正在排隊...")
        
        # 在背景處理命令
        background_tasks.add_task(process_command_task, command_id, command_with_id, background_tasks)
        
        # 立即返回響應
        return MCPResponse(
            command_id=command_id,
            status=CommandStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
    except MCPError as e:
        # 直接重新拋出MCPError，讓異常處理器處理
        raise
        
    except Exception as e:
        # 記錄錯誤
        logger.error(f"命令處理初始化錯誤: {str(e)}", exc_info=True)
        
        # 轉換為MCPError
        raise system_error(
            message=f"命令處理初始化失敗: {str(e)}",
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )


@app.get("/api/command/{command_id}", response_model=MCPResponse)
async def get_command_status(command_id: str) -> MCPResponse:
    """獲取命令狀態
    
    Args:
        command_id: 命令ID
        
    Returns:
        命令狀態響應
    """
    try:
        # 先從結果緩存獲取
        cache_result = await result_cache.get(command_id)
        if cache_result.success:
            # 從緩存中構建響應
            return MCPResponse.model_validate(cache_result.data)
        
        # 從進度緩存獲取
        progress_result = await progress_cache.get(command_id)
        if progress_result.success:
            progress_data = progress_result.data
            status_map = {
                "PENDING": CommandStatus.PENDING,
                "PROCESSING": CommandStatus.PROCESSING,
                "COMPLETED": CommandStatus.COMPLETED,
                "FAILED": CommandStatus.FAILED,
                "CANCELLED": CommandStatus.CANCELLED
            }
            
            return MCPResponse(
                command_id=command_id,
                status=status_map.get(progress_data["status"], CommandStatus.PROCESSING),
                progress_info={
                    "progress": progress_data["progress"],
                    "message": progress_data["message"],
                    "updated_at": progress_data["updated_at"]
                },
                created_at=datetime.now(),
                updated_at=progress_data["updated_at"]
            )
        
        # 從指令存儲獲取
        cmd_result = await command_storage.get_command(command_id)
        if not cmd_result.success:
            raise input_validation_error(
                message=f"找不到命令: {command_id}",
                error_code=ErrorCode.RESOURCE_NOT_FOUND,
                command_id=command_id
            )
            
        command_data = cmd_result.data
        
        # 返回基本狀態
        response_data = {
            "command_id": command_id,
            "status": command_data.get("status", "PENDING"),
        }
        
        # 如果有結果，添加到響應
        if "result" in command_data:
            response_data.update(command_data["result"])
        
        # 如果有錯誤，添加到響應
        if "error" in command_data:
            response_data["error"] = command_data["error"]
        
        # 返回響應
        return MCPResponse.model_validate(response_data)
        
    except MCPError as e:
        # 直接重新拋出MCPError
        raise
        
    except Exception as e:
        # 記錄錯誤
        logger.error(f"獲取命令狀態錯誤: {str(e)}", exc_info=True)
        raise system_error(
            message=f"獲取命令狀態失敗: {str(e)}",
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )


@app.post("/api/command/{command_id}/cancel")
async def cancel_command(command_id: str):
    """取消命令處理
    
    Args:
        command_id: 命令ID
        
    Returns:
        取消狀態
    """
    try:
        # 更新進度緩存
        await update_task_progress(command_id, "CANCELLED", 0, "任務已取消")
        
        # 更新指令狀態
        await command_storage.update_command_status(
            command_id,
            CommandStatus.CANCELLED,
            error="任務已被用戶取消"
        )
        
        # 取消實際任務
        coordinator = ModelCoordinator()
        cancel_result = coordinator.cancel_command(command_id)
        
        return {
            "success": True,
            "message": "任務已取消",
            "command_id": command_id
        }
        
    except Exception as e:
        # 記錄錯誤
        logger.error(f"取消命令錯誤: {str(e)}", exc_info=True)
        raise system_error(
            message=f"取消命令失敗: {str(e)}",
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )


@app.get("/api/command/{command_id}/progress")
async def get_command_progress(command_id: str):
    """獲取命令處理進度
    
    Args:
        command_id: 命令ID
        
    Returns:
        進度信息
    """
    try:
        # 從緩存中獲取進度
        progress_result = await progress_cache.get(command_id)
        
        if progress_result.success:
            progress_data = progress_result.data
            return {
                "command_id": command_id,
                "status": progress_data["status"],
                "progress": progress_data["progress"],
                "message": progress_data["message"],
                "updated_at": progress_data["updated_at"]
            }
        
        # 從指令存儲獲取
        cmd_result = await command_storage.get_command(command_id)
        if not cmd_result.success:
            raise input_validation_error(
                message=f"找不到命令: {command_id}",
                error_code=ErrorCode.RESOURCE_NOT_FOUND,
                command_id=command_id
            )
            
        command_data = cmd_result.data
        status = command_data.get("status", "UNKNOWN")
        
        # 根據狀態返回進度
        if status == "COMPLETED":
            return {
                "command_id": command_id,
                "status": "COMPLETED",
                "progress": 100,
                "message": "處理完成",
                "updated_at": command_data.get("updated_at", datetime.now())
            }
        elif status == "FAILED":
            return {
                "command_id": command_id,
                "status": "FAILED",
                "progress": 0,
                "message": f"處理失敗: {command_data.get('error', '未知錯誤')}",
                "updated_at": command_data.get("updated_at", datetime.now())
            }
        elif status == "CANCELLED":
            return {
                "command_id": command_id,
                "status": "CANCELLED",
                "progress": 0,
                "message": "任務已取消",
                "updated_at": command_data.get("updated_at", datetime.now())
            }
        else:
            return {
                "command_id": command_id,
                "status": status,
                "progress": 0,
                "message": "無進度信息",
                "updated_at": command_data.get("updated_at", datetime.now())
            }
            
    except MCPError as e:
        # 直接重新拋出MCPError
        raise
        
    except Exception as e:
        # 記錄錯誤
        logger.error(f"獲取命令進度錯誤: {str(e)}", exc_info=True)
        raise system_error(
            message=f"獲取命令進度失敗: {str(e)}",
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )


@app.get("/api/commands/history")
async def get_command_history(
    limit: int = 10,
    offset: int = 0,
    status: Optional[str] = None
):
    """獲取命令歷史
    
    Args:
        limit: 返回數量限制
        offset: 起始偏移
        status: 過濾狀態
        
    Returns:
        命令歷史列表
    """
    try:
        # 解析狀態過濾
        status_filter = None
        if status:
            if "," in status:
                status_filter = status.split(",")
            else:
                status_filter = status
        
        # 獲取指令歷史
        result = await command_storage.get_command_history(
            limit=limit,
            offset=offset,
            status=status_filter
        )
        
        if not result.success:
            raise storage_error(
                message=f"獲取命令歷史失敗: {result.message}",
                error_code=ErrorCode.STORAGE_READ_FAILURE
            )
        
        # 獲取總數
        total_count = await command_storage.count_commands(status=status_filter)
        
        return {
            "commands": result.data,
            "total": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except MCPError as e:
        # 直接重新拋出MCPError
        raise
        
    except Exception as e:
        # 記錄錯誤
        logger.error(f"獲取命令歷史錯誤: {str(e)}", exc_info=True)
        raise system_error(
            message=f"獲取命令歷史失敗: {str(e)}",
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )


@app.get("/api/tasks/active")
async def get_active_tasks():
    """獲取當前活躍任務列表
    
    Returns:
        活躍任務列表
    """
    # 返回所有活躍任務
    return {
        "active_tasks": list(active_tasks.values()),
        "count": len(active_tasks)
    }


@app.get("/api/system/status")
async def get_system_status():
    """獲取系統狀態
    
    Returns:
        系統狀態信息
    """
    try:
        # 獲取各種命令數量
        pending_count = await command_storage.count_commands(status="PENDING")
        processing_count = await command_storage.count_commands(status="PROCESSING")
        completed_count = await command_storage.count_commands(status="COMPLETED")
        failed_count = await command_storage.count_commands(status="FAILED")
        cancelled_count = await command_storage.count_commands(status="CANCELLED")
        
        # 系統信息
        system_info = {
            "version": "1.0.0",
            "uptime": "Unknown",  # 實際應用中可以記錄啟動時間
            "active_tasks": len(active_tasks),
            "command_stats": {
                "pending": pending_count,
                "processing": processing_count,
                "completed": completed_count,
                "failed": failed_count,
                "cancelled": cancelled_count,
                "total": pending_count + processing_count + completed_count + failed_count + cancelled_count
            }
        }
        
        return system_info
        
    except Exception as e:
        # 記錄錯誤
        logger.error(f"獲取系統狀態錯誤: {str(e)}", exc_info=True)
        raise system_error(
            message=f"獲取系統狀態失敗: {str(e)}",
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )


# 音頻處理相關端點

@app.post("/api/audio/upload")
async def upload_audio(audio: UploadFile = File(...)):
    """上傳音頻文件
    
    Args:
        audio: 上傳的音頻文件
        
    Returns:
        處理結果及文件ID
    """
    try:
        # 創建臨時目錄存儲上傳的文件
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, f"upload_{generate_id()}.webm")
        
        # 保存上傳的文件
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
        
        # 生成文件ID
        file_id = generate_id()
        
        # 實際項目中，這裡可能需要將文件移動到永久存儲位置
        target_dir = os.path.join("data", "audio")
        os.makedirs(target_dir, exist_ok=True)
        target_path = os.path.join(target_dir, f"{file_id}.webm")
        shutil.copy(temp_file_path, target_path)
        
        logger.info(f"音頻文件已上傳，ID：{file_id}，路徑：{target_path}")
        
        return {
            "success": True,
            "file_id": file_id,
            "message": "音頻上傳成功"
        }
        
    except Exception as e:
        logger.error(f"音頻上傳失敗: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"音頻上傳失敗: {str(e)}"
        )
    finally:
        # 清理臨時目錄
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir, ignore_errors=True)


@app.post("/api/audio/correct-pitch")
async def correct_pitch(audio: UploadFile = File(...)):
    """校正音頻音高
    
    Args:
        audio: 上傳的音頻文件
        
    Returns:
        校正後的音頻文件
    """
    if basic_pitch_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="音高校正服務不可用，可能缺少必要的依賴庫"
        )
        
    try:
        # 創建臨時目錄存儲上傳的文件
        temp_dir = tempfile.mkdtemp()
        input_path = os.path.join(temp_dir, f"input_{generate_id()}.webm")
        output_path = os.path.join(temp_dir, f"output_{generate_id()}.wav")
        
        # 保存上傳的文件
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
        
        # 使用 Basic Pitch 服務進行音高校正
        try:
            corrected_path = basic_pitch_service.correct_pitch(
                audio_file_path=input_path,
                output_path=output_path
            )
            
            logger.info(f"音高校正成功，輸出文件：{corrected_path}")
            
            # 返回校正後的音頻文件
            return FileResponse(
                path=corrected_path,
                media_type="audio/wav",
                filename="pitch_corrected.wav"
            )
            
        except Exception as e:
            logger.error(f"音高校正失敗: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"音高校正失敗: {str(e)}"
            )
        
    except Exception as e:
        logger.error(f"處理請求失敗: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"處理請求失敗: {str(e)}"
        )
    finally:
        # 清理臨時目錄
        if 'temp_dir' in locals():
            # 延遲一點時間清理，確保文件已經被返回
            asyncio.create_task(delayed_cleanup(temp_dir))


@app.post("/api/audio/analyze")
async def analyze_audio(audio: UploadFile = File(...)):
    """分析音頻文件
    
    Args:
        audio: 上傳的音頻文件
        
    Returns:
        分析結果
    """
    if audio_processor is None or basic_pitch_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="音頻分析服務不可用，可能缺少必要的依賴庫"
        )
        
    try:
        # 創建臨時目錄存儲上傳的文件
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, f"analyze_{generate_id()}.webm")
        
        # 保存上傳的文件
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
        
        # 分析音頻
        try:
            import librosa
            import numpy as np
            
            # 加載音頻
            y, sr = librosa.load(temp_file_path, sr=None)
            
            # 使用音頻處理器分析
            analysis_results = audio_processor.analyze_audio(audio_data=y, sample_rate=sr)
            
            # 檢查是否有錯誤
            if 'error' in analysis_results:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=analysis_results['error']
                )
            
            # 提取主要信息，避免返回過大的數據
            simplified_results = {
                "tempo": analysis_results["rhythm"]["tempo"],
                "key": basic_pitch_service.detect_key(temp_file_path),
                "pitches": [],
                "rhythm_complexity": analysis_results["rhythm"]["pattern"]["complexity"]
            }
            
            logger.info(f"音頻分析成功，速度：{simplified_results['tempo']} BPM，調性：{simplified_results['key']}")
            
            return {
                "success": True,
                "analysis": simplified_results
            }
        except ImportError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"音頻分析服務缺少必要的依賴庫: {str(e)}"
            )
        
    except HTTPException:
        # 重新拋出HTTP異常
        raise
    except Exception as e:
        logger.error(f"音頻分析失敗: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"音頻分析失敗: {str(e)}"
        )
    finally:
        # 清理臨時目錄
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir, ignore_errors=True)


@app.post("/api/audio/to-midi")
async def audio_to_midi(audio: UploadFile = File(...)):
    """將音頻轉換為MIDI
    
    Args:
        audio: 上傳的音頻文件
        
    Returns:
        轉換後的MIDI文件
    """
    if basic_pitch_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="音頻轉MIDI服務不可用，可能缺少必要的依賴庫"
        )
        
    try:
        # 創建臨時目錄存儲上傳的文件
        temp_dir = tempfile.mkdtemp()
        input_path = os.path.join(temp_dir, f"input_{generate_id()}.webm")
        output_path = os.path.join(temp_dir, f"output_{generate_id()}.mid")
        
        # 保存上傳的文件
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
        
        # 使用 Basic Pitch 服務轉換為 MIDI
        try:
            midi_path = basic_pitch_service.audio_to_midi(
                audio_file_path=input_path,
                output_midi_path=output_path
            )
            
            logger.info(f"音頻轉換為MIDI成功，輸出文件：{midi_path}")
            
            # 返回MIDI文件
            return FileResponse(
                path=midi_path,
                media_type="audio/midi",
                filename="converted.mid"
            )
            
        except ImportError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"音頻轉MIDI服務缺少必要的依賴庫: {str(e)}"
            )
        except Exception as e:
            logger.error(f"音頻轉換失敗: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"音頻轉換失敗: {str(e)}"
            )
        
    except HTTPException:
        # 重新拋出HTTP異常
        raise
    except Exception as e:
        logger.error(f"處理請求失敗: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"處理請求失敗: {str(e)}"
        )
    finally:
        # 清理臨時目錄
        if 'temp_dir' in locals():
            # 延遲一點時間清理，確保文件已經被返回
            asyncio.create_task(delayed_cleanup(temp_dir))


@app.post("/api/audio/generate-chords")
async def generate_chords(audio: UploadFile = File(...), 
                         style: str = Form("pop"), 
                         complexity: int = Form(3)):
    """根據音頻生成和弦進行
    
    Args:
        audio: 上傳的音頻文件
        style: 音樂風格
        complexity: 複雜度（1-5）
        
    Returns:
        生成的和弦進行
    """
    if basic_pitch_service is None or chord_generator is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="和弦生成服務不可用，可能缺少必要的依賴庫"
        )
        
    try:
        # 創建臨時目錄存儲上傳的文件
        temp_dir = tempfile.mkdtemp()
        input_path = os.path.join(temp_dir, f"input_{generate_id()}.webm")
        
        # 保存上傳的文件
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
        
        # 從音頻提取旋律
        try:
            melody_input = basic_pitch_service.audio_to_melody(input_path)
            
            # 生成和弦進行
            chord_progression = chord_generator.generate_chords(
                melody=melody_input,
                style=style,
                complexity=complexity
            )
            
            logger.info(f"成功為音頻生成和弦進行，共 {len(chord_progression)} 個和弦")
            
            return {
                "success": True,
                "chord_progression": chord_progression
            }
            
        except ImportError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"和弦生成服務缺少必要的依賴庫: {str(e)}"
            )
        except Exception as e:
            logger.error(f"和弦生成失敗: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"和弦生成失敗: {str(e)}"
            )
        
    except HTTPException:
        # 重新拋出HTTP異常
        raise
    except Exception as e:
        logger.error(f"處理請求失敗: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"處理請求失敗: {str(e)}"
        )
    finally:
        # 清理臨時目錄
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir, ignore_errors=True)


@app.post("/api/audio/generate-accompaniment")
async def generate_accompaniment(audio: UploadFile = File(...), 
                                style: str = Form("pop"), 
                                complexity: int = Form(3),
                                return_midi: bool = Form(False)):
    """生成多軌伴奏
    
    Args:
        audio: 上傳的音頻文件
        style: 音樂風格
        complexity: 複雜度（1-5）
        return_midi: 是否返回MIDI文件
        
    Returns:
        生成的伴奏軌道或MIDI文件
    """
    if basic_pitch_service is None or accompaniment_generator is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="伴奏生成服務不可用，可能缺少必要的依賴庫"
        )
        
    try:
        # 創建臨時目錄存儲上傳的文件
        temp_dir = tempfile.mkdtemp()
        input_path = os.path.join(temp_dir, f"input_{generate_id()}.webm")
        output_path = os.path.join(temp_dir, f"accompaniment_{generate_id()}.mid")
        
        # 保存上傳的文件
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
        
        # 從音頻提取旋律
        try:
            melody_input = basic_pitch_service.audio_to_melody(input_path)
            
            # 生成伴奏
            accompaniment = accompaniment_generator.generate_accompaniment(
                melody=melody_input,
                style=style,
                complexity=complexity
            )
            
            if return_midi:
                try:
                    # 創建MIDI文件
                    from music21 import midi
                    from music21 import note as m21_note
                    import music21
                    
                    # 創建MIDI文件
                    midi_file = midi.MidiFile()
                    
                    # 添加軌道
                    melody_track = midi.MidiTrack(0)
                    midi_file.tracks.append(melody_track)
                    
                    # 為旋律添加音符
                    for note_obj in melody_input.notes:
                        midi_note = m21_note.Note()
                        midi_note.pitch.midi = note_obj.pitch
                        midi_note.duration = music21.duration.Duration(note_obj.duration)
                        midi_note.offset = note_obj.start_time
                        melody_track.events.append(midi_note.pitch)
                    
                    # 為伴奏的每個軌道添加音符
                    track_index = 1
                    for track_name, notes in accompaniment["tracks"].items():
                        track = midi.MidiTrack(track_index)
                        midi_file.tracks.append(track)
                        
                        for note_data in notes:
                            midi_note = m21_note.Note()
                            midi_note.pitch.midi = note_data["pitch"]
                            midi_note.duration = music21.duration.Duration(note_data["duration"])
                            midi_note.offset = note_data["start_time"]
                            track.events.append(midi_note.pitch)
                        
                        track_index += 1
                    
                    # 保存MIDI文件
                    midi_file.write(output_path)
                    
                    logger.info(f"成功生成伴奏MIDI文件: {output_path}")
                    
                    # 返回MIDI文件
                    return FileResponse(
                        path=output_path,
                        media_type="audio/midi",
                        filename="accompaniment.mid"
                    )
                except ImportError as e:
                    logger.error(f"MIDI生成失敗，可能缺少music21: {str(e)}")
                    # 如果MIDI生成失敗，退回到返回JSON數據
                    return {
                        "success": True,
                        "accompaniment": accompaniment,
                        "error": f"MIDI生成失敗，將返回JSON數據: {str(e)}"
                    }
            else:
                # 返回JSON數據
                logger.info(f"成功生成伴奏，共 {len(accompaniment['tracks'])} 個軌道")
                
                return {
                    "success": True,
                    "accompaniment": accompaniment
                }
            
        except ImportError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"伴奏生成服務缺少必要的依賴庫: {str(e)}"
            )
        except Exception as e:
            logger.error(f"伴奏生成失敗: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"伴奏生成失敗: {str(e)}"
            )
        
    except HTTPException:
        # 重新拋出HTTP異常
        raise
    except Exception as e:
        logger.error(f"處理請求失敗: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"處理請求失敗: {str(e)}"
        )
    finally:
        # 清理臨時目錄
        if 'temp_dir' in locals() and not return_midi:
            shutil.rmtree(temp_dir, ignore_errors=True)
        elif return_midi and 'temp_dir' in locals():
            # 延遲清理，確保文件已經被傳送
            asyncio.create_task(delayed_cleanup(temp_dir))


async def delayed_cleanup(directory_path, delay_seconds=5):
    """延遲清理目錄
    
    Args:
        directory_path: 要清理的目錄路徑
        delay_seconds: 延遲秒數
    """
    await asyncio.sleep(delay_seconds)
    try:
        shutil.rmtree(directory_path, ignore_errors=True)
        logger.debug(f"已清理臨時目錄: {directory_path}")
    except Exception as e:
        logger.error(f"清理臨時目錄失敗: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=config.get("server.host", "127.0.0.1"),
        port=config.get("server.port", 8000),
        reload=config.get("server.reload", True)
    )