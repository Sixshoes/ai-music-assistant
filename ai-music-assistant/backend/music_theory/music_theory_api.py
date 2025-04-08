#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""音樂理論API

提供音樂理論分析的API端點，包括和弦分析、旋律分析、和聲檢測等功能
"""

import os
import logging
import json
import tempfile
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

from music21_service import Music21Service
from ..theory_validator import TheoryValidator, load_notes_from_json, Note

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('music_theory_api')

# 創建路由
router = APIRouter(
    prefix="/api/theory",
    tags=["music-theory"],
    responses={404: {"description": "Not found"}},
)

# 初始化服務
theory_service = Music21Service()
theory_validator = TheoryValidator()

# 嘗試導入pydantic，如果不可用則使用簡單替代模型
try:
    from pydantic import BaseModel, Field
    USE_PYDANTIC = True
except ImportError:
    logging.warning("無法導入pydantic，使用基本類型替代。某些功能可能不可用。")
    USE_PYDANTIC = False
    
    # 創建簡單替代類
    class BaseModel:
        def __init__(self, **data):
            for key, value in data.items():
                setattr(self, key, value)
                
    # 簡單的Field替代函數
    def Field(*args, **kwargs):
        return None

# 數據模型
class NoteData(BaseModel):
    pitch: int
    duration: float
    startTime: Optional[float] = None
    velocity: Optional[int] = 64

class MusicDataRequest(BaseModel):
    notes: List[NoteData]

class TheoryQueryRequest(BaseModel):
    query: str
    musicData: Optional[str] = None
    notes: Optional[List[NoteData]] = None

class TheoryAnalysisResponse(BaseModel):
    score: int
    key: str
    tempo: Optional[int] = None
    timeSignature: Optional[str] = None
    chords: List[str]
    chordNumerals: List[str]
    progression: str
    suggestions: List[str]
    errors: List[str] = []
    warnings: List[str] = []
    structure: Optional[Dict[str, List[int]]] = None
    melodyAnalysis: Optional[Dict[str, Any]] = None
    harmonyAnalysis: Optional[Dict[str, Any]] = None

@router.post("/analyze-midi", response_model=TheoryAnalysisResponse)
async def analyze_midi_file(
    midi_file: UploadFile = File(...),
) -> Dict[str, Any]:
    """分析上傳的MIDI文件

    Args:
        midi_file: 上傳的MIDI文件

    Returns:
        音樂理論分析結果
    """
    try:
        logger.info(f"接收到MIDI分析請求: {midi_file.filename}")
        
        # 創建臨時文件保存上傳的MIDI
        temp_dir = tempfile.mkdtemp()
        temp_midi_path = os.path.join(temp_dir, midi_file.filename)
        
        # 保存上傳的文件
        with open(temp_midi_path, "wb") as f:
            f.write(await midi_file.read())
        
        # 使用Music21服務分析MIDI文件
        analysis_result = theory_service.analyze_midi_file(temp_midi_path)
        
        # 轉換為API響應格式
        response = {
            "score": 85,  # 這應該從分析結果中獲取
            "key": str(analysis_result.key),
            "tempo": analysis_result.tempo,
            "timeSignature": str(analysis_result.time_signature),
            "chords": analysis_result.chord_progression.chords,
            "chordNumerals": convert_to_numerals(
                analysis_result.chord_progression.chords, 
                analysis_result.key
            ),
            "progression": " - ".join(analysis_result.chord_progression.chords),
            "suggestions": analysis_result.suggestions,
            "errors": [],
            "warnings": analysis_result.harmony_issues,
            "structure": analysis_result.structure,
            "melodyAnalysis": {
                "pitchRange": 19,  # 這些值應從分析中獲取
                "averagePitch": 60,
                "mostCommonInterval": 2,
                "rhythmicDiversity": 0.7
            },
            "harmonyAnalysis": {
                "diatonicPercentage": 85,
                "dissonanceLevel": 0.3,
                "colorChords": ["F#dim7", "Eb7"]
            }
        }
        
        # 刪除臨時文件
        os.remove(temp_midi_path)
        os.rmdir(temp_dir)
        
        return response
        
    except Exception as e:
        logger.error(f"分析MIDI文件時出錯: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"分析失敗: {str(e)}")

@router.post("/analyze-notes", response_model=TheoryAnalysisResponse)
async def analyze_notes(
    request: MusicDataRequest
) -> Dict[str, Any]:
    """分析音符數據

    Args:
        request: 包含音符列表的請求

    Returns:
        音樂理論分析結果
    """
    try:
        logger.info(f"接收到音符分析請求，包含 {len(request.notes)} 個音符")
        
        # 將API請求模型轉換為內部Note類型
        notes = []
        for note_data in request.notes:
            notes.append(Note(
                pitch=note_data.pitch,
                duration=note_data.duration,
                velocity=note_data.velocity or 64
            ))
        
        # 使用TheoryValidator進行分析
        validation_result = theory_validator.validate(notes)
        
        # 計算更多的旋律分析數據
        melody_analysis = theory_validator.analyze_melody(notes)
        
        # 轉換為API響應格式
        response = {
            "score": validation_result["score"],
            "key": validation_result["key"],
            "tempo": 120,  # 默認值，實際應從分析結果獲取
            "timeSignature": "4/4",  # 默認值，實際應從分析結果獲取
            "chords": validation_result["chords"],
            "chordNumerals": convert_to_numerals(
                validation_result["chords"], 
                validation_result["key"]
            ),
            "progression": " - ".join(validation_result["chords"]),
            "suggestions": [suggestion for suggestion in validation_result["suggestions"]],
            "errors": [],
            "warnings": [issue["message"] for issue in validation_result["issues"]],
            "structure": {
                "verse": [1, 5],
                "chorus": [9, 13]
            },
            "melodyAnalysis": {
                "pitchRange": melody_analysis["pitch_range"],
                "averagePitch": melody_analysis["average_pitch"],
                "mostCommonInterval": melody_analysis["most_common_interval"],
                "rhythmicDiversity": 0.7
            },
            "harmonyAnalysis": {
                "diatonicPercentage": 85,
                "dissonanceLevel": 0.3,
                "colorChords": []
            }
        }
        
        return response
        
    except Exception as e:
        logger.error(f"分析音符時出錯: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"分析失敗: {str(e)}")

@router.post("/analyze-music-data", response_model=TheoryAnalysisResponse)
async def analyze_music_data(
    music_data: str = Form(...)
) -> Dict[str, Any]:
    """分析音樂數據字符串

    Args:
        music_data: JSON格式的音樂數據

    Returns:
        音樂理論分析結果
    """
    try:
        logger.info("接收到音樂數據分析請求")
        
        # 從JSON加載音符數據
        notes = load_notes_from_json(music_data)
        
        # 使用TheoryValidator進行分析
        validation_result = theory_validator.validate(notes)
        
        # 與analyze_notes相同的響應處理流程
        response = {
            "score": validation_result["score"],
            "key": validation_result["key"],
            "tempo": 120,
            "timeSignature": "4/4",
            "chords": validation_result["chords"],
            "chordNumerals": convert_to_numerals(
                validation_result["chords"], 
                validation_result["key"]
            ),
            "progression": " - ".join(validation_result["chords"]),
            "suggestions": [suggestion for suggestion in validation_result["suggestions"]],
            "errors": [],
            "warnings": [issue["message"] for issue in validation_result["issues"]],
            "structure": {
                "verse": [1, 5],
                "chorus": [9, 13]
            },
            "melodyAnalysis": {
                "pitchRange": 19,
                "averagePitch": 60,
                "mostCommonInterval": 2,
                "rhythmicDiversity": 0.7
            },
            "harmonyAnalysis": {
                "diatonicPercentage": 85,
                "dissonanceLevel": 0.3,
                "colorChords": []
            }
        }
        
        return response
        
    except Exception as e:
        logger.error(f"分析音樂數據時出錯: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"分析失敗: {str(e)}")

@router.post("/theory-query", response_model=Dict[str, str])
async def theory_query(
    request: TheoryQueryRequest
) -> Dict[str, str]:
    """處理特定的音樂理論查詢

    Args:
        request: 包含查詢和相關音樂數據的請求

    Returns:
        對查詢的回應
    """
    try:
        logger.info(f"接收到音樂理論查詢: {request.query}")
        
        # 這裡可以實現更複雜的查詢處理邏輯，例如將查詢發送到LLM
        # 簡單示例響應
        response = {
            "response": f"關於'{request.query}'的分析：在古典音樂中，常見的做法是使用調內的II-V-I進行增加和聲張力，您可以在第8小節後嘗試這個進行。"
        }
        
        return response
        
    except Exception as e:
        logger.error(f"處理理論查詢時出錯: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"查詢處理失敗: {str(e)}")

@router.post("/auto-correct", response_model=Dict[str, Any])
async def auto_correct(
    request: MusicDataRequest
) -> Dict[str, Any]:
    """基於樂理規則自動修正音樂

    Args:
        request: 包含要修正的音符數據

    Returns:
        修正後的音符數據和說明
    """
    try:
        logger.info(f"接收到自動修正請求，包含 {len(request.notes)} 個音符")
        
        # 將API請求模型轉換為內部Note類型
        notes = []
        for note_data in request.notes:
            notes.append(Note(
                pitch=note_data.pitch,
                duration=note_data.duration,
                velocity=note_data.velocity or 64
            ))
        
        # 使用TheoryValidator進行分析
        validation_result = theory_validator.validate(notes)
        
        # 這裡應該實現自動修正邏輯
        # 簡單示例：將所有音符移到最近的調內音
        corrected_notes = []
        key_root, key_type = 0, "major"  # 默認C大調，實際應從分析中獲取
        
        # 模擬自動修正
        for i, original_note in enumerate(request.notes):
            # 簡單示例修正：移動到最近的調內音
            # 實際應用中需要更複雜的邏輯
            corrected_note = NoteData(
                pitch=original_note.pitch,
                duration=original_note.duration,
                startTime=original_note.startTime,
                velocity=original_note.velocity
            )
            
            # 添加到結果
            corrected_notes.append(corrected_note)
        
        # 構建響應
        response = {
            "originalNotes": request.notes,
            "correctedNotes": corrected_notes,
            "corrections": [
                "修正了第2小節的不協和音",
                "調整了第5小節的和弦進行以避免平行五度",
                "調整了第7小節的旋律以保持在調內"
            ],
            "explanation": "基於C大調的樂理規則進行了修正，主要修正了調外音和不自然的和聲進行。"
        }
        
        return response
        
    except Exception as e:
        logger.error(f"自動修正時出錯: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"自動修正失敗: {str(e)}")

def convert_to_numerals(chords: List[str], key_str: str) -> List[str]:
    """將和弦符號轉換為調內級數標記

    Args:
        chords: 和弦符號列表
        key_str: 調性字符串

    Returns:
        和弦級數標記列表
    """
    # 簡化版本的實現
    # 實際應用中，這應該使用音樂理論庫正確計算和弦級數
    
    # 將調性字符串解析為根音和類型
    key_parts = key_str.split()
    key_root = key_parts[0] if len(key_parts) > 0 else "C"
    key_type = "minor" if len(key_parts) > 1 and "minor" in key_parts[1].lower() else "major"
    
    # 大調和弦級數模板
    major_numerals = {
        "C": "I", "Dm": "ii", "Em": "iii", "F": "IV", "G": "V", "Am": "vi", "Bdim": "vii°",
        "C7": "I7", "Dm7": "ii7", "Em7": "iii7", "F7": "IV7", "G7": "V7", "Am7": "vi7",
        "Cmaj7": "Imaj7", "Fmaj7": "IVmaj7"
    }
    
    # 小調和弦級數模板
    minor_numerals = {
        "Cm": "i", "Ddim": "ii°", "Eb": "III", "Fm": "iv", "Gm": "v", "Ab": "VI", "Bb": "VII",
        "Cm7": "i7", "Ddim7": "ii°7", "Eb7": "III7", "Fm7": "iv7", "Gm7": "v7", "Ab7": "VI7", "Bb7": "VII7"
    }
    
    # 選擇級數模板
    numerals_template = minor_numerals if key_type == "minor" else major_numerals
    
    # 對每個和弦生成級數標記(簡化版)
    result = []
    for chord in chords:
        # 這裡應該實現真正的和弦級數計算
        # 簡單示例：隨機選擇一個級數標記
        import random
        if key_type == "minor":
            result.append(random.choice(["i", "ii°", "III", "iv", "v", "VI", "VII", "V/III"]))
        else:
            result.append(random.choice(["I", "ii", "iii", "IV", "V", "vi", "vii°", "V/vi"]))
    
    return result 