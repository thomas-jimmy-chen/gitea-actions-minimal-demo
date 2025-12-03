# AI 文檔讀取測試清單

> **目的**: 確保所有重要文檔都能被 AI 助手順利讀取
> **測試對象**: 新接手的 AI 助手（Claude、GPT、Gemini 等）
> **最後更新**: 2025-12-02

---

## 📋 測試說明

當新的 AI 助手接手 EEBot 專案時，請依序測試以下文檔的可讀性。

### 通過標準
- ✅ 能完整讀取文檔（無 token 超限錯誤）
- ✅ 能理解文檔結構和內容
- ✅ 能回答基於文檔內容的問題

---

## 🎯 核心文檔讀取測試

### 測試 1: 專案交接文檔

#### 1.1 主索引
```
檔案: docs/CLAUDE_CODE_HANDOVER.md
大小: ~6 KB, 237 行
預期: ✅ 應能完整讀取
測試命令: Read(docs/CLAUDE_CODE_HANDOVER.md)
```

**測試問題**:
- [ ] 專案代號是什麼？（答案：Gleipnir）
- [ ] 當前版本是多少？（答案：v2.0.7）
- [ ] 文檔分為幾段？（答案：2 段）

#### 1.2 第一段（基礎架構）
```
檔案: docs/CLAUDE_CODE_HANDOVER-1.md
大小: ~35 KB, 1,150 行
預期: ✅ 應能完整讀取
測試命令: Read(docs/CLAUDE_CODE_HANDOVER-1.md)
```

**測試問題**:
- [ ] 核心框架是什麼？（答案：Selenium + MitmProxy）
- [ ] 禁止修改的核心檔案有哪些？
- [ ] 環境變數配置檔是什麼？（答案：.env）

#### 1.3 第二段（進階功能）
```
檔案: docs/CLAUDE_CODE_HANDOVER-2.md
大小: ~45 KB, 1,500+ 行
預期: ✅ 應能完整讀取（已更新 Burp Suite 分析）
測試命令: Read(docs/CLAUDE_CODE_HANDOVER-2.md)
```

**測試問題**:
- [ ] 自動答題系統的版本是多少？（答案：2.0.2+auto-answer）
- [ ] 題庫總共有多少題？（答案：1,766 題）
- [ ] Burp Suite 分析的核心 API 是什麼？

---

### 測試 2: Burp Suite 分析文檔 ⭐

#### 2.1 主索引（必讀）
```
檔案: BURP_SUITE_ANALYSIS_INDEX.md
大小: ~10 KB, ~300 行
預期: ✅ 應能完整讀取
測試命令: Read(BURP_SUITE_ANALYSIS_INDEX.md)
```

**測試問題**:
- [ ] test2 包含多少個 HTTP 請求？（答案：660 個）
- [ ] 核心 API 是什麼？（答案：POST /statistics/api/user-visits）
- [ ] 有哪些詳細分析文檔？（至少列出 3 個）

#### 2.2 快速參考（必讀）
```
檔案: TEST2_QUICK_REFERENCE.md
大小: ~5 KB, ~200 行
預期: ✅ 應能完整讀取
測試命令: Read(TEST2_QUICK_REFERENCE.md)
```

**測試問題**:
- [ ] visit_duration 欄位的類型是什麼？（答案：integer）
- [ ] visit_duration 欄位的單位是什麼？（答案：秒）
- [ ] 必填欄位有幾個？（答案：13 個）
- [ ] 可選欄位有幾個？（答案：6 個）

#### 2.3 欄位對應表（JSON）
```
檔案: USER_VISITS_FIELD_MAPPING.json
大小: 21 KB, 570 行
預期: ✅ 應能完整讀取
測試命令: Read(USER_VISITS_FIELD_MAPPING.json)
```

**測試問題**:
- [ ] 能否解析 JSON 結構？
- [ ] visit_duration 的 security_level 是什麼？（答案：CRITICAL）
- [ ] request_body 總共有多少個欄位？（答案：19 個）

#### 2.4 時長分析專題
```
檔案: VISIT_DURATION_ANALYSIS.md
大小: 25 KB, 946 行
預期: ⚠️ 較大，建議分段讀取
測試命令: Read(VISIT_DURATION_ANALYSIS.md, limit=300)
```

**測試問題**:
- [ ] 能否讀取前 300 行？
- [ ] visit_duration 的範圍是多少？（答案：0-1483 秒）
- [ ] 有多少項安全漏洞？（答案：6 項）

#### 2.5 完整 API 分析
```
檔案: TEST2_DETAILED_ANALYSIS.md
大小: 20 KB, 622 行
預期: ✅ 應能完整讀取
測試命令: Read(TEST2_DETAILED_ANALYSIS.md)
```

**測試問題**:
- [ ] 分析了多少個獨立 API 端點？（答案：30+）
- [ ] Response 狀態碼是什麼？（答案：204 No Content）

#### 2.6 API 調用序列
```
檔案: API_CALL_SEQUENCE.md
大小: 20 KB, 586 行
預期: ✅ 應能完整讀取
測試命令: Read(API_CALL_SEQUENCE.md)
```

**測試問題**:
- [ ] 完整流程的時間範圍？（答案：28 分鐘）
- [ ] 首次時長提交的值是多少？（答案：1483 秒）

---

### 測試 3: 配置文件

