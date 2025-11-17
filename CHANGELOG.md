# Eebot 更新日誌

---
**專案代號**: Gleipnir (格萊普尼爾)
北歐神話中用來綑綁魔狼芬里爾的鎖鏈，意為「糾纏者」或「欺詐者」，亦稱「縛狼鎖」。
象徵此專案如同神話中的鎖鏈，精準地「綑綁」並自動化繁瑣的學習流程。

---

> 📁 **歷史版本**: 舊版本更新日誌已移至 [docs/changelogs/CHANGELOG_archive_2025.md](docs/changelogs/CHANGELOG_archive_2025.md)

---

## [2.0.5] - 2025-11-17

### 作者
- wizard03 (with Claude Code CLI - Sonnet 4.5)

### 🎯 本次更新重點：穩定性與配置優化

#### 1. 登入重試機制強化
**問題**: 智能推薦功能 ('i' 選項) 在驗證碼輸入錯誤時無法重試，程式仍繼續執行導致後續操作失敗。

**解決方案**:
- 實現最多 3 次登入重試機制
- 每次失敗後自動刷新頁面獲取新驗證碼
- 3 次失敗後優雅終止流程並提示使用者

**修改檔案**:
- `menu.py` (lines 263-294) - 智能推薦功能登入流程
- `src/scenarios/course_learning.py` (lines 78-103) - 課程學習場景登入流程
- `src/scenarios/exam_learning.py` (lines 82-107) - 考試學習場景登入流程

**技術細節**:
```python
max_retries = 3
for attempt in range(max_retries):
    login_success = self.login_page.auto_login(...)
    if login_success:
        break
    else:
        if attempt < max_retries - 1:
            # 刷新頁面獲取新驗證碼
            login_page.goto(config.get('target_http'))
        else:
            # 終止流程
            raise Exception('Login failed after maximum retries')
```

#### 2. 排程去重機制（雙層保護）
**問題**: 智能推薦掃描課程時，最後一個主題會重複加入排程。

**解決方案**:
實現雙層去重保護機制：

**第一層 - 掃描階段去重** (`src/pages/course_list_page.py`, lines 271-305):
- 使用 `set()` 追蹤已掃描的課程/考試名稱
- 防止 DOM 重複元素導致的重複掃描
- O(1) 時間複雜度的高效查找

**第二層 - 加入排程階段去重** (`menu.py`, lines 446-485):
- 檢查現有排程避免重複加入
- 考試與課程使用不同的比對邏輯：
  - **考試**: 比對 `program_name` + `exam_name` + `course_type`
  - **課程**: 比對 `program_name` + `lesson_name` + `course_id`
- 跳過重複項目並顯示統計信息

**修改檔案**:
- `src/pages/course_list_page.py` - 掃描階段去重
- `menu.py` - 加入排程階段去重

#### 3. MitmProxy 配置外部化（統一配置管理）
**問題**: `visit_duration_increase` 值 (9000) 在多處 hardcode，難以維護且容易不一致。

**解決方案**:
採用「單一數據源 (Single Source of Truth)」設計模式：

**配置流程**:
1. `config/eebot.cfg` (line 19) - 定義配置參數
2. `main.py` (line 65) - 統一讀取配置（唯一的 default 值位置）
3. `main.py` (lines 137, 153) - 作為參數傳遞給 scenario
4. `course_learning.py` / `exam_learning.py` - 接收並使用配置值

**架構優勢**:
- ✅ **單一數據源**: default 值 9000 只在 `main.py` 一處
- ✅ **依賴注入**: 配置從外部注入，scenario 不需知道 default 值
- ✅ **易於維護**: 修改配置只需改 `eebot.cfg`，修改 default 值只需改 `main.py`
- ✅ **解耦設計**: scenario 類別與配置邏輯分離

**新增配置參數** (`config/eebot.cfg`):
```ini
# 訪問時長修改設定 (Visit Duration Modification)
# visit_duration_increase: 增加的訪問時長（秒），預設為 9000 秒 (150 分鐘)
visit_duration_increase = 9000
```

