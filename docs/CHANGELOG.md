# 修改日誌 (Changelog)

本文件記錄 EEBot 專案的所有重要修改。

---

## [2025-01-13] - 新增考試流程支持

### 📝 更新摘要
新增考試類型課程的自動化支持，與現有的課程學習流程並行運作。考試流程包含額外的確認步驟（勾選同意條款、彈窗確認等）。

### 🐛 修復記錄 (2025-01-13 晚間)

#### 修復 #1: 考試頁面"繼續答題"按鈕無法定位

**問題描述**:
- 考試流程在第2步（點擊考試頁面的"繼續答題"按鈕）時失敗
- 錯誤：`Element not found` - XPath 定位器過於嚴格

**修復方案**:
- 修改 `exam_detail_page.py` 中的 `click_continue_exam_button()` 方法
- 實現多重定位策略（Fallback Mechanism）：
  1. 策略1: 根據文本內容定位（`contains(., '繼續答題')`）
  2. 策略2: 根據 ng-click 部分匹配（`contains(@ng-click, 'openStartExamConfirmationPopup')`）
  3. 策略3: 根據 span 文字定位，再回溯到父元素
  4. 策略4: 使用 exam-button-container 容器定位
- 如果一個策略失敗，自動嘗試下一個策略

**檔案修改**:
- `src/pages/exam_detail_page.py` - 更新 `click_continue_exam_button()` 方法（第73-115行）

---

#### 修復 #2: 彈窗內"繼續答題"按鈕無法點擊

**問題描述**:
- 考試流程在第4步（點擊彈窗內的"繼續答題"按鈕）時失敗
- 錯誤：`Element not clickable` - 按鈕可能處於 disabled 狀態或被遮擋
- 即使 checkbox 已勾選，AngularJS 需要時間更新按鈕狀態

**修復方案**:
- 修改 `exam_detail_page.py` 中的 `click_popup_continue_button()` 方法
- 實現5種定位策略（按優先順序）：
  1. 策略1: 精確路徑（使用者提供的 XPath）`//*[@id='start-exam-confirmation-popup']/div/div/div[3]/div/button[1]`
  2. 策略2: 彈窗 ID + 第一個綠色按鈕
  3. 策略3: 部分匹配 class 和 ng-click
  4. 策略4: 根據按鈕文本內容定位
  5. 策略5: popup-footer 容器內的第一個綠色按鈕
- 增加按鈕 disabled 狀態檢查：
  - 檢測按鈕是否 disabled
  - 如果是，等待最多 5 秒讓 AngularJS 更新狀態
  - 使用 JavaScript 點擊（繞過元素遮擋檢查）
- 所有策略都使用 `execute_script` 點擊，避免 Selenium 的點擊檢查

**檔案修改**:
- `src/pages/exam_detail_page.py` - 完全重寫 `click_popup_continue_button()` 方法（第142-200行）

**技術細節**:
```python
# 檢查並等待按鈕啟用
is_disabled = element.get_attribute('disabled')
if is_disabled:
    for _ in range(10):  # 最多等 5 秒
        time.sleep(0.5)
        is_disabled = element.get_attribute('disabled')
        if not is_disabled:
            break

# 使用 JavaScript 點擊
self.driver.execute_script("arguments[0].click();", element)
```

**用戶貢獻**:
- 感謝用戶提供精確的 XPath 路徑，大幅提升定位成功率

### ✨ 新增功能

#### 1. 新增考試頁面操作類
- **文件**: `src/pages/exam_detail_page.py`
- **功能**:
  - `click_exam_by_name()` - 根據考試名稱點擊考試
  - `click_exam_by_xpath()` - 使用 XPath 點擊考試（備用方法）
  - `click_continue_exam_button()` - 點擊"繼續答題"按鈕
  - `check_agreement_checkbox()` - 勾選"我已詳閱考試要求並承諾遵守考試紀律"
  - `click_popup_continue_button()` - 點擊彈窗內的確認按鈕
  - `complete_exam_flow()` - 一鍵完成整個考試流程（便捷方法）
  - `is_on_exam_page()` - 檢查是否在考試頁面
  - `wait_for_exam_page_load()` - 等待考試頁面載入
- **繼承自**: `BasePage`
- **設計模式**: Page Object Model (POM)

