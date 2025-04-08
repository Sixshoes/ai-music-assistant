#!/bin/bash

# 音樂工具啟動腳本
# 用於啟動音樂工具命令行介面

# 檢查 Python 環境
if ! command -v python3 &> /dev/null; then
    echo "錯誤: 找不到 Python 3。請安裝 Python 3.8 或更高版本。"
    exit 1
fi

# 檢查虛擬環境
if [ ! -d "venv" ]; then
    echo "未找到虛擬環境。設置中..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r backend/requirements.txt
else
    source venv/bin/activate
fi

# 設置 Python 路徑
export PYTHONPATH=$PYTHONPATH:$(pwd)

# 使用命令行參數運行 music_tools_cli.py
python -m backend.mcp.music_tools_cli "$@" 