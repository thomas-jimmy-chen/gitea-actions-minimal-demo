# EEBot - Claude Code CLI 交接文檔

> **專為 Claude Code CLI 優化的項目交接文檔**
>
> 本文檔使用 Claude Code 的最佳實踐格式編寫，方便快速理解項目結構並進行後續開發。

**文檔版本**: 1.0
**最後更新**: 2025-01-13
**項目版本**: 2.0.1+exam
**維護者**: wizard03

---

## 🎯 快速開始 (Quick Start for Claude)

### 閱讀本文檔前
1. 使用 `@workspace` 索引整個項目（建議）
2. 閱讀本文檔獲取項目概覽
3. 查看 `docs/CHANGELOG.md` 了解最新修改

### 關鍵文件路徑
```
D:\Dev\eebot\
├── data/courses.json          ← 課程配置（最重要！）
├── main.py                    ← 程式入口
├── menu.py                    ← 互動式選單
├── src/scenarios/             ← 業務流程層
│   ├── course_learning.py     ← 課程流程（原有，勿改）
│   └── exam_learning.py       ← 考試流程（2025-01-13 新增）
├── src/pages/                 ← 頁面操作層 (POM)
│   ├── exam_detail_page.py    ← 考試頁面（2025-01-13 新增）
│   ├── course_list_page.py    ← 課程列表（原有，勿改）
│   └── course_detail_page.py  ← 課程詳情（原有，勿改）
└── docs/                      ← 項目文檔
    ├── AI_ASSISTANT_GUIDE.md  ← 通用 AI 助手文檔
    └── CHANGELOG.md           ← 修改歷史記錄
```

---

## 📖 項目概述

### 項目資訊
- **名稱**: EEBot (Elearn Automation Bot)
- **用途**: 台灣郵政 e 大學自動化學習機器人
- **目標網站**: https://elearn.post.gov.tw
- **主要語言**: Python 3.x
- **核心框架**: Selenium WebDriver + MitmProxy

### 架構模式
```
POM (Page Object Model) + API Interceptor
├── Core Layer       (核心基礎設施)
├── Pages Layer      (頁面物件模型)
├── Scenarios Layer  (業務流程編排)
└── API Layer        (HTTP 請求攔截)
```

### 工作原理
1. **自動登入**: 使用 Cookies 或帳密登入
2. **課程/考試選擇**: 根據 `data/courses.json` 配置
3. **自動瀏覽**: Selenium 模擬用戶操作
4. **時長修改**: MitmProxy 攔截並修改訪問時長
5. **完成學習**: 自動完成課程或考試流程

---

## 🏗️ 項目架構

### 分層架構圖
```
┌─────────────────────────────────────────────┐
│              main.py (入口)                  │
│  ┌─────────────────────────────────────┐   │
│  │    menu.py (互動式排程管理)          │   │
│  └─────────────────────────────────────┘   │
└──────────────┬──────────────────────────────┘
               │
        ┌──────▼──────────────┐
        │  Scenarios Layer    │ ← 業務流程編排
        │  - course_learning  │   (勿改原有檔案)
        │  - exam_learning ✨ │   (新增)
        └──────┬──────────────┘
               │
        ┌──────▼──────────────┐
        │   Pages Layer       │ ← 頁面物件 (POM)
        │  - login_page       │
        │  - course_list_page │   (勿改)
        │  - course_detail    │   (勿改)
        │  - exam_detail ✨   │   (新增)
        └──────┬──────────────┘
               │
        ┌──────▼──────────────┐
        │    Core Layer       │ ← 核心模組
        │  - driver_manager   │   (勿改)
        │  - config_loader    │   (勿改)
        │  - cookie_manager   │   (勿改)
        │  - proxy_manager    │   (勿改)
        └─────────────────────┘
```

