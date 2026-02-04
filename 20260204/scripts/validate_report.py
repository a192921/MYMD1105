#!/usr/bin/env python3
"""
Design Report Validator
驗證生成的設計報告是否符合品質要求

檢查項目:
1. 是否包含行號溯源
2. 關鍵信號是否經過追蹤驗證
3. 階層地圖是否已參考
"""

import re
import sys
import json
from pathlib import Path
from typing import List, Dict, Tuple


class ReportValidator:
    """設計報告驗證器"""
    
    def __init__(self, report_file: str):
        self.report_path = Path(report_file)
        self.issues = []
        self.warnings = []
        
    def validate(self) -> Tuple[bool, List[str], List[str]]:
        """執行所有驗證檢查"""
        print(f"[INFO] 驗證報告: {self.report_path}")
        
        with open(self.report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查項目
        self._check_line_references(content)
        self._check_verification_markers(content)
        self._check_skeleton_reference(content)
        self._check_signal_trace_evidence(content)
        self._check_vague_statements(content)
        
        # 判定結果
        is_valid = len(self.issues) == 0
        
        return is_valid, self.issues, self.warnings
    
    def _check_line_references(self, content: str):
        """檢查是否包含行號溯源"""
        # 尋找行號引用格式: "第 1234 行" 或 "行 1234-5678"
        line_ref_pattern = r'第?\s*\d+(?:-\d+)?\s*行|line[s]?\s+\d+(?:-\d+)?'
        matches = re.findall(line_ref_pattern, content, re.IGNORECASE)
        
        if len(matches) < 3:
            self.issues.append(
                "❌ 報告中缺乏足夠的行號引用(至少應有3處),無法溯源驗證"
            )
        else:
            print(f"✓ 找到 {len(matches)} 處行號引用")
    
    def _check_verification_markers(self, content: str):
        """檢查是否標註驗證狀態"""
        # 尋找驗證標記: "✓ 已確認" 或 "已驗證" 或 "全檔掃描"
        verify_markers = [
            r'[✓✔]\s*已確認',
            r'已驗證',
            r'全檔掃描',
            r'trace.*完成',
        ]
        
        found_any = False
        for pattern in verify_markers:
            if re.search(pattern, content, re.IGNORECASE):
                found_any = True
                break
        
        if not found_any:
            self.warnings.append(
                "⚠️  報告中未明確標註驗證狀態(建議加入 '✓ 已確認' 等標記)"
            )
    
    def _check_skeleton_reference(self, content: str):
        """檢查是否參考階層地圖"""
        skeleton_keywords = [
            'skeleton',
            '階層地圖',
            '全景',
            'module.*總數',
            '共.*個模組',
        ]
        
        found_any = False
        for keyword in skeleton_keywords:
            if re.search(keyword, content, re.IGNORECASE):
                found_any = True
                break
        
        if not found_any:
            self.warnings.append(
                "⚠️  報告似乎未參考階層地圖,可能遺漏整體架構分析"
            )
    
    def _check_signal_trace_evidence(self, content: str):
        """檢查是否有信號追蹤的證據"""
        trace_patterns = [
            r'驅動源.*\d+',
            r'出現.*\d+.*次',
            r'trace.*signal',
            r'全檔.*搜尋',
        ]
        
        found_count = 0
        for pattern in trace_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                found_count += 1
        
        if found_count == 0:
            self.issues.append(
                "❌ 報告中未顯示信號追蹤證據,可能僅依賴 RAG 而未進行全檔驗證"
            )
        elif found_count < 2:
            self.warnings.append(
                "⚠️  信號追蹤證據較少,建議增加驗證資訊"
            )
    
    def _check_vague_statements(self, content: str):
        """檢查是否有模糊的斷言(未標註來源)"""
        vague_patterns = [
            r'根據(?:代碼)?分析',
            r'看起來',
            r'似乎',
            r'可能是',
            r'應該是',
        ]
        
        vague_count = 0
        for pattern in vague_patterns:
            matches = re.findall(pattern, content)
            vague_count += len(matches)
        
        if vague_count > 5:
            self.warnings.append(
                f"⚠️  報告中有 {vague_count} 處模糊表述,建議改用明確的行號引用"
            )


def main():
    if len(sys.argv) < 2:
        print("用法: python validate_report.py <report_file>")
        print("範例: python validate_report.py design_report.md")
        sys.exit(1)
    
    report_file = sys.argv[1]
    
    # 驗證報告
    validator = ReportValidator(report_file)
    is_valid, issues, warnings = validator.validate()
    
    # 輸出結果
    print("\n" + "="*60)
    print("驗證結果")
    print("="*60)
    
    if issues:
        print("\n嚴重問題:")
        for issue in issues:
            print(f"  {issue}")
    
    if warnings:
        print("\n建議改進:")
        for warning in warnings:
            print(f"  {warning}")
    
    if is_valid and not warnings:
        print("\n✓ 報告通過所有驗證檢查!")
    elif is_valid:
        print("\n✓ 報告通過基本驗證,但有改進空間")
    else:
        print(f"\n❌ 報告存在 {len(issues)} 個嚴重問題,需要修正")
    
    # 返回狀態碼
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()