#### 2. 新增考試流程場景類
- **文件**: `src/scenarios/exam_learning.py`
- **功能**:
  - `execute()` - 執行考試列表
  - `_process_exam()` - 處理單一考試
  - `execute_single_exam()` - 執行單一考試（便捷方法）
  - `_wait_for_manual_close()` - 錯誤時等待手動關閉（調試用）
- **參考自**: `CourseLearningScenario`
- **工作流程**:
  1. 自動登入
  2. 前往我的課程
  3. 選擇課程計畫
  4. 點擊考試名稱
  5. 點擊"繼續答題"按鈕
  6. 勾選同意條款
  7. 點擊彈窗內的確認按鈕
  8. 返回課程列表

#### 3. 新增考試配置
- **文件**: `data/courses.json`
- **新增項目**:
  ```json
  {
    "program_name": "高齡客戶投保權益保障(114年度)",
    "exam_name": "高齡測驗(100分及格)",
    "course_type": "exam",
    "delay": 10.0,
    "description": "高齡客戶投保權益保障考試流程 (新增於 2025-01-13)"
  }
  ```
- **新欄位說明**:
  - `exam_name`: 考試名稱（與 `lesson_name` 對應，用於考試類型）
  - `course_type`: 類型標記（`"exam"` 或 `"course"`，預設為 `"course"`）
  - `delay`: 延遲時間設為 10.0 秒（考試流程較複雜，需要更長等待時間）

### 🔧 修改的文件

#### 1. menu.py - 課程排程管理介面
- **修改方法**:
  - `display_menu()` - 新增考試類型的顯示標記 `[考試]`
  - `display_schedule()` - 排程列表區分顯示課程和考試
  - `add_course_to_schedule()` - 添加課程時顯示正確的類型標記
- **向下兼容**: 完全兼容現有課程配置（無 `course_type` 欄位時預設為 `"course"`）
- **視覺改進**: 考試項目會顯示 `[考試]` 標籤，便於識別

#### 2. main.py - 程式入口
- **新增導入**: `from src.scenarios.exam_learning import ExamLearningScenario`
- **新增邏輯**:
  - Step 5: 分離課程和考試（根據 `course_type` 欄位）
  - Step 6.1: 執行一般課程（使用 `CourseLearningScenario`）
  - Step 6.2: 執行考試（使用 `ExamLearningScenario`）
- **執行策略**: 混合排程時會先執行所有一般課程，再執行所有考試

### 📁 新增的文件

```
src/
├── pages/
│   └── exam_detail_page.py      (新增) - 考試頁面操作
└── scenarios/
    └── exam_learning.py          (新增) - 考試流程場景

docs/
├── CHANGELOG.md                  (新增) - 本文件
├── CLAUDE_CODE_HANDOVER.md       (新增) - Claude Code CLI 專用文檔
└── AI_ASSISTANT_GUIDE.md         (新增) - 通用 AI 助手交接文檔
```

### 🚫 未修改的文件（保持原樣）

以下文件**完全未被修改**，確保向下兼容：

```
✅ src/scenarios/course_learning.py     - 原有課程流程
✅ src/pages/course_list_page.py        - 課程列表頁面
✅ src/pages/course_detail_page.py      - 課程詳情頁面
✅ src/pages/login_page.py              - 登入頁面
✅ src/pages/base_page.py               - 頁面基類
✅ src/core/*                           - 所有核心模組
✅ src/api/*                            - 所有 API 模組
✅ config/eebot.cfg                     - 配置檔案
✅ data/courses.json (原有課程項目)     - 現有課程配置
```

### 🔍 技術細節

#### Selenium 定位策略
- **考試名稱**: `By.LINK_TEXT` 或 `By.XPATH` (使用 `ng-click='changeActivity(activity)'`)
- **繼續答題按鈕**: `By.XPATH` 定位 `class='button button-green take-exam'`
- **同意條款 Checkbox**: `By.XPATH` 定位 `ng-model='ui.confirmationCheck'`
- **彈窗確認按鈕**: `By.XPATH` 定位 `ng-click='takeExam(exam.referrer_type)'`

#### MitmProxy 機制
- 考試流程**完全沿用**現有的 MitmProxy 配置
- 訪問時長修改機制保持不變
- 代理啟動/停止邏輯保持不變

