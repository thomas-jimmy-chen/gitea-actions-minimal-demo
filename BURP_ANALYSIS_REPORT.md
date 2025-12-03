# Burp Suite XML 分析報告 - EEBot 平台 API 端點

**分析日期**: 2025-12-02
**匯出時間**: Tue Dec 02 21:36:42 CST 2025
**Burp Suite 版本**: 2023.7
**分析範圍**: 20 個 HTTP 請求/回應記錄

---

## 概述

本報告詳細分析了 EEBot 平台（elearn.post.gov.tw）的 4 個關鍵 API 端點，包括請求/回應 headers、body 內容、參數結構和數據格式。

---

## 1. 登入請求 (POST /login)

### 基本信息
- **URL**: `https://elearn.post.gov.tw/login?no_cas=&next=`
- **方法**: POST
- **回應狀態**: 302 (Found / Redirect)
- **回應長度**: 209 bytes
- **重定向目標**: `https://elearn.post.gov.tw/`

### Request Headers

| Header | 值 |
|--------|-----|
| Host | elearn.post.gov.tw |
| Content-Type | application/x-www-form-urlencoded |
| Content-Length | 105 |
| User-Agent | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/142.0.0.0 Safari/537.36 |
| Origin | https://elearn.post.gov.tw |
| Referer | https://elearn.post.gov.tw/login |
| Accept | text/html,application/xhtml+xml,application/xml;q=0.9,... |
| Accept-Encoding | gzip, deflate |
| Accept-Language | zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7 |
| Sec-Ch-Ua | "Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99" |
| Sec-Ch-Ua-Mobile | ?0 |
| Sec-Ch-Ua-Platform | "Windows" |
| Sec-Fetch-Dest | document |
| Sec-Fetch-Mode | navigate |
| Sec-Fetch-Site | same-origin |
| Sec-Fetch-User | ?1 |
| Cache-Control | max-age=0 |
| Dnt | 1 |
| Upgrade-Insecure-Requests | 1 |
| Priority | u=0, i |
| Connection | close |

### Request Cookies

```
warning%3Achange_password=hide
_ga=GA1.3.839482039.1755469685
_ga_227RNMEJEV=GS2.1.s1763624314$o3$g0$t1763624314$j60$l0$h0
lang=zh-TW
session=V2-5cb0edda-4fb9-49f0-a6af-b1a9e2105330.MA.1764682648156.LvzR8jRAB9Xnu1VRlIg8IKJsWGg
```

### Request Body (URL Encoded Form Data)

```
next=
org_id=1
user_name=522673
password=jHRnpqZIFRYOG2RsGZVz
captcha_code=6479
submit=登入
```

**關鍵參數說明**:
- `user_name`: 使用者帳號/工號 (522673)
- `password`: 密碼 (明文傳輸: jHRnpqZIFRYOG2RsGZVz)
- `org_id`: 組織 ID (預設值: 1)
- `captcha_code`: 驗證碼 (6479)
- `next`: 登入後重定向 URL (空值)

### Response Headers

| Header | 值 |
|--------|-----|
| Server | Tengine |
| Date | Tue, 02 Dec 2025 13:34:31 GMT |
| Content-Type | text/html; charset=utf-8 |
| Content-Length | 209 |
| Connection | close |
| Location | https://elearn.post.gov.tw/ |
| Set-Cookie | session=V2-1-5cb0edda-4fb9-49f0-a6af-b1a9e2105330.MTk2ODg.1764704071379.4Ewyj59b1EPStyoNMBo0MsChtDo; Secure; HttpOnly; Path=/; SameSite=Strict; |
| X-SESSION-ID | V2-1-5cb0edda-4fb9-49f0-a6af-b1a9e2105330.MTk2ODg.1764704071379.4Ewyj59b1EPStyoNMBo0MsChtDo |
| Access-Control-Allow-Origin | * |
| Access-Control-Expose-Headers | X-SESSION-ID |
| Cache-Control | no-store |
| Content-Security-Policy | frame-ancestors 'self' https://elearnh5.post.gov.tw/; |
| X-Content-Type-Options | nosniff |
| X-Frame-Options | SAMEORIGIN |
| X-XSS-Protection | 1; mode=block |
| Strict-Transport-Security | max-age=31536000; includeSubDomains; preload; |
| Referrer-Policy | strict-origin-when-cross-origin |
| Permissions-Policy | geolocation=(self), microphone=(), camera=() |

### Response Body

```html
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<title>Redirecting...</title>
<h1>Redirecting...</h1>
<p>You should be redirected automatically to target URL: <a href="/">/ </a>. If not click the link.
```

