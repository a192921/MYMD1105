# Assets Directory

This directory is reserved for any Verilog files or templates that should be included with the skill.

## Suggested Usage

Place your Verilog files here for processing. For example:
- `assets/top_1.v` - Your main Verilog design file
- `assets/templates/` - Any Verilog templates or reference designs

## Example

If you have a Verilog file at `assets/top_1.v`, you can process it with:

```bash
python scripts/verilog_workflow.py assets/top_1.v
```

This will create a workflow output directory with all chunks and reports.