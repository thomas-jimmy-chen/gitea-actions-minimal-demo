# Burp Suite 分析文檔 - 主索引

> **📌 AI 讀取優先級文檔**
> 本文檔是 test1 和 test2 Burp Suite 分析的完整索引，設計為 AI 助手友善格式。

**最後更新**: 2025-12-02
**分析工具**: Burp Suite + Claude Code CLI
**專案**: EEBot (Gleipnir)

---

## 🎯 快速導航

### 對於新接手的 AI 助手
**推薦閱讀順序**：
1. 先讀 **本索引** (當前文檔)
2. 再讀 [TEST2_QUICK_REFERENCE.md](./TEST2_QUICK_REFERENCE.md) - 5 分鐘快速了解核心資訊
3. 需要時查閱詳細文檔（見下方）

### 對於需要深入分析的 AI 助手
1. [USER_VISITS_FIELD_MAPPING.json](./USER_VISITS_FIELD_MAPPING.json) - 完整欄位對應表
2. [VISIT_DURATION_ANALYSIS.md](./VISIT_DURATION_ANALYSIS.md) - 時長分析專題
3. [TEST2_DETAILED_ANALYSIS.md](./TEST2_DETAILED_ANALYSIS.md) - 完整 API 分析

---

## 📊 分析概覽

### test1 分析（登入與初始化流程）
- **檔案**: `test1` (984 KB)
- **請求數**: 20 個
- **時間範圍**: 登入到首頁載入
- **主要發現**: 登入機制、Session 管理、課程列表 API

### test2 分析（完整學習流程）⭐ 重點
- **檔案**: `test2` (57 MB)
- **請求數**: 660 個
- **時間範圍**: 28 分鐘完整學習流程
- **主要發現**: **時長提交 API**、課程訪問流程、統計機制

---

## 📁 文檔清單與讀取指南

### 1. 快速參考文檔（優先讀取）

#### TEST2_QUICK_REFERENCE.md ⭐ 最重要
**大小**: ~5 KB, 150 行
**讀取時間**: < 1 分鐘
**內容**:
- 核心 API 端點摘要
- visit_duration 欄位快速參考
- 19 個欄位的精簡對應表
- MitmProxy 攔截代碼範例

**適用場景**:
- 快速了解專案核心機制
- 實作 MitmProxy 攔截
- 查詢欄位定義

**AI 讀取建議**: ✅ 總是優先讀取此文檔

---

### 2. 欄位對應表（結構化資料）

#### USER_VISITS_FIELD_MAPPING.json
**大小**: 21 KB, 570 行
**格式**: JSON
**讀取時間**: 1-2 分鐘
**內容**:
- POST /statistics/api/user-visits 的完整 Schema
- 19 個欄位的詳細定義（類型、範例、說明）
- Request/Response 完整結構
- 安全評估矩陣

**適用場景**:
- 需要精確的欄位定義
- 開發 API 客戶端
- 資料驗證邏輯

**AI 讀取建議**: ✅ JSON 格式易於解析，推薦讀取

**關鍵欄位預覽**:
```json
{
  "visit_duration": {
    "type": "integer",
    "unit": "seconds",
    "range": "0 to 1483",
    "security_level": "CRITICAL"
  }
}
```

---

### 3. 時長分析專題（深度分析）

#### VISIT_DURATION_ANALYSIS.md
**大小**: 25 KB, 946 行
**讀取時間**: 3-5 分鐘
**內容**:
- visit_duration 計算邏輯（含 JavaScript 偽代碼）
- 時間戳機制分析
- 6 項安全漏洞詳解
- 4 個實際攻擊案例
- MitmProxy 完整實現代碼
- 安全加固方案（HMAC、時間戳驗證、去重）

**適用場景**:
- 理解時長計算邏輯
- 實作攻擊/防禦機制
- 安全審計

**AI 讀取建議**: ⚠️ 文檔較長，建議分段讀取或查詢特定章節

**章節索引**:
- 第 1-100 行: 欄位定義與統計
- 第 101-300 行: 計算邏輯與偽代碼
- 第 301-600 行: 防篡改機制評估
- 第 601-946 行: 攻擊案例與防禦代碼

---

### 4. 完整 API 分析（主報告）

#### TEST2_DETAILED_ANALYSIS.md
**大小**: 20 KB, 622 行
**讀取時間**: 2-3 分鐘
**內容**:
- 30+ 個 API 端點的頻率統計
- POST /statistics/api/user-visits 完整分析
- Request/Response Headers 詳細列表
- 資料流程圖
- 安全觀察與建議

**適用場景**:
- 全面了解 API 生態系統
- 識別其他相關 API
- 架構設計參考

**AI 讀取建議**: ✅ 結構清晰，易於導航

---

### 5. API 調用序列（時序分析）

#### API_CALL_SEQUENCE.md
**大小**: 20 KB, 586 行
**讀取時間**: 2-3 分鐘
**內容**:
- 28 分鐘完整時間軸（精確到秒）
- 44 個 user-visits 調用的詳細記錄
- 參數依賴關係圖
- 時間間隔分析
- 3 個子流程詳解

**適用場景**:
- 理解完整的學習流程
- 時序優化
- 行為模式分析

**AI 讀取建議**: ✅ 時序清晰，適合流程分析

---

### 6. 總結報告（快速概覽）

#### ANALYSIS_SUMMARY_REPORT.md
**大小**: 8 KB, 330 行
**讀取時間**: < 2 分鐘
**內容**:
- 分析成果總覽
- 關鍵發現摘要
- 安全分析總結
- 實施建議
- 文檔使用指南

**適用場景**:
- 快速了解分析成果
- 向他人報告
- 決策參考

**AI 讀取建議**: ✅ 精簡扼要，適合快速瀏覽

