# AI 助手快速讀取交接文檔指南

> **Quick Guide for AI Assistants to Load Handover Documentation**
>
> 本文檔提供各種 AI 程式助手快速讀取 EEBot 專案交接文檔的提示詞範例

**文檔版本**: 1.2
**最後更新**: 2025-12-29
**適用 AI**: Claude Code CLI, Cursor, GitHub Copilot CLI, Cody, Tabnine 等

---

## 🔥 最新優先任務 (2025-12-29)

> **P0 優先**: CAPTCHA OCR 整合到 EEBot 登入流程

**立即讀取**: `docs/CLAUDE_CODE_HANDOVER-8.md`

```
任務摘要:
1. 建立 src/utils/captcha_ocr.py
2. 修改 src/pages/login_page.py
3. 測試完整登入流程

研究成果: 97.6% 準確率 (optimized_ocr.py)
```

---

## 📚 交接文檔位置

```
D:\Dev\eebot\docs\
├── CLAUDE_CODE_HANDOVER-8.md      # ★ 最新交接（2025-12-29）
├── AI_ASSISTANT_GUIDE.md          # 通用 AI 助手指南（英文）
├── TODO.md                        # 待辦事項（含 P0 任務詳情）
├── CAPTCHA_OCR_TECHNICAL_GUIDE.md # CAPTCHA OCR 技術文檔
├── CHANGELOG.md                   # 修改歷史
└── AI助手快速讀取交接文檔.md      # 本文件
```

---

## 🎯 按情境分類的提示詞

### 情境 1：全新對話，需要完整理解專案

#### ⭐ 推薦指令（最完整）
```
請讀取本專案的 AI 工作交接文檔，位於 docs/ 目錄。
特別關注 AI_ASSISTANT_GUIDE.md 和 CLAUDE_CODE_HANDOVER.md，
以及最新的 CHANGELOG.md。
```

#### 簡化版
```
讀取專案交接文檔
```

#### 英文版（適用英文 AI）
```
Read the AI handover documentation in docs/
```

#### 使用 @workspace（Claude Code CLI）
```
@workspace 讀取 docs 目錄的交接文檔
```


---

### 情境 2：只想了解自動答題規劃

#### ⭐ 推薦指令
```
讀取 docs/AI_ASSISTANT_GUIDE.md 和 docs/CHANGELOG.md，
重點查看自動答題功能的規劃（2025-01-14）
```

#### 簡化版
```
查看自動答題功能規劃
```

#### 更明確版
```
讀取 docs/AI_ASSISTANT_GUIDE.md 中的
"Planned Features: Auto-Answer System" 章節
```

---

### 情境 3：準備開始實作自動答題

#### ⭐ 推薦指令
```
我要開始實作自動答題功能，請先讀取：
1. docs/AI_ASSISTANT_GUIDE.md（自動答題規劃章節）
2. docs/CHANGELOG.md（2025-01-14 條目）
3. 郵政E大學114年題庫/ 目錄結構

然後告訴我從哪裡開始。
```

#### 簡化版
```
準備實作自動答題功能，請讀取相關規劃文檔
```

---

### 情境 4：查看專案最新狀態

#### ⭐ 推薦指令
```
查看 docs/CHANGELOG.md 最新修改記錄
```

#### 或
```
專案目前進度如何？請讀取 CHANGELOG
```

---

### 情境 5：需要快速索引整個專案

#### Claude Code CLI 專用
```
@workspace 讀取 docs 目錄的交接文檔
```

#### 或
```
@workspace 查看自動答題功能規劃
```

---

## 🔧 按 AI 工具分類的最佳實踐

### Claude Code CLI（推薦）

#### 方法 1：直接提示（最簡單）
```
讀取專案交接文檔
```

#### 方法 2：使用 @workspace（最快速）
```
@workspace 查看 docs 目錄的 AI 交接文檔
```

#### 方法 3：明確指定文件（最精確）
```
讀取 docs/AI_ASSISTANT_GUIDE.md 和 docs/CHANGELOG.md
```