### Cookie 設置重點

新 session cookie:
```
session=V2-1-5cb0edda-4fb9-49f0-a6af-b1a9e2105330.MTk2ODg.1764704071379.4Ewyj59b1EPStyoNMBo0MsChtDo
Secure; HttpOnly; Path=/; SameSite=Strict;
```

---

## 2. 我的課程 API (GET /api/my-courses)

### 基本信息
- **URL**: `https://elearn.post.gov.tw/api/my-courses`
- **方法**: GET
- **回應狀態**: 200 OK
- **回應長度**: 9968 bytes
- **Content-Type**: application/json

### Request Headers

| Header | 值 |
|--------|-----|
| Host | elearn.post.gov.tw |
| Accept | application/json, text/plain, */* |
| Accept-Encoding | gzip, deflate |
| Accept-Language | zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7 |
| User-Agent | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/142.0.0.0 Safari/537.36 |
| Referer | https://elearn.post.gov.tw/user/index |
| Sec-Ch-Ua | "Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99" |
| Sec-Ch-Ua-Mobile | ?0 |
| Sec-Ch-Ua-Platform | "Windows" |
| Sec-Fetch-Dest | empty |
| Sec-Fetch-Mode | cors |
| Sec-Fetch-Site | same-origin |
| Priority | u=1, i |
| Cache-Control | (no cache directive) |
| Dnt | 1 |
| Connection | close |

### Request Cookies

```
warning%3Achange_password=hide
_ga=GA1.3.839482039.1755469685
_ga_227RNMEJEV=GS2.1.s1763624314$o3$g0$t1763624314$j60$l0$h0
lang=zh-TW
warning:verification_email=show
session=V2-1-5cb0edda-4fb9-49f0-a6af-b1a9e2105330.MTk2ODg.1764704072648.StL06WXn9rPaWY7wWIcFTe4m04s
```

### Request Body

無 (GET 請求)

### Response Headers

| Header | 值 |
|--------|-----|
| Server | Tengine |
| Date | Tue, 02 Dec 2025 13:34:34 GMT |
| Content-Type | application/json |
| Content-Length | 9968 |
| Connection | close |
| Set-Cookie | session=V2-1-5cb0edda-4fb9-49f0-a6af-b1a9e2105330.MTk2ODg.1764704074607.QgPkvq0lDX4y-s5gQgZAAPdAZLk; Secure; HttpOnly; Path=/; SameSite=Strict; |
| X-SESSION-ID | V2-1-5cb0edda-4fb9-49f0-a6af-b1a9e2105330.MTk2ODg.1764704074607.QgPkvq0lDX4y-s5gQgZAAPdAZLk |
| Access-Control-Allow-Headers | DNT,X-SESSION-ID,User-Agent,X-Requested-With,If-Modified-Since,Content-Type,Range |
| Access-Control-Expose-Headers | X-SESSION-ID |
| Cache-Control | no-store |
| Content-Security-Policy | frame-ancestors 'self' https://elearnh5.post.gov.tw/; |
| X-Content-Type-Options | nosniff |
| Vary | Origin |
| X-Frame-Options | SAMEORIGIN |
| X-XSS-Protection | 1; mode=block |
| Strict-Transport-Security | max-age=31536000; includeSubDomains; preload; |
| Referrer-Policy | strict-origin-when-cross-origin |
| Permissions-Policy | geolocation=(self), microphone=(), camera=() |

### Response Body - JSON 結構

```json
{
  "courses": [
    {
      "id": 465,
      "name": "(課程名稱 - 中文編碼)",
      "course_code": "901011114",
      "credit": "2.0",
      "course_type": 1,
      "start_date": "2025-03-01",
      "end_date": "2025-12-31",
      "academic_year": null,
      "semester": null,
      "grade": null,
      "klass": null,
      "department": null,
      "compulsory": true,
      "is_graduated": true,
      "is_manual_registered": false,
      "is_mute": false,
      "org_id": 1,
      "instructors": [],
      "course_attributes": {
        "published": true,
        "student_count": 25474,
        "teaching_class_name": null
      },
      "org": {
        "is_enterprise_or_organization": null
      }
    },
    ... (更多課程對象)
  ]
}
```

### 課程數據欄位列表 (前 20 個欄位)

1. `id` - 課程 ID (integer)
2. `name` - 課程名稱 (string, 中文)
3. `course_code` - 課程代碼 (string)
4. `credit` - 學分 (string, 例: "2.0")
5. `course_type` - 課程類型 (integer, 1 表示一般課程)
6. `start_date` - 開始日期 (date string, YYYY-MM-DD)
7. `end_date` - 結束日期 (date string, YYYY-MM-DD)
8. `academic_year` - 學年 (null or integer)
9. `semester` - 學期 (null or integer)
10. `grade` - 成績 (null or string)
11. `klass` - 班級 (null or string)
12. `department` - 部門 (null or string)
13. `compulsory` - 是否必修 (boolean)
14. `is_graduated` - 是否已結業 (boolean)
15. `is_manual_registered` - 是否手動註冊 (boolean)
16. `is_mute` - 是否靜音 (boolean)
17. `org_id` - 組織 ID (integer)
18. `instructors` - 講師列表 (array)
19. `course_attributes` - 課程屬性 (object)
20. `org` - 組織信息 (object)

### course_attributes 結構

```json
{
  "published": boolean,      // 是否已發佈
  "student_count": integer,  // 學生人數
  "teaching_class_name": string or null  // 教學班級名稱
}
```

---

## 3. 考試中心 API (GET /api/exam-center/my-exams)

### 基本信息
- **URL**: `https://elearn.post.gov.tw/api/exam-center/my-exams`
- **方法**: GET
- **回應狀態**: 200 OK
- **回應長度**: 16 bytes
- **Content-Type**: application/json

### Request Headers

| Header | 值 |
|--------|-----|
| Host | elearn.post.gov.tw |
| Accept | application/json, text/plain, */* |
| Accept-Encoding | gzip, deflate |
| Accept-Language | zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7 |
| User-Agent | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/142.0.0.0 Safari/537.36 |
| Referer | https://elearn.post.gov.tw/user/index |
| Sec-Ch-Ua | "Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99" |
| Sec-Ch-Ua-Mobile | ?0 |
| Sec-Ch-Ua-Platform | "Windows" |
| Sec-Fetch-Dest | empty |
| Sec-Fetch-Mode | cors |
| Sec-Fetch-Site | same-origin |
| Priority | u=1, i |
| Dnt | 1 |
| Connection | close |

