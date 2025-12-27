# ExecutionWrapper 使用指南

**版本**: 1.0.0
**創建日期**: 2025-12-21
**作者**: Claude Code (Sonnet 4.5)

---

## 📋 目錄

1. [簡介](#簡介)
2. [快速開始](#快速開始)
3. [核心概念](#核心概念)
4. [API 參考](#api-參考)
5. [使用範例](#使用範例)
6. [最佳實踐](#最佳實踐)
7. [常見問題](#常見問題)
8. [故障排除](#故障排除)

---

## 簡介

### 什麼是 ExecutionWrapper？

ExecutionWrapper 是一個標準化的執行包裝器，統一管理時間追蹤和截圖功能。它讓 EEBot 的所有功能選項都能一致地記錄執行時間和截取網頁截圖。

### 核心功能

- ✅ **時間追蹤**: 記錄程式、階段、課程、考試的執行時間
- ✅ **自動報告**: 自動生成詳細的時間統計報告（控制台 + Markdown 文件）
- ✅ **截圖管理**: 自動截圖並添加時間戳
- ✅ **統一接口**: 所有功能使用相同的方式記錄時間和截圖
- ✅ **可選配置**: 可選擇啟用或禁用時間追蹤和截圖

### 設計目標

1. **簡單易用**: 一行代碼即可開始使用（with 語句）
2. **輕量級**: 不改變現有功能的內部邏輯
3. **自動化**: 自動管理開始、結束、報告生成
4. **靈活配置**: 支持靈活配置和自定義

---

## 快速開始

### 最簡單的使用方式

```python
from src.utils.execution_wrapper import ExecutionWrapper

# 在任何功能中使用
def my_function(self):
    """我的功能"""

    # 創建執行包裝器
    with ExecutionWrapper(self.config, "我的功能") as wrapper:
        # ... 執行功能代碼 ...
        pass

    # 離開 with 區塊時，自動生成時間報告
```

**就這麼簡單！** ExecutionWrapper 會自動：
1. 記錄程式開始和結束時間
2. 在功能執行完成後生成詳細的時間報告
3. 保存報告到 `reports/我的功能/` 目錄

### 輸出範例

**控制台輸出**:
```
================================================================================
[執行包裝器] 我的功能 - 開始執行
================================================================================

[時間追蹤] 程式開始執行 - 2025-12-21 10:00:00

... [功能執行過程] ...

[時間追蹤] 程式執行結束 - 2025-12-21 10:05:30

================================================================================
[執行包裝器] 我的功能 - 執行結束
================================================================================

========================================================================================
                        📊 時間統計報告 📊
========================================================================================

【程式執行時間】
  開始時間: 2025-12-21 10:00:00
  結束時間: 2025-12-21 10:05:30
  總執行時間: 5m 30s
  總延遲時間: 1m 10s
  使用者等待: 30s
  淨執行時間: 3m 50s

========================================================================================

📄 時間統計報告已保存: reports/我的功能/time_report_20251221_100000.md
```

---

## 核心概念

### 1. 執行包裝器 (ExecutionWrapper)

ExecutionWrapper 是一個上下文管理器（Context Manager），使用 Python 的 `with` 語句自動管理執行的開始和結束。

```python
with ExecutionWrapper(config, "功能名稱") as wrapper:
    # ... 功能代碼 ...
    pass
# 離開 with 區塊時，自動結束並生成報告
```

### 2. 時間追蹤層次

ExecutionWrapper 支持三個層次的時間追蹤：

```
程式 (Program)
├── 階段 (Phase)
│   ├── 階段 1: 初始化
│   ├── 階段 2: 處理課程
│   └── 階段 3: 清理
└── 項目 (Item)
    ├── 課程 1
    ├── 課程 2
    └── 考試 1
```

**程式層級**: 整個功能的執行時間
**階段層級**: 功能內的各個階段（如：初始化、處理、清理）
**項目層級**: 個別課程或考試的處理時間

### 3. 截圖功能

ExecutionWrapper 整合了 ScreenshotManager，可以在關鍵點截取網頁並自動添加時間戳。

```python
wrapper.take_screenshot(driver, "課程名稱", sequence=1)
```

截圖會自動：
- 添加時間戳（右下角，半透明背景）
- 按使用者和日期組織目錄
- 保存到 `screenshots/` 目錄

### 4. 延遲時間記錄

ExecutionWrapper 可以記錄各種延遲時間（如等待頁面載入），並在報告中統計。

```python
wrapper.record_delay(5.0, "等待頁面載入")
```

### 5. 自動報告生成

離開 `with` 區塊時，ExecutionWrapper 自動生成兩種報告：
1. **控制台報告**: 即時查看
2. **Markdown 報告**: 永久保存到 `reports/` 目錄

---

## API 參考

### 初始化

```python
ExecutionWrapper(
    config: ConfigLoader,
    function_name: str,
    enable_tracking: bool = True,
    enable_screenshot: bool = True
)
```

**參數**:
- `config`: ConfigLoader 實例（必需）
- `function_name`: 功能名稱，用於報告文件名（必需）
- `enable_tracking`: 是否啟用時間追蹤（預設 True）
- `enable_screenshot`: 是否啟用截圖（預設 True）

**範例**:
```python
# 啟用所有功能
wrapper = ExecutionWrapper(config, "我的功能")

# 只啟用時間追蹤，禁用截圖
wrapper = ExecutionWrapper(config, "我的功能", enable_screenshot=False)

# 只啟用截圖，禁用時間追蹤
wrapper = ExecutionWrapper(config, "我的功能", enable_tracking=False)

# 禁用所有功能（空包裝器）
wrapper = ExecutionWrapper(config, "我的功能", enable_tracking=False, enable_screenshot=False)
```

---

### 階段管理

#### start_phase(phase_name)

開始一個新階段。

**參數**:
- `phase_name`: 階段名稱（字串）

**範例**:
```python
wrapper.start_phase("初始化")
# ... 初始化代碼 ...
wrapper.end_phase("初始化")
```

#### end_phase(phase_name=None)

結束一個階段。

**參數**:
- `phase_name`: 階段名稱（可選，預設結束當前階段）

**範例**:
```python
# 方式 1: 指定階段名稱
wrapper.start_phase("處理課程")
# ... 處理代碼 ...
wrapper.end_phase("處理課程")

# 方式 2: 自動結束當前階段
wrapper.start_phase("處理課程")
# ... 處理代碼 ...
wrapper.end_phase()  # 自動結束 "處理課程"
```

---

### 項目管理

#### start_item(item_name, program_name='', item_type='course')

開始處理一個項目（課程或考試）。

**參數**:
- `item_name`: 項目名稱（必需）
- `program_name`: 課程計畫名稱（可選）
- `item_type`: 項目類型，'course' 或 'exam'（預設 'course'）

**範例**:
```python
# 處理課程
wrapper.start_item("性別平等工作法-課程1", "性別平等工作法", item_type='course')
# ... 處理課程 ...
wrapper.end_item()

# 處理考試
wrapper.start_item("資通安全測驗", "資通安全測驗(114年度)", item_type='exam')
# ... 處理考試 ...
wrapper.end_item()
```

#### end_item(item_name=None)

結束處理一個項目。

**參數**:
- `item_name`: 項目名稱（可選，預設結束當前項目）

---

### 延遲記錄

#### record_delay(delay_seconds, description='')

記錄延遲時間。

**參數**:
- `delay_seconds`: 延遲秒數（float）
- `description`: 延遲描述（可選）

**範例**:
```python
import time

# 記錄延遲
time.sleep(5.0)
wrapper.record_delay(5.0, "等待頁面載入")

# 記錄不同類型的延遲
wrapper.record_delay(3.0, "等待登入")
wrapper.record_delay(10.0, "等待課程列表")
wrapper.record_delay(2.0, "等待 API 響應")
```

---

### 截圖管理

#### take_screenshot(driver, item_name, sequence=1)

截取網頁並自動添加時間戳。

**參數**:
- `driver`: Selenium WebDriver（必需）
- `item_name`: 項目名稱，用於檔名（必需）
- `sequence`: 序號，用於區分同一項目的多張截圖（預設 1）

**返回值**:
- `str`: 截圖檔案路徑，若未啟用則返回 None

**範例**:
```python
# 第一張截圖
wrapper.take_screenshot(driver, "課程1", sequence=1)

# ... 執行操作 ...

# 第二張截圖
wrapper.take_screenshot(driver, "課程1", sequence=2)
```

**截圖保存位置**:
```
screenshots/
└── {username}/
    └── {date}/
        ├── 課程1_2512211000-1.jpg
        └── 課程1_2512211000-2.jpg
```

---

### 使用者輸入等待

#### start_user_wait(description='等待使用者輸入')

開始記錄使用者輸入等待時間。

**參數**:
- `description`: 等待描述（可選）

#### end_user_wait()

結束記錄使用者輸入等待時間。

**範例**:
```python
wrapper.start_user_wait("等待使用者確認")
user_input = input("請輸入 (y/n): ")
wrapper.end_user_wait()
```

---

### 工具方法

#### is_tracking_enabled()

檢查是否啟用時間追蹤。

**返回值**: `bool`

#### is_screenshot_enabled()

檢查是否啟用截圖。

**返回值**: `bool`

#### get_stats()

取得統計數據。

**返回值**: `Dict` - 按課程計畫分組的統計數據

#### print_status()

打印當前狀態（用於調試）。

**範例**:
```python
wrapper.print_status()

# 輸出:
# [執行包裝器狀態]
#   功能名稱: 我的功能
#   時間追蹤: 啟用
#   截圖功能: 啟用
#   當前階段: 處理課程
#   當前課程: 性別平等工作法 > 課程1
```

---

## 使用範例

### 範例 1: 簡單功能

```python
from src.utils.execution_wrapper import ExecutionWrapper

def simple_function(self):
    """簡單功能 - 基本使用"""

    with ExecutionWrapper(self.config, "簡單功能") as wrapper:
        # 階段 1: 初始化
        wrapper.start_phase("初始化")
        # ... 初始化代碼 ...
        wrapper.end_phase("初始化")

        # 階段 2: 執行
        wrapper.start_phase("執行")
        # ... 執行代碼 ...
        wrapper.end_phase("執行")

        # 階段 3: 清理
        wrapper.start_phase("清理")
        # ... 清理代碼 ...
        wrapper.end_phase("清理")
```

---

### 範例 2: 處理課程列表

```python
def process_courses(self):
    """處理課程列表"""

    with ExecutionWrapper(self.config, "處理課程") as wrapper:
        # 階段 1: 掃描課程
        wrapper.start_phase("掃描課程")
        courses = self.scan_courses()
        wrapper.end_phase("掃描課程")

        # 階段 2: 處理課程
        wrapper.start_phase("處理課程")

        for course in courses:
            # 開始處理課程
            wrapper.start_item(
                course['name'],
                course['program'],
                item_type='course'
            )

            # 處理課程邏輯
            self.select_course(course['name'])

            # 記錄延遲
            import time
            time.sleep(3.0)
            wrapper.record_delay(3.0, "等待課程頁面載入")

            # 執行課程
            self.execute_course(course)

            # 結束處理課程
            wrapper.end_item()

        wrapper.end_phase("處理課程")
```

---

### 範例 3: 課程和考試混合處理

```python
def process_mixed_items(self):
    """處理課程和考試混合列表"""

    with ExecutionWrapper(self.config, "混合處理") as wrapper:
        wrapper.start_phase("處理項目")

        for item in items:
            item_type = item.get('item_type', 'course')
            item_name = item.get('name')
            program_name = item.get('program')

            # 開始處理項目
            wrapper.start_item(item_name, program_name, item_type)

            if item_type == 'exam':
                # 考試處理邏輯
                self.process_exam(item)
                wrapper.record_delay(5.0, "等待考試頁面")
            else:
                # 課程處理邏輯
                self.process_course(item)
                wrapper.record_delay(3.0, "等待課程頁面")

            # 結束處理項目
            wrapper.end_item()

        wrapper.end_phase("處理項目")
```

---

### 範例 4: 帶截圖的處理

```python
def process_with_screenshot(self, driver):
    """帶截圖的處理"""

    with ExecutionWrapper(self.config, "帶截圖處理") as wrapper:
        # 檢查是否啟用截圖
        if wrapper.is_screenshot_enabled():
            print("截圖功能已啟用")

        wrapper.start_phase("處理課程")

        for course in courses:
            wrapper.start_item(course['name'], course['program'])

            # 進入課程頁面
            self.goto_course(course['name'])

            # 第一張截圖（進入時）
            wrapper.take_screenshot(driver, course['name'], sequence=1)

            # 執行課程邏輯
            self.execute_course(course)

            # 第二張截圖（完成時）
            wrapper.take_screenshot(driver, course['name'], sequence=2)

            wrapper.end_item()

        wrapper.end_phase("處理課程")
```

---

### 範例 5: h 功能批量模式整合

```python
def hybrid_scan_batch_mode(self):
    """h 功能選項 2 - 批量模式"""

    with ExecutionWrapper(self.config, "h功能_批量模式") as wrapper:
        # Stage 1: 掃描
        wrapper.start_phase("Stage 1: 掃描")
        scanned_items = self.scan_all_items()
        wrapper.end_phase("Stage 1: 掃描")

        # Stage 2: 選擇
        wrapper.start_phase("Stage 2: 選擇")
        selected_items = self.show_selection_menu(scanned_items)
        wrapper.end_phase("Stage 2: 選擇")

        # Stage 3: 處理
        wrapper.start_phase("Stage 3: 處理")

        for item in selected_items:
            item_type = item.get("item_type", "course")
            item_name = (item.get("exam_name") if item_type == "exam"
                        else item.get("course_name"))
            program_name = item.get("program_name")

            # 開始處理項目
            wrapper.start_item(item_name, program_name, item_type)

            try:
                if item_type == "exam":
                    # 考試處理
                    self.process_exam(item)
                    wrapper.record_delay(5.0, "等待考試頁面載入")
                else:
                    # 課程處理
                    self.process_course(item)
                    wrapper.record_delay(3.0, "發送時長")

                wrapper.end_item()
            except Exception as e:
                print(f"處理失敗: {e}")
                wrapper.end_item()
                continue

        wrapper.end_phase("Stage 3: 處理")

        # Stage 4: 驗證
        wrapper.start_phase("Stage 4: 驗證")
        self.verify_results()
        wrapper.end_phase("Stage 4: 驗證")
```

---

### 範例 6: 使用者輸入等待

```python
def interactive_function(self):
    """互動式功能 - 記錄使用者等待時間"""

    with ExecutionWrapper(self.config, "互動功能") as wrapper:
        wrapper.start_phase("執行")

        # 記錄使用者輸入等待時間
        wrapper.start_user_wait("等待使用者確認")
        confirm = input("確定要執行嗎？(y/n): ")
        wrapper.end_user_wait()

        if confirm.lower() == 'y':
            # ... 執行邏輯 ...
            pass

        wrapper.end_phase("執行")
```

---

### 範例 7: 條件性啟用功能

```python
def conditional_features(self):
    """條件性啟用時間追蹤和截圖"""

    # 根據配置決定是否啟用
    enable_tracking = self.config.get_bool('enable_time_tracking', True)
    enable_screenshot = self.config.get_bool('enable_screenshot', False)

    with ExecutionWrapper(
        self.config,
        "條件功能",
        enable_tracking=enable_tracking,
        enable_screenshot=enable_screenshot
    ) as wrapper:
        # ... 功能代碼 ...

        # 檢查功能是否啟用
        if wrapper.is_tracking_enabled():
            print("時間追蹤已啟用")

        if wrapper.is_screenshot_enabled():
            print("截圖功能已啟用")
```

---

## 最佳實踐

### 1. 使用 with 語句

**✅ 推薦**:
```python
with ExecutionWrapper(config, "功能名稱") as wrapper:
    # ... 功能代碼 ...
    pass
# 自動結束並生成報告
```

**❌ 不推薦**:
```python
wrapper = ExecutionWrapper(config, "功能名稱")
wrapper.__enter__()
# ... 功能代碼 ...
wrapper.__exit__(None, None, None)  # 手動管理，容易出錯
```

### 2. 階段命名清晰

**✅ 推薦**:
```python
wrapper.start_phase("Stage 1: 掃描課程")
wrapper.start_phase("Stage 2: 處理課程")
wrapper.start_phase("Stage 3: 驗證結果")
```

**❌ 不推薦**:
```python
wrapper.start_phase("階段1")
wrapper.start_phase("處理")
wrapper.start_phase("其他")
```

### 3. 記錄有意義的延遲描述

**✅ 推薦**:
```python
wrapper.record_delay(5.0, "等待課程列表頁面載入")
wrapper.record_delay(3.0, "等待 API 響應")
wrapper.record_delay(10.0, "等待考試頁面載入")
```

**❌ 不推薦**:
```python
wrapper.record_delay(5.0)  # 沒有描述
wrapper.record_delay(3.0, "延遲")  # 描述不清楚
```

### 4. 合理使用項目類型

**✅ 推薦**:
```python
# 明確指定項目類型
wrapper.start_item("課程1", "性別平等", item_type='course')
wrapper.start_item("考試1", "資通安全", item_type='exam')
```

**❌ 不推薦**:
```python
# 混淆課程和考試
wrapper.start_item("考試1", "資通安全", item_type='course')  # 錯誤類型
```

### 5. 處理異常

**✅ 推薦**:
```python
with ExecutionWrapper(config, "功能名稱") as wrapper:
    wrapper.start_phase("處理")

    for item in items:
        wrapper.start_item(item['name'])

        try:
            self.process_item(item)
            wrapper.end_item()
        except Exception as e:
            print(f"處理失敗: {e}")
            wrapper.end_item()  # 確保結束項目記錄
            continue

    wrapper.end_phase("處理")
```

### 6. 適時使用 print_status()

在調試時使用 `print_status()` 查看當前狀態：

```python
wrapper.start_phase("處理課程")

for course in courses:
    wrapper.start_item(course['name'])

    # 調試：查看當前狀態
    wrapper.print_status()

    # ... 處理邏輯 ...

    wrapper.end_item()
```

---

## 常見問題

### Q1: ExecutionWrapper 會影響功能性能嗎？

**A**: 影響極小（< 1%）。時間追蹤和截圖操作都是輕量級的，不會顯著影響功能執行速度。

### Q2: 如何禁用時間追蹤或截圖？

**A**: 使用初始化參數：
```python
# 禁用截圖
wrapper = ExecutionWrapper(config, "功能", enable_screenshot=False)

# 禁用時間追蹤
wrapper = ExecutionWrapper(config, "功能", enable_tracking=False)

# 禁用所有功能
wrapper = ExecutionWrapper(config, "功能",
                          enable_tracking=False,
                          enable_screenshot=False)
```

### Q3: 報告保存在哪裡？

**A**:
- **時間報告**: `reports/{功能名稱}/time_report_YYYYMMDD_HHMMSS.md`
- **截圖**: `screenshots/{username}/{date}/item_name_timestamp-sequence.jpg`

### Q4: 可以在功能執行過程中取得統計數據嗎？

**A**: 可以，使用 `get_stats()` 方法：
```python
with ExecutionWrapper(config, "功能") as wrapper:
    # ... 處理邏輯 ...

    # 取得當前統計
    stats = wrapper.get_stats()
    print(f"已處理課程: {len(stats.get('courses', []))}")
```

### Q5: ExecutionWrapper 支持巢狀使用嗎？

**A**: 不建議。每個功能應該使用一個 ExecutionWrapper。如果需要追蹤子功能，使用階段（Phase）或項目（Item）區分即可。

### Q6: 如何自定義報告保存目錄？

**A**: 報告目錄由功能名稱決定，格式為 `reports/{功能名稱}/`。如果需要更複雜的組織結構，可以在功能名稱中使用路徑分隔符：
```python
# 報告會保存到 reports/h功能/批量模式/
wrapper = ExecutionWrapper(config, "h功能/批量模式")
```

### Q7: 截圖失敗會影響功能執行嗎？

**A**: 不會。截圖失敗只會打印警告信息，不會中斷功能執行。

### Q8: 如何訪問底層的 TimeTracker 或 ScreenshotManager？

**A**: 使用 `get_time_tracker()` 和 `get_screenshot_manager()` 方法：
```python
with ExecutionWrapper(config, "功能") as wrapper:
    # 取得底層實例
    time_tracker = wrapper.get_time_tracker()
    screenshot_manager = wrapper.get_screenshot_manager()

    # 使用底層方法（高級用法）
    if time_tracker:
        time_tracker.start_phase("自定義階段")
```

---

## 故障排除

### 問題 1: ExecutionWrapper 初始化失敗

**症狀**:
```
TypeError: __init__() missing 1 required positional argument: 'function_name'
```

**原因**: 缺少必需參數

**解決方案**:
```python
# ❌ 錯誤
wrapper = ExecutionWrapper(config)

# ✅ 正確
wrapper = ExecutionWrapper(config, "功能名稱")
```

---

### 問題 2: 報告生成失敗

**症狀**:
```
[執行包裝器] 生成報告失敗: [Errno 2] No such file or directory: 'reports/...'
```

**原因**: reports 目錄不存在

**解決方案**:
- ExecutionWrapper 會自動創建目錄，如果仍然失敗，檢查磁碟空間和權限
- 手動創建 reports 目錄: `mkdir reports`

---

### 問題 3: 截圖功能不工作

**症狀**: `take_screenshot()` 返回 None

**可能原因**:
1. 截圖功能在配置中被禁用
2. 截圖功能在初始化時被禁用
3. PIL/Pillow 庫未安裝

**解決方案**:
```python
# 檢查截圖是否啟用
if wrapper.is_screenshot_enabled():
    wrapper.take_screenshot(driver, "item_name", 1)
else:
    print("截圖功能未啟用")

# 檢查配置文件 config/timing.json
{
  "screenshot": {
    "enabled": true,  // ← 確保為 true
    ...
  }
}

# 安裝 Pillow
pip install Pillow
```

---

### 問題 4: 時間統計不準確

**症狀**: 報告中的時間統計與預期不符

**可能原因**:
1. 未正確調用 `end_phase()` 或 `end_item()`
2. 延遲時間未記錄

**解決方案**:
```python
# 確保每個 start 都有對應的 end
wrapper.start_phase("階段1")
# ... 代碼 ...
wrapper.end_phase("階段1")  # ← 不要忘記

# 記錄所有 sleep 延遲
import time
time.sleep(5.0)
wrapper.record_delay(5.0, "描述")  # ← 記錄延遲
```

---

### 問題 5: 中文字體顯示問題（截圖）

**症狀**: 截圖中的時間戳顯示為方框或亂碼

**原因**: 系統缺少中文字體

**解決方案**:
```bash
# Windows: 通常已包含微軟雅黑，無需安裝

# Linux: 安裝中文字體
sudo apt-get install fonts-wqy-zenhei
# 或
sudo apt-get install fonts-noto-cjk

# macOS: 通常已包含蘋方，無需安裝
```

---

## 附錄

### A. 配置文件範例

**文件**: `config/timing.json`

```json
{
  "delays": {
    "stage_1_course_list": 3.0,
    "stage_2_program_detail": 11.0,
    "stage_3_lesson_detail": 7.0
  },
  "screenshot": {
    "enabled": true,
    "base_directory": "screenshots",
    "organize_by_user": true,
    "organize_by_date": true,
    "date_format": "%Y-%m-%d",
    "timestamp_format": "%Y-%m-%d %H:%M:%S",
    "filename_timestamp": "%y%m%d%H%M",
    "font_settings": {
      "size": 48,
      "color": "#FFFFFF",
      "background_color": "#000000",
      "background_opacity": 180,
      "margin": 20
    }
  },
  "tracking": {
    "enabled": true,
    "auto_save_report": true,
    "report_base_directory": "reports"
  }
}
```

### B. 完整範例程式

**文件**: `examples/execution_wrapper_example.py`

```python
#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
ExecutionWrapper 完整範例
展示所有功能的使用方式
"""

from src.core.config_loader import ConfigLoader
from src.utils.execution_wrapper import ExecutionWrapper
import time


def example_complete_usage():
    """完整使用範例"""

    # 載入配置
    config = ConfigLoader("config/eebot.cfg")
    config.load()

    # 創建執行包裝器
    with ExecutionWrapper(config, "完整範例") as wrapper:

        # ===== 階段 1: 初始化 =====
        wrapper.start_phase("初始化")
        print("正在初始化...")
        time.sleep(1.0)
        wrapper.record_delay(1.0, "初始化延遲")
        wrapper.end_phase("初始化")

        # ===== 階段 2: 處理項目 =====
        wrapper.start_phase("處理項目")

        # 模擬課程列表
        items = [
            {"name": "課程1", "program": "程式計畫A", "type": "course"},
            {"name": "課程2", "program": "程式計畫A", "type": "course"},
            {"name": "考試1", "program": "程式計畫B", "type": "exam"},
        ]

        for item in items:
            # 開始處理項目
            wrapper.start_item(
                item['name'],
                item['program'],
                item_type=item['type']
            )

            # 模擬處理
            print(f"正在處理 {item['name']}...")
            time.sleep(2.0)
            wrapper.record_delay(2.0, f"處理 {item['name']}")

            # 結束處理項目
            wrapper.end_item()

        wrapper.end_phase("處理項目")

        # ===== 階段 3: 清理 =====
        wrapper.start_phase("清理")
        print("正在清理...")
        time.sleep(0.5)
        wrapper.record_delay(0.5, "清理延遲")
        wrapper.end_phase("清理")

        # 打印狀態
        wrapper.print_status()

    # 離開 with 區塊，自動生成報告
    print("\n範例執行完成！")
    print("請查看 reports/完整範例/ 目錄中的時間報告")


if __name__ == "__main__":
    example_complete_usage()
```

### C. 相關文檔

- **研究報告**: `docs/STANDARDIZATION_TIME_SCREENSHOT_RESEARCH.md`
- **TimeTracker 源碼**: `src/utils/time_tracker.py`
- **ScreenshotManager 源碼**: `src/utils/screenshot_utils.py`
- **ExecutionWrapper 源碼**: `src/utils/execution_wrapper.py`

---

**使用指南完成** | 2025-12-21

**版本**: 1.0.0

**下一步**: 開始使用 ExecutionWrapper 整合到您的功能中！
