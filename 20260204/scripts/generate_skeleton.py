#!/usr/bin/env python3
"""
Verilog Design Skeleton Generator
產生 Verilog 設計檔案的階層地圖(JSON格式)

用途: 掃描大型 .v 檔案,提取所有模組定義、階層關係、端口列表
"""

import re
import json
import sys
from pathlib import Path
from typing import List, Dict, Any


class VerilogSkeletonGenerator:
    """解析 Verilog 檔案並產生結構化階層地圖"""
    
    def __init__(self, verilog_file: str):
        self.file_path = Path(verilog_file)
        self.modules = []
        self.global_defines = []
        self.includes = []
        
    def parse(self) -> Dict[str, Any]:
        """主解析函數"""
        print(f"[INFO] 解析檔案: {self.file_path}")
        
        with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            total_lines = content.count('\n') + 1
            
        # 提取全域定義
        self._extract_defines(content)
        self._extract_includes(content)
        
        # 提取所有模組
        self._extract_modules(content)
        
        # 建立階層關係
        self._build_hierarchy()
        
        # 組裝結果
        skeleton = {
            "file_info": {
                "path": str(self.file_path),
                "size_mb": round(self.file_path.stat().st_size / 1024 / 1024, 2),
                "total_lines": total_lines,
                "total_modules": len(self.modules)
            },
            "global_defines": self.global_defines,
            "includes": self.includes,
            "modules": self.modules
        }
        
        print(f"[INFO] 找到 {len(self.modules)} 個模組")
        return skeleton
    
    def _extract_defines(self, content: str):
        """提取 `define 宏定義"""
        pattern = r'`define\s+(\w+)'
        self.global_defines = list(set(re.findall(pattern, content)))
    
    def _extract_includes(self, content: str):
        """提取 `include 檔案"""
        pattern = r'`include\s+"([^"]+)"'
        self.includes = list(set(re.findall(pattern, content)))
    
    def _extract_modules(self, content: str):
        """提取所有 module 定義及其元數據"""
        # 正則: 捕獲 module 名稱與參數列表
        module_pattern = re.compile(
            r'^\s*module\s+(\w+)\s*(?:#\s*\([^)]*\))?\s*\((.*?)\);',
            re.MULTILINE | re.DOTALL
        )
        
        lines = content.split('\n')
        
        for match in module_pattern.finditer(content):
            module_name = match.group(1)
            port_section = match.group(2)
            start_pos = match.start()
            
            # 計算起始行號
            start_line = content[:start_pos].count('\n') + 1
            
            # 尋找對應的 endmodule(簡化版,假設格式規範)
            end_match = re.search(
                r'\bendmodule\b',
                content[start_pos:]
            )
            end_line = start_line + content[start_pos:start_pos + end_match.end()].count('\n') if end_match else start_line + 100
            
            # 解析端口
            ports = self._parse_ports(port_section)
            
            # 提取實例化的子模組
            module_content = content[start_pos:start_pos + (end_match.end() if end_match else 1000)]
            instances = self._extract_instances(module_content)
            
            self.modules.append({
                "name": module_name,
                "line_range": [start_line, end_line],
                "ports": ports,
                "instances": instances,
                "parent": None,  # 後續填入
                "depth": 0        # 後續計算
            })
    
    def _parse_ports(self, port_section: str) -> List[str]:
        """解析端口列表"""
        if not port_section:
            return []
        
        # 移除註解
        port_section = re.sub(r'//.*', '', port_section)
        port_section = re.sub(r'/\*.*?\*/', '', port_section, flags=re.DOTALL)
        
        # 提取端口名稱(支援 input/output/inout 標註)
        port_pattern = r'(?:input|output|inout)?\s*(?:wire|reg)?\s*(?:\[\s*[\w:\s+-]+\s*\])?\s*(\w+)'
        ports = re.findall(port_pattern, port_section)
        
        return ports
    
    def _extract_instances(self, module_content: str) -> List[str]:
        """提取模組內實例化的子模組名稱"""
        # 正則: 捕獲 module_name instance_name (...)
        instance_pattern = r'\b(\w+)\s+(?:#\s*\([^)]*\)\s*)?(\w+)\s*\('
        
        instances = []
        for match in re.finditer(instance_pattern, module_content):
            module_type = match.group(1)
            # 排除 Verilog 關鍵字
            if module_type not in ['input', 'output', 'inout', 'wire', 'reg', 'assign', 
                                   'always', 'initial', 'begin', 'end', 'if', 'else', 'case']:
                instances.append(module_type)
        
        return list(set(instances))  # 去重
    
    def _build_hierarchy(self):
        """建立階層關係(根據實例化推斷父子關係)"""
        module_dict = {m['name']: m for m in self.modules}
        
        # 建立子模組到父模組的映射
        child_to_parent = {}
        for module in self.modules:
            for instance in module['instances']:
                if instance in module_dict:
                    child_to_parent[instance] = module['name']
        
        # 計算深度並填入父模組
        def calc_depth(mod_name, visited=set()):
            if mod_name in visited:
                return 0  # 避免循環
            visited.add(mod_name)
            
            parent = child_to_parent.get(mod_name)
            if not parent:
                return 0  # 頂層模組
            
            return 1 + calc_depth(parent, visited)
        
        for module in self.modules:
            module['parent'] = child_to_parent.get(module['name'])
            module['depth'] = calc_depth(module['name'])
        
        # 排序: 深度由淺到深
        self.modules.sort(key=lambda x: x['depth'])


def main():
    if len(sys.argv) < 2:
        print("用法: python generate_skeleton.py <verilog_file> [output_json]")
        print("範例: python generate_skeleton.py soc_top.v skeleton.json")
        sys.exit(1)
    
    verilog_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "skeleton.json"
    
    # 解析並產生骨架
    generator = VerilogSkeletonGenerator(verilog_file)
    skeleton = generator.parse()
    
    # 輸出 JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(skeleton, f, indent=2, ensure_ascii=False)
    
    print(f"[SUCCESS] 階層地圖已儲存至: {output_file}")
    
    # 顯示摘要
    print(f"\n=== 摘要 ===")
    print(f"檔案大小: {skeleton['file_info']['size_mb']} MB")
    print(f"總行數: {skeleton['file_info']['total_lines']}")
    print(f"模組數量: {skeleton['file_info']['total_modules']}")
    print(f"全域定義: {len(skeleton['global_defines'])} 個")
    print(f"Include 檔案: {len(skeleton['includes'])} 個")
    
    # 顯示頂層模組
    top_modules = [m['name'] for m in skeleton['modules'] if m['depth'] == 0]
    print(f"頂層模組: {', '.join(top_modules)}")


if __name__ == "__main__":
    main()