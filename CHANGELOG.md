# Eebot 更新日誌

---
**專案代號**: Gleipnir (格萊普尼爾)
北歐神話中用來綑綁魔狼芬里爾的鎖鏈，意為「糾纏者」或「欺詐者」，亦稱「縛狼鎖」。
象徵此專案如同神話中的鎖鏈，精準地「綑綁」並自動化繁瑣的學習流程。

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
