# 自動文檔分割工具 (Auto Document Splitter)

## 📌 功能簡介

自動偵測並分割大型 Markdown 文檔為 AI 友善的可讀取大小（≤ 25,000 tokens）。

### 主要功能

1. **自動分析**：偵測文件大小並估算 token 數量
2. **智能分割**：自動識別章節邊界（## 二級標題）作為分割點
3. **品質評分**：為每個候選分割點計算品質分數，選擇最佳位置
4. **導航生成**：自動生成雙向導航連結和索引文件
5. **Windows 兼容**：處理 Windows 編碼問題，確保跨平台運作

---

## 🚀 快速開始

### 基本用法

```bash
# 分析文檔（不執行分割）
python scripts/auto_split_docs.py docs/YOUR_FILE.md --analyze-only

# 試運行模式（顯示分割計畫但不寫入文件）
python scripts/auto_split_docs.py docs/YOUR_FILE.md --dry-run

# 執行分割
python scripts/auto_split_docs.py docs/YOUR_FILE.md
```

### 進階選項

```bash
# 自訂 token 限制（預設 25000）
python scripts/auto_split_docs.py docs/YOUR_FILE.md --max-tokens 20000

# 查看幫助
python scripts/auto_split_docs.py --help
```

---

## 📖 使用範例

### 範例 1: 分析文檔

```bash
$ python scripts/auto_split_docs.py docs/CLAUDE_CODE_HANDOVER-2.md --analyze-only

正在分析文檔: CLAUDE_CODE_HANDOVER-2.md
============================================================
基本資訊:
   - 總行數: 3,277 行
   - 總字元數: 92,180 字元
   - 檔案大小: 92.20 KB
   - 估算 Tokens: ~40,028 tokens

章節結構:
   - Level 1 (#): 1 個章節
   - Level 2 (##): 13 個章節
   - Level 3 (###): 87 個章節
   - Level 4 (####): 126 個章節

分割需求:
   ⚠️  需要分割 (超過 25,000 token 限制)
   建議分割為: 2 段

✅ 分析完成
```

### 範例 2: 試運行分割

```bash
$ python scripts/auto_split_docs.py docs/CLAUDE_CODE_HANDOVER-2.md --dry-run

# ... 分析輸出 ...

============================================================
開始分割程序
============================================================

尋找最佳分割點...
   ✅ 找到 1 個分割點:

   1. 行 2066: GUI 開發計畫 (2025-11-24 規劃)
      - 之前: ~20,156 tokens
      - 之後: ~19,872 tokens
      - 分數: 87.3/100

創建分割段落...
   ✅ 創建 2 個段落:

   - 2A 段: CLAUDE_CODE_HANDOVER-2A.md
     行數: 1-2065 (2,065 行)
     Tokens: ~20,156
     章節數: 6

   - 2B 段: CLAUDE_CODE_HANDOVER-2B.md
     行數: 2066-3277 (1,212 行)
     Tokens: ~19,872
     章節數: 7

🔍 Dry-run 模式 - 不寫入檔案
```

### 範例 3: 執行分割

```bash
$ python scripts/auto_split_docs.py docs/CLAUDE_CODE_HANDOVER-2.md

# ... 分析與分割點輸出 ...

寫入分割文件...
   ✅ CLAUDE_CODE_HANDOVER-2A.md (2,065 行)
   ✅ CLAUDE_CODE_HANDOVER-2B.md (1,212 行)

生成導航索引...
   ✅ CLAUDE_CODE_HANDOVER-2.md (索引文件)

============================================================
✅ 分割完成！
============================================================

驗證報告:
   - 原始文件: 3,277 行, ~40,028 tokens
   - 分割段數: 2 段
   - 輸出文件: 3 個 (2 段 + 1 索引)

   請使用 AI 助手驗證以下文件可正常讀取:
   - CLAUDE_CODE_HANDOVER-2A.md
   - CLAUDE_CODE_HANDOVER-2B.md
   - CLAUDE_CODE_HANDOVER-2.md (索引)
```

---

## 🔧 工作原理

### 1. Token 估算

使用以下係數估算 token 數量：

- **中文字元**: ~2.5 tokens/字
- **英文單字**: ~1.3 tokens/字
- **程式碼**: ~1.5 tokens/字

### 2. 章節識別

解析 Markdown 標題層級（# 到 ######），建立章節樹狀結構。

### 3. 分割點評分

為每個候選分割點（二級標題 ##）計算品質分數，考量：

1. **接近理想大小** (50%)：與理想段落大小的接近程度
2. **避免過小段落** (30%)：確保每段都超過最小大小（15,000 tokens）
3. **段落平衡度** (20%)：前後段落大小的平衡性

### 4. 導航生成

自動為每個分割段落添加：

- **標頭導航**：連結到上一段、下一段、索引
- **結尾導航**：連結到下一段繼續閱讀

