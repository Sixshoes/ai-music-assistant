"""錯誤類型模組

定義系統中使用的錯誤類型和錯誤處理功能
"""

from enum import Enum
from typing import Dict, Any, Optional, Union, List
from fastapi import status


class ErrorCategory(str, Enum):
    """錯誤類別枚舉"""
    SYSTEM = "system"
    INPUT = "input"
    MODEL = "model"
    STORAGE = "storage"
    NETWORK = "network"
    UNKNOWN = "unknown"


class ErrorSeverity(str, Enum):
    """錯誤嚴重性枚舉"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ErrorCode(str, Enum):
    """錯誤代碼枚舉"""
    # 系統錯誤 (1000-1999)
    INTERNAL_SERVER_ERROR = "1000"
    CONFIGURATION_ERROR = "1001"
    DEPENDENCY_ERROR = "1002"
    RESOURCE_EXHAUSTED = "1003"
    TIMEOUT = "1004"
    
    # 輸入錯誤 (2000-2999)
    INVALID_INPUT = "2000"
    MISSING_REQUIRED_FIELD = "2001"
    INVALID_FORMAT = "2002"
    UNSUPPORTED_OPERATION = "2003"
    RESOURCE_NOT_FOUND = "2004"
    
    # 模型錯誤 (3000-3999)
    MODEL_INITIALIZATION_ERROR = "3000"
    MODEL_EXECUTION_ERROR = "3001"
    MODEL_NOT_AVAILABLE = "3002"
    MODEL_OUTPUT_ERROR = "3003"
    
    # 存儲錯誤 (4000-4999)
    STORAGE_READ_FAILURE = "4000"
    STORAGE_WRITE_FAILURE = "4001"
    STORAGE_DELETE_FAILURE = "4002"
    
    # 網路錯誤 (5000-5999)
    NETWORK_ERROR = "5000"
    API_ERROR = "5001"
    RATE_LIMIT_EXCEEDED = "5002"
    
    # 未知錯誤 (9000-9999)
    UNKNOWN_ERROR = "9000"


class MCPError(Exception):
    """MCP 錯誤基類"""
    
    def __init__(self, 
                message: str, 
                error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
                error_category: ErrorCategory = ErrorCategory.UNKNOWN,
                error_severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                details: Optional[Dict[str, Any]] = None,
                command_id: Optional[str] = None):
        """初始化 MCP 錯誤
        
        Args:
            message: 錯誤消息
            error_code: 錯誤代碼
            error_category: 錯誤類別
            error_severity: 錯誤嚴重性
            details: 詳細信息
            command_id: 相關指令 ID
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.error_category = error_category
        self.error_severity = error_severity
        self.details = details or {}
        self.command_id = command_id
    
    def to_dict(self) -> Dict[str, Any]:
        """將錯誤轉換為字典
        
        Returns:
            Dict[str, Any]: 錯誤字典
        """
        return {
            "error": {
                "message": self.message,
                "code": self.error_code.value,
                "category": self.error_category.value,
                "severity": self.error_severity.value,
                "details": self.details,
                "command_id": self.command_id
            }
        }
    
    def get_http_status_code(self) -> int:
        """獲取對應的 HTTP 狀態碼
        
        Returns:
            int: HTTP 狀態碼
        """
        # 根據錯誤類別和代碼返回適當的 HTTP 狀態碼
        category_map = {
            ErrorCategory.SYSTEM: status.HTTP_500_INTERNAL_SERVER_ERROR,
            ErrorCategory.INPUT: status.HTTP_400_BAD_REQUEST,
            ErrorCategory.MODEL: status.HTTP_500_INTERNAL_SERVER_ERROR,
            ErrorCategory.STORAGE: status.HTTP_500_INTERNAL_SERVER_ERROR,
            ErrorCategory.NETWORK: status.HTTP_503_SERVICE_UNAVAILABLE,
            ErrorCategory.UNKNOWN: status.HTTP_500_INTERNAL_SERVER_ERROR
        }
        
        # 特殊情況處理
        if self.error_code == ErrorCode.RESOURCE_NOT_FOUND:
            return status.HTTP_404_NOT_FOUND
        
        return category_map.get(self.error_category, status.HTTP_500_INTERNAL_SERVER_ERROR)


# 工廠函數
def input_validation_error(message: str, 
                          error_code: ErrorCode = ErrorCode.INVALID_INPUT, 
                          details: Optional[Dict[str, Any]] = None,
                          command_id: Optional[str] = None) -> MCPError:
    """創建輸入驗證錯誤
    
    Args:
        message: 錯誤消息
        error_code: 錯誤代碼
        details: 詳細信息
        command_id: 指令 ID
        
    Returns:
        MCPError: 輸入驗證錯誤
    """
    return MCPError(
        message=message,
        error_code=error_code,
        error_category=ErrorCategory.INPUT,
        error_severity=ErrorSeverity.MEDIUM,
        details=details,
        command_id=command_id
    )


def model_error(message: str, 
               error_code: ErrorCode = ErrorCode.MODEL_EXECUTION_ERROR, 
               details: Optional[Dict[str, Any]] = None,
               command_id: Optional[str] = None) -> MCPError:
    """創建模型錯誤
    
    Args:
        message: 錯誤消息
        error_code: 錯誤代碼
        details: 詳細信息
        command_id: 指令 ID
        
    Returns:
        MCPError: 模型錯誤
    """
    return MCPError(
        message=message,
        error_code=error_code,
        error_category=ErrorCategory.MODEL,
        error_severity=ErrorSeverity.HIGH,
        details=details,
        command_id=command_id
    )


def storage_error(message: str, 
                 error_code: ErrorCode = ErrorCode.STORAGE_WRITE_FAILURE, 
                 details: Optional[Dict[str, Any]] = None,
                 command_id: Optional[str] = None) -> MCPError:
    """創建存儲錯誤
    
    Args:
        message: 錯誤消息
        error_code: 錯誤代碼
        details: 詳細信息
        command_id: 指令 ID
        
    Returns:
        MCPError: 存儲錯誤
    """
    return MCPError(
        message=message,
        error_code=error_code,
        error_category=ErrorCategory.STORAGE,
        error_severity=ErrorSeverity.HIGH,
        details=details,
        command_id=command_id
    )


def system_error(message: str, 
                error_code: ErrorCode = ErrorCode.INTERNAL_SERVER_ERROR, 
                details: Optional[Dict[str, Any]] = None,
                command_id: Optional[str] = None) -> MCPError:
    """創建系統錯誤
    
    Args:
        message: 錯誤消息
        error_code: 錯誤代碼
        details: 詳細信息
        command_id: 指令 ID
        
    Returns:
        MCPError: 系統錯誤
    """
    return MCPError(
        message=message,
        error_code=error_code,
        error_category=ErrorCategory.SYSTEM,
        error_severity=ErrorSeverity.CRITICAL,
        details=details,
        command_id=command_id
    )


def network_error(message: str, 
                 error_code: ErrorCode = ErrorCode.NETWORK_ERROR, 
                 details: Optional[Dict[str, Any]] = None,
                 command_id: Optional[str] = None) -> MCPError:
    """創建網路錯誤
    
    Args:
        message: 錯誤消息
        error_code: 錯誤代碼
        details: 詳細信息
        command_id: 指令 ID
        
    Returns:
        MCPError: 網路錯誤
    """
    return MCPError(
        message=message,
        error_code=error_code,
        error_category=ErrorCategory.NETWORK,
        error_severity=ErrorSeverity.HIGH,
        details=details,
        command_id=command_id
    ) 