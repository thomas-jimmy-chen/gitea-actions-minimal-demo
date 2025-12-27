# EEBot 技術規格文檔 (Technical Specification)

> **專案名稱**: EEBot (代號: AliCorn 天角獸)
> **版本**: v2.3.8
> **文檔版本**: 1.0
> **建立日期**: 2025-12-27
> **維護者**: Claude Code (Opus 4.5)
> **用途**: 定義專案的技術邊界、資料格式、流程邏輯，確保開發一致性

---

## 目錄

1. [常量定義](#1-常量定義)
2. [配置規格](#2-配置規格)
3. [API 規格](#3-api-規格)
4. [頁面元素定位器](#4-頁面元素定位器)
5. [攔截器規格](#5-攔截器規格)
6. [流程規格](#6-流程規格)
7. [資料格式規格](#7-資料格式規格)
8. [邊界條件](#8-邊界條件)
9. [異常規格](#9-異常規格)
10. [檔案路徑規格](#10-檔案路徑規格)

---

## 1. 常量定義

### 1.1 HTTP 狀態碼

| 常量名稱 | 值 | 說明 |
|---------|-----|------|
| `HTTP_SUCCESS_MIN` | 200 | 成功狀態碼最小值 |
| `HTTP_SUCCESS_MAX` | 300 | 成功狀態碼最大值（不含） |
| `HTTP_OK` | 200 | 請求成功 |
| `HTTP_CREATED` | 201 | 資源已創建 |
| `HTTP_NO_CONTENT` | 204 | 成功，無響應內容 |
| `HTTP_BAD_REQUEST` | 400 | 錯誤的請求 |
| `HTTP_UNAUTHORIZED` | 401 | 未授權 |
| `HTTP_FORBIDDEN` | 403 | 禁止訪問 |
| `HTTP_NOT_FOUND` | 404 | 資源未找到 |
| `HTTP_INTERNAL_ERROR` | 500 | 服務器內部錯誤 |
| `HTTP_TIMEOUT` | 30 | HTTP 請求超時（秒） |

### 1.2 延遲常量

| 常量名稱 | 值（秒） | 用途 |
|---------|----------|------|
| `DEFAULT_PAGE_LOAD_DELAY` | 7 | 一般頁面載入 |
| `SHORT_PAGE_LOAD_DELAY` | 2 | 快速頁面 |
| `LONG_PAGE_LOAD_DELAY` | 10 | 複雜頁面 |
| `LESSON_SELECT_DELAY` | 2.0 | 選擇課程 |
| `CLICK_DELAY` | 1.0 | 點擊操作 |
| `INPUT_DELAY` | 0.5 | 輸入操作 |
| `API_REQUEST_DELAY` | 1 | API 請求間隔 |
| `PAYLOAD_CAPTURE_WAIT` | 3 | Payload 捕獲 |
| `RETRY_DELAY` | 5 | 重試等待 |

### 1.3 重試常量

| 常量名稱 | 值 | 說明 |
|---------|-----|------|
| `MAX_LOGIN_RETRIES` | 3 | 登入重試次數 |
| `MAX_OPERATION_RETRIES` | 3 | 操作重試次數 |
| `MAX_API_RETRIES` | 3 | API 重試次數 |
| `CAPTCHA_MAX_RETRIES` | 3 | 驗證碼重試次數 |

### 1.4 超時常量

| 常量名稱 | 值（秒） | 用途 |
|---------|----------|------|
| `DEFAULT_TIMEOUT` | 40 | BasePage 預設超時 |
| `DEFAULT_POLL_FREQUENCY` | 0.5 | 元素輪詢頻率 |
| `DEFAULT_WAIT_TIMEOUT` | 10 | 一般等待 |
| `LONG_WAIT_TIMEOUT` | 30 | 長等待 |
| `SHORT_WAIT_TIMEOUT` | 5 | 短等待 |

### 1.5 時長常量

| 常量名稱 | 值 | 說明 |
|---------|-----|------|
| `BUFFER_SECONDS` | 10 | 發送時長緩衝 |
| `MINIMUM_DURATION_SECONDS` | 60 | 最小學習時長 |
| `SECONDS_PER_MINUTE` | 60 | 秒/分鐘 |
| `MINUTES_PER_HOUR` | 60 | 分鐘/小時 |

---

## 2. 配置規格

### 2.1 配置檔案格式

**檔案**: `config/eebot.cfg`

```ini
[DEFAULT]
# === 必填項目 ===
target_http = https://elearn.post.gov.tw
execute_file = C:\tools\chromedriver\chromedriver.exe
user_name = <用戶名>
password = <密碼>
cookies_file = cookies.json

# === 選填項目（有預設值） ===
# Proxy 設定
listen_host = 127.0.0.1          # 預設: 127.0.0.1
listen_port = 8080               # 預設: 8080

# 功能開關
modify_visits = y                # 預設: y (啟用時長修改)
silent_mitm = y                  # 預設: y (靜默模式)
log_save = n                     # 預設: n

# 時長設定
visit_duration_increase = 9000   # 預設: 9000 (秒)

# 自動答題設定
enable_auto_answer = y           # 預設: y
question_bank_mode = file_mapping  # 預設: file_mapping
question_bank_path = 郵政E大學114年題庫/總題庫.json
answer_confidence_threshold = 0.85  # 預設: 0.85
auto_submit_exam = n             # 預設: n
screenshot_on_mismatch = y       # 預設: y
screenshot_dir = screenshots/unmatched
```

### 2.2 配置項目規格

| 配置項 | 類型 | 必填 | 預設值 | 範圍/格式 |
|--------|------|------|--------|-----------|
| target_http | URL | ✅ | - | https://... |
| execute_file | Path | ✅ | - | 絕對路徑 |
| user_name | String | ✅ | - | 非空字串 |
| password | String | ✅ | - | 非空字串 |
| cookies_file | Path | ✅ | cookies.json | 相對/絕對路徑 |
| listen_host | IP | ❌ | 127.0.0.1 | 有效 IP |
| listen_port | Integer | ❌ | 8080 | 1024-65535 |
| modify_visits | Boolean | ❌ | y | y/n |
| silent_mitm | Boolean | ❌ | y | y/n |
| visit_duration_increase | Integer | ❌ | 9000 | > 0 |
| answer_confidence_threshold | Float | ❌ | 0.85 | 0.0-1.0 |

### 2.3 環境變數優先級

```
優先級（高到低）:
1. 環境變數 EEBOT_<KEY>
2. 配置檔案 config/eebot.cfg
3. 程式預設值
```

**環境變數映射**:
| 環境變數 | 配置項 |
|----------|--------|
| EEBOT_USERNAME | user_name |
| EEBOT_PASSWORD | password |
| EEBOT_TARGET_URL | target_http |
| EEBOT_PROXY_HOST | listen_host |
| EEBOT_PROXY_PORT | listen_port |

---

## 3. API 規格

### 3.1 API 端點列表

| 端點 | 方法 | 用途 |
|------|------|------|
| `/api/my-courses` | GET | 取得我的課程列表 |
| `/api/courses/{id}` | GET | 取得課程詳情 |
| `/api/courses/{id}/activities` | GET | 取得課程活動 |
| `/statistics/api/user-visits` | POST | 發送訪問時長 |
| `/api/exams/{id}/distribute` | GET | 取得考試題目 |
| `/api/exams/{id}/submissions` | POST | 提交考試答案 |
| `/api/announcement` | GET | 觸發 Session 更新 |

### 3.2 訪問時長 API (user-visits)

**端點**: `POST /statistics/api/user-visits`

**請求格式**:
```json
{
  "user_id": "string",           // 必填
  "org_id": "string",            // 必填，通常 "1"
  "visit_duration": 9000,        // 必填，秒數
  "is_teacher": false,           // 必填
  "browser": "chrome",           // 必填
  "user_agent": "string",        // 必填
  "visit_start_from": "2025/12/27T14:30:00",  // 必填
  "org_name": "郵政ｅ大學",      // 必填
  "user_no": "string",           // 必填
  "user_name": "string",         // 必填
  "dep_id": "string",            // 必填
  "dep_name": "string",          // 必填
  "dep_code": "string",          // 必填
  "course_id": "string",         // 可選
  "course_code": "string",       // 可選
  "course_name": "string",       // 可選
  "activity_id": "string",       // 可選
  "activity_type": "scorm"       // 可選
}
```

**必填欄位驗證**:
```python
required_keys = (
    "user_id", "org_id", "visit_duration", "is_teacher",
    "browser", "user_agent", "visit_start_from", "org_name",
    "user_no", "user_name", "dep_id", "dep_name", "dep_code"
)
```

**響應**: HTTP 204 No Content

### 3.3 考試分發 API (distribute)

**端點**: `GET /api/exams/{exam_id}/distribute`

**響應格式**:
```json
{
  "id": 48,
  "exam_paper_instance_id": "string",
  "exam_submission_id": "string",
  "subjects": [
    {
      "id": 1,
      "description": "<p>題目 HTML</p>",
      "options": [
        {"id": "opt1", "content": "<p>選項 A</p>"},
        {"id": "opt2", "content": "<p>選項 B</p>"}
      ],
      "updated_at": "ISO8601"
    }
  ]
}
```

### 3.4 考試提交 API (submissions)

**端點**: `POST /api/exams/{exam_id}/submissions`

**請求格式**:
```json
{
  "exam_paper_instance_id": "string",
  "exam_submission_id": "string",
  "subjects": [
    {
      "subject_id": "string",
      "answer_option_ids": ["opt1"],
      "subject_updated_at": "ISO8601"
    }
  ],
  "progress": {
    "answered_num": 10,
    "total_subjects": 10
  }
}
```

### 3.5 HTTP Headers 規格

```http
Content-Type: text/plain;charset=UTF-8
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Accept: */*
Accept-Language: zh-TW,zh;q=0.9,en-US;q=0.8
Origin: https://elearn.post.gov.tw
Sec-Ch-Ua: "Google Chrome";v="143"
Sec-Ch-Ua-Platform: "Windows"
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: no-cors
```

---

## 4. 頁面元素定位器

### 4.1 登入頁面 (LoginPage)

```python
USERNAME_INPUT = (By.ID, 'user_name')
PASSWORD_INPUT = (By.ID, 'password')
CAPTCHA_IMAGE = (By.XPATH, "//form//img[contains(@src,'captcha')]")
CAPTCHA_INPUT = (By.NAME, 'captcha_code')
SUBMIT_BUTTON = (By.ID, 'submit')
LOGIN_CONTENT = (By.CSS_SELECTOR, 'div.login-content.ng-scope')
```

### 4.2 課程列表頁面 (CourseListPage)

```python
MY_COURSES_LINK = (By.LINK_TEXT, "我的課程")
GO_BACK_LINK = (By.XPATH, "//a[@class='go-back-link' and span[text()='返回']]")

# 課程選擇（按優先順序）
COURSE_STRATEGIES = [
    (By.LINK_TEXT, "{course_name}"),
    (By.PARTIAL_LINK_TEXT, "{course_name[:30]}"),
    (By.XPATH, "//a[@ng-bind='course.display_name' and contains(text(), '{name}')]"),
    (By.XPATH, "//a[contains(text(), '{name}')]")
]

# 修習中課程
IN_PROGRESS_LABEL = (By.XPATH, "//span[contains(text(), '修習中')]")
```

### 4.3 課程詳情頁面 (CourseDetailPage)

```python
CLICKABLE_AREA = (By.XPATH, "//div[@class='clickable-area']")
BACK_TO_COURSE = (By.XPATH, "//a[@ng-click='goBackCourse({course_id})']")

# 已閱讀時數提取（按優先順序）
DURATION_STRATEGIES = [
    "//*[contains(text(), '已閱讀時數')]",
    "//*[contains(text(), '分鐘') and contains(text(), '閱讀')]",
    "//div[contains(@class, 'course-info')]//div[contains(text(), '分鐘')]"
]
```

### 4.4 考試詳情頁面 (ExamDetailPage)

```python
# 考試選擇
EXAM_STRATEGIES = [
    (By.LINK_TEXT, "{exam_name}"),
    (By.PARTIAL_LINK_TEXT, "{exam_name[:20]}"),
    (By.XPATH, "//a[@ng-bind='activity.title' and contains(text(), '{name}')]"),
    (By.XPATH, "//a[@ng-click='changeActivity(activity)' and contains(., '{name}')]")
]

# 繼續答題按鈕
CONTINUE_EXAM_STRATEGIES = [
    (By.XPATH, "//a[contains(@class, 'take-exam') and contains(., '繼續答題')]"),
    (By.XPATH, "//a[contains(@class, 'take-exam') and contains(., '開始答題')]"),
    (By.XPATH, "//a[contains(@ng-click, 'openStartExamConfirmationPopup')]")
]

# 同意勾選框
AGREEMENT_CHECKBOX = (By.XPATH, "//input[@type='checkbox' and @name='confirm']")

# 彈窗確認按鈕
POPUP_CONFIRM = (By.XPATH, "//button[@ng-click='takeExam(exam.referrer_type)']")
```

### 4.5 考試答題頁面 (ExamAnswerPage)

```python
SUBJECT_LIST = (By.CLASS_NAME, "subject")
SUBJECT_DESCRIPTION = (By.CLASS_NAME, "subject-description")
OPTION_LIST = (By.CLASS_NAME, "option")
OPTION_CONTENT = (By.CLASS_NAME, "option-content")
RADIO_INPUT = (By.CSS_SELECTOR, "input[type='radio']")
CHECKBOX_INPUT = (By.CSS_SELECTOR, "input[type='checkbox']")

# 提交按鈕
SUBMIT_BUTTON = (By.XPATH, "//a[contains(@class, 'submit-exam')]")
CONFIRM_SUBMIT = (By.XPATH, "//button[contains(@class, 'button-green')]")
```

---

## 5. 攔截器規格

### 5.1 訪問時長攔截器 (VisitDurationInterceptor)

**觸發條件**:
```python
flow.request.path == "/statistics/api/user-visits"
flow.request.method == "POST"
```

**修改邏輯**:
```python
# 解析 payload
payload = json.loads(flow.request.get_text())

# 驗證必填欄位
assert all(k in payload for k in ["course_code", "course_name", "visit_duration"])

# 修改時長
payload["visit_duration"] += self.increase_duration

# 更新請求
flow.request.set_text(json.dumps(payload))
```

**預設增加時長**: 9000 秒 (150 分鐘)

### 5.2 考試自動答題攔截器 (ExamAutoAnswerInterceptor)

**階段 1: 攔截題目 (response)**

```python
# 觸發條件
'/api/exams/' in url and '/distribute' in url
flow.request.method == 'GET'

# 處理邏輯
1. 解析響應 JSON
2. 提取 exam_paper_instance_id
3. 遍歷 subjects
4. 匹配題庫答案
5. 存儲到 exam_data_store[exam_id]
```

**階段 2: 注入答案 (request)**

```python
# 觸發條件
'/api/exams/' in url and '/submissions' in url
flow.request.method == 'POST'

# 處理邏輯
1. 解析請求 JSON
2. 查找 exam_data_store[exam_id]
3. 遍歷 subjects，注入 answer_option_ids
4. 更新 progress.answered_num
5. 更新請求
```

**答案匹配算法**:
```python
def match_answer(web_question, bank_questions):
    # 1. 標準化文字
    normalized = normalize(web_question)

    # 2. 精確匹配
    for q in bank_questions:
        if normalize(q.description) == normalized:
            return q, 1.0

    # 3. 模糊匹配
    best_match = None
    best_score = 0
    for q in bank_questions:
        score = SequenceMatcher(None, normalized, normalize(q.description)).ratio()
        if score > best_score:
            best_score = score
            best_match = q

    # 4. 信心門檻
    if best_score >= CONFIDENCE_THRESHOLD:  # 0.85
        return best_match, best_score

    return None, 0
```

---

## 6. 流程規格

### 6.1 h 選項 2 Stage 6 考試流程

```
┌─────────────────────────────────────────────────────────────┐
│  [1/5] 點擊考試名稱                                          │
│        ├─ 調用: exam_detail_page.click_exam_by_name()       │
│        ├─ 延遲: 3.0 秒                                       │
│        └─ 等待: URL 包含 'learning-activity/full-screen'    │
│                                                             │
│  [2/5] Before 截圖（開始答題前）                              │
│        ├─ 滾動: scroll_to_bottom_multi_strategy() x2       │
│        ├─ 等待: 6 秒 + 頁面高度穩定                          │
│        └─ 截圖: exam_{id}_before.png                        │
│                                                             │
│  [3/5] 開始答題                                              │
│        ├─ 點擊: 繼續答題按鈕                                 │
│        ├─ 勾選: 同意 checkbox                               │
│        ├─ 點擊: 確認按鈕                                     │
│        └─ 等待: 3.0 秒                                       │
│                                                             │
│  [4/5] 自動提交考卷                                          │
│        ├─ API 攔截器自動注入答案                             │
│        └─ 調用: exam_answer_page.submit_exam_directly()     │
│                                                             │
│  [5/5] After 截圖（提交後）                                   │
│        ├─ 等待: 2.0 秒（結果顯示）                           │
│        ├─ 滾動: scroll_to_bottom_multi_strategy()           │
│        └─ 截圖: exam_{id}_after.png                         │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 scroll_to_bottom_multi_strategy 規格

```python
def scroll_to_bottom_multi_strategy(drv, max_scrolls=10, wait_time=2.0):
    """
    多策略滾動到頁面底部並等待 Lazy-load 元素載入

    Args:
        drv: WebDriver 實例
        max_scrolls: 最大滾動迭代次數，預設 10
        wait_time: 每次滾動後等待時間（秒），預設 2.0

    策略:
        策略 1: 檢測 body 是否被鎖住
            - getComputedStyle(body).overflow === 'hidden'
            - getComputedStyle(html).overflow === 'hidden'
            - 若被鎖住，避免無效的 window.scrollTo

        策略 2: 檢測 Modal/Dialog（雙滾動條問題）
            - 搜尋 Modal 選擇器（優先順序）：
              1. 考試頁面專用：
                 .reveal-modal:not([style*="display: none"]),
                 .popup-area:not([style*="display: none"])
              2. 通用 Modal：
                 .modal, .modal-dialog, .modal-content, .modal-body,
                 .dialog, .popup, .overlay-content,
                 [role="dialog"], [role="alertdialog"],
                 .ant-modal, .el-dialog, .MuiDialog-root,
                 .v-dialog, .chakra-modal__content
            - 檢測 Modal 內可滾動容器（scrollHeight > clientHeight + 10）
            - 若有 Modal，優先滾動 Modal 內部

        策略 3: 偵測一般滾動容器
            - 搜尋可能的滾動容器（優先順序）：
              1. 考試頁面專用（基於 Burp Suite 分析）：
                 .fullscreen-right, .activity-content-box, .exam-subjects,
                 .submission-list.exam-area, .sync-scroll
              2. 通用容器：
                 .main-container, .content-wrapper, .scroll-container,
                 .app-content, .page-content, [class*="scroll"],
                 main, #main, #content, .container
            - 判斷容器條件: scrollHeight > clientHeight

        策略 4: scrollTo 直接滾動（根據環境選擇）
            - 有 Modal → 滾動 Modal 內容器
            - body 被鎖住但有容器 → 滾動容器
            - 有容器 → 滾動容器 + window（雙保險）
            - 預設 → window.scrollTo

        策略 5: scrollBy 增量滾動（觸發 lazy load）
            - 僅在 body 未鎖住時執行
            - window.scrollBy(0, viewport_height)

        策略 6: scrollIntoView 元素定位滾動
            - lastElement.scrollIntoView({behavior: 'instant', block: 'end'})

        策略 7: 等待高度穩定
            - 取 Math.max(body.scrollHeight, documentElement.scrollHeight)
            - 連續兩次相同才視為載入完成

    Returns:
        int: 執行的滾動迭代次數
    """
```

**關鍵技術點**:

| 問題 | 解決策略 |
|------|----------|
| body overflow: hidden | 策略 1 檢測鎖定狀態，避免無效滾動 |
| Modal/Dialog 雙滾動條 | 策略 2 偵測 Modal，滾動 Modal 內部 |
| 不是 body 在滾 | 策略 3 偵測真正的滾動容器 |
| Selenium 太早動手 | 策略 7 等待高度穩定（連續確認） |
| 虛擬清單/Lazy Load | 策略 5 scrollBy 觸發載入 |
| 滾動條變短 | 取 max(body, documentElement) 高度 |

**Modal 選擇器支援**:

| 框架 | 選擇器 |
|------|--------|
| **考試頁面** | `.reveal-modal`, `.popup-area` |
| Bootstrap | `.modal`, `.modal-dialog`, `.modal-body` |
| Ant Design | `.ant-modal` |
| Element UI | `.el-dialog` |
| Material-UI | `.MuiDialog-root` |
| Vuetify | `.v-dialog` |
| Chakra UI | `.chakra-modal__content` |
| 通用 | `[role="dialog"]`, `[role="alertdialog"]` |

**考試頁面滾動容器**（基於 Burp Suite 分析）:

| 選擇器 | 用途 |
|--------|------|
| `.fullscreen-right` | 全螢幕模式主內容區 |
| `.activity-content-box` | 活動內容容器 |
| `.exam-subjects` | 考試題目區域 |
| `.submission-list.exam-area` | 提交歷史列表 |
| `.sync-scroll` | 同步滾動區域（表格用） |

**使用場景**:

| 場景 | max_scrolls | wait_time | 說明 |
|------|-------------|-----------|------|
| Before 截圖（主要） | 10 | 2.0 | 完整載入所有 Lazy-load 內容 |
| Before 截圖（確認） | 3 | 1.5 | 額外確認滾動 |
| After 截圖 | 5 | 1.5 | 結果頁面載入 |

### 6.3 課程選擇重試邏輯

```python
def select_course(course_name, max_retries=3):
    """
    選擇課程，帶重試機制

    重試策略（按順序）:
        1. LINK_TEXT 完全匹配
        2. PARTIAL_LINK_TEXT 部分匹配
        3. XPath + ng-bind
        4. XPath + contains

    每種策略失敗後等待 2 秒再試下一種
    """
```

---

## 7. 資料格式規格

### 7.1 時間格式

| 用途 | 格式 | 範例 |
|------|------|------|
| 日期時間 | `%Y-%m-%d %H:%M:%S` | 2025-12-27 14:30:00 |
| 檔案名稱 | `%Y%m%d_%H%M%S` | 20251227_143000 |
| API 時間戳 | `%Y/%m/%dT%H:%M:%S` | 2025/12/27T14:30:00 |
| ISO8601 | `%Y-%m-%dT%H:%M:%SZ` | 2025-12-27T14:30:00Z |

### 7.2 題庫格式

```json
{
  "分類名稱": [
    {
      "subjects": [
        {
          "id": 1,
          "description": "題目文字（可含 HTML）",
          "options": [
            {"id": "opt1", "content": "選項 A"},
            {"id": "opt2", "content": "選項 B"}
          ],
          "answer": ["opt1"]
        }
      ]
    }
  ]
}
```

### 7.3 狀態碼

```python
# 課程狀態
STATUS_NOT_STARTED = 'not_started'
STATUS_IN_PROGRESS = 'in_progress'
STATUS_COMPLETED = 'completed'
STATUS_PASSED = 'passed'
STATUS_FAILED = 'failed'

# 執行狀態
EXEC_SUCCESS = 'success'
EXEC_FAILED = 'failed'
EXEC_PENDING = 'pending'
EXEC_SKIPPED = 'skipped'

# 題型
QUESTION_SINGLE = 'single'
QUESTION_MULTIPLE = 'multiple'
QUESTION_TRUE_FALSE = 'true_false'
```

---

## 8. 邊界條件

### 8.1 超時邊界

| 操作 | 超時時間 | 處理方式 |
|------|----------|----------|
| 頁面載入 | 40 秒 | 拋出 TimeoutException |
| 元素等待 | 10 秒 | 重試或跳過 |
| API 請求 | 30 秒 | 重試 3 次 |
| Payload 捕獲 | 5 秒 | 標記失敗 |
| 考試頁面載入 | 15 秒 | 繼續執行 |

### 8.2 重試邊界

| 操作 | 最大重試 | 重試間隔 |
|------|----------|----------|
| 登入 | 3 次 | 5 秒 |
| 課程選擇 | 3 次 | 2 秒 |
| API 請求 | 3 次 | 3 秒 |
| 驗證碼 | 3 次 | 2 秒 |

### 8.3 數值邊界

| 項目 | 最小值 | 最大值 | 預設值 |
|------|--------|--------|--------|
| 訪問時長增加 | 60 秒 | 無限制 | 9000 秒 |
| 信心閾值 | 0.0 | 1.0 | 0.85 |
| Proxy 端口 | 1024 | 65535 | 8080 |
| 滾動嘗試次數 | 1 | 10 | 5 |

---

## 9. 異常規格

### 9.1 異常層次結構

```
EEBotError (基類)
│
├── ConfigError
│   ├── ConfigFileNotFoundError
│   ├── ConfigValidationError
│   └── ConfigKeyMissingError
│
├── AuthenticationError
│   ├── LoginError
│   ├── CaptchaError
│   └── SessionExpiredError
│
├── WebDriverError
│   ├── DriverInitializationError
│   ├── ElementNotFoundError
│   └── PageLoadTimeoutError
│
├── ProxyError
│   ├── ProxyStartError
│   ├── ProxyStopError
│   └── ProxyConnectionError
│
├── ScanError
│   ├── CourseNotFoundError
│   ├── PayloadNotFoundError
│   └── ScanTimeoutError
│
├── APIError
│   ├── APIRequestError
│   ├── APIResponseError
│   └── APITimeoutError
│
├── DataError
│   ├── InvalidDataError
│   ├── DataParseError
│   └── DataValidationError
│
└── ExamError
    ├── QuestionNotFoundError
    ├── AnswerMatchError
    └── SubmissionError
```

### 9.2 異常介面

```python
class EEBotError(Exception):
    def __init__(self, message: str, **details):
        self.message = message
        self.details = details
        super().__init__(message)

    def to_dict(self) -> dict:
        return {
            'error': self.__class__.__name__,
            'message': self.message,
            'details': self.details
        }
```

---

## 10. 檔案路徑規格

### 10.1 固定路徑

| 用途 | 路徑 |
|------|------|
| 配置檔案 | `config/eebot.cfg` |
| Cookie 存儲 | `resource/cookies/cookies.json` |
| 題庫預設 | `resource/question_bank.json` |
| Stealth JS | `resource/plugins/stealth.min.js` |
| 日誌檔案 | `logs/eebot.log` |

### 10.2 動態路徑格式

| 用途 | 格式 | 範例 |
|------|------|------|
| 批量結果 | `batch_result_{timestamp}.json` | batch_result_20251227_143000.json |
| 快速完成 | `quick_complete_result_{timestamp}.json` | quick_complete_result_20251227_143000.json |
| 混合掃描 | `hybrid_scan_result.json` | - |
| 截圖目錄 | `reports/exam_screenshots/` | - |
| 截圖檔案 | `exam_{id}_before.png` / `exam_{id}_after.png` | exam_48_before.png |

---

## 附錄 A: 變更禁止事項

以下為關鍵邏輯，**禁止未經授權修改**：

1. **ProxyManager 使用 Threading**（非 multiprocessing）
2. **Stage 6 重啟瀏覽器邏輯**（use_proxy=True）
3. **答案匹配權重**（40% 題目 + 60% 選項）
4. **scroll_to_bottom_multi_strategy 多策略滾動邏輯**
5. **Before 截圖在「開始答題」之前**

---

## 附錄 B: 版本歷史

| 版本 | 日期 | 說明 |
|------|------|------|
| 1.0 | 2025-12-27 | 初版建立 |

---

**文檔結束**
