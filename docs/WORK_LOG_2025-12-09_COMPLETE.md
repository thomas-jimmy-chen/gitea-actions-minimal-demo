# 工作日誌 - 2025-12-09 (完整版)

## 📊 今日總覽

**工作時間：** 上午 + 下午（全天）
**總體進度：** 60% → 95% ✅
**狀態：** 混合掃描功能基本完成，等待測試驗證

---

## 🌅 上午工作內容

### 🔍 子課程 API 端點研究

**目標：** 找到獲取主課程下子課程列表的 API

**收到的資料：**
- API 端點：`GET /api/courses/465`
- Burp Suite 封包：`api_courses_465_field.txt`

**分析結果：**

#### ❌ 這不是子課程列表 API

分析發現 `GET /api/courses/{id}` 返回的是：
- ✅ 單一課程的詳細資料
- ❌ **NOT** 子課程列表
- ❌ 沒有 lessons/units/topics 欄位

**關鍵欄位：**
```json
{
  "id": 465,
  "name": "性別平等工作法...",
  "is_child": false,
  "is_master": false,
  "students_count": 25481,
  "course_code": "901011114"
}
```

### 📁 上午創建的文檔

1. **analyze_course_detail_api.py** - 課程詳細資料 API 分析腳本
2. **COURSE_DETAIL_API_ANALYSIS.md** - 分析報告與下一步建議

---

## 🌆 下午工作內容（4 個主要階段）

### 階段 1: 子課程 API 發現與分析

**時間：** 下午 1:00 - 2:00

#### 🎯 收到正確的子課程 API

**API 端點：** `GET /api/courses/465/activities`
**封包檔案：** `api_courses_465_activities.txt`

#### ✅ 分析結果 - 找到了！

這個 API 返回課程的所有**學習活動 (activities)**，相當於子課程列表。

**關鍵發現：**
1. **Activities = 子課程**
   ```json
   {
     "activities": [
       {
         "id": 1492,
         "title": "怯場平息工作法與窮盡選擇法...",
         "type": "scorm",
         "sort": 1,
         "completion_criterion": "累積觀看時長達 100 分..."
       }
     ]
   }
   ```

2. **SCORM 結構包含章節列表（孫課程）**
   ```json
   {
     "uploads": [{
       "scorm": {
         "data": {
           "manifest": {
             "organizations": {
               "organization": {
                 "item": [
                   {"identifier": "...", "title": "一、導入簡介"},
                   {"identifier": "...", "title": "二、流程概述"}
                 ]
               }
             }
           }
         }
       }
     }]
   }
   ```

#### 📄 創建的文檔

- **COURSE_ACTIVITIES_API_ANALYSIS.md** - 詳細 API 分析報告
- **HYBRID_SCAN_IMPLEMENTATION_SUMMARY.md** - 實作總結

---

### 階段 2: 3 層遍歷實作（主課程 → 子課程）

**時間：** 下午 2:00 - 3:30

#### ✅ 實作內容

**1. 新增輔助函數** (`menu.py`, line 570-738)

`get_course_activities()`
- 調用 `/api/courses/{id}/activities` API
- 獲取子課程列表
- 完整的錯誤處理

`match_activities()`
- 匹配 API activities 與 Web 掃描項目
- 使用 `difflib.SequenceMatcher`
- 閾值：0.6 (60%)

**2. 整合到階段 4.5** (`menu.py`, line 1038-1123)

流程：
```
for 每個已匹配的主課程:
    1. 調用 get_course_activities() 獲取 API 子課程
    2. 從 web_courses 篩選該 program 的 Web 子課程
    3. 調用 match_activities() 執行匹配
    4. 統計匹配結果
    5. 將結果添加到 matched_course['activity_matches']
```

**3. 更新輸出結構**

JSON 輸出：
```json
{
  "summary": {
    "total_api_activities": 28,
    "matched_activities": 25,
    "activity_match_rate": 89.29
  },
  "matched_courses": [{
    "activity_matches": [...]
  }]
}
```

#### ⚠️ 遇到的錯誤

**錯誤：** `AttributeError: 'dict' object has no attribute 'lower'`

