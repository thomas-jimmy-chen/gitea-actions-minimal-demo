# EEBot API 快速參考指南

## 登入流程

### 步驟 1: 取得登入頁面
```
GET https://elearn.post.gov.tw/login HTTP/1.1
```

**回應**: 取得初始 session cookie

### 步驟 2: 提交登入表單
```
POST https://elearn.post.gov.tw/login?no_cas=&next= HTTP/1.1
Content-Type: application/x-www-form-urlencoded

next=&org_id=1&user_name=[USER_ID]&password=[PASSWORD]&captcha_code=[CODE]&submit=登入
```

**參數**:
- `user_name`: 用戶工號 (例: 522673)
- `password`: 密碼
- `org_id`: 1 (預設)
- `captcha_code`: 驗證碼
- `submit`: 登入 (按鈕值)

**回應**: 302 Redirect 到 `/` + 新 session cookie

### 步驟 3: 跟隨重定向
```
GET https://elearn.post.gov.tw/ HTTP/1.1
Cookie: session=[SESSION_COOKIE]
```

---

## API 端點快速表

### 1. 我的課程
```
GET /api/my-courses HTTP/1.1
Accept: application/json
Cookie: session=[SESSION_COOKIE]
```

**回應範例**:
```json
{
  "courses": [
    {
      "id": 465,
      "name": "課程名稱",
      "course_code": "901011114",
      "credit": "2.0",
      "start_date": "2025-03-01",
      "end_date": "2025-12-31",
      "is_graduated": true,
      "student_count": 25474
    }
  ]
}
```

### 2. 我的考試
```
GET /api/exam-center/my-exams HTTP/1.1
Accept: application/json
Cookie: session=[SESSION_COOKIE]
```

**回應範例**:
```json
{
  "my_exams": []
}
```

### 3. 課程計畫
```
GET /api/curriculums?conditions={"not_withdrawn":0,"owner_id":19688}&fields=id,name,code,status HTTP/1.1
Accept: application/json
Cookie: session=[SESSION_COOKIE]
```

**Query 參數**:
- `conditions`: JSON object with filter criteria (URL encoded)
  - `not_withdrawn`: 0 (include withdrawn) or 1 (exclude)
  - `owner_id`: curriculum owner's user ID
- `fields`: comma-separated fields to return

**回應範例**:
```json
{
  "curriculums": [
    {
      "id": 25,
      "code": "11407",
      "name": "課程計畫名稱",
      "status": "in_progress"
    }
  ]
}
```

---

## HTTP Headers 參考

### 必要 Headers (所有 API 請求)
```
Host: elearn.post.gov.tw
Accept: application/json, text/plain, */*
Accept-Encoding: gzip, deflate
Accept-Language: zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/142.0.0.0 Safari/537.36
Cookie: session=[SESSION_COOKIE]
```

### 登入特定 Headers
```
Origin: https://elearn.post.gov.tw
Referer: https://elearn.post.gov.tw/login
Content-Type: application/x-www-form-urlencoded
```

### 推薦的 Headers (瀏覽器相容性)
```
Sec-Ch-Ua: "Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Sec-Fetch-Dest: [empty|document]
Sec-Fetch-Mode: [cors|navigate]
Sec-Fetch-Site: same-origin
Upgrade-Insecure-Requests: 1
```

---

## Session Cookie 格式

```
session=V2-[UUID].[TIMESTAMP].[CHECKSUM]; Secure; HttpOnly; Path=/; SameSite=Strict;
```

**例**:
```
session=V2-5cb0edda-4fb9-49f0-a6af-b1a9e2105330.MTk2ODg.1764704071379.4Ewyj59b1EPStyoNMBo0MsChtDo
```

**重點**:
- 每次請求都會更新（新 session cookie 在回應中）
- `Secure` 標記 - 僅 HTTPS
- `HttpOnly` 標記 - JavaScript 無法存取
- `SameSite=Strict` - 防止 CSRF

---

## 課程數據欄位

### Course Object
| 欄位 | 類型 | 說明 |
|------|------|------|
| id | integer | 課程 ID |
| name | string | 課程名稱 (中文) |
| course_code | string | 課程代碼 |
| credit | string | 學分 (例: "2.0") |
| course_type | integer | 課程類型 |
| start_date | date | 開始日期 (YYYY-MM-DD) |
| end_date | date | 結束日期 (YYYY-MM-DD) |
| grade | string/null | 成績 |
| compulsory | boolean | 是否必修 |
| is_graduated | boolean | 是否已結業 |
| is_manual_registered | boolean | 是否手動註冊 |
| is_mute | boolean | 是否靜音 |
| org_id | integer | 組織 ID |
| course_attributes | object | 課程屬性 (published, student_count) |

---

## 課程計畫數據欄位