### Request Cookies

```
warning%3Achange_password=hide
_ga=GA1.3.839482039.1755469685
_ga_227RNMEJEV=GS2.1.s1763624314$o3$g0$t1763624314$j60$l0$h0
lang=zh-TW
warning:verification_email=show
session=V2-1-5cb0edda-4fb9-49f0-a6af-b1a9e2105330.MTk2ODg.1764704072648.StL06WXn9rPaWY7wWIcFTe4m04s
```

### Request Body

無 (GET 請求)

### Response Headers

| Header | 值 |
|--------|-----|
| Server | Tengine |
| Date | Tue, 02 Dec 2025 13:34:36 GMT |
| Content-Type | application/json |
| Content-Length | 16 |
| Connection | close |
| Set-Cookie | session=V2-1-5cb0edda-4fb9-49f0-a6af-b1a9e2105330.MTk2ODg.1764704076026.UedCZew3U6Sp8kuC_ZV5A6dfM4E; Secure; HttpOnly; Path=/; SameSite=Strict; |
| X-SESSION-ID | V2-1-5cb0edda-4fb9-49f0-a6af-b1a9e2105330.MTk2ODg.1764704076026.UedCZew3U6Sp8kuC_ZV5A6dfM4E |
| Access-Control-Allow-Headers | DNT,X-SESSION-ID,User-Agent,X-Requested-With,If-Modified-Since,Content-Type,Range |
| Access-Control-Expose-Headers | X-SESSION-ID |
| Cache-Control | no-store |
| Content-Security-Policy | frame-ancestors 'self' https://elearnh5.post.gov.tw/; |
| X-Content-Type-Options | nosniff |
| Vary | Origin |
| X-Frame-Options | SAMEORIGIN |
| X-XSS-Protection | 1; mode=block |
| Strict-Transport-Security | max-age=31536000; includeSubDomains; preload; |
| Referrer-Policy | strict-origin-when-cross-origin |
| Permissions-Policy | geolocation=(self), microphone=(), camera=() |

### Response Body - JSON 結構

```json
{
  "my_exams": []
}
```

**說明**: 該使用者目前沒有任何考試 (空陣列)。

### 預期的 my_exams 陣列項目結構 (基於 API 設計推測)

