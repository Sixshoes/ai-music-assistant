#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
簡化版MCP服務測試腳本
"""

import os
import sys
import argparse
from simplified_mcp import SimplifiedMCP

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="簡化版MCP服務測試腳本")
    parser.add_argument("--description", "-d", type=str, default="創作一首爵士風格的輕快旋律", help="音樂描述")
    parser.add_argument("--output", "-o", type=str, default="output/simplified_mcp_output.mid", help="輸出MIDI文件路徑")
    parser.add_argument("--key", "-k", type=str, default="C", help="調性")
    parser.add_argument("--tempo", "-t", type=int, default=120, help="速度")
    
    args = parser.parse_args()
    
    # 確保輸出目錄存在
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    
    # 初始化MCP服務
    mcp = SimplifiedMCP()
    
    # 設置參數
    params = {
        "description": args.description,
        "key": args.key,
        "tempo": args.tempo
    }
    
    # 生成完整音樂
    result = mcp.generate_musical_idea(params, args.output)
    
    # 打印結果
    print(f"\n音樂已生成並保存到: {args.output}")
    print(f"風格: {result['style']}")
    print(f"旋律長度: {result['melody_length']} 音符")
    print(f"和弦進行: {', '.join(result['chord_progression'])}")
    print(f"低音音符: {result['bass_notes']} 個")
    print(f"鼓聲部音符: {result['drum_notes']} 個")

if __name__ == "__main__":
    main() 