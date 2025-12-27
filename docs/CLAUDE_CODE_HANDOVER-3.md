# Claude Code 交接文檔 - 批量模式修復 (2025-12-18)

## 文檔資訊
- **版本**: 3.0
- **日期**: 2025-12-18
- **前置文檔**: CLAUDE_CODE_HANDOVER-2B.md
- **工作日誌**: WORK_LOG_2025-12-18.md

---

## 本次會話摘要

### 主要任務
修復批量模式 (選單選項 15) 的多個關鍵問題，使其能完整運行掃描、選擇、發送、驗證四個階段。

### 修復的問題
1. ✅ AttributeError: `get_program_info()` 方法不存在
2. ✅ 子課程點擊方法錯誤
3. ✅ 通過條件提取時機錯誤
4. ✅ HTTP 204 被誤判為失敗
5. ℹ️ MitmProxy 連接重置警告（無功能影響）

---

## 批量模式架構 (選單選項 15)

### 功能概述
**混合式時長發送 - 批量模式** 允許用戶一次性掃描所有課程、選擇需要的課程，然後批量發送時長數據。

### 四個階段流程

#### Stage 1A: API 掃描 - 獲取課程 ID
**目的**: 從 API 獲取所有課程的 ID 和名稱

**實現位置**: `menu.py:2285-2343`

**關鍵步驟**:
1. 提取 Selenium Session Cookie
2. 調用 `/api/my-courses` API
3. 解析響應並儲存 `api_courses` 列表

**代碼示例**:
```python
# 提取 Session Cookie
selenium_cookies = driver.get_cookies()
session_cookie = {cookie['name']: cookie['value'] for cookie in selenium_cookies}

# 調用 API
api_url = f"{base_url}/api/my-courses"
response = requests.get(api_url, cookies=session_cookie, ...)
api_courses = data.get('courses', [])
```

**輸出**:
```
[Stage 1A] API 掃描 - 獲取課程 ID
✓ 獲取成功，共 N 門課程
```

---

#### Stage 1B: Web 掃描 - 獲取子課程並捕獲 Payload
**目的**: 通過 Selenium 訪問每個課程，觸發 Payload 捕獲

**實現位置**: `menu.py:2345-2492`

**關鍵步驟**:
1. 前往「我的課程」
2. 獲取修習中的課程列表
3. 對每個課程：
   - 使用 `get_program_courses_and_exams()` 獲取子課程列表
   - **匹配 API Course ID**（關鍵修復點）
   - 提取通過條件（**在點擊子課程之前**）
   - 點擊第一個子課程觸發 Payload 捕獲
   - 返回到課程列表

**API Course ID 匹配邏輯** (`menu.py:2407-2421`):
```python
# 匹配 API 課程 ID（參考混合掃描模式）
api_course_id = None
for api_course in api_courses:
    api_name = api_course.get('name', '')
    if api_name == program_name or api_name in program_name or program_name in api_name:
        api_course_id = api_course.get('id') or api_course.get('course_id')
        print(f'  ✓ 匹配到 API 課程 ID: {api_course_id}')
        break
```

**通過條件提取** (`menu.py:2439-2450`):
```python
# 初始化 CourseDetailPage 並提取通過條件（在點擊子課程之前）
detail_page = CourseDetailPage(driver)
required_minutes = None
try:
    module_id = detail_page.get_first_module_id()
    if module_id:
        requirement = detail_page.extract_pass_requirement(module_id)
        required_minutes = requirement.get('required_minutes')
except Exception as e:
    print(f'  [WARNING] 無法提取通過條件: {e}')

# 點擊子課程（在提取之後）
detail_page.select_lesson_by_name(subcourse_name, delay=2.0)
```

**重要注意事項**:
- ⚠️ 必須在點擊子課程**之前**提取通過條件
- ⚠️ Module 元素只存在於課程詳情頁，不存在於子課程學習頁
- ✅ 使用 `select_lesson_by_name()` 而非不存在的 `click_subcourse_by_name()`

