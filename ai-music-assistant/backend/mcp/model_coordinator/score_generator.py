"""樂譜生成器模組

提供樂譜生成和轉換功能
"""

import os
import base64
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ScoreGenerator:
    """樂譜生成器"""
    
    def __init__(self):
        """初始化樂譜生成器"""
        self._setup_fonts()
    
    def _setup_fonts(self):
        """設置字體"""
        try:
            import matplotlib.font_manager as fm
            # 使用相對路徑獲取字體文件路徑
            font_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "fonts",
                "FreeSans.ttf"
            )
            
            # 檢查字體文件是否存在
            if os.path.exists(font_path):
                # 嘗試註冊字體
                fm.fontManager.addfont(font_path)
                logger.info(f"成功註冊字體: {font_path}")
            else:
                # 如果字體文件不存在，記錄警告
                logger.warning(f"無法註冊字體: 找不到字體文件 {font_path}")
                
                # 嘗試使用系統字體
                system_fonts = fm.findSystemFonts(fontpaths=None, fontext='ttf')
                if system_fonts:
                    # 使用第一個找到的系統字體
                    fm.fontManager.addfont(system_fonts[0])
                    logger.info(f"使用系統字體替代: {system_fonts[0]}")
                    
        except Exception as e:
            # 記錄錯誤但不中斷程序
            logger.warning(f"字體註冊過程中發生錯誤: {str(e)}")
            logger.info("繼續執行，使用默認字體")
    
    def generate_musicxml(self, notes: list, key: str, time_signature: str) -> str:
        """生成 MusicXML
        
        Args:
            notes: 音符列表
            key: 調性
            time_signature: 拍號
            
        Returns:
            MusicXML 字符串
        """
        # 這裡返回一個簡單的 MusicXML 示例
        return """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1">
  <part-list>
    <score-part id="P1">
      <part-name>Music</part-name>
    </score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>1</divisions>
        <key>
          <fifths>0</fifths>
        </key>
        <time>
          <beats>4</beats>
          <beat-type>4</beat-type>
        </time>
        <clef>
          <sign>G</sign>
          <line>2</line>
        </clef>
      </attributes>
      <note>
        <pitch>
          <step>C</step>
          <octave>4</octave>
        </pitch>
        <duration>4</duration>
        <type>whole</type>
      </note>
    </measure>
  </part>
</score-partwise>"""
    
    def generate_pdf(self, title: str, key: str, tempo: int, genre: str) -> bytes:
        """生成 PDF
        
        Args:
            title: 標題
            key: 調性
            tempo: 速度
            genre: 風格
            
        Returns:
            PDF 文件的字節數據
        """
        try:
            # 使用 reportlab 生成 PDF
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from io import BytesIO
            
            # 創建 BytesIO 對象
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            
            # 嘗試使用註冊的字體，如果失敗則使用系統默認字體
            try:
                c.setFont("FreeSans", 24)
            except:
                logger.warning("無法使用 FreeSans 字體，使用 Helvetica 替代")
                c.setFont("Helvetica", 24)
            
            # 添加標題
            c.drawString(72, 800, title)
            
            # 使用系統默認字體添加音樂信息
            c.setFont("Helvetica", 12)
            c.drawString(72, 750, f"調性: {key}")
            c.drawString(72, 730, f"速度: {tempo} BPM")
            c.drawString(72, 710, f"風格: {genre}")
            
            # 保存 PDF
            c.save()
            
            # 返回 PDF 數據
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"生成 PDF 時發生錯誤: {str(e)}")
            # 返回一個簡單的備用 PDF
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from io import BytesIO
            
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            c.setFont("Helvetica", 24)
            c.drawString(72, 800, "無法生成樂譜")
            c.save()
            return buffer.getvalue()
    
    def generate_score_data(self, title: str, notes: list, key: str,
                          time_signature: str, tempo: int, genre: str) -> Dict[str, str]:
        """生成樂譜數據
        
        Args:
            title: 標題
            notes: 音符列表
            key: 調性
            time_signature: 拍號
            tempo: 速度
            genre: 風格
            
        Returns:
            包含 MusicXML 和 PDF 數據的字典
        """
        try:
            # 生成 MusicXML
            musicxml = self.generate_musicxml(notes, key, time_signature)
            musicxml_base64 = base64.b64encode(musicxml.encode()).decode()
            
            # 生成 PDF
            pdf = self.generate_pdf(title, key, tempo, genre)
            pdf_base64 = base64.b64encode(pdf).decode()
            
            return {
                "musicxml": musicxml_base64,
                "pdf": pdf_base64
            }
        except Exception as e:
            logger.error(f"生成樂譜數據時發生錯誤: {str(e)}")
            return {
                "musicxml": "",
                "pdf": ""
            } 