### 目錄結構
```
eebot/
├── src/
│   ├── core/                    # 核心基礎設施
│   │   ├── config_loader.py     # 配置載入器
│   │   ├── driver_manager.py    # WebDriver 管理
│   │   ├── cookie_manager.py    # Cookie 管理
│   │   └── proxy_manager.py     # MitmProxy 管理
│   │
│   ├── pages/                   # 頁面物件 (POM)
│   │   ├── base_page.py         # 基類（提供通用方法）
│   │   ├── login_page.py        # 登入頁面
│   │   ├── course_list_page.py  # 課程列表頁面 (勿改)
│   │   ├── course_detail_page.py # 課程詳情頁面 (勿改)
│   │   └── exam_detail_page.py  # 考試詳情頁面 (新增 ✨)
│   │
│   ├── scenarios/               # 業務流程編排
│   │   ├── course_learning.py   # 課程學習流程 (勿改)
│   │   └── exam_learning.py     # 考試流程 (新增 ✨)
│   │
│   ├── api/
│   │   └── interceptors/
│   │       └── visit_duration.py # HTTP 攔截器（修改訪問時長）
│   │
│   └── utils/
│       └── stealth_extractor.py  # 反檢測工具
│
├── data/
│   ├── courses.json             # 課程配置 (重要！)
│   └── schedule.json            # 排程配置（自動生成）
│
├── config/
│   └── eebot.cfg                # 系統配置
│
├── docs/                        # 項目文檔
│   ├── AI_ASSISTANT_GUIDE.md    # 通用 AI 助手指南
│   ├── CLAUDE_CODE_HANDOVER.md  # 本文件
│   └── CHANGELOG.md             # 修改歷史
│
├── main.py                      # 主程式入口
└── menu.py                      # 互動式選單
```

---

## 🔧 核心概念

### 1. 課程配置 (courses.json)

這是整個系統的**數據核心**，定義所有可執行的課程和考試。

#### 課程類型 (course)
```json
{
  "program_name": "課程計畫名稱",
  "lesson_name": "課程名稱",
  "course_id": 369,
  "delay": 7.0,
  "description": "課程描述"
}
```

#### 考試類型 (exam) - 2025-01-13 新增
```json
{
  "program_name": "課程計畫名稱",
  "exam_name": "考試名稱",
  "course_type": "exam",
  "delay": 10.0,
  "description": "考試描述"
}
```

**關鍵差異**:
- 課程使用 `lesson_name` + `course_id`
- 考試使用 `exam_name` + `course_type: "exam"`
- 考試沒有 `course_id`（因為考試的返回邏輯不同）

### 2. 執行流程

#### 課程流程 (course_learning.py)
```
登入 → 我的課程 → 選擇計畫 → 選擇課程 → 返回計畫 → 返回列表
```

#### 考試流程 (exam_learning.py) - 新增
```
登入 → 我的課程 → 選擇計畫 → 點擊考試
  → 點擊"繼續答題" → 勾選同意 → 確認 → 考卷區
```

### 3. MitmProxy 機制

MitmProxy 用於攔截並修改 HTTP 請求，特別是修改訪問時長參數。

**工作流程**:
1. `ProxyManager` 啟動 MitmProxy 伺服器
2. `VisitDurationInterceptor` 攔截特定請求
3. 修改請求中的 `visit_duration` 參數（+9000 秒）
4. 讓系統誤以為用戶已觀看足夠時長

**配置**: `config/eebot.cfg` 中的 `modify_visits` 選項

---

## 📝 常見任務指南

### 任務 1: 添加新的課程（學習類型）

#### Step 1: 編輯 courses.json
```json
{
  "program_name": "新課程計畫名稱",
  "lesson_name": "新課程名稱",
  "course_id": 999,          // 從網頁 HTML 找到 ng-click='goBackCourse(XXX)'
  "delay": 7.0,
  "description": "課程描述"
}
```

#### Step 2: 使用 menu.py 選擇課程
```bash
python menu.py
# 選擇課程編號
# 輸入 's' 儲存排程
```

#### Step 3: 執行
```bash
python main.py
```

**注意**: 不需要修改任何代碼！

---

### 任務 2: 添加新的考試（考試類型）

#### Step 1: 編輯 courses.json
```json
{
  "program_name": "考試計畫名稱",
  "exam_name": "考試名稱",
  "course_type": "exam",      // 必須設為 "exam"
  "delay": 10.0,              // 考試流程較複雜，建議 10 秒以上
  "description": "考試描述"
}
```

#### Step 2-3: 同上（使用 menu.py 和 main.py）

---

### 任務 3: 修改考試流程