**原因：** `web_item['item_name']` 有時是 dict 而非 string

**修復：**
1. 在 `match_activities()` 添加類型檢查
2. 在 Web 掃描階段正確處理 dict 類型的課程資料

---

### 階段 3: 4 層遍歷實作（主課程 → 子課程 → 孫課程）

**時間：** 下午 3:30 - 5:00

#### 🎯 用戶需求

> "我之前是說 掃描 我的課程 -> 主課程 -> 子課程 遍歷，
> 現在要增加為到 我的課程 -> 主課程 -> 子課程 -> 孫課程 遍歷"

**要求：**
1. 需要與 Web 掃描匹配
2. 都要（JSON + 終端輸出）
3. 在 h 功能內實施

#### ✅ 實作內容

**1. 新增章節提取函數** (`menu.py`, line 618-664)

`extract_scorm_chapters()`
- 從 SCORM manifest 提取章節列表
- 處理嵌套的 JSON 結構
- 完整的容錯處理

**2. 新增章節匹配函數** (`menu.py`, line 666-738)

`match_chapters()`
- 匹配 API 章節與 Web 項目
- 閾值降低到 0.5 (50%)
- 原因：章節名稱較短，需要較寬鬆的匹配

**3. 整合到階段 4.5** (`menu.py`, line 1235-1285)

嵌套循環結構：
```python
for matched_course in matched_courses:
    for activity in activities:
        # 提取章節
        chapters = extract_scorm_chapters(activity)

        # 匹配章節
        chapter_matches = match_chapters(chapters, web_items)

        # 保存到 activity['chapter_matches']
```

**4. 更新輸出** (`menu.py`, lines 1375-1413)

終端輸出：
```
【主課程匹配】...
【子課程（活動）匹配】...
【孫課程（章節）匹配】  ← 新增
  API 章節總數: 28
  成功匹配: 25
  匹配率: 89.29%
```

JSON 輸出：
```json
{
  "summary": {
    "total_api_chapters": 28,
    "matched_chapters": 25,
    "chapter_match_rate": 89.29
  }
}
```

---

### 階段 4: Web 點擊流程修復

**時間：** 下午 5:00 - 6:00

#### ⚠️ 用戶發現問題

> "點了我的課程後，點擊了第一個子課程，就馬上按返回跳回主課程了"

#### 🔍 問題分析

**錯誤流程：**
```
1. 點擊主課程 A → 進入子課程列表
2. 獲取子課程列表
3. 立即 driver.back() 返回主課程列表  ← 問題！
4. 嘗試點擊子課程 → 失敗（已經不在子課程列表頁面）
```

**根本原因：**
- `get_program_courses_and_exams()` 在獲取子課程後立即返回
- 導致後續無法點擊子課程獲取章節

#### ✅ 修復方案

**1. 修改 `course_list_page.py`** (line 308-310)
- 移除 `get_program_courses_and_exams()` 中的 `driver.back()`
- 讓調用者決定何時返回

**2. 新增 `get_course_chapters()` 方法** (line 332-410)
- 點擊子課程
- 獲取章節列表
- 自動返回子課程列表

**3. 修改 `menu.py` 階段 3** (line 1080-1126)
```python
for course in courses:
    # 點擊進入子課程，獲取章節
    chapters = get_course_chapters(course_name)

    # 將章節添加到 web_courses
    for chapter in chapters:
        web_courses.append({
            'item_type': 'chapter',
            'item_name': chapter['name'],
            'parent_course': course_name
        })

# 處理完所有子課程後，返回主課程列表
driver.back()
```

**正確流程：**
```
1. 點擊主課程 A → 停留在子課程列表
2. 點擊子課程 1 → 獲取章節 → 返回子課程列表
3. 點擊子課程 2 → 獲取章節 → 返回子課程列表
4. 處理完所有子課程 → 返回主課程列表
5. 繼續處理主課程 B...
```

---

### 階段 5: 改為以 Web 為主的匹配邏輯

**時間：** 下午 6:00 - 7:00

#### 🎯 用戶需求

