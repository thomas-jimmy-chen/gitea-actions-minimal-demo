# 考試頁面渲染流程分析報告

**專案**: EEBot v2.3.8 (代號: AliCorn 天角獸)
**分析日期**: 2025-12-27
**資料來源**: Burp Suite 捕獲 (`高齡測驗(100分及格).txt`)
**分析者**: Claude Code (Opus 4.5)

---

## 1. 執行摘要

本報告分析從點擊考試連結到頁面完全渲染的完整流程，包含 16 個 HTTP 請求的時序、技術規格和滾動容器識別。

### 關鍵發現

| 項目 | 發現 |
|------|------|
| 總請求數 | 16 個 |
| 渲染時間 | 約 20 秒 (08:27:07 - 08:27:27) |
| 主頁面大小 | 1.4MB (HTML) |
| 框架技術 | AngularJS + Vue.js 混合 |
| 滾動容器 | `fullscreen-right` > `activity-content-box` > `exam-subjects` |
| Body 初始狀態 | `display: none` (JavaScript 控制顯示) |

---

## 2. 請求時序分析

### 2.1 完整請求列表

| # | 時間 | 方法 | 端點 | 類型 | 大小 | 用途 |
|---|------|------|------|------|------|------|
| 01 | 08:27:07 | GET | `/api/courses/452/exam-scores` | JSON | 1.4KB | 獲取考試分數列表 |
| 02 | 08:27:24 | POST | `/statistics/api/user-visits` | - | 443B | 記錄用戶訪問 |
| 03 | 08:27:24 | GET | `/course/452/learning-activity/full-screen` | HTML | 1.4MB | **主頁面** |
| 04 | 08:27:26 | GET | `/api/courses/452?fields=...` | JSON | 2.2KB | 課程詳情 |
| 05 | 08:27:26 | GET | `/api/courses/452/modules` | JSON | 1.3KB | 課程模組 |
| 06 | 08:27:26 | GET | `/api/courses/452/exams` | JSON | 3.3KB | 考試列表 |
| 07 | 08:27:26 | GET | `/api/courses/452/classroom-list` | JSON | 988B | 教室列表 |
| 08 | 08:27:26 | GET | `/api/courses/452/activities` | JSON | 8.7KB | 活動列表 |
| 09 | 08:27:26 | GET | `/api/exams/48/zip-status` | JSON | 989B | 考卷壓縮狀態 |
| 10 | 08:27:26 | GET | `/api/exams/48` | JSON | 3.4KB | 考試詳情 |
| 11 | 08:27:26 | POST | `/api/course/activities-read/exam/48` | JSON | 758B | 標記已讀 |
| 12 | 08:27:26 | GET | `/api/exams/48/submissions/storage` | JSON | 882B | 暫存答案 (404) |
| 13 | 08:27:26 | GET | `/api/exam/48/make-up-record` | JSON | 972B | 補考記錄 |
| 14 | 08:27:26 | GET | `/api/exams/48/subjects-summary` | JSON | 1.9KB | 題目摘要 |
| 15 | 08:27:26 | GET | `/api/exams/48/submissions` | JSON | 15.5KB | 提交歷史 |
| 16 | 08:27:27 | GET | `/api/exams/48/subjects-summary` | JSON | 1.9KB | 題目摘要 (重複) |

### 2.2 請求階段分析

```
Phase 1: 預載入 (08:27:07)
├── GET /api/courses/452/exam-scores
└── 目的: 預載考試成績，準備顯示

Phase 2: 頁面請求 (08:27:24)
├── POST /statistics/api/user-visits (追蹤)
└── GET /course/452/learning-activity/full-screen (主頁面 1.4MB)

Phase 3: 並行 API 請求 (08:27:26)
├── 課程相關 (4 個並行)
│   ├── GET /api/courses/452?fields=...
│   ├── GET /api/courses/452/modules
│   ├── GET /api/courses/452/exams
│   └── GET /api/courses/452/activities
│
├── 考試相關 (6 個並行)
│   ├── GET /api/exams/48/zip-status
│   ├── GET /api/exams/48
│   ├── POST /api/course/activities-read/exam/48
│   ├── GET /api/exams/48/submissions/storage
│   ├── GET /api/exam/48/make-up-record
│   └── GET /api/exams/48/subjects-summary
│
└── GET /api/exams/48/submissions

Phase 4: 最終確認 (08:27:27)
└── GET /api/exams/48/subjects-summary (重複請求)
```

---

## 3. HTML 頁面結構分析

### 3.1 技術棧

| 技術 | 版本/說明 | 用途 |
|------|----------|------|
| AngularJS | ng-app="activity" | 主框架，模板渲染 |
| Vue.js | vue-announcement, vue-alert | 公告和警告組件 |
| MathJax | mathjax-ignore class | 數學公式渲染 |
| CSS | 10+ 樣式表 | 延遲載入 (media="none") |
| JavaScript | LMS-main bundle | 主業務邏輯 |

