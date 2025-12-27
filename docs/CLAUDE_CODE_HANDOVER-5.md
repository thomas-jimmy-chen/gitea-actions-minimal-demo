# AI 助手交接文檔 #5

**專案**: EEBot v2.3.8 (代號: AliCorn 天角獸)
**交接日期**: 2025-12-26
**前次交接**: `docs/CLAUDE_CODE_HANDOVER-4.md`
**本次工作**: Stage 6 Proxy 修復 + 考試截圖優化 + 選單重組 + 技術文檔
**執行者**: Claude Code (Opus 4.5)

---

## 🎯 快速概覽（30 秒理解本次工作）

### 主要成果
1. **修復 h 選項 2 Stage 6 考試攔截器不工作的問題**
2. **修正考試截圖流程** - Before/After 現在都在同一頁面
3. **重組主選單** - 邏輯分組、簡潔風格
4. **撰寫技術架構文檔** - 確保日後開發不會有不當更改
5. **專案命名規範化** - 產品名 EEBot + 代號 AliCorn

### 核心技術修復
Stage 5 使用 `use_proxy=False` 建立瀏覽器，Stage 6 需要重啟瀏覽器使用 `use_proxy=True` 才能讓流量經過 MitmProxy。

### 關鍵檔案
- `menu.py` (Lines 2312-2347 Stage 6 Proxy 修復, 2405-2500 截圖流程)
- `src/api/interceptors/exam_auto_answer.py` (日誌清理)
- `src/pages/exam_answer_page.py` (新增 `submit_exam_directly()`)
- `docs/TECHNICAL_ARCHITECTURE_REPORT.md` (新建 - 完整技術架構報告)

---

## 📋 專案狀態

### 版本信息
- **當前版本**: v2.3.8
- **專案名稱**: EEBot
- **代號**: AliCorn (天角獸)
- **Python**: 3.13
- **關鍵依賴**: Selenium, MitmProxy, OpenAI API

### 重要文檔
- **技術架構**: `docs/TECHNICAL_ARCHITECTURE_REPORT.md` (日後開發必讀)
- **工作日誌**: `docs/WORK_LOG_2025-12-26.md`
- **待辦事項**: `docs/TODO.md`

### 功能狀態
| 功能 | 狀態 | 備註 |
|------|------|------|
| i 功能 (一鍵執行) | ✅ 穩定 | 全自動模式 |
| h 選項 1 (快速查看) | ✅ 穩定 | Pure API |
| h 選項 2 (批量模式) | ✅ 已修復 | 課程+考試混合 |
| h 選項 3 (考試模式) | ✅ 穩定 | 獨立考試處理 |
| w 功能 (學習統計) | ✅ 穩定 | < 3 秒查詢 |
| 主選單 | ✅ 已重組 | 邏輯分組 |

---

## 🔧 本次工作詳細記錄

### 問題 1: Stage 6 MitmProxy 攔截器不工作

**現象**:
- Stage 2 有 `[ExamAutoAnswer][ALL]` 日誌（enable=False）
- Stage 6 完全沒有日誌（enable=True 但沒攔截到）

**根本原因**:
```python
# Stage 5 建立瀏覽器時使用 use_proxy=False
driver = driver_manager.create_driver(use_proxy=False)

# Stage 6 繼續使用這個瀏覽器，流量不經過 MitmProxy
```

**解決方案** (`menu.py` Lines 2312-2347):
```python
# Stage 6 開始時重啟瀏覽器
print('\n[6.1] 重啟瀏覽器（啟用 proxy 模式）...')
try:
    driver.quit()
except Exception:
    pass
driver = driver_manager.create_driver(use_proxy=True)
print('  ✓ 已啟動新瀏覽器（使用 proxy 127.0.0.1:8080）')

# 重新登入
login_page = LoginPage(driver)
login_page.navigate_and_login()
```

---

### 問題 2: 考試截圖在錯誤的頁面

**原問題**:
- Before 截圖：點擊考試名稱**之後**（錯誤）
- After 截圖：可能在不同頁面

**用戶需求**:
Before 和 After 都應該在 `/learning-activity/full-screen#/exam/xx` 頁面

**解決方案** (`menu.py` Lines 2405-2500):

