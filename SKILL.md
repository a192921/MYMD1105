---
name: verilog-design-report
description: Automate Verilog file processing and design report generation. Use when you need to (1) split large Verilog files into manageable chunks, (2) run design_report analysis on Verilog code, (3) batch process multiple Verilog files, or (4) execute the complete workflow of splitting and analyzing Verilog designs. Triggered by requests involving .v files, Verilog processing, design reports, or CLI tool automation with script/cli.py.
---

# Verilog Design Report

## Overview

This skill automates the process of splitting large Verilog files and generating design reports using a CLI tool. It provides a complete workflow for processing Verilog designs at scale.

## Workflow

### Complete Workflow (Recommended)

Use `scripts/verilog_workflow.py` for the end-to-end process:

```bash
python scripts/verilog_workflow.py <input_file> [options]

Options:
  --cli-path <path>       Path to cli.py (default: script/cli.py)
  --max-lines <number>    Max lines per chunk (default: 500)
  --output-dir <dir>      Base output directory
```

**Example:**
```bash
python scripts/verilog_workflow.py assets/top_1.v --cli-path script/cli.py
```

This workflow:
1. Splits the input Verilog file into smaller chunks
2. Runs design_report on each chunk
3. Saves all results in organized directories

**Output structure:**
```
<input_basename>_workflow/
├── chunks/              # Split Verilog files
│   ├── top_1_module_1.v
│   ├── top_1_module_2.v
│   └── ...
└── reports/             # Generated reports
    ├── top_1_module_1_report.txt
    ├── top_1_module_2_report.txt
    └── ...
```

### Individual Operations

#### Split Verilog Files

Use `scripts/split_verilog.py` to split a large Verilog file:

```bash
python scripts/split_verilog.py <input_file> <output_dir> [max_lines]
```

**Splitting strategy:**
- First attempts to split by module boundaries (module...endmodule)
- Falls back to line-count splitting if no modules found
- Default chunk size: 500 lines

**Example:**
```bash
python scripts/split_verilog.py assets/top_1.v ./chunks 500
```

#### Batch Process Files

Use `scripts/batch_design_report.py` to run design_report on multiple files:

```bash
python scripts/batch_design_report.py <file1.v> [file2.v ...] [options]

Options:
  --cli-path <path>    Path to cli.py (default: script/cli.py)
  --output-dir <dir>   Directory to save reports
```

**Example:**
```bash
python scripts/batch_design_report.py chunks/*.v \
  --cli-path script/cli.py \
  --output-dir reports
```

## Usage Patterns

### Pattern 1: Quick Split and Process

When a user provides a Verilog file and asks to process it:

1. Run the complete workflow script
2. Provide summary of chunks and reports created
3. Offer to examine specific reports if needed

### Pattern 2: Custom Processing

When a user needs specific chunk sizes or custom paths:

1. Use individual scripts with custom parameters
2. Chain operations as needed
3. Validate outputs before proceeding

### Pattern 3: Analyzing Results

After generating reports:

1. List generated report files
2. Read and summarize key findings
3. Identify patterns or issues across chunks

## Error Handling

All scripts include error handling for:
- Missing input files
- Failed subprocess calls
- Timeout protection (5 minute limit per file)
- Permission issues

Check script exit codes and stderr output for debugging.

## Requirements

- Python 3.6+
- Valid path to `script/cli.py` with `design_report` command
- Read/write permissions for input/output directories

## Scripts Reference

### scripts/verilog_workflow.py
Complete automated workflow combining splitting and report generation.

### scripts/split_verilog.py
Splits Verilog files by module boundaries or line count.

### scripts/batch_design_report.py
Batch processes multiple Verilog files through design_report CLI.