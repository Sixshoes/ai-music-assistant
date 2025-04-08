"""錯誤類型模組

定義系統中可能出現的各種錯誤類型和處理方法
"""

from enum import Enum
from typing import Dict, Any, Optional, List


class ErrorSeverity(Enum):
    """錯誤嚴重程度枚舉"""
    INFO = "info"           # 僅供信息，不影響正常運行
    WARNING = "warning"     # 警告，可能影響結果但不阻止執行
    ERROR = "error"         # 錯誤，可能導致特定功能失敗
    CRITICAL = "critical"   # 嚴重錯誤，導致整個操作失敗


class ErrorCategory(Enum):
    """錯誤類別枚舉"""
    INPUT_VALIDATION = "input_validation"  # 輸入驗證錯誤
    PERMISSION = "permission"              # 權限或授權錯誤
    RESOURCE = "resource"                  # 資源不可用或耗盡
    MODEL = "model"                        # 模型相關錯誤
    PROCESSING = "processing"              # 處理過程中的錯誤
    STORAGE = "storage"                    # 儲存相關錯誤
    NETWORK = "network"                    # 網絡連接錯誤
    SYSTEM = "system"                      # 系統級錯誤
    UNKNOWN = "unknown"                    # 未知錯誤


class ErrorCode(Enum):
    """詳細錯誤代碼枚舉"""
    # 輸入驗證錯誤
    INVALID_INPUT_FORMAT = "invalid_input_format"  # 輸入格式無效
    MISSING_REQUIRED_FIELD = "missing_required_field"  # 缺少必要字段
    INVALID_PARAMETER_VALUE = "invalid_parameter_value"  # 參數值無效
    UNSUPPORTED_COMMAND_TYPE = "unsupported_command_type"  # 不支持的命令類型
    
    # 權限錯誤
    UNAUTHORIZED_ACCESS = "unauthorized_access"  # 未授權訪問
    INSUFFICIENT_PERMISSIONS = "insufficient_permissions"  # 權限不足
    
    # 資源錯誤
    RESOURCE_NOT_FOUND = "resource_not_found"  # 資源未找到
    RESOURCE_EXHAUSTED = "resource_exhausted"  # 資源耗盡
    MODEL_UNAVAILABLE = "model_unavailable"  # 模型不可用
    
    # 模型錯誤
    MODEL_LOAD_FAILURE = "model_load_failure"  # 模型加載失敗
    MODEL_EXECUTION_FAILURE = "model_execution_failure"  # 模型執行失敗
    
    # 處理錯誤
    PROCESSING_TIMEOUT = "processing_timeout"  # 處理超時
    TASK_CANCELLED = "task_cancelled"  # 任務被取消
    WORKFLOW_FAILURE = "workflow_failure"  # 工作流失敗
    
    # 存儲錯誤
    STORAGE_WRITE_FAILURE = "storage_write_failure"  # 儲存寫入失敗
    STORAGE_READ_FAILURE = "storage_read_failure"  # 儲存讀取失敗
    DATABASE_CONNECTION_ERROR = "database_connection_error"  # 數據庫連接錯誤
    
    # 網絡錯誤
    NETWORK_CONNECTION_ERROR = "network_connection_error"  # 網絡連接錯誤
    API_REQUEST_FAILURE = "api_request_failure"  # API請求失敗
    
    # 系統錯誤
    INTERNAL_SERVER_ERROR = "internal_server_error"  # 內部服務器錯誤
    CONFIGURATION_ERROR = "configuration_error"  # 配置錯誤
    
    # 未知錯誤
    UNKNOWN_ERROR = "unknown_error"  # 未知錯誤