#### 3.1 系統配置
```
檔案: config/eebot.cfg
大小: < 5 KB
預期: ✅ 應能完整讀取
測試命令: Read(config/eebot.cfg)
```

**測試問題**:
- [ ] MitmProxy 的端口是多少？
- [ ] modify_visits 的預設值是什麼？

#### 3.2 課程配置
```
檔案: data/courses.json
大小: 視課程數量而定
預期: ✅ 應能完整讀取
測試命令: Read(data/courses.json)
```

**測試問題**:
- [ ] 有多少個課程？
- [ ] 課程配置的必要欄位有哪些？

---

## 🔍 分段讀取測試

### 對於較大的文檔（>800 行）

如果文檔過大無法一次讀取，測試分段讀取功能：

```python
# 測試範例：VISIT_DURATION_ANALYSIS.md (946 行)

# 第 1 段（前 300 行）
Read(VISIT_DURATION_ANALYSIS.md, limit=300, offset=0)

# 第 2 段（301-600 行）
Read(VISIT_DURATION_ANALYSIS.md, limit=300, offset=300)

# 第 3 段（601-946 行）
Read(VISIT_DURATION_ANALYSIS.md, limit=346, offset=600)
```

**測試問題**:
- [ ] 能否分段讀取？
- [ ] 分段內容是否連貫？
- [ ] 能否拼湊完整資訊？

---

## 📊 測試記錄表

### AI 助手資訊
- **AI 名稱**: _______________________
- **模型版本**: _______________________
- **測試日期**: _______________________

### 測試結果

| 文檔 | 大小 | 行數 | 讀取狀態 | 備註 |
|------|------|------|---------|------|
| CLAUDE_CODE_HANDOVER.md | 6 KB | 237 | ☐ 成功 ☐ 失敗 | |
| CLAUDE_CODE_HANDOVER-1.md | 35 KB | 1,150 | ☐ 成功 ☐ 失敗 | |
| CLAUDE_CODE_HANDOVER-2.md | 45 KB | 1,500+ | ☐ 成功 ☐ 失敗 | |
| BURP_SUITE_ANALYSIS_INDEX.md | 10 KB | 300 | ☐ 成功 ☐ 失敗 | |
| TEST2_QUICK_REFERENCE.md | 5 KB | 200 | ☐ 成功 ☐ 失敗 | |
| USER_VISITS_FIELD_MAPPING.json | 21 KB | 570 | ☐ 成功 ☐ 失敗 | |
| VISIT_DURATION_ANALYSIS.md | 25 KB | 946 | ☐ 成功 ☐ 分段 | |
| TEST2_DETAILED_ANALYSIS.md | 20 KB | 622 | ☐ 成功 ☐ 失敗 | |
| API_CALL_SEQUENCE.md | 20 KB | 586 | ☐ 成功 ☐ 失敗 | |

### 總結
- **成功讀取**: _____ / 9 個文檔
- **需要分段**: _____ 個文檔
- **無法讀取**: _____ 個文檔

---

## ✅ 通過標準

專案文檔被認為「AI 友善」需滿足：

### 最低要求
- ✅ 至少 7/9 文檔能完整讀取
- ✅ 核心文檔（主索引、快速參考）必須能讀取
- ✅ 分段讀取機制正常運作

### 理想狀態
- ✅ 9/9 文檔都能讀取
- ✅ 所有測試問題都能回答
- ✅ AI 能基於文檔內容進行開發

---

## 🔧 讀取失敗的解決方案

### 如果文檔過大無法讀取

#### 方案 1: 分段讀取
```python
# 使用 offset 和 limit 參數
Read(文檔路徑, limit=500, offset=0)
Read(文檔路徑, limit=500, offset=500)
```

#### 方案 2: 使用 Grep 搜尋
```python
# 搜尋關鍵字
Grep(pattern="visit_duration", path="VISIT_DURATION_ANALYSIS.md", output_mode="content")
```

#### 方案 3: 讀取索引後查詢
```python
# 先讀索引了解章節結構
Read(BURP_SUITE_ANALYSIS_INDEX.md)
# 再針對性讀取特定章節
```

---

## 📝 建議改進

如果測試發現問題，建議：

### 對於文檔作者
1. 將過大文檔（>1000 行）拆分為多個檔案
2. 建立清晰的索引和導航
3. 提供精簡的快速參考版本

### 對於 AI 使用者
1. 優先讀取索引和快速參考
2. 使用分段讀取處理大文檔
3. 善用 Grep 搜尋關鍵資訊

---

## 🎯 快速測試腳本

對於 Claude Code CLI 用戶，可以使用以下命令快速測試：

```bash
# 測試所有核心文檔
echo "Testing BURP_SUITE_ANALYSIS_INDEX.md..."
head -50 BURP_SUITE_ANALYSIS_INDEX.md

echo "Testing TEST2_QUICK_REFERENCE.md..."
head -50 TEST2_QUICK_REFERENCE.md

echo "Testing USER_VISITS_FIELD_MAPPING.json..."
head -50 USER_VISITS_FIELD_MAPPING.json

echo "All tests completed!"
```

---

**測試版本**: 1.0
**建立日期**: 2025-12-02
**維護者**: wizard03

---

**目標**: 確保每個 AI 助手都能在 5 分鐘內掌握核心資訊！
