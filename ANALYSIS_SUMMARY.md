# Burp Suite XML 分析 - 總結報告

**分析日期**: 2025-12-02
**平台**: EEBot Learning Management System (elearn.post.gov.tw)
**分析工具**: Burp Suite 2023.7
**XML 檔案**: D:\Dev\eebot\test1 (984.2 KB, 20 HTTP 請求)

---

## 分析成果

### 生成的文檔

本分析已生成以下三份詳細文檔，位於 D:\Dev\eebot\ 目錄下：

#### 1. **BURP_ANALYSIS_REPORT.md** (主要分析報告)
   - **內容**: 完整的 4 個 API 端點分析
   - **涵蓋項目**:
     - 登入請求 (POST /login) 的完整 headers、cookies、request body、response headers
     - 我的課程 API (GET /api/my-courses) 的 JSON 結構和欄位詳解
     - 考試中心 API (GET /api/exam-center/my-exams) 的回應格式
     - 課程計畫 API (GET /api/curriculums) 的查詢參數和複雜嵌套結構
     - 安全觀察 (Cookie 管理、HTTPS、CORS、CSP 等)
   - **大小**: ~25 KB
   - **用途**: 深度技術文檔

#### 2. **API_TECHNICAL_SPEC.json** (技術規範)
   - **內容**: JSON 格式的結構化 API 規範
   - **涵蓋項目**:
     - 4 個端點的完整技術規範
     - 請求/回應的詳細 schema
     - Query 參數說明
     - 身份驗證機制
     - 安全設定
     - 實際範例
   - **大小**: ~20 KB
   - **用途**: API 集成和開發參考

#### 3. **API_QUICK_REFERENCE.md** (快速參考)
   - **內容**: 實用的快速查詢指南
   - **涵蓋項目**:
     - 登入流程逐步說明
     - API 端點快速表
     - HTTP Headers 參考
     - Session Cookie 格式
     - 數據欄位速查表
     - cURL 和 Python 範例
     - 常見錯誤排除
     - 安全最佳實踐
   - **大小**: ~15 KB
   - **用途**: 開發者快速參考

#### 4. **parse_burp_analysis.py** (分析腳本)
   - **內容**: Python 自動化分析工具
   - **功能**: 可自動解析 Burp XML 並提取目標 API 端點
   - **用途**: 後續更新或批量分析

---

## 關鍵發現

### 1. 登入機制

**端點**: `POST /login?no_cas=&next=`

**必要參數**:
```
user_name: 員工編號/帳號
password: 密碼 (明文傳輸)
org_id: 組織 ID (預設 1)
captcha_code: 驗證碼
submit: 登入
```

**認證流程**:
1. GET /login 取得初始 session
2. POST /login 提交認證
3. 302 重定向到 / (如成功)
4. 新 session cookie 設定

**重點**: 密碼以明文形式在 HTTPS 上傳輸

---

### 2. API 認證

所有 API 端點使用 **Session-Based 認證**:
- Session 格式: `V2-[UUID].[timestamp].[checksum]`
- 屬性: Secure, HttpOnly, SameSite=Strict
- **每次請求都會更新** (伺服器每次回應都設定新 cookie)
- X-SESSION-ID header 用於額外追蹤

---

### 3. 課程數據結構

**/api/my-courses** 回應包含:
```json
{
  "courses": [
    {
      "id": 465,
      "name": "課程名稱",
      "course_code": "901011114",
      "credit": "2.0",
      "course_type": 1,
      "start_date": "2025-03-01",
      "end_date": "2025-12-31",
      "is_graduated": true,
      "student_count": 25474,
      ...20 more fields
    }
  ]
}
```

**共 20+ 欄位**，包括:
- 基本信息 (id, name, code, credit)
- 日期 (start_date, end_date)
- 狀態 (is_graduated, is_manual_registered)
- 屬性 (course_type, compulsory, is_mute)
- 關係 (org_id, instructors, department)

---

### 4. 課程計畫複雜結構

**/api/curriculums** 支援:
- **Filtering**: via `conditions` JSON 參數
  ```
  conditions={"not_withdrawn":0,"owner_id":19688}
  ```
- **Field Selection**: via `fields` 參數，支援嵌套
  ```
  fields=id,name,code,status,
         curriculum_conditions(id,name,type,
                               target(id,name,course_list(id,name)),
                               items(id,name))
  ```

**嵌套結構**:
```
Curriculum
  └─ curriculum_conditions[] (多個)
      ├─ target
      │  └─ course_list[] (課程列表)
      └─ items[] (課程項目)
```

---

### 5. 考試 API

**/api/exam-center/my-exams** 目前回應為空陣列:
```json
{
  "my_exams": []
}
```

預期欄位 (當有考試時):
- id, name, course_id
- start_time, end_time, duration_minutes
- status (scheduled/in_progress/completed)
- score, passing_score

---

## 安全分析