#### 延遲時間配置
- 一般課程: 7.0 秒（保持不變）
- 考試流程: 10.0 秒（考試頁面載入較慢，需要更長等待）

### 📊 影響範圍

| 類別 | 新增 | 修改 | 刪除 | 總計 |
|------|-----|------|------|------|
| Python 文件 | 2 | 2 | 0 | 4 |
| 配置文件 | 1 項目 | 0 | 0 | 1 |
| 文檔文件 | 3 | 0 | 0 | 3 |
| **總計** | **6** | **2** | **0** | **8** |

### ✅ 測試建議

#### 單獨測試考試流程
```bash
# 1. 使用 menu.py 選擇考試
python menu.py
# 選擇考試項目（例如：高齡測驗）
# 輸入 's' 儲存排程

# 2. 執行排程
python main.py
```

#### 混合測試（課程 + 考試）
```bash
# 1. 在 menu.py 中同時選擇課程和考試
python menu.py
# 選擇多個課程和考試
# 輸入 's' 儲存排程

# 2. 執行排程（會先執行課程，再執行考試）
python main.py
```

### 🐛 已知限制

1. **考試和課程不能交叉執行**: 當排程包含課程和考試時，會先執行完所有課程，再執行所有考試（這是設計決策，避免頻繁切換 scenario 造成的瀏覽器重啟）

2. **考試成績不會自動提交**: 目前的實現只到達考卷區，不會自動答題或提交成績

3. **單一瀏覽器會話**: 每種類型（課程/考試）會使用獨立的瀏覽器會話

### 💡 未來改進方向

- [ ] 支援自動答題（讀取題庫檔案）
- [ ] 支援成績查詢與記錄
- [ ] 優化混合執行（考試和課程交叉執行）
- [ ] 新增重試機制（考試失敗時自動重試）
- [ ] 新增進度保存（中斷後可續傳）

---

## 📊 今日完成總結 (2025-01-13)

### ✅ 已完成項目

| 項目 | 狀態 | 說明 |
|------|------|------|
| 考試流程功能 | ✅ 完成 | 新增完整的考試自動化支持 |
| 考試頁面操作類 | ✅ 完成 | `exam_detail_page.py` |
| 考試流程場景類 | ✅ 完成 | `exam_learning.py` |
| 課程配置更新 | ✅ 完成 | 新增高齡客戶考試配置 |
| 菜單支持考試 | ✅ 完成 | `menu.py` 和 `main.py` |
| 按鈕定位修復 #1 | ✅ 完成 | 考試頁面"繼續答題"按鈕 |
| 按鈕定位修復 #2 | ✅ 完成 | 彈窗內"繼續答題"按鈕 |
| 完整文檔 | ✅ 完成 | CHANGELOG, AI_GUIDE, CLAUDE_GUIDE |

### 📈 代碼統計

- **新增文件**: 5 個（2 Python + 3 文檔）
- **修改文件**: 3 個（menu.py, main.py, exam_detail_page.py）
- **新增代碼行數**: ~800 行（含文檔）
- **修復問題**: 2 個關鍵 bug

### 🎯 測試狀態

- ✅ 考試流程：4 步驟全部可執行
- ✅ 多重策略：考試頁面 4 策略，彈窗 5 策略
- ✅ 錯誤處理：自動重試備用定位方法
- ✅ 向下兼容：原有課程完全不受影響

### 🔄 下次改進建議

1. 收集更多考試類型的 HTML 樣本
2. 考慮增加自動答題功能（讀取題庫）
3. 添加考試成績自動記錄
4. 優化延遲時間（可能減少到 8 秒）

---

## 版本歷史

### v2.0.1+exam.2 (2025-01-13 晚間)
- 修復考試流程中的按鈕定位問題
- 實現多重定位策略和自動重試
- 增加 disabled 狀態檢查和等待機制

### v2.0.1+exam.1 (2025-01-13)
- 新增考試類型課程支持
- 新增 exam_detail_page.py 和 exam_learning.py
- 完整的項目文檔和交接文件

### v2.0.1 (2025-11-10)
- 初始版本（wizard03 重構）
- 採用 POM + API 模組化架構

### v2.0.0
- 原始版本（Guy Fawkes）

---

**維護者**: wizard03
**最後更新**: 2025-01-13 (晚間修復完成)
**文檔版本**: 1.2
**項目狀態**: ✅ 可用於生產環境
