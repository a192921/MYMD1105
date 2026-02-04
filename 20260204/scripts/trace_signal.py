#!/usr/bin/env python3
"""
Verilog Signal Tracer
全檔掃描並分析信號的所有出現位置

用途: 追蹤信號在整個設計中的使用,避免 RAG 遺漏
"""

import re
import sys
import json
from pathlib import Path
from typing import List, Dict, Any


class VerilogSignalTracer:
    """信號追蹤與分類器"""
    
    SIGNAL_TYPES = {
        'input': r'^\s*input\s+.*\b{signal}\b',
        'output': r'^\s*output\s+.*\b{signal}\b',
        'inout': r'^\s*inout\s+.*\b{signal}\b',
        'wire': r'^\s*wire\s+.*\b{signal}\b',
        'reg': r'^\s*reg\s+.*\b{signal}\b',
        'assign': r'^\s*assign\s+{signal}\s*=',
        'always_lhs': r'^\s*{signal}\s*<=|^\s*{signal}\s*=',  # 賦值左側
        'always_rhs': r'[^a-zA-Z_]{signal}\b(?!\s*[<=])',     # 賦值右側(被讀取)
        'instance_port': r'\.\s*{signal}\s*\(',                # 端口連接
    }
    
    def __init__(self, verilog_file: str):
        self.file_path = Path(verilog_file)
        
    def trace(self, signal_name: str) -> Dict[str, Any]:
        """追蹤指定信號的所有出現位置"""
        print(f"[INFO] 追蹤信號: {signal_name} 於檔案: {self.file_path}")
        
        occurrences = []
        current_module = None
        
        with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, start=1):
            # 追蹤當前所在模組
            module_match = re.match(r'^\s*module\s+(\w+)', line)
            if module_match:
                current_module = module_match.group(1)
            
            # 檢查該行是否包含目標信號
            if signal_name not in line:
                continue
            
            # 分類信號類型
            signal_type = self._classify_signal(line, signal_name)
            
            if signal_type:
                occurrences.append({
                    "line": line_num,
                    "type": signal_type,
                    "module": current_module,
                    "context": line.strip()
                })
        
        # 組裝結果
        result = {
            "signal": signal_name,
            "file": str(self.file_path),
            "total_count": len(occurrences),
            "occurrences": occurrences,
            "summary": self._generate_summary(occurrences)
        }
        
        return result
    
    def _classify_signal(self, line: str, signal: str) -> str:
        """判斷信號在該行的使用類型"""
        for sig_type, pattern in self.SIGNAL_TYPES.items():
            regex = pattern.format(signal=re.escape(signal))
            if re.search(regex, line):
                return sig_type
        
        # 如果沒有匹配到特定類型,歸類為 reference
        return "reference"
    
    def _generate_summary(self, occurrences: List[Dict]) -> Dict[str, Any]:
        """產生信號使用摘要"""
        type_counts = {}
        modules = set()
        
        for occ in occurrences:
            sig_type = occ['type']
            type_counts[sig_type] = type_counts.get(sig_type, 0) + 1
            if occ['module']:
                modules.add(occ['module'])
        
        # 判斷驅動源數量
        driver_types = ['output', 'reg', 'assign', 'always_lhs']
        driver_count = sum(type_counts.get(t, 0) for t in driver_types)
        
        return {
            "type_distribution": type_counts,
            "modules_involved": sorted(list(modules)),
            "driver_count": driver_count,
            "has_multiple_drivers": driver_count > 1
        }


def main():
    if len(sys.argv) < 3:
        print("用法: python trace_signal.py <verilog_file> <signal_name> [output_json]")
        print("範例: python trace_signal.py soc_top.v data_bus result.json")
        sys.exit(1)
    
    verilog_file = sys.argv[1]
    signal_name = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    # 追蹤信號
    tracer = VerilogSignalTracer(verilog_file)
    result = tracer.trace(signal_name)
    
    # 輸出結果
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"[SUCCESS] 追蹤結果已儲存至: {output_file}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 顯示摘要
    print(f"\n=== 追蹤摘要 ===")
    print(f"信號名稱: {result['signal']}")
    print(f"出現次數: {result['total_count']}")
    print(f"涉及模組: {len(result['summary']['modules_involved'])}")
    print(f"驅動源數量: {result['summary']['driver_count']}")
    
    if result['summary']['has_multiple_drivers']:
        print("⚠️  警告: 檢測到多個驅動源,可能存在衝突!")
    
    # 顯示類型分佈
    print("\n類型分佈:")
    for sig_type, count in sorted(result['summary']['type_distribution'].items()):
        print(f"  {sig_type}: {count}")


if __name__ == "__main__":
    main()