#### 方法 4：指定路徑（最詳細）
```
請使用 Read 工具讀取以下文件：
- D:\Dev\eebot\docs\AI_ASSISTANT_GUIDE.md
- D:\Dev\eebot\docs\CHANGELOG.md
```

---

### Cursor

#### 使用 Ctrl+K
```
@docs 讀取交接文檔
```

#### 在 Chat 中使用
```
@folder docs 查看 AI 交接文檔
```

#### 明確指定
```
@file docs/AI_ASSISTANT_GUIDE.md
@file docs/CHANGELOG.md
查看自動答題功能規劃
```

---

### GitHub Copilot CLI

#### 解釋文檔目錄
```bash
gh copilot explain "D:\Dev\eebot\docs"
```

#### 詢問專案狀態
```bash
gh copilot suggest "如何開始 eebot 專案的自動答題功能？"
```

---

### Cody

#### 使用 @docs
```
@docs 讀取 AI_ASSISTANT_GUIDE.md 和 CHANGELOG.md
```

#### 使用 @file
```
@file docs/AI_ASSISTANT_GUIDE.md
查看自動答題規劃
```

---

### Tabnine / 其他 AI 助手

#### 通用指令
```
請讀取以下文件並總結專案狀態：
- docs/AI_ASSISTANT_GUIDE.md
- docs/CHANGELOG.md
```

---

## ⭐ 推薦的標準開場白（最佳實踐）

### 方案 A：完整版（推薦給新 AI 助手）
```
你好，我是 eebot 專案的維護者。

請先讀取以下交接文檔以了解專案：
1. docs/AI_ASSISTANT_GUIDE.md
2. docs/CHANGELOG.md

然後告訴我專案目前的狀態，以及自動答題功能的規劃進度。
```

### 方案 B：簡潔版（日常使用）
```
讀取本專案 AI 交接文檔（docs/ 目錄），
特別是自動答題功能的規劃（2025-01-14）。
```

### 方案 C：超簡版（最快速）
```
讀取專案交接文檔
```

---

## 💡 特殊情境提示詞

### 如果 AI 沒有自動讀取文檔
```
請使用 Read 工具讀取以下文件：
- docs/AI_ASSISTANT_GUIDE.md
- docs/CHANGELOG.md
```

### 如果需要查看特定章節
```
讀取 docs/AI_ASSISTANT_GUIDE.md 中的
"Planned Features: Auto-Answer System" 章節
```

### 如果需要對比中英文版本
```
對比 docs/AI_ASSISTANT_GUIDE.md（英文）和
docs/CLAUDE_CODE_HANDOVER.md（中文）中的自動答題規劃
```

### 如果需要查看題庫資料
```
1. 讀取 docs/AI_ASSISTANT_GUIDE.md（自動答題規劃）
2. 分析 郵政E大學114年題庫/ 目錄結構
3. 讀取 郵政E大學114年題庫/總題庫.json 的前 50 行
```

### 如果需要查看考試 HTML 結構
```
讀取 高齡客戶投保權益保障(114年度) - 郵政ｅ大學-exam/4郵政ｅ大學.html
並分析題目和選項的 HTML 元素定位
```

---

## ✅ 驗證 AI 是否正確讀取

AI 讀取完交接文檔後，應該能回答以下問題：

### 基礎驗證（5 題）

1. **專案目前是什麼狀態？**
   - ✅ 正確答案：考試流程已完成（2025-01-13），自動答題規劃中（2025-01-14）

2. **自動答題功能推薦使用什麼資料庫？**
   - ✅ 正確答案：混合模式（SQLite + JSON）

3. **題庫有多少題目？**
   - ✅ 正確答案：1,766 題，5.3 MB，23 個分類

4. **預估實作時間？**
   - ✅ 正確答案：8-11 小時，分 4 階段（MVP → 優化 → SQLite → Production）

5. **哪些文件不能修改？**
   - ✅ 正確答案：
     - `src/scenarios/course_learning.py`
     - `src/pages/exam_detail_page.py`
     - `src/pages/exam_learning.py`
     - 所有 `src/core/*` 文件

### 進階驗證（5 題）

6. **考試頁面的題目元素如何定位？**
   - ✅ 正確答案：CSS `.subject-description` 或 XPath `//span[@class='subject-description']`

