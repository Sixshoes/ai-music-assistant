#!/usr/bin/env python3
"""測試HuggingFace API連接

這個腳本用於測試與HuggingFace推理API的連接
"""

import os
import sys
import requests
import json
import logging

# 配置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_huggingface_connection(api_key, model_url=None):
    """測試與HuggingFace API的連接
    
    Args:
        api_key: HuggingFace API金鑰
        model_url: 模型URL，默認使用Mistral-7B
    """
    if not model_url:
        model_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 簡單的測試輸入
    payload = {
        "inputs": "你好，請用繁體中文回答：給我一個D調的中國風五聲音階旋律描述，非常簡短。",
        "parameters": {
            "max_new_tokens": 100,
            "temperature": 0.7,
            "return_full_text": False
        }
    }
    
    try:
        logger.info(f"正在連接 HuggingFace API: {model_url}")
        response = requests.post(model_url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            logger.info("連接成功! 收到回應:")
            
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get('generated_text', '')
                logger.info(f"生成的文本: {generated_text}")
            elif isinstance(result, dict):
                generated_text = result.get('generated_text', '')
                logger.info(f"生成的文本: {generated_text}")
            else:
                logger.info(f"原始回應: {json.dumps(result, ensure_ascii=False, indent=2)}")
                
            return True
        elif response.status_code == 503:
            logger.warning("模型正在加載中，請稍後再試")
            logger.info(f"回應: {response.text}")
            return False
        else:
            logger.error(f"請求失敗，狀態碼: {response.status_code}")
            logger.error(f"錯誤訊息: {response.text}")
            return False
    
    except Exception as e:
        logger.error(f"連接過程中發生錯誤: {str(e)}")
        return False

def main():
    """主函數"""
    # 從環境變數或命令行參數獲取API金鑰
    api_key = os.environ.get("HF_API_KEY")
    
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    
    if not api_key:
        logger.error("請提供HuggingFace API金鑰，可通過環境變數HF_API_KEY或命令行參數提供")
        logger.info("使用方法: python test_huggingface_connection.py YOUR_API_KEY")
        sys.exit(1)
    
    # 可選的模型URL
    model_url = os.environ.get("HF_API_URL")
    
    # 測試連接
    success = test_huggingface_connection(api_key, model_url)
    
    if success:
        logger.info("HuggingFace API 連接測試成功!")
    else:
        logger.error("HuggingFace API 連接測試失敗!")
        sys.exit(1)

if __name__ == "__main__":
    main() 