### Curriculum Object
| 欄位 | 類型 | 說明 |
|------|------|------|
| id | integer | 課程計畫 ID |
| code | string | 課程計畫代碼 |
| name | string | 課程計畫名稱 |
| status | string | 狀態 (active, in_progress, completed) |
| curriculum_conditions | array | 課程計畫條件陣列 |

### Curriculum Condition Object
| 欄位 | 類型 | 說明 |
|------|------|------|
| id | integer | 條件 ID |
| name | string/null | 條件名稱 |
| type | string | 條件類型 (course_subject_partial, etc) |
| target | object | 目標對象 |
| items | array | 課程項目陣列 |

### Target Object
| 欄位 | 類型 | 說明 |
|------|------|------|
| id | integer | 目標 ID |
| name | string | 目標名稱 |
| course_list | array | 課程清單 |

---

## 通用 Query 參數

### conditions (JSON Filter)
```
conditions={"not_withdrawn":0,"owner_id":19688}
```

URL 編碼後:
```
conditions=%7B%22not_withdrawn%22:0,%22owner_id%22:19688%7D
```

### fields (Field Selection)
```
fields=id,name,code,status,curriculum_conditions(id,name,type)
```

支援嵌套:
```
fields=id,name,target(id,name,course_list(id,name)),items(id,name)
```

---

## HTTP 狀態碼

| 狀態碼 | 說明 |
|--------|------|
| 200 | OK - 成功 |
| 302 | Found - 重定向 |
| 400 | Bad Request - 請求格式錯誤 |
| 401 | Unauthorized - 未認證 |
| 403 | Forbidden - 無權限 |
| 404 | Not Found - 資源不存在 |
| 500 | Internal Server Error - 伺服器錯誤 |

---

## 性能注意事項

### Cookie 更新
- 每次 API 請求的回應都包含新的 session cookie
- 建議保存並在後續請求中使用最新 cookie
- Cookie 無限期有效期間為未知 (未在回應中指定)

### 響應壓縮
- 所有回應都支援 gzip/deflate 壓縮
- 預設使用壓縮傳輸 (Content-Encoding: gzip)

### 請求超時
- 未在分析中觀察到超時設定
- 建議設定 30 秒超時

---

## cURL 範例

### 登入
```bash
curl -X POST "https://elearn.post.gov.tw/login?no_cas=&next=" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "User-Agent: Mozilla/5.0..." \
  -d "next=&org_id=1&user_name=522673&password=PASSWORD&captcha_code=6479&submit=登入" \
  -v
```

### 取得課程列表
```bash
curl -X GET "https://elearn.post.gov.tw/api/my-courses" \
  -H "Accept: application/json" \
  -H "Cookie: session=SESSION_COOKIE" \
  -H "User-Agent: Mozilla/5.0..." \
  -v
```

### 取得課程計畫
```bash
curl -X GET 'https://elearn.post.gov.tw/api/curriculums?conditions=%7B%22not_withdrawn%22:0,%22owner_id%22:19688%7D&fields=id,name,code,status' \
  -H "Accept: application/json" \
  -H "Cookie: session=SESSION_COOKIE" \
  -H "User-Agent: Mozilla/5.0..." \
  -v
```

---

## Python requests 範例

### 登入
```python
import requests

session = requests.Session()
response = session.post(
    'https://elearn.post.gov.tw/login?no_cas=&next=',
    data={
        'next': '',
        'org_id': '1',
        'user_name': '522673',
        'password': 'PASSWORD',
        'captcha_code': '6479',
        'submit': '登入'
    },
    headers={
        'User-Agent': 'Mozilla/5.0...'
    }
)
# session.cookies 現在包含有效的 session cookie
```

### 取得課程列表
```python
response = session.get(
    'https://elearn.post.gov.tw/api/my-courses',
    headers={
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0...'
    }
)
courses = response.json()['courses']
```

---

## 常見錯誤排除

| 問題 | 原因 | 解決方案 |
|------|------|--------|
| 401 Unauthorized | Session 過期或無效 | 重新登入 |
| 403 Forbidden | 無權限訪問資源 | 確認權限和用戶角色 |
| CORS 錯誤 | 跨域請求被阻止 | 確認 Origin header |
| 密碼錯誤 | 認證失敗 | 驗證用戶名和密碼 |
| 驗證碼錯誤 | 驗證碼不正確或過期 | 重新取得驗證碼並重試 |

---

## 安全最佳實踐

1. **密碼管理**
   - 不要在代碼中硬編碼密碼
   - 使用環境變數或安全的配置管理

2. **Session 管理**
   - 定期更新 session cookie (每次請求自動更新)
   - 登出時清除所有 cookie
   - 設定合理的超時時間

3. **HTTPS**
   - 總是使用 HTTPS
   - 驗證 SSL/TLS 證書

4. **Headers**
   - 總是包含 User-Agent
   - 正確設定 Referer header
   - 遵守 CORS 政策

5. **速率限制**
   - 實施請求速率限制
   - 避免過度查詢

---

**最後更新**: 2025-12-02
**文件版本**: 1.0