> "匹配的邏輯上，以 web 的為主，非 web 的一律去除，
> 我要看看 web 掃描出來的，是否會與 api 的完成完整的匹配"

**核心要求：**
- 以 Web 掃描為主
- 去除 API 獨有的項目
- 檢驗 Web 項目與 API 的匹配完整度

#### ✅ 實作變更

**1. 修改階段 4 匹配邏輯** (`menu.py`, line 1144-1229)

**之前（以 API 為主）：**
```python
for api_course in api_courses:
    找到對應的 Web 課程
    if 找到:
        matched_courses.append(...)
    else:
        unmatched_api_courses.append(...)  # 保留未匹配的 API
```

**現在（以 Web 為主）：**
```python
# 按 program_name 分組 Web 課程
for program_name, web_items in web_programs.items():
    找到對應的 API 課程

    if 找到:
        matched_courses.append({
            'api_data': {...},
            'web_data': {'program_name': ..., 'items': web_items}
        })
    else:
        # 仍保留該 Web 課程，標記無 API
        matched_courses.append({
            'api_data': None,
            'web_data': {'program_name': ..., 'items': web_items}
        })

# 不再追蹤 unmatched_api_courses（去除 API 獨有的）
```

**2. 修改階段 4.5** (`menu.py`, line 1251-1282)
```python
for matched_course in matched_courses:
    # 檢查是否有對應的 API
    if matched_course['api_data'] is None:
        print(f'跳過: {program_name}... (無對應 API)')
        continue

    # 有 API 才調用 activities API
    course_id = matched_course['api_data']['course_id']
    api_activities = get_course_activities(course_id, ...)
```

**3. 更新輸出結構** (`menu.py`, line 1416-1464)

JSON 輸出：
```json
{
  "summary": {
    "total_api_courses": 18,
    "total_web_programs": 15,
    "total_web_items": 120,
    "web_with_api": 14,      // 有對應 API
    "web_without_api": 1,    // 無對應 API
    "match_rate": 93.33      // 基於 Web 的匹配率
  },
  "courses": [...],          // 所有 Web 課程
  "note": "以 Web 為主，api_data 為 None 表示無對應 API"
}
```

終端輸出：
```
掃描摘要（以 Web 為主）
======================================================================

【主課程匹配】
  API 課程總數:         18
  Web 主課程總數:       15
  Web 項目總數:         120 (含子課程、章節)
  有對應 API:           14
  無對應 API:           1
  匹配率:               93.33%
```

---

## 📁 今日創建/更新的文件

### 分析文檔
1. `COURSE_DETAIL_API_ANALYSIS.md` - 課程詳細 API 分析
2. `COURSE_ACTIVITIES_API_ANALYSIS.md` - 子課程 API 分析
3. `HYBRID_SCAN_IMPLEMENTATION_SUMMARY.md` - 實作總結

### 代碼文件
1. `menu.py` - 主要修改（~500 行變更）
   - 新增 3 個輔助函數
   - 修改階段 3、4、4.5
   - 更新輸出結構

2. `src/pages/course_list_page.py` - 新增方法
   - `get_course_chapters()` - 獲取章節列表

### 工作日誌
1. `docs/WORK_LOG_2025-12-09_COMPLETE.md` - 今日完整工作日誌（本文檔）

---

## 📊 最終完成進度

```
混合掃描功能 (h 選項)
├─ 階段 1: 初始化登入 ✅ 100%
├─ 階段 2: API 掃描
│   ├─ 主課程 API ✅ 100%
│   └─ 子課程 API ✅ 100%
├─ 階段 3: Web 掃描
│   ├─ 主課程掃描 ✅ 100%
│   ├─ 子課程掃描 ✅ 100%
│   └─ 孫課程掃描 ✅ 100%
├─ 階段 4: 主課程匹配 ✅ 100%
├─ 階段 4.5: 子課程匹配 ✅ 100%
└─ 輸出 JSON/終端 ✅ 100%

總體進度: 95%
剩餘工作: 測試驗證 (5%)
```

---

## 🎯 技術要點總結

### 1. 4 層遍歷架構