如果需要調整考試流程的點擊邏輯：

#### 編輯文件
- `src/pages/exam_detail_page.py`
- `src/scenarios/exam_learning.py`

#### 可修改的方法
```python
# exam_detail_page.py
def click_exam_by_name()          # 點擊考試名稱
def check_agreement_checkbox()    # 勾選同意條款
def click_popup_continue_button() # 確認進入考試
```

#### ⚠️ 不可修改的文件
- `src/scenarios/course_learning.py`
- `src/pages/course_list_page.py`
- `src/pages/course_detail_page.py`
- 任何 `src/core/*` 檔案

---

### 任務 4: 新增新類型的流程

假設你需要添加「問卷」類型：

#### Step 1: 創建頁面類
```python
# src/pages/survey_page.py
from .base_page import BasePage

class SurveyPage(BasePage):
    def click_survey_by_name(self, survey_name, delay=10.0):
        # 實作邏輯
        pass
```

#### Step 2: 創建場景類
```python
# src/scenarios/survey_learning.py
from ..pages.survey_page import SurveyPage

class SurveyLearningScenario:
    def execute(self, surveys):
        # 實作邏輯
        pass
```

#### Step 3: 修改 main.py
```python
from src.scenarios.survey_learning import SurveyLearningScenario

# 在 main() 中添加分離邏輯
surveys = [item for item in courses if item.get('course_type') == 'survey']
```

#### Step 4: 修改 menu.py
在 `display_menu()` 和 `display_schedule()` 中添加問卷類型的顯示邏輯。

---

## 🚫 禁止修改清單

以下文件**絕對不可修改**（除非有明確需求並經過審查）：

### Scenarios Layer
- ❌ `src/scenarios/course_learning.py`

### Pages Layer
- ❌ `src/pages/base_page.py`
- ❌ `src/pages/login_page.py`
- ❌ `src/pages/course_list_page.py`
- ❌ `src/pages/course_detail_page.py`

### Core Layer
- ❌ `src/core/config_loader.py`
- ❌ `src/core/driver_manager.py`
- ❌ `src/core/cookie_manager.py`
- ❌ `src/core/proxy_manager.py`

### API Layer
- ❌ `src/api/interceptors/visit_duration.py`

### 配置文件
- ❌ `config/eebot.cfg`
- ❌ `data/courses.json` 中的**原有課程條目**

### 原因
這些文件是系統的核心，已經過充分測試且穩定運行。修改可能導致現有功能崩潰。

---

## 🔍 關鍵代碼索引

### 1. 如何定位網頁元素？

查看 `src/pages/base_page.py`:
```python
def find_element(self, locator: tuple) -> WebElement:
    # 使用 WebDriverWait 等待元素出現
    return self.wait.until(EC.presence_of_element_located(locator))

def click(self, locator: tuple, use_js: bool = False):
    # 智能點擊（處理被遮擋的情況）
    # 如果普通點擊失敗，會自動使用 JS 點擊
```

**使用範例**:
```python
# 在任何 Page 類中
exam_button = (By.XPATH, "//button[text()='繼續答題']")
self.click(exam_button)
```

### 2. 如何添加延遲等待？

```python
import time
time.sleep(10.0)  # 固定延遲 10 秒

# 或使用 BasePage 提供的方法
self.sleep(10.0)
```

### 3. 如何處理彈窗？

查看 `src/pages/exam_detail_page.py`:
```python
def check_agreement_checkbox(self, delay: float = 10.0):
    # 使用 JavaScript 點擊（避免被其他元素覆蓋）
    element = self.find_element(self.AGREEMENT_CHECKBOX)
    self.driver.execute_script("arguments[0].click();", element)
```

### 4. 如何讀取配置？

查看 `src/core/config_loader.py`:
```python
config = ConfigLoader("config/eebot.cfg")
config.load()

username = config.get('user_name')
password = config.get('password')
modify_visits = config.get_bool('modify_visits')
```

---

## 💡 Claude Code 特定建議

### 使用 @workspace
在與 Claude Code 對話時，使用 `@workspace` 快速索引項目：
```
@workspace 請幫我找到所有定義 click 方法的文件
@workspace 課程配置檔在哪裡？
@workspace 考試流程是如何實現的？
```