### 3.2 Body 初始化

```html
<style>body{display: none}</style>

<body -ng-app="activity"
      ng-strict-di
      on-modal-state-change
      ng-init="isInstructorView = false; ..."
      class='fullscreen-activity mathjax-ignore'>
```

**關鍵點**:
- Body 初始 `display: none`，由 JavaScript 控制顯示
- 使用 `fullscreen-activity` class 表示全螢幕模式
- `mathjax-ignore` 防止 MathJax 處理整個 body

### 3.3 頁面結構層級

```
<body class='fullscreen-activity'>
│
├── <div id="end-date-filter-popup" class="reveal-modal popup-area">
│   └── 過期提醒 Modal (隱藏)
│
├── <div class="wrapper">
│   │
│   ├── <div id="announcement">
│   │   └── Vue 公告組件
│   │
│   ├── <div id="alertMessages">
│   │   └── Vue 警告組件
│   │
│   ├── <div ng-controller="HeaderWarningController">
│   │   └── 瀏覽器/密碼過期警告
│   │
│   └── <div class="fullscreen-right">  ← 主內容區
│       │
│       └── <div class="activity-content-box syllabus-activity-content">
│           │
│           └── <ng-template id="exam/_show_exam_activity.html">
│               │
│               └── <div class="exam-activity-box" ng-controller="ExamController">
│                   │
│                   ├── <div ng-controller="ExamActivityShowController">
│                   │   ├── 考試標題
│                   │   ├── 考試狀態警告
│                   │   └── 分數顯示
│                   │
│                   ├── <div class="exam-subjects">  ← 題目容器
│                   │   └── <ol class="subjects-jit-display">
│                   │       └── <li class="subject" ng-repeat="...">
│                   │           ├── 題目標題
│                   │           └── 答案選項
│                   │
│                   └── <div class="submission-list exam-area">
│                       └── 提交歷史列表
│
└── <div class="reveal-modal popup-area">  ← 各種 Modal
    └── 確認對話框、檔案選擇器等
```

---

## 4. 滾動容器識別

### 4.1 主要滾動區域

基於 HTML 分析，識別出以下滾動容器：

| 優先級 | 選擇器 | 說明 |
|--------|--------|------|
| 1 | `.fullscreen-right` | 全螢幕右側主內容區 |
| 2 | `.activity-content-box` | 活動內容容器 |
| 3 | `.exam-subjects` | 考試題目區域 |
| 4 | `.submission-list.exam-area` | 提交歷史列表 |
| 5 | `.sync-scroll` | 同步滾動區域 (表格用) |

### 4.2 Modal 對話框

頁面包含多個 Modal，可能造成雙滾動條問題：

| Class | 用途 |
|-------|------|
| `.reveal-modal.popup-area.popup-480` | 小型確認框 (480px) |
| `.reveal-modal.popup-area.popup-600` | 中型對話框 (600px) |
| `.reveal-modal.popup-area.popup-1080` | 大型對話框 (1080px) |
| `.reveal-modal.popup-area.popup-full-page` | 全頁面對話框 |

### 4.3 滾動策略建議

```javascript
// 建議的滾動目標偵測順序
const scrollTargets = [
    // 1. Modal 內容 (如果 Modal 可見)
    '.reveal-modal:not([style*="display: none"]) .popup-content',

    // 2. 全螢幕內容區
    '.fullscreen-right',

    // 3. 活動內容區
    '.activity-content-box',

    // 4. 考試題目區
    '.exam-subjects',

    // 5. 同步滾動區
    '.sync-scroll',

    // 6. 預設 body
    'body'
];
```

---

## 5. 技術規格邊界

### 5.1 AngularJS 控制器

| 控制器 | 用途 | 初始化變數 |
|--------|------|-----------|
| `ExamController` | 考試主控制 | `scoreRuleMap`, `courseId` |
| `ExamActivityShowController` | 考試顯示 | `i18nMessages` |
| `ExamSubmissionListController` | 提交列表 | - |
| `HeaderWarningController` | 警告訊息 | `changePasswordNotifyInterval` |

### 5.2 CSS 延遲載入

```html
<link rel="stylesheet" href="/static/styles-*.css"
      media="none"
      onload="if(media!='all')media='all'">
```

**影響**: 樣式表延遲載入，可能導致 FOUC (Flash of Unstyled Content)

### 5.3 渲染時機

| 事件 | 預估時間 | 說明 |
|------|----------|------|
| HTML 下載完成 | +0ms | 1.4MB 需要時間 |
| CSS 載入 | +500ms | 10+ 樣式表 |
| AngularJS 初始化 | +1000ms | 模板編譯 |
| API 數據到達 | +2000ms | 約 12 個 API |
| 題目渲染完成 | +3000ms | ng-repeat 渲染 |
| 頁面穩定 | +5000ms | 所有動態內容完成 |

