#!/usr/bin/env python3
"""
Batch process Verilog files with design_report CLI tool.
"""
import subprocess
import sys
import os
from pathlib import Path


def run_design_report(verilog_file, cli_path="script/cli.py"):
    """
    Run design_report on a single Verilog file.
    
    Args:
        verilog_file: Path to the Verilog file
        cli_path: Path to the CLI script (default: script/cli.py)
    
    Returns:
        Tuple of (returncode, stdout, stderr)
    """
    cmd = ["python", cli_path, "design_report", verilog_file]
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Error: Command timed out after 5 minutes"
    except Exception as e:
        return -1, "", f"Error: {str(e)}"


def batch_process_files(file_list, cli_path="script/cli.py", output_dir=None):
    """
    Batch process multiple Verilog files.
    
    Args:
        file_list: List of Verilog file paths
        cli_path: Path to the CLI script
        output_dir: Optional directory to save reports
    
    Returns:
        Dictionary with results for each file
    """
    results = {}
    
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
    
    for verilog_file in file_list:
        print(f"\n{'='*60}")
        print(f"Processing: {verilog_file}")
        print(f"{'='*60}")
        
        returncode, stdout, stderr = run_design_report(verilog_file, cli_path)
        
        results[verilog_file] = {
            'returncode': returncode,
            'stdout': stdout,
            'stderr': stderr,
            'success': returncode == 0
        }
        
        if returncode == 0:
            print(f"✓ Successfully processed {verilog_file}")
            if output_dir:
                # Save output to file
                output_file = output_path / f"{Path(verilog_file).stem}_report.txt"
                with open(output_file, 'w') as f:
                    f.write(stdout)
                print(f"  Report saved to: {output_file}")
        else:
            print(f"✗ Failed to process {verilog_file}")
            if stderr:
                print(f"  Error: {stderr}")
    
    return results


def print_summary(results):
    """Print a summary of batch processing results."""
    print(f"\n{'='*60}")
    print("BATCH PROCESSING SUMMARY")
    print(f"{'='*60}")
    
    total = len(results)
    successful = sum(1 for r in results.values() if r['success'])
    failed = total - successful
    
    print(f"Total files: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    
    if failed > 0:
        print("\nFailed files:")
        for file, result in results.items():
            if not result['success']:
                print(f"  - {file}")
                if result['stderr']:
                    print(f"    Error: {result['stderr'][:100]}...")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python batch_design_report.py <file1.v> [file2.v ...] [--cli-path <path>] [--output-dir <dir>]")
        print("\nOptions:")
        print("  --cli-path <path>    Path to cli.py (default: script/cli.py)")
        print("  --output-dir <dir>   Directory to save reports")
        sys.exit(1)
    
    # Parse arguments
    files = []
    cli_path = "script/cli.py"
    output_dir = None
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--cli-path":
            cli_path = sys.argv[i + 1]
            i += 2
        elif arg == "--output-dir":
            output_dir = sys.argv[i + 1]
            i += 2
        elif not arg.startswith("--"):
            files.append(arg)
            i += 1
        else:
            i += 1
    
    # Validate files exist
    missing_files = [f for f in files if not os.path.exists(f)]
    if missing_files:
        print("Error: The following files do not exist:")
        for f in missing_files:
            print(f"  - {f}")
        sys.exit(1)
    
    # Run batch processing
    results = batch_process_files(files, cli_path, output_dir)
    print_summary(results)
    
    # Exit with error code if any files failed
    if any(not r['success'] for r in results.values()):
        sys.exit(1)