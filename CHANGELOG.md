# Eebot 更新日誌

## [2.0.1] - 2025-11-10

### 作者
- wizard03

### 新增功能
- **互動式選單系統 (menu.py)**
  - 新增課程選擇選單，可以按數字選擇課程
  - 支援查看當前排程 (v 指令)
  - 支援清除排程 (c 指令)
  - 支援儲存排程 (s 指令)
  - 支援直接執行排程 (r 指令)
  - 支援重複選擇同一課程
  - 離開前提示儲存未保存的排程

- **排程管理系統**
  - 新增 `data/schedule.json` 排程檔案
  - 課程現在以排程方式執行，而非一次執行全部
  - 使用者可自行安排要執行的課程順序和數量

### 修改功能
- **main.py**
  - 改為讀取 `data/schedule.json` 而非 `data/courses.json`
  - 排程為空時會提示使用者先執行 `menu.py` 建立排程
  - 排程檔案不存在時會提示使用者先建立排程

- **課程執行邏輯 (src/scenarios/course_learning.py)**
  - 移除執行完成後的手動關閉等待（不再需要按 Ctrl+C）
  - 新增最後一個課程完成後的 10 秒倒數計時
  - 倒數結束後自動關閉瀏覽器和 mitmproxy
  - 改善清理流程的日誌輸出

- **頁面操作優化**
  - **src/pages/course_list_page.py**
    - 移除 `select_course_by_name` 的下拉功能
    - 移除 `select_course_by_partial_name` 的下拉功能
  - **src/pages/course_detail_page.py**
    - 移除 `select_lesson_by_name` 的下拉功能
    - 移除 `select_lesson_by_partial_name` 的下拉功能
  - 提升執行速度，減少不必要的頁面滾動

### 使用方式變更
**舊版本 (v2.0.0):**
```bash
python main.py  # 執行所有課程
```

**新版本 (v2.0.1):**
```bash
# 步驟 1: 設定排程
python menu.py
# 選擇課程 → 按 's' 儲存 → 按 'q' 離開

# 步驟 2: 執行排程
python main.py
```

### 技術改進
- Windows 命令行編碼處理（menu.py）
- 改善錯誤處理和使用者提示
- 優化課程執行流程
- 移除不必要的頁面滾動操作

### 檔案變更清單
- **新增檔案:**
  - `menu.py` - 互動式選單管理系統
  - `data/schedule.json` - 課程排程檔案
  - `CHANGELOG.md` - 本更新日誌

- **修改檔案:**
  - `main.py` - 排程讀取邏輯
  - `src/scenarios/course_learning.py` - 執行流程優化
  - `src/pages/course_list_page.py` - 移除下拉功能
  - `src/pages/course_detail_page.py` - 移除下拉功能

### 向後相容性
- `data/courses.json` 保持不變，作為課程資料庫
- 所有原有功能維持正常運作
- 配置檔 `config/eebot.cfg` 無需修改

---

## [2.0.0] - 2025-01-01

### 作者
- Guy Fawkes

### 初始版本
- 採用 POM (Page Object Model) + API 模組化設計
- 實作自動化課程學習功能
- 支援 Cookie 管理
- 支援 mitmproxy 訪問時長修改
- 支援多課程批次執行
