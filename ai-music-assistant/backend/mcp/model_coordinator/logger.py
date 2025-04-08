"""日誌設置模組

提供日誌配置和初始化功能
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logger(name: str, log_dir: str = "logs") -> logging.Logger:
    """設置日誌記錄器
    
    Args:
        name: 日誌記錄器名稱
        log_dir: 日誌文件目錄
        
    Returns:
        配置好的日誌記錄器
    """
    # 創建日誌目錄
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 創建日誌記錄器
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # 檢查是否已經有處理器，避免重複添加
    if not logger.handlers:
        # 創建控制台處理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # 創建文件處理器
        file_handler = RotatingFileHandler(
            log_dir / f"{name}.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

__all__ = ['setup_logger'] 