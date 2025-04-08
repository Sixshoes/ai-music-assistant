from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import tempfile
import logging
import json
from typing import Dict, Any, Optional

# 配置日誌
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 確保輸出目錄存在
output_dir = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(output_dir, exist_ok=True)

@app.route('/test', methods=['GET'])
def test():
    return jsonify({"status": "success", "message": "API is working!"})

@app.route('/generate', methods=['POST'])
def generate_music():
    try:
        # 獲取請求數據
        data = request.get_json()
        description = data.get('description', '')
        
        if not description:
            return jsonify({"status": "error", "message": "缺少音樂描述"}), 400
        
        # 暫時返回測試響應
        return jsonify({
            "status": "success", 
            "message": "收到請求",
            "description": description
        })
        
    except Exception as e:
        logger.error(f"音樂生成過程中發生錯誤: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 