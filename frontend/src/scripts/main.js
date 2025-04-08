/**
 * AI音樂創作助手 - 前端交互
 */

// 獲取DOM元素
const musicForm = document.getElementById('musicForm');
const musicDescription = document.getElementById('musicDescription');
const useLLM = document.getElementById('useLLM');
const generateBtn = document.getElementById('generateBtn');
const resultSection = document.getElementById('resultSection');
const resultMessage = document.getElementById('resultMessage');
const loadingSection = document.getElementById('loadingSection');
const musicPlayer = document.getElementById('musicPlayer');
const audioPlayer = document.getElementById('audioPlayer');
const downloadBtn = document.getElementById('downloadBtn');

// API端點
const API_URL = 'http://localhost:5000';

// 跟踪當前生成的音樂文件
let currentMusicFilename = null;

// 表單提交處理
musicForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  // 獲取表單數據
  const description = musicDescription.value.trim();
  const useLLMValue = useLLM.checked;
  
  // 驗證表單
  if (!description) {
    showResult('請輸入音樂描述', 'error');
    return;
  }
  
  // 顯示加載中
  showLoading(true);
  
  try {
    // 發送請求至後端
    const response = await fetch(`${API_URL}/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        description,
        use_llm: useLLMValue
      })
    });
    
    const data = await response.json();
    
    // 隱藏加載中
    showLoading(false);
    
    // 處理響應
    if (data.status === 'success') {
      // 保存當前文件名
      currentMusicFilename = data.filename;
      
      // 設置音頻播放器源
      const audioSrc = `${API_URL}/download/${data.filename}`;
      
      // 顯示成功信息
      showResult(`
        <p class="success">音樂已成功生成！</p>
        <p>您的音樂描述：${description}</p>
        <p>生成的音樂類型：${data.details?.stages?.requirement_analysis?.genre || '未知'}</p>
        <p>情感特徵：${data.details?.stages?.requirement_analysis?.mood || '未知'}</p>
      `, 'success');
      
      // 顯示音樂播放器
      showMusicPlayer(audioSrc);
    } else {
      // 顯示錯誤信息
      showResult(`生成音樂時發生錯誤：${data.message}`, 'error');
    }
  } catch (error) {
    // 隱藏加載中
    showLoading(false);
    
    // 顯示錯誤信息
    showResult(`發生錯誤：${error.message}`, 'error');
  }
});

// 下載按鈕點擊處理
downloadBtn.addEventListener('click', () => {
  if (currentMusicFilename) {
    window.location.href = `${API_URL}/download/${currentMusicFilename}`;
  }
});

/**
 * 顯示結果信息
 * @param {string} message - 要顯示的信息
 * @param {string} type - 信息類型（success/error）
 */
function showResult(message, type = 'success') {
  resultMessage.innerHTML = message;
  resultMessage.className = type;
  resultSection.classList.remove('hidden');
}

/**
 * 顯示或隱藏加載中狀態
 * @param {boolean} show - 是否顯示加載中
 */
function showLoading(show) {
  if (show) {
    loadingSection.classList.remove('hidden');
    resultSection.classList.add('hidden');
    generateBtn.disabled = true;
  } else {
    loadingSection.classList.add('hidden');
    generateBtn.disabled = false;
  }
}

/**
 * 顯示音樂播放器
 * @param {string} audioSrc - 音頻文件URL
 */
function showMusicPlayer(audioSrc) {
  audioPlayer.src = audioSrc;
  musicPlayer.classList.remove('hidden');
}

/**
 * 頁面加載時初始化
 */
function init() {
  // 隱藏結果和加載中區域
  resultSection.classList.add('hidden');
  loadingSection.classList.add('hidden');
  musicPlayer.classList.add('hidden');
  
  // 設置默認描述示例
  musicDescription.value = '創作一首平靜的古典音樂，帶有中國傳統元素，適合沉思和冥想';
}

// 頁面加載時初始化
window.addEventListener('load', init); 