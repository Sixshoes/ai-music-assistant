import os
import sys

# 添加專案根目錄到 Python 路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import magenta
import note_seq
from note_seq.protobuf import music_pb2
import tempfile
import logging
import json
from typing import Dict, Any, Optional
from backend.models import init_db

# 配置日誌
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 導入文本到音樂轉換器
try:
    from text_to_music import TextToMusicConverter
except ImportError:
    logger.error("找不到 text_to_music 模組，請確保 text_to_music.py 在當前目錄中")
    sys.exit(1)

app = Flask(__name__)
CORS(app)

# 資料庫配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///music_assistant.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化資料庫
init_db(app)

# 確保輸出目錄存在
output_dir = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(output_dir, exist_ok=True)

# 初始化文本到音樂轉換器
converter = TextToMusicConverter(use_llm=False)

@app.route('/generate', methods=['POST'])
def generate_music():
    try:
        # 獲取請求數據
        data = request.get_json()
        description = data.get('description', '')
        use_llm = data.get('use_llm', False)
        
        if not description:
            return jsonify({"status": "error", "message": "缺少音樂描述"}), 400
        
        # 創建臨時文件路徑
        temp_dir = tempfile.mkdtemp()
        output_path = os.path.join(temp_dir, 'generated_music.mid')
        
        # 創建音樂
        if use_llm != converter.use_llm:
            # 如果請求的 LLM 設置與當前實例不同，創建新實例
            temp_converter = TextToMusicConverter(use_llm=use_llm)
            result = temp_converter.create_music(description, output_path)
        else:
            result = converter.create_music(description, output_path)
        
        # 檢查結果
        output_file = result.get('output_file', '')
        if not output_file or not os.path.exists(output_file):
            return jsonify({
                "status": "error", 
                "message": "音樂生成失敗，未生成輸出文件"
            }), 500
        
        # 將臨時文件複製到持久化目錄
        import shutil
        filename = os.path.basename(output_file)
        persistent_path = os.path.join(output_dir, filename)
        shutil.copy2(output_file, persistent_path)
        
        # 返回結果
        return jsonify({
            "status": "success", 
            "message": "音樂生成成功", 
            "filename": filename,
            "details": result
        })
    except Exception as e:
        logger.error(f"音樂生成過程中發生錯誤: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """下載生成的音樂文件"""
    try:
        file_path = os.path.join(output_dir, filename)
        if not os.path.exists(file_path):
            return jsonify({"status": "error", "message": "文件不存在"}), 404
        
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        logger.error(f"下載文件過程中發生錯誤: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 