索引文件包含：

- 文檔結構概覽
- 每段的內容預覽
- 按主題快速導航
- 閱讀建議

---

## 📊 輸出結果

### 分割後的文件結構

假設原文件為 `DOCUMENT-2.md`，分割後會產生：

```
docs/
├── DOCUMENT-2.md       ← 轉換為導航索引
├── DOCUMENT-2A.md      ← 第一段（含導航標頭）
└── DOCUMENT-2B.md      ← 第二段（含導航標頭）
```

### 導航標頭範例

```markdown
# DOCUMENT-2 (第 2A 段)

> **分段資訊**: 本文檔共 2 段
> - 📄 **當前**: 第 2A 段
> - ➡️ **下一段**: [DOCUMENT-2B.md](./DOCUMENT-2B.md)
> - 📑 **完整索引**: [返回索引](./DOCUMENT-2.md)

---

[原文檔內容...]

---

**本段結束**

📍 **繼續閱讀**: [DOCUMENT-2B.md](./DOCUMENT-2B.md)
```

---

## ⚙️ 命令列選項

| 選項 | 說明 | 預設值 |
|------|------|--------|
| `file` | 要分割的 Markdown 文件路徑（必填） | - |
| `--max-tokens` | 每段的最大 token 數量 | 25000 |
| `--dry-run` | 試運行模式，只分析不寫入文件 | False |
| `--analyze-only` | 僅分析文檔，不執行分割 | False |
| `-h, --help` | 顯示幫助訊息 | - |

---

## 📋 適用場景

### ✅ 適合使用

- 大型技術文檔（> 25,000 tokens）
- AI 交接文檔
- 詳細的 API 說明文件
- 長篇教學指南
- 研究報告

### ❌ 不適合使用

- 小型文件（< 15,000 tokens）
- 沒有明確章節結構的文件
- 需要保持為單一文件的內容

---

## 🛠️ 技術細節

### 依賴套件

```python
import re
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
```

**無需額外安裝套件** - 僅使用 Python 標準函式庫！

### 主要類別

- `TokenEstimator`: Token 數量估算
- `ChapterParser`: 章節結構解析
- `DocumentSplitter`: 分割邏輯實作
- `IndexGenerator`: 索引與導航生成

### 編碼處理

工具包含 `safe_print()` 函數處理 Windows 編碼問題：

```python
def safe_print(text: str = "") -> None:
    """安全的 print 函數，處理 Windows 編碼問題"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Windows CMD 不支援某些字元，移除 emoji 後重試
        clean_text = re.sub(r'[^\x00-\x7F\u4e00-\u9fff]+', '', text)
        print(clean_text)
```

---

## 🔍 驗證流程

分割完成後，建議執行以下驗證：

### 1. AI 助手驗證

請 AI 助手讀取所有分割文件，確認：

- ✅ 文件可正常讀取
- ✅ 內容完整無遺失
- ✅ 導航連結正確
- ✅ Token 數量符合限制

### 2. 手動檢查

- 檢查分割點是否在適當的章節邊界
- 確認索引文件包含正確的段落資訊
- 驗證導航連結可正常點擊

---

## 📝 注意事項

1. **原文件會被覆蓋**：原始 Markdown 文件會被轉換為索引文件，建議先備份
2. **僅支援 Markdown**：目前僅支援 `.md` 文件
3. **需要章節結構**：文件必須包含明確的 `##` 二級標題作為分割點
4. **Token 估算為近似值**：實際 token 數可能略有差異（±10%）

---

## 🚨 常見問題

### Q: 找不到合適的分割點怎麼辦？

**A**: 確保文件包含足夠的二級標題（`##`）。若文件全是三級或更低標題，工具無法找到分割點。

### Q: 分割後的段落大小不平衡？

**A**: 工具會盡量平衡，但受限於章節邊界。可以手動調整 `--max-tokens` 參數。

### Q: Windows CMD 顯示亂碼？

**A**: 這是正常現象，不影響功能。亂碼是因為 Windows CMD 編碼限制，實際寫入的文件是正確的 UTF-8 格式。

### Q: 可以分割成 3 段以上嗎？

**A**: 可以！工具會自動計算需要的段數。例如 60,000 tokens 的文件會自動分割為 3 段。

---

## 📜 版本歷史

### v1.0.0 (2025-12-07)

- ✅ 初始版本
- ✅ 支援自動 token 估算
- ✅ 智能章節邊界識別
- ✅ 品質評分系統
- ✅ 自動導航生成
- ✅ Windows 編碼處理

---

## 👤 作者

**專案**: EEBot (Gleipnir)
**維護者**: wizard03
**開發工具**: Claude Code CLI
**日期**: 2025-12-07

---

## 📄 授權

本工具為 EEBot 專案的一部分。

---

**🎯 提示**: 使用 `--dry-run` 先預覽分割計畫，確認無誤後再執行實際分割！