當有考試時，預期結構可能為:
```json
{
  "my_exams": [
    {
      "id": "exam_id",
      "name": "考試名稱",
      "course_id": 465,
      "start_time": "2025-12-20T09:00:00",
      "end_time": "2025-12-20T11:00:00",
      "duration_minutes": 120,
      "status": "scheduled|in_progress|completed",
      "score": null,
      ...
    }
  ]
}
```

---

## 4. 課程計畫 API (GET /api/curriculums)

### 基本信息
- **URL**: `https://elearn.post.gov.tw/api/curriculums?conditions=%7B%22not_withdrawn%22:0,%22owner_id%22:19688%7D&fields=id,name,code,status,curriculum_conditions(id,name,type,target(id,name,course_list(id,name)),items(id,name))`
- **方法**: GET
- **回應狀態**: 200 OK
- **回應長度**: 6018 bytes
- **Content-Type**: application/json

### Query Parameters

#### conditions 參數 (URL Encoded: %7B...%7D)
解碼後:
```json
{
  "not_withdrawn": 0,
  "owner_id": 19688
}
```

**參數說明**:
- `not_withdrawn`: 0 表示包含已撤銷的課程計畫
- `owner_id`: 19688 - 課程計畫所有者 ID

#### fields 參數
```
id,name,code,status,curriculum_conditions(id,name,type,target(id,name,course_list(id,name)),items(id,name))
```

**欄位說明**:
- `id` - 課程計畫 ID
- `name` - 課程計畫名稱
- `code` - 課程計畫代碼
- `status` - 狀態
- `curriculum_conditions` - 課程計畫條件陣列
  - `id` - 條件 ID
  - `name` - 條件名稱
  - `type` - 條件類型
  - `target` - 目標對象
    - `id` - 目標 ID
    - `name` - 目標名稱
    - `course_list` - 課程清單
      - `id` - 課程 ID
      - `name` - 課程名稱
  - `items` - 課程項目
    - `id` - 項目 ID
    - `name` - 項目名稱

### Request Headers