1. **新流程**:
```
[1/5] 點擊考試名稱
[2/5] 進入考試頁面（繼續答題 → 勾選 → 確認）
      → 等待 URL 包含 'learning-activity/full-screen#/exam/'
[3/5] Before 截圖（考試全螢幕頁面）
[4/5] 自動提交考卷
[5/5] After 截圖（同一頁面）
```

2. **滾動等待函數**:
```python
def scroll_to_bottom_and_wait(driver, max_attempts=5):
    last_height = driver.execute_script("return document.body.scrollHeight")
    for attempt in range(max_attempts):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            time.sleep(1.0)
            break
        last_height = new_height
```

3. **URL 驗證**:
```python
max_wait = 15
for wait_sec in range(max_wait):
    time.sleep(1)
    if 'learning-activity/full-screen#/exam/' in driver.current_url:
        print(f'✓ 已進入考試頁面: {driver.current_url[:70]}...')
        break
else:
    print(f'⚠️ URL 未變更: {driver.current_url[:70]}...')
```

---

### 問題 3: 主選單重組

**用戶需求**:
- 預製排程 (1-13, v, c, s, r) → 114年郵政E大學學員個人課程
- 智能掃描 (i, h)
- 快速查詢 (w, t)
- 簡潔風格

**新選單結構** (`menu.py` Lines 79-112):
```
======================================================================
  EEBot 課程排程管理系統
======================================================================

[智能掃描] 自動偵測修習中課程
  i - 一鍵自動執行 (掃描 + 執行)
  h - 混合掃描 (API + Web 混合模式)

[快速查詢] 無需瀏覽器
  w - 學習統計查詢 (< 3 秒)
  t - 測試 API (研究用)

[預製排程] 114年郵政E大學學員個人課程
  1-13 - 選擇課程加入排程
  v - 查看排程 | c - 清除 | s - 儲存 | r - 執行

  課程列表:
    1. 課程名稱 - 內容
    ...

  q - 離開
======================================================================
```

---

### 問題 4: 新增專案代號 AliCorn

**修改的檔案**:
| 檔案 | 位置 |
|------|------|
| `menu.py` | Line 5, 82, 4910 |
| `main.py` | Line 5, 34 |
| `README.md` | Line 1 |
| `src/__init__.py` | Line 2 |
| `CHANGELOG-A.md` | Line 10 |
| `docs/changelogs/CHANGELOG_archive_2025.md` | Line 1 |
| `docs/LEARNING_STATS_INTEGRATION_SUMMARY.md` | Line 25 |

---

## 📊 技術架構圖

### h 功能選項 2（批量模式）完整流程

```
┌─────────────────────────────────────────────────────────────────┐
│                h 選項 2 - 批量模式 (已修復)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Stage 1: API 掃描                                              │
│  ├── GET /api/my-courses                                       │
│  ├── GET /api/courses/{id}/activities                          │
│  └── 輸出: scanned_courses + scanned_exams                     │
│                                                                 │
│  Stage 2: 選擇菜單                                              │
│  ├── 顯示課程 (📚) 和考試 (📝)                                   │
│  └── 用戶選擇要處理的項目                                       │
│                                                                 │
│  Stage 3: Web 驗證 (PayloadCaptureInterceptor)                 │
│  ├── 啟動 MitmProxy (use_proxy=True)                           │
│  ├── 捕獲 POST user-visits payload                             │
│  └── 關閉 MitmProxy                                            │
│                                                                 │
│  Stage 4: API 發送                                              │
│  ├── 直接 POST /api/.../user-visits                            │
│  └── 使用 captured payload                                     │
│                                                                 │
│  Stage 5: 一般課程處理                                          │
│  ├── 重啟瀏覽器 (use_proxy=False) ← 這是關鍵                    │
│  ├── Web 自動化執行課程                                         │
│  └── 時間追蹤: start_item/end_item                             │
│                                                                 │
│  Stage 6: 考試處理 ⭐ 已修復                                     │
│  ├── 重啟瀏覽器 (use_proxy=True) ← 修復點                       │
│  ├── ExamAutoAnswerInterceptor.enable = True                   │
│  ├── 進入考試頁面                                               │
│  ├── URL 驗證 (/learning-activity/full-screen#/exam/)          │
│  ├── Before 截圖                                                │
│  ├── 自動答題 (interceptor 注入)                                │
│  ├── 提交考卷                                                   │
│  ├── After 截圖                                                 │
│  └── 時間追蹤: start_item/end_item                             │
│                                                                 │
│  Stage 7: 結果報告                                              │
│  └── ExecutionWrapper.print_summary()                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### ExamAutoAnswerInterceptor 工作流程

```
┌─────────────────────────────────────────────────────────────────┐
│              ExamAutoAnswerInterceptor                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Response 攔截 (GET /api/exams/{id}/distribute)                │
│  ├── 解析 JSON 響應                                             │
│  ├── 提取題目 (subjects)                                        │
│  ├── 匹配題庫 (QuestionBankService)                            │
│  ├── 存儲結果到 exam_data_store                                 │
│  └── 輸出: "匹配完成: 10/10 題"                                  │
│                                                                 │
│  Request 攔截 (POST /api/exams/{id}/submissions)               │
│  ├── 讀取 exam_data_store                                       │
│  ├── 修改 payload.subjects[].answer_option_ids                 │
│  ├── 更新 payload.progress                                      │
│  └── 輸出: "已注入 10 題答案"                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔍 關鍵程式碼位置

### menu.py

| 功能 | 行號 | 說明 |
|------|------|------|
| 主選單顯示 | 79-112 | 新的分組選單 |
| Stage 6 Proxy 修復 | 2312-2347 | 重啟瀏覽器 |
| 滾動等待函數 | 2405-2425 | `scroll_to_bottom_and_wait()` |
| URL 驗證 | 2443-2454 | 等待進入考試頁面 |
| Before 截圖 | 2456-2463 | 步驟 3/5 |
| After 截圖 | 2485-2500 | 步驟 5/5 |

### src/api/interceptors/exam_auto_answer.py

| 功能 | 行號 | 說明 |
|------|------|------|
| Response 攔截 | 56-71 | distribute API |
| Request 攔截 | 73-88 | submissions API |
| 題目匹配 | 208-274 | `_match_questions()` |
| 答案注入 | 276-314 | `_inject_answers()` |

### src/pages/exam_answer_page.py

| 功能 | 行號 | 說明 |
|------|------|------|
| 直接提交 | 333-360 | `submit_exam_directly()` |

---

## ⏳ 待完成事項

| 項目 | 優先級 | 狀態 | 說明 |
|------|--------|------|------|
| 測試 Stage 6 截圖 | P1 | 待驗證 | 確認 Before/After URL 一致 |
| 測試批量模式 | P1 | 待驗證 | 課程+考試混合處理 |
| 更新版本號 | P2 | 待處理 | v2.3.7 → v2.3.8 |
| PEP8 清理 | P3 | 長期 | 逐步遷移 |

---

## 📚 文檔索引

### 技術文檔
- **專案架構**: `docs/PROJECT_ARCHITECTURE_REPORT_2025-12-18.md`
- **AI 指南**: `docs/AI_ASSISTANT_GUIDE-1.md`
- **h 功能分析**: `docs/H_FUNCTION_WORKFLOW_ANALYSIS.md`
- **ExecutionWrapper**: `docs/EXECUTION_WRAPPER_GUIDE.md`

### 工作記錄
- **本次工作**: `docs/WORK_LOG_2025-12-26.md`
- **前次工作**: `docs/WORK_LOG_2025-12-21.md`

### 交接文檔
- **本文檔**: `docs/CLAUDE_CODE_HANDOVER-5.md`
- **前次交接**: `docs/CLAUDE_CODE_HANDOVER-4.md`
- **歷史交接**: `docs/CLAUDE_CODE_HANDOVER-3.md`, `-2.md`, `-1.md`

---

## 🤖 AI 助手快速入門

### 如果你是新接手的 AI 助手，請按以下順序閱讀：

1. **本文檔** - 了解最新狀態
2. `docs/AI_ASSISTANT_GUIDE-1.md` - 專案概覽和架構
3. `docs/PROJECT_ARCHITECTURE_REPORT_2025-12-18.md` - 詳細架構
4. `menu.py` - 主程式入口（約 5000 行）

### 常見任務

| 任務 | 關鍵檔案 | 說明 |
|------|----------|------|
| 修改選單 | `menu.py` L79-112 | `display_menu()` |
| 修改 h 功能 | `menu.py` L1800+ | `handle_h_function()` |
| 修改攔截器 | `src/api/interceptors/` | MitmProxy addons |
| 修改頁面操作 | `src/pages/` | Selenium POM |

---

**文檔版本**: 1.0
**建立日期**: 2025-12-26
**維護者**: Claude Code (Opus 4.5)