### 快速命令參考
```bash
# 查看課程列表並排程
python menu.py

# 執行排程
python main.py

# 查看配置
cat config/eebot.cfg

# 查看課程配置
cat data/courses.json

# 查看排程
cat data/schedule.json

# 查看修改歷史
cat docs/CHANGELOG.md
```

### 代碼修改流程
1. **閱讀本文檔** → 理解項目結構
2. **查看 CHANGELOG.md** → 了解最新修改
3. **定位目標文件** → 使用上方的文件索引
4. **檢查禁止清單** → 確保不修改核心文件
5. **進行修改** → 遵循現有代碼風格
6. **更新 CHANGELOG.md** → 記錄你的修改
7. **測試** → 使用 menu.py 和 main.py 測試

---

## 📞 問題排查

### 問題 1: 考試按鈕無法點擊 (已於 2025-01-13 修復)

#### 1.1 考試頁面"繼續答題"按鈕找不到

**症狀**: `Element not found` 在 Step 2

**原因**: XPath 定位器過於嚴格

**解決方案** (已實現):
- `click_continue_exam_button()` 現在使用 4 種備用策略
- 如果仍失敗：增加 `delay` 到 15 秒

#### 1.2 彈窗內"繼續答題"按鈕無法點擊

**症狀**: `Element not clickable` 在 Step 4

**原因**:
- 按鈕在 checkbox 勾選後需要時間啟用
- AngularJS 更新狀態延遲
- 元素可能被遮擋

**解決方案** (已實現):
- `click_popup_continue_button()` 使用 5 種策略
- 自動檢查 disabled 狀態並等待
- 使用 JavaScript 點擊
- 詳見：`exam_detail_page.py` 第 142-200 行

**如果仍失敗**:
1. 增加 `delay` 時間（從 10 秒增加到 15 秒）
2. 檢查彈窗 ID 是否為 `start-exam-confirmation-popup`
3. 使用瀏覽器 DevTools 檢查實際結構

### 問題 2: MitmProxy 無法啟動

**可能原因**:
- 端口被佔用
- 權限不足

**解決方案**:
1. 檢查 `config/eebot.cfg` 中的 `listen_port`
2. 更改為其他端口（例如 8081）
3. 或設置 `modify_visits=n` 禁用代理

### 問題 3: 課程和考試混合執行順序問題

**現狀**:
當排程包含課程和考試時，會先執行所有課程，再執行所有考試。

**原因**:
每種類型使用獨立的 Scenario，避免頻繁切換造成瀏覽器重啟。

**如需交叉執行**:
需要修改 `main.py`，實現單一 Scenario 統一處理。

---

## 🎯 規劃中功能：自動答題系統 (Phase 2)

> **狀態**: 規劃階段（評估於 2025-01-14）
> **預計實作時間**: 待定
> **目前進度**: 考試流程自動化已完成，自動答題尚未實作

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

### 重要提醒

⚠️ **請勿實作**，直到：
1. 使用者明確要求實作
2. 現有考試流程功能穩定
3. 題庫資料已驗證且最新
4. 法律與道德考量已處理

✅ **本規劃文檔**作為：
- 未來 AI 助手的參考
- 實作設計藍圖
- 風險評估與緩解指南
- 成功標準檢查清單

---

**規劃文檔版本**: 1.0
**評估者**: Claude Code CLI (Sonnet 4.5)
**評估日期**: 2025-01-14
**狀態**: ⏸️ 規劃階段 - 等待用戶批准

**詳細技術規格**: 請參考 `docs/AI_ASSISTANT_GUIDE.md` 的對應章節

---

## 📚 延伸閱讀

- **通用 AI 助手指南**: `docs/AI_ASSISTANT_GUIDE.md`
- **修改歷史**: `docs/CHANGELOG.md`
- **Selenium 文檔**: https://www.selenium.dev/documentation/
- **MitmProxy 文檔**: https://docs.mitmproxy.org/

---

**維護者**: wizard03
**文檔版本**: 1.0
**最後更新**: 2025-01-13

如有任何問題，請參考 `docs/AI_ASSISTANT_GUIDE.md` 或查看 `docs/CHANGELOG.md` 了解最新修改。