**修改檔案**:
- `config/eebot.cfg` - 新增配置參數
- `main.py` - 統一讀取配置並傳遞
- `src/scenarios/course_learning.py` - 接收配置參數
- `src/scenarios/exam_learning.py` - 接收配置參數

#### 4. 蟲洞功能顯示位置優化
**問題**: 蟲洞（時間加速）信息在課程開始時顯示，使用者無法在關鍵階段感知時間加速效果。

**解決方案**:
將蟲洞信息移至三個關鍵階段轉換點顯示：

**顯示位置**:
1. **第二階 - 進入時**: 截圖 1/2 之後（選擇課程計畫後）
2. **第三階 - 進入時**: 選擇課程單元之後
3. **第二階 - 返回時**: 返回課程計畫之後

**顯示格式**:
```
⏰ 蟲洞: 已開啟，時間推至 150 分鐘
```

**修改檔案**:
- `src/scenarios/course_learning.py` (lines 180-184, 210-213, 219-222, 234-237)

**使用者體驗提升**:
- 在關鍵等待階段提醒使用者蟲洞功能已生效
- 透明化顯示時間加速效果（9000 秒 = 150 分鐘）
- 提高使用者對系統運作的信心

---

### 📊 統計數據
- **修改檔案數**: 7 個
- **新增配置參數**: 1 個
- **新增功能**: 4 個（登入重試、雙層去重、配置外部化、蟲洞顯示優化）
- **代碼行數變更**: 約 +150 行（含註解與文檔）

---

### 🔧 技術債務清理
- 移除多處 hardcoded default 值
- 統一配置管理模式
- 改善代碼可維護性

---

### 📝 文檔更新
- 更新 `CHANGELOG.md`
- 新增 `docs/DAILY_WORK_LOG_20251117.md`
- 更新 `docs/CLAUDE_CODE_HANDOVER.md`

---

## [2.0.4] - 2025-01-17

### 作者
- wizard03 (with Claude Code CLI - Sonnet 4.5)

### 🎯 重大新增功能：完整時間統計系統

#### 核心功能
- **全方位時間追蹤**
  - 程式總執行時間（開始 → 結束）
  - 各階段執行時間（初始化、登入、課程執行、考試執行、清理）
  - 每個課程的執行時間（包含課程計畫分組）
  - 每個考試的執行時間（包含課程計畫分組）
  - 延遲時間統計（頁面載入等待時間）
  - 使用者輸入等待時間（手動操作等待）

- **智能時間分類**
  - 總時間 = 淨執行時間 + 延遲時間 + 使用者等待時間
  - 延遲時間：頁面載入、sleep 等待
  - 使用者等待：input() 等待手動操作
  - 淨執行時間：實際程式運行時間

- **階層化統計**
  - 程式總時間
  - 階段時間（6 個階段）
  - 課程計畫統計（大章節分組）
    - 課程明細（小章節）
    - 考試明細（小章節）

- **雙重輸出**
  - 螢幕輸出：彩色格式化的終端報告
  - 文檔輸出：Markdown 格式報告自動保存到 `reports/` 目錄

#### 新增檔案

**時間追蹤工具**
- `src/utils/time_tracker.py` - 完整的時間追蹤器類別（596 行）
  - TimeTracker 類別
  - 時間記錄方法（start/end）
  - 統計計算方法
  - 螢幕報告輸出
  - Markdown 文件輸出

#### 修改檔案

- **main.py**
  - 導入 TimeTracker
  - 創建並啟動追蹤器
  - 在 7 個階段記錄時間
  - 將追蹤器傳遞給 scenario
  - 程式結束時輸出完整報告並保存到文件

- **src/scenarios/course_learning.py**
  - 構造函數接受 `time_tracker` 參數
  - 記錄每個課程的開始/結束時間
  - 記錄 4 個階段的延遲時間：
    - 課程計畫頁面載入等待（Stage 2）
    - 課程單元頁面載入等待（Stage 3）
    - 返回課程計畫等待（Stage 2）
    - 返回課程列表等待（Stage 1）
  - 自動計算課程淨執行時間