7. **答案匹配策略有哪些？**
   - ✅ 正確答案：精確匹配 → 包含匹配 → 相似度匹配（85% 門檻）

8. **SQLite 資料表設計包含哪些表？**
   - ✅ 正確答案：questions（題目）、options（選項）、questions_fts（全文檢索）

9. **Phase 1 (MVP) 的主要任務是什麼？**
   - ✅ 正確答案：使用 JSON 檔案、實作 QuestionBankService、AnswerMatcher、ExamAnswerPage

10. **自動答題功能的主要風險有哪些？**
    - ✅ 正確答案：匹配失敗、動態載入延遲、自動化檢測、題庫過期、複選題邏輯

---

## 📋 快速參考卡

### 最常用指令（複製即用）

#### 開始新對話
```
讀取專案交接文檔
```

#### 查看自動答題規劃
```
查看自動答題功能規劃（2025-01-14）
```

#### 準備實作
```
我要開始實作自動答題功能，請讀取相關規劃文檔
```

#### 查看最新狀態
```
查看 CHANGELOG 最新修改
```

#### 使用 @workspace（Claude Code）
```
@workspace 讀取 docs 交接文檔
```

---

## 🎯 推薦工作流程

### Step 1：初次對話
```
讀取專案交接文檔
```

### Step 2：確認 AI 已理解
詢問 AI：「專案目前的狀態是什麼？自動答題規劃進度如何？」

### Step 3：開始工作
根據 AI 的回答，繼續你的任務（修改代碼、新增功能等）

### Step 4：定期同步
每次新對話開始時，重複 Step 1

---

## 📖 文檔內容速查

### AI_ASSISTANT_GUIDE.md（英文，最詳細）

**包含章節**:
- Quick Project Overview
- Project Structure
- Architecture Diagram
- Core Configuration (courses.json)
- How It Works
- Usage Guide
- Code Examples
- Common Tasks & How-To
- DO NOT MODIFY - Protected Files
- Troubleshooting
- **Planned Features: Auto-Answer System** ⭐（自動答題規劃）

**適用對象**: 所有 AI 助手

---

### CLAUDE_CODE_HANDOVER.md（中文）

**包含章節**:
- 快速開始
- 項目概述
- 項目架構
- 核心概念
- 常見任務指南
- 禁止修改清單
- 關鍵代碼索引
- 問題排查
- **規劃中功能：自動答題系統** ⭐（自動答題規劃）

**適用對象**: Claude Code CLI（中文使用者）

---

### CHANGELOG.md（中英混合）

**包含條目**:
- **[2025-01-14]** - 自動答題功能規劃評估 ⭐（最新）
- **[2025-01-13]** - 新增考試流程支持
  - 修復 #1: 考試頁面"繼續答題"按鈕無法定位
  - 修復 #2: 彈窗內"繼續答題"按鈕無法點擊

**適用對象**: 查看修改歷史、了解最新進度

---

## 🚨 常見問題 FAQ

### Q1: AI 說找不到文檔怎麼辦？

**方案 1**: 明確指定完整路徑
```
讀取 D:\Dev\eebot\docs\AI_ASSISTANT_GUIDE.md
```

**方案 2**: 要求使用 Read 工具
```
請使用 Read 工具讀取 docs/AI_ASSISTANT_GUIDE.md
```

**方案 3**: 使用 @workspace（Claude Code）
```
@workspace 索引 docs 目錄
```

---

### Q2: AI 只讀了部分文檔怎麼辦？

明確列出所有需要讀取的文件：
```
請依序讀取以下文件：
1. docs/AI_ASSISTANT_GUIDE.md
2. docs/CLAUDE_CODE_HANDOVER.md
3. docs/CHANGELOG.md

並總結專案狀態。
```

---

### Q3: 如何確認 AI 真的讀取了文檔？

使用本文檔的「驗證問題」進行測試（見上方「✅ 驗證 AI 是否正確讀取」章節）

---

### Q4: 不同 AI 助手需要不同的指令嗎？

大部分情況下，「讀取專案交接文檔」這句話通用於所有 AI。