**輸出**:
```
【1/N】課程名稱...
  [1/3] 獲取課程和考試列表...
  → 找到 X 個子課程, Y 個測驗
  [2/3] 匹配 API 課程 ID...
  ✓ 匹配到 API 課程 ID: 465
  [3/3] 訪問子課程觸發 Payload 捕獲...
  → 通過條件: 需觀看 100 分鐘
  ✓ 已捕獲 Payload（課程 ID: 465, 子課程 ID: 901011114）
```

---

#### Stage 2: 互動選單選擇課程
**目的**: 讓用戶選擇要發送時長的課程

**實現位置**: `menu.py:2494-2546`

**功能**:
- 顯示掃描結果（課程 ID、子課程 ID、需要時長）
- 提供指令選擇課程：`1-7`, `all`, `s` (顯示詳情), `c` (確認)

**輸出**:
```
[1] 性別平等工作法...
    └─ ID: 465 | 子課程: 901011114 | 需要: 100 分鐘 | 狀態: ⬜ 未選

請輸入指令 (h 查看幫助): all
✓ 已選擇所有 7 個課程
```

---

#### Stage 3: 批量發送時長
**目的**: 通過 MitmProxy 批量發送修改後的時長

**實現位置**: `menu.py:2548-2665`

**關鍵修復 - HTTP 狀態碼判斷** (`menu.py:2637-2653`):
```python
# 修復前：只接受 HTTP 200
if response.status_code == 200:
    print(f'  ✓ 發送成功（{response.status_code}）')

# 修復後：接受所有 2xx 狀態碼
# HTTP 2xx 都視為成功（包括 200 OK 和 204 No Content）
if 200 <= response.status_code < 300:
    print(f'  ✓ 發送成功（HTTP {response.status_code}）')
```

**HTTP 狀態碼說明**:
- `200 OK`: 成功，有響應內容
- `204 No Content`: 成功，無響應內容（**常見於時長發送**）
- `201 Created`: 成功，資源已創建
- 所有 2xx (200-299) 都表示成功

**輸出**:
```
[Stage 3/4] 批量發送時長

【1/7】性別平等工作法...
  課程 ID: 465
  需要時長: 100 分鐘
  ✓ 發送成功（HTTP 204）

[Stage 3 完成] 已發送 7 個課程
  ✓ 成功: 7
  ✗ 失敗: 0
```

---

#### Stage 4: 驗證時長增加
**目的**: 驗證時長是否成功增加

**實現位置**: `menu.py:2667-2730`

**功能**:
- 返回「我的課程」頁面
- 重新訪問每個課程檢查時長變化

---

## 關鍵技術要點

### 1. API 與 Web 數據整合

**問題**: Web 掃描獲得課程名稱，API 提供課程 ID，如何連接？

**解決方案**: 名稱匹配
```python
for api_course in api_courses:
    api_name = api_course.get('name', '')
    # 三種匹配策略
    if (api_name == program_name or           # 完全匹配
        api_name in program_name or            # API 名稱是 Web 名稱的子集
        program_name in api_name):             # Web 名稱是 API 名稱的子集
        api_course_id = api_course.get('id')
        break
```

**參考實現**: 混合掃描模式 (`menu.py:1068-1074`)

---

### 2. Page Object 時機控制

**問題**: 在哪個頁面狀態提取什麼數據？

**頁面狀態流程**:
```
我的課程 → 課程詳情 → 子課程學習 → 課程詳情 → 我的課程
         ↑           ↑             ↑
         │           │             │
      進入課程    點擊子課程    driver.back()
```

**數據提取時機**:
| 數據類型 | 提取時機 | 原因 |
|---------|---------|------|
| 課程列表 | 我的課程頁 | 使用 `get_in_progress_programs()` |
| 子課程列表 | 課程詳情頁 | 使用 `get_program_courses_and_exams()` |
| Module ID | 課程詳情頁 | 元素只在此頁面存在 |
| 通過條件 | 課程詳情頁 | 需要 Module ID |
| Payload | 子課程學習頁 | 點擊子課程後觸發 API 請求 |

**錯誤示例**:
```python
# ❌ 錯誤：在子課程學習頁提取 Module ID
detail_page.select_lesson_by_name(subcourse_name)  # 現在在子課程學習頁
module_id = detail_page.get_first_module_id()       # 找不到元素！
```

