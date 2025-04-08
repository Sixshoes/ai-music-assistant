#!/bin/bash

# 顯示歡迎訊息
echo "======================================================"
echo "       AI 音樂創作助手 - 開發環境啟動腳本"
echo "======================================================"

# 定義顏色
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 設置環境變數
export AI_MUSIC_HOME=$(pwd)
export PYTHONPATH=$PYTHONPATH:$AI_MUSIC_HOME
export LOG_LEVEL="INFO"
export AI_MODEL_PATH="$AI_MUSIC_HOME/models"
export TEMP_DIR="$AI_MUSIC_HOME/backend/temp"
export MIDI_SOUNDFONT="$AI_MUSIC_HOME/backend/soundfonts/FluidR3_GM.sf2"

# 建立配置文件（如果不存在）
if [ ! -f .env ]; then
    echo -e "${YELLOW}創建默認環境配置文件...${NC}"
    cat > .env << EOF
# AI音樂創作助手配置
AI_MUSIC_HOME=$(pwd)
PYTHONPATH=$PYTHONPATH:$AI_MUSIC_HOME
LOG_LEVEL=INFO
AI_MODEL_PATH=$AI_MUSIC_HOME/models
TEMP_DIR=$AI_MUSIC_HOME/backend/temp
MIDI_SOUNDFONT=$AI_MUSIC_HOME/backend/soundfonts/FluidR3_GM.sf2
PORT=8000
FRONTEND_PORT=3000
EOF
    echo -e "${GREEN}配置文件 .env 已創建${NC}"
fi

# 加載環境變數
source .env

# 確保目錄結構
mkdir -p backend/logs
mkdir -p backend/temp
mkdir -p backend/static
mkdir -p backend/soundfonts
mkdir -p backend/fonts
mkdir -p models
mkdir -p frontend/public

# 檢查soundfont文件
if [ ! -f "$MIDI_SOUNDFONT" ]; then
    echo -e "${YELLOW}下載SoundFont文件...${NC}"
    curl -L -o backend/soundfonts/FluidR3_GM.sf2 "https://archive.org/download/fluidr3-gm-gs/FluidR3_GM.sf2"
    echo -e "${GREEN}SoundFont下載完成${NC}"
fi

# 確保Python虛擬環境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}創建Python虛擬環境...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}虛擬環境已創建${NC}"
fi

# 激活虛擬環境
source venv/bin/activate

# 安裝依賴
echo -e "${YELLOW}安裝後端依賴...${NC}"
pip install -r backend/requirements.txt

# 檢查字體文件
if [ ! -f "backend/fonts/FreeSans.ttf" ]; then
    echo -e "${YELLOW}下載字體文件...${NC}"
    curl -L -o backend/fonts/FreeSans.ttf "https://github.com/adobe-fonts/source-sans-pro/raw/release/TTF/SourceSansPro-Regular.ttf"
    echo -e "${GREEN}字體下載完成${NC}"
fi

# 檢查端口佔用
echo -e "${YELLOW}檢查端口佔用情況...${NC}"
PORT_CHECK=$(lsof -i :$PORT | grep LISTEN)
if [ ! -z "$PORT_CHECK" ]; then
    echo -e "${RED}端口 $PORT 已被佔用，正在終止相關進程...${NC}"
    lsof -i :$PORT | grep LISTEN | awk '{print $2}' | xargs kill -9
    echo -e "${GREEN}進程已終止${NC}"
fi

# 後端啟動提示
echo -e "${GREEN}啟動後端服務 (端口: $PORT)...${NC}"

# 根據參數決定運行模式
if [ "$1" == "frontend" ]; then
    # 後台啟動後端
    cd backend
    nohup python main.py > logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo -e "${GREEN}後端服務已在後台啟動 (PID: $BACKEND_PID)${NC}"
    
    # 啟動前端
    cd ../frontend
    echo -e "${YELLOW}安裝前端依賴...${NC}"
    npm install
    echo -e "${GREEN}啟動前端服務 (端口: $FRONTEND_PORT)...${NC}"
    npm run dev
elif [ "$1" == "backend" ]; then
    # 只啟動後端
    cd backend
    python main.py
else
    # 啟動開發伺服器
    cd backend
    python main.py 