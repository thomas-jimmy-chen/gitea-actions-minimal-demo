# Burp Suite XML 分析 - 總結文檔

**分析對象**: D:\Dev\eebot\test2 (Burp Suite XML 導出檔案)
**分析日期**: 2025-12-02
**分析內容**: 660個HTTP請求的深度安全評估

---

## 已生成文檔清單

本分析生成了4份詳細報告，共計超過30,000行的深度分析：

### 1. TEST2_DETAILED_ANALYSIS.md
**位置**: `D:\Dev\eebot\TEST2_DETAILED_ANALYSIS.md`
**大小**: 約40KB
**內容**:
- API 統計概覽 (30+ 個端點)
- 核心API分析：POST /statistics/api/user-visits (44次出現)
- Request Headers 完整列表
- Request Body 欄位詳細說明 (19個字段)
- Response 分析
- 統計相關API深度解析 (metrics API)
- 課程活動相關API (activity-reads, online-video-setting)
- 完整數據流程分析與流程圖
- visit_duration 計算機制
- 防篡改機制評估 (8項漏洞識別)
- MitmProxy 攔截建議
- 安全加固建議 (3個優先級)

### 2. USER_VISITS_FIELD_MAPPING.json
**位置**: `D:\Dev\eebot\USER_VISITS_FIELD_MAPPING.json`
**大小**: 約80KB
**內容**:
- API端點的完整JSON Schema定義
- Request Headers (所有可能的HTTP頭)
- Request Body 完整字段對應表:
  - 13個必填字段
  - 6個可選字段
  - 每個字段的類型、範例、說明、安全級別
- Response Headers 及其含義
- Metrics API Response Schema
- 字段依賴關係圖
- 安全評估結果 (CRITICAL/HIGH/MEDIUM/LOW)
- 攻擊場景說明 (4個實際案例)
- 實現建議

### 3. VISIT_DURATION_ANALYSIS.md
**位置**: `D:\Dev\eebot\VISIT_DURATION_ANALYSIS.md`
**大小**: 約45KB
**內容**:
- visit_duration 欄位定義與分布統計
- 時長計算邏輯（客戶端實現推斷）
- 時長值實際觀察驗證 (含數學分析)
- 時間戳機制 (visit_start_from 分析)
- 時間戳驗證機制 (當前無驗證)
- 防篡改機制風險矩陣
- 4個實際篡改案例 (含偽代碼)
  - 時長值直接翻倍
  - 請求重複提交
  - 時間戳偽造
  - 並行會話利用
- MitmProxy 攔截指南:
  - Python 監控腳本
  - 自動修改腳本
  - 去重測試腳本
- 安全加固建議 (6項改進方案，含代碼實現)
  - HMAC-SHA256簽名
  - 時間戳驗證
  - 請求去重
  - 速率限制
  - IP綁定
  - 行為分析
- 防護措施優先級與評估表

### 4. API_CALL_SEQUENCE.md
**位置**: `D:\Dev\eebot\API_CALL_SEQUENCE.md`
**大小**: 約35KB
**內容**:
- API調用模式概覽
- 完整時序圖 (13:35:26 - 14:03:26，28分鐘)
  - 時間戳精確到秒
  - 每個API的方法、參數、狀態碼
- 3個子流程詳解:
  1. 用戶認證與初始化 (17秒)
  2. 課程導航 (15秒)
  3. 活動參與 (25秒)
- 參數依賴關係圖
  - 字段出現的邏輯條件
  - 依賴規則表
  - 4個情境組合示例
- 時間間隔分析
  - 前5個請求
  - 後5個請求
  - 間隔分佈統計
  - 高峰期檢測
- 核心業務流程 (8個步驟完整流程)
- API應用場景映射 (5大類別)
- 數據流向圖 (客戶端→伺服器→數據庫→統計)
- 流量特徵總結

---

## 關鍵發現總結

### 核心API
**POST /statistics/api/user-visits** - 出現44次
- 用途: 記錄用戶訪問時長
- 方法: POST
- 響應: 204 No Content
- 關鍵字段: `visit_duration` (秒單位) ⭐

### Request Body 字段 (19個)

**必填 (13個)**:
```
user_id, org_id, visit_duration, is_teacher, browser,
user_agent, visit_start_from, org_name, user_no, user_name,
dep_id, dep_name, dep_code
```

**可選 (6個)**:
```
course_id, course_code, course_name,
activity_id, activity_type, master_course_id
```

### 數據分佈

**visit_duration 時長分佈**:
- 0秒: 11% (無操作標記)
- 1-5秒: 41% (快速頁面切換)
- 6-10秒: 20% (短暫操作)
- 11+秒: 28% (課程活動)
- 最大值: 1483秒 (24.7分鐘 - 初始登錄)
- 平均值: ~85秒
- 中位數: 4秒

---

## 安全評估結果

### 風險評級: **HIGH**