| Header | 值 |
|--------|-----|
| Host | elearn.post.gov.tw |
| Accept | application/json, text/plain, */* |
| Accept-Encoding | gzip, deflate |
| Accept-Language | zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7 |
| User-Agent | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/142.0.0.0 Safari/537.36 |
| Referer | https://elearn.post.gov.tw/user/index |
| Sec-Ch-Ua | "Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99" |
| Sec-Ch-Ua-Mobile | ?0 |
| Sec-Ch-Ua-Platform | "Windows" |
| Sec-Fetch-Dest | empty |
| Sec-Fetch-Mode | cors |
| Sec-Fetch-Site | same-origin |
| Priority | u=1, i |
| Dnt | 1 |
| Connection | close |

### Request Cookies

```
warning%3Achange_password=hide
_ga=GA1.3.839482039.1755469685
_ga_227RNMEJEV=GS2.1.s1763624314$o3$g0$t1763624314$j60$l0$h0
lang=zh-TW
warning:verification_email=show
session=V2-1-5cb0edda-4fb9-49f0-a6af-b1a9e2105330.MTk2ODg.1764704074607.QgPkvq0lDX4y-s5gQgZAAPdAZLk
```

### Request Body

無 (GET 請求)

### Response Headers

| Header | 值 |
|--------|-----|
| Server | Tengine |
| Date | Tue, 02 Dec 2025 13:34:35 GMT |
| Content-Type | application/json |
| Content-Length | 6018 |
| Connection | close |
| Set-Cookie | session=V2-1-5cb0edda-4fb9-49f0-a6af-b1a9e2105330.MTk2ODg.1764704075040.33lvtp94jYFSMszrGCtPOn-GUuE; Secure; HttpOnly; Path=/; SameSite=Strict; |
| X-SESSION-ID | V2-1-5cb0edda-4fb9-49f0-a6af-b1a9e2105330.MTk2ODg.1764704075040.33lvtp94jYFSMszrGCtPOn-GUuE |
| Access-Control-Allow-Headers | DNT,X-SESSION-ID,User-Agent,X-Requested-With,If-Modified-Since,Content-Type,Range |
| Access-Control-Expose-Headers | X-SESSION-ID |
| Cache-Control | no-store |
| Content-Security-Policy | frame-ancestors 'self' https://elearnh5.post.gov.tw/; |
| X-Content-Type-Options | nosniff |
| Vary | Origin |
| X-Frame-Options | SAMEORIGIN |
| X-XSS-Protection | 1; mode=block |
| Strict-Transport-Security | max-age=31536000; includeSubDomains; preload; |
| Referrer-Policy | strict-origin-when-cross-origin |
| Permissions-Policy | geolocation=(self), microphone=(), camera=() |

### Response Body - JSON 結構 (部分示例)

```json
{
  "curriculums": [
    {
      "id": 25,
      "code": "11407",
      "name": "(課程計畫名稱)",
      "status": "in_progress",
      "curriculum_conditions": [
        {
          "id": 186,
          "name": null,
          "type": "course_subject_partial",
          "target": {
            "id": 333,
            "name": "(目標名稱)",
            "course_list": [
              {
                "id": 465,
                "name": "(課程名稱)"
              }
            ]
          },
          "items": [
            {
              "id": 465,
              "name": "(課程項目名稱)"
            }
          ]
        }
      ]
    },
    {
      "id": 26,
      "code": "11409",
      "name": "(課程計畫名稱 2)",
      "status": "in_progress",
      "curriculum_conditions": [
        {
          "id": 195,
          "name": null,
          "type": "course_subject_partial",
          ...
        },
        ...
      ]
    },
    ...
  ]
}
```

### 課程計畫數據欄位列表 (前 20 個)

**Curriculum 對象層級**:
1. `id` - 課程計畫 ID (integer)
2. `code` - 課程計畫代碼 (string, 例: "11407")
3. `name` - 課程計畫名稱 (string, 中文)
4. `status` - 狀態 (string, 例: "in_progress")
5. `curriculum_conditions` - 課程計畫條件陣列 (array)

**Curriculum Conditions 層級**:
1. `id` - 條件 ID (integer)
2. `name` - 條件名稱 (null or string)
3. `type` - 條件類型 (string, 例: "course_subject_partial")
4. `target` - 目標對象 (object)
5. `items` - 課程項目陣列 (array)

**Target 層級**:
1. `id` - 目標 ID (integer)
2. `name` - 目標名稱 (string, 中文)
3. `course_list` - 課程清單 (array)

---

## 5. 關鍵安全觀察

### Cookie 管理
1. **Session Cookie**:
   - 使用格式: `V2-[UUID].[timestamp].[checksum]`
   - 屬性: `Secure; HttpOnly; Path=/; SameSite=Strict`
   - 每次請求後都會更新新的 session cookie

2. **其他 Cookie**:
   - `lang=zh-TW` - 語言設定
   - `warning:verification_email=show` - 電子郵件驗證警告
   - `_ga`, `_ga_227RNMEJEV` - Google Analytics 追蹤

### 密碼傳輸安全性
- 登入時密碼以明文形式在 URL encoded body 中傳輸
- 雖然使用 HTTPS，但密碼未加密就被傳送到伺服器

### API 端點特性
- 所有 API 都使用 CORS (Cross-Origin Resource Sharing)
- 回應包含 `X-SESSION-ID` header 用於會話追蹤
- 使用 `Content-Security-Policy` 限制 iframe 來源
- 啟用 XSS 保護

### HTTP Headers 安全性

| 安全相關 Header | 設定值 |
|--------|--------|
| Strict-Transport-Security | max-age=31536000; includeSubDomains; preload; |
| X-Content-Type-Options | nosniff |
| X-Frame-Options | SAMEORIGIN |
| X-XSS-Protection | 1; mode=block |
| Content-Security-Policy | frame-ancestors 'self' https://elearnh5.post.gov.tw/; |
| Referrer-Policy | strict-origin-when-cross-origin |

---

## 6. 總結

| API 端點 | 方法 | 狀態 | 認證方式 | 返回數據類型 | 關鍵欄位 |
|---------|------|------|--------|-----------|---------|
| /login | POST | 302 | Form Data | Redirect + Cookie | user_name, password, captcha_code |
| /api/my-courses | GET | 200 | Cookie/Session | JSON Array | id, name, course_code, credit, status |
| /api/exam-center/my-exams | GET | 200 | Cookie/Session | JSON Object | my_exams (array) |
| /api/curriculums | GET | 200 | Cookie/Session | JSON Object | id, code, name, status, curriculum_conditions |

---

## 附錄: 完整 Headers 比較

### 所有共同 Headers

```
Server: Tengine
Connection: close
Permissions-Policy: geolocation=(self), microphone=(), camera=()
Referrer-Policy: strict-origin-when-cross-origin
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload;
```

### API 請求共同特性

- 都使用 Chrome 142 User-Agent
- 都包含 `Accept-Language: zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7`
- 都使用 `Sec-Fetch-*` headers (Chrome 安全檢查)
- 都包含有效的 session cookie

---

**報告生成日期**: 2025-12-02
**分析工具**: Burp Suite 2023.7 XML Parser