---

### 7. test1 分析文檔（登入流程）

#### BURP_ANALYSIS_REPORT.md
**大小**: 18 KB, 520 行
**讀取時間**: 2-3 分鐘
**內容**:
- 登入 API 分析 (POST /login)
- 我的課程 API (GET /api/my-courses)
- 考試中心 API (GET /api/exam-center/my-exams)
- 課程計畫 API (GET /api/curriculums)
- Session Cookie 機制

**適用場景**:
- 理解登入流程
- Session 管理
- 課程列表獲取

**AI 讀取建議**: ✅ 補充 test2 的前置知識

---

## 🎯 核心資訊速查

### 最重要的 API 端點
```
POST /statistics/api/user-visits
- 用途: 提交用戶訪問時長
- 頻率: 44 次 / 28 分鐘
- 關鍵欄位: visit_duration (integer, 秒)
- 回應: 204 No Content
```

### 最關鍵的欄位
```json
{
  "visit_duration": {
    "類型": "integer",
    "單位": "秒",
    "範圍": "0-1483",
    "平均值": "85 秒",
    "中位數": "4 秒",
    "安全性": "🔴 CRITICAL - 無驗證"
  }
}
```

### MitmProxy 攔截（最簡版本）
```python
import json
from mitmproxy import http

def request(flow: http.HTTPFlow) -> None:
    if '/statistics/api/user-visits' in flow.request.url:
        body = json.loads(flow.request.get_text())
        if 'visit_duration' in body:
            body['visit_duration'] *= 10  # ×10 倍
        flow.request.set_text(json.dumps(body))
```

---

## 🔍 AI 讀取策略

### 策略 A: 快速了解（5 分鐘）
1. 讀取本索引（當前文檔）
2. 讀取 [TEST2_QUICK_REFERENCE.md](./TEST2_QUICK_REFERENCE.md)
3. 完成！你已掌握 80% 的核心資訊

### 策略 B: 實作開發（15 分鐘）
1. 讀取 [TEST2_QUICK_REFERENCE.md](./TEST2_QUICK_REFERENCE.md)
2. 讀取 [USER_VISITS_FIELD_MAPPING.json](./USER_VISITS_FIELD_MAPPING.json)
3. 讀取 [VISIT_DURATION_ANALYSIS.md](./VISIT_DURATION_ANALYSIS.md) 的前 300 行
4. 開始實作！

### 策略 C: 完整分析（30 分鐘）
1. 按順序讀取所有 7 份文檔
2. 重點關注安全章節
3. 理解完整的資料流程

---

## 📊 文檔統計

| 文檔 | 大小 | 行數 | 讀取時間 | 優先級 |
|------|------|------|---------|--------|
| TEST2_QUICK_REFERENCE.md | 5 KB | 150 | 1 分鐘 | ⭐⭐⭐⭐⭐ |
| USER_VISITS_FIELD_MAPPING.json | 21 KB | 570 | 2 分鐘 | ⭐⭐⭐⭐⭐ |
| VISIT_DURATION_ANALYSIS.md | 25 KB | 946 | 5 分鐘 | ⭐⭐⭐⭐ |
| TEST2_DETAILED_ANALYSIS.md | 20 KB | 622 | 3 分鐘 | ⭐⭐⭐⭐ |
| API_CALL_SEQUENCE.md | 20 KB | 586 | 3 分鐘 | ⭐⭐⭐ |
| ANALYSIS_SUMMARY_REPORT.md | 8 KB | 330 | 2 分鐘 | ⭐⭐⭐ |
| BURP_ANALYSIS_REPORT.md | 18 KB | 520 | 3 分鐘 | ⭐⭐⭐ |

**總計**: 117 KB, ~3,700 行

---

## ⚠️ 重要提醒

### 對於 AI 讀取
- ✅ 所有文檔都在 1000 行以內（除 VISIT_DURATION_ANALYSIS.md）
- ✅ 使用 Markdown 格式，結構清晰
- ✅ JSON 文檔可直接解析
- ⚠️ VISIT_DURATION_ANALYSIS.md 建議分段讀取

### 對於人類讀者
- 📖 建議從 TEST2_QUICK_REFERENCE.md 開始
- 🔍 需要詳細資訊時查閱對應的專題文檔
- 💻 實作時參考 USER_VISITS_FIELD_MAPPING.json

---

## 🔗 相關文檔

### EEBot 專案文檔
- [CLAUDE_CODE_HANDOVER-2.md](./CLAUDE_CODE_HANDOVER-2.md) - 專案交接文檔（已更新）
- [CHANGELOG.md](./CHANGELOG.md) - 版本變更記錄

### 技術參考
- [MitmProxy 官方文檔](https://docs.mitmproxy.org/)
- [Burp Suite 使用指南](https://portswigger.net/burp/documentation)

---

## 📝 版本歷史

| 版本 | 日期 | 變更 |
|------|------|------|
| 1.0 | 2025-12-02 | 初始版本，包含 test1 和 test2 完整分析 |

---

**維護者**: wizard03 (with Claude Code CLI - Sonnet 4.5)
**專案**: EEBot (Gleipnir)
**最後更新**: 2025-12-02 22:30

---

## 🎉 使用建議

1. **每次新 AI 接手時**: 先讀本索引 + TEST2_QUICK_REFERENCE.md
2. **需要實作功能時**: 參考 USER_VISITS_FIELD_MAPPING.json
3. **遇到問題時**: 查閱對應的專題文檔（VISIT_DURATION_ANALYSIS.md 等）
4. **安全審計時**: 重點閱讀 VISIT_DURATION_ANALYSIS.md 的安全章節

**目標**: 讓每個 AI 助手都能在 5 分鐘內掌握核心資訊，15 分鐘內開始實作！