**正確示例**:
```python
# ✅ 正確：在課程詳情頁提取 Module ID
module_id = detail_page.get_first_module_id()       # 在課程詳情頁
detail_page.select_lesson_by_name(subcourse_name)  # 然後進入子課程
```

---

### 3. CourseDetailPage 可用方法

**文件**: `src/pages/course_detail_page.py`

**常用方法**:
```python
# 選擇課程
select_lesson_by_name(lesson_name, delay=7.0)           # 完整名稱
select_lesson_by_partial_name(partial_name, delay=7.0) # 部分名稱

# 提取信息
get_first_module_id() -> str                            # 獲取第一個 Module ID
extract_pass_requirement(module_id) -> dict             # 提取通過條件
extract_current_read_time() -> dict                     # 提取已閱讀時數
get_all_lesson_names() -> list                          # 獲取所有課程名稱

# 導航
go_back_to_course(course_id)                            # 返回課程計畫
go_back_with_text(link_text="返回課程")                 # 使用連結文字返回
click_clickable_area()                                  # 點擊 clickable-area
```

**不存在的方法**:
- ❌ `get_program_info()` - 不存在
- ❌ `click_subcourse_by_name()` - 不存在

---

## 參考實現對比

### 批量模式 vs 混合掃描模式

| 特性 | 批量模式 (選項 15) | 混合掃描模式 (選項 i) |
|-----|-------------------|---------------------|
| API 掃描 | ✅ Stage 1A | ✅ 階段 2 |
| Web 掃描 | ✅ Stage 1B | ✅ 階段 3 |
| 點擊子課程 | ✅ 是（觸發 Payload） | ❌ 否（不觸發） |
| 返回次數 | 2 次（子課程→詳情→列表） | 1 次（詳情→列表） |
| 互動選擇 | ✅ 是（Stage 2） | ❌ 否（自動處理） |
| 發送方式 | 批量 API 請求 | 逐個訪問並發送 |

**導航差異**:
```python
# 批量模式：點擊子課程，需返回兩次
detail_page.select_lesson_by_name(subcourse_name)
driver.back()  # 子課程 → 課程詳情
driver.back()  # 課程詳情 → 我的課程

# 混合掃描模式：不點擊子課程，只返回一次
details = course_list_page.get_program_courses_and_exams(program_name)
driver.back()  # 課程詳情 → 我的課程
```

---

## 常見錯誤與解決方案

### 錯誤 1: AttributeError - 方法不存在

**錯誤訊息**:
```
'CourseDetailPage' object has no attribute 'get_program_info'
```

**原因**: 調用了不存在的方法

**解決方案**:
1. 使用 `Grep` 或 `Read` 工具檢查類定義
2. 參考現有工作代碼（如混合掃描模式）
3. 使用正確的實現方式（API 掃描 + 名稱匹配）

---

### 錯誤 2: NoSuchElementException - 找不到元素

**錯誤訊息**:
```
Unable to locate element: {"method":"xpath","selector":"//div[starts-with(@id, \"module-\")]"}
```

**原因**: 在錯誤的頁面狀態提取數據

**解決方案**:
1. 確認當前頁面狀態
2. 在正確的頁面提取數據
3. 調整操作順序（提取 → 導航）

---

### 錯誤 3: HTTP 狀態碼誤判

**錯誤行為**:
```
✗ 發送失敗（HTTP 204）
```

**原因**: 只將 HTTP 200 視為成功

**解決方案**: 使用範圍判斷
```python
if 200 <= response.status_code < 300:
    # 成功
```

---

## 調試技巧

### 1. 對比參考實現
遇到問題時，找到類似功能的工作代碼：
- 混合掃描模式 (`menu.py:900-1200`)
- i 功能 (`menu.py:250-400`)

### 2. 檢查頁面狀態
使用 `print()` 輸出當前 URL：
```python
print(f"當前 URL: {driver.current_url}")
```

### 3. 驗證方法存在性
```python
# 檢查類的所有方法
print(dir(detail_page))

# 或使用 hasattr
if hasattr(detail_page, 'get_program_info'):
    # 方法存在
```

