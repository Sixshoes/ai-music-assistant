#!/usr/bin/env python
"""
AI 音樂助手 - 獨立應用版本

這個腳本結合了 Magenta 服務和 Web 界面，讓用戶可以直接生成音樂並在瀏覽器中預覽。
不需要依賴完整的後端和前端框架。
"""

import os
import sys
import json
import base64
import logging
import tempfile
import threading
import webbrowser
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse

# 設置日誌記錄
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 設置環境變量以使用模擬服務
os.environ["USE_MOCK_MAGENTA"] = "true"

# 將當前目錄添加到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent))

# 導入服務
try:
    from backend.music_generation import MagentaService
    logger.info("成功導入 Magenta 服務")
except ImportError as e:
    logger.error(f"導入 Magenta 服務失敗: {e}")
    print("\n無法導入 Magenta 服務，請確保您在正確的目錄中運行此腳本。")
    print("確保目錄結構正確，且 backend/music_generation 模塊可用。")
    sys.exit(1)

# HTTP 服務器端口
PORT = 8080

# 存儲生成的音樂文件
MUSIC_FILES = {}

# 自定義請求處理器
class MusicAppHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        """處理 GET 請求"""
        # 主頁
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(get_index_html().encode("utf-8"))
            return
        
        # API 請求 - 生成音樂列表
        if self.path == "/api/music/list":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(list(MUSIC_FILES.values())).encode("utf-8"))
            return
            
        # 處理靜態文件和生成的音樂文件
        try:
            # 檢查是否是預先生成的 MIDI 文件
            if self.path.startswith("/generated/"):
                music_id = self.path.split("/")[-1]
                if music_id in MUSIC_FILES:
                    midi_path = MUSIC_FILES[music_id]["file_path"]
                    self.send_response(200)
                    self.send_header("Content-type", "audio/midi")
                    self.send_header("Content-Disposition", f'attachment; filename="{MUSIC_FILES[music_id]["filename"]}"')
                    self.end_headers()
                    with open(midi_path, "rb") as f:
                        self.wfile.write(f.read())
                    return
            
            # 處理常規文件請求
            return SimpleHTTPRequestHandler.do_GET(self)
        except Exception as e:
            logger.error(f"處理 GET 請求時發生錯誤: {e}")
            self.send_error(500, f"服務器錯誤: {str(e)}")
    
    def do_POST(self):
        """處理 POST 請求"""
        # 處理 API 請求
        if self.path.startswith("/api/"):
            try:
                # 獲取請求內容長度
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                params = json.loads(post_data)
                
                # 根據請求路徑處理不同的 API
                if self.path == "/api/music/generate":
                    # 生成音樂 API
                    response = handle_generate_music(params)
                    
                    # 發送響應
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode("utf-8"))
                    return
                
                # 未知 API
                self.send_response(404)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "未知 API 端點"}).encode("utf-8"))
                
            except Exception as e:
                logger.error(f"處理 POST 請求時發生錯誤: {e}")
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

def generate_music_id():
    """生成唯一的音樂 ID"""
    import time
    return f"music_{int(time.time() * 1000)}"

