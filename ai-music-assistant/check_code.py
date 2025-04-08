#!/usr/bin/env python3
"""
代碼檢查腳本

用於檢查項目中的常見問題，並報告可能的修復建議
"""

import os
import sys
import re
from pathlib import Path

FRONTEND_DIR = Path('./frontend')
BACKEND_DIR = Path('./backend')
MCP_DIR = Path('./mcp')

def check_file(filepath):
    """檢查文件中的問題"""
    issues = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            content = f.read()
        except UnicodeDecodeError:
            issues.append(f"無法讀取文件 {filepath}: 編碼錯誤")
            return issues
    
    # 檢查 TypeScript/JavaScript 問題
    if filepath.suffix in ['.ts', '.tsx', '.js', '.jsx']:
        # 檢查未使用的變數
        unused_vars = re.findall(r'const\s+(\w+)\s*=.*?\/\/\s*eslint-disable.*?no-unused-vars', content)
        if unused_vars:
            issues.append(f"發現未使用的變數: {', '.join(unused_vars)}")
        
        # 檢查audioData vs audioUrl
        if 'audioData' in content and '<MusicPlayer' in content:
            issues.append("發現使用 audioData 作為 MusicPlayer 屬性，應該改為 audioUrl")
        
    # 檢查 Python 問題
    if filepath.suffix == '.py':
        # 檢查導入錯誤
        if 'ImportError' in content and not ('try:' in content and 'except ImportError' in content):
            issues.append("發現可能沒有處理的導入錯誤")
        
        # 檢查對pydantic的依賴
        if 'from pydantic import' in content and 'try:' not in content:
            issues.append("使用了pydantic但沒有處理可能的導入錯誤")
    
    return issues

def scan_directory(directory, ignore_dirs=None):
    """掃描目錄中的所有文件"""
    if ignore_dirs is None:
        ignore_dirs = ['.git', 'node_modules', '__pycache__', 'venv', '.venv']
    
    issues_by_file = {}
    
    for root, dirs, files in os.walk(directory):
        # 跳過忽略的目錄
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            if file.startswith('.'):
                continue
                
            filepath = Path(root) / file
            
            # 只檢查特定類型的文件
            if filepath.suffix in ['.ts', '.tsx', '.js', '.jsx', '.py']:
                file_issues = check_file(filepath)
                if file_issues:
                    issues_by_file[str(filepath)] = file_issues
    
    return issues_by_file

def main():
    """主函數"""
    print("開始代碼檢查...\n")
    
    # 掃描前端代碼
    if FRONTEND_DIR.exists():
        print(f"掃描前端目錄: {FRONTEND_DIR}")
        frontend_issues = scan_directory(FRONTEND_DIR)
        if frontend_issues:
            print(f"\n發現前端問題 ({len(frontend_issues)} 個文件):")
            for file, issues in frontend_issues.items():
                print(f"\n  {file}:")
                for issue in issues:
                    print(f"    - {issue}")
        else:
            print("前端代碼檢查通過！")
    else:
        print(f"前端目錄不存在: {FRONTEND_DIR}")
    
    # 掃描後端代碼
    if BACKEND_DIR.exists():
        print(f"\n掃描後端目錄: {BACKEND_DIR}")
        backend_issues = scan_directory(BACKEND_DIR)
        if backend_issues:
            print(f"\n發現後端問題 ({len(backend_issues)} 個文件):")
            for file, issues in backend_issues.items():
                print(f"\n  {file}:")
                for issue in issues:
                    print(f"    - {issue}")
        else:
            print("後端代碼檢查通過！")
    else:
        print(f"後端目錄不存在: {BACKEND_DIR}")
    
    # 掃描MCP目錄
    if MCP_DIR.exists():
        print(f"\n掃描MCP目錄: {MCP_DIR}")
        mcp_issues = scan_directory(MCP_DIR)
        if mcp_issues:
            print(f"\n發現MCP問題 ({len(mcp_issues)} 個文件):")
            for file, issues in mcp_issues.items():
                print(f"\n  {file}:")
                for issue in issues:
                    print(f"    - {issue}")
        else:
            print("MCP代碼檢查通過！")
    else:
        print(f"MCP目錄不存在: {MCP_DIR}")
    
    print("\n代碼檢查完成")

if __name__ == "__main__":
    main() 