### 強項
1. ✓ HTTPS/TLS 1.2+ 必須
2. ✓ HSTS 支援 (max-age=31536000)
3. ✓ XSS 保護 (X-XSS-Protection)
4. ✓ Clickjacking 保護 (X-Frame-Options: SAMEORIGIN)
5. ✓ HttpOnly Cookies (JavaScript 無法存取)
6. ✓ SameSite=Strict Cookie (CSRF 保護)
7. ✓ Content-Security-Policy 限制 iframe

### 薄弱點
1. ⚠ 密碼以明文形式在請求 body 中傳輸
2. ⚠ Session cookie 未指定過期時間 (預期應有)
3. ⚠ 缺少 rate limiting (未觀察到 429 限制)

---

## HTTP Headers 概覽

### 響應中的重要 Headers

```
Server: Tengine (阿里雲中國版)
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload;
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Content-Security-Policy: frame-ancestors 'self' https://elearnh5.post.gov.tw/;
Referrer-Policy: strict-origin-when-cross-origin
```

### 客戶端識別

所有請求都包含:
```
Chrome 142 User-Agent
Sec-Ch-Ua headers (提供版本、品牌信息)
Accept-Language: zh-TW (繁體中文台灣)
```

---

## 數據編碼

### 語言
- 課程名稱、計畫名稱等使用 **中文** (UTF-8)
- 某些捕獲中可能有編碼顯示問題，但 JSON 本身正確

### 格式
- 日期: ISO 8601 (`YYYY-MM-DD`)
- 數值: 字符串形式 (例: credit 為 "2.0" 而非 2.0)
- 布林: JSON boolean 類型

---

## 與分析相關的統計

| 指標 | 值 |
|------|-----|
| 總請求數 | 20 |
| 分析的 API 端點 | 4 |
| GET 請求 | 3 |
| POST 請求 | 1 |
| Base64 編碼的內容 | 100% (request/response) |
| JSON 回應 | 3 個 API |
| HTML 回應 | 2 個 (首頁和登入頁) |
| 平均回應大小 | ~50 KB (含 HTML 頁面) |
| 平均 API 回應 | ~7 KB |

---

## 實施建議

### 對於 EEBot 客戶端開發

1. **認證流程**
   - 實施登入表單提交
   - 自動保存 session cookie
   - 實施重新登入邏輯

2. **API 調用**
   - 使用 CORS 兼容的請求方式
   - 總是包含 Accept: application/json header
   - 自動使用最新的 session cookie

3. **錯誤處理**
   - 401 → 重新認證
   - 403 → 權限提示
   - 5xx → 重試邏輯

4. **數據處理**
   - 使用 UTF-8 解碼器處理課程名稱
   - 日期字符串轉換為日期對象
   - 數值字符串轉換為數值

### 對於安全加強

1. 考慮實施 OAuth 2.0 或 JWT
2. 實施 API rate limiting
3. 添加密碼加密 (client-side)
4. 實施更強的 session 超時機制

---

## 相關文件位置

```
D:\Dev\eebot\
├── BURP_ANALYSIS_REPORT.md      ← 完整分析報告
├── API_TECHNICAL_SPEC.json       ← JSON 技術規範
├── API_QUICK_REFERENCE.md        ← 快速參考指南
├── parse_burp_analysis.py        ← 分析工具
└── ANALYSIS_SUMMARY.md           ← 本文件
```

---

## 如何使用這些文檔

### 針對開發者
1. 先讀 **API_QUICK_REFERENCE.md** 快速了解
2. 參考 **API_TECHNICAL_SPEC.json** 進行開發
3. 遇到問題時查閱 **BURP_ANALYSIS_REPORT.md** 深度信息

### 針對 API 集成
1. 使用 **API_TECHNICAL_SPEC.json** 作為規範
2. 參考 cURL 和 Python 範例進行測試
3. 查閱 Headers 和參數詳情

### 針對安全審計
1. 完整閱讀 **BURP_ANALYSIS_REPORT.md** 的安全部分
2. 檢查 **API_TECHNICAL_SPEC.json** 中的安全設定
3. 對照安全最佳實踐

---

## 分析限制

1. **時間快照**: 分析基於 2025-12-02 的單次捕獲
2. **場景限制**: 僅分析已認證用戶的 API 調用
3. **用戶特定**: 某些課程名稱包含中文編碼，可能因編碼問題顯示不完整
4. **未測試**: 未測試錯誤場景、邊界情況、rate limiting
5. **API 版本**: 未發現 API 版本控制信息

---

## 後續建議

1. **重複分析**: 定期更新分析以跟蹤 API 變更
2. **端點補充**: 分析登出、更新個人資料等其他 API
3. **測試環境**: 在測試環境中驗證 API 行為
4. **性能分析**: 進行響應時間和吞吐量測試
5. **身份驗證測試**: 測試無效 session、過期 token 等

---

**報告完成日期**: 2025-12-02 21:40 UTC+8
**報告版本**: 1.0
**分析工具**: Claude Code + Python XML Parser
**作者**: AI 代碼分析助手