def handle_generate_music(params):
    """處理音樂生成請求"""
    try:
        # 創建服務實例
        service = MagentaService()
        
        # 解析參數
        text = params.get("text", "")
        use_text = params.get("use_text", False)
        
        # 創建音樂參數
        class MusicParameters:
            def __init__(self):
                self.tempo = params.get("tempo", 120)
                self.key = params.get("key", "C")
                self.genre = params.get("genre", "pop")
                self.description = text or "AI 生成的音樂"
        
        params_obj = MusicParameters()
        
        # 生成音樂
        if use_text and text:
            logger.info(f"根據文本生成旋律: '{text}'")
            melody = service.text_to_melody(text, params_obj)
            source_type = "text"
            description = f"根據文本生成: {text}"
        else:
            logger.info("生成隨機旋律")
            melody = service.generate_melody(params_obj)
            source_type = "random"
            description = "隨機生成的旋律"
        
        # 生成 ID
        music_id = generate_music_id()
        
        # 構建文件名
        filename = f"{music_id}.mid"
        
        # 將旋律保存為 MIDI
        temp_dir = tempfile.gettempdir()
        midi_path = os.path.join(temp_dir, filename)
        service.melody_to_midi(melody, midi_path, params_obj.tempo)
        
        # 存儲音樂文件信息
        music_info = {
            "id": music_id,
            "filename": filename,
            "file_path": midi_path,
            "description": description,
            "text": text,
            "tempo": params_obj.tempo,
            "key": params_obj.key,
            "genre": params_obj.genre,
            "notes_count": len(melody),
            "source_type": source_type,
            "created_at": import_time_module().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        MUSIC_FILES[music_id] = music_info
        
        return {
            "success": True,
            "music": music_info
        }
        
    except Exception as e:
        logger.error(f"生成音樂時發生錯誤: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def import_time_module():
    """導入 time 模塊並返回 time 對象"""
    import time
    return time

def get_index_html():
    """獲取主頁 HTML"""
    return """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI 音樂助手</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }
        h1, h2, h3 {
            color: #1976d2;
        }
        .container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        .card {
            background-color: #f5f5f5;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="text"],
        input[type="number"],
        select,
        textarea {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        button {
            background-color: #1976d2;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #1565c0;
        }
        .music-list {
            list-style: none;
            padding: 0;
        }
        .music-item {
            background-color: white;
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 10px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .music-controls {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }
        .loading {
            display: none;
            align-items: center;
            justify-content: center;
            margin: 20px 0;
        }
        .loading-spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #1976d2;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin-right: 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .error-message {
            color: #d32f2f;
            font-weight: bold;
            margin: 10px 0;
            display: none;
        }
        .success-message {
            color: #388e3c;
            font-weight: bold;
            margin: 10px 0;
            display: none;
        }
        .music-info {
            margin-top: 5px;
            color: #666;
            font-size: 14px;
        }
        @media (max-width: 768px) {
            .container {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <h1>AI 音樂助手</h1>
    
    <div class="container">
        <div>
            <div class="card">
                <h2>生成音樂</h2>
                <form id="musicForm">
                    <div class="form-group">
                        <label for="musicType">生成方式</label>
                        <select id="musicType" name="musicType">
                            <option value="random">隨機生成</option>
                            <option value="text">根據文本生成</option>
                        </select>
                    </div>
                    
                    <div class="form-group" id="textInputGroup" style="display: none;">
                        <label for="textInput">音樂描述</label>
                        <textarea id="textInput" name="textInput" rows="3" placeholder="例如：輕快的夏日旋律，帶有一絲微風的感覺"></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="tempo">速度 (BPM)</label>
                        <input type="number" id="tempo" name="tempo" min="60" max="180" value="120">
                    </div>
                    
                    <div class="form-group">
                        <label for="key">調性</label>
                        <select id="key" name="key">
                            <option value="C">C 大調</option>
                            <option value="G">G 大調</option>
                            <option value="D">D 大調</option>
                            <option value="A">A 大調</option>
                            <option value="F">F 大調</option>
                            <option value="Am">A 小調</option>
                            <option value="Em">E 小調</option>
                            <option value="Dm">D 小調</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="genre">風格</label>
                        <select id="genre" name="genre">
                            <option value="pop">流行</option>
                            <option value="rock">搖滾</option>
                            <option value="jazz">爵士</option>
                            <option value="classical">古典</option>
                            <option value="electronic">電子</option>
                            <option value="folk">民謠</option>
                        </select>
                    </div>
                    
                    <button type="submit">生成音樂</button>
                </form>
                
                <div class="loading" id="loading">
                    <div class="loading-spinner"></div>
                    <span>正在生成音樂...</span>
                </div>
                
                <div class="error-message" id="errorMessage"></div>
                <div class="success-message" id="successMessage"></div>
            </div>
        </div>
        
        <div>
            <div class="card">
                <h2>我的音樂</h2>
                <div id="musicListContainer">
                    <p>尚未生成任何音樂。</p>
                </div>
            </div>
        </div>
    </div>
    
    <div class="card">
        <h3>關於 AI 音樂助手</h3>
        <p>
            這是一個使用 AI 技術生成音樂的應用。您可以隨機生成旋律，或者根據文字描述來創作音樂。
            生成的音樂將以 MIDI 格式保存，您可以直接在瀏覽器中播放，或下載到您的電腦進行編輯。
        </p>
        <p>
            <strong>注意：</strong> 由於使用模擬模式運行，生成的音樂是通過簡單算法創建的示例，
            並非真正的 AI 生成結果。這僅用於演示目的。
        </p>
    </div>

    <script>
        // 當頁面載入完成後執行
        document.addEventListener('DOMContentLoaded', function() {
            // 獲取元素
            const musicForm = document.getElementById('musicForm');
            const musicType = document.getElementById('musicType');
            const textInputGroup = document.getElementById('textInputGroup');
            const textInput = document.getElementById('textInput');
            const loading = document.getElementById('loading');
            const errorMessage = document.getElementById('errorMessage');
            const successMessage = document.getElementById('successMessage');
            const musicListContainer = document.getElementById('musicListContainer');
            
            // 載入已生成的音樂列表
            loadMusicList();
            
            // 根據選擇的音樂生成方式顯示/隱藏文本輸入框
            musicType.addEventListener('change', function() {
                if (this.value === 'text') {
                    textInputGroup.style.display = 'block';
                } else {
                    textInputGroup.style.display = 'none';
                }
            });
            
            // 處理表單提交
            musicForm.addEventListener('submit', function(e) {
                e.preventDefault();
                
                // 隱藏之前的消息
                errorMessage.style.display = 'none';
                successMessage.style.display = 'none';
                
                // 顯示載入中
                loading.style.display = 'flex';
                
                // 準備表單數據
                const formData = {
                    use_text: musicType.value === 'text',
                    text: textInput.value,
                    tempo: parseInt(document.getElementById('tempo').value),
                    key: document.getElementById('key').value,
                    genre: document.getElementById('genre').value
                };
                
                // 發送 API 請求
                fetch('/api/music/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                })
                .then(response => response.json())
                .then(data => {
                    // 隱藏載入中
                    loading.style.display = 'none';
                    
                    if (data.success) {
                        // 顯示成功消息
                        successMessage.textContent = '音樂生成成功！';
                        successMessage.style.display = 'block';
                        
                        // 更新音樂列表
                        loadMusicList();
                    } else {
                        // 顯示錯誤消息
                        errorMessage.textContent = '生成音樂失敗: ' + data.error;
                        errorMessage.style.display = 'block';
                    }
                })
                .catch(error => {
                    // 隱藏載入中
                    loading.style.display = 'none';
                    
                    // 顯示錯誤消息
                    errorMessage.textContent = '發生錯誤: ' + error.message;
                    errorMessage.style.display = 'block';
                });
            });
            
            // 載入音樂列表
            function loadMusicList() {
                fetch('/api/music/list')
                    .then(response => response.json())
                    .then(musicList => {
                        if (musicList.length > 0) {
                            // 有音樂，顯示列表
                            let html = '<ul class="music-list">';
                            
                            // 最新的排在前面
                            musicList.reverse().forEach(music => {
                                html += `
                                    <li class="music-item">
                                        <strong>${music.description}</strong>
                                        <div class="music-info">
                                            ${music.notes_count} 個音符 | ${music.tempo} BPM | ${music.key} | ${formatGenre(music.genre)}
                                        </div>
                                        <div class="music-controls">
                                            <button onclick="playMusic('${music.id}')">播放</button>
                                            <a href="/generated/${music.id}" download="${music.filename}">
                                                <button>下載</button>
                                            </a>
                                        </div>
                                    </li>
                                `;
                            });
                            
                            html += '</ul>';
                            musicListContainer.innerHTML = html;
                        } else {
                            // 沒有音樂
                            musicListContainer.innerHTML = '<p>尚未生成任何音樂。</p>';
                        }
                    })
                    .catch(error => {
                        musicListContainer.innerHTML = `<p>載入音樂列表失敗: ${error.message}</p>`;
                    });
            }
            
            // 將音樂風格代碼轉換為顯示名稱
            window.formatGenre = function(genre) {
                const genres = {
                    'pop': '流行',
                    'rock': '搖滾',
                    'jazz': '爵士',
                    'classical': '古典',
                    'electronic': '電子',
                    'folk': '民謠'
                };
                return genres[genre] || genre;
            };
            
            // 播放音樂
            window.playMusic = function(musicId) {
                window.open(`/generated/${musicId}`, '_blank');
            };
        });
    </script>
</body>
</html>
"""

def start_server():
    """啟動 HTTP 服務器"""
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, MusicAppHandler)
    print(f"\n服務器啟動在 http://localhost:{PORT}")
    print("您可以在瀏覽器中訪問此地址來使用 AI 音樂助手")
    print("\n按 Ctrl+C 停止服務器\n")
    httpd.serve_forever()

def main():
    """主函數"""
    print("\n===== AI 音樂助手 - 獨立應用版本 =====\n")
    
    try:
        # 創建服務實例測試
        service = MagentaService()
        print("Magenta 服務初始化成功")
        
        # 啟動服務器
        server_thread = threading.Thread(target=start_server)
        server_thread.daemon = True
        server_thread.start()
        
        # 打開瀏覽器
        webbrowser.open(f"http://localhost:{PORT}")
        
        # 保持主線程運行
        while True:
            server_thread.join(1)
    
    except KeyboardInterrupt:
        print("\n服務器已停止")
    except Exception as e:
        logger.error(f"啟動應用時發生錯誤: {e}")
        print(f"\n啟動應用時發生錯誤: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 