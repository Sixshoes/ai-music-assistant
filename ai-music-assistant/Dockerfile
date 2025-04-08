FROM tensorflow/tensorflow:2.4.0

# 安裝基本依賴
RUN apt-get update && apt-get install -y \
    build-essential \
    fluidsynth \
    libfluidsynth-dev \
    libasound2-dev \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Python 依賴
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install magenta note-seq==0.0.5 pyfluidsynth

# 設置環境變量
ENV USE_MOCK_MAGENTA=false

# 複製應用程式代碼
COPY . .

# 啟動命令
CMD ["python", "-m", "backend.main"] 