---

## 6. 實務執行建議

### 6.1 滾動前等待策略

```python
# 建議等待條件
def wait_for_exam_page_ready(driver, timeout=15):
    """等待考試頁面完全載入"""

    # 1. 等待 URL 包含考試路徑
    WebDriverWait(driver, timeout).until(
        lambda d: 'learning-activity/full-screen#/exam/' in d.current_url
    )

    # 2. 等待 body 可見 (display != none)
    WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((By.TAG_NAME, 'body'))
    )

    # 3. 等待考試題目容器出現
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.exam-subjects'))
    )

    # 4. 等待題目列表有內容
    WebDriverWait(driver, timeout).until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, '.subject')) > 0
    )

    # 5. 額外等待動態內容穩定
    time.sleep(2)
```

### 6.2 多策略滾動實現

```python
def scroll_exam_page(driver):
    """考試頁面專用滾動"""

    # 策略 1: 檢查 Modal 是否存在
    modal = driver.execute_script("""
        var modal = document.querySelector('.reveal-modal:not([style*="display: none"])');
        if (modal) {
            var content = modal.querySelector('.popup-content');
            if (content && content.scrollHeight > content.clientHeight) {
                return 'modal';
            }
        }
        return null;
    """)

    if modal:
        driver.execute_script("""
            var content = document.querySelector('.reveal-modal .popup-content');
            content.scrollTo(0, content.scrollHeight);
        """)
        return

    # 策略 2: 滾動 fullscreen-right
    driver.execute_script("""
        var container = document.querySelector('.fullscreen-right');
        if (container) {
            container.scrollTo(0, container.scrollHeight);
        }
    """)

    # 策略 3: 同時滾動 window
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
```

### 6.3 截圖前置作業

```python
def prepare_screenshot(driver):
    """截圖前確保頁面狀態正確"""

    # 1. 關閉所有 Modal
    driver.execute_script("""
        document.querySelectorAll('.reveal-modal').forEach(function(modal) {
            modal.style.display = 'none';
        });
    """)

    # 2. 滾動到底部
    scroll_exam_page(driver)

    # 3. 等待滾動完成
    time.sleep(1.5)

    # 4. 確認高度穩定
    last_height = driver.execute_script("return document.body.scrollHeight")
    time.sleep(0.5)
    new_height = driver.execute_script("return document.body.scrollHeight")

    if last_height != new_height:
        # 如果高度變化，再等待
        time.sleep(1)
```

---

## 7. API 數據結構

### 7.1 考試分數 API

**端點**: `GET /api/courses/452/exam-scores`

```json
{
  "exam_scores": [
    {
      "activity_id": 48,
      "score": 100.0,
      "submission_scores": [100.0, 0.0, 0.0, 0.0, 90.0, 100.0, ...]
    }
  ]
}
```

### 7.2 題目摘要 API

**端點**: `GET /api/exams/48/subjects-summary`

```json
{
  "subjects": [
    {
      "has_audio": false,
      "id": 2932,
      "point": "10.0",
      "sub_subjects": [],
      "type": "single_selection"
    }
  ]
}
```

### 7.3 提交歷史 API

**端點**: `GET /api/exams/48/submissions`

```json
{
  "exam_final_score": null,
  "exam_score": 100.0,
  "exam_score_rule": "highest",
  "submissions": [
    {
      "created_at": "2025-06-30T13:28:12Z",
      "exam_id": 48,
      "exam_type_text": "...",
      "score": 100
    }
  ]
}
```

---

## 8. 結論與下一步

### 8.1 關鍵發現總結

1. **頁面結構複雜**: 1.4MB HTML，使用 AngularJS + Vue.js 混合架構
2. **滾動容器多層**: `fullscreen-right` → `activity-content-box` → `exam-subjects`
3. **Modal 影響**: 多個 Modal 可能造成雙滾動條
4. **延遲載入**: CSS 和 API 數據都是異步載入

### 8.2 建議的實施順序

1. **更新 `scroll_to_bottom_multi_strategy()`**
   - 添加 `.fullscreen-right` 選擇器
   - 添加 `.exam-subjects` 選擇器
   - 優化 Modal 檢測邏輯

2. **增強等待邏輯**
   - 等待 `.subject` 元素出現
   - 等待 API 響應完成
   - 等待高度穩定

3. **測試驗證**
   - 測試 Before 截圖位置
   - 測試 After 截圖位置
   - 確認 URL 一致性

---

**文檔版本**: 1.0
**建立日期**: 2025-12-27
**維護者**: Claude Code (Opus 4.5)