- **src/scenarios/exam_learning.py**
  - 構造函數接受 `time_tracker` 參數
  - 記錄每個考試的開始/結束時間
  - 記錄延遲時間（課程計畫載入、考試流程、返回列表）
  - 記錄使用者手動操作等待時間（手動完成考試時）
  - 自動計算考試淨執行時間

#### 技術特性

**時間記錄方法**
```python
tracker.start_program()                          # 程式開始
tracker.start_phase('階段名稱')                   # 開始階段
tracker.end_phase('階段名稱')                     # 結束階段
tracker.start_course('課程名', '課程計畫名')      # 開始課程
tracker.end_course()                             # 結束課程
tracker.start_exam('考試名', '課程計畫名')        # 開始考試
tracker.end_exam()                               # 結束考試
tracker.record_delay(秒數, '描述')               # 記錄延遲
tracker.start_user_wait('描述')                  # 開始等待用戶輸入
tracker.end_user_wait()                          # 結束等待用戶輸入
tracker.print_report()                           # 輸出報告
```

**報告輸出格式**
- 螢幕輸出：格式化的中文表格報告
- 文檔輸出：Markdown 格式，包含：
  - 程式執行時間總表
  - 階段執行時間表
  - 課程計畫統計（分組）
  - 課程明細表
  - 考試明細表
  - 使用者輸入等待統計
  - 總結與時間佔比分析

**文件命名規則**
```
reports/time_report_YYYYMMDD_HHMMSS.md
例如：reports/time_report_20250117_153000.md
```

#### 使用方式

**自動啟用**
時間追蹤功能已自動整合，執行程式時自動記錄：
```bash
python main.py
```

**報告查看**
1. 螢幕報告：程式結束時自動顯示
2. 文檔報告：自動保存到 `reports/` 目錄
   - 可用任何 Markdown 閱讀器查看
   - 包含完整的時間統計數據

#### 統計範例

```
【程式執行時間】
  開始時間: 2025-01-17 15:30:00
  結束時間: 2025-01-17 15:45:30
  總執行時間: 15m 30s
  總延遲時間: 5m 20s
  使用者等待: 2m 10s
  淨執行時間: 8m 0s

【課程計畫統計】（大章節）
  📚 資通安全教育訓練(114年度)
     項目數: 3 (課程: 2, 考試: 1)
     總時間: 10m 30s (執行: 7m 10s + 延遲: 3m 20s)

     📖 課程明細:
        • 資通安全基礎課程    8m 0s (執行: 5m 40s + 延遲: 2m 20s)
        • 個資保護與管理      2m 30s (執行: 1m 30s + 延遲: 1m 0s)

     📝 考試明細:
        • 資通安全測驗        2m 30s (執行: 1m 20s + 延遲: 1m 10s)
```

#### 向後相容性

- ✅ 所有原有功能完全保留
- ✅ 時間追蹤為可選功能（透過參數控制）
- ✅ 無報告文件時優雅降級
- ✅ 不影響程式執行效能

#### 優勢與應用

- **透明化**: 程式每個階段的時間都被精確記錄
- **易於分析**: 自動生成格式化報告，一目了然
- **持久化記錄**: Markdown 文件可長期保存和查閱
- **效能優化參考**: 延遲時間佔比幫助識別優化空間
- **用戶體驗追蹤**: 記錄使用者等待時間，優化互動流程
- **執行效率分析**: 了解課程/考試的實際執行時間

---

### 🎨 產品化輸出訊息優化（補充）

#### 核心改進
- **使用者友善**: 將技術性檔案名稱改為通用描述
- **一致性**: 統一術語使用

#### 修改內容

**檔案刪除輸出優化**
- `main.py` - 檔案刪除顯示優化
- `menu.py` - 檔案刪除顯示優化（2 處）

**輸出效果對比**:

修改前：
```
✓ 已刪除: stealth.min.js
✓ 已刪除: resource/plugins/stealth.min.js
✓ Removed: stealth.min.js
```

修改後：
```
✓ 已刪除: stealth mode file
✓ 已刪除: resource/plugins/stealth mode file
✓ Removed: stealth mode file
```

