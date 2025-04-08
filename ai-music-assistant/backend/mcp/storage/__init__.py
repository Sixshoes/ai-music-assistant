"""存儲模塊

提供持久化儲存和緩存功能
"""

from .persistence import (
    PersistenceStorage, 
    StorageResult, 
    StorageFactory,
    generate_id
)
from .json_storage import JSONStorage
from .sqlite_storage import SQLiteStorage
from .command_storage import CommandStorage
from .cache_service import CacheService

__all__ = [
    "PersistenceStorage",
    "StorageResult",
    "StorageFactory",
    "generate_id",
    "JSONStorage",
    "SQLiteStorage",
    "CommandStorage",
    "CacheService"
] 