### 4. 漸進式測試
不要一次修改太多，逐步測試：
1. 先測試 API 掃描
2. 再測試單個課程的 Web 掃描
3. 最後測試完整流程

---

## 代碼質量建議

### 1. 添加清晰註釋
```python
# ✅ 好的註釋：說明為什麼
# 必須在點擊子課程之前提取通過條件，因為 Module 元素只在課程詳情頁存在
module_id = detail_page.get_first_module_id()

# ❌ 差的註釋：只說明做什麼
# 獲取 Module ID
module_id = detail_page.get_first_module_id()
```

### 2. 保持一致性
參考項目現有代碼風格：
- 縮排：4 空格
- 命名：snake_case
- 字符串：單引號
- 註釋：中文

### 3. 錯誤處理
```python
# ✅ 好的錯誤處理：特定異常 + 有意義的訊息
try:
    module_id = detail_page.get_first_module_id()
except NoSuchElementException:
    print('[WARNING] 無法找到 Module 元素，可能不在課程詳情頁')
except Exception as e:
    print(f'[ERROR] 提取 Module ID 失敗: {e}')
```

---

## 下次接手注意事項

### 1. 測試批量模式完整流程
```bash
# 運行批量模式
python menu.py
# 選擇: 15
# 執行完整流程並驗證結果
```

### 2. 確認 HTTP 204 處理正確
檢查 Stage 3 輸出：
```
✓ 發送成功（HTTP 204）  # ✅ 正確
✗ 發送失敗（HTTP 204）  # ❌ 錯誤
```

### 3. 監控 MitmProxy 錯誤
如果 `ConnectionResetError` 影響功能，需要添加異常處理。

### 4. 考慮重構
- 提取 API 掃描為獨立函數
- 提取名稱匹配邏輯為輔助方法
- 統一所有模式的課程 ID 獲取方式

---

## 相關文件清單

### 核心代碼
- `menu.py`: 主菜單，包含所有模式實現
  - Line 2188-2770: 批量模式完整實現
  - Line 990-1166: 混合掃描模式（參考實現）
- `src/pages/course_detail_page.py`: 課程詳情頁面對象
- `src/pages/course_list_page.py`: 課程列表頁面對象
- `src/api/interceptors/payload_capture.py`: Payload 捕獲攔截器

### 文檔
- `docs/WORK_LOG_2025-12-18.md`: 本次工作詳細日誌
- `docs/HYBRID_DURATION_SEND_GUIDE.md`: 混合時長發送指南
- `docs/AI_ASSISTANT_GUIDE-1.md`: AI 助手使用指南

### 測試數據
- `batch_result_*.json`: 批量執行結果
- `quick_complete_result_*.json`: 快速完成執行結果

---

## 快速參考

### 批量模式執行流程
```
1. 選單選擇: 15
2. Stage 1A: API 掃描 (自動)
3. Stage 1B: Web 掃描 (自動)
4. Stage 2: 選擇課程 (互動)
   - 輸入 "all" 選擇全部
   - 輸入 "s" 查看詳情
   - 輸入 "c" 確認
5. Stage 3: 批量發送 (自動)
6. Stage 4: 驗證 (自動)
```

### 關鍵方法速查
```python
# CourseListPage
course_list_page.goto_my_courses()
course_list_page.get_in_progress_programs()
course_list_page.get_program_courses_and_exams(program_name)

# CourseDetailPage
detail_page.get_first_module_id()
detail_page.extract_pass_requirement(module_id)
detail_page.select_lesson_by_name(name, delay=2.0)

# PayloadCaptureInterceptor
payload_interceptor.get_payload_by_course_id(course_id)
```

### API 端點
```
GET  /api/my-courses           # 獲取課程列表
POST /api/user-visits          # 發送時長數據
GET  /api/courses/{id}/activities  # 獲取課程活動
```

---

**文檔結束**

如有問題或需要進一步說明，請參考：
- 工作日誌: `WORK_LOG_2025-12-18.md`
- 前置交接: `CLAUDE_CODE_HANDOVER-2B.md`
- 項目指南: `AI_ASSISTANT_GUIDE-1.md`