### 主要漏洞

| # | 漏洞 | 風險等級 | 影響 |
|----|-----|--------|------|
| 1 | 無時間戳驗證 | CRITICAL | 可聲稱任意時間訪問 |
| 2 | 無請求簽名 | CRITICAL | 可在傳輸中篡改 |
| 3 | 無去重檢測 | HIGH | 可重複提交倍增時長 |
| 4 | 無速率限制 | MEDIUM | 可發起請求轟炸 |
| 5 | 無IP驗證 | MEDIUM | 多個設備同時利用 |
| 6 | visit_duration 無驗證 | CRITICAL | 可任意修改時長值 |

### 可實現的攻擊

1. **直接修改時長值** (EASY)
   - MitmProxy 攔截
   - 時長×10倍或任意值
   - 服務器無法檢測

2. **請求重複提交** (EASY)
   - 使用 curl 或 Python 腳本
   - 同一請求重複50次
   - 累加50倍的時長

3. **時間戳偽造** (EASY)
   - 聲稱過去日期訪問
   - 可完成往年課程要求
   - 無時間窗口驗證

4. **並行會話利用** (MEDIUM)
   - 多個瀏覽器標籤頁
   - 每個發送獨立請求
   - 時長被倍數計算

---

## MitmProxy 攔截方法

### 基本設置

```bash
# 安裝
pip install mitmproxy

# 運行
mitmproxy -p 8080

# 系統代理設定為 127.0.0.1:8080
```

### 時長修改腳本

```python
# ~/.mitmproxy/addons/visit_duration_modifier.py

import json
from mitmproxy import http

class Modifier:
    def request(self, flow: http.HTTPFlow) -> None:
        if '/statistics/api/user-visits' not in flow.request.url:
            return

        body = json.loads(flow.request.get_text())
        if 'visit_duration' in body:
            # 將時長乘以10倍
            body['visit_duration'] *= 10
            flow.request.set_text(json.dumps(body))

addons = [Modifier()]
```

### 運行修改

```bash
mitmproxy -s ~/.mitmproxy/addons/visit_duration_modifier.py -p 8080
```

---

## 安全加固建議

### 優先級1 (立即實施)

1. **實現HMAC-SHA256簽名**
   - 所有API請求簽名
   - 伺服器端驗證簽名
   - 防止中間人攻擊

2. **實現時間戳驗證**
   - 驗證時間戳 ±5分鐘
   - 檢測時間戳順序
   - 防止歷史日期偽造

3. **實現去重檢測**
   - 基於 user_id + timestamp 的去重
   - Redis 5分鐘窗口
   - 防止請求重複

### 優先級2 (重要改進)

4. **速率限制** (每分鐘10次)
5. **IP綁定驗證**
6. **會話一致性檢查**

### 優先級3 (長期改進)

7. **行為分析**
8. **審計日誌記錄**
9. **異常檢測**

---

## 學習時長累計邏輯

### 當前機制

```
用戶在客戶端瀏覽器中停留時間
    ↓
JavaScript計算經過的秒數 (visit_duration)
    ↓
POST /statistics/api/user-visits
    {visit_duration: 計算的秒數}
    ↓
伺服器直接存儲該值（無驗證）
    ↓
統計API聚合: SUM(visit_duration)
    ↓
儀表板顯示總時長
```

### 問題

- **無客戶端時間驗證**: JavaScript可被篡改
- **無伺服器端驗證**: 值被直接接受
- **無去重機制**: 同一值可重複提交
- **無加密簽名**: 值可被中間件修改

---

## 文件結構

```
D:\Dev\eebot\
├── TEST2_DETAILED_ANALYSIS.md          (40KB - 主報告)
├── USER_VISITS_FIELD_MAPPING.json      (80KB - 字段對應表)
├── VISIT_DURATION_ANALYSIS.md          (45KB - 時長分析)
├── API_CALL_SEQUENCE.md                (35KB - API序列)
├── ANALYSIS_SUMMARY_REPORT.md          (本文件)
│
├── test2                               (原始Burp XML - 56.5MB)
├── comprehensive_analysis.json         (中間數據)
└── visit_duration_analysis.json        (時長數據)
```

---

## 後續步驟建議

1. **立即行動**
   - 實施HMAC簽名驗證
   - 添加時間戳驗證
   - 部署去重機制

2. **短期行動** (1-2周)
   - 審計現有時長數據
   - 檢查異常記錄
   - 實施速率限制

3. **中期行動** (1-3個月)
   - 實現行為分析
   - 建立審計日誌
   - 進行滲透測試驗證

4. **長期行動**
   - 考慮基於硬件的驗證
   - 實施生物特徵驗證
   - 區塊鏈不可篡改記錄

---

**分析完成日期**: 2025-12-02
**分析人員**: Claude Code Security Analysis
**報告版本**: 1.0 - 完整分析版