class MCPError(Exception):
    """MCP 系統錯誤基類"""
    
    def __init__(
        self, 
        message: str, 
        error_code: ErrorCode, 
        error_category: ErrorCategory = None, 
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        details: Dict[str, Any] = None,
        recovery_hints: List[str] = None,
        command_id: str = None
    ):
        """初始化錯誤
        
        Args:
            message: 錯誤消息
            error_code: 錯誤代碼
            error_category: 錯誤類別，如果未指定將從錯誤代碼自動判斷
            severity: 錯誤嚴重程度
            details: 錯誤詳情
            recovery_hints: 錯誤恢復提示
            command_id: 相關命令ID
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        
        # 如果未指定錯誤類別，根據錯誤代碼自動判斷
        if error_category is None:
            self.error_category = self._determine_category(error_code)
        else:
            self.error_category = error_category
            
        self.severity = severity
        self.details = details or {}
        self.recovery_hints = recovery_hints or []
        self.command_id = command_id
    
    def _determine_category(self, error_code: ErrorCode) -> ErrorCategory:
        """根據錯誤代碼確定錯誤類別
        
        Args:
            error_code: 錯誤代碼
            
        Returns:
            對應的錯誤類別
        """
        code_str = error_code.value
        
        if code_str.startswith("invalid_") or code_str.startswith("missing_") or code_str == "unsupported_command_type":
            return ErrorCategory.INPUT_VALIDATION
        elif code_str.endswith("_permissions") or code_str.startswith("unauthorized"):
            return ErrorCategory.PERMISSION
        elif code_str.endswith("_not_found") or code_str.endswith("_exhausted") or code_str.endswith("_unavailable"):
            return ErrorCategory.RESOURCE
        elif code_str.startswith("model_"):
            return ErrorCategory.MODEL
        elif code_str.endswith("_timeout") or code_str.endswith("_cancelled") or code_str.endswith("_failure"):
            return ErrorCategory.PROCESSING
        elif code_str.startswith("storage_") or code_str.startswith("database_"):
            return ErrorCategory.STORAGE
        elif code_str.startswith("network_") or code_str.startswith("api_"):
            return ErrorCategory.NETWORK
        elif code_str == "internal_server_error" or code_str == "configuration_error":
            return ErrorCategory.SYSTEM
        else:
            return ErrorCategory.UNKNOWN
    
    def to_dict(self) -> Dict[str, Any]:
        """將錯誤轉換為字典表示
        
        Returns:
            錯誤的字典表示
        """
        return {
            "message": self.message,
            "error_code": self.error_code.value,
            "error_category": self.error_category.value,
            "severity": self.severity.value,
            "details": self.details,
            "recovery_hints": self.recovery_hints,
            "command_id": self.command_id
        }
    
    def get_http_status_code(self) -> int:
        """獲取對應的HTTP狀態碼
        
        Returns:
            適合的HTTP狀態碼
        """
        category_status_map = {
            ErrorCategory.INPUT_VALIDATION: 400,  # Bad Request
            ErrorCategory.PERMISSION: 403,        # Forbidden
            ErrorCategory.RESOURCE: 404,          # Not Found
            ErrorCategory.MODEL: 500,             # Internal Server Error
            ErrorCategory.PROCESSING: 500,        # Internal Server Error
            ErrorCategory.STORAGE: 500,           # Internal Server Error
            ErrorCategory.NETWORK: 502,           # Bad Gateway
            ErrorCategory.SYSTEM: 500,            # Internal Server Error
            ErrorCategory.UNKNOWN: 500            # Internal Server Error
        }
        
        # 特別處理某些錯誤代碼
        code_status_map = {
            ErrorCode.RESOURCE_NOT_FOUND: 404,               # Not Found
            ErrorCode.PROCESSING_TIMEOUT: 408,               # Request Timeout
            ErrorCode.UNAUTHORIZED_ACCESS: 401,              # Unauthorized
            ErrorCode.MODEL_UNAVAILABLE: 503,                # Service Unavailable
            ErrorCode.TASK_CANCELLED: 499                    # Client Closed Request
        }
        
        # 首先檢查特定錯誤代碼
        if self.error_code in code_status_map:
            return code_status_map[self.error_code]
        
        # 然後根據錯誤類別返回狀態碼
        return category_status_map.get(self.error_category, 500)


# 特定錯誤類型 - 為了方便使用而定義的工廠函數

def input_validation_error(
    message: str, 
    error_code: ErrorCode = ErrorCode.INVALID_INPUT_FORMAT,
    details: Dict[str, Any] = None,
    command_id: str = None
) -> MCPError:
    """創建輸入驗證錯誤
    
    Args:
        message: 錯誤消息
        error_code: 具體錯誤代碼
        details: 錯誤詳情
        command_id: 相關命令ID
        
    Returns:
        MCPError實例
    """
    return MCPError(
        message=message,
        error_code=error_code,
        error_category=ErrorCategory.INPUT_VALIDATION,
        severity=ErrorSeverity.ERROR,
        details=details,
        recovery_hints=["請檢查輸入數據格式和參數值是否正確"],
        command_id=command_id
    )

def model_error(
    message: str, 
    error_code: ErrorCode = ErrorCode.MODEL_EXECUTION_FAILURE,
    details: Dict[str, Any] = None,
    command_id: str = None
) -> MCPError:
    """創建模型錯誤
    
    Args:
        message: 錯誤消息
        error_code: 具體錯誤代碼
        details: 錯誤詳情
        command_id: 相關命令ID
        
    Returns:
        MCPError實例
    """
    return MCPError(
        message=message,
        error_code=error_code,
        error_category=ErrorCategory.MODEL,
        severity=ErrorSeverity.ERROR,
        details=details,
        recovery_hints=["請稍後重試", "嘗試使用不同的模型參數"],
        command_id=command_id
    )

def storage_error(
    message: str, 
    error_code: ErrorCode = ErrorCode.STORAGE_WRITE_FAILURE,
    details: Dict[str, Any] = None,
    command_id: str = None
) -> MCPError:
    """創建存儲錯誤
    
    Args:
        message: 錯誤消息
        error_code: 具體錯誤代碼
        details: 錯誤詳情
        command_id: 相關命令ID
        
    Returns:
        MCPError實例
    """
    return MCPError(
        message=message,
        error_code=error_code,
        error_category=ErrorCategory.STORAGE,
        severity=ErrorSeverity.ERROR,
        details=details,
        recovery_hints=["請檢查存儲空間是否足夠", "檢查文件或數據庫權限"],
        command_id=command_id
    )

def system_error(
    message: str, 
    error_code: ErrorCode = ErrorCode.INTERNAL_SERVER_ERROR,
    details: Dict[str, Any] = None,
    command_id: str = None
) -> MCPError:
    """創建系統錯誤
    
    Args:
        message: 錯誤消息
        error_code: 具體錯誤代碼
        details: 錯誤詳情
        command_id: 相關命令ID
        
    Returns:
        MCPError實例
    """
    return MCPError(
        message=message,
        error_code=error_code,
        error_category=ErrorCategory.SYSTEM,
        severity=ErrorSeverity.CRITICAL,
        details=details,
        recovery_hints=["請聯繫系統管理員", "查看系統日誌獲取更多信息"],
        command_id=command_id
    ) 