**修改方式**：
使用字串替換策略處理動態檔案路徑顯示：
```python
display_name = file_path.replace('stealth.min.js', 'stealth mode file')
print(f'  ✓ 已刪除: {display_name}')
```

#### 修改統計
- 修改檔案數: 3 個
- 修改行數: 9 行（純輸出語句）
- 邏輯變更: 0 個
- 向後相容性: 100%

---

## [2.0.2+auto-answer.1] - 2025-11-15 晚間

### 作者
- wizard03 (with Claude Code CLI - Gleipnir Project)

### 🐛 重大 Bug 修復：題庫懶載入導致匹配失敗

#### 問題描述
執行多個自動答題考試時，第二個及後續考試出現 0% 匹配率。

#### 問題根源
**檔案**: `src/scenarios/exam_learning.py:261`
**原始程式碼**:
```python
if self.question_bank is None:  # ❌ 懶載入邏輯錯誤
    self.question_bank = QuestionBankService(self.config)
    question_count = self.question_bank.load_question_bank(exam.get('program_name'))
```

**問題機制**:
1. 同一個 `ExamLearningScenario` 實例處理多個考試（main.py:128-130）
2. 第一個考試載入題庫 A（例如：高齡投保 10 題）
3. `self.question_bank` 不再是 `None`
4. 第二個考試跳過題庫載入邏輯
5. 使用錯誤的題庫 A 匹配題庫 B 的題目
6. 結果：0% 匹配率

#### 調查過程

**Phase 1: 驗證題庫檔案**
- ✅ 確認題庫檔案 `銀行業金融友善服務（21題）.json` 存在且包含正確題目
- ✅ 手動比對 unmatched.zip 中的題目與題庫，3/3 題目完全匹配

**Phase 2: 獨立測試**
- 建立 `debug_question_bank.py` 測試腳本
- ✅ 題庫載入：成功載入 21 題
- ✅ 匹配測試：Q1, Q2, Q3 全部達到 100% 匹配成功
- 結論：題庫服務和匹配引擎本身正常運作

**Phase 3: 程式碼審查**
- 追蹤 `ExamLearningScenario` 的生命週期
- 發現 main.py 使用單一實例處理所有考試
- 識別懶載入邏輯導致題庫無法更新

#### 修復方案

**修改檔案**: `src/scenarios/exam_learning.py:260-276`

**修復後程式碼**:
```python
# 1. 為每個考試載入對應的題庫
# 修復：每次都重新載入，避免不同考試使用錯誤的題庫
print('  📚 正在載入題庫...')

# 創建新的題庫服務實例
self.question_bank = QuestionBankService(self.config)

# 載入題庫（根據 program_name 或使用總題庫）
program_name = exam.get('program_name')
question_count = self.question_bank.load_question_bank(program_name)

if question_count > 0:
    print(f'  ✅ 題庫已載入（共 {question_count} 題）')
    print(f'  📋 課程名稱: {program_name}')
else:
    print(f'  ❌ 題庫載入失敗')
    return
```

**關鍵改變**:
1. ✅ 移除 `if self.question_bank is None:` 條件判斷
2. ✅ 每個考試都創建新的 `QuestionBankService` 實例
3. ✅ 每個考試都載入對應的題庫（根據 program_name）
4. ✅ 新增 program_name 日誌輸出，方便追蹤除錯

#### 影響範圍
- **修復前**: 單次執行多個自動答題考試時，只有第一個考試能正常匹配
- **修復後**: 每個考試都使用正確的題庫，匹配率應達 ~100%

#### 經驗教訓與防範措施

**⚠️ 重要教訓**:
1. **懶載入陷阱**: 當物件被多次調用時，懶載入可能導致狀態污染
2. **實例共享風險**: 同一實例處理不同資料時，必須重置相關狀態
3. **測試盲點**: 單一考試測試無法發現多考試場景的問題

**🛡️ 防範原則**:
```python
# ❌ 危險模式：共享狀態 + 懶載入
if self.shared_resource is None:
    self.shared_resource = load_resource(identifier_A)
# 第二次調用時，identifier_B 會錯誤使用 resource_A

# ✅ 安全模式：每次重新載入
self.shared_resource = load_resource(current_identifier)
# 每次都確保使用正確的資源
```

