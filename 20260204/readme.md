# Verilog Large Design Analysis Skill - 使用範例

## 快速開始

### 1. 產生階層地圖

```bash
python scripts/generate_skeleton.py test_design.v skeleton.json
```

**輸出範例:**
```json
{
  "file_info": {
    "path": "test_design.v",
    "size_mb": 0.01,
    "total_lines": 98,
    "total_modules": 3
  },
  "modules": [
    {
      "name": "chip_top",
      "line_range": [7, 35],
      "ports": ["clk_100mhz", "clk_pcie", "rst_n", "data_in", "data_out", "interrupt"],
      "instances": ["cpu_core", "pcie_interface"],
      "depth": 0
    }
  ]
}
```

### 2. 追蹤信號

```bash
python scripts/trace_signal.py test_design.v data_bus
```

**輸出範例:**
```
=== 追蹤摘要 ===
信號名稱: data_bus
出現次數: 4
涉及模組: 2
驅動源數量: 1

類型分佈:
  output: 1
  always_lhs: 1
  instance_port: 1
  reference: 1
```

### 3. 驗證報告品質

假設你已經用 AI 生成了設計報告 `design_report.md`:

```bash
python scripts/validate_report.py design_report.md
```

**可能的輸出:**
```
============================================================
驗證結果
============================================================

建議改進:
  ⚠️  報告中有 8 處模糊表述,建議改用明確的行號引用

✓ 報告通過基本驗證,但有改進空間
```

## 工具測試

### 測試 generate_skeleton.py

```bash
cd verilog-large-design-analysis
python scripts/generate_skeleton.py test_design.v test_skeleton.json
cat test_skeleton.json
```

### 測試 trace_signal.py

```bash
# 追蹤 FSM 狀態信號
python scripts/trace_signal.py test_design.v state

# 追蹤 CDC 同步信號
python scripts/trace_signal.py test_design.v sync_ff1
```

### 測試 validate_report.py

首先建立一個測試報告:

```bash
cat > test_report.md << 'EOF'
# 設計分析報告

## 模組: chip_top (第 7-35 行)

chip_top 是頂層模組,實例化了 cpu_core 和 pcie_interface。

### 關鍵信號: data_bus
- **驅動源:** 第 72 行 (cpu_core 模組內部)
- **使用位置:** 第 24 行 (連接到 cpu_inst)
- **驗證狀態:** ✓ 已確認唯一驅動源 (全檔掃描完成)

## CDC 檢查

找到一個 CDC 同步器 (第 85-93 行):
- sync_signal → sync_ff1 → sync_ff2
- ✓ 正確使用雙觸發器同步
EOF

python scripts/validate_report.py test_report.md
```

## 整合到 AI 工作流程

當 AI 收到「分析這個大型 Verilog 檔案」的請求時:

1. **Phase 1 - 全域掃描:**
   ```python
   # AI 執行
   bash("python scripts/generate_skeleton.py large_design.v skeleton.json")
   skeleton = read_json("skeleton.json")
   # 現在 AI 知道有多少模組、階層關係
   ```

2. **Phase 2 - RAG 檢索:**
   ```python
   # AI 使用向量資料庫
   results = rag_query("FSM state machine")
   # 得到可疑的區域和行號
   ```

3. **Phase 3 - 精確驗證:**
   ```python
   # AI 驗證 RAG 結果的完整性
   trace_result = bash("python scripts/trace_signal.py large_design.v state_reg")
   # 確認沒有遺漏任何 state_reg 的使用
   ```

4. **Phase 4 - 生成報告並驗證:**
   ```python
   # AI 寫完報告後
   bash("python scripts/validate_report.py design_report.md")
   # 自動檢查報告品質
   ```

## 預期效果

使用此 skill 後,AI 應該能:

✓ 避免「只看到樹木,沒看到森林」的問題  
✓ 在報告中明確標註每個斷言的來源行號  
✓ 發現 RAG 可能遺漏的關鍵邏輯  
✓ 正確識別並檢查 CDC、FSM 等常見模式  
✓ 產生可追溯、可驗證的高品質報告  

## 文件結構

```
verilog-large-design-analysis/
├── SKILL.md                        # 主 skill 定義
├── scripts/                        # 工具腳本
│   ├── generate_skeleton.py        # 產生階層地圖
│   ├── trace_signal.py             # 信號追蹤
│   └── validate_report.py          # 報告驗證
├── references/                     # 參考文件
│   ├── verilog-patterns.md         # RTL 模式識別
│   └── cdc-checklist.md            # CDC 檢查清單
└── test_design.v                   # 測試用 Verilog 檔案
```