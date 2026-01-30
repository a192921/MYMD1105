#!/usr/bin/env python3
"""
Split a Verilog file into smaller chunks based on module boundaries.
"""
import re
import sys
import os
from pathlib import Path


def split_verilog_file(input_file, output_dir, max_lines=500):
    """
    Split a Verilog file into smaller files.
    
    Args:
        input_file: Path to the input Verilog file
        output_dir: Directory to save the split files
        max_lines: Maximum number of lines per chunk (default: 500)
    
    Returns:
        List of created file paths
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    input_path = Path(input_file)
    base_name = input_path.stem
    
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Try to split by module boundaries
    module_pattern = r'(module\s+\w+.*?endmodule)'
    modules = re.findall(module_pattern, content, re.DOTALL)
    
    created_files = []
    
    if modules:
        # Split by modules
        for i, module in enumerate(modules, 1):
            output_file = output_dir / f"{base_name}_module_{i}.v"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(module)
            created_files.append(str(output_file))
            print(f"Created: {output_file}")
    else:
        # Fallback: split by line count
        lines = content.split('\n')
        num_chunks = (len(lines) + max_lines - 1) // max_lines
        
        for i in range(num_chunks):
            start_idx = i * max_lines
            end_idx = min((i + 1) * max_lines, len(lines))
            chunk = '\n'.join(lines[start_idx:end_idx])
            
            output_file = output_dir / f"{base_name}_chunk_{i+1}.v"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(chunk)
            created_files.append(str(output_file))
            print(f"Created: {output_file}")
    
    return created_files


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python split_verilog.py <input_file> <output_dir> [max_lines]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    max_lines = int(sys.argv[3]) if len(sys.argv) > 3 else 500
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)
    
    created_files = split_verilog_file(input_file, output_dir, max_lines)
    print(f"\nTotal files created: {len(created_files)}")
    print("\nCreated files:")
    for f in created_files:
        print(f"  - {f}")