**📋 Code Review 檢查清單**:
- [ ] 是否有懶載入邏輯？
- [ ] 該物件是否會被多次調用處理不同資料？
- [ ] 是否需要根據參數載入不同資源？
- [ ] 是否有測試多次調用的場景？

#### 測試建議
執行包含多個自動答題考試的流程，應看到每個考試都正確載入對應題庫：
```
[6.2] Executing exams...
--- Processing Exam 1/2 ---
  📚 正在載入題庫...
  ✅ 題庫已載入（共 10 題）
  📋 課程名稱: 高齡客戶投保權益保障(114年度)

--- Processing Exam 2/2 ---
  📚 正在載入題庫...
  ✅ 題庫已載入（共 21 題）
  📋 課程名稱: 金融服務業公平待客原則＆洗錢防制及打擊資恐教育訓練(114年度)
```

---

## [2.0.2+auto-answer] - 2025-11-15

### 作者
- wizard03 (with Claude Code CLI - Gleipnir Project)

### 🎯 重大新增功能：自動答題系統 (Phase 2)

#### 核心功能
- **自動偵測考題**
  - 自動偵測考試總題數
  - 自動識別題型（單選題/複選題）
  - 自動提取題目與選項文字

- **智能答案匹配**
  - 多層級匹配演算法（精確匹配 → 包含匹配 → 相似度匹配）
  - 信心門檻機制（預設 85%，可調整）
  - HTML 標籤清理與文字標準化
  - 全形/半形標點符號轉換

- **題庫管理**
  - 支援總題庫模式（1766 題）
  - 支援分類題庫模式（根據課程自動選擇）
  - 題庫檔案對應表（program_name → 題庫檔案）

- **自動作答**
  - 單選題自動點擊
  - 複選題自動點擊
  - 答題進度即時顯示
  - 答題統計摘要

- **錯誤處理**
  - 無法匹配題目時自動截圖
  - 記錄未匹配題目資訊到文字檔
  - 可選擇跳過或停止作答

- **交卷流程**
  - 使用者確認機制
  - 自動交卷選項（可關閉）
  - 考試結果顯示

#### 新增檔案

**資料模型層 (Models)**
- `src/models/__init__.py` - 模型套件初始化
- `src/models/question.py` - Question 和 Option 資料類別

**服務層 (Services)**
- `src/services/__init__.py` - 服務套件初始化
- `src/services/question_bank.py` - 題庫載入與查詢服務
- `src/services/answer_matcher.py` - 答案匹配引擎

**頁面物件層 (Pages)**
- `src/pages/exam_answer_page.py` - 考卷區答題頁面操作

**場景層 (Scenarios)**
- `src/scenarios/exam_auto_answer.py` - 自動答題場景編排

#### 修改檔案

- **config/eebot.cfg**
  - 新增 `[AUTO_ANSWER]` 配置區塊
  - `enable_auto_answer` - 啟用/停用自動答題
  - `question_bank_mode` - 題庫模式（total_bank / file_mapping）
  - `question_bank_path` - 題庫檔案路徑
  - `answer_confidence_threshold` - 匹配信心門檻（0.85）
  - `auto_submit_exam` - 自動交卷開關
  - `screenshot_on_mismatch` - 無法匹配時截圖
  - `skip_unmatched_questions` - 跳過無法匹配的題目
  - `screenshot_dir` - 截圖儲存目錄

- **main.py**
  - 匯入 `ExamAutoAnswerScenario`
  - 根據 `enable_auto_answer` 配置選擇考試場景
  - 自動答題模式 vs 手動模式切換邏輯

#### 技術特性

**匹配演算法**
```python
策略 1: 精確匹配（100% 信心）
策略 2: 包含匹配（95% 信心）
策略 3: 相似度匹配（使用 SequenceMatcher）
```

**文字標準化處理**
- 移除 HTML 標籤（使用 BeautifulSoup）
- 移除所有空白字元
- 全形標點符號轉半形
- 轉小寫（英文字母）

**驗證機制**
- 選項數量驗證（允許 ±1 差異）
- 題型一致性檢查
- 正確答案數量檢查
- 索引範圍驗證

