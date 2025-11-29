# EEBot - Claude Code CLI 交接文檔 (第 2 段)

> **分段資訊**: 本文檔共 2 段
> - 📄 **當前**: 第 2 段 - 進階功能詳解
> - ⬅️ **上一段**: [CLAUDE_CODE_HANDOVER-1.md](./CLAUDE_CODE_HANDOVER-1.md) - 基礎架構與使用指南
> - 📑 **完整索引**: [返回索引](./CLAUDE_CODE_HANDOVER.md)

---

## 📖 本段內容

- [已完成功能：自動答題系統](#已完成功能自動答題系統-phase-2)
- [智能模式：按課程啟用自動答題](#智能模式按課程啟用自動答題-2025-11-15-更新)
- [GUI 開發計畫](#gui-開發計畫-2025-11-24-規劃)
- [延伸閱讀](#延伸閱讀)

---

## 🎯 已完成功能：自動答題系統 (Phase 2)

> **狀態**: ✅ **已實作完成** (2025-11-15)
> **版本**: 2.0.2+auto-answer
> **實作者**: wizard03 (with Claude Code CLI)
> **目前進度**: 完整的自動答題系統，含智能匹配引擎

### 功能概述

自動答題系統將透過比對考試頁面題目與題庫答案，實現自動答題功能。

### 題庫資料

**位置**: `郵政E大學114年題庫/`

**統計資料**:
- 總題數：**1,766 題**
- 總大小：**5.3 MB**
- 分類數：**23 個主題**
- 格式：**JSON 檔案**

**範例分類**:
```
窗口線上測驗（390題）
郵務窗口(114年度)（188題）
法令遵循／防制洗錢（262題）
資通安全（30題）
高齡投保（10題）
... 共 23 個分類
```

---

### 考試頁面元素分析

#### 題目元素
```html
<li class="subject">
    <span class="subject-description">題目內容</span>
</li>
```

**定位方式**: `.subject-description` 或 `//span[@class='subject-description']`

#### 選項元素

**單選題 (Radio)**:
```html
<input type="radio" ng-model="subject.answeredOption" />
<div class="option-content"><span>選項內容</span></div>
```

**複選題 (Checkbox)**:
```html
<input type="checkbox" ng-model="option.checked" />
<div class="option-content"><span>選項內容</span></div>
```

**定位方式**: `.option-content`, `input[type="radio"]`, `input[type="checkbox"]`

#### 交卷按鈕
```html
<a class="button button-green" ng-click="calUnsavedSubjects()">交卷</a>
<button ng-click="submitAnswer(...)">確定</button>
```

**重要**: 考試採用**整頁顯示**模式（所有題目在同一頁），非分頁模式。

---

### 資料庫方案評估

#### 推薦方案：混合模式 (SQLite + JSON)

| 方案 | 適用性 | 速度 | 部署難度 | 推薦度 |
|------|-------|------|---------|--------|
| **SQLite** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ (零配置) | **✅ 強烈推薦** |
| JSON | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ (現成) | ✅ 適合 MVP |
| MySQL | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ (需安裝) | ❌ 殺雞用牛刀 |

**為何選擇 SQLite？**
- ✅ 零配置（Python 內建 `sqlite3`）
- ✅ 檔案式（單一 `.db` 檔案）
- ✅ 查詢速度快（毫秒級）
- ✅ 支援全文檢索（FTS5）
- ✅ 適合 5.3MB 資料量

**分階段策略**:
```
階段 1 (MVP)：直接使用現有 JSON 檔案
階段 2 (優化)：首次啟動自動建立 SQLite
階段 3 (正式)：使用 SQLite，保留 JSON 作備份
```

---

### 新增檔案架構（符合 POM 模式）

```
eebot/
├── src/
│   ├── pages/
│   │   ├── exam_detail_page.py        # 現有（勿改）
│   │   └── exam_answer_page.py        # 【新增】答題頁面
│   │
│   ├── scenarios/
│   │   ├── exam_learning.py           # 現有（勿改）
│   │   └── exam_auto_answer.py        # 【新增】自動答題場景
│   │
│   ├── services/                      # 【新增】業務邏輯層
│   │   ├── question_bank.py           # 題庫查詢服務
│   │   └── answer_matcher.py          # 答案匹配引擎
│   │
│   └── models/                        # 【新增】資料模型
│       └── question.py                # 題目/選項資料類別
│
├── data/
│   ├── courses.json                   # 現有
│   └── questions.db                   # 【新增】SQLite 資料庫
│
└── 郵政E大學114年題庫/
    └── *.json                         # 現有（保留作備份）
```

---

### 核心模組設計

#### ExamAnswerPage（答題頁面物件）
```python
class ExamAnswerPage(BasePage):
    def get_all_questions()              # 取得所有題目元素
    def get_question_text(question_elem) # 取得題目文字
    def get_options(question_elem)       # 取得題目選項
    def get_option_text(option_elem)     # 取得選項文字
    def click_option(option_elem)        # 點擊選項
    def submit_exam()                    # 提交考試
```

#### QuestionBankService（題庫服務）
```python
class QuestionBankService:
    def __init__(mode='sqlite', **kwargs)
    def find_answer(question_text) -> Optional[Dict]
    # 返回：{question_id, type, correct_options[]}
```

#### AnswerMatcher（答案匹配引擎）
```python
class AnswerMatcher:
    @staticmethod
    def normalize_text(text)             # 標準化文字
    def find_best_match(web_q, db_qs)    # 模糊匹配
    # 多層級回退：
    # 1. 精確匹配（最快）
    # 2. 包含匹配
    # 3. 相似度匹配（SequenceMatcher）
```

---

### 匹配策略

#### 挑戰：網頁題目 vs 題庫題目差異

| 差異類型 | 範例 | 解決方案 |
|---------|------|---------|
| HTML 標籤 | `<p>題目</p>` vs `題目` | BeautifulSoup 去除 |
| 空白字元 | 多空格 vs 單空格 | 正規化 |
| 標點符號 | 全形 vs 半形 | 統一轉換 |

#### 匹配信心門檻

**設定**: 0.85（85% 相似度）以避免誤配

---

### SQLite 資料表設計

```sql
-- 題目表
CREATE TABLE questions (
    id INTEGER PRIMARY KEY,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    description_text TEXT,              -- 純文字版（用於匹配）
    type TEXT NOT NULL,                 -- single_selection/multiple_selection
    difficulty_level TEXT,
    answer_explanation TEXT
);

-- 選項表
CREATE TABLE options (
    id INTEGER PRIMARY KEY,
    question_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    content_text TEXT,                  -- 純文字版
    is_answer BOOLEAN NOT NULL,         -- 正確答案標記
    sort INTEGER,
    FOREIGN KEY (question_id) REFERENCES questions(id)
);

-- 全文檢索索引（關鍵！）
CREATE VIRTUAL TABLE questions_fts USING fts5(
    description_text,
    content='questions',
    content_rowid='id'
);
```

---

### 實作階段規劃

#### 階段 1：MVP（最小可行產品）
**目標**: 驗證自動答題可行性

- ✅ 使用現有 JSON 檔案
- ✅ 實作 `QuestionBankService`（JSON 模式）
- ✅ 實作基礎 `AnswerMatcher`
- ✅ 實作 `ExamAnswerPage`
- ✅ 整合至 `ExamLearningScenario`

**預估時間**: 2-3 小時

#### 階段 2：優化匹配準確度
**目標**: 提升匹配率

- ✅ 改進相似度演算法
- ✅ 處理 HTML 清理邏輯
- ✅ 新增匹配日誌

**預估時間**: 2-3 小時

#### 階段 3：遷移至 SQLite
**目標**: 效能優化

- ✅ 撰寫 JSON → SQLite 遷移腳本
- ✅ 建立 FTS5 全文檢索索引
- ✅ 實作 `QuestionBankService`（SQLite 模式）

**預估時間**: 1-2 小時

#### 階段 4：生產就緒
**目標**: 穩健與可維護

- ✅ 混合模式（首次啟動自動建立 SQLite）
- ✅ 自動偵測題庫更新
- ✅ 失敗時截圖除錯
- ✅ 生成答題準確率報告

**預估時間**: 2-3 小時

---

### 配置選項（規劃）

#### eebot.cfg 新增項目
```ini
# 現有配置...
user_name=your_username
password=your_password

# 新增：自動答題配置
enable_auto_answer=y                     # 啟用自動答題
question_bank_mode=sqlite                # 'sqlite' 或 'json'
question_bank_path=data/questions.db
answer_confidence_threshold=0.85         # 最低相似度門檻
auto_submit_exam=y                       # 自動提交考試
screenshot_on_mismatch=y                 # 無法匹配時截圖
```

---

### 風險評估

| 風險 | 描述 | 緩解策略 |
|------|------|---------|
| **匹配失敗** | 網頁題目與題庫不一致 | 多層級回退 + 信心門檻 |
| **動態載入** | AngularJS 渲染延遲 | 增加 WebDriverWait |
| **檢測風險** | 網站可能偵測自動化 | 已使用 Stealth JS |
| **題庫過期** | 題庫與考試不同步 | 記錄失敗案例 |

---

### 成功標準

**MVP 成功**:
- [ ] 成功匹配 ≥80% 題目
- [ ] 自動點擊正確選項（單選）
- [ ] 自動點擊正確選項（複選）
- [ ] 自動提交考試

**正式版成功**:
- [ ] 匹配率 ≥95%
- [ ] SQLite 查詢 <10ms/題
- [ ] 零誤答（無誤判）
- [ ] 優雅處理未匹配題目

---

### ✅ 實作完成總結 (2025-11-15)

**實作狀態**: ✅ 所有規劃功能已完整實作

**新增檔案**:
```
src/models/
├── __init__.py
└── question.py                  # 資料模型

src/services/
├── __init__.py
├── question_bank.py             # 題庫服務
└── answer_matcher.py            # 匹配引擎

src/pages/
└── exam_answer_page.py          # 答題頁面

src/scenarios/
└── exam_auto_answer.py          # 自動答題場景
```

**修改檔案**:
- `config/eebot.cfg` - 新增 AUTO_ANSWER 配置區塊
- `main.py` - 整合自動答題場景
- `requirements.txt` - 新增 beautifulsoup4 依賴

**使用方式**:
```bash
# 1. 安裝依賴
pip install beautifulsoup4

# 2. 設定排程
python menu.py

# 3. 執行自動答題（enable_auto_answer=y）
python main.py
```

**核心功能**:
- ✅ 自動偵測題目數量與題型
- ✅ 多層級匹配演算法 (85% 門檻)
- ✅ 單選/複選題自動作答
- ✅ 未匹配題目截圖記錄
- ✅ 答題統計報告
- ✅ 使用者確認交卷機制

---

**實作版本**: 2.0.2+auto-answer
**實作者**: wizard03 (with Claude Code CLI - Sonnet 4.5)
**實作日期**: 2025-11-15
**狀態**: ✅ **已完成並可使用**

**詳細變更記錄**: 請參考 `CHANGELOG.md` 版本 2.0.2+auto-answer
**技術細節**: 請參考 `docs/AI_ASSISTANT_GUIDE.md` Phase 2 章節

---

## 🚀 智能模式：按課程啟用自動答題 (2025-11-15 更新)

> **重大變更**: 自動答題邏輯從全局啟用改為按課程啟用

### 變更概述

**舊邏輯** (v2.0.2+auto-answer):
- 全局 `enable_auto_answer` 設定於 `config/eebot.cfg`
- 所有考試統一啟用或停用自動答題
- 需修改配置檔才能切換模式

**新邏輯** (v2.0.2+auto-answer Smart Mode):
- 每個考試獨立設定 `enable_auto_answer` 於 `data/courses.json`
- 不同考試可選擇不同模式（自動/手動）
- 自動偵測考卷區頁面後才啟動
- 懶加載機制（僅在需要時載入題庫）

### 配置變更

#### 1. 課程配置 (courses.json)

**新增 `enable_auto_answer` 欄位**:

```json
{
  "program_name": "高齡客戶投保權益保障(114年度)",
  "exam_name": "高齡測驗(100分及格)",
  "course_type": "exam",
  "enable_auto_answer": true,    // 新增：啟用此考試的自動答題
  "delay": 7.0,
  "description": "高齡測驗 - 自動答題"
}
```

**未設定則預設為手動模式**:

```json
{
  "program_name": "其他考試(114年度)",
  "exam_name": "其他測驗",
  "course_type": "exam",
  // 未設定 enable_auto_answer → 手動模式
  "delay": 7.0,
  "description": "需手動完成"
}
```

#### 2. 系統配置 (eebot.cfg)

**推薦設定**: 改用 `file_mapping` 模式

```ini
[AUTO_ANSWER]
enable_auto_answer = y                          # 保留（舊版相容）
question_bank_mode = file_mapping               # 從 'total_bank' 改為此
question_bank_path = 郵政E大學114年題庫/總題庫.json
answer_confidence_threshold = 0.85
auto_submit_exam = n
screenshot_on_mismatch = y
skip_unmatched_questions = y
screenshot_dir = screenshots/unmatched
```

### 工作流程變更

#### 舊流程（全局模式）
```
1. 編輯 config/eebot.cfg → 設定 enable_auto_answer=y
2. 執行 python menu.py → 選擇考試
3. 執行 python main.py → 所有考試自動答題
4. 如需停用，再編輯 config/eebot.cfg
```

#### 新流程（智能模式）
```
1. 編輯 data/courses.json → 為特定考試加入 "enable_auto_answer": true
2. 執行 python menu.py → 選擇考試
3. 執行 python main.py → 只有標記的考試自動答題
4. 系統自動偵測考卷區後才啟動
```

### 技術實作細節

#### 1. 考卷區頁面偵測

**新增方法**: `_is_in_exam_answer_page()` 於 `ExamLearningScenario`

```python
def _is_in_exam_answer_page(self) -> bool:
    """偵測是否進入考卷區頁面"""
    try:
        driver = self.driver_manager.get_driver()
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li.subject"))
        )
        questions = driver.find_elements(By.CSS_SELECTOR, "li.subject")
        if len(questions) > 0:
            print(f'  ✅ 偵測到考卷區頁面（共 {len(questions)} 題）')
            return True
        return False
    except Exception as e:
        print(f'  ⚠️  考卷區檢測失敗: {e}')
        return False
```

**目的**: 防止在錯誤頁面啟動自動答題

#### 2. 懶加載機制

**舊方式**: 為所有考試載入題庫和匹配器

**新方式**: 僅在需要時才初始化

```python
class ExamLearningScenario:
    def __init__(self, config, keep_browser_on_error=False):
        # ... 現有代碼 ...
        self.exam_answer_page = ExamAnswerPage(driver)
        self.question_bank = None      # 懶加載
        self.answer_matcher = None     # 懶加載

    def _auto_answer_current_exam(self, exam):
        """僅在需要時初始化題庫"""
        if self.question_bank is None:
            print('[初始化] 載入題庫...')
            self.question_bank = QuestionBankService(self.config)
            question_count = self.question_bank.load_question_bank(
                exam.get('program_name')
            )

        if self.answer_matcher is None:
            print('[初始化] 載入答案匹配器...')
            self.answer_matcher = AnswerMatcher(self.config)
```

**優點**:
- 節省記憶體（手動考試不載入）
- 加快啟動速度
- 只載入相關題庫（file_mapping 模式）

#### 3. 條件啟動邏輯

**新流程** (於 `_process_exam()` 中):

```python
def _process_exam(self, exam: Dict[str, any]):
    # ... 現有考試流程（登入、導航、點擊考試）...

    # 新增：檢查該考試是否啟用自動答題
    enable_auto_answer = exam.get('enable_auto_answer', False)

    if enable_auto_answer and self._is_in_exam_answer_page():
        print('【自動答題模式啟動】')
        self._auto_answer_current_exam(exam)
    else:
        print('請手動完成考試')
        input('完成後按 Enter 繼續...')
```

**決策樹**:
```
是否 enable_auto_answer=true?
  ├─ 否 → 手動模式（等待使用者）
  └─ 是 → 檢查是否在考卷區頁面
      ├─ 否 → 手動模式（頁面錯誤）
      └─ 是 → 自動答題模式（啟動）
```

### 主程式簡化

**舊方式**: 兩個分離的場景

```python
# 舊代碼（已移除）
if enable_auto_answer:
    exam_scenario = ExamAutoAnswerScenario(...)
else:
    exam_scenario = ExamLearningScenario(...)
```

**新方式**: 統一場景

```python
# 新代碼（簡化）
exam_scenario = ExamLearningScenario(config, keep_browser_on_error)
exam_scenario.execute(exams)
# 每個考試內部自行決定模式
```

**優點**:
- 單一瀏覽器會話處理所有考試
- 無需在考試間重啟瀏覽器
- main.py 代碼更簡潔

### 重要 Bug 修復 (2025-11-15)

#### 1. UTF-8 BOM 編碼
**問題**: JSON 檔案含有 UTF-8 BOM 標記
**解決**: 所有 JSON 讀取改用 `encoding='utf-8-sig'`

**影響檔案**:
- `src/services/question_bank.py` (2 處)
- `main.py` (1 處)
- `menu.py` (3 處)

#### 2. 分頁結構解析
**問題**: 題庫檔案使用 `[{"subjects": [...]}]` 分頁結構
**解決**: `_load_specific_bank()` 新增分頁偵測處理

```python
if isinstance(data[0], dict) and 'subjects' in data[0]:
    # 分頁結構
    for page in data:
        if 'subjects' in page:
            for subject in page['subjects']:
                # 處理題目
```

#### 3. 元素互動問題
**問題**: 交卷按鈕無法點擊 (element not interactable)
**解決**: 使用 JavaScript 點擊 + 精確 XPath

```python
# 更新定位器 (exam_answer_page.py)
SUBMIT_BUTTON = (By.XPATH, "/html/body/div[3]/div[4]/div[3]/div[9]/div/div/div[3]/div/div[3]/a")
CONFIRM_BUTTON = (By.XPATH, "//*[@id='submit-exam-confirmation-popup']/div/div[3]/div/button[1]")

# JavaScript 點擊
self.driver.execute_script("arguments[0].click();", submit_btn)
time.sleep(3)
```

#### 4. QuestionBankService 初始化
**問題**: 使用錯誤參數 `mode=...`, `total_bank_path=...`
**解決**: 正確初始化方式

```python
self.question_bank = QuestionBankService(self.config)
question_count = self.question_bank.load_question_bank(exam.get('program_name'))
```

#### 5. 方法名稱不一致
**問題**: `get_all_questions()` 等方法不存在
**解決**: 統一命名

```python
# 正確的方法名稱 (ExamAnswerPage)
detect_questions()             # 非 get_all_questions()
extract_question_text()        # 非 get_question_text()
extract_options()              # 非 get_options()
submit_exam_with_confirmation() # 非 submit_exam()
```

#### 6. 回傳型別處理
**問題**: `find_best_match()` 回傳 tuple 非 dict
**解決**: 正確的 tuple 解包

```python
match_result = self.answer_matcher.find_best_match(question_text, questions)
if match_result is None:
    # 處理無匹配
else:
    db_question, confidence = match_result  # tuple 解包
```

### 測試結果

**測試課程**: 高齡客戶投保權益保障考試

| 項目 | 結果 |
|-----|------|
| 題庫載入 | 10 題 |
| 匹配成功 | 10/10 (100%) |
| 匹配信心度 | 95-100% |
| 自動作答 | ✅ 全部正確 |
| 考試提交 | ✅ 成功 |

### 使用範例

#### 範例 1: 為特定考試啟用自動答題

**步驟 1**: 編輯 `data/courses.json`

```json
{
  "description": "課程資料配置檔",
  "version": "1.0",
  "courses": [
    {
      "program_name": "高齡客戶投保權益保障(114年度)",
      "exam_name": "高齡測驗(100分及格)",
      "course_type": "exam",
      "enable_auto_answer": true,    // 啟用此考試
      "delay": 7.0,
      "description": "高齡測驗 - 自動答題"
    },
    {
      "program_name": "資通安全測驗(114年度)",
      "exam_name": "資通安全測驗",
      "course_type": "exam",
      "enable_auto_answer": true,    // 啟用此考試
      "delay": 7.0,
      "description": "資通安全測驗 - 自動答題"
    },
    {
      "program_name": "其他考試(114年度)",
      "exam_name": "其他測驗",
      "course_type": "exam",
      // 未設定 → 手動模式
      "delay": 7.0,
      "description": "其他測驗 - 手動完成"
    }
  ]
}
```

**步驟 2**: 排程與執行

```bash
python menu.py
# 選擇三個考試

python main.py
# 考試 1 (高齡測驗): 自動答題 ✅
# 考試 2 (資通安全測驗): 自動答題 ✅
# 考試 3 (其他測驗): 手動模式 ⏸️
```

#### 範例 2: 混合課程與考試排程

```bash
python menu.py
# 選擇:
# [1] 課程 A (一般課程)
# [2] 課程 B (一般課程)
# [3] 考試 A (enable_auto_answer: true)
# [4] 考試 B (enable_auto_answer: false)

python main.py
# 執行順序:
# 1. 課程 A → 自動完成 ✅
# 2. 課程 B → 自動完成 ✅
# 3. 考試 A → 自動答題 ✅
# 4. 考試 B → 手動模式 ⏸️
```

### 向後相容性

**相容性說明**:
- ✅ 未設定 `enable_auto_answer` 的考試預設為手動模式
- ✅ 原有手動考試流程完全保留
- ✅ 所有課程學習功能不受影響
- ✅ 配置檔 `enable_auto_answer` 保留但作用改變

**破壞性變更**:
- ❌ 全局 `enable_auto_answer` 不再控制所有考試
- ❌ 必須為每個考試明確設定配置
- ❌ `ExamAutoAnswerScenario` 類別已移除（功能整合至 `ExamLearningScenario`）

### 遷移指南

**如果你正在使用全局 `enable_auto_answer`**:

1. 保留 `enable_auto_answer=y` 於 `config/eebot.cfg`（向後相容）
2. 為需要自動答題的考試加入 `"enable_auto_answer": true`
3. 將 `question_bank_mode` 改為 `file_mapping` 提升準確度
4. 移除舊的 `ExamAutoAnswerScenario` 匯入（如果有）

### 最佳實踐

#### 1. 先手動測試
```json
{
  "enable_auto_answer": false,  // 或省略此欄位
  "description": "先手動測試"
}
```

#### 2. 確認題庫對應
檢查 `src/services/question_bank.py` 中的 program name 對應:

```python
QUESTION_BANK_MAPPING = {
    "高齡客戶投保權益保障(114年度)": "高齡投保（10題）.json",
    "資通安全測驗(114年度)": "資通安全（30題）.json",
    "壽險業務員在職訓練學程課程及測驗(114年度)": "壽險業務員在職訓練（30題）.json",
    # 根據需求新增更多對應
}
```

#### 3. 監控匹配成功率
觀察終端輸出:
```
[匹配] 第 1 題: 題目內容
  ✅ 匹配成功（信心: 100.00%）
  ✅ 正確答案: ['選項1', '選項2']
```

#### 4. 檢視失敗截圖
未匹配題目儲存於 `screenshots/unmatched/`:
```
question_5_20251115_143022.png
question_5_20251115_143022.txt  // 含題目文字
```

### 問題排查

#### 問題 1: 自動答題未啟動

**檢查**:
1. `courses.json` 中是否設定 `"enable_auto_answer": true`？
2. 是否成功進入考卷區頁面？
3. 查看終端是否有頁面偵測訊息

**除錯輸出**:
```
✅ 偵測到考卷區頁面（共 10 題）
【自動答題模式啟動】
[初始化] 載入題庫...
```

#### 問題 2: 題目無法匹配

**檢查**:
1. `question_bank_mode` 是否正確設定？
2. program name 是否精確對應題庫對應表？
3. 信心門檻是否過高（預設 0.85）

**除錯輸出**:
```
[載入] 題庫檔案: 郵政E大學114年題庫/高齡投保（10題）.json
[成功] 載入題庫: 10 題
```

#### 問題 3: 交卷按鈕無法使用

**檢查**:
1. `exam_answer_page.py` 中的 XPath 定位器
2. 點擊間的等待時間（預設 3 秒）
3. JavaScript 執行是否啟用

**解決方案**: 定位器已更新為使用者提供的精確 XPath

#### 問題 4: 第二個考試 0% 匹配率 (嚴重 Bug - 已修復)

**症狀**:
- 第一個考試: 100% 匹配率 ✅
- 第二個考試: 0% 匹配率 ❌
- 所有題目顯示「無法匹配」

**根本原因**:
`src/scenarios/exam_learning.py:261` 的懶載入邏輯錯誤，導致多個考試共用同一個題庫實例。

**問題機制**:
```python
# ❌ 錯誤代碼（修復前）
if self.question_bank is None:
    self.question_bank = QuestionBankService(self.config)
    question_count = self.question_bank.load_question_bank(exam.get('program_name'))
```

1. 考試 1 載入題庫 A（例如：高齡投保 10 題）
2. `self.question_bank` 不再是 `None`
3. 考試 2 跳過初始化
4. 考試 2 嘗試用錯誤的題庫 A 匹配題庫 B 的題目
5. 結果：0% 匹配率

**修復方案** (v2.0.2+auto-answer.1):
```python
# ✅ 修復後代碼
# 為每個考試重新載入對應題庫
self.question_bank = QuestionBankService(self.config)
program_name = exam.get('program_name')
question_count = self.question_bank.load_question_bank(program_name)
```

**關鍵改變**:
- ✅ 移除 `if self.question_bank is None` 檢查
- ✅ 每個考試都創建新的 `QuestionBankService` 實例
- ✅ 每個考試都載入對應的題庫
- ✅ 新增 program_name 日誌輸出

**驗證方式**:
執行包含多個考試的流程，應看到每個考試都正確載入對應題庫：
```
--- Processing Exam 1/2 ---
  📚 正在載入題庫...
  ✅ 題庫已載入（共 10 題）
  📋 課程名稱: 高齡客戶投保權益保障(114年度)

--- Processing Exam 2/2 ---
  📚 正在載入題庫...
  ✅ 題庫已載入（共 21 題）
  📋 課程名稱: 金融服務業公平待客原則＆洗錢防制及打擊資恐教育訓練(114年度)
```

**⚠️ 重要經驗**:
> **懶載入 + 共享狀態 = 潛在 Bug**
>
> 當物件實例被重複使用處理不同資料集時：
> - ❌ 不要在不檢查資料上下文的情況下使用懶載入
> - ✅ 處理新資料時務必重新載入資源
> - ✅ 加入日誌追蹤載入的資源
> - ✅ 測試多個連續操作的場景

**程式碼審查檢查清單**:
- [ ] 是否有懶載入邏輯（`if self.resource is None`）？
- [ ] 該實例是否會被重複使用處理不同資料？
- [ ] 資源是否依賴輸入參數？
- [ ] 是否有測試多個連續操作的情境？

---

**智能模式版本**: 2.0.2+auto-answer.1 (懶載入 Bug 已修復)
**更新日期**: 2025-11-15 晚間
**更新者**: wizard03 (with Claude Code CLI - Gleipnir Project)

---

## 🎨 GUI 開發計畫 (2025-11-24 規劃)

> **狀態**: 📋 規劃階段
> **可行性**: ✅ 完全可行
> **預估時程**: 18-26 小時
> **優先級**: 中等（增強使用者體驗）

### 概述

專案架構完全支援整合 GUI 介面，可作為獨立展示層，不破壞現有 CLI 功能。

### 技術方案

#### 推薦 GUI 框架

🏆 **CustomTkinter** (最佳選擇)

**選擇理由**:
- ✅ 現代化外觀（Material Design 風格）
- ✅ 基於 Tkinter，穩定可靠
- ✅ 跨平台支援（Windows/Linux/macOS）
- ✅ 安裝簡單：`pip install customtkinter`
- ✅ 支援深色模式
- ✅ 向後相容 Tkinter API

**替代方案**:
- **PyQt5/PySide6**: 功能強大但體積較大
- **原生 Tkinter**: Python 內建但外觀較傳統
- **PySimpleGUI**: 語法簡單但自訂性較低

### 架構設計

#### 新增檔案結構

```
eebot/
├── gui/                          # 【新增】GUI 層
│   ├── __init__.py
│   ├── main_window.py            # 主視窗
│   ├── widgets/                  # GUI 元件
│   │   ├── course_selector.py    # 課程選擇器
│   │   ├── config_editor.py      # 配置編輯器
│   │   ├── progress_monitor.py   # 執行進度監控
│   │   ├── log_viewer.py         # 日誌查看器
│   │   ├── report_viewer.py      # 時間統計報告查看器
│   │   └── screenshot_viewer.py  # 截圖瀏覽器
│   └── utils/                    # GUI 工具
│       ├── thread_manager.py     # 多執行緒管理
│       └── notification.py       # 系統通知
│
├── gui_main.py                   # 【新增】GUI 入口
├── main.py                       # 【保留】CLI 入口
└── menu.py                       # 【保留】CLI 選單
```

#### 設計原則

1. **不修改核心程式碼** ✅
   - 遵循「禁止修改清單」
   - 保護 `src/core/`, `src/pages/`, `src/scenarios/`

2. **GUI 作為獨立層** ✅
   - 直接呼叫現有 scenario 和 service
   - 透過 callback 機制更新 GUI 狀態

3. **保持 CLI 可用** ✅
   - 用戶可自由選擇 CLI 或 GUI

4. **多執行緒設計** ✅
   - 避免 GUI 凍結

### 主要功能模組

#### 1. 課程管理介面（替代 menu.py）
- 視覺化課程選擇
- 排程管理（新增、移除、清空）
- 標記顯示（課程 vs 考試、自動答題 🤖）

#### 2. 配置管理介面（編輯 eebot.cfg）
- 圖形化編輯所有配置項
- 帳號設定、MitmProxy 設定、自動答題設定
- 即時驗證與儲存

#### 3. 執行監控介面
- 即時進度條（總進度 + 當前課程進度）
- 執行日誌滾動顯示
- 蟲洞狀態顯示（⏰ 時間加速）
- 暫停/停止控制

#### 4. 智能推薦介面（替代 menu.py 的 'i' 功能）
- 自動掃描「修習中」課程
- 樹狀顯示掃描結果
- 一鍵執行確認對話框

#### 5. 時間統計報告查看器
- 讀取 `reports/time_report_*.md`
- 圖表化顯示（圓餅圖、長條圖）
- 課程明細表格
- 匯出功能

#### 6. 截圖瀏覽器
- 縮圖網格顯示
- 點擊放大檢視
- 時間戳與課程名稱顯示

### Linux 跨平台支援

✅ **完全支援** - 專案本身已經跨平台

**證據**:
1. **字體支援** - `src/utils/screenshot_utils.py` 已處理 15+ Linux 字體路徑
2. **路徑處理** - 使用 Python 標準路徑處理
3. **依賴套件** - 所有依賴皆跨平台

**CustomTkinter 在 Linux 上**:
- ✅ 支援所有主流發行版（Ubuntu, Debian, Fedora, Arch）
- ✅ 支援所有主流桌面環境（GNOME, KDE, XFCE, Cinnamon）
- ✅ 自動適應系統主題

**安裝步驟（Ubuntu/Debian）**:
```bash
sudo apt install python3 python3-tk fonts-wqy-zenhei
pip3 install customtkinter
python3 gui_main.py
```

### 需要調整的現有檔案

#### 最小侵入性修改

**Scenario 類別** - 新增進度回呼參數（可選）:

```python
# src/scenarios/course_learning.py
class CourseLearningScenario:
    def __init__(self, config, keep_browser_on_error=False,
                 time_tracker=None, visit_duration_increase=9000,
                 progress_callback=None):  # 新增可選參數
        self.progress_callback = progress_callback

    def _process_course(self, course):
        # 更新進度到 GUI（如果有）
        if self.progress_callback:
            self.progress_callback({
                'type': 'progress',
                'current': self.current_index,
                'total': self.total_count,
                'course_name': course['lesson_name'],
                'stage': 'Stage 2 - 課程計畫頁面'
            })
        # 原有邏輯不變
```

**修改原則**:
- ✅ 只新增可選參數（預設 `None`）
- ✅ 向後相容（CLI 模式不受影響）
- ✅ 不修改核心邏輯

### 實作計畫

| 階段 | 工作內容 | 預估時間 |
|-----|---------|---------|
| **Phase 1** | 基礎 GUI 框架 + 課程選擇器 | 4-6 小時 |
| **Phase 2** | 配置編輯器 + 執行監控 | 4-6 小時 |
| **Phase 3** | 智能推薦 GUI + 多執行緒整合 | 3-4 小時 |
| **Phase 4** | 時間統計報告查看器 + 截圖瀏覽 | 3-4 小時 |
| **Phase 5** | 測試與優化 + 打包 | 4-6 小時 |
| **總計** | | **18-26 小時** |

### 建議實作順序

1. ✅ 建立基礎 GUI 框架（主視窗 + 分頁）
2. ✅ 實作課程選擇器（讀取 `courses.json`）
3. ✅ 整合執行流程（呼叫 scenario）
4. ✅ 實作進度監控（即時顯示）
5. ✅ 實作配置編輯器
6. ✅ 實作智能推薦 GUI
7. ✅ 實作報告與截圖查看器
8. ✅ 打包成可執行檔（PyInstaller）

### 技術要點

#### 1. 多執行緒管理（關鍵）

```python
import threading

def start_execution(self):
    # 在背景執行緒執行避免 GUI 凍結
    thread = threading.Thread(
        target=self.run_automation,
        args=(scheduled,),
        daemon=True
    )
    thread.start()
```

#### 2. 進度回呼機制

```python
# Scenario 呼叫 callback
if self.progress_callback:
    self.progress_callback({
        'type': 'progress',
        'current': 2,
        'total': 5,
        'message': '正在執行課程 2/5'
    })
```

#### 3. 打包成執行檔

```bash
# Windows
pyinstaller --onefile --windowed --name="EEBot-Gleipnir" gui_main.py

# Linux
pyinstaller --onefile --windowed --name="EEBot-Gleipnir" gui_main.py
```

### 參考資源

- **CustomTkinter 官方文檔**: https://customtkinter.tomschimansky.com/
- **範例專案**: https://github.com/TomSchimansky/CustomTkinter
- **工作日誌**: [DAILY_WORK_LOG_202511242300.md](./DAILY_WORK_LOG_202511242300.md)

### 當前狀態

- ✅ 可行性評估完成
- ✅ 技術方案確定（CustomTkinter）
- ✅ 架構設計完成
- ✅ Linux 跨平台支援確認
- ⏳ 等待實作開始

---

## 📚 延伸閱讀

- **通用 AI 助手指南**: `docs/AI_ASSISTANT_GUIDE.md`
- **修改歷史**: `docs/CHANGELOG.md`
- **Selenium 文檔**: https://www.selenium.dev/documentation/
- **MitmProxy 文檔**: https://docs.mitmproxy.org/

---

**維護者**: wizard03
**文檔版本**: 1.9
**最後更新**: 2025-11-24 (GUI 開發計畫新增)

如有任何問題，請參考 `docs/AI_ASSISTANT_GUIDE.md` 或查看 `docs/CHANGELOG.md` 了解最新修改。

---

## 📅 最新工作日誌

- **2025-11-24 23:00**: [DAILY_WORK_LOG_202511242300.md](./DAILY_WORK_LOG_202511242300.md) - GUI 介面可行性評估 ⭐ NEW
  - ✅ 確認專案可加入 GUI 介面
  - ✅ 評估多種 GUI 框架方案（推薦 CustomTkinter）
  - ✅ 確認 Linux 跨平台完全支援
  - ✅ 設計 GUI 架構方案（6 大功能模組）
  - ✅ 規劃實作時程（18-26 小時）
- **2025-11-24 21:57**: [DAILY_WORK_LOG_202511242157.md](./DAILY_WORK_LOG_202511242157.md) - 課程配置優化討論 + 工作日誌規範化
  - ✅ 緊急修復：menu.py 智能推薦 stealth 提取步驟
  - 📝 討論：MitmProxy 精密攔截與課程連動
  - 📝 討論：課程流程標準化與 Import/Export 系統
  - 📝 規範：工作日誌檔名格式變更（yyyymmdd → yyyymmddhhmm）
- **2025-11-17**: [DAILY_WORK_LOG_20251117.md](./DAILY_WORK_LOG_20251117.md) - 穩定性與配置優化 (v2.0.5)
- **2025-11-16**: [DAILY_WORK_LOG_20251116.md](./DAILY_WORK_LOG_20251116.md) - 安全性增強與智能推薦修復
- **2025-11-15**: [DAILY_WORK_LOG_20251115.md](./DAILY_WORK_LOG_20251115.md) - 自動答題系統完整實作
- **2025-11-14**: [DAILY_WORK_LOG_20251114.md](./DAILY_WORK_LOG_20251114.md) - 早期開發記錄
- **2025-01-17 (更新4)**: CHANGELOG.md 拆分優化 - 提升 Claude Code CLI 可讀性 (v2.0.4)
- **2025-01-17 (更新3)**: 完整時間統計系統 + 產品化輸出訊息 (v2.0.4)
- **2025-01-17 (更新2)**: 產品化輸出訊息優化（MVP → Release） (v2.0.3)
- **2025-01-17 (更新1)**: 一鍵自動執行功能 + 跨平台字體支援 (v2.0.3)
- **2025-01-16**: [DAILY_WORK_LOG_20250116.md](./DAILY_WORK_LOG_20250116.md) - 截圖功能實作與時間配置分離

---

**本段結束**

✅ **文檔已全部閱讀完畢**

📑 返回: [完整索引](./CLAUDE_CODE_HANDOVER.md)

---

*文檔版本: 2.0 | 最後更新: 2025-11-24 | 專案: Gleipnir*