但針對特定 AI 的優化指令會更高效（見「🔧 按 AI 工具分類的最佳實踐」章節）

---

### Q5: 文檔更新後，AI 會自動知道嗎？

不會。每次新對話開始時，都需要重新提示 AI 讀取文檔。

---

## 📞 支援資訊

### 如果提示詞不起作用

1. **檢查文件路徑**是否正確（使用 `ls docs/` 確認）
2. **檢查 AI 權限**（是否有讀取檔案的權限）
3. **嘗試不同的提示詞**（見本文檔各章節）
4. **查看 AI 錯誤訊息**（可能給出具體原因）

### 聯繫資訊

- **項目維護者**: wizard03
- **最後更新**: 2025-01-14
- **文檔版本**: 1.0

---

## 🎓 進階技巧

### 技巧 1: 組合多個文件查詢

```
請先讀取 docs/AI_ASSISTANT_GUIDE.md，
然後對比 data/courses.json 中的考試配置，
最後查看 郵政E大學114年題庫/ 目錄結構。

告訴我自動答題功能需要處理哪些題型。
```

### 技巧 2: 增量式讀取

```
第一步：讀取 docs/CHANGELOG.md
第二步：根據 CHANGELOG，讀取相關的源碼檔案
第三步：總結最新修改的影響範圍
```

### 技巧 3: 使用上下文提示

```
我正在開發自動答題功能（參考 docs/AI_ASSISTANT_GUIDE.md 的規劃），
現在遇到 HTML 元素定位問題。
請讀取考試頁面 HTML 快照並提供定位建議。
```

---

## ✨ 最佳實踐總結

### ✅ DO（推薦做法）

1. ✅ **新對話必讀**：每次新對話都提示 AI 讀取交接文檔
2. ✅ **使用簡潔指令**：「讀取專案交接文檔」通常就夠了
3. ✅ **驗證讀取結果**：用驗證問題測試 AI 是否真的理解
4. ✅ **明確需求**：告訴 AI 你要做什麼（如：實作自動答題）
5. ✅ **善用工具特性**：Claude Code 用 @workspace，Cursor 用 @docs

### ❌ DON'T（避免做法）

1. ❌ **假設 AI 記得**：不要假設 AI 記得上次對話的內容
2. ❌ **過於簡略**：不要只說「開始工作」而不提供上下文
3. ❌ **跳過驗證**：不要不驗證就開始讓 AI 修改代碼
4. ❌ **忽略錯誤**：如果 AI 說找不到文件，不要忽略
5. ❌ **混淆文檔**：不要混淆不同版本的文檔（中文/英文）

---

## 🔗 相關資源

- **主項目文檔**: `README.md`
- **通用 AI 指南**: `AI_ASSISTANT_GUIDE.md`
- **Claude Code 指南**: `CLAUDE_CODE_HANDOVER.md`
- **修改歷史**: `CHANGELOG.md`

---

**快速開始命令**:
```bash
# 查看文檔列表
ls D:\Dev\eebot\docs\

# 閱讀本文件
cat D:\Dev\eebot\docs\AI助手快速讀取交接文檔.md

# 閱讀通用指南
cat D:\Dev\eebot\docs\AI_ASSISTANT_GUIDE.md

# 閱讀修改歷史
cat D:\Dev\eebot\docs\CHANGELOG.md
```

---

**文檔維護者**: wizard03
**文檔版本**: 1.1
**最後更新**: 2025-11-16
**狀態**: ✅ 可用

---

## 📅 最新更新 (2025-11-16)

### 安全性增強
專案新增自動清理臨時檔案功能，在程式結束時自動刪除敏感資料（cookies.json、stealth.min.js）。

### 智能推薦修復
修正智能推薦功能的課程掃描問題，現在可以正確找到所有「修習中」的課程。

### 最新文檔
- **工作日誌**: [DAILY_WORK_LOG_20251116.md](./DAILY_WORK_LOG_20251116.md)
- **變更記錄**: 查看 CHANGELOG.md 的 2025-11-16 條目

---

**使用建議**: 將此文檔加入書籤，每次啟動新 AI 助手時參考使用。

**Happy Coding! 🚀**
