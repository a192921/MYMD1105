---
name: verilog-large-design-analysis
description: Analyze and report on large Verilog design files (100MB-1GB+) using hybrid detection architecture combining RAG vector search with full-file scanning to prevent incomplete analysis. Use when tasked with analyzing large .v files, generating design reports, tracing signal paths across hierarchies, extracting module structures, or documenting hardware logic from Verilog RTL code. Particularly critical for EDA workflows where missing a single signal connection or module instance could invalidate the entire analysis.
---

# Verilog Large Design Analysis

專門處理大型 Verilog 設計檔案(100MB-1GB+)的混合式分析系統,防止「以偏概全」問題。

## 核心原則:混合偵測架構

**警告:** 純 RAG(檢索增強生成)在硬體邏輯分析中極度危險,因為:
- 硬體正確性需要 100% 完整鏈路
- RAG 本質是「機率性抽樣」
- 可能遺漏關鍵的 CDC、反相器、參數覆寫

**解決方案:** RAG 找位置 + MCP 工具驗證完整性

## 三階段分析流程

### Phase 1: 全域掃描 (Global Skeleton)

**目標:** 建立設計全景地圖,讓 AI 知道「這個檔案裡到底有什麼」

#### 1.1 產生模組清單

```bash
# 使用 ctags 快速索引
ctags --languages=verilog --fields=+ne -R <verilog_file>

# 或用 Python 正則抓取
grep -n "^\s*module\s" <verilog_file> > modules_list.txt
```

#### 1.2 建立階層地圖 (JSON 格式)

使用 `scripts/generate_skeleton.py` 產生結構化索引:

```python
{
  "file_info": {
    "path": "top_design.v",
    "size_mb": 523,
    "total_lines": 1250000
  },
  "modules": [
    {
      "name": "chip_top",
      "line_range": [1, 5000],
      "ports": ["clk", "rst_n", "data_in[31:0]", ...],
      "instances": ["cpu_core", "dma_ctrl", ...],
      "depth": 0
    },
    {
      "name": "cpu_core", 
      "line_range": [5001, 25000],
      "parent": "chip_top",
      "depth": 1
    }
  ],
  "global_defines": ["ADDR_WIDTH", "DATA_WIDTH"],
  "includes": ["defs.vh", "params.vh"]
}
```

**關鍵點:** 儲存每個模組的**確切行號範圍**,供後續精確讀取。

### Phase 2: 結構化檢索 (Structured Retrieval)

**目標:** 使用 RAG 快速定位相關邏輯區域

#### 2.1 向量化策略

**切分粒度:** 以 `always` 塊或 `module` 為單位,而非固定行數

```python
# 好的切分範例
chunks = [
  {
    "type": "always_block",
    "content": "always @(posedge clk) begin ... end",
    "line_range": [1234, 1256],
    "module": "fsm_controller",
    "signals": ["state", "next_state"]
  },
  {
    "type": "module_def",
    "content": "module cpu_core(...); ... endmodule",
    "line_range": [5001, 25000],
    "hierarchy_depth": 1
  }
]
```

#### 2.2 查詢範例

```python
# 查詢: 找出所有 FSM 狀態機
rag_query("finite state machine OR FSM OR state register", top_k=10)

# 回傳: 包含行號的片段
results = [
  {"content": "...", "line_range": [1234, 1256], "module": "fsm_ctrl"},
  ...
]
```

**重要:** RAG 僅用於「導航」,不能作為唯一依據。

### Phase 3: 鏈路追蹤與驗證 (Trace & Verify)

**目標:** 使用 MCP 工具全檔掃描,確保無遺漏

#### 3.1 信號追蹤工具

**MCP Tool: `verilog_trace_signal`**

```python
def verilog_trace_signal(signal_name: str, file_path: str) -> dict:
    """
    全檔掃描信號的所有出現位置
    
    Returns:
    {
      "signal": "data_bus",
      "occurrences": [
        {"line": 1234, "type": "output", "module": "top"},
        {"line": 5678, "type": "input", "module": "cpu_core"},
        {"line": 9012, "type": "assign", "context": "assign data_bus = ..."}
      ],
      "total_count": 3
    }
    """
    # 使用 ripgrep (rg) 快速搜尋
    import subprocess
    result = subprocess.run(
        ['rg', '--line-number', '--with-filename', signal_name, file_path],
        capture_output=True, text=True
    )
    # 解析並分類結果...
```

#### 3.2 一致性檢查

**必須執行的檢查:**

1. **端口一致性:** 模組定義的端口 vs 實例化的連接
2. **位寬檢查:** 信號宣告的位寬是否匹配
3. **驅動源驗證:** 確認信號只有唯一驅動源(或已處理多驅動)
4. **時鐘域檢查:** 追蹤跨時鐘域信號,標註 CDC 處理

**工具呼叫範例:**

```python
# AI 在分析 data_bus 後,必須調用
trace_result = verilog_trace_signal("data_bus", "top.v")

if trace_result["total_count"] != len(rag_retrieved_chunks):
    print("警告: RAG 未找到所有相關代碼,進行全檔補充掃描")
```

#### 3.3 精確範圍讀取