```
我的課程
  └─ 主課程（API: /api/my-courses）
      ├─ 匹配邏輯: API.name ←→ Web.program_name
      │
      └─ 子課程（API: /api/courses/{id}/activities）
          ├─ 匹配邏輯: API.activity.title ←→ Web.item_name
          │
          └─ 孫課程（SCORM: manifest.organizations.item）
              └─ 匹配邏輯: API.chapter.title ←→ Web.item_name
```

### 2. 匹配閾值策略

- **主課程**: 0.7 (70%) - 名稱較長較精確
- **子課程**: 0.6 (60%) - 名稱中等長度
- **孫課程**: 0.5 (50%) - 名稱較短，需較寬鬆匹配

### 3. Web 點擊流程

```python
# 正確流程
for program in programs:
    點擊主課程  # 進入子課程列表頁面

    for course in courses:
        點擊子課程  # 進入章節頁面
        獲取章節
        driver.back()  # 返回子課程列表

    driver.back()  # 返回主課程列表
```

### 4. 以 Web 為主的設計哲學

**優點：**
- 確保所有 Web 掃描的內容都在結果中
- 清楚標示哪些 Web 項目有對應的 API
- 更符合用戶驗證需求

**實現：**
- `matched_courses` 包含所有 Web 課程
- `api_data: None` 表示該 Web 課程無對應 API
- 不保留 `unmatched_api_courses`（去除 API 獨有項目）

---

## 🐛 今日解決的 Bug

### Bug 1: Type Error - 'dict' object has no attribute 'lower'

**原因:** Web 掃描的 item_name 有時是 dict 而非 string

**修復:**
```python
# 添加類型檢查
if not isinstance(web_item, dict):
    continue

web_name = web_item.get('item_name', '')
if not isinstance(web_name, str):
    continue
```

### Bug 2: Web 點擊流程錯誤

**原因:** 過早調用 `driver.back()`，導致後續點擊失敗

**修復:**
1. 移除 `get_program_courses_and_exams()` 中的 `driver.back()`
2. 在處理完所有子課程後才調用 `driver.back()`

---

## 📝 待辦事項

### ⏳ 高優先級（用戶測試後）

- [ ] 根據測試結果修復 bug
- [ ] 優化選擇器（如果 Web 掃描失敗）
- [ ] 調整匹配閾值（如果匹配率不理想）

### 📋 中優先級

- [ ] 更新 CHANGELOG.md
- [ ] 更新 README.md（新增混合掃描說明）
- [ ] 撰寫混合掃描使用指南

### 📝 低優先級

- [ ] 代碼重構（拆分大函數）
- [ ] 撰寫單元測試
- [ ] 效能優化

---

## 💡 經驗教訓

### 1. API 端點發現

- ✅ 實際測試比猜測更快
- ✅ Burp Suite 是關鍵工具
- ✅ 命名可能不符合預期（activities 而非 lessons）

### 2. 錯誤處理

- ✅ 類型檢查很重要（dict vs string）
- ✅ 早期發現問題可節省大量時間
- ✅ 用戶測試可發現邏輯錯誤（點擊流程）

### 3. 需求變更管理

- ✅ 3 層 → 4 層擴展相對容易（模組化設計）
- ✅ 以 API 為主 → 以 Web 為主需要重構
- ✅ 清晰的代碼結構使變更更容易

### 4. Token 管理

- ✅ 分階段執行，避免一次性消耗過多
- ✅ 重要節點保存進度
- ✅ 文檔優先，確保知識不流失

---

## 🎉 今日成就

1. ✅ **完整實現 4 層遍歷** - 主課程 → 子課程 → 孫課程
2. ✅ **修復 Web 點擊流程** - 正確的返回時機
3. ✅ **改為 Web 為主邏輯** - 符合用戶驗證需求
4. ✅ **完整的輸出結構** - JSON + 終端雙重輸出
5. ✅ **詳細的文檔記錄** - 3 份分析文檔 + 工作日誌

**總代碼變更：**
- 新增：~600 行
- 修改：~300 行
- 文件：10+ 個

---

**最後更新：** 2025-12-09 19:30
**狀態：** 等待用戶測試驗證
**下一步：** 根據測試結果進行修復/優化