#### 使用方式

**啟用自動答題**
```ini
# config/eebot.cfg
enable_auto_answer = y
```

**執行流程**
```bash
# 1. 設定排程（選擇考試）
python menu.py

# 2. 執行自動答題
python main.py
```

**執行過程**
1. 載入題庫（1766 題）
2. 進入考試 → 處理確認流程
3. 偵測題目與題型
4. 逐題匹配並自動作答
5. 顯示答題統計
6. 使用者確認交卷
7. 顯示考試結果

#### 統計資訊

系統會顯示：
- 總題數
- 匹配成功題數
- 無法匹配題數
- 已作答題數
- 匹配成功率
- 作答率

#### 截圖功能

當題目無法匹配時：
- 自動截圖儲存（`screenshots/unmatched/`）
- 記錄題號、時間、題目文字到 `.txt` 檔案
- 方便後續手動檢查

#### 依賴套件

新增依賴：
- `beautifulsoup4` - HTML 解析
- `difflib` - 字串相似度比較（Python 內建）

#### 配置範例

```ini
[AUTO_ANSWER]
enable_auto_answer = y
question_bank_mode = total_bank
question_bank_path = 郵政E大學114年題庫/總題庫.json
answer_confidence_threshold = 0.85
auto_submit_exam = n
screenshot_on_mismatch = y
skip_unmatched_questions = y
screenshot_dir = screenshots/unmatched
```

#### 向後相容性

- ✅ 原有課程學習功能完全保留
- ✅ 原有考試流程（手動模式）保留
- ✅ 可透過配置檔切換自動/手動模式
- ✅ 所有原有檔案保持不變

#### 已知限制

- 匹配準確度取決於題庫資料品質
- 題目或選項文字差異過大時可能無法匹配
- 需要手動確認交卷（預設安全機制）

#### 未來改進方向

- 支援 SQLite 題庫（提升查詢效能）
- 機器學習相似度模型
- 答題歷史記錄
- 錯題本功能

---

### 🚀 重大更新：智能模式 (Smart Mode) - 2025-11-15

#### 核心變更：從全局啟用改為按課程啟用

**原邏輯**：所有考試統一由 `enable_auto_answer` 全局配置控制

**新邏輯**：每個考試獨立配置，只有標記 `enable_auto_answer: true` 的考試才會自動答題

#### 修改內容

**1. 資料結構變更 (data/courses.json)**
- 新增 `enable_auto_answer` 欄位到每個考試項目
- 範例：
  ```json
  {
    "program_name": "高齡客戶投保權益保障(114年度)",
    "exam_name": "高齡測驗(100分及格)",
    "course_type": "exam",
    "enable_auto_answer": true,  // 新增欄位
    "delay": 10.0,
    "description": "高齡客戶投保權益保障考試流程 - 啟用自動答題"
  }
  ```

**2. 場景邏輯優化 (src/scenarios/exam_learning.py)**
- **新增功能**：
  - `_is_in_exam_answer_page()` - 偵測是否進入考卷區頁面
  - `_auto_answer_current_exam()` - 執行自動答題流程
  - 懶加載機制：題庫和匹配器僅在需要時初始化

- **核心流程變更**：
  ```python
  # 檢查該考試是否啟用自動答題
  enable_auto_answer = exam.get('enable_auto_answer', False)

  if enable_auto_answer and self._is_in_exam_answer_page():
      print('【自動答題模式啟動】')
      self._auto_answer_current_exam(exam)
  else:
      print('請手動完成考試')
      input('完成後按 Enter 繼續...')
  ```

**3. 主程式簡化 (main.py)**
- 移除 `ExamAutoAnswerScenario` 匯入
- 所有考試統一使用 `ExamLearningScenario`
- 場景內部自動判斷是否啟用自動答題

**4. 配置調整 (config/eebot.cfg)**
- `question_bank_mode` 改為 `file_mapping`（根據課程自動選擇題庫）
- `enable_auto_answer` 配置保留但不再作為全局開關使用

#### 重要 Bug 修復

