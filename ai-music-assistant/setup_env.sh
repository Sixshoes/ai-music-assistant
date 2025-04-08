#!/bin/bash
# 設置 Magenta 模擬環境的腳本

# 顯示彩色輸出的函數
function echo_color {
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    RED='\033[0;31m'
    NC='\033[0m' # No Color
    
    if [ "$2" = "success" ]; then
        echo -e "${GREEN}$1${NC}"
    elif [ "$2" = "warning" ]; then
        echo -e "${YELLOW}$1${NC}"
    elif [ "$2" = "error" ]; then
        echo -e "${RED}$1${NC}"
    else
        echo -e "$1"
    fi
}

# 歡迎信息
echo_color "AI音樂助手: 環境設置腳本" "success"
echo_color "=================================" "success"
echo

# 檢測 Python 版本
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo_color "檢測到 $PYTHON_VERSION" "success"
else
    echo_color "未檢測到 Python 3，請先安裝 Python 3.8 或更高版本" "error"
    exit 1
fi

# 創建虛擬環境
echo
echo_color "步驟 1: 創建 Python 虛擬環境..." "warning"
if [ -d "magenta_env" ]; then
    echo_color "已存在 magenta_env 虛擬環境。是否要重新創建? (y/n)" "warning"
    read -r recreate
    if [ "$recreate" = "y" ]; then
        echo_color "刪除現有虛擬環境..."
        rm -rf magenta_env
        python3 -m venv magenta_env
        echo_color "已重新創建虛擬環境" "success"
    else
        echo_color "保留現有虛擬環境" "success"
    fi
else
    python3 -m venv magenta_env
    echo_color "已創建虛擬環境" "success"
fi

# 激活虛擬環境
echo
echo_color "步驟 2: 激活虛擬環境..." "warning"
source magenta_env/bin/activate
echo_color "已激活虛擬環境: $(which python)" "success"

# 升級 pip 和安裝 setuptools
echo
echo_color "步驟 3: 升級 pip 和安裝基本工具..." "warning"
pip install --upgrade pip setuptools
echo_color "完成" "success"

# 安裝依賴項
echo
echo_color "步驟 4: 安裝基本依賴項..." "warning"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo_color "已從 requirements.txt 安裝依賴項" "success"
else
    echo_color "未找到 requirements.txt，安裝核心依賴項..." "warning"
    pip install numpy protobuf==3.19.0 note-seq
    echo_color "已安裝核心依賴項" "success"
fi

# 創建啟動腳本
echo
echo_color "步驟 5: 創建啟動腳本..." "warning"

# 開發模式腳本
cat > run_dev.sh << 'EOF'
#!/bin/bash
export USE_MOCK_MAGENTA=true
source magenta_env/bin/activate
python -m backend.main
EOF
chmod +x run_dev.sh

# 生產模式腳本
cat > run_prod.sh << 'EOF'
#!/bin/bash
export USE_MOCK_MAGENTA=false
source magenta_env/bin/activate
python -m backend.main
EOF
chmod +x run_prod.sh

echo_color "已創建啟動腳本 run_dev.sh (模擬模式) 和 run_prod.sh (真實模式)" "success"

# 設置環境變量
echo
echo_color "步驟 6: 設置環境變量..." "warning"
export PYTHONPATH=$PYTHONPATH:$(pwd)
export USE_MOCK_MAGENTA=true

# 告訴用戶如何啟動開發環境
echo
echo_color "環境設置完成！" "success"
echo_color "=================================" "success"
echo_color "要啟動開發環境（模擬模式）:" "warning"
echo_color "  ./run_dev.sh" "success"
echo_color "要啟動生產環境（真實 Magenta）:" "warning"
echo_color "  ./run_prod.sh" "success"
echo_color "要在 Docker 中運行:" "warning"
echo_color "  docker-compose up" "success"
echo
echo_color "現在您已在模擬模式下設置好環境變量。如需測試是否正常運行，請執行:" "warning"
echo_color "  python test_magenta_service.py" "success" 