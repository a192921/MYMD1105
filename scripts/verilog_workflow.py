#!/usr/bin/env python3
"""
Complete workflow: Split Verilog file and generate design reports for each chunk.
"""
import sys
import os
from pathlib import Path
import subprocess


def run_workflow(input_file, cli_path="script/cli.py", max_lines=500, output_base_dir=None):
    """
    Complete workflow to split Verilog and generate reports.
    
    Args:
        input_file: Path to the input Verilog file
        cli_path: Path to the CLI script
        max_lines: Maximum lines per chunk
        output_base_dir: Base directory for all outputs
    
    Returns:
        Dictionary with workflow results
    """
    input_path = Path(input_file)
    base_name = input_path.stem
    
    # Set up output directories
    if output_base_dir is None:
        output_base_dir = Path.cwd() / f"{base_name}_workflow"
    else:
        output_base_dir = Path(output_base_dir)
    
    chunks_dir = output_base_dir / "chunks"
    reports_dir = output_base_dir / "reports"
    
    print(f"{'='*60}")
    print(f"VERILOG DESIGN REPORT WORKFLOW")
    print(f"{'='*60}")
    print(f"Input file: {input_file}")
    print(f"Output directory: {output_base_dir}")
    print(f"CLI path: {cli_path}")
    print(f"Max lines per chunk: {max_lines}")
    print(f"{'='*60}\n")
    
    # Step 1: Split the Verilog file
    print("STEP 1: Splitting Verilog file...")
    print("-" * 60)
    
    script_dir = Path(__file__).parent
    split_script = script_dir / "split_verilog.py"
    
    split_cmd = ["python", str(split_script), input_file, str(chunks_dir), str(max_lines)]
    result = subprocess.run(split_cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error splitting file: {result.stderr}")
        return {"success": False, "error": "Failed to split Verilog file"}
    
    print(result.stdout)
    
    # Get list of created chunk files
    chunk_files = sorted(chunks_dir.glob("*.v"))
    
    if not chunk_files:
        print("Error: No chunk files were created")
        return {"success": False, "error": "No chunks created"}
    
    print(f"\nCreated {len(chunk_files)} chunk files\n")
    
    # Step 2: Run design_report on each chunk
    print("\nSTEP 2: Generating design reports...")
    print("-" * 60)
    
    batch_script = script_dir / "batch_design_report.py"
    
    batch_cmd = [
        "python", str(batch_script),
        *[str(f) for f in chunk_files],
        "--cli-path", cli_path,
        "--output-dir", str(reports_dir)
    ]
    
    result = subprocess.run(batch_cmd, capture_output=True, text=True)
    print(result.stdout)
    
    if result.stderr:
        print(f"Warnings/Errors:\n{result.stderr}")
    
    # Step 3: Summary
    print(f"\n{'='*60}")
    print("WORKFLOW COMPLETE")
    print(f"{'='*60}")
    print(f"Chunks directory: {chunks_dir}")
    print(f"Reports directory: {reports_dir}")
    
    report_files = list(reports_dir.glob("*_report.txt"))
    print(f"\nGenerated {len(report_files)} reports:")
    for report in sorted(report_files):
        print(f"  - {report.name}")
    
    return {
        "success": result.returncode == 0,
        "chunks_dir": str(chunks_dir),
        "reports_dir": str(reports_dir),
        "num_chunks": len(chunk_files),
        "num_reports": len(report_files)
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verilog_workflow.py <input_file> [options]")
        print("\nOptions:")
        print("  --cli-path <path>       Path to cli.py (default: script/cli.py)")
        print("  --max-lines <number>    Max lines per chunk (default: 500)")
        print("  --output-dir <dir>      Base output directory")
        print("\nExample:")
        print("  python verilog_workflow.py assets/top_1.v --cli-path script/cli.py")
        sys.exit(1)
    
    input_file = sys.argv[1]
    cli_path = "script/cli.py"
    max_lines = 500
    output_dir = None
    
    # Parse optional arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--cli-path" and i + 1 < len(sys.argv):
            cli_path = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--max-lines" and i + 1 < len(sys.argv):
            max_lines = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--output-dir" and i + 1 < len(sys.argv):
            output_dir = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)
    
    result = run_workflow(input_file, cli_path, max_lines, output_dir)
    
    if not result.get("success", False):
        sys.exit(1)