**Bug #1: UTF-8 BOM 編碼問題**
- **問題**：`Unexpected UTF-8 BOM (decode using utf-8-sig)`
- **解決**：所有 JSON 檔案讀取改用 `utf-8-sig` 編碼
- **影響檔案**：
  - `src/services/question_bank.py` (2 處)
  - `main.py` (1 處)
  - `menu.py` (3 處)

**Bug #2: 分頁結構解析**
- **問題**：特定題庫檔案使用 `[{"subjects": [...]}]` 結構，但程式預期直接陣列
- **解決**：`_load_specific_bank()` 新增分頁結構偵測與處理
- **結果**：題庫載入從 1 題修正為正確的 10 題

**Bug #3: 方法名稱不一致**
- **問題**：`get_all_questions()` 等方法不存在於 `ExamAnswerPage`
- **解決**：統一方法命名：
  - `get_all_questions()` → `detect_questions()`
  - `get_question_text()` → `extract_question_text()`
  - `get_options()` → `extract_options()`
  - `submit_exam()` → `submit_exam_with_confirmation()`

**Bug #4: 回傳型別處理**
- **問題**：`find_best_match()` 回傳 tuple 而非 dict
- **解決**：正確的 tuple 解包
  ```python
  match_result = self.answer_matcher.find_best_match(question_text, questions)
  if match_result is None:
      # 處理無匹配
  else:
      db_question, confidence = match_result  # 正確解包
  ```

**Bug #5: 元素互動問題**
- **問題**：`element not interactable` - 交卷按鈕無法點擊
- **解決**：
  - 使用精確的 XPath 定位器
  - 改用 JavaScript 點擊
  - 增加等待時間 (3 秒)
- **更新定位器**：
  ```python
  SUBMIT_BUTTON = (By.XPATH, "/html/body/div[3]/div[4]/div[3]/div[9]/div/div/div[3]/div/div[3]/a")
  CONFIRM_BUTTON = (By.XPATH, "//*[@id='submit-exam-confirmation-popup']/div/div[3]/div/button[1]")
  ```

**Bug #6: QuestionBankService 初始化參數錯誤**
- **問題**：使用錯誤的參數 `mode=...`, `total_bank_path=...`
- **解決**：正確的初始化方式
  ```python
  self.question_bank = QuestionBankService(self.config)
  question_count = self.question_bank.load_question_bank(exam.get('program_name'))
  ```

#### 測試驗證結果

**測試課程**：高齡客戶投保權益保障(114年度) - 高齡測驗
- ✅ 題庫載入：10 題
- ✅ 匹配成功率：100% (10/10)
- ✅ 匹配信心度：95-100%
- ✅ 自動作答：成功
- ✅ 自動交卷：成功

#### 技術優化

**懶加載機制**
- 題庫和匹配器僅在 `enable_auto_answer=true` 時載入
- 節省記憶體，提升效能

**程式碼整合**
- 統一考試場景，減少重複程式碼
- 維持原有 `ExamLearningScenario` 手動模式相容性

**錯誤處理強化**
- 更詳細的日誌輸出
- 匹配失敗時的截圖功能保留

#### 使用方式

**啟用特定考試的自動答題**：
1. 編輯 `data/courses.json`
2. 為需要自動答題的考試加入 `"enable_auto_answer": true`
3. 使用 `menu.py` 選擇該考試加入排程
4. 執行 `python main.py`

**範例**：
```bash
# 1. 配置課程（在 courses.json 設定 enable_auto_answer）
# 2. 選擇課程
python menu.py
# 選擇 [10] 高齡客戶投保權益保障考試

# 3. 執行（自動偵測並啟動答題）
python main.py
```

#### 向後相容性

- ✅ 未設定 `enable_auto_answer` 的考試預設為 `false`（手動模式）
- ✅ 原有手動考試流程完全保留
- ✅ 所有課程學習功能不受影響
- ✅ 配置檔 `enable_auto_answer` 保留但作用改變

#### 技術債務清理

- 移除未使用的 `ExamAutoAnswerScenario` 相關程式碼
- 統一編碼策略（utf-8-sig 為主，utf-8 為備用）
- 統一方法命名規範

---
