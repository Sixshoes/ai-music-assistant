#!/bin/bash
# Magenta 安裝腳本

echo "開始安裝 Magenta 及其依賴..."

# 確保 pip 是最新版本
pip3 install --upgrade pip

# 安裝 TensorFlow 和其他基本依賴
pip3 install tensorflow==2.8.0 numpy==1.22.3 scipy==1.8.0 

# 安裝 protobuf 和其他相關依賴
pip3 install protobuf==3.19.4 absl-py==1.0.0 

# 安裝 note-seq 和其他音樂處理庫
pip3 install note-seq==0.0.5 pretty-midi==0.2.9 mir-eval==0.6

# 安裝 tensor2tensor 和其他機器學習庫
pip3 install tensor2tensor==1.15.7

# 嘗試安裝 magenta (不安裝依賴，因為我們已經手動安裝了)
pip3 install magenta==2.1.4 --no-deps

echo "安裝完成！"
echo "如果仍然有導入錯誤，可能需要手動安裝特定版本的依賴或從源代碼安裝 Magenta。"
echo "參考: https://github.com/magenta/magenta#installation" 