**MCP Tool: `read_line_range`**

```python
def read_line_range(file_path: str, start: int, end: int) -> str:
    """精確讀取指定行範圍的原始碼"""
    with open(file_path) as f:
        lines = f.readlines()[start-1:end]
    return ''.join(lines)
```

**使用時機:** 當 RAG 摘要不清楚或需要驗證細節時

## 報告生成策略

### 由大到小的層次

**Level 0: 介面報告 (Interface Summary)**
- 僅讀取 `module` 定義的 port list
- 快速,無需 RAG

**Level 1: 架構摘要 (Architecture Overview)**  
- 使用階層地圖 + RAG 檢索關鍵模組
- 描述主要數據流和控制邏輯

**Level 2: 詳細分析 (Deep Dive)**
- 針對複雜邏輯,使用 `read_line_range` 讀取原始碼
- 使用 `verilog_trace_signal` 驗證連接性

### 報告必須包含的溯源資訊

**範例格式:**

```markdown
## 模組: cpu_core

### 主要功能
基於第 5001-5050 行的模組定義,cpu_core 是五級流水線處理器核心。

### 關鍵信號: instruction_bus
- **驅動源:** 第 12345 行 (i_cache 模組輸出)
- **使用位置:** 
  - 第 12678 行 (decode 階段)
  - 第 13890 行 (exception handler)
- **驗證狀態:** ✓ 已確認無其他驅動源 (全檔掃描完成)
```

**禁止寫法:** 「根據代碼分析,instruction_bus 連接到...」(未標註行號)

## 防錯機制清單

在生成最終報告前,AI 必須自我檢查:

- [ ] 已讀取完整的階層地圖 (skeleton.json)
- [ ] 每個關鍵信號都用 `verilog_trace_signal` 驗證過
- [ ] 報告中的每個斷言都標註了行號範圍
- [ ] 對於複雜邏輯,已用 `read_line_range` 查看原始碼
- [ ] 已檢查 `include` 和全域 `define`,確認參數覆寫
- [ ] 跨模組信號追蹤時,已驗證完整鏈路(從頂層到葉節點)

## 工具優先級

```
內部工具(如 Google Drive 中的設計文檔)
    ↓
全域掃描工具 (generate_skeleton.py)
    ↓
RAG 向量檢索 (快速定位)
    ↓
MCP 精確工具 (trace_signal, read_line_range)
    ↓
web_search (查詢 Verilog 語法或 EDA 工具文檔)
```

**關鍵原則:** 永遠不要只依賴 RAG,必須用工具驗證完整性。

## 範例工作流程

**User:** 分析這個 500MB 的 SoC 設計,找出所有時鐘域交叉(CDC)位置

**AI 正確做法:**

1. **全域掃描:** 
   ```bash
   python scripts/generate_skeleton.py soc_top.v
   # 產生 skeleton.json,發現有 87 個模組
   ```

2. **RAG 初步檢索:**
   ```python
   rag_query("clock domain crossing OR CDC OR async fifo")
   # 找到 5 個可疑區域
   ```

3. **信號追蹤驗證:**
   ```python
   for signal in ["clk_100mhz", "clk_200mhz", "async_rst"]:
       trace_result = verilog_trace_signal(signal, "soc_top.v")
       # 發現 clk_100mhz 有 23 處使用
   ```

4. **精確讀取可疑區域:**
   ```python
   read_line_range("soc_top.v", 45000, 45200)
   # 確認第 45123 行有未處理的 CDC
   ```

5. **生成報告:** 標註每個 CDC 位置的行號、涉及的時鐘域、是否有同步器

## 常見陷阱與解法

| 陷阱 | 後果 | 解法 |
|------|------|------|
| 只用 RAG 分析 | 遺漏關鍵邏輯 | 必須用 `trace_signal` 全檔驗證 |
| 未讀階層地圖 | 不知道有多少模組 | 先讀 `skeleton.json` |
| 直接跳到細節 | 沒有全局觀 | 遵循 Level 0→1→2 順序 |
| 忽略 `include` 檔案 | 參數定義錯誤 | 檢查 skeleton 的 `includes` 欄位 |
| 未標註行號 | 無法溯源驗證 | 每個斷言都附上 `line_range` |

## 檔案組織

```
skill-folder/
├── SKILL.md (本檔案)
├── scripts/
│   ├── generate_skeleton.py    # 產生階層地圖
│   ├── trace_signal.py          # 信號追蹤工具
│   └── validate_report.py       # 報告驗證腳本
└── references/
    ├── verilog-patterns.md      # 常見 RTL 模式
    └── cdc-checklist.md         # CDC 檢查清單
```

## 總結

**核心理念:** RAG 是圖書目錄,MCP Tool 是翻書的手。只看目錄會以偏概全,但結合目錄與親手翻閱關鍵頁面,就能確保分析的完整性與正確性。

**適用場景:**
- 100MB 以上的單一 Verilog 檔案
- 需要生成設計文檔或審查報告
- 信號追蹤與連接性驗證
- CDC、RDC、結構化分析

**不適用場景:**
- 小型檔案(<10MB),直接讀取即可
- 需要編譯或模擬的任務,請使用 EDA 工具