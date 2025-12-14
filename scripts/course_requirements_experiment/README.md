# 課程通過條件提取實驗

**創建日期**: 2025-12-05
**目的**: 驗證獲取課程通過條件（觀看時長、測驗成績）的可行方案

---

## 📋 實驗目標

1. **探索課程詳細 API** - 是否有 API 端點返回通過條件
2. **驗證 XPath 提取** - 從頁面提取通過條件的可靠性
3. **資料格式分析** - 通過條件的文字格式是否一致
4. **方案選擇** - 決定採用 API 還是 Selenium 提取

---

## 🎯 通過條件說明

### 位置

**所在頁面**: 課程計畫詳情頁（非課程列表頁）

**存取流程**:
1. 前往 `/my-courses` - 課程列表頁
2. 點擊課程計畫名稱 - 進入課程計畫詳情頁
3. 在詳情頁上，每個課程單元（module）上方顯示通過條件

**XPath**: `//*[@id="module-{module_id}"]/div[1]/div[1]/span`

**範例**:
- `module-485` - 課程單元 ID 為 485
- `module-465` - 課程單元 ID 為 465

### 格式

**可能的文字格式**:
1. "觀看時長90分鐘 測驗成績達80分" （兩個條件）
2. "觀看時長60分鐘" （僅時長）
3. "測驗成績達70分" （僅測驗）
4. 可能為空（無條件）

---

## 🧪 實驗腳本

### 1. test_course_details_api.py

**功能**: 探索課程詳細 API 端點

**測試端點**:
- `GET /api/courses/{id}`
- `GET /api/courses/{id}/details`
- `GET /api/courses/{id}/modules`
- `GET /api/courses/{id}/requirements`
- `GET /api/my-courses/{id}`

**預期結果**:
- 如果找到 → 返回 JSON 包含通過條件
- 如果沒有 → 返回 404 或無相關欄位

### 2. test_pass_requirements_extraction.py

**功能**: 測試從頁面提取通過條件

**測試內容**:
- 登入並前往課程列表頁
- 從 API 獲取課程計畫列表
- 逐個進入課程計畫詳情頁
- 提取每個課程單元（module）的通過條件
- 分析文字格式
- 驗證提取成功率

**測試流程**:
1. 登入 → 前往 `/my-courses`
2. 調用 API 獲取課程計畫列表
3. 對每個課程計畫：
   - 點擊進入課程計畫詳情頁
   - 找到所有 `module-*` 元素
   - 提取通過條件 (XPath: `//*[@id="module-{id}"]/div[1]/div[1]/span`)
   - 返回課程列表頁

**預期結果**:
- 提取成功的課程單元數量
- 文字格式統計
- 異常情況記錄

---

## 🚀 執行方式

### 前提

```bash
cd D:\Dev\eebot
conda activate eebot
```

### Step 1: 探索 API

```bash
python scripts\course_requirements_experiment\test_course_details_api.py
```

### Step 2: 測試 XPath 提取

```bash
python scripts\course_requirements_experiment\test_pass_requirements_extraction.py
```

---

## 📊 預期產出

**結果目錄**: `scripts/course_requirements_experiment/results/`

**報告檔案**:
1. `api_exploration_report.md` - API 探索結果
2. `extraction_test_report.md` - XPath 提取測試結果
3. `final_recommendation.md` - 最終方案建議

---

## ⏱️ 預計時間

- API 探索：30 分鐘
- XPath 提取測試：30 分鐘
- 資料分析：30 分鐘
- **總計**：1.5 小時

---

**實驗完成後，將決定採用哪